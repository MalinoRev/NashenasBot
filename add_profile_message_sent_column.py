#!/usr/bin/env python3
"""
Migration script to add profile_message_sent column to user_rewards table.
Run this script to add the missing column.
"""

import asyncio
import os
from sqlalchemy import text
from app.src.core.database import get_session


async def add_column():
    """Add profile_message_sent column to user_rewards table"""
    try:
        async with get_session() as session:
            # Check if column exists
            result = await session.execute(text("""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'user_rewards'
                AND COLUMN_NAME = 'profile_message_sent'
                AND TABLE_SCHEMA = DATABASE()
            """))

            column_exists = result.fetchone() is not None

            if not column_exists:
                print("Adding profile_message_sent column to user_rewards table...")

                # Add the column
                await session.execute(text("""
                    ALTER TABLE user_rewards
                    ADD COLUMN profile_message_sent BOOLEAN NOT NULL DEFAULT 0
                """))

                await session.commit()
                print("✅ Column added successfully!")
            else:
                print("✅ Column already exists!")

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    return True


if __name__ == "__main__":
    print("Starting migration...")
    success = asyncio.run(add_column())
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
