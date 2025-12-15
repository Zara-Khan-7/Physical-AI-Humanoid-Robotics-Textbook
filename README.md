# Physical AI & Humanoid Robotics Textbook

An AI-native educational resource on Physical AI and Humanoid Robotics, featuring a multi-agent RAG-powered system with a neon futuristic glassmorphism UI.

## Features

### Core Features
- **6 Comprehensive Chapters** covering Physical AI from foundations to applications
- **Multi-Agent RAG System** with 8 specialized AI agents and 29+ skills
- **Bilingual Support** for English and Urdu with RTL rendering
- **Math Rendering** with KaTeX for equations
- **Local Search** for quick content discovery

### AI-Powered Features
- **Intelligent Chatbot** with context-aware responses and citations
- **Content Personalization** adapting difficulty to user level
- **Real-time Translation** to Urdu with proper RTL formatting
- **User Progress Tracking** with analytics dashboard
- **Smart Quiz Generation** based on chapter content

### UI/UX Features
- **Neon Futuristic Theme** with glassmorphism effects
- **Animated Interactions** with energy waves and glowing effects
- **Responsive Design** optimized for all devices
- **User Authentication** with session management
- **Progress Dashboard** with achievements and activity tracking

---

## Multi-Agent Architecture

The backend implements a sophisticated multi-agent system with specialized agents for different tasks:

### Agent Overview

| Agent | Description | Skills |
|-------|-------------|--------|
| **ContentAgent** | Generates and manages educational content | `createContent`, `generateQuizzes`, `explainConcepts` |
| **CodeAgent** | Handles code-related queries and generation | `generateCode`, `fixCode`, `explainCode` |
| **RAGAgent** | Retrieval-Augmented Generation for Q&A | `ragQuery`, `searchChapters`, `retrieveSections` |
| **PersonalizationAgent** | Adapts content to user preferences | `personalizeContent`, `adaptDifficulty`, `recommendChapters` |
| **TranslationAgent** | Handles English-Urdu translation | `translateToUrdu`, `formatRTL`, `translateTerms` |
| **AuthAgent** | User authentication and session management | `getProfile`, `updateProfile`, `validateSession`, `createSession`, `registerUser`, `deleteSession` |
| **HistoryAgent** | Tracks user interactions and analytics | `recordEvent`, `queryHistory`, `getAnalytics`, `exportHistory`, `getUserHistory` |
| **UIAgent** | Manages UI theming and components | `getTheme`, `generateComponent`, `getAnimationConfig`, `generateGradient`, `getChatbotVisualization` |

### Agent System Components

```
backend/app/agents/
├── base.py                  # BaseAgent class, AgentContext, AgentResponse
├── registry.py              # AgentRegistry singleton for agent management
├── router.py                # Intent-based AgentRouter for query routing
├── content_agent.py         # Educational content generation
├── code_agent.py            # Code assistance and explanation
├── rag_agent.py             # RAG-powered Q&A
├── personalization_agent.py # Content adaptation
├── translation_agent.py     # Urdu translation
├── auth_agent.py            # Authentication
├── history_agent.py         # PHR and analytics
├── ui_agent.py              # Theme and UI management
└── __init__.py              # Module exports
```

### How Agents Work

1. **Query Routing**: The `AgentRouter` analyzes incoming queries and routes them to the appropriate agent(s) based on intent detection.

2. **Skill Execution**: Each agent has a set of skills (functions) that can be executed:
   ```python
   result = await agent.execute_skill("skillName", {"param": "value"}, context)
   ```

3. **Context Sharing**: Agents share context through `AgentContext` which includes user info, conversation history, and session data.

4. **Response Format**: All agents return standardized `AgentResponse` objects with data, metadata, and optional error information.

---

## Tech Stack

### Frontend
- **Docusaurus 3.x** - React-based static site generator
- **TypeScript** - Type-safe development
- **KaTeX** - Mathematical equation rendering
- **CSS3** - Neon glassmorphism theme with animations
- **Local Search Plugin** - Full-text search

### Backend
- **FastAPI** - High-performance Python web framework
- **Google Gemini** - LLM for intelligent responses
- **Google text-embedding-004** - Text embeddings
- **Qdrant** - Vector database for semantic search
- **SQLite** - User authentication storage

---

## Project Structure

```
Hackathon/
├── frontend/                     # Docusaurus site
│   ├── docs/                     # Markdown content (6 chapters)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chatbot.tsx       # AI chatbot component
│   │   │   ├── ChapterActions.tsx # Personalize/Translate buttons
│   │   │   ├── Dashboard.tsx     # User progress dashboard
│   │   │   └── Auth/             # Authentication components
│   │   ├── css/
│   │   │   ├── neon-theme.css    # Global neon theme variables
│   │   │   ├── chatbot.css       # Chatbot styling
│   │   │   ├── dashboard.css     # Dashboard styling
│   │   │   ├── chapter-actions.css # Action buttons styling
│   │   │   └── custom.css        # Global overrides
│   │   ├── services/
│   │   │   └── api.ts            # Backend API client
│   │   ├── context/
│   │   │   └── AuthContext.tsx   # Authentication state
│   │   └── theme/                # Theme customization
│   ├── i18n/                     # Urdu translations
│   └── static/                   # Static assets
│
├── backend/                      # FastAPI server
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/           # API endpoints
│   │   │   └── deps.py           # Dependencies
│   │   ├── agents/               # Multi-agent system (8 agents)
│   │   ├── core/
│   │   │   ├── config.py         # Configuration
│   │   │   └── rate_limit.py     # Rate limiting
│   │   ├── models/               # Pydantic models
│   │   └── services/
│   │       ├── rag_service.py    # RAG implementation
│   │       └── auth_service.py   # Authentication
│   ├── scripts/
│   │   └── index_content.py      # Content indexing
│   └── history/                  # PHR records storage
│
├── specs/                        # Specification documents
├── history/                      # Prompt History Records
│   ├── prompts/                  # PHR storage
│   └── adr/                      # Architecture Decision Records
└── .specify/                     # SpecKit Plus templates
```

---

## UI Theme: Neon Futuristic Glassmorphism

The application features a striking neon futuristic theme with glassmorphism effects.

### Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Neon Cyan | `#00f5ff` | Primary actions, highlights |
| Neon Purple | `#bf00ff` | Secondary elements, gradients |
| Neon Green | `#39ff14` | Accent, translation, success |
| Neon Orange | `#ff6b35` | Warnings |
| Neon Red | `#ff0055` | Errors |
| Neon Mint | `#00ff88` | Success states |

### CSS Variables

```css
:root {
  --neon-primary: #00f5ff;
  --neon-secondary: #bf00ff;
  --neon-accent: #39ff14;
  --glass-bg: rgba(20, 20, 40, 0.6);
  --glass-blur: blur(20px);
  --glow-primary: 0 0 20px rgba(0, 245, 255, 0.5);
}
```

### Effects & Animations

- **Glassmorphism**: Translucent backgrounds with backdrop blur
- **Neon Glow**: Text and element shadows with color glow
- **Energy Waves**: Pulsing ring animations
- **Shimmer**: Hover sweep effects on buttons
- **Neural Pulse**: Background particle effects
- **Float Animation**: Subtle vertical movement

---

## API Endpoints

### Health & Status
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check |

### Chat & Search
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/chat` | POST | RAG-powered chat |
| `/api/v1/search` | POST | Content search |
| `/api/v1/personalize` | POST | Personalize content |
| `/api/v1/translate` | POST | Translate to Urdu |

### Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | User registration |
| `/api/v1/auth/login` | POST | User login |
| `/api/v1/auth/logout` | POST | User logout |
| `/api/v1/auth/profile` | GET | Get user profile |

### Agent System
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/agents` | GET | List all agents |
| `/api/v1/agents/{name}/skills` | GET | Get agent skills |
| `/api/v1/agents/{name}/execute` | POST | Execute agent skill |

### Example Requests

#### Chat Request
```json
{
  "query": "What is Physical AI?",
  "language": "en",
  "history": []
}
```

#### Chat Response
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

#### Agent Skill Execution
```json
{
  "skill": "personalizeContent",
  "params": {
    "content": "Chapter content here...",
    "user_level": "beginner"
  }
}
```

---

## Content Chapters

1. **Introduction to Physical AI** - Overview and motivation
2. **Foundations of Humanoid Robotics** - Kinematics, dynamics, control
3. **Sensors and Perception** - Vision, touch, sensor fusion
4. **Actuators and Movement** - Motors, transmission, control
5. **AI Integration** - ML, RL, learning methods
6. **Applications and Future** - Real-world use cases

---

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
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm start

# Build for production
npm run build
```

### Environment Variables

Create `backend/.env`:

```env
GOOGLE_API_KEY=your-google-ai-api-key
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key
SECRET_KEY=your-jwt-secret-key
```

---

## User Features

### Authentication
- Email/password registration
- Secure session management with JWT
- Profile customization

### Dashboard
- **Overview Tab**: Learning progress, chapters completed, time spent
- **Activity Tab**: Recent actions (reads, quizzes, translations)
- **Achievements Tab**: Unlockable badges and milestones

### Personalization
- Adaptive difficulty based on user level
- Content recommendations
- Learning path suggestions

### Translation
- Real-time English to Urdu translation
- Proper RTL (Right-to-Left) rendering
- Technical term preservation

---

## Development

### Adding Content

1. Add/edit Markdown files in `frontend/docs/`
2. Re-run `python scripts/index_content.py` to update vectors

### Adding a New Agent

1. Create `backend/app/agents/new_agent.py`:
   ```python
   from .base import BaseAgent, Skill

   class NewAgent(BaseAgent):
       @property
       def name(self) -> str:
           return "NewAgent"

       @property
       def description(self) -> str:
           return "Description of agent"

       def _register_skills(self) -> None:
           self.register_skill(Skill(
               name="skillName",
               description="What the skill does",
               handler=self._skill_handler,
               parameters={"param": "description"}
           ))

       async def _skill_handler(self, params, context):
           # Implementation
           return {"result": "data"}
   ```

2. Register in `registry.py`:
   ```python
   from .new_agent import NewAgent
   registry.register(NewAgent())
   ```

3. Export in `__init__.py`

### Rate Limiting

Chat endpoint is rate-limited to 5 requests/minute per IP.

---

## Deployment

### Frontend (Vercel)

```bash
cd frontend
npm run build
# Deploy `build/` directory or connect GitHub repo
```

### Backend (HuggingFace Spaces / Railway)

```bash
cd backend
# Deploy with Python 3.11+ runtime
# Set environment variables in dashboard
```

---

## File Reference

### Key Frontend Files

| File | Description |
|------|-------------|
| `src/components/Chatbot.tsx` | AI chatbot with neon UI |
| `src/components/Dashboard.tsx` | User progress dashboard |
| `src/components/ChapterActions.tsx` | Personalize/Translate buttons |
| `src/css/neon-theme.css` | Global neon theme variables |
| `src/css/chatbot.css` | Chatbot glassmorphism styles |
| `src/css/dashboard.css` | Dashboard neon styles |
| `src/context/AuthContext.tsx` | Authentication state management |
| `src/services/api.ts` | Backend API client |

### Key Backend Files

| File | Description |
|------|-------------|
| `app/main.py` | FastAPI application entry |
| `app/agents/base.py` | BaseAgent class and types |
| `app/agents/registry.py` | Agent registration singleton |
| `app/agents/router.py` | Intent-based query routing |
| `app/services/rag_service.py` | RAG implementation |
| `app/services/auth_service.py` | JWT authentication |

---

## License

MIT

---

## Acknowledgments

- Built with [Docusaurus](https://docusaurus.io/)
- Powered by [Google Gemini](https://ai.google.dev/)
- Vector search by [Qdrant](https://qdrant.tech/)
- Neon UI inspired by cyberpunk aesthetics
