import requests
import config


def register_metadata():
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
        "Authorization": f"Bot {config.DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json",
    }

    response = requests.put(url, json=metadata_schema, headers=headers)
    response.raise_for_status()


if __name__ == "__main__":
    register_metadata()
