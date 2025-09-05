import asyncio
import logging

from .base import Base
from .engine import engine

# Import models so that they are registered on Base.metadata
from . import admins as _admins  # noqa: F401
from . import chat_history as _chat_history  # noqa: F401
from . import chat_queue as _chat_queue  # noqa: F401
from . import chat_requests as _chat_requests  # noqa: F401
from . import chats as _chats  # noqa: F401
from . import cities as _cities  # noqa: F401
from . import contacts as _contacts  # noqa: F401
from . import directs as _directs  # noqa: F401
from . import likes as _likes  # noqa: F401
from . import media as _media  # noqa: F401
from . import payments as _payments  # noqa: F401
from . import products as _products  # noqa: F401
from . import prices as _prices  # noqa: F401
from . import requested_channels as _requested_channels  # noqa: F401
from . import rewards as _rewards  # noqa: F401
from . import states as _states  # noqa: F401
from . import user_bans as _user_bans  # noqa: F401
from . import user_blocked as _user_blocked  # noqa: F401
from . import user_filters as _user_filters  # noqa: F401
from . import user_locations as _user_locations  # noqa: F401
from . import user_profiles as _user_profiles  # noqa: F401
from . import user_rewards as _user_rewards  # noqa: F401
from . import user_settings as _user_settings  # noqa: F401
from . import user_vips as _user_vips  # noqa: F401
from . import users as _users  # noqa: F401


logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


async def run() -> None:
	logging.info("Creating all tables if not exist...")
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)
	logging.info("Done.")


if __name__ == "__main__":
	asyncio.run(run())


