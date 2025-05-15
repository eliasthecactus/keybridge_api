from collections import defaultdict
from models import db, AuthSource, Access, Application, ApplicationOptionGroup, ApplicationOptionGroupItem, LdapObject
from services.ldap_service import connect_to_ldap, get_user_groups
from services.auth_service import jwt_decoder
from services.logger import loggie

def get_client_applications(identity):
    """Retrieve applications the client has access to."""
    try:
        user_id = identity.get("id")
        server_id = identity.get("data")["auth_id"]

        # Retrieve AuthSource
        auth_source = db.session.query(AuthSource).filter_by(id=server_id).first()
        if not auth_source:
            return {"code": 40, "message": "AuthSource not found", "status_code": 404}

        # Connect to LDAP
        ldap_conn = connect_to_ldap(auth_source.host, auth_source.bind_user_dn, auth_source.bind_password, port=auth_source.port, ssl=auth_source.ssl)
        if not ldap_conn.bind():
            return {"code": 50, "message": "Error binding to LDAP Server", "status_code": 500}

        # Get user UUIDs (including groups)
        uuids = [user_id] + get_user_groups(ldap_conn, auth_source.base_dn, user_id, is_ad=(auth_source.server_type == "ad"), cascade=True)

        # Query applications based on user and group UUIDs
        access_records = db.session.query(Access).join(LdapObject, LdapObject.id == Access.ldap_object_id).filter(LdapObject.object_uuid.in_(uuids)).all()

        # Collect unique application IDs
        application_ids = {record.access_to for record in access_records}

        # Query applications that the user or groups have access to
        applications = (
            db.session.query(ApplicationOptionGroup, Application, ApplicationOptionGroupItem)
            .join(Application, ApplicationOptionGroup.application_id == Application.id)
            .join(ApplicationOptionGroupItem, ApplicationOptionGroup.id == ApplicationOptionGroupItem.group_id)
            .filter(ApplicationOptionGroup.id.in_(application_ids))
            .all()
        )

        # INFO: Applications without option group items are not returned
        application_map = defaultdict(lambda: {
            "application_id": None,
            "application_name": None,
            "application_image": None,
            "application_option_groups": []
        })

        for option_group, app, item in applications:
            app_data = application_map[app.id]
            app_data["application_id"] = app.id
            app_data["application_name"] = app.name
            app_data["application_image"] = app.image

            # Add option group details
            option_group_data = next(
                (og for og in app_data["application_option_groups"] if og["id"] == option_group.id),
                None
            )
            if not option_group_data:
                option_group_data = {
                    "id": option_group.id,
                    "name": option_group.name,
                    "items": []
                }
                app_data["application_option_groups"].append(option_group_data)

            # Add items to the option group
            option_group_data["items"].append({
                "id": item.id,
                "name": item.name
            })

        # Convert the map to a list of application dictionaries
        results = list(application_map.values())

        return {"code": 0, "message": "Applications retrieved successfully", "data": {"applications": results}, "status_code": 200}

    except Exception as e:
        loggie.error(f"Unexpected error retrieving client applications: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}