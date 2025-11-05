# Quick Start Guide - RAG Chat Backend API

Get your RAG Chat Backend API up and running in 5 minutes!

## Prerequisites

- Python 3.8 or higher installed
- API Keys ready:
  - OpenAI API Key
  - Pinecone API Key
  - Supabase URL and Service Key

## Step 1: Setup Environment

### Clone and Navigate
```bash
cd rag-chat-backend
```

### Create Virtual Environment
```bash
# Create venv
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/macOS)
source .venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 2: Configure Environment Variables

Create a `.env` file in the root directory:

```bash
# Copy the example file
cp .env.example .env

# Edit with your API keys
notepad .env  # Windows
nano .env     # Linux/macOS
```

Add your keys:
```env
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=pcsk_...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=eyJhbG...
```

## Step 3: Start the Server

### Option A: Using Startup Script
```bash
# Windows
start.bat

# Linux/macOS
./start.sh
```

### Option B: Direct Command
```bash
python main.py
```

The server will start at: **http://localhost:8000**

## Step 4: Verify It's Working

### Open API Documentation
Open your browser and visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Or Test with Command Line
```bash
# Test root endpoint
curl http://localhost:8000/

# Test health check
curl http://localhost:8000/health

# Or use the test script
python test_api.py
```

## Step 5: Try Your First Request

### Register a User
```bash
curl -X POST "http://localhost:8000/api/users/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "name": "Test User"}'
```

Expected response:
```json
{
  "user_id": "uuid-here",
  "email": "test@example.com",
  "name": "Test User",
  "created_at": "2025-01-01T00:00:00Z"
}
```

### Upload a Book (via Swagger UI)
1. Go to http://localhost:8000/docs
2. Find `POST /api/books/upload-and-process`
3. Click "Try it out"
4. Fill in:
   - **file**: Select your PDF
   - **user_id**: Your user_id from registration
   - **book_title**: "My First Book"
   - **author**: "Author Name"
5. Click "Execute"

### Start a Chat
```bash
curl -X POST "http://localhost:8000/api/chats/new" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "your-user-id",
    "question": "What is this book about?"
  }'
```

## Common Commands

### Start Server
```bash
python main.py
```

### Stop Server
Press `CTRL+C` in the terminal

### View Logs
Check the terminal where the server is running

### Test API
```bash
python test_api.py
```

### Import Postman Collection
1. Open Postman
2. Click "Import"
3. Select `RAG_Chat_API.postman_collection.json`
4. Start testing!

## Troubleshooting

### Server Won't Start
```bash
# Check if port 8000 is already in use
# Windows
netstat -ano | findstr :8000

# Linux/macOS
lsof -i :8000

# Kill the process or change port in main.py
```

### Module Not Found Error
```bash
# Make sure venv is activated
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# Reinstall dependencies
pip install -r requirements.txt
```

### Environment Variables Not Loading
```bash
# Check .env file exists
ls -la .env  # Linux/macOS
dir .env     # Windows

# Verify format (no spaces around =)
OPENAI_API_KEY=sk-...  # ✓ Correct
OPENAI_API_KEY = sk-...  # ✗ Wrong
```

### Database Connection Error
- Verify Supabase URL and key are correct
- Check if Supabase project is active
- Ensure database tables are created

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Read Documentation**: Check `README.md` for detailed info
3. **Test Endpoints**: Use the Postman collection
4. **Build a Frontend**: Connect your web app to the API

## Support

- **Documentation**: See `README.md`
- **API Reference**: http://localhost:8000/docs
- **Issues**: Open an issue on GitHub

## Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/api/users/register` | POST | Register user |
| `/api/users/login` | POST | Login user |
| `/api/books/upload-and-process` | POST | Upload PDF |
| `/api/chats/new` | POST | Start chat |
| `/api/chats/continue` | POST | Continue chat |
| `/api/chats/user/{user_id}` | GET | Get user chats |

**Happy Coding! 🚀**
