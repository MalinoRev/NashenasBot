import asyncio
from sqlalchemy import select
from src.core.database import get_session
from src.databases.products import Product


async def get_message() -> str:
	async with get_session() as session:
		product: Product | None = await session.scalar(select(Product))
		price = int(getattr(product, "delete_account_price", 0)) if product else 0
	async def _fetch():
		from src.services.bot_settings_service import get_bot_name
		return await get_bot_name()
	try:
		brand = asyncio.get_event_loop().run_until_complete(_fetch())  # type: ignore[arg-type]
	except Exception:
		brand = "ربات"
	return (
		f"👈اگر میخواهید از ربات {brand} بصورت کامل خارج شوید و کل اطلاعات ذخیره شده شما حذف شود\n\n"
		f"با پرداخت هزینه {price} تومان کل اطلاعات شما از ربات حذف میشود شما و دیگر اکانتی داخل ربات نخواهید داشت\n"
		"بعد پرداخت بظور خودکار اکانت شما حذف میشود 👇"
	)


async def get_prepare_message() -> str:
	async with get_session() as session:
		product: Product | None = await session.scalar(select(Product))
		price = int(getattr(product, "delete_account_price", 0)) if product else 0
	return (
		"⚠️ توجه داشته باشید بعد از پرداخت مرورگرتان را تا دریافت نتیجه نبندید! ⛔️⛔️⛔️\n\n"
		"💡 برای ورود به درگاه پرداخت روی لینک زیر ضربه بزنید تا کپی شود سپس وارد مرورگر گوشیتان شده و در بخش آدرس لینک کپی شده را وارد کنید.\n\n"
		f"لینک پرداخت حذف اکانت به مبلغ {price} تومان برای شما در حال ساخته شدن میباشد 👇"
	)


