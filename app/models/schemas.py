from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Literal


# ==================== USER SCHEMAS ====================

class UserCreateRequest(BaseModel):
    """Request model for creating a new user"""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)


class UserResponse(BaseModel):
    """Response model for user data"""
    user_id: str
    email: str
    name: str
    created_at: str


# ==================== BOOK SCHEMAS ====================

class BookUploadRequest(BaseModel):
    """Request model for uploading a book/PDF"""
    book_title: str = Field(..., min_length=1, max_length=200)
    author: Optional[str] = Field(None, max_length=100)


class BookProcessRequest(BaseModel):
    """Request model for processing a book into vectors"""
    book_title: str = Field(..., min_length=1, max_length=200)
    chunk_size: int = Field(400, ge=100, le=2000, description="Size of text chunks for vectorization")
    chunk_overlap: int = Field(50, ge=0, le=500, description="Overlap between chunks")


class BookResponse(BaseModel):
    """Response model for book data"""
    book_id: str
    user_id: str
    book_title: str
    filename: str
    author: Optional[str]
    storage_path: str
    pinecone_namespace: str
    uploaded_at: str


class BookListResponse(BaseModel):
    """Response model for list of books"""
    books: List[BookResponse]
    total: int


# ==================== MESSAGE SCHEMAS ====================

class MessageRequest(BaseModel):
    """Request model for a single message/question"""
    question: str = Field(..., min_length=1, max_length=5000)


class MessageResponse(BaseModel):
    """Response model for a message"""
    message_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: str


# ==================== CHAT SCHEMAS ====================

class NewChatRequest(BaseModel):
    """Request model for creating a new chat"""
    user_id: str
    question: str = Field(..., min_length=1, max_length=5000)


class ContinueChatRequest(BaseModel):
    """Request model for continuing an existing chat"""
    chat_id: str
    question: str = Field(..., min_length=1, max_length=5000)


class ChatResponse(BaseModel):
    """Response model for chat data"""
    chat_id: str
    user_id: str
    title: str
    created_at: str
    updated_at: str
    messages: Optional[Dict[str, Dict]] = {}


class ChatDetailResponse(BaseModel):
    """Response model for detailed chat with messages"""
    chat_id: str
    user_id: str
    title: str
    created_at: str
    updated_at: str
    messages: List[MessageResponse]


class ChatListResponse(BaseModel):
    """Response model for list of chats"""
    chats: List[ChatResponse]
    total: int


class ChatMessageResponse(BaseModel):
    """Response model for a chat interaction (question + answer)"""
    chat_id: Optional[str] = None
    question: str
    answer: str
    continue_status: Optional[str] = None  # "c" for continue, "end" for end


# ==================== GENERIC RESPONSE SCHEMAS ====================

class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = True
    message: str
    data: Optional[Dict] = None


class ErrorResponse(BaseModel):
    """Generic error response"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    status_code: int = 400


class VectorProcessResponse(BaseModel):
    """Response for vector processing operations"""
    success: bool
    message: str
    namespace: Optional[str] = None
    chunks_count: Optional[int] = None


# ==================== UPLOAD SCHEMAS ====================

class FileUploadResponse(BaseModel):
    """Response for file upload operations"""
    success: bool
    message: str
    book_id: Optional[str] = None
    filename: Optional[str] = None
    storage_path: Optional[str] = None
