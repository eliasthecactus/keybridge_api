from models import db, TwoFaSources
from services.logger import loggie
from schemas import TwoFaSourceSchema, TwoFaValidatorSchema
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
import requests
from requests.exceptions import RequestException
import json

# Initialize schemas
twofa_schema = TwoFaSourceSchema()
twofa_validator_schema = TwoFaValidatorSchema()

twofa_list_schema = TwoFaSourceSchema(many=True)

def create_twofa_source(data):
    """Create a new 2FA source."""
    try:
        validated_data = twofa_schema.load(data)

        new_source = TwoFaSources(**validated_data)
        db.session.add(new_source)
        db.session.commit()

        loggie.info(f"New 2FA source added: {validated_data['name']}")
        return {"code": 0, "message": "2FA source added successfully", "status_code": 201}

    except ValidationError as e:
        return {"code": 40, "message": "Invalid request data", "data": e.messages, "status_code": 400}
    except IntegrityError:
        db.session.rollback()
        return {"code": 50, "message": "2FA source already exists", "status_code": 409}
    except Exception as e:
        loggie.error(f"Unexpected error adding 2FA source: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}

def get_twofa_sources():
    """Retrieve all 2FA sources."""
    try:
        sources = TwoFaSources.query.all()
        return {
            "code": 0,
            "message": "2FA sources retrieved successfully",
            "data": twofa_list_schema.dump(sources),
            "status_code": 200,
        }
    except Exception as e:
        loggie.error(f"Unexpected error fetching 2FA sources: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}

def get_twofa_source(twofa_id):
    """Retrieve a single 2FA source."""
    source = db.session.get(TwoFaSources, twofa_id)
    if not source:
        return {"code": 40, "message": "2FA source not found", "status_code": 404}

    return {
        "code": 0,
        "message": "2FA source retrieved successfully",
        "data": twofa_schema.dump(source),
        "status_code": 200,
    }

def update_twofa_source(twofa_id, data):
    """Update an existing 2FA source."""
    try:
        source = db.session.get(TwoFaSources, twofa_id)
        if not source:
            return {"code": 40, "message": "2FA source not found", "status_code": 404}

        validated_data = twofa_schema.load(data, partial=True)

        for key, value in validated_data.items():
            setattr(source, key, value)

        db.session.commit()
        loggie.info(f"2FA source updated: {source.name}")
        return {"code": 0, "message": "2FA source updated successfully", "status_code": 200}

    except Exception as e:
        loggie.error(f"Unexpected error updating 2FA source: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}

def delete_twofa_source(twofa_id):
    """Delete a 2FA source."""
    try:
        source = db.session.get(TwoFaSources, twofa_id)
        if not source:
            return {"code": 40, "message": "2FA source not found", "status_code": 404}

        db.session.delete(source)
        db.session.commit()

        loggie.info(f"2FA source deleted: {source.name}")
        return {"code": 0, "message": "2FA source deleted successfully", "status_code": 200}

    except Exception as e:
        loggie.error(f"Unexpected error deleting 2FA source: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}
    
def validate_twofa(twofa_data):
    """Validate 2FA data against the configured source."""
    try:
        source = TwoFaSources.query.filter_by(disabled=False).first()
        if not source:
            return {"code": 40, "message": "2FA source not found", "status_code": 404}

        validated_data = twofa_validator_schema.load(twofa_data)
        user = validated_data.get('user')
        code = validated_data.get('code')

        # Validate the 2FA data against the configured source
        if source.type == "linotp":
            if linotp_validator(source.host, source.port, source.ssl, source.realm, user, code):
                return {"code": 0, "message": "2FA code is valid", "status_code": 200}
            return {"code": 40, "message": "Invalid 2FA code", "status_code": 401}
        else:
            return {"code": 40, "message": "Invalid 2FA source type", "status_code": 400}

    except ValidationError as e:
        return {"code": 40, "message": "Invalid request data", "data": e.messages, "status_code": 400}
    except Exception as e:
        loggie.error(f"Unexpected error during 2FA validation: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}

def linotp_validator(host, port, ssl, realm, user, code):
    """
    Validate a users 2FA code against LinOTP.
    
    :param host: LinOTP server host
    :param port: LinOTP server port
    :param ssl: Boolean indicating whether to use HTTPS
    :param realm: The realm for LinOTP authentication
    :param user: The username
    :param code: The 2FA code
    :return: Response from LinOTP server
    """
    try:
        protocol = "https" if ssl else "http"
        url = f"{protocol}://{host}:{port}/validate/check"
        
        payload = {
            "user": user,
            "pass": str(code),
            "realm": realm
        }
        print(payload)
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        
        # Raise an error if the request failed
        response.raise_for_status()
        
        result = response.json()
        
        # Check LinOTP response
        if result.get("result", {}).get("status") is True and result.get("result", {}).get("value") is True:
            loggie.info(f"Successfully validated 2FA with user {str(user)} on realm {str(realm)}")
            return True
        else:
            loggie.error(f"2FA validation failed for user {str(user)} on realm {str(realm)}")
            return False
    
    except RequestException as e:
        return False