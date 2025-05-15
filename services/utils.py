import uuid
import random
import string
from marshmallow import Schema, fields, ValidationError


def validate_uuid(value):
    try:
        uuid.UUID(value)
    except ValueError:
        raise ValidationError("Invalid UUID format.")

def generate_random_string(length=12, use_uppercase=True, use_lowercase=True, use_digits=True, use_special=False):
    """Generates a secure random string."""
    char_set = ""
    if use_uppercase:
        char_set += string.ascii_uppercase
    if use_lowercase:
        char_set += string.ascii_lowercase
    if use_digits:
        char_set += string.digits
    if use_special:
        char_set += string.punctuation

    if not char_set:
        raise ValueError("At least one character set must be enabled.")

    return ''.join(random.choice(char_set) for _ in range(length))

def validate_server_type(value):
    allowed_types = ["ldap", "radius", "ad"]
    if value not in allowed_types:
        raise ValidationError(f"Invalid server type. Allowed values: {allowed_types}")
