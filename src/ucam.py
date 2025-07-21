import secrets
from requests_oauthlib import OAuth2Session
from src import config


TENANT_ID = "49a50445-bdfa-4b79-ade3-547b4f3986e9"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
AUTHORIZATION_ENDPOINT = f"{AUTHORITY}/oauth2/v2.0/authorize"
TOKEN_ENDPOINT = f"{AUTHORITY}/oauth2/v2.0/token"
GRAPH_ENDPOINT = "https://graph.microsoft.com/v1.0"

# https://help.uis.cam.ac.uk/service/accounts-passwords/it-staff/university-central-directory/understanding-users-and-groups
UOC_USERS_STUDENT = "0cbcd7fb-1f17-48fc-ac3e-4a22131fa92d"

SCOPE = ["openid", "profile", "email", "User.Read"]


def get_auth_url(discord_user_id: str):
    state = f"{discord_user_id}:{secrets.token_urlsafe(32)}"

    oauth = OAuth2Session(
        client_id=config.OIDC_CLIENT_ID,
        redirect_uri=config.OIDC_REDIRECT_URI,
        scope=SCOPE,
    )

    return oauth.authorization_url(
        AUTHORIZATION_ENDPOINT,
        state=state,
        prompt="select_account",
        domain_hint="cam.ac.uk",
    )


def get_token(code: str) -> dict:
    oauth = OAuth2Session(
        client_id=config.OIDC_CLIENT_ID, redirect_uri=config.OIDC_REDIRECT_URI
    )

    return oauth.fetch_token(
        TOKEN_ENDPOINT,
        code=code,
        client_secret=config.OIDC_CLIENT_SECRET,
        include_client_id=True,
    )


def get_user_info(access_token: str) -> dict:
    oauth = OAuth2Session(
        client_id=config.OIDC_CLIENT_ID,
        token={"access_token": access_token, "token_type": "Bearer"},
    )

    response = oauth.get(f"{GRAPH_ENDPOINT}/me?$select=userPrincipalName")
    response.raise_for_status()
    user_data = response.json()

    groups_response = oauth.get(f"{GRAPH_ENDPOINT}/me/memberOf?$select=id")
    groups_response.raise_for_status()
    groups_data = groups_response.json()
    user_data["groups"] = groups_data.get("value", [])

    return user_data


def is_student(user_info: dict) -> bool:
    upn = user_info.get("userPrincipalName", "")
    groups = user_info.get("groups", [])
    group_ids = {group.get("id") for group in groups if group.get("id")}
    return UOC_USERS_STUDENT in group_ids
