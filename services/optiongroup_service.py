from models import db, Application, ApplicationOptionGroup
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from services.logger import loggie
from schemas import ApplicationOptionGroupSchema

def create_application_group(application_id, data):
    """Create a new application option group."""
    try:
        # Check if application exists
        application = db.session.get(Application, application_id)
        if not application:
            return {"code": 30, "message": "Application not found", "status_code": 404}

        # Validate schema
        schema = ApplicationOptionGroupSchema()
        validated_data = schema.load(data)

        # Create option group
        new_group = ApplicationOptionGroup(
            name=validated_data['name'],
            description=validated_data.get('description', ''),
            application_id=application_id
        )
        db.session.add(new_group)
        db.session.commit()

        return {"code": 0, "message": "Application group created successfully", "status_code": 201}

    except ValidationError as err:
        return {"code": 30, "message": "Validation error", "data": err.messages, "status_code": 400}
    except IntegrityError:
        db.session.rollback()
        return {"code": 50, "message": "Application group already exists", "status_code": 409}
    except Exception as e:
        loggie.error(f"Unexpected error creating application group: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}

def get_application_groups(application_id):
    """Retrieve all option groups for an application."""
    try:
        application = db.session.get(Application, application_id)
        if not application:
            return {"code": 30, "message": "Application not found", "status_code": 404}

        groups = ApplicationOptionGroup.query.filter_by(application_id=application_id).all()
        result = [
            {
                "id": group.id,
                "name": group.name,
                "description": group.description,
                "disabled": group.disabled,
                "created_at": group.created_at.isoformat(),
                "updated_at": group.updated_at.isoformat()
            }
            for group in groups
        ]

        return {"code": 0, "message": "Application groups retrieved successfully", "data": result, "status_code": 200}
    
    except Exception as e:
        loggie.error(f"Unexpected error retrieving application groups: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}

def update_application_group(application_id, group_id, data):
    """Update an application option group."""
    try:
        application = db.session.get(Application, application_id)
        if not application:
            return {"code": 30, "message": "Application not found", "status_code": 404}

        group = ApplicationOptionGroup.query.filter_by(id=group_id, application_id=application_id).first()
        if not group:
            return {"code": 30, "message": "Application group not found", "status_code": 404}

        schema = ApplicationOptionGroupSchema(partial=True)
        validated_data = schema.load(data)

        # Update fields
        group.name = validated_data.get('name', group.name)
        group.description = validated_data.get('description', group.description)
        group.disabled = validated_data.get('disabled', group.disabled)

        db.session.commit()

        return {"code": 0, "message": "Application group updated successfully", "status_code": 200}

    except ValidationError as err:
        return {"code": 30, "message": "Validation error", "data": err.messages, "status_code": 400}
    except IntegrityError:
        db.session.rollback()
        return {"code": 50, "message": "Database integrity error", "status_code": 409}
    except Exception as e:
        loggie.error(f"Unexpected error updating application group: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}

def delete_application_group(application_id, group_id):
    """Delete an application option group."""
    try:
        application = db.session.get(Application, application_id)
        if not application:
            return {"code": 30, "message": "Application not found", "status_code": 404}

        group = ApplicationOptionGroup.query.filter_by(id=group_id, application_id=application_id).first()
        if not group:
            return {"code": 30, "message": "Application group not found", "status_code": 404}

        db.session.delete(group)
        db.session.commit()

        return {"code": 0, "message": "Application group deleted successfully", "status_code": 200}
    
    except IntegrityError:
        db.session.rollback()
        return {"code": 50, "message": "Database integrity error", "status_code": 409}
    except Exception as e:
        loggie.error(f"Unexpected error deleting application group: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}
