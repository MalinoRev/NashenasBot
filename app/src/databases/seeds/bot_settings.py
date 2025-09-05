import os
from sqlalchemy import select

from src.core.database import get_session
from src.databases.bot_settings import BotSetting


async def seed_bot_settings_defaults() -> None:
	async with get_session() as session:
		existing = await session.scalar(select(BotSetting))
		if existing:
			return
		row = BotSetting(
			bot_name=os.getenv("BOT_BRAND_NAME", "NashenasBot"),
			bot_support_username=os.getenv("BOT_SUPPORT_USERNAME") or None,
			bot_channel=os.getenv("BOT_CHANNEL_SLUG") or None,
			cache_channel_id=int(os.getenv("CACHE_CHANNEL_ID") or 0) or None,
			maintenance_mode=False,
		)
		session.add(row)
		await session.commit()


