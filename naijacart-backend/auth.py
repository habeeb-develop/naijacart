"""Minimal auth helpers for demo purposes.
This is NOT production-ready — only for local testing.
"""

VALID_TOKEN = "testtoken"

def login(email, password):
    # In a real app verify credentials; here accept any email and password 'password'
    if not email or password != "password":
        return None
    return VALID_TOKEN

def check_token(header_value):
    if not header_value:
        return False
    parts = header_value.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return False
    return parts[1] == VALID_TOKEN
