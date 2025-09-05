from sqlalchemy import select

from src.core.database import get_session
from src.databases.products import Product


async def get_product_singleton() -> Product:
	"""Return the single Product row, creating default one if missing."""
	async with get_session() as session:
		row: Product | None = await session.scalar(select(Product))
		if row is None:
			row = Product()
			session.add(row)
			await session.commit()
			# refresh to ensure autoincrement id
			await session.refresh(row)
		return row



