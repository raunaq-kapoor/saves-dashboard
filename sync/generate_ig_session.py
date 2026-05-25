"""
Run this ONCE locally to generate an Instagram mobile session for GitHub Actions.
Paste the printed JSON as the INSTAGRAM_SESSION GitHub secret.

Usage:
    pip install instagrapi Pillow
    python sync/generate_ig_session.py

This creates a proper instagrapi mobile-API session. Do NOT replace this with
a sessionid cookie from instagram.com — that is a web cookie and is rejected
by the mobile API with HTTP 467.
"""

import json
import getpass
from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, TwoFactorRequired

username = input("Instagram username: ").strip()
password = getpass.getpass("Instagram password: ")

cl = Client()

try:
    cl.login(username, password)
except TwoFactorRequired:
    code = input("Two-factor code (from your authenticator app or SMS): ").strip()
    cl.login(username, password, verification_code=code)
except ChallengeRequired:
    print("\nInstagram sent a security challenge.")
    print("Check your Instagram app — there should be a notification asking you to confirm the login.")
    input("Press Enter once you have approved it in the app...")
    cl.challenge_resolve(cl.last_json)

settings = cl.get_settings()

print("\n--- Copy everything between the dashes and paste as INSTAGRAM_SESSION ---\n")
print(json.dumps(settings))
print("\n--- End ---")
print("\nAlso add INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD as GitHub secrets.")
