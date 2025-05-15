import re

def check_password_strength(password):
    """Checks if a password meets security requirements."""
    if len(password) < 8 or not any(c.islower() for c in password) or not any(c.isupper() for c in password) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True
