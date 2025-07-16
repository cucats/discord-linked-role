import requests
import secrets
from datetime import datetime, timedelta
from urllib.parse import urlencode
import config
import database


def get_oauth_url():
    """Generate Discord OAuth URL with state parameter."""
    state = secrets.token_urlsafe(32)

    params = {
        "client_id": config.DISCORD_CLIENT_ID,
        "redirect_uri": config.DISCORD_REDIRECT_URI,
        "response_type": "code",
        "scope": "identify role_connections.write",
        "state": state,
        "prompt": "consent",
    }

    url = f"https://discord.com/api/oauth2/authorize?{urlencode(params)}"
    return {"url": url, "state": state}


def get_oauth_tokens(code: str) -> dict:
    # Exchange authorization code for tokens.
    data = {
        "client_id": config.DISCORD_CLIENT_ID,
        "client_secret": config.DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": config.DISCORD_REDIRECT_URI,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(
        f"{config.DISCORD_API_ENDPOINT}/oauth2/token", data=data, headers=headers
    )

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"Error fetching OAuth tokens: [{response.status_code}] {response.text}"
        )


async def get_access_token(user_id: str, tokens: dict) -> str:
    """Get valid access token, refreshing if necessary."""
    if datetime.now().timestamp() > tokens.get("expires_at", 0):
        # Refresh the token
        data = {
            "client_id": config.DISCORD_CLIENT_ID,
            "client_secret": config.DISCORD_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": tokens["refresh_token"],
        }

        response = requests.post(
            f"{config.DISCORD_API_ENDPOINT}/oauth2/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if response.status_code == 200:
            new_tokens = response.json()
            new_tokens["expires_at"] = (
                datetime.now().timestamp() + new_tokens["expires_in"]
            )
            await database.store_discord_tokens(user_id, new_tokens)
            return new_tokens["access_token"]
        else:
            raise Exception(
                f"Error refreshing access token: [{response.status_code}] {response.text}"
            )

    return tokens["access_token"]


def get_user_data(tokens: dict) -> dict:
    """Get Discord user data."""
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    response = requests.get(
        f"{config.DISCORD_API_ENDPOINT}/oauth2/@me", headers=headers
    )

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"Error fetching user data: [{response.status_code}] {response.text}"
        )


async def push_metadata(user_id: str, tokens: dict, metadata: dict):
    """Push metadata to Discord for linked roles."""
    access_token = await get_access_token(user_id, tokens)

    body = {"platform_name": "Cambridge Verification", "metadata": metadata}

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = requests.put(
        f"{config.DISCORD_API_ENDPOINT}/users/@me/applications/{config.DISCORD_CLIENT_ID}/role-connection",
        json=body,
        headers=headers,
    )

    if response.status_code != 200:
        raise Exception(
            f"Error pushing Discord metadata: [{response.status_code}] {response.text}"
        )
