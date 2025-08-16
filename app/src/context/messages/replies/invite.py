def get_message(user_referral_count: int) -> str:
	count_str = str(user_referral_count or 0)
	return (
		"لینک⚡️ دعوت شما با موفقیت ساخته شد 👆\n\n"
		"شما میتوانید بنر حاوی لینک⚡️ خود را به گـــروه ها و دوستان خود ارسال کنید\n\n"
		"- با معرفی هر نفر 50 سکه بگیرید!برای اطلاعات بیشتر راهنمای سکه (/help_credit) را بخوانید.\n\n"
		f"👈 شما تاکنون {count_str} نفر را به این ربات دعوت کرده اید ."
	)
