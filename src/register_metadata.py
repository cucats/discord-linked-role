"""
Register Discord linked role metadata schema.
This should be run once to register the metadata fields with Discord.
"""

import config
import requests


def register_metadata():
    """Register metadata schema with Discord."""

    url = f"{config.DISCORD_API_ENDPOINT}/applications/{config.DISCORD_CLIENT_ID}/role-connections/metadata"

    metadata_schema = [
        {
            "key": "is_student",
            "name": "Current Student",
            "description": "Current student",
            "type": 7,  # boolean_eq
        },
    ]

    headers = {
        "Authorization": f"Bot {config.DISCORD_TOKEN}",
        "Content-Type": "application/json",
    }

    response = requests.put(url, json=metadata_schema, headers=headers)

    if response.status_code == 200:
        print(f"Success: {response.json()}")
    else:
        print(f"Error: {response.status_code} {response.text}")


if __name__ == "__main__":
    register_metadata()
