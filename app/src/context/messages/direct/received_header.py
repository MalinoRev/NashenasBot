def format_message(sender_unique_id: str) -> str:
	return (
		"📩 شما یک پیام دایرکت جدید دریافت کردید!\n"
		"👤 برای مشاهده پروفایل فرستنده دستور زیر را بفرستید:\n"
		f"/user_{sender_unique_id}\n"
		"——————————————\n"
		"متن پیام در ادامه می‌آید:" 
	)


