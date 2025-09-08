def get_read_receipt_message(receiver_name: str) -> str:
	"""
	Get read receipt message for direct messages
	
	Args:
		receiver_name: Name or unique_id of the receiver
		
	Returns:
		Formatted read receipt message
	"""
	return f"✅ {receiver_name} پیام شما را دید"
