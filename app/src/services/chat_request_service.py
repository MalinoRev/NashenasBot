from typing import Optional
from datetime import datetime
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.databases.chat_requests import ChatRequest
from src.databases.users import User


class ChatRequestService:
    """Service for managing chat requests"""

    @staticmethod
    async def save_chat_request(sender_id: int, target_id: int) -> Optional[int]:
        """
        Save a new chat request to database

        Args:
            sender_id: Database ID of the user sending request
            target_id: Database ID of the target user

        Returns:
            int: Chat request ID if successful, None otherwise
        """
        try:
            print(f"LOG: ChatRequestService.save_chat_request called with sender_id={sender_id}, target_id={target_id}")
            async with get_session() as session:
                # Check if there's already an active request from this sender to this target
                print(f"LOG: Checking for existing request from {sender_id} to {target_id}")
                existing_request = await session.scalar(
                    select(ChatRequest).where(
                        ChatRequest.user_id == sender_id,
                        ChatRequest.target_id == target_id,
                        ChatRequest.accepted_at.is_(None),
                        ChatRequest.rejected_at.is_(None),
                        ChatRequest.canceled_at.is_(None)
                    )
                )

                if existing_request:
                    print(f"LOG: Found existing request id={existing_request.id}, resetting it")
                    # Delete the old notification message if it exists
                    if existing_request.request_message_id:
                        print(f"LOG: Found old request_message_id={existing_request.request_message_id}, deleting message")
                        try:
                            # We need to get the target user's Telegram ID to delete the message
                            target_user = await session.scalar(select(User).where(User.id == existing_request.target_id))
                            if target_user and target_user.user_id:
                                # Note: We can't actually delete the message here because we don't have bot instance
                                # This should be handled by the caller
                                print(f"LOG: Would delete message {existing_request.request_message_id} from user {target_user.user_id}")
                        except Exception as e:
                            print(f"LOG: Error handling old message deletion: {e}")

                    # Reset all timestamp fields and update created_at
                    existing_request.created_at = datetime.utcnow()
                    existing_request.accepted_at = None
                    existing_request.rejected_at = None
                    existing_request.canceled_at = None
                    existing_request.request_message_id = None
                    await session.commit()
                    print(f"LOG: Existing request reset and updated, returning id={existing_request.id}")
                    return existing_request.id

                print("LOG: No existing request found, creating new one")
                # Create new chat request
                chat_request = ChatRequest(
                    user_id=sender_id,
                    target_id=target_id
                )
                session.add(chat_request)
                await session.commit()

                # Refresh to get the ID
                await session.refresh(chat_request)
                print(f"LOG: New chat request created with id={chat_request.id}")
                return chat_request.id

        except Exception as e:
            print(f"ERROR: Failed to save chat request: {e}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    async def get_chat_request(request_id: int) -> Optional[ChatRequest]:
        """
        Get a chat request by ID

        Args:
            request_id: Chat request ID

        Returns:
            ChatRequest: The chat request object if found, None otherwise
        """
        try:
            async with get_session() as session:
                return await session.scalar(
                    select(ChatRequest).where(ChatRequest.id == request_id)
                )
        except Exception as e:
            print(f"ERROR: Failed to get chat request {request_id}: {e}")
            return None

    @staticmethod
    async def get_unread_chat_requests(target_id: int) -> list[ChatRequest]:
        """
        Get all unread chat requests for a user

        Args:
            target_id: Database ID of the target user

        Returns:
            list: List of unread chat requests
        """
        try:
            async with get_session() as session:
                result = await session.scalars(
                    select(ChatRequest).where(
                        ChatRequest.target_id == target_id,
                        ChatRequest.accepted_at.is_(None),
                        ChatRequest.rejected_at.is_(None)
                    ).order_by(desc(ChatRequest.created_at))
                )
                return list(result.all())
        except Exception as e:
            print(f"ERROR: Failed to get unread chat requests for {target_id}: {e}")
            return []



    @staticmethod
    async def accept_chat_request(request_id: int) -> tuple[bool, Optional[ChatRequest]]:
        """
        Accept a chat request

        Args:
            request_id: Chat request ID

        Returns:
            tuple: (success: bool, chat_request: ChatRequest | None)
        """
        try:
            async with get_session() as session:
                chat_request = await session.scalar(
                    select(ChatRequest).where(ChatRequest.id == request_id)
                )

                if not chat_request:
                    return False, None

                if chat_request.accepted_at or chat_request.rejected_at:
                    # Already processed
                    return False, chat_request

                chat_request.accepted_at = datetime.utcnow()
                await session.commit()

                return True, chat_request

        except Exception as e:
            print(f"ERROR: Failed to accept chat request {request_id}: {e}")
            return False, None

    @staticmethod
    async def reject_chat_request(request_id: int) -> tuple[bool, Optional[ChatRequest]]:
        """
        Reject a chat request

        Args:
            request_id: Chat request ID

        Returns:
            tuple: (success: bool, chat_request: ChatRequest | None)
        """
        try:
            async with get_session() as session:
                chat_request = await session.scalar(
                    select(ChatRequest).where(ChatRequest.id == request_id)
                )

                if not chat_request:
                    return False, None

                if chat_request.accepted_at or chat_request.rejected_at:
                    # Already processed
                    return False, chat_request

                chat_request.rejected_at = datetime.utcnow()
                await session.commit()

                return True, chat_request

        except Exception as e:
            print(f"ERROR: Failed to reject chat request {request_id}: {e}")
            return False, None

    @staticmethod
    async def update_request_message_id(request_id: int, message_id: int) -> bool:
        """
        Update the request_message_id for a chat request

        Args:
            request_id: Chat request ID
            message_id: Telegram message ID of the notification

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print(f"LOG: ChatRequestService.update_request_message_id called with request_id={request_id}, message_id={message_id}")
            async with get_session() as session:
                print(f"LOG: Looking for chat request with id={request_id}")
                chat_request = await session.scalar(
                    select(ChatRequest).where(ChatRequest.id == request_id)
                )

                if not chat_request:
                    print(f"LOG: Chat request {request_id} not found")
                    return False

                print(f"LOG: Chat request found, updating request_message_id from {chat_request.request_message_id} to {message_id}")
                chat_request.request_message_id = message_id
                await session.commit()
                print(f"LOG: Chat request updated successfully")

                return True

        except Exception as e:
            print(f"ERROR: Failed to update request message ID for {request_id}: {e}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    async def cancel_chat_request(user_id: int, target_id: int) -> tuple[bool, Optional[int]]:
        """
        Cancel a chat request and delete the notification message

        Args:
            user_id: User ID who sent the request (sender)
            target_id: Target user ID (receiver)

        Returns:
            tuple: (success: bool, message_id_to_delete: int | None)
        """
        try:
            async with get_session() as session:
                chat_request = await session.scalar(
                    select(ChatRequest).where(
                        ChatRequest.user_id == user_id,
                        ChatRequest.target_id == target_id,
                        ChatRequest.accepted_at.is_(None),
                        ChatRequest.rejected_at.is_(None),
                        ChatRequest.canceled_at.is_(None)
                    )
                )

                if not chat_request:
                    return False, None

                from datetime import datetime
                chat_request.canceled_at = datetime.utcnow()

                # Get the message ID to delete
                message_id_to_delete = chat_request.request_message_id

                await session.commit()

                return True, message_id_to_delete

        except Exception as e:
            print(f"ERROR: Failed to cancel chat request from {user_id} to {target_id}: {e}")
            return False, None

    @staticmethod
    async def get_chat_request_with_users(request_id: int) -> Optional[ChatRequest]:
        """
        Get a chat request with related user objects

        Args:
            request_id: Chat request ID

        Returns:
            ChatRequest: The chat request with user relationships loaded, None if not found
        """
        try:
            print(f"LOG: ChatRequestService.get_chat_request_with_users called with request_id={request_id}")
            async with get_session() as session:
                from sqlalchemy.orm import selectinload

                result = await session.scalar(
                    select(ChatRequest)
                    .where(ChatRequest.id == request_id)
                    .options(
                        selectinload(ChatRequest.user),
                        selectinload(ChatRequest.target)
                    )
                )
                print(f"LOG: ChatRequestService.get_chat_request_with_users result: {'Found' if result else 'Not found'}")
                if result:
                    print(f"LOG: Chat request details: id={result.id}, user_id={result.user_id}, target_id={result.target_id}, request_message_id={result.request_message_id}")
                return result
        except Exception as e:
            print(f"ERROR: Failed to get chat request with users {request_id}: {e}")
            import traceback
            traceback.print_exc()
            return None
