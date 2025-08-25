from typing import Dict, Optional, Tuple


# sender_db_id -> (from_chat_id, message_id, target_internal_id)
_drafts: Dict[int, Tuple[int, int, int]] = {}


def set_draft(sender_db_id: int, from_chat_id: int, message_id: int, target_internal_id: int) -> None:
	_drafts[sender_db_id] = (from_chat_id, message_id, target_internal_id)


def get_draft(sender_db_id: int) -> Optional[Tuple[int, int, int]]:
	return _drafts.get(sender_db_id)


def clear_draft(sender_db_id: int) -> None:
	_drafts.pop(sender_db_id, None)




