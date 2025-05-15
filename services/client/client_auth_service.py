from models import db, AuthSource, TwoFaSources
from services.ldap_service import connect_to_ldap, validate_credentials
from services.auth_service import token_creator
from services.logger import loggie
from services.twofa_service import validate_twofa
from schemas import TwoFaValidatorSchema
import json
twofa_validator_schema = TwoFaValidatorSchema()


def authenticate_client(data):
    """Authenticate client using multiple authentication sources."""
    try:
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"code": 30, "message": "Username and password are required", "status_code": 400}

        auth_sources = db.session.query(AuthSource).all()
        twofa_enabled = db.session.query(TwoFaSources).filter_by(disabled=False).first() is not None

        for server in auth_sources:
            try:
                loggie.info(f"Attempting login for {username} via {server.host}")

                # Connect to LDAP
                ldap_server = connect_to_ldap(server.host, server.bind_user_dn, server.bind_password, port=server.port, ssl=server.ssl)
                if not ldap_server.bind():
                    loggie.warning(f"Failed to bind to {server.host}. Skipping.")
                    continue

                # Validate credentials
                result = validate_credentials(
                    server.host, ldap_server, server.base_dn, username, password,
                    is_ad=(server.server_type == "ad"), port=server.port, ssl=server.ssl
                )

                if result.get("success"):
                    loggie.info(f"User {username} authenticated successfully on {server.host}")

                    # Assign role based on whether 2FA is required
                    role = "client_semi" if twofa_enabled else "client"

                    # Generate JWT token
                    access_token = token_creator(result["data"][0]["uuid"], role, data={"auth_id": server.id})

                    return {
                        "code": 0,
                        "message": "Successfully logged in",
                        "data": {
                            "access_token": access_token,
                            "username": str(result["data"][0]["id"]),
                            "requires_twofa": twofa_enabled
                        },
                        "status_code": 200
                    }

            except Exception as e:
                loggie.error(f"Error connecting to {server.host}: {str(e)}")

        # If no successful authentication occurred
        return {"code": 30, "message": "Invalid credentials", "status_code": 401}

    except Exception as e:
        loggie.error(f"Unexpected error during login: {str(e)}")
        return {"code": 70, "message": "Failed to login due to an unexpected error", "status_code": 500}
    

def authenticate_client_twofa(data, identity):
    """Authenticate client using multiple authentication sources."""
    try:
        validated_data = twofa_validator_schema.load(data)
        json_identity = json.loads(identity)

        user = validated_data.get("user")
        code = validated_data.get("code")
        user_id = json_identity.get("id")
        user_data = json_identity.get("data")

        if not user or not code:
            return {"code": 30, "message": "User and Code are required", "status_code": 400}
        
        validation = validate_twofa(data)
        if validation.get("code") != 0:
            return {"code": 0, "message": "Invalid credentials", "status_code": 401}
        
        access_token = token_creator(user_id, 'client', data=user_data)

        
        
        return {
            "code": 0,
            "message": "Successfully logged in",
            "data": {
                "access_token": access_token,
                "username": user_id,
                "requires_twofa": False
            },
            "status_code": 200
        }
    except Exception as e:
        loggie.error(f"Unexpected error during twofa login: {str(e)}")
        return {"code": 30, "message": f"There was an error: {str(e)}", "status_code": 400}
