def get_message(name: str | None = None) -> str:
	person = name or "دوست"
	return (
		f"سلام {person}!\n"
		"به ربات مونوگپ خوش اومدی."
	)



