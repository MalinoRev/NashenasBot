from sqlalchemy import select
from aiogram import Bot

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_settings import UserSetting
from src.context.messages.visitor.profile_like_notification import get_profile_like_notification


class ProfileLikeService:
    """Service for managing profile like notifications"""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_profile_like_notification(self, target_user_id: int, liker_user_id: int) -> bool:
        """
        Send profile like notification to target user if they have profile_like_alarm enabled

        Args:
            target_user_id: Target user's database ID
            liker_user_id: Liker user's database ID

        Returns:
            bool: True if notification sent successfully
        """
        try:
            async with get_session() as session:
                # Get target user's settings
                settings: UserSetting | None = await session.scalar(
                    select(UserSetting).where(UserSetting.user_id == target_user_id)
                )

                # Check if user has profile_like_alarm enabled
                # Default is False (0) if no settings exist
                alarm_enabled = False
                if settings:
                    alarm_enabled = settings.profile_like_alarm

                # Don't send notification if alarm is disabled
                if not alarm_enabled:
                    return False

                # Get liker info
                liker: User | None = await session.scalar(
                    select(User).where(User.id == liker_user_id)
                )
                if not liker:
                    return False

                # Get target user's telegram ID
                target: User | None = await session.scalar(
                    select(User).where(User.id == target_user_id)
                )
                if not target or not target.user_id:
                    return False

                # Get liker name
                liker_name = liker.tg_name or "کاربر"
                if liker.unique_id:
                    liker_name = f"/user_{liker.unique_id}"

                # Send notification
                notification_text = get_profile_like_notification(liker_name)
                await self.bot.send_message(
                    chat_id=target.user_id,
                    text=notification_text
                )
                return True

        except Exception as e:
            print(f"Error sending profile like notification: {e}")
            return False
