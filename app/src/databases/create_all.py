import asyncio
import logging

from .base import Base
from .engine import engine

# Import models so that they are registered on Base.metadata
from . import states as _states  # noqa: F401
from . import users as _users  # noqa: F401
from . import chats as _chats  # noqa: F401
from . import directs as _directs  # noqa: F401
from . import chat_requests as _chat_requests  # noqa: F401


logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


async def run() -> None:
	logging.info("Creating all tables if not exist...")
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)
	logging.info("Done.")


if __name__ == "__main__":
	asyncio.run(run())


