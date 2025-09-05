from sqlalchemy import select

from src.core.database import get_session
from src.databases.bot_settings import BotSetting


async def get_bot_settings() -> BotSetting | None:
	async with get_session() as session:
		return await session.scalar(select(BotSetting))


async def get_bot_name() -> str:
	settings = await get_bot_settings()
	return settings.bot_name if settings and getattr(settings, "bot_name", None) else "NashenasBot"


async def get_support_username() -> str | None:
	settings = await get_bot_settings()
	return getattr(settings, "bot_support_username", None) if settings else None


async def get_channel_slug() -> str | None:
	settings = await get_bot_settings()
	return getattr(settings, "bot_channel", None) if settings else None


async def get_cache_channel_id() -> int | None:
	settings = await get_bot_settings()
	value = getattr(settings, "cache_channel_id", None) if settings else None
	return int(value) if value is not None else None


async def is_maintenance_mode() -> bool:
	settings = await get_bot_settings()
	return bool(getattr(settings, "maintenance_mode", False)) if settings else False


