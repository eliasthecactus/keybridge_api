from models import db, AuthSource, ApplicationOptionGroup, Access, LdapObject
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from marshmallow import ValidationError
from services.ldap_service import handle_ldap_object
from services.logger import loggie

def add_access_right(data):
    """Add access rights for a user or group to an application option group."""
    try:
        auth_source_id = data.get('auth_source_id')
        object_uuid = data.get('object_uuid')
        access_to = data.get('access_to')

        if not all([auth_source_id, object_uuid, access_to]):
            return {"code": 30, "message": "All fields are required", "status_code": 400}

        auth_source = db.session.get(AuthSource, auth_source_id)
        if not auth_source:
            return {"code": 40, "message": "AuthSource not found", "status_code": 404}

        app_option_group = db.session.get(ApplicationOptionGroup, access_to)
        if not app_option_group:
            return {"code": 41, "message": "ApplicationOptionGroup not found", "status_code": 404}

        ldap_object = handle_ldap_object(object_uuid, auth_source_id)
        if not ldap_object:
            return {"code": 50, "message": "There was an error while adding this account", "status_code": 409}

        existing_access = db.session.query(Access).filter_by(
            ldap_object_id=ldap_object.id,
            access_to=access_to
        ).first()

        if existing_access:
            return {"code": 50, "message": "Access right already exists", "status_code": 409}

        new_access = Access(
            ldap_object_id=ldap_object.id,
            access_to=access_to
        )

        db.session.add(new_access)
        db.session.commit()

        return {"code": 0, "message": "Access right added successfully", "status_code": 201}

    except IntegrityError:
        db.session.rollback()
        return {"code": 50, "message": "Database integrity error", "status_code": 409}
    except SQLAlchemyError as e:
        loggie.error(f"Database error: {str(e)}")
        return {"code": 70, "message": "A database error occurred", "status_code": 500}
    except Exception as e:
        loggie.error(f"Unexpected error adding access right: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}

def get_access_rights(params):
    """Retrieve access rights with optional filtering."""
    try:
        filters = []
        auth_source_id = params.get('auth_source_id')
        object_type = params.get('object_type')
        object_uuid = params.get('object_uuid')
        application_id = params.get('application_id')
        name = params.get('name')
        access_to = params.get('access_to')

        query = db.session.query(Access).join(LdapObject, Access.ldap_object_id == LdapObject.id)

        if auth_source_id:
            filters.append(LdapObject.auth_source_id == int(auth_source_id))
        if object_type:
            filters.append(LdapObject.object_type == object_type)
        if object_uuid:
            filters.append(LdapObject.object_uuid == object_uuid)
        if name:
            filters.append(LdapObject.name.ilike(f"%{name}%"))
        if access_to:
            filters.append(Access.access_to == int(access_to))

        if application_id:
            query = query.join(ApplicationOptionGroup, Access.access_to == ApplicationOptionGroup.id)
            query = query.filter(ApplicationOptionGroup.application_id == int(application_id))

        query = query.filter(*filters)
        access_rights = query.all()

        results = [
            {
                "id": access.id,
                "ldap_object_id": access.ldap_object_id,
                "auth_source_id": access.ldap_object.auth_source_id,
                "object_type": access.ldap_object.object_type,
                "object_uuid": access.ldap_object.object_uuid,
                "name": access.ldap_object.name,
                "access_to": access.access_to
            }
            for access in access_rights
        ]

        return {"code": 0, "message": "Access rights retrieved successfully", "status_code": 200, "data": results}

    except Exception as e:
        loggie.error(f"Unexpected error retrieving access rights: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}

def delete_access_right(access_id):
    """Delete a specific access right by ID."""
    try:
        access_right = db.session.get(Access, access_id)
        if not access_right:
            return {"code": 40, "message": "Access right not found", "status_code": 404}

        db.session.delete(access_right)
        db.session.commit()

        return {"code": 0, "message": "Access right deleted successfully", "status_code": 200}

    except Exception as e:
        loggie.error(f"Unexpected error deleting access right: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}