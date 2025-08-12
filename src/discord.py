from datetime import datetime
import requests
from requests_oauthlib import OAuth2Session
from src import config


DISCORD_TOKEN_URL = f"{config.DISCORD_API_ENDPOINT}/oauth2/token"


def get_oauth_url():
    oauth = OAuth2Session(
        client_id=config.DISCORD_CLIENT_ID,
        redirect_uri=config.DISCORD_REDIRECT_URI,
        scope=["identify", "role_connections.write"],
    )

    return oauth.authorization_url(
        "https://discord.com/api/oauth2/authorize", prompt="consent"
    )


def get_token(code: str) -> dict:
    oauth = OAuth2Session(
        client_id=config.DISCORD_CLIENT_ID, redirect_uri=config.DISCORD_REDIRECT_URI
    )

    token = oauth.fetch_token(
        DISCORD_TOKEN_URL,
        code=code,
        client_secret=config.DISCORD_CLIENT_SECRET,
        include_client_id=True,
    )

    if "expires_in" in token:
        token["expires_at"] = datetime.now().timestamp() + token["expires_in"]

    return token


def get_access_token(tokens: dict) -> dict:
    if datetime.now().timestamp() > tokens.get("expires_at", 0):
        oauth = OAuth2Session(config.DISCORD_CLIENT_ID, token=tokens)

        new_tokens = oauth.refresh_token(
            DISCORD_TOKEN_URL,
            refresh_token=tokens["refresh_token"],
            client_id=config.DISCORD_CLIENT_ID,
            client_secret=config.DISCORD_CLIENT_SECRET,
        )

        if "expires_in" in new_tokens:
            new_tokens["expires_at"] = (
                datetime.now().timestamp() + new_tokens["expires_in"]
            )

        return new_tokens

    return tokens


def push_metadata(tokens: dict, metadata: dict):
    updated_tokens = get_access_token(tokens)

    oauth = OAuth2Session(config.DISCORD_CLIENT_ID, token=updated_tokens)

    body = {"platform_name": "Cambridge Verification", "metadata": metadata}

    response = oauth.put(
        f"{config.DISCORD_API_ENDPOINT}/users/@me/applications/{config.DISCORD_CLIENT_ID}/role-connection",
        json=body,
    )

    response.raise_for_status()


class ApplicationRoleConnectionMetadataType:
    INTEGER_LESS_THAN_OR_EQUAL = 1  # 	the metadata value (integer) is less than or equal to the guild's configured value (integer)
    INTEGER_GREATER_THAN_OR_EQUAL = 2  # 	the metadata value (integer) is greater than or equal to the guild's configured value (integer)
    INTEGER_EQUAL = 3  # the metadata value (integer) is equal to the guild's configured value (integer)
    INTEGER_NOT_EQUAL = 4  # the metadata value (integer) is not equal to the guild's configured value (integer)
    DATETIME_LESS_THAN_OR_EQUAL = 5  # the metadata value (ISO8601 string) is less than or equal to the guild's configured value (integer; days before current date)
    DATETIME_GREATER_THAN_OR_EQUAL = 6  # the metadata value (ISO8601 string) is greater than or equal to the guild's configured value (integer; days before current date)
    BOOLEAN_EQUAL = 7  # the metadata value (integer) is equal to the guild's configured value (integer; 1)
    BOOLEAN_NOT_EQUAL = 8


def register_metadata():
    url = f"{config.DISCORD_API_ENDPOINT}/applications/{config.DISCORD_CLIENT_ID}/role-connections/metadata"

    metadata_schema = [
        {
            "key": "is_student",
            "name": "Current Student",
            "description": "Current student",
            "type": ApplicationRoleConnectionMetadataType.BOOLEAN_EQUAL,
        },
    ]

    headers = {
        "Authorization": f"Bot {config.DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json",
    }

    response = requests.put(url, json=metadata_schema, headers=headers)
    response.raise_for_status()


if __name__ == "__main__":
    register_metadata()
