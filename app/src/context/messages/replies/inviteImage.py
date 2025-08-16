def get_caption(bot_username: str, referral_id: str) -> str:
	link = f"http://t.me/{bot_username}?start=inv_{referral_id}"
	return (
		"《مِلو گپ 🤖》 هستم،بامن میتونی\n\n"
		"📡افراد نزدیک یا 👫هم سن خودت رو پیدا کنی و بصورت ناشناس چت کنی...\n\n"
		" ➕ میتونی از هر شهری که دلت بخواد دوست مجازی پیدا کنی و کلی امکانت دیگه...😎\n\n"
		"همین الان رو لینک بزن 👇\n"
		f"{link}\n\n"
		"✅ #رایگان و کاملا #واقعی 😎"
	)
