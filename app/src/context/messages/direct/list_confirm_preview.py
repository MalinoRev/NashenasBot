def format_header() -> str:
	return (
		"📝 پیش‌نمایش ارسال دایرکت به لیست\n\n"
		"این پیام به فهرست نتایج انتخاب‌شده ارسال خواهد شد."
	)


def format_footer(cost_coins: int, balance_coins: int) -> str:
	return (
		"\n\n"
		f"💰 این عملیات {cost_coins} سکه از شما کسر خواهد کرد.\n"
		f"🔸 موجودی فعلی سکه شما: {balance_coins}"
	)


