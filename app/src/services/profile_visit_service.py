from datetime import datetime
from sqlalchemy import select
from aiogram import Bot

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_settings import UserSetting
from src.context.messages.visitor.profile_visit_notification import get_profile_visit_notification


class ProfileVisitService:
    """Service for managing profile visit notifications"""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_profile_visit_notification(self, target_user_id: int, visitor_user_id: int) -> bool:
        """
        Send profile visit notification to target user if they have profile_visit_alarm enabled

        Args:
            target_user_id: Target user's database ID
            visitor_user_id: Visitor user's database ID

        Returns:
            bool: True if notification sent successfully
        """
        try:
            async with get_session() as session:
                # Get target user's settings
                settings: UserSetting | None = await session.scalar(
                    select(UserSetting).where(UserSetting.user_id == target_user_id)
                )

                # Check if user has profile_visit_alarm enabled
                # Default is False (0) if no settings exist
                alarm_enabled = False
                if settings:
                    alarm_enabled = settings.profile_visit_alarm

                # Don't send notification if alarm is disabled
                if not alarm_enabled:
                    return False

                # Get visitor info
                visitor: User | None = await session.scalar(
                    select(User).where(User.id == visitor_user_id)
                )
                if not visitor:
                    return False

                # Get target user's telegram ID
                target: User | None = await session.scalar(
                    select(User).where(User.id == target_user_id)
                )
                if not target or not target.user_id:
                    return False

                # Get visitor name
                visitor_name = visitor.tg_name or "کاربر"
                if visitor.unique_id:
                    visitor_name = f"/user_{visitor.unique_id}"

                # Send notification
                notification_text = get_profile_visit_notification(visitor_name)
                await self.bot.send_message(
                    chat_id=target.user_id,
                    text=notification_text
                )
                return True

        except Exception as e:
            print(f"Error sending profile visit notification: {e}")
            return False
