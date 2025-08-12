from datetime import datetime
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


async def push_metadata(tokens: dict, metadata: dict):
    updated_tokens = get_access_token(tokens)

    oauth = OAuth2Session(config.DISCORD_CLIENT_ID, token=updated_tokens)

    body = {"platform_name": "Cambridge Verification", "metadata": metadata}

    response = oauth.put(
        f"{config.DISCORD_API_ENDPOINT}/users/@me/applications/{config.DISCORD_CLIENT_ID}/role-connection",
        json=body,
    )

    response.raise_for_status()
