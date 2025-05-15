from models import db, Application, ApplicationOptionGroup, ApplicationOptionGroupItem
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from services.logger import loggie
from schemas import ApplicationOptionGroupItemSchema

def add_application_group_item(application_id, group_id, data):
    """Add a new item to an application option group."""
    try:
        # Check if application exists
        application = db.session.get(Application, application_id)
        if not application:
            return {"code": 30, "message": "Application not found", "status_code": 404}

        # Check if group exists under the application
        group = db.session.get(ApplicationOptionGroup, group_id)
        if not group or group.application_id != application_id:
            return {"code": 30, "message": "Application group not found", "status_code": 404}

        # Validate schema
        schema = ApplicationOptionGroupItemSchema()
        validated_data = schema.load(data)

        sensitive = validated_data.get("sensitive", False)
        sensitive_mask = validated_data.get("sensitive_mask", None) if sensitive else None

        # Create new item
        new_item = ApplicationOptionGroupItem(
            name=validated_data["name"],
            value=validated_data["value"],
            sensitive=sensitive,
            sensitive_mask=sensitive_mask,
            group_id=group_id
        )
        db.session.add(new_item)
        db.session.commit()

        return {"code": 0, "message": "Item added to application group successfully", "status_code": 201}

    except ValidationError as err:
        return {"code": 30, "message": "Validation error", "data": err.messages, "status_code": 400}
    except IntegrityError:
        db.session.rollback()
        return {"code": 50, "message": "Item already exists in this group", "status_code": 409}
    except Exception as e:
        loggie.error(f"Unexpected error adding item to application group: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}

def get_application_group_items(application_id, group_id):
    """Retrieve all items for a specific application option group."""
    try:
        application = db.session.get(Application, application_id)
        if not application:
            return {"code": 30, "message": "Application not found", "status_code": 404}

        group = db.session.get(ApplicationOptionGroup, group_id)
        if not group or group.application_id != application_id:
            return {"code": 30, "message": "Application group not found", "status_code": 404}

        items = ApplicationOptionGroupItem.query.filter_by(group_id=group_id).all()
        result = [
            {
                "id": item.id,
                "name": item.name,
                "value": (
                    ''.join([
                        item.value[i] if i < len(item.sensitive_mask) and item.sensitive_mask[i] == 's' else '*'
                        for i in range(len(item.value))
                    ])
                    if item.sensitive and item.sensitive_mask else item.value
                ),
                "sensitive": item.sensitive,
            }
            for item in items
        ]

        return {"code": 0, "message": "Items retrieved successfully", "data": result, "status_code": 200}

    except Exception as e:
        loggie.error(f"Unexpected error retrieving application group items: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}

def update_application_group_item(application_id, group_id, item_id, data):
    """Update an existing item in an application option group."""
    try:
        application = db.session.get(Application, application_id)
        if not application:
            return {"code": 30, "message": "Application not found", "status_code": 404}

        group = db.session.get(ApplicationOptionGroup, group_id)
        if not group or group.application_id != application_id:
            return {"code": 30, "message": "Application group not found", "status_code": 404}

        item = db.session.get(ApplicationOptionGroupItem, item_id)
        if not item or item.group_id != group_id:
            return {"code": 30, "message": "Item not found", "status_code": 404}

        # Validate schema
        schema = ApplicationOptionGroupItemSchema(partial=True)
        validated_data = schema.load(data)
        
        new_value = validated_data.get("value", item.value)
        if new_value != item.value:
            # If value is updated, reset the sensitive mask
            item.sensitive_mask = None


        # Update fields
        item.name = validated_data.get("name", item.name)
        item.value = validated_data.get("value", item.value)

        db.session.commit()

        return {"code": 0, "message": "Item updated successfully", "status_code": 200}

    except ValidationError as err:
        return {"code": 30, "message": "Validation error", "data": err.messages, "status_code": 400}
    except IntegrityError:
        db.session.rollback()
        return {"code": 50, "message": "Database integrity error", "status_code": 409}
    except Exception as e:
        loggie.error(f"Unexpected error updating application group item: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}

def delete_application_group_item(application_id, group_id, item_id):
    """Delete an item from an application option group."""
    try:
        application = db.session.get(Application, application_id)
        if not application:
            return {"code": 30, "message": "Application not found", "status_code": 404}

        group = db.session.get(ApplicationOptionGroup, group_id)
        if not group or group.application_id != application_id:
            return {"code": 30, "message": "Application group not found", "status_code": 404}

        item = db.session.get(ApplicationOptionGroupItem, item_id)
        if not item or item.group_id != group_id:
            return {"code": 30, "message": "Item not found", "status_code": 404}

        db.session.delete(item)
        db.session.commit()

        return {"code": 0, "message": "Item deleted successfully", "status_code": 200}

    except IntegrityError:
        db.session.rollback()
        return {"code": 50, "message": "Database integrity error", "status_code": 409}
    except Exception as e:
        loggie.error(f"Unexpected error deleting application group item: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}