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

DISCORD_TOKEN = getenv("DISCORD_TOKEN")
DISCORD_CLIENT_ID = getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = getenv("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = f"{HOST}/discord-oauth-callback"

OIDC_CLIENT_ID = getenv("OIDC_CLIENT_ID")
OIDC_CLIENT_SECRET = getenv("OIDC_CLIENT_SECRET")
OIDC_REDIRECT_URI = f"{HOST}/ucd-oidc-callback"

FLASK_SECRET = getenv("FLASK_SECRET")

MYSQL_HOST = getenv("MYSQL_HOST")
MYSQL_PORT = int(getenv("MYSQL_PORT"))
MYSQL_USER = getenv("MYSQL_USER")
MYSQL_PASSWORD = getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = getenv("MYSQL_DATABASE")
