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
            async with get_session() as session:
                # Check if there's already an active request from this sender to this target
                existing_request = await session.scalar(
                    select(ChatRequest).where(
                        ChatRequest.user_id == sender_id,
                        ChatRequest.target_id == target_id,
                        ChatRequest.accepted_at.is_(None),
                        ChatRequest.rejected_at.is_(None)
                    )
                )

                if existing_request:
                    # Update the created_at timestamp to make it recent
                    existing_request.created_at = datetime.utcnow()
                    await session.commit()
                    return existing_request.id

                # Create new chat request
                chat_request = ChatRequest(
                    user_id=sender_id,
                    target_id=target_id
                )
                session.add(chat_request)
                await session.commit()

                # Refresh to get the ID
                await session.refresh(chat_request)
                return chat_request.id

        except Exception as e:
            print(f"ERROR: Failed to save chat request: {e}")
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
    async def get_chat_request_with_users(request_id: int) -> Optional[ChatRequest]:
        """
        Get a chat request with related user objects

        Args:
            request_id: Chat request ID

        Returns:
            ChatRequest: The chat request with user relationships loaded, None if not found
        """
        try:
            async with get_session() as session:
                from sqlalchemy.orm import selectinload

                return await session.scalar(
                    select(ChatRequest)
                    .where(ChatRequest.id == request_id)
                    .options(
                        selectinload(ChatRequest.user),
                        selectinload(ChatRequest.target)
                    )
                )
        except Exception as e:
            print(f"ERROR: Failed to get chat request with users {request_id}: {e}")
            return None
