from datetime import datetime


def get_not_found_message() -> str:
	return "❌ کاربر یافت نشد."


def format_caption(
	*,
	name: str,
	gender_text: str,
	state_name: str,
	city_name: str,
	age: str,
	unique_id: str,
	distance_text: str,
	last_activity: str | None,
) -> str:
	last_activity_text = (f"آخرین فعالیت: {last_activity}" if last_activity else "")
	lines: list[str] = [
		f"• نام: {name}",
		f"• جنسیت: {gender_text}",
		f"• استان: {state_name}",
		f"• شهر: {city_name}",
		f"• سن: {age}",
	]
	if last_activity_text:
		lines.append("")
		lines.append(last_activity_text)
	lines.extend(
		[
			"",
			f"🆔 آیدی : /user_{unique_id}",
			"",
			f"🏁 فاصله از شما:  {distance_text}",
		]
	)
	return "\n".join(lines)


