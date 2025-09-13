def get_message(steps_remaining: int, reward_amount: int) -> str:
	steps = int(steps_remaining or 0)
	coins = int(reward_amount or 0)
	return (
		f"🔔 فقط {steps} قدم تا تکمیل پروفایل !\n\n"
		"اطلاعات تکمیل نشده ی شما :  نام، عکس و موقعیت جی پی اس\n\n"
		f"پروفایل خود را تکمیل کنید👇 و {coins} سکه دریافت کنید ."
	)


