# Physical AI & Humanoid Robotics Textbook

An AI-native educational resource on Physical AI and Humanoid Robotics, featuring a RAG-powered chatbot assistant.

## Features

- **6 Comprehensive Chapters** covering Physical AI from foundations to applications
- **RAG Chatbot Assistant** that answers questions based on textbook content
- **Bilingual Support** for English and Urdu
- **Math Rendering** with KaTeX for equations
- **Local Search** for quick content discovery

## Tech Stack

### Frontend
- Docusaurus 3.x (React-based static site generator)
- TypeScript
- KaTeX for math rendering
- Local search plugin

### Backend
- FastAPI (Python)
- Google Gemini for LLM responses
- Google text-embedding-004 for embeddings
- Qdrant for vector storage

## Project Structure

```
├── frontend/               # Docusaurus site
│   ├── docs/              # Markdown content (6 chapters)
│   ├── src/
│   │   ├── components/    # React components (Chatbot)
│   │   ├── css/           # Styles
│   │   ├── services/      # API client
│   │   └── theme/         # Theme customization
│   └── i18n/              # Urdu translations
│
├── backend/                # FastAPI server
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Config, rate limiting
│   │   ├── models/        # Pydantic models
│   │   └── services/      # Business logic
│   └── scripts/           # Content indexing
│
└── specs/                  # Specification documents
```

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- Google AI API key
- Qdrant Cloud account (or local instance)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Index content
python scripts/index_content.py

# Run server
python -m app.main
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm start
```

### Environment Variables

Create `backend/.env`:

```env
GOOGLE_API_KEY=your-google-ai-api-key
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check |
| `/api/v1/chat` | POST | RAG-powered chat |
| `/api/v1/search` | POST | Content search |

### Chat Request

```json
{
  "query": "What is Physical AI?",
  "language": "en",
  "history": []
}
```

### Chat Response

```json
{
  "answer": "Physical AI refers to...",
  "citations": [
    {
      "chapter_id": "01-intro-en",
      "chapter_title": "Introduction to Physical AI",
      "section_id": "what-is-physical-ai",
      "section_title": "What is Physical AI?",
      "path": "/01-intro"
    }
  ],
  "model": "gemini-2.0-flash-001",
  "language": "en"
}
```

## Content Chapters

1. **Introduction to Physical AI** - Overview and motivation
2. **Foundations of Humanoid Robotics** - Kinematics, dynamics, control
3. **Sensors and Perception** - Vision, touch, sensor fusion
4. **Actuators and Movement** - Motors, transmission, control
5. **AI Integration** - ML, RL, learning methods
6. **Applications and Future** - Real-world use cases

## Development

### Adding Content

1. Add/edit Markdown files in `frontend/docs/`
2. Re-run `python scripts/index_content.py` to update vectors

### Rate Limiting

Chat endpoint is rate-limited to 5 requests/minute per IP.

## Deployment

### Frontend (Vercel/Netlify)

```bash
cd frontend
npm run build
# Deploy `build/` directory
```

### Backend (Railway/Render)

```bash
cd backend
# Deploy with Python 3.11+ runtime
# Set environment variables in dashboard
```

## License

MIT

## Acknowledgments

- Built with [Docusaurus](https://docusaurus.io/)
- Powered by [Google Gemini](https://ai.google.dev/)
- Vector search by [Qdrant](https://qdrant.tech/)
