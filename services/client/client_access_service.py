from models import db, Application, AccessRequest, LdapObject
from services.response_service import make_response
from services.auth_service import jwt_decoder
from services.ldap_service import handle_ldap_object

def get_requestable_applications(identity):
    """Retrieve applications that the client can request access to."""
    try:
        user_id = identity.get("id")
        server_id = identity.get("data")["auth_id"]

        # Fetch applications with request access enabled
        applications = db.session.query(Application).filter(Application.allow_request_access).all()

        # Fetch user's existing access requests
        requests = (
            db.session.query(AccessRequest, Application)
            .join(Application, AccessRequest.application_id == Application.id)
            .join(LdapObject, LdapObject.id == AccessRequest.ldap_object_id)
            .filter(LdapObject.object_uuid == user_id)
            .all()
        )

        # Prepare response data
        data = {
            'applications': [
                {'id': app.id, 'name': app.name, 'image': app.image}
                for app in applications
            ],
            'requests': [
                {'application_id': req.application_id, 'application_name': app.name}
                for req, app in requests
            ]
        }

        return make_response(code=0, message="Requestable applications retrieved successfully", data=data)

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return make_response(code=70, message="An unexpected error occurred", status_code=500)


def create_access_request(data, identity):
    """Process a client's request to access an application."""
    try:
        user_id = identity.get("id")
        server_id = identity.get("data")["auth_id"]

        application_id = data.get("application_id")
        if not application_id:
            return make_response(code=30, message="Application ID is required", status_code=400)

        # Validate application existence
        application = db.session.query(Application).filter(Application.id == application_id).first()
        if not application:
            return make_response(code=30, message=f"No application found with ID {application_id}", status_code=400)

        # Check for existing request
        existing_request = (
            db.session.query(AccessRequest)
            .join(LdapObject, LdapObject.id == AccessRequest.ldap_object_id)
            .filter(AccessRequest.application_id == application_id, LdapObject.object_uuid == user_id)
            .first()
        )

        if existing_request:
            return make_response(code=30, message="Access request already exists", status_code=400)

        # Create or retrieve LDAP object
        ldap_object = handle_ldap_object(uuid=user_id, auth_source_id=server_id)
        if not ldap_object:
            return make_response(code=30, message="Error adding this user", status_code=400)

        # Create new access request
        new_access_request = AccessRequest(application_id=application_id, ldap_object_id=ldap_object.id)
        db.session.add(new_access_request)
        db.session.commit()

        return make_response(code=0, message="Access request added successfully", status_code=201)

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return make_response(code=70, message="An unexpected error occurred", status_code=500)