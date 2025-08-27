import re
from typing import Any, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import Message

from sqlalchemy import select
from src.core.database import get_session
from src.databases.users import User
from src.context.messages.link_filter.blocked_link import get_message as get_blocked_link_message


class LinkFilterMiddleware(BaseMiddleware):
    """Middleware to block links in direct messages and chats"""

    def __init__(self):
        super().__init__()
        # Comprehensive regex pattern to match all types of URLs
        self.url_pattern = re.compile(
            r'(?:https?://)?(?:www\.)?[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*(?:\.[a-zA-Z]{2,})(?:/[^\s]*)?',
            re.IGNORECASE
        )

        # Also match telegram.me, t.me links (with or without protocol)
        self.telegram_pattern = re.compile(
            r'(?:https?://)?(?:www\.)?(?:telegram\.me|t\.me)/[^\s]+',
            re.IGNORECASE
        )

        # Match email addresses
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            re.IGNORECASE
        )

        # Match Telegram usernames (@username) - comprehensive pattern
        # This matches @ followed by 1-32 word characters, then either non-word char or end of string
        self.username_pattern = re.compile(
            r'@\w{1,32}(?=\W|$)',
            re.IGNORECASE
        )

        # Alternative pattern for usernames (more permissive)
        self.username_pattern_alt = re.compile(
            r'@[a-zA-Z0-9_]{1,32}',
            re.IGNORECASE
        )

        # Match phone numbers (Iranian and international formats)
        self.phone_pattern = re.compile(
            r'(\+98|0)?9\d{9}|\+?\d{1,4}[\s\-\.]?\d{1,4}[\s\-\.]?\d{1,4}[\s\-\.]?\d{1,9}',
            re.IGNORECASE
        )

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Any],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # Skip if not a text message
        if not event.text:
            return await handler(event, data)

        user_id = event.from_user.id if event.from_user else 0

        # Check if user is in direct message or chat
        async with get_session() as session:
            user = await session.scalar(
                select(User).where(User.user_id == user_id)
            )

            if not user:
                return await handler(event, data)

            # Check if user is in direct message flow or chatting
            is_direct_or_chat = (
                user.step and user.step.startswith("direct_to_") or
                user.step == "chatting"
            )

            if not is_direct_or_chat:
                return await handler(event, data)

        # Check for links in the message
        message_text = event.text.strip()

        # Check for regular URLs (including without protocol)
        if self.url_pattern.search(message_text):
            await self._block_link(event)
            return

        # Check for Telegram links (with or without protocol)
        if self.telegram_pattern.search(message_text):
            await self._block_link(event)
            return

        # Check for email addresses
        if self.email_pattern.search(message_text):
            await self._block_link(event)
            return

        # Check for Telegram usernames (try both patterns for maximum coverage)
        if self.username_pattern.search(message_text) or self.username_pattern_alt.search(message_text):
            await self._block_link(event)
            return

        # Check for phone numbers
        if self.phone_pattern.search(message_text):
            await self._block_link(event)
            return

        # If no links found, continue with normal processing
        return await handler(event, data)

    def test_patterns(self, text: str) -> Dict[str, bool]:
        """Test all patterns against a text (for debugging)"""
        return {
            'url': bool(self.url_pattern.search(text)),
            'telegram': bool(self.telegram_pattern.search(text)),
            'email': bool(self.email_pattern.search(text)),
            'username': bool(self.username_pattern.search(text)),
            'username_alt': bool(self.username_pattern_alt.search(text)),
            'phone': bool(self.phone_pattern.search(text))
        }

    async def _block_link(self, event: Message) -> None:
        """Block the message containing link"""
        blocked_message = get_blocked_link_message()

        # Debug: print what was detected
        detected = self.test_patterns(event.text)
        detected_types = [k for k, v in detected.items() if v]
        if detected_types:
            print(f"DEBUG: Blocked message containing: {detected_types} - Text: '{event.text[:50]}...'")

        try:
            await event.delete()
            await event.bot.send_message(
                chat_id=event.chat.id,
                text=blocked_message,
                reply_to_message_id=None
            )
        except Exception as e:
            print(f"Error blocking link: {e}")
            # If delete fails, send warning message
            try:
                await event.bot.send_message(
                    chat_id=event.chat.id,
                    text=blocked_message,
                    reply_to_message_id=event.message_id
                )
            except Exception as e2:
                print(f"Error sending warning: {e2}")
