from marshmallow import Schema, fields, validate, ValidationError, validates_schema
from services.utils import validate_uuid, validate_server_type

class ApplicationSchema(Schema):
    name = fields.String(required=True, error_messages={"required": "Name is required."})
    path = fields.List(fields.String(), required=True, error_messages={"required": "Path is required."})
    hash = fields.List(fields.String(), required=False)
    check_hash = fields.Boolean(missing=False)
    multiple_processes = fields.Boolean(missing=False)
    allow_request_access = fields.Boolean(missing=False)
    disabled = fields.Boolean(missing=False)

class ApplicationOptionGroupSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    description = fields.Str(allow_none=True, validate=validate.Length(max=255))
    disabled = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class ApplicationOptionGroupItemSchema(Schema):
    """Schema for validating application option group item requests."""

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    value = fields.Str(required=True, validate=validate.Length(min=1, max=240))
    sensitive = fields.Bool(required=False)
    sensitive_mask = fields.Str(
        required=False,
        validate=validate.Length(min=1, max=240),
        error_messages={"invalid": "Sensitive mask must be a string with valid length."}
    )

    def validate_sensitive_mask(self, data, **kwargs):
        """Custom validation for sensitive mask when 'sensitive' is True."""
        if data.get("sensitive", False):
            if "sensitive_mask" not in data or not data["sensitive_mask"]:
                raise ValidationError("Sensitive item must have a sensitive mask.")

            if len(data["value"]) != len(data["sensitive_mask"]):
                raise ValidationError("Sensitive mask must match the length of the value.")

            if not all(char in ["s", "h"] for char in set(data["sensitive_mask"])):
                raise ValidationError("Sensitive mask must only contain 's' (show) and 'h' (hide).")

        return data
    
class ApplicationOptionGroupItemSchema(Schema):
    """Schema for validating application option group item requests."""

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    value = fields.Str(required=True, validate=validate.Length(min=1, max=240))
    sensitive = fields.Bool(required=False)
    sensitive_mask = fields.Str(
        required=False,
        validate=validate.Length(min=1, max=240),
        error_messages={"invalid": "Sensitive mask must be a string with valid length."}
    )
    @validates_schema
    def validate_sensitive_mask(self, data, **kwargs):
        """Custom validation for sensitive mask when 'sensitive' is True."""
        if data.get("sensitive", False):
            if "sensitive_mask" not in data or not data["sensitive_mask"]:
                raise ValidationError("Sensitive item must have a sensitive mask.", field_name="sensitive_mask")

            if len(data["value"]) != len(data["sensitive_mask"]):
                raise ValidationError("Sensitive mask must match the length of the value.", field_name="sensitive_mask")

            if not all(char in ["s", "h"] for char in set(data["sensitive_mask"])):
                raise ValidationError("Sensitive mask must only contain 's' (show) and 'h' (hide).", field_name="sensitive_mask")
        return data

class LicenseSchema(Schema):
    """Schema for validating license key requests."""
    license_key = fields.String(required=True, validate=validate_uuid)


class AuthSourceSchema(Schema):
    """Schema for validating authentication source requests."""
    id = fields.Int(dump_only=True)  # Only for responses, not input
    name = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    server_type = fields.Str(required=True, validate=validate_server_type)
    description = fields.Str(validate=validate.Length(max=255), allow_none=True)
    ssl = fields.Boolean(missing=False)  # Defaults to False if not provided
    port = fields.Int(required=True, validate=validate.Range(min=1, max=65535))
    host = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    bind_user_dn = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    bind_password = fields.Str(required=True, validate=validate.Length(min=1, max=255), load_only=True)
    base_dn = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    disabled = fields.Boolean(missing=False)


class SyslogSchema(Schema):
    """Schema for validating Syslog server requests."""
    id = fields.Int(dump_only=True)  # Only for responses
    name = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    host = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    port = fields.Int(required=True, validate=validate.Range(min=1, max=65535))
    protocol = fields.Str(required=True, validate=validate.OneOf(["tcp", "udp"]))
    disabled = fields.Boolean(missing=False)

class SmtpSchema(Schema):
    """Schema for validating SMTP server requests."""
    id = fields.Int(dump_only=True)  # Only for responses
    name = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    host = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    port = fields.Int(required=True, validate=validate.Range(min=1, max=65535))
    username = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    password = fields.Str(required=True, validate=validate.Length(min=3, max=255), load_only=True)
    from_email = fields.Email(required=True)
    security = fields.Str(required=True, validate=validate.OneOf(["SSL", "STARTTLS", "NONE"]))
    
class LdapObjectSchema(Schema):
    """Schema for serializing LdapObject instances."""
    id = fields.Int(dump_only=True)
    auth_source_id = fields.Int(required=True)
    object_type = fields.Str(required=True, validate=validate.OneOf(["user", "group"]))
    object_uuid = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=80))
    ldap_uid = fields.Str(required=True, validate=validate.Length(min=1, max=80))
    data_fetched_at = fields.DateTime(dump_only=True)
    two_factor_data = fields.Str(allow_none=True)

    class Meta:
        ordered = True

class LdapObjectDTOSchema(Schema):
    """DTO Schema for returning limited LdapObject data."""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    object_type = fields.Str(required=True)
    object_uuid = fields.Str(required=True)

    class Meta:
        ordered = True  # Ensures JSON output is properly ordered

class TwoFaSourceSchema(Schema):
    """Schema for validating 2FA sources."""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    host = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    port = fields.Int(required=False, validate=validate.Range(min=1, max=65535), missing=443)
    ssl = fields.Boolean(missing=True)  # Default True
    disabled = fields.Boolean(missing=False)  # Default False
    type = fields.Str(required=True, validate=validate.OneOf(["linotp"], error="Type must be one of: linotp"), error_messages={"required": "Type is required.", "invalid": "Invalid type format."} )
    realm = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    
class TwoFaValidatorSchema(Schema):
    user = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    code = fields.Int(required=True, validate=validate.Range(min=1, max=99999999))
    