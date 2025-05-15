import uuid
from models import db, ServerConfig
from services.logger import loggie

def ensure_server_config():
    """Ensure there is a ServerConfig row in the database."""
    config = ServerConfig.query.first()
    if not config:
        config = ServerConfig()
        db.session.add(config)
        db.session.commit()
    return config


def apply_license(license_key):
    """Apply a new license key."""
    if not license_key:
        return {"code": 30, "message": "License key is required", "status_code": 400}

    if not is_valid_uuid(license_key):
        return {"code": 30, "message": "Invalid license key format", "status_code": 400}

    # Placeholder: Check with external license validation server
    # tbd - Validate license with remote server

    config = ensure_server_config()
    config.license_key = license_key
    db.session.commit()

    loggie.info(f"License key applied: {license_key}")
    return {"code": 0, "message": "License key applied successfully", "status_code": 200}


def get_license():
    """Retrieve the current license key."""
    config = ensure_server_config()
    
    if not config.license_key:
        return {"code": 30, "message": "No license key found", "status_code": 404}

    return {"code": 0, "message": "License key retrieved successfully", "data": {"license_key": config.license_key}, "status_code": 200}


def remove_license():
    """Delete the current license key."""
    config = ensure_server_config()

    if not config.license_key:
        return {"code": 30, "message": "No license key found", "status_code": 404}

    config.license_key = None
    db.session.commit()

    loggie.info("License key removed")
    return {"code": 0, "message": "License key deleted successfully", "status_code": 200}


def update_license(license_key):
    """Change the license key."""
    if not license_key:
        return {"code": 30, "message": "License key is required", "status_code": 400}

    if not is_valid_uuid(license_key):
        return {"code": 30, "message": "Invalid license key format", "status_code": 400}

    config = ensure_server_config()

    if not config.license_key:
        return {"code": 30, "message": "No existing license key found", "status_code": 404}

    config.license_key = license_key
    db.session.commit()

    loggie.info(f"License key updated: {license_key}")
    return {"code": 0, "message": "License key changed successfully", "status_code": 200}


def is_valid_uuid(value):
    """Check if a string is a valid UUID."""
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False