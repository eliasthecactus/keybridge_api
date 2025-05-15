import base64
from io import BytesIO
from models import db, Application, ApplicationPath, ApplicationHash
from services.logger import loggie
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from marshmallow import ValidationError
from schemas import ApplicationSchema
from PIL import Image

application_schema = ApplicationSchema()
application_partial_schema = ApplicationSchema(partial=True)

### ADD APPLICATION ###
def create_application(data):
    """Create a new application"""
    try:
        # Validate input
        validated_data = application_schema.load(data)

        name = validated_data['name']
        paths = validated_data['path']
        allow_request_access = validated_data['allow_request_access']
        hash_list = validated_data.get('hash', [])
        check_hash = validated_data['check_hash']
        multiple_processes = validated_data['multiple_processes']
        disabled = validated_data['disabled']

        if check_hash and not hash_list:
            return {"code": 40, "message": "Hash is needed if hash check is enabled", "status_code": 400}

        # Check for duplicate
        if Application.query.filter_by(name=name).first():
            return {"code": 50, "message": f"Application with name {name} already exists", "status_code": 409}

        new_application = Application(
            name=name,
            check_hash=check_hash,
            allow_request_access=allow_request_access,
            multiple_processes=multiple_processes,
            disabled=disabled
        )

        for path in paths:
            new_application.paths.append(ApplicationPath(value=path))
        for hash_value in hash_list:
            new_application.hashes.append(ApplicationHash(value=hash_value))

        db.session.add(new_application)
        db.session.commit()
        loggie.info(f"Application '{name}' added successfully")
        return {"code": 0, "message": "Application added successfully", "status_code": 201}

    except ValidationError as e:
        return {"code": 30, "message": "Validation error", "data": e.messages, "status_code": 400}
    except IntegrityError:
        db.session.rollback()
        return {"code": 50, "message": "Application with this name already exists", "status_code": 409}
    except Exception as e:
        loggie.error(f"Unexpected error: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}

### GET APPLICATION(S) ###
def get_applications(application_id=None):
    """Retrieve applications"""
    try:
        if application_id:
            application = db.session.get(Application, application_id)
            if not application:
                return {"code": 30, "message": "Application not found", "status_code": 404}

            # Convert the application to a dict including paths & hashes
            result = {
                "id": application.id,
                "name": application.name,
                "path": [path.value for path in application.paths],  # Get all paths
                "hash": [hash.value for hash in application.hashes],  # Get all hashes
                "allow_request_access": application.allow_request_access,
                "check_hash": application.check_hash,
                "image": application.image,
                "multiple_processes": application.multiple_processes,
                "disabled": application.disabled,
            }
        else:
            # Query all applications and include their paths & hashes
            applications = Application.query.all()
            result = [
                {
                    "id": app.id,
                    "name": app.name,
                    "path": [path.value for path in app.paths],  # Get all paths
                    "hash": [hash.value for hash in app.hashes],  # Get all hashes
                    "allow_request_access": app.allow_request_access,
                    "check_hash": app.check_hash,
                    "image": app.image,
                    "multiple_processes": app.multiple_processes,
                    "disabled": app.disabled,
                }
                for app in applications
            ]

        return {"code": 0, "message": "Applications retrieved successfully", "data": result, "status_code": 200}

    except Exception as e:
        loggie.error(f"Error retrieving applications: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}
    
### UPDATE APPLICATION ###
def update_application(application_id, data):
    """Modify an existing application"""
    try:
        application = db.session.get(Application, application_id)
        if not application:
            return {"code": 30, "message": "Application not found", "status_code": 404}

        validated_data = application_partial_schema.load(data)
        for key, value in validated_data.items():
            setattr(application, key, value)
        
        # Update paths if provided
        if 'path' in validated_data:
            application.paths.clear()  # Remove old paths
            for path in validated_data['path']:
                application.paths.append(ApplicationPath(value=path))

        # Update hashes if provided
        if 'hash' in validated_data:
            application.hashes.clear()  # Remove old hashes
            for hash_value in validated_data['hash']:
                application.hashes.append(ApplicationHash(value=hash_value))


        db.session.commit()
        loggie.info(f"Application '{application.name}' updated successfully")

        return {"code": 0, "message": "Application updated successfully", "status_code": 200}

    except ValidationError as e:
        return {"code": 30, "message": "Validation error", "data": e.messages, "status_code": 400}
    except Exception as e:
        loggie.error(f"Unexpected error: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}

### DELETE APPLICATION ###
def delete_application(application_id):
    """Delete an application"""
    try:
        application = db.session.get(Application, application_id)
        if not application:
            return {"code": 30, "message": "Application not found", "status_code": 404}

        db.session.delete(application)
        db.session.commit()
        loggie.info(f"Application '{application.name}' deleted successfully")
        return {"code": 0, "message": "Application deleted successfully", "status_code": 200}

    except Exception as e:
        loggie.error(f"Unexpected error: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}

### ADD APPLICATION IMAGE ###
def add_application_image(application_id, files):
    """Upload an application image"""
    try:
        file = files.get('image')
        if not file:
            return {"code": 20, "message": "No image file provided", "status_code": 400}

        # Validate and process image
        image = Image.open(file.stream)
        image = image.resize((512, 512), Image.Resampling.LANCZOS)

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        encoded_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

        application = db.session.get(Application, application_id)
        application.image = encoded_image
        db.session.commit()

        return {"code": 0, "message": "Application image uploaded successfully", "status_code": 200}

    except Exception as e:
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}

### REMOVE APPLICATION IMAGE ###
def remove_application_image(application_id):
    """Remove an application image"""
    try:
        application = db.session.get(Application, application_id)
        application.image = None
        db.session.commit()

        return {"code": 0, "message": "Application image removed successfully", "status_code": 200}
    except Exception as e:
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}