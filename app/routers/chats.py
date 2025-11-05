from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, List

from app.models.schemas import (
    NewChatRequest,
    ContinueChatRequest,
    ChatResponse,
    ChatDetailResponse,
    ChatListResponse,
    ChatMessageResponse,
    MessageResponse,
    SuccessResponse
)
from app.services.chat_service import ChatService
from app.database.chats_repo import chatsRepo
from app.database.messages_repo import MessagesRepo


router = APIRouter(
    prefix="/api/chats",
    tags=["chats"]
)


@router.post("/new", response_model=ChatMessageResponse, status_code=201)
async def create_new_chat(request: NewChatRequest):
    """
    Create a new chat session and get the first response.

    This endpoint:
    1. Creates a new chat session for the user
    2. Processes the user's first question
    3. Uses RAG (Retrieval Augmented Generation) to search user's uploaded books
    4. Returns the AI-generated response

    Args:
        request: NewChatRequest with user_id and question

    Returns:
        ChatMessageResponse with chat_id, question, and AI answer

    Raises:
        HTTPException: If chat creation or processing fails
    """
    try:
        # Initialize ChatService
        chat_service = ChatService(
            user_id=request.user_id,
            question=request.question,
            retrieve_history=False
        )

        # Create new chat
        result = chat_service.new_chat(
            question=request.question,
            vectorstore=chat_service.vectorstore
        )

        if not result or result == "end":
            raise HTTPException(
                status_code=500,
                detail="Failed to create chat or generate response"
            )

        # Get the chat_id that was just created
        chats_repo_instance = chatsRepo()
        all_chats = chats_repo_instance.get_all_chats(user_id=request.user_id)

        if all_chats and len(all_chats) > 0:
            # Sort by created_at and get the most recent
            sorted_chats = sorted(all_chats, key=lambda x: x.get('created_at', ''), reverse=True)
            chat_id = sorted_chats[0].get('chat_id')

            return ChatMessageResponse(
                chat_id=chat_id,
                question=request.question,
                answer=result,
                continue_status="c"
            )
        else:
            # Fallback if we can't get the chat_id
            return ChatMessageResponse(
                chat_id=None,
                question=request.question,
                answer=result,
                continue_status="c"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating new chat: {str(e)}"
        )


@router.post("/continue", response_model=ChatMessageResponse)
async def continue_existing_chat(request: ContinueChatRequest):
    """
    Continue an existing chat conversation.

    This endpoint:
    1. Retrieves the chat history
    2. Processes the new question with context from previous messages
    3. Uses RAG to search user's books for relevant information
    4. Returns the AI-generated response

    Args:
        request: ContinueChatRequest with chat_id and question

    Returns:
        ChatMessageResponse with chat_id, question, and AI answer

    Raises:
        HTTPException: If chat not found or processing fails
    """
    try:
        # Verify chat exists
        chats_repo_instance = chatsRepo()
        chat_data = chats_repo_instance.get_chat_by_id(chat_id=request.chat_id)

        if not chat_data:
            raise HTTPException(
                status_code=404,
                detail=f"Chat with ID '{request.chat_id}' not found"
            )

        # Get user_id from chat
        user_id = chat_data.get('user_id')

        # Initialize ChatService
        chat_service = ChatService(
            user_id=user_id,
            question=request.question,
            retrieve_history=True
        )

        # Continue existing chat
        result = chat_service.continuing_chat(
            chat_id=request.chat_id,
            question=request.question
        )

        if not result or result == "end":
            raise HTTPException(
                status_code=500,
                detail="Failed to continue chat or generate response"
            )

        return ChatMessageResponse(
            chat_id=request.chat_id,
            question=request.question,
            answer=result,
            continue_status="c"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error continuing chat: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=ChatListResponse)
async def get_user_chats(user_id: str):
    """
    Get all chats for a specific user.

    Returns a list of all chat sessions created by the user,
    sorted by creation date (most recent first).

    Args:
        user_id: ID of the user

    Returns:
        ChatListResponse with list of chats and total count

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        chats_repo_instance = chatsRepo()
        chats = chats_repo_instance.get_all_chats(user_id=user_id)

        if not chats:
            chats = []

        # Convert to response format
        chat_responses = []
        for chat in chats:
            chat_responses.append(ChatResponse(
                chat_id=chat.get('chat_id'),
                user_id=chat.get('user_id'),
                title=chat.get('chat_title', 'Untitled Chat'),
                created_at=chat.get('created_at'),
                updated_at=chat.get('updated_at', chat.get('created_at')),
                messages=chat.get('messages', {})
            ))

        return ChatListResponse(
            chats=chat_responses,
            total=len(chat_responses)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving chats: {str(e)}"
        )


@router.get("/{chat_id}", response_model=ChatDetailResponse)
async def get_chat_by_id(chat_id: str):
    """
    Get detailed chat information including all messages.

    Retrieves a specific chat with its full message history,
    sorted chronologically.

    Args:
        chat_id: ID of the chat

    Returns:
        ChatDetailResponse with chat details and messages

    Raises:
        HTTPException: If chat not found
    """
    try:
        chats_repo_instance = chatsRepo()
        chat_data = chats_repo_instance.get_chat_by_id(chat_id=chat_id)

        if not chat_data:
            raise HTTPException(
                status_code=404,
                detail=f"Chat with ID '{chat_id}' not found"
            )

        # Get messages from messages_table for proper ordering
        messages_repo = MessagesRepo()
        messages_list = messages_repo.get_messages_by_chat_id(chat_id=chat_id)

        # Convert messages to response format
        message_responses = []
        if messages_list:
            # Sort messages by created_at to ensure chronological order
            sorted_messages = sorted(messages_list, key=lambda x: x.get('created_at', ''))

            for msg in sorted_messages:
                message_responses.append(MessageResponse(
                    message_id=msg.get('message_id'),
                    role=msg.get('role'),
                    content=msg.get('content'),
                    created_at=msg.get('created_at')
                ))

        return ChatDetailResponse(
            chat_id=chat_data.get('chat_id'),
            user_id=chat_data.get('user_id'),
            title=chat_data.get('chat_title', 'Untitled Chat'),
            created_at=chat_data.get('created_at'),
            updated_at=chat_data.get('updated_at', chat_data.get('created_at')),
            messages=message_responses
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving chat: {str(e)}"
        )


@router.delete("/{chat_id}", response_model=SuccessResponse)
async def delete_chat(chat_id: str):
    """
    Delete a chat and its associated messages.

    This will permanently delete the chat session and all its messages.

    Args:
        chat_id: ID of the chat to delete

    Returns:
        SuccessResponse confirming deletion

    Raises:
        HTTPException: If chat not found or deletion fails
    """
    try:
        chats_repo_instance = chatsRepo()

        # Check if chat exists
        chat_data = chats_repo_instance.get_chat_by_id(chat_id=chat_id)
        if not chat_data:
            raise HTTPException(
                status_code=404,
                detail=f"Chat with ID '{chat_id}' not found"
            )

        # Delete chat (this should cascade to delete messages in database)
        result = chats_repo_instance.delete_chat(chat_id=chat_id)

        return SuccessResponse(
            success=True,
            message=f"Chat deleted successfully",
            data={"chat_id": chat_id}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting chat: {str(e)}"
        )
