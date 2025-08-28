def format_message(sender_unique_id: str) -> str:
	print(f"LOG: format_message called with sender_unique_id='{sender_unique_id}'")
	result = (
		f"🔔 درخواست چت از طرف /user_{sender_unique_id}\n\n"
		"💡با فعال کردن حالت سایلنت ، کسی امکان درخواست چت به شما را نخواهد داشت 👈 /silent"
	)
	print(f"LOG: format_message result length = {len(result)}")
	return result


