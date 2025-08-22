def get_message(name: str, gender_text: str, age: str, unique_id: str) -> str:
	return (
		"✉️ ارسال پیام دایرکت\n"
		"این کار 1 سکه هزینه دارد.\n"
		f"گیرنده: {name} | {gender_text} | سن: {age}\n"
		f"آیدی: /user_{unique_id}"
	)


