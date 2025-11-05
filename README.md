# RAG Chat Backend API

A FastAPI-based Retrieval-Augmented Generation (RAG) chat application that allows users to upload PDF books and chat with AI about their content using OpenAI, Pinecone, and Supabase.

## Features

- **Book Management**: Upload and process PDF documents
- **Intelligent Chat**: Chat with AI about your uploaded books
- **RAG Technology**: Uses vector similarity search to find relevant content
- **Chat History**: Maintain and retrieve conversation history
- **User Management**: User registration and authentication
- **RESTful API**: Clean, well-documented REST API endpoints

## Tech Stack

- **Framework**: FastAPI
- **Language Model**: OpenAI GPT
- **Vector Database**: Pinecone
- **Database**: Supabase (PostgreSQL)
- **Document Processing**: LangChain, PyPDF
- **Server**: Uvicorn

## Prerequisites

- Python 3.8+
- OpenAI API Key
- Pinecone API Key
- Supabase Account (URL and Service Key)

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd rag-chat-backend
```

2. **Create a virtual environment**
```bash
python -m venv .venv
```

3. **Activate the virtual environment**
- Windows:
```bash
.venv\Scripts\activate
```
- macOS/Linux:
```bash
source .venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Set up environment variables**

Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
```

## Running the Application

### Development Mode

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Root & Health

#### `GET /`
Get API information and available endpoints.

**Response:**
```json
{
  "message": "RAG Chat Backend API",
  "version": "1.0.0",
  "status": "running",
  "documentation": {
    "swagger_ui": "/docs",
    "redoc": "/redoc"
  },
  "endpoints": {
    "users": "/api/users",
    "chats": "/api/chats",
    "messages": "/api/messages",
    "books": "/api/books"
  }
}
```

#### `GET /health`
Health check endpoint for monitoring.

### Users (`/api/users`)

#### `POST /api/users/register`
Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "name": "John Doe"
}
```

**Response (201):**
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2025-01-01T00:00:00Z"
}
```

#### `POST /api/users/login`
Login user by email or name.

**Query Parameters:**
- `email` (optional): User's email
- `name` (optional): User's name

**Response (200):**
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2025-01-01T00:00:00Z"
}
```

#### `GET /api/users/{user_id}`
Get user details by user ID.

#### `GET /api/users/email/{email}`
Get user details by email.

#### `GET /api/users/name/{name}`
Get user details by name.

### Chats (`/api/chats`)

#### `POST /api/chats/new`
Create a new chat and get the first AI response.

**Request Body:**
```json
{
  "user_id": "uuid",
  "question": "What is the main theme of the book?"
}
```

**Response (201):**
```json
{
  "chat_id": "uuid",
  "question": "What is the main theme of the book?",
  "answer": "Based on your uploaded books, the main theme...",
  "continue_status": "c"
}
```

#### `POST /api/chats/continue`
Continue an existing chat conversation.

**Request Body:**
```json
{
  "chat_id": "uuid",
  "question": "Can you elaborate on that?"
}
```

**Response (200):**
```json
{
  "chat_id": "uuid",
  "question": "Can you elaborate on that?",
  "answer": "Certainly! Let me provide more details...",
  "continue_status": "c"
}
```

#### `GET /api/chats/user/{user_id}`
Get all chats for a specific user.

**Response (200):**
```json
{
  "chats": [
    {
      "chat_id": "uuid",
      "user_id": "uuid",
      "title": "Chat about Book Title",
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:05:00Z",
      "messages": {}
    }
  ],
  "total": 1
}
```

#### `GET /api/chats/{chat_id}`
Get detailed chat information including all messages.

**Response (200):**
```json
{
  "chat_id": "uuid",
  "user_id": "uuid",
  "title": "Chat about Book Title",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:05:00Z",
  "messages": [
    {
      "message_id": "uuid",
      "role": "user",
      "content": "What is the main theme?",
      "created_at": "2025-01-01T00:00:00Z"
    },
    {
      "message_id": "uuid",
      "role": "assistant",
      "content": "The main theme is...",
      "created_at": "2025-01-01T00:00:01Z"
    }
  ]
}
```

#### `DELETE /api/chats/{chat_id}`
Delete a chat and its associated messages.

### Messages (`/api/messages`)

#### `GET /api/messages/chat/{chat_id}`
Get all messages for a specific chat.

**Response (200):**
```json
[
  {
    "message_id": "uuid",
    "role": "user",
    "content": "What is the main theme?",
    "created_at": "2025-01-01T00:00:00Z"
  },
  {
    "message_id": "uuid",
    "role": "assistant",
    "content": "The main theme is...",
    "created_at": "2025-01-01T00:00:01Z"
  }
]
```

#### `GET /api/messages/{message_id}`
Get a specific message by its ID.

### Books (`/api/books`)

#### `POST /api/books/upload`
Upload a PDF book and create a database record.

**Request (multipart/form-data):**
- `file`: PDF file
- `user_id`: User ID
- `book_title`: Title of the book
- `author` (optional): Author name

**Response (200):**
```json
{
  "success": true,
  "message": "Book uploaded successfully",
  "book_id": "uuid",
  "filename": "book.pdf",
  "storage_path": "path/to/book.pdf"
}
```

#### `POST /api/books/upload-and-process`
Upload a PDF book and process it into vector embeddings (one operation).

**Request (multipart/form-data):**
- `file`: PDF file
- `user_id`: User ID
- `book_title`: Title of the book
- `author` (optional): Author name
- `chunk_size` (optional, default: 400): Size of text chunks
- `chunk_overlap` (optional, default: 50): Overlap between chunks

**Response (200):**
```json
{
  "success": true,
  "message": "Book uploaded and processed successfully. 150 chunks created.",
  "namespace": "user_uuid",
  "chunks_count": 150
}
```

#### `POST /api/books/process/{book_title}`
Process an already uploaded book into vector embeddings.

**Query Parameters:**
- `chunk_size` (optional, default: 400): Size of text chunks
- `chunk_overlap` (optional, default: 50): Overlap between chunks

#### `GET /api/books/user/{user_id}`
Get all books for a specific user.

**Response (200):**
```json
{
  "books": [
    {
      "book_id": "uuid",
      "user_id": "uuid",
      "book_title": "Example Book",
      "filename": "book.pdf",
      "author": "John Author",
      "storage_path": "path/to/book.pdf",
      "pinecone_namespace": "user_uuid",
      "uploaded_at": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

#### `GET /api/books/{book_title}`
Get book details by title.

#### `DELETE /api/books/{book_title}`
Delete a book and its associated data.

## Example Usage

### Using cURL

**Register a user:**
```bash
curl -X POST "http://localhost:8000/api/users/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "name": "John Doe"}'
```

**Upload and process a book:**
```bash
curl -X POST "http://localhost:8000/api/books/upload-and-process" \
  -F "file=@/path/to/book.pdf" \
  -F "user_id=your-user-id" \
  -F "book_title=My Book" \
  -F "author=John Author"
```

**Start a new chat:**
```bash
curl -X POST "http://localhost:8000/api/chats/new" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "your-user-id",
    "question": "What is this book about?"
  }'
```

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Register user
response = requests.post(
    f"{BASE_URL}/api/users/register",
    json={"email": "user@example.com", "name": "John Doe"}
)
user = response.json()
user_id = user["user_id"]

# Upload and process book
with open("book.pdf", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/api/books/upload-and-process",
        files={"file": f},
        data={
            "user_id": user_id,
            "book_title": "My Book",
            "author": "John Author"
        }
    )

# Start a chat
response = requests.post(
    f"{BASE_URL}/api/chats/new",
    json={
        "user_id": user_id,
        "question": "What is this book about?"
    }
)
chat = response.json()
print(f"AI Response: {chat['answer']}")
```

## Project Structure

```
rag-chat-backend/
  app/
     __init__.py
     database/           # Database repositories
        base.py
        users_repo.py
        chats_repo.py
        messages_repo.py
        books_repo.py
     models/             # Pydantic schemas
        schemas.py
     routers/            # API endpoints
        users.py
        chats.py
        messages.py
        books.py
     services/           # Business logic
        chat_service.py
        book_processing_service.py
        openai_service.py
        pinecone_service.py
        ragappfunction.py
     utils/              # Utility functions
         logger.py
  main.py                 # FastAPI application entry point
  requirements.txt        # Python dependencies
  .env                    # Environment variables (not in git)
  README.md              # This file
```

## How It Works

1. **User Registration**: Users register with email and name
2. **Book Upload**: Users upload PDF books which are:
   - Stored in Supabase Storage
   - Processed into text chunks
   - Converted to embeddings using OpenAI
   - Stored in Pinecone vector database with user-specific namespace
3. **Chat**: When users ask questions:
   - The question is converted to an embedding
   - Similar chunks are retrieved from Pinecone
   - Context + question is sent to OpenAI
   - AI generates response using RAG
   - Conversation history is maintained

## Database Schema

### Users Table
- `user_id` (UUID, PK)
- `email` (String, Unique)
- `name` (String)
- `created_at` (Timestamp)

### Books Table
- `book_id` (UUID, PK)
- `user_id` (UUID, FK)
- `book_title` (String)
- `filename` (String)
- `author` (String, Optional)
- `storage_path` (String)
- `pinecone_namespace` (String)
- `uploaded_at` (Timestamp)

### Chats Table
- `chat_id` (UUID, PK)
- `user_id` (UUID, FK)
- `chat_title` (String)
- `messages` (JSONB)
- `created_at` (Timestamp)
- `updated_at` (Timestamp)

### Messages Table
- `message_id` (UUID, PK)
- `chat_id` (UUID, FK)
- `role` (String: user/assistant/system)
- `content` (Text)
- `created_at` (Timestamp)

## Error Handling

The API uses standard HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `404` - Not Found
- `500` - Internal Server Error

Error responses follow this format:
```json
{
  "detail": "Error message here"
}
```

## CORS Configuration

CORS is configured to allow all origins in development. For production, update the `allow_origins` in main.py:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Update this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

[Add your license here]

## Support

For issues and questions, please open an issue on the GitHub repository.

## Acknowledgments

- OpenAI for GPT models
- Pinecone for vector database
- LangChain for RAG framework
- FastAPI for the web framework
- Supabase for database and storage

---

## Development Notes (Previous Implementation)

1. Test1_ragapp was the original file where RAG app functions were built from scratch.
2. 'Withimport' file and 'Ragappfunctions' file contain defined functions for each process: adding a doc, making it into chunks, uploading to the vectordb, etc.
3. These functions were created to be reusable when building the RAG app from scratch.
4. The 'shortstory' PDF used for testing is in the Co-Op folder, and code files are in the code-files directory.
5. Note: Some LangChain functions used are deprecated and may show warnings, but this does not impact functionality.
