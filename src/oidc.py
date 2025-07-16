"""
OIDC implementation for University Central Directory (UCD) authentication.
Authenticates @cam.ac.uk accounts via UCD OIDC.
"""

import requests
import secrets
from urllib.parse import urlencode
from src import config


TENANT_ID = "49a50445-bdfa-4b79-ade3-547b4f3986e9"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
AUTHORIZE_ENDPOINT = f"{AUTHORITY}/oauth2/v2.0/authorize"
TOKEN_ENDPOINT = f"{AUTHORITY}/oauth2/v2.0/token"
GRAPH_ENDPOINT = "https://graph.microsoft.com/v1.0"

# https://help.uis.cam.ac.uk/service/accounts-passwords/it-staff/university-central-directory/understanding-users-and-groups
UOC_USERS_STUDENT = "0cbcd7fb-1f17-48fc-ac3e-4a22131fa92d"


def get_oidc_auth_url(discord_user_id: str):
    """Generate OIDC authorization URL for UCD authentication."""
    # Store Discord user ID in state for later retrieval
    state = f"{discord_user_id}:{secrets.token_urlsafe(32)}"

    params = {
        "client_id": config.OIDC_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": config.OIDC_REDIRECT_URI,
        "response_mode": "query",
        "scope": "openid profile email User.Read",
        "state": state,
        "prompt": "select_account",
        "domain_hint": "cam.ac.uk",
    }

    url = f"{AUTHORIZE_ENDPOINT}?{urlencode(params)}"
    return {"url": url, "state": state}


def get_oidc_tokens(code: str) -> dict:
    """Exchange authorization code for OIDC tokens."""
    data = {
        "client_id": config.OIDC_CLIENT_ID,
        "client_secret": config.OIDC_CLIENT_SECRET,
        "code": code,
        "redirect_uri": config.OIDC_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    response = requests.post(TOKEN_ENDPOINT, data=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"Error fetching OIDC tokens: [{response.status_code}] {response.text}"
        )


def get_user_info(access_token: str) -> dict:
    """Get minimal user info from Graph API - just UPN and groups."""
    headers = {"Authorization": f"Bearer {access_token}"}

    # Only request the UPN field we need
    url = f"{GRAPH_ENDPOINT}/me?$select=userPrincipalName"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        user_data = response.json()

        # Get user's group memberships - only need IDs
        try:
            groups_response = requests.get(
                f"{GRAPH_ENDPOINT}/me/memberOf?$select=id",
                headers=headers,
            )

            if groups_response.status_code == 200:
                user_data["groups"] = groups_response.json().get("value", [])
            else:
                user_data["groups"] = []
        except Exception as e:
            print(f"Error getting groups: {e}")
            user_data["groups"] = []

        return user_data
    else:
        raise Exception(
            f"Error fetching user info: [{response.status_code}] {response.text}"
        )


def verify_cambridge_user(user_info: dict) -> dict:
    """
    Check if user is a current student based on UCD group membership.
    Returns dict with verification status and student status only.
    """
    upn = user_info.get("userPrincipalName", "")
    groups = user_info.get("groups", [])
    group_ids = {group.get("id") for group in groups if group.get("id")}
    is_student = UOC_USERS_STUDENT in group_ids

    result = {
        "verified": True,
        "upn": upn,
        "is_student": is_student,
    }

    return result
