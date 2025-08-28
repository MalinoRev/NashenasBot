import os
from typing import Any, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select, update

from src.core.database import get_session
from src.databases.users import User


class ReferralMiddleware(BaseMiddleware):
    """
    Middleware to handle referral rewards after user authentication.
    Runs after all other middlewares to ensure user is properly authenticated.
    """

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Any],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        # First, let the handler process the event
        result = await handler(event, data)

        # After handler completes, check for referral processing
        user_id: Optional[int] = None

        if isinstance(event, Message):
            if event.from_user:
                user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            if event.from_user:
                user_id = event.from_user.id

        if not user_id:
            return result

        # Check if user has referral_queue and process it
        async with get_session() as session:
            # Get current user
            user: User | None = await session.scalar(
                select(User).where(User.user_id == user_id)
            )

            if not user or not user.referraled_queue:
                # No referral to process
                return result

            print(f"LOG: Processing referral for user {user_id}, referrer: {user.referraled_queue}")

            # Get referrer user
            referrer: User | None = await session.scalar(
                select(User).where(User.id == user.referraled_queue)
            )

            if not referrer:
                print(f"LOG: Referrer {user.referraled_queue} not found")
                return result

            # Get referral coin amount from environment
            try:
                referral_coin_amount = int(os.getenv("REFERRAL_COIN_AMOUNT", "10"))
            except (ValueError, TypeError):
                referral_coin_amount = 10  # Default value
                print(f"LOG: Invalid REFERRAL_COIN_AMOUNT, using default: {referral_coin_amount}")

            # Update referrer's credit
            old_credit = referrer.credit or 0
            new_credit = old_credit + referral_coin_amount

            # Update referrer's credit
            await session.execute(
                update(User)
                .where(User.id == referrer.id)
                .values(credit=new_credit)
            )

            # Update current user's referraled_by and clear referraled_queue
            await session.execute(
                update(User)
                .where(User.id == user.id)
                .values(
                    referraled_by=user.referraled_queue,
                    referraled_queue=None
                )
            )

            await session.commit()

            print(f"LOG: Referral processed - Referrer {referrer.id} credit: {old_credit} -> {new_credit}")

            # Send notification to referrer
            try:
                notification_message = (
                    f"🎉 تبریک!\n\n"
                    f"یک کاربر جدید با استفاده از لینک معرف شما در ربات ثبت نام کرد.\n\n"
                    f"💰 شما {referral_coin_amount} سکه دریافت کردید!\n"
                    f"💳 موجودی فعلی: {new_credit} سکه"
                )

                if isinstance(event, Message) and event.bot:
                    await event.bot.send_message(
                        chat_id=int(referrer.user_id),
                        text=notification_message
                    )
                elif isinstance(event, CallbackQuery) and event.bot:
                    await event.bot.send_message(
                        chat_id=int(referrer.user_id),
                        text=notification_message
                    )

                print(f"LOG: Referral notification sent to referrer {referrer.user_id}")

            except Exception as e:
                print(f"ERROR: Failed to send referral notification to {referrer.user_id}: {e}")

        return result
