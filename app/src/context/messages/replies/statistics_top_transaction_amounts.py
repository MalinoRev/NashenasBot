def get_message(transactions: list) -> str:
	if not transactions:
		return "💰 **بیشترین مبلغ تراکنش‌ها**\n\nهیچ تراکنش موفقی یافت نشد."
	
	header = "💰 **بیشترین مبلغ تراکنش‌ها**\n\n📊 **کاربران با بیشترین مجموع پرداختی‌ها:**\n\n"
	
	rows = []
	for i, (user, total_amount) in enumerate(transactions, 1):
		rows.append(f"{i}. `{user.user_id}` - {total_amount:,} تومان")
	
	return header + "\n".join(rows)
