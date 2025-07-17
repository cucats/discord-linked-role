"""
MySQL database storage for Discord tokens and user verification.
"""

import mysql.connector
from mysql.connector import Error
import json
from typing import Optional, Dict, Any
from src import config


def get_connection():
    """Create and return a MySQL database connection."""
    return mysql.connector.connect(
        host=config.MYSQL_HOST,
        port=config.MYSQL_PORT,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DATABASE,
    )


def init_database():
    """Initialize database tables if they don't exist."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Create table for Discord tokens and user verification
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_data (
                discord_user_id VARCHAR(255) PRIMARY KEY,
                discord_tokens JSON,
                upn VARCHAR(255),
                is_student BOOLEAN,
                verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_upn (upn)
            )
        """
        )

        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully")

    except Error as e:
        print(f"Error initializing database: {e}")
        raise


async def store_discord_tokens(user_id: str, tokens: dict) -> None:
    """Store Discord OAuth tokens for a user."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        tokens_json = json.dumps(tokens)

        cursor.execute(
            """
            INSERT INTO user_data (discord_user_id, discord_tokens) 
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE 
            discord_tokens = VALUES(discord_tokens),
            updated_at = CURRENT_TIMESTAMP
        """,
            (user_id, tokens_json),
        )

        conn.commit()
        cursor.close()
        conn.close()

    except Error as e:
        print(f"Error storing Discord tokens: {e}")
        raise


async def get_discord_tokens(user_id: str) -> Optional[Dict[str, Any]]:
    """Get Discord OAuth tokens for a user."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT discord_tokens FROM user_data 
            WHERE discord_user_id = %s
        """,
            (user_id,),
        )

        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result and result[0]:
            return json.loads(result[0])
        return None

    except Error as e:
        print(f"Error getting Discord tokens: {e}")
        return None


async def store_verification(user_id: str, upn: str, is_student: bool) -> None:
    """Store user verification data including UPN."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO user_data (discord_user_id, upn, is_student) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            upn = VALUES(upn),
            is_student = VALUES(is_student),
            verified_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        """,
            (user_id, upn, is_student),
        )

        conn.commit()
        cursor.close()
        conn.close()

    except Error as e:
        print(f"Error storing verification: {e}")
        raise


async def get_verification(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user verification data."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT upn, is_student, verified_at 
            FROM user_data 
            WHERE discord_user_id = %s AND upn IS NOT NULL
        """,
            (user_id,),
        )

        result = cursor.fetchone()
        cursor.close()
        conn.close()

        return result

    except Error as e:
        print(f"Error getting verification: {e}")
        return None

if __name__ == "__main__":
    init_database()
