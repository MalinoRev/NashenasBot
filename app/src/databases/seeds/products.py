import os
from sqlalchemy import select

from src.core.database import get_session
from src.databases.products import Product


async def seed_products_defaults() -> None:
	"""Ensure a single products row exists, seeded from env if present."""
	async with get_session() as session:
		existing = await session.scalar(select(Product))
		if existing is None:
			row = Product(
				unban_price=int(os.getenv("UNBAN_PRICE", "0") or 0),
				delete_account_price=int(os.getenv("ACCOUNT_DELETE_PRICE", "0") or 0),
				vip_rank_price=int(os.getenv("VIP_RANK_PRICE", "0") or 0),
				vip_rank_time=int((os.getenv("VIP_RANK_TIME", "30d") or "30d").rstrip("d").strip() or 30),
			)
			session.add(row)
			await session.commit()




