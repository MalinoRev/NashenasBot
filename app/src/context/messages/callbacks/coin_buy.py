def get_intro_message() -> str:
	return (
		"برای پرداخت، لینک زیر را کپی کرده و در مرورگر خود باز کنید.\n"
		"در پیام بعدی لینک به‌صورت قابل‌کپی ارسال می‌شود."
	)


def get_link_message(url: str) -> str:
	# Send inside backticks so it's easy to copy
	return f"`{url}`"


def get_error_message() -> str:
	return "❌ خطا در ایجاد لینک پرداخت. لطفاً بعداً دوباره تلاش کنید."


