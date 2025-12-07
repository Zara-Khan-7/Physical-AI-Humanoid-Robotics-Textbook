# Implementation Plan: AI-Native Textbook with RAG Chatbot

**Branch**: `001-textbook-generation` | **Date**: 2025-12-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-textbook-generation/spec.md`

---

## Summary

Build an educational platform delivering a 6-chapter textbook on Physical AI and Humanoid Robotics with an integrated RAG chatbot. The frontend uses Docusaurus v3 with auto-sidebar and a swizzled chatbot component. The backend uses FastAPI to orchestrate RAG queries through Google text-embedding-004 (768 dimensions) for embeddings, Qdrant Cloud for vector storage, Google Gemini for response generation, and Neon PostgreSQL for conversation metadata. User personalization uses browser localStorage (no authentication).

---

## Technical Context

**Language/Version**: TypeScript 5.x (frontend), Python 3.11+ (backend)
**Primary Dependencies**:
- Frontend: Docusaurus 3.x, React 18, @docusaurus/plugin-search-local
- Backend: FastAPI, google-generativeai, qdrant-client, asyncpg, pydantic

**Storage**:
- Vector DB: Qdrant Cloud (free tier - 1GB, ~1M vectors at 768-dim)
- Relational DB: Neon PostgreSQL (free tier - 0.5GB, conversation metadata only)
- Client-side: localStorage (reading progress, preferences)

**Testing**: Vitest (frontend), pytest + pytest-asyncio (backend)
**Target Platform**: Web (static Docusaurus site + FastAPI server)
**Project Type**: Web application (frontend + backend)
**Performance Goals**:
- Page load: <3 seconds
- Chatbot response: <5 seconds (p95)
- Search results: <2 seconds

**Constraints**:
- Free-tier API limits: Gemini 15 RPM, embeddings 1500 RPM
- Qdrant free: 1GB storage
- Neon free: 0.5GB storage
- No heavy GPU usage

**Scale/Scope**: 100 concurrent users, 6 chapters (~50-100 sections)

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| Simplicity | ✅ PASS | Two-tier architecture (Docusaurus + FastAPI), minimal services |
| Accuracy | ✅ PASS | RAG grounded in book content only, citations required |
| Minimalism | ✅ PASS | Only essential features for MVP, localStorage over auth system |
| Fast Builds | ✅ PASS | Docusaurus static build, no heavy preprocessing |
| Free-tier Architecture | ✅ PASS | Qdrant Cloud, Neon, Google Gemini all free tier |
| RAG Answers Only from Book | ✅ PASS | System prompt enforces book-only context, citations trace sources |

**Gate Status**: ✅ PASSED - All constitution principles satisfied.

---

## Project Structure

### Documentation (this feature)

```text
specs/001-textbook-generation/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (API specs)
│   └── openapi.yaml
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
# Web application structure

backend/
├── app/
│   ├── main.py              # FastAPI app, CORS, middleware
│   ├── api/
│   │   ├── routes/
│   │   │   ├── chat.py      # POST /chat endpoint
│   │   │   ├── search.py    # GET /search endpoint
│   │   │   └── health.py    # Health check
│   │   └── dependencies.py  # Shared dependencies
│   ├── services/
│   │   ├── embeddings.py    # Google text-embedding integration
│   │   ├── vector_store.py  # Qdrant operations
│   │   ├── llm.py           # Gemini response generation
│   │   └── chunker.py       # Markdown chunking for indexing
│   ├── models/
│   │   ├── requests.py      # Pydantic request schemas
│   │   └── responses.py     # Pydantic response schemas
│   └── core/
│       ├── config.py        # Settings from environment
│       └── rate_limiter.py  # SlowAPI rate limiting
├── scripts/
│   └── index_content.py     # One-time content indexing script
├── tests/
│   ├── unit/
│   └── integration/
├── requirements.txt
└── .env.example

frontend/
├── docusaurus.config.ts     # Docusaurus configuration
├── sidebars.ts              # Auto-generated sidebar config
├── src/
│   ├── components/
│   │   ├── ChatBot/
│   │   │   ├── ChatBot.tsx      # Main chatbot component
│   │   │   ├── ChatMessage.tsx  # Message bubble component
│   │   │   ├── ChatInput.tsx    # Input field component
│   │   │   └── Citation.tsx     # Citation link component
│   │   └── SelectTextAsk/
│   │       └── SelectTextAsk.tsx # Select-text → Ask AI feature
│   ├── theme/
│   │   └── Footer/
│   │       └── index.tsx    # Swizzled footer (chatbot injection)
│   ├── hooks/
│   │   ├── useChat.ts       # Chat state management
│   │   └── useProgress.ts   # Reading progress (localStorage)
│   ├── services/
│   │   └── api.ts           # Backend API client
│   └── css/
│       └── chatbot.css      # Chatbot styles
├── docs/
│   ├── 01-introduction/
│   │   └── index.md
│   ├── 02-humanoid-robotics/
│   │   └── index.md
│   ├── 03-ros2-fundamentals/
│   │   └── index.md
│   ├── 04-digital-twin/
│   │   └── index.md
│   ├── 05-vision-language-action/
│   │   └── index.md
│   └── 06-capstone/
│       └── index.md
├── i18n/
│   └── ur/                  # Urdu translations (optional)
│       └── docusaurus-plugin-content-docs/
├── static/
│   └── img/
├── tests/
│   └── components/
├── package.json
└── tsconfig.json
```

**Structure Decision**: Web application with separate frontend (Docusaurus static site) and backend (FastAPI server). Frontend deployed as static files, backend as containerized service.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                             │
├─────────────────────────────────────────────────────────────────┤
│  Docusaurus Site (Static)                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Chapters    │  │   Search     │  │  ChatBot Component   │  │
│  │  (Markdown)  │  │  (Local)     │  │  (React + API)       │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                              │                    │              │
│                              │              localStorage         │
│                              │         (progress, history)       │
└──────────────────────────────┼────────────────────┼─────────────┘
                               │                    │
                               ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  /chat       │  │  /search     │  │  Rate Limiter        │  │
│  │  endpoint    │  │  endpoint    │  │  (SlowAPI)           │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────────────────┘  │
│         │                 │                                      │
│         ▼                 ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              RAG Pipeline                                │    │
│  │  1. Embed query (Google text-embedding-004)              │    │
│  │  2. Vector search (Qdrant)                               │    │
│  │  3. Generate response (Google Gemini)                    │    │
│  │  4. Return with citations                                │    │
│  └─────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
                    │                    │
                    ▼                    ▼
        ┌───────────────────┐  ┌───────────────────┐
        │   Qdrant Cloud    │  │  Google AI APIs   │
        │   (Vector DB)     │  │  - Gemini         │
        │   Free tier       │  │  - Embeddings     │
        └───────────────────┘  └───────────────────┘
```

---

## Key Technical Decisions

### 1. Embedding Strategy
- **Model**: Google text-embedding-004 with `output_dimensionality=768`
- **Rationale**: Balances quality and storage (1M vectors in free tier vs 250K at 3072-dim)
- **Chunking**: Markdown-aware splitting by headers, 512-1000 tokens with 10% overlap

### 2. Chatbot Integration
- **Method**: Swizzle Footer component (wrap mode)
- **Rationale**: Non-invasive, maintains upgrade compatibility, loads after main content

### 3. Search Implementation
- **Primary**: Docusaurus built-in search plugin (@docusaurus/plugin-search-local)
- **RAG Search**: Vector similarity via backend for chatbot context retrieval

### 4. Conversation Context
- **Storage**: Browser localStorage (session-scoped)
- **History Limit**: Last 10 exchanges for context window management
- **Rationale**: No server-side storage needed, simpler architecture, privacy-friendly

### 5. Rate Limiting
- **Strategy**: SlowAPI with 5 req/min per IP for /chat endpoint
- **Fallback**: Graceful degradation with "try again later" message

---

## Complexity Tracking

> No constitution violations requiring justification.

| Aspect | Complexity Level | Justification |
|--------|------------------|---------------|
| Authentication | None | localStorage-only per constitution |
| Database | Minimal | Qdrant for vectors only, no Neon needed for MVP |
| Deployment | Simple | Static frontend + single backend service |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Gemini rate limits exceeded | Rate limiting + queue with retry, clear error messaging |
| Qdrant free tier storage exceeded | Monitor usage, 768-dim embeddings maximize capacity |
| Chatbot hallucination | System prompt restricts to book content, citation required |
| Slow response times | Streaming responses, optimistic UI updates |

---

## Phase Outputs Checklist

- [x] Technical Context filled
- [x] Constitution Check passed
- [x] Project Structure defined
- [x] research.md (Phase 0)
- [x] data-model.md (Phase 1)
- [x] contracts/openapi.yaml (Phase 1)
- [x] quickstart.md (Phase 1)
