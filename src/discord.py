from datetime import datetime

import requests
from requests_oauthlib import OAuth2Session

from .config import (
    DISCORD_API_ENDPOINT,
    DISCORD_CLIENT_ID,
    DISCORD_CLIENT_SECRET,
    DISCORD_REDIRECT_URI,
    DISCORD_BOT_TOKEN,
)


DISCORD_TOKEN_URL = f"{DISCORD_API_ENDPOINT}/oauth2/token"


def get_authorization_url():
    oauth = OAuth2Session(
        client_id=DISCORD_CLIENT_ID,
        redirect_uri=DISCORD_REDIRECT_URI,
        scope=["identify", "role_connections.write"],
    )

    return oauth.authorization_url(
        "https://discord.com/api/oauth2/authorize", prompt="consent"
    )


def get_tokens(code: str) -> dict:
    oauth = OAuth2Session(
        client_id=DISCORD_CLIENT_ID,
        redirect_uri=DISCORD_REDIRECT_URI,
    )

    token = oauth.fetch_token(
        DISCORD_TOKEN_URL,
        code=code,
        client_secret=DISCORD_CLIENT_SECRET,
        include_client_id=True,
    )

    if "expires_in" in token:
        token["expires_at"] = datetime.now().timestamp() + token["expires_in"]

    return token


def get_access_token(tokens: dict) -> dict:
    if datetime.now().timestamp() < tokens.get("expires_at", 0):
        return tokens

    oauth = OAuth2Session(DISCORD_CLIENT_ID, token=tokens)

    new_tokens = oauth.refresh_token(
        DISCORD_TOKEN_URL,
        refresh_token=tokens["refresh_token"],
        client_id=DISCORD_CLIENT_ID,
        client_secret=DISCORD_CLIENT_SECRET,
    )

    if "expires_in" in new_tokens:
        new_tokens["expires_at"] = datetime.now().timestamp() + new_tokens["expires_in"]

    return new_tokens


def push_metadata(tokens: dict, metadata: dict):
    updated_tokens = get_access_token(tokens)

    oauth = OAuth2Session(DISCORD_CLIENT_ID, token=updated_tokens)

    body = {"platform_name": "Cambridge Verification", "metadata": metadata}

    response = oauth.put(
        f"{DISCORD_API_ENDPOINT}/users/@me/applications/{DISCORD_CLIENT_ID}/role-connection",
        json=body,
    )

    response.raise_for_status()


# https://discord.com/developers/docs/resources/application-role-connection-metadata


class ApplicationRoleConnectionMetadataType:
    INTEGER_LESS_THAN_OR_EQUAL = 1
    INTEGER_GREATER_THAN_OR_EQUAL = 2
    INTEGER_EQUAL = 3
    INTEGER_NOT_EQUAL = 4
    DATETIME_LESS_THAN_OR_EQUAL = 5
    DATETIME_GREATER_THAN_OR_EQUAL = 6
    BOOLEAN_EQUAL = 7
    BOOLEAN_NOT_EQUAL = 8


def register_metadata():
    url = f"{DISCORD_API_ENDPOINT}/applications/{DISCORD_CLIENT_ID}/role-connections/metadata"

    metadata_schema = [
        {
            "key": "is_student",
            "name": "Current Student",
            "description": "Current student",
            "type": ApplicationRoleConnectionMetadataType.BOOLEAN_EQUAL,
        },
    ]

    headers = {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json",
    }

    response = requests.put(url, json=metadata_schema, headers=headers)
    response.raise_for_status()


if __name__ == "__main__":
    register_metadata()
