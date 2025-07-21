import os
from dotenv import load_dotenv

load_dotenv()


def getenv(key: str) -> str:
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"Required: {key}")
    return value


DISCORD_API_ENDPOINT = "https://discord.com/api/v10"

HOST = getenv("HOST")

DISCORD_BOT_TOKEN = getenv("DISCORD_BOT_TOKEN")
DISCORD_CLIENT_ID = getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = getenv("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = f"{HOST}/discord/callback"

OIDC_CLIENT_ID = getenv("UCAM_CLIENT_ID")
OIDC_CLIENT_SECRET = getenv("UCAM_CLIENT_SECRET")
OIDC_REDIRECT_URI = f"{HOST}/ucam/callback"

FLASK_SECRET = getenv("FLASK_SECRET")
