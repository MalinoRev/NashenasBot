from typing import Dict, Optional, Tuple
from src.services.direct_draft_cache import MessageData


# sender_db_id -> (from_chat_id, message_id, kind, page, message_data)
_list_drafts: Dict[int, Tuple[int, int, str, int, MessageData]] = {}


def set_list_draft(sender_db_id: int, from_chat_id: int, message_id: int, kind: str, page: int, message_data: MessageData) -> None:
    _list_drafts[sender_db_id] = (from_chat_id, message_id, kind, page, message_data)


def get_list_draft(sender_db_id: int) -> Optional[Tuple[int, int, str, int, MessageData]]:
    return _list_drafts.get(sender_db_id)


def clear_list_draft(sender_db_id: int) -> None:
    _list_drafts.pop(sender_db_id, None)


