import asyncio
import sys
from typing import Literal

from . import Base, engine

# Import models so they register on Base.metadata
import src.databases.states  # noqa: F401
import src.databases.users  # noqa: F401
import src.databases.cities  # noqa: F401
import src.databases.user_profiles  # noqa: F401
import src.databases.user_locations  # noqa: F401
import src.databases.user_settings  # noqa: F401
import src.databases.user_filters  # noqa: F401
import src.databases.user_bans  # noqa: F401
import src.databases.requested_channels  # noqa: F401


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
    from src.databases.seeds.cities import (
        seed_cities_state_1,
        seed_cities_state_2,
        seed_cities_state_3,
        seed_cities_state_4,
        seed_cities_state_5,
        seed_cities_state_6,
        seed_cities_state_7,
        seed_cities_state_8,
        seed_cities_state_9,
        seed_cities_state_10,
        seed_cities_state_11,
        seed_cities_state_12,
        seed_cities_state_13,
        seed_cities_state_14,
        seed_cities_state_15,
        seed_cities_state_16,
        seed_cities_state_17,
        seed_cities_state_18,
        seed_cities_state_19,
        seed_cities_state_20,
        seed_cities_state_21,
        seed_cities_state_22,
        seed_cities_state_23,
        seed_cities_state_24,
        seed_cities_state_25,
        seed_cities_state_26,
        seed_cities_state_27,
        seed_cities_state_28,
        seed_cities_state_29,
        seed_cities_state_30,
        seed_cities_state_31,
    )

    await seed_states()
    await seed_cities_state_1()
    await seed_cities_state_2()
    await seed_cities_state_3()
    await seed_cities_state_4()
    await seed_cities_state_5()
    await seed_cities_state_6()
    await seed_cities_state_7()
    await seed_cities_state_8()
    await seed_cities_state_9()
    await seed_cities_state_10()
    await seed_cities_state_11()
    await seed_cities_state_12()
    await seed_cities_state_13()
    await seed_cities_state_14()
    await seed_cities_state_15()
    await seed_cities_state_16()
    await seed_cities_state_17()
    await seed_cities_state_18()
    await seed_cities_state_19()
    await seed_cities_state_20()
    await seed_cities_state_21()
    await seed_cities_state_22()
    await seed_cities_state_23()
    await seed_cities_state_24()
    await seed_cities_state_25()
    await seed_cities_state_26()
    await seed_cities_state_27()
    await seed_cities_state_28()
    await seed_cities_state_29()
    await seed_cities_state_30()
    await seed_cities_state_31()


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


