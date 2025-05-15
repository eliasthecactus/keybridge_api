from models import db, ApplicationOptionGroupItem, ApplicationOptionGroup, Application, Access, LdapObject, AuthSource
from services.auth_service import jwt_decoder
from services.ldap_service import connect_to_ldap, get_user_groups
from services.logger import loggie

def check_launch_request(aogi_id, identity):
    """Verify if a client has access to launch an application option group item."""
    try:
        user_id = identity.get("id")
        server_id = identity.get("data")['auth_id']

        aogi = db.session.query(ApplicationOptionGroupItem).filter_by(id=aogi_id).first()
        if not aogi:
            return {"code": 30, "message": "Invalid Application Option Group Item ID", "status_code": 400}

        # Get the user's LDAP groups
        auth_source = db.session.query(AuthSource).filter_by(id=server_id).first()
        c = connect_to_ldap(auth_source.host, auth_source.bind_user_dn, auth_source.bind_password, port=auth_source.port, ssl=auth_source.ssl)
        if not c.bind():
            return {"code": 10, "message": "There was an error binding to the LDAP Server", "status_code": 500}

        uuids = [user_id] + get_user_groups(c, auth_source.base_dn, user_id, is_ad=auth_source.server_type == "ad", cascade=True)

        # Query applications based on user and group UUIDs
        application_access_records = (
            db.session.query(Access)
            .join(LdapObject, LdapObject.id == Access.ldap_object_id)
            .filter(LdapObject.object_uuid.in_(uuids))
            .all()
        )

        aog_ids = {record.access_to for record in application_access_records}

        # Query applications that the user or groups have access to
        data = (
            db.session.query(Application, ApplicationOptionGroup, ApplicationOptionGroupItem)
            .join(ApplicationOptionGroup, ApplicationOptionGroup.application_id == Application.id)
            .join(ApplicationOptionGroupItem, ApplicationOptionGroup.id == ApplicationOptionGroupItem.group_id)
            .filter(ApplicationOptionGroup.id.in_(aog_ids))
            .filter(ApplicationOptionGroupItem.id == aogi_id)
            .all()
        )

        if not data:
            return {"code": 20, "message": "User does not have access to this ApplicationOptionGroup", "status_code": 403}

        result = {
            'details': [
                {
                    'app_name': app.name,
                    'group_name': group.name,
                    'item_name': item.name,
                    'app_id': app.id,
                    'group_id': group.id,
                    'item_id': item.id,
                    'multiple_processes': app.multiple_processes,
                    'check_hash': app.check_hash,
                    'hashes': [app_hash.value for app_hash in app.hashes],
                    'paths': [app_path.value for app_path in app.paths]
                }
                for app, group, item in data
            ]
        }
        loggie.info(f"User {user_id} checked in to launch {result['details'][0]['app_name']}")
        return {"code": 0, "message": "Successfully received launch specification", "data": result}

    except Exception as e:
        return {"code": 70, "message": f"Unexpected error: {str(e)}", "status_code": 500}


def process_launch(aogi_id, identity, data):
    """Process the client’s request to launch an application."""
    try:
        user_id = identity.get("id")
        server_id = identity.get("data")['auth_id']

        application_hash = data.get('hash')
        application_path = data.get('path')

        auth_source = db.session.query(AuthSource).filter_by(id=server_id).first()
        c = connect_to_ldap(auth_source.host, auth_source.bind_user_dn, auth_source.bind_password, port=auth_source.port, ssl=auth_source.ssl)
        if not c.bind():
            return {"code": 10, "message": "There was an error binding to the LDAP Server", "status_code": 500}

        uuids = [user_id] + get_user_groups(c, auth_source.base_dn, user_id, is_ad=auth_source.server_type == "ad", cascade=True)
        c.unbind()

        result = (
            db.session.query(ApplicationOptionGroupItem)
            .join(ApplicationOptionGroup, ApplicationOptionGroup.id == ApplicationOptionGroupItem.group_id)
            .join(Application, Application.id == ApplicationOptionGroup.application_id)
            .join(Access, Access.access_to == ApplicationOptionGroup.id)
            .join(LdapObject, LdapObject.id == Access.ldap_object_id)
            .filter(ApplicationOptionGroupItem.id == aogi_id, LdapObject.object_uuid.in_(uuids))
            .first()
        )

        if not result:
            return {"code": 30, "message": "Not enough rights for your request", "status_code": 404}

        response_data = {
            "details": [
                {
                    "value": result.value,
                    "path": application_path,
                    "hash": application_hash
                }
            ]
        }

        loggie.info(
            message=f"User '{user_id}' launched '{result.group.application.name}' as '{result.group.name}' with config '{result.name}'",
            title="Application launch"
        )

        return {"code": 0, "message": "Successfully received launch details", "data": response_data}

    except Exception as e:
        return {"code": 70, "message": f"Unexpected error: {str(e)}", "status_code": 500}