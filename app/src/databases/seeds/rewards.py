from sqlalchemy import select

from src.core.database import get_session
from src.databases.rewards import Reward


async def seed_rewards_defaults() -> None:
	async with get_session() as session:
		existing = await session.scalar(select(Reward))
		if existing is None:
			row = Reward()
			session.add(row)
			await session.commit()



