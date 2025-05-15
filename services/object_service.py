from models import db, LdapObject
from services.logger import loggie
from schemas import LdapObjectSchema, LdapObjectDTOSchema

# Create an instance of the schema
ldap_object_listschema = LdapObjectSchema(many=True)

def get_all_objects():
    """Retrieve all objects from LdapObjects table."""
    try:
        objects = LdapObject.query.all()
        return {
            "code": 0,
            "message": "Objects retrieved successfully",
            "data": ldap_object_listschema.dump(objects),
            "status_code": 200,
        }
    except Exception as e:
        loggie.error(f"Unexpected error fetching objects: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}