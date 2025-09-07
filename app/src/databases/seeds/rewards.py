from sqlalchemy import select

from src.core.database import get_session
from src.databases.rewards import Reward


async def seed_rewards_defaults() -> None:
	async with get_session() as session:
		existing = await session.scalar(select(Reward))
		if existing is None:
			row = Reward(
				invite_amount=10,
				profile_amount=5,
				report_amount=3
			)
			session.add(row)
			await session.commit()



