import asyncio
import sys
from typing import Literal

from . import Base, engine

# Import models so they register on Base.metadata
import src.databases.states  # noqa: F401
import src.databases.users  # noqa: F401


Action = Literal["create", "drop", "recreate"]


async def create_all() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def seed_all() -> None:
    # Import and run seeds here
    from src.databases.seeds import seed_states

    await seed_states()


def main() -> None:
    action: Action = (sys.argv[1] if len(sys.argv) > 1 else "create")  # type: ignore[assignment]
    if action not in ("create", "drop", "recreate", "seed"):
        print("Usage: python -m src.core.database.manage [create|drop|recreate|seed]")
        raise SystemExit(2)

    if action == "create":
        asyncio.run(create_all())
    elif action == "drop":
        asyncio.run(drop_all())
    elif action == "recreate":
        asyncio.run(drop_all())
        asyncio.run(create_all())
    else:  # seed
        asyncio.run(seed_all())


if __name__ == "__main__":
    main()


