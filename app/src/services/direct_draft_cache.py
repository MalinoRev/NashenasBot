from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class MessageData:
	text: Optional[str] = None
	photo: Optional[Any] = None
	video: Optional[Any] = None
	animation: Optional[Any] = None
	audio: Optional[Any] = None
	document: Optional[Any] = None
	sticker: Optional[Any] = None
	caption: Optional[str] = None


# sender_db_id -> (from_chat_id, message_id, target_internal_id, message_data)
_drafts: Dict[int, Tuple[int, int, int, MessageData]] = {}


def set_draft(sender_db_id: int, from_chat_id: int, message_id: int, target_internal_id: int, message_data: MessageData) -> None:
	_drafts[sender_db_id] = (from_chat_id, message_id, target_internal_id, message_data)


def get_draft(sender_db_id: int) -> Optional[Tuple[int, int, int, MessageData]]:
	return _drafts.get(sender_db_id)


def clear_draft(sender_db_id: int) -> None:
	_drafts.pop(sender_db_id, None)




