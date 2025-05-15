from models import db, SmtpServer
from services.logger import loggie
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from marshmallow import ValidationError
from schemas import SmtpSchema

smtp_schema = SmtpSchema()
smtp_list_schema = SmtpSchema(many=True)

def create_smtp_server(data):
    """Create a new SMTP server."""
    try:
        # Validate data
        validated_data = smtp_schema.load(data)
        
        # Validate security protocol
        if validated_data["security"].upper() not in ["SSL", "STARTTLS", "NONE"]:
            return {"code": 30, "message": "Invalid security protocol. Allowed: 'SSL', 'STARTTLS', 'NONE'", "status_code": 400}
        
        # Create and save the new SMTP server
        new_smtp_server = SmtpServer(**validated_data)

        with db.session.begin_nested():
            db.session.add(new_smtp_server)
            db.session.commit()

        loggie.info(f"New SMTP server added: {validated_data['name']}")
        return {"code": 0, "message": "SMTP server added successfully", "status_code": 201}

    except ValidationError as e:
        return {"code": 40, "message": "Invalid request data", "data": e.messages, "status_code": 400}
    except IntegrityError:
        db.session.rollback()
        return {"code": 50, "message": "SMTP server with the same name already exists", "status_code": 409}
    except Exception as e:
        loggie.error(f"Unexpected error creating SMTP server: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}

def get_smtp_servers():
    """Retrieve all SMTP servers."""
    try:
        smtp_servers = SmtpServer.query.all()
        return {
            "code": 0,
            "message": "SMTP servers retrieved successfully",
            "data": smtp_list_schema.dump(smtp_servers),
            "status_code": 200,
        }
    except Exception as e:
        loggie.error(f"Unexpected error fetching SMTP servers: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}

def update_smtp_server(smtp_id, data):
    """Update an SMTP server."""
    try:
        smtp_server = db.session.get(SmtpServer, smtp_id)
        if not smtp_server:
            return {"code": 40, "message": "SMTP server not found", "status_code": 404}

        # Validate and update fields
        validated_data = smtp_schema.load(data, partial=True)
        for key, value in validated_data.items():
            setattr(smtp_server, key, value)

        db.session.commit()
        loggie.info(f"SMTP server updated: {smtp_server.name}")
        return {"code": 0, "message": "SMTP server updated successfully", "status_code": 200}

    except ValidationError as e:
        return {"code": 40, "message": "Invalid request data", "data": e.messages, "status_code": 400}
    except Exception as e:
        loggie.error(f"Unexpected error updating SMTP server: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}

def delete_smtp_server(smtp_id):
    """Delete an SMTP server."""
    try:
        smtp_server = db.session.get(SmtpServer, smtp_id)
        if not smtp_server:
            return {"code": 40, "message": "SMTP server not found", "status_code": 404}

        db.session.delete(smtp_server)
        db.session.commit()

        loggie.info(f"SMTP server deleted: {smtp_server.name}")
        return {"code": 0, "message": "SMTP server deleted successfully", "status_code": 200}

    except Exception as e:
        loggie.error(f"Unexpected error deleting SMTP server: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}