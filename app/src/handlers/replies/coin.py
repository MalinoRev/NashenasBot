from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.databases.prices import Price
from src.databases.products import Product
from src.databases.rewards import Reward
from src.context.messages.replies.coin import get_message as get_coin_message
from src.context.keyboards.inline.coin_prices import build_keyboard as build_coin_prices_kb


async def handle_coin(user_id_tg: int) -> dict:
	"""Return text and inline keyboard for the coin page."""
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id_tg))
		if not user:
			return {"text": ""}
		# Fetch invite reward (single row table)
		reward: Reward | None = await session.scalar(select(Reward).limit(1))
		invite_reward = int(getattr(reward, "invite_amount", 0)) if reward else 0
		# Fetch prices
		prices_rows = (await session.execute(select(Price).order_by(Price.amount))).scalars().all()
		prices: list[tuple[int, int, int]] = [(p.id, p.amount, p.price) for p in prices_rows]
		# Fetch vip price from products
		product: Product | None = await session.scalar(select(Product))
		vip_price = int(getattr(product, "vip_rank_price", 0)) if product else 0

	text = get_coin_message(int(user.credit or 0), invite_reward)
	kb = build_coin_prices_kb(prices, vip_price=vip_price)
	return {"text": text, "reply_markup": kb}


