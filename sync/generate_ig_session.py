"""
Run this script once on your local machine to generate an Instagram session.
The output is a JSON string — paste it as the INSTAGRAM_SESSION GitHub secret.

Usage:
    pip install instagrapi
    python sync/generate_ig_session.py
"""

import json
import getpass
from instagrapi import Client

username = input("Instagram username: ")
password = getpass.getpass("Instagram password: ")

cl = Client()
try:
    cl.login(username, password)
except Exception as e:
    code = input(f"Instagram sent a verification code (check email/SMS). Enter it: ")
    cl.challenge_resolve(cl.last_json, code)

session = cl.get_settings()
print("\n--- Copy everything below this line and paste it as INSTAGRAM_SESSION ---\n")
print(json.dumps(session))
print("\n--- End of session JSON ---")
