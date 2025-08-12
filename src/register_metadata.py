import requests
import config
from enum import Enum


class ApplicationRoleConnectionMetadataType(Enum):
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
