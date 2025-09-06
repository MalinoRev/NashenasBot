def get_message(transactions: list) -> str:
	if not transactions:
		return "📊 **بیشترین تراکنش‌های موفق**\n\nهیچ تراکنش موفقی یافت نشد."
	
	header = "💳 **بیشترین تراکنش‌های موفق**\n\n📊 **کاربران با بیشترین تراکنش‌های پرداخت شده:**\n\n"
	
	rows = []
	for i, (user, count) in enumerate(transactions, 1):
		rows.append(f"{i}. `{user.user_id}` - {count:,} تراکنش موفق")
	
	return header + "\n".join(rows)
