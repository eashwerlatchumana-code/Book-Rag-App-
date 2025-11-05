from fastapi import APIRouter, HTTPException
from typing import List

from app.models.schemas import MessageResponse
from app.database.messages_repo import MessagesRepo


router = APIRouter(
    prefix="/api/messages",
    tags=["messages"]
)


@router.get("/chat/{chat_id}", response_model=List[MessageResponse])
async def get_chat_messages(chat_id: str):
    """
    Get all messages for a specific chat.

    Retrieves all messages in chronological order for a given chat session.

    Args:
        chat_id: ID of the chat

    Returns:
        List of MessageResponse objects

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        messages_repo = MessagesRepo()
        messages_list = messages_repo.get_messages_by_chat_id(chat_id=chat_id)

        if not messages_list:
            messages_list = []

        # Sort messages by created_at to ensure chronological order
        sorted_messages = sorted(messages_list, key=lambda x: x.get('created_at', ''))

        # Convert to response format
        message_responses = []
        for msg in sorted_messages:
            message_responses.append(MessageResponse(
                message_id=msg.get('message_id'),
                role=msg.get('role'),
                content=msg.get('content'),
                created_at=msg.get('created_at')
            ))

        return message_responses

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving messages: {str(e)}"
        )


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message_by_id(message_id: str):
    """
    Get a specific message by its ID.

    Args:
        message_id: ID of the message

    Returns:
        MessageResponse with message details

    Raises:
        HTTPException: If message not found
    """
    try:
        messages_repo = MessagesRepo()
        message = messages_repo.get_message_by_id(message_id=message_id)

        if not message:
            raise HTTPException(
                status_code=404,
                detail=f"Message with ID '{message_id}' not found"
            )

        return MessageResponse(
            message_id=message.get('message_id'),
            role=message.get('role'),
            content=message.get('content'),
            created_at=message.get('created_at')
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving message: {str(e)}"
        )
