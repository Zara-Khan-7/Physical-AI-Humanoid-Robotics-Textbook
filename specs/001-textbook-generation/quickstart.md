# Quickstart: AI-Native Textbook with RAG Chatbot

**Feature**: 001-textbook-generation
**Date**: 2025-12-07

---

## Prerequisites

- Node.js 18+ (for Docusaurus frontend)
- Python 3.11+ (for FastAPI backend)
- Google Cloud account with Gemini API access
- Qdrant Cloud account (free tier)

---

## 1. Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd Hackathon

# Switch to feature branch
git checkout 001-textbook-generation
```

---

## 2. Backend Setup

### Install Dependencies

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Google AI
GOOGLE_API_KEY=your_gemini_api_key

# Qdrant Cloud
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION=textbook_chunks

# Model Configuration
EMBEDDING_MODEL=models/text-embedding-004
EMBEDDING_DIM=768
LLM_MODEL=gemini-2.0-flash-001

# Server
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Index Content (One-time)

```bash
# From backend directory
python scripts/index_content.py --docs-path ../frontend/docs
```

This will:
1. Parse all Markdown files from `frontend/docs/`
2. Chunk content by headers (512-1000 tokens)
3. Generate embeddings via Google text-embedding-004
4. Store vectors in Qdrant

### Run Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Verify at: http://localhost:8000/api/v1/health

---

## 3. Frontend Setup

### Install Dependencies

```bash
cd frontend
npm install
```

### Configure API Endpoint

Edit `src/services/api.ts`:

```typescript
const API_BASE_URL = process.env.NODE_ENV === 'production'
  ? 'https://api.your-domain.com'
  : 'http://localhost:8000';
```

### Run Development Server

```bash
npm run start
```

Open: http://localhost:3000

---

## 4. Verify Setup

### Test Chatbot

1. Navigate to any chapter page
2. Click the chat icon in the bottom-right corner
3. Ask: "What is Physical AI?"
4. Verify response includes citations

### Test Search

1. Click the search bar (or press `/`)
2. Search for "ROS 2"
3. Verify results link to correct sections

### Test Progress Tracking

1. Read a chapter section
2. Check localStorage for `textbook_progress`
3. Navigate away and return - verify progress persists

---

## 5. API Quick Reference

### Chat Endpoint

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is Physical AI?",
    "session_id": "test-session-123"
  }'
```

### Search Endpoint

```bash
curl "http://localhost:8000/api/v1/search?q=humanoid%20robot&limit=5"
```

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

---

## 6. Development Workflow

### Adding Content

1. Create/edit Markdown files in `frontend/docs/`
2. Re-run indexing: `python scripts/index_content.py`
3. Refresh Docusaurus: content updates automatically

### Modifying Chatbot UI

1. Edit components in `frontend/src/components/ChatBot/`
2. Styles in `frontend/src/css/chatbot.css`
3. Hot reload in development mode

### Backend Changes

1. Edit FastAPI routes in `backend/app/api/routes/`
2. Update services in `backend/app/services/`
3. Auto-reload with `--reload` flag

---

## 7. Common Issues

### "Qdrant connection failed"

- Verify `QDRANT_URL` and `QDRANT_API_KEY` in `.env`
- Check Qdrant Cloud console for cluster status
- Free tier suspends after 1 week of inactivity

### "Rate limit exceeded"

- Gemini free tier: 15 requests/minute
- Wait 60 seconds or upgrade API tier
- Backend returns `Retry-After` header

### "No relevant content found"

- Ensure indexing completed successfully
- Check Qdrant console for vector count
- Verify query language matches indexed content

### CORS errors in browser

- Verify `CORS_ORIGINS` includes your frontend URL
- Check backend logs for CORS middleware output

---

## 8. Production Deployment

### Frontend (Static)

```bash
cd frontend
npm run build
# Deploy `build/` to Vercel, Netlify, or static hosting
```

### Backend (Container)

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Deploy to:
- Railway (free tier available)
- Render (free tier available)
- Google Cloud Run
- AWS Lambda with Mangum

---

## 9. Environment Summary

| Service | Free Tier Limits | Dashboard |
|---------|------------------|-----------|
| Google Gemini | 15 req/min, 1500/day | [AI Studio](https://aistudio.google.com/) |
| Qdrant Cloud | 1GB storage | [Qdrant Console](https://cloud.qdrant.io/) |
| Vercel (frontend) | 100GB bandwidth/mo | [Vercel Dashboard](https://vercel.com/dashboard) |
| Railway (backend) | $5 credit/mo | [Railway Dashboard](https://railway.app/dashboard) |

---

## Next Steps

1. Review [spec.md](./spec.md) for full requirements
2. Review [plan.md](./plan.md) for architecture details
3. Run `/sp.tasks` to generate implementation tasks
