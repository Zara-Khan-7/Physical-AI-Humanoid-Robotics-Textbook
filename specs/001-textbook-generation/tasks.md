# Tasks: AI-Native Textbook with RAG Chatbot

**Input**: Design documents from `/specs/001-textbook-generation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Tests**: Not explicitly requested in spec - test tasks NOT included (can be added via `/sp.checklist` if needed)

**Organization**: Tasks grouped by user story for independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1, US2, US3, US4, US5)
- File paths relative to repository root

## User Story Mapping

| Story | Priority | Title | Independent Test |
|-------|----------|-------|------------------|
| US1 | P1 | Browse and Read Textbook Content | Navigate chapters, verify formatting |
| US2 | P1 | Ask Questions via RAG Chatbot | Ask question, verify cited response |
| US3 | P2 | Search Textbook Content | Search term, verify results |
| US4 | P3 | Read Content in Urdu | Switch language, verify RTL |
| US5 | P3 | Personalized Learning Experience | Track progress, verify recommendations |

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for both frontend and backend

- [x] T001 Create root project structure with backend/ and frontend/ directories
- [x] T002 [P] Initialize Python 3.11+ backend with FastAPI in backend/
- [x] T003 [P] Initialize Docusaurus 3.x frontend with TypeScript in frontend/
- [x] T004 [P] Create backend/requirements.txt with FastAPI, google-generativeai, qdrant-client, pydantic, slowapi, python-dotenv, uvicorn
- [x] T005 [P] Create frontend/package.json with Docusaurus dependencies and @docusaurus/plugin-search-local
- [x] T006 [P] Configure backend/.env.example with GOOGLE_API_KEY, QDRANT_URL, QDRANT_API_KEY placeholders
- [x] T007 [P] Configure frontend/docusaurus.config.ts with site metadata and auto-sidebar
- [x] T008 [P] Setup backend linting with ruff in pyproject.toml
- [x] T009 [P] Setup frontend linting with ESLint in frontend/.eslintrc.js
- [x] T010 Create frontend/sidebars.ts with auto-generated sidebar configuration

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can begin

**CRITICAL**: No user story work can begin until this phase is complete

### Backend Core

- [ ] T011 Create backend/app/core/config.py with Settings class using pydantic-settings
- [ ] T012 [P] Create backend/app/models/requests.py with ChatRequest, SearchRequest Pydantic models (from OpenAPI spec)
- [ ] T013 [P] Create backend/app/models/responses.py with ChatResponse, SearchResponse, Citation, ErrorResponse models
- [ ] T014 Create backend/app/main.py with FastAPI app initialization, CORS middleware for frontend origins
- [ ] T015 Create backend/app/core/rate_limiter.py with SlowAPI configuration (5 req/min for /chat)
- [ ] T016 Create backend/app/api/routes/health.py with GET /api/v1/health endpoint
- [ ] T017 Create backend/app/api/dependencies.py with shared dependency injection setup

### Backend Services (RAG Pipeline)

- [ ] T018 Create backend/app/services/embeddings.py with EmbeddingService class for Google text-embedding-004
- [ ] T019 Create backend/app/services/vector_store.py with VectorStoreService class for Qdrant operations
- [ ] T020 Create backend/app/services/llm.py with LLMService class for Google Gemini response generation
- [ ] T021 Create backend/app/services/chunker.py with MarkdownChunker class (header-based, 512-1000 tokens)

### Content Indexing

- [ ] T022 Create backend/scripts/index_content.py script to chunk and embed Markdown files into Qdrant

### Frontend Core

- [ ] T023 Create frontend/src/services/api.ts with API client for backend endpoints (chat, search, health)
- [ ] T024 Create frontend/src/css/chatbot.css with chatbot component styles

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - Browse and Read Textbook Content (Priority: P1)

**Goal**: Learners can navigate and read the 6-chapter textbook with proper formatting, code highlighting, and sidebar navigation

**Independent Test**: Navigate to any chapter via sidebar, verify content renders with syntax highlighting and table of contents

### Content Creation

- [ ] T025 [P] [US1] Create frontend/docs/01-introduction/_category_.json with chapter metadata
- [ ] T026 [P] [US1] Create frontend/docs/01-introduction/index.md with chapter overview and placeholder content
- [ ] T027 [P] [US1] Create frontend/docs/02-humanoid-robotics/_category_.json and index.md
- [ ] T028 [P] [US1] Create frontend/docs/03-ros2-fundamentals/_category_.json and index.md
- [ ] T029 [P] [US1] Create frontend/docs/04-digital-twin/_category_.json and index.md
- [ ] T030 [P] [US1] Create frontend/docs/05-vision-language-action/_category_.json and index.md
- [ ] T031 [P] [US1] Create frontend/docs/06-capstone/_category_.json and index.md

### Frontend Configuration

- [ ] T032 [US1] Configure frontend/docusaurus.config.ts with prism syntax highlighting for Python, TypeScript, YAML, bash
- [ ] T033 [US1] Configure frontend/docusaurus.config.ts with math/KaTeX plugin for LaTeX notation
- [ ] T034 [US1] Add responsive CSS overrides in frontend/src/css/custom.css for mobile/desktop

### Verification

- [ ] T035 [US1] Run frontend dev server and verify all 6 chapters appear in sidebar
- [ ] T036 [US1] Verify code blocks render with syntax highlighting and copy button
- [ ] T037 [US1] Verify table of contents appears on chapter pages

**Checkpoint**: User Story 1 complete - textbook is browsable and readable

---

## Phase 4: User Story 2 - Ask Questions via RAG Chatbot (Priority: P1)

**Goal**: Learners can ask questions and receive accurate, cited answers from the textbook content within 5 seconds

**Independent Test**: Ask "What is ROS 2?" and verify response includes citation linking to Chapter 3

### Backend RAG Endpoint

- [ ] T038 [US2] Create backend/app/api/routes/chat.py with POST /api/v1/chat endpoint
- [ ] T039 [US2] Implement RAG pipeline in chat route: embed query → search Qdrant → generate with Gemini → return citations
- [ ] T040 [US2] Add system prompt in backend/app/services/llm.py restricting answers to book content only
- [ ] T041 [US2] Add conversation context handling (last 10 messages from history parameter)
- [ ] T042 [US2] Add error handling for Gemini rate limits with 429 response and Retry-After header

### Content Indexing

- [ ] T043 [US2] Run backend/scripts/index_content.py to index all chapter content into Qdrant
- [ ] T044 [US2] Verify Qdrant collection has vectors with correct metadata (chapter_id, section_id, path)

### Frontend Chatbot Components

- [ ] T045 [P] [US2] Create frontend/src/components/ChatBot/ChatBot.tsx main container component
- [ ] T046 [P] [US2] Create frontend/src/components/ChatBot/ChatInput.tsx input field with send button
- [ ] T047 [P] [US2] Create frontend/src/components/ChatBot/ChatMessage.tsx message bubble component
- [ ] T048 [P] [US2] Create frontend/src/components/ChatBot/Citation.tsx clickable citation link component
- [ ] T049 [US2] Create frontend/src/hooks/useChat.ts hook for chat state and localStorage persistence
- [ ] T050 [US2] Swizzle Footer: run `npm run swizzle @docusaurus/theme-classic Footer -- --wrap`
- [ ] T051 [US2] Implement frontend/src/theme/Footer/index.tsx to inject ChatBot component

### Integration

- [ ] T052 [US2] Connect ChatBot to backend /api/v1/chat endpoint via api.ts
- [ ] T053 [US2] Implement citation click handler to navigate to source section
- [ ] T054 [US2] Add loading state and error handling UI in ChatBot component
- [ ] T055 [US2] Add "I can't answer that" response handling for out-of-scope queries

### Verification

- [ ] T056 [US2] Test chatbot with sample questions from each chapter
- [ ] T057 [US2] Verify response time is under 5 seconds
- [ ] T058 [US2] Verify citations link to correct textbook sections

**Checkpoint**: User Story 2 complete - RAG chatbot is functional with citations

---

## Phase 5: User Story 3 - Search Textbook Content (Priority: P2)

**Goal**: Learners can search across all chapters and navigate to matching sections with highlighted results

**Independent Test**: Search "humanoid kinematics" and verify results appear with context snippets

### Backend Search Endpoint

- [ ] T059 [US3] Create backend/app/api/routes/search.py with GET /api/v1/search endpoint
- [ ] T060 [US3] Implement vector search with query embedding and Qdrant similarity search
- [ ] T061 [US3] Add chapter and language filter parameters to search endpoint
- [ ] T062 [US3] Format search results with highlighted snippets

### Frontend Search Integration

- [ ] T063 [US3] Configure @docusaurus/plugin-search-local in frontend/docusaurus.config.ts
- [ ] T064 [US3] Verify search modal opens with keyboard shortcut (/)
- [ ] T065 [US3] Test search result navigation to correct sections

**Checkpoint**: User Story 3 complete - search functionality works

---

## Phase 6: User Story 4 - Read Content in Urdu (Priority: P3)

**Goal**: Learners can switch to Urdu translation with proper RTL layout and Urdu chatbot responses

**Independent Test**: Switch to Urdu locale, verify content displays RTL, ask chatbot question in Urdu

### Docusaurus i18n Setup

- [ ] T066 [P] [US4] Configure i18n in frontend/docusaurus.config.ts with defaultLocale: 'en', locales: ['en', 'ur']
- [ ] T067 [P] [US4] Create frontend/i18n/ur/docusaurus-theme-classic/ with UI string translations
- [ ] T068 [US4] Create frontend/i18n/ur/docusaurus-plugin-content-docs/current/ directory structure
- [ ] T069 [US4] Add RTL CSS support in frontend/src/css/custom.css for [dir="rtl"] selectors
- [ ] T070 [US4] Add language switcher component to navbar in docusaurus.config.ts

### Urdu Content (Placeholder)

- [ ] T071 [US4] Create placeholder Urdu translations for Chapter 1 in frontend/i18n/ur/docusaurus-plugin-content-docs/current/01-introduction/

### Backend Urdu Support

- [ ] T072 [US4] Add language parameter to /api/v1/chat endpoint for Urdu responses
- [ ] T073 [US4] Update system prompt to respond in same language as query
- [ ] T074 [US4] Index Urdu content with language: 'ur' payload filter

### Verification

- [ ] T075 [US4] Test language switcher navigates to Urdu locale
- [ ] T076 [US4] Verify RTL layout renders correctly
- [ ] T077 [US4] Test Urdu chatbot interaction

**Checkpoint**: User Story 4 complete - Urdu translation works with RTL

---

## Phase 7: User Story 5 - Personalized Learning Experience (Priority: P3)

**Goal**: Returning learners see reading progress, continue where they left off, and receive recommendations

**Independent Test**: Read a chapter, refresh page, verify "Continue Learning" shows last position

### Progress Tracking Hook

- [ ] T078 [P] [US5] Create frontend/src/hooks/useProgress.ts hook for localStorage progress tracking
- [ ] T079 [US5] Implement section read detection (scroll + time on page threshold)
- [ ] T080 [US5] Store progress in localStorage with format from data-model.md (textbook_progress key)

### Progress UI Components

- [ ] T081 [P] [US5] Create frontend/src/components/ProgressBar/ProgressBar.tsx for chapter completion
- [ ] T082 [P] [US5] Create frontend/src/components/ContinueLearning/ContinueLearning.tsx for homepage
- [ ] T083 [US5] Add progress indicators to sidebar chapter items
- [ ] T084 [US5] Implement "Continue Learning" section on homepage showing last read position

### Recommendations (Basic)

- [ ] T085 [US5] Store chatbot question topics in localStorage
- [ ] T086 [US5] Create simple recommendation logic: suggest sections related to frequent chatbot topics
- [ ] T087 [US5] Display recommendations on homepage below "Continue Learning"

### Verification

- [ ] T088 [US5] Test progress persists across browser sessions
- [ ] T089 [US5] Test "Continue Learning" links to correct position
- [ ] T090 [US5] Test recommendations update based on chatbot usage

**Checkpoint**: User Story 5 complete - personalization features work

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple user stories, production readiness

### Select-Text → Ask AI Feature

- [ ] T091 [P] Create frontend/src/components/SelectTextAsk/SelectTextAsk.tsx with text selection detection
- [ ] T092 Implement floating "Ask AI" button on text selection
- [ ] T093 Connect selection to chatbot with pre-filled context

### Error Handling & Edge Cases

- [ ] T094 [P] Add graceful degradation when Qdrant is unavailable (show error, suggest search)
- [ ] T095 [P] Add graceful degradation when Gemini rate limit exceeded (show retry message)
- [ ] T096 Implement conversation history limit (10 exchanges) with "Start Fresh" button

### Production Configuration

- [ ] T097 [P] Create backend/Dockerfile for containerized deployment
- [ ] T098 [P] Update frontend/docusaurus.config.ts with production URL
- [ ] T099 Create .github/workflows/deploy.yml for CI/CD (optional)

### Documentation

- [ ] T100 Update README.md with setup instructions from quickstart.md
- [ ] T101 Verify all quickstart.md steps work end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ─────────────────────────────────────────────────┐
                                                                  │
Phase 2 (Foundational) ──────────────────────────────────────────┤
         │                                                        │
         ▼                                                        │
    ┌────┴────┐                                                   │
    │ GATE    │  All user stories BLOCKED until Phase 2 complete  │
    └────┬────┘                                                   │
         │                                                        │
         ├──────────────────────────────────────────────────────┐ │
         │                                                      │ │
    Phase 3 (US1: Content)                                      │ │
         │                                                      │ │
         ▼                                                      │ │
    Phase 4 (US2: Chatbot) ─ depends on indexed content ────────┤ │
         │                                                      │ │
         ▼                                                      │ │
    Phase 5 (US3: Search) ─ can run parallel with Phase 4 ──────┤ │
         │                                                      │ │
         ▼                                                      │ │
    Phase 6 (US4: Urdu) ─ can run parallel with Phase 4/5 ──────┤ │
         │                                                      │ │
         ▼                                                      │ │
    Phase 7 (US5: Progress) ─ can run parallel with above ──────┘ │
         │                                                        │
         ▼                                                        │
    Phase 8 (Polish) ─ depends on all user stories ───────────────┘
```

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|------------|-------------------|
| US1 (Content) | Phase 2 only | None (first) |
| US2 (Chatbot) | Phase 2 + US1 content indexed | US3, US4, US5 |
| US3 (Search) | Phase 2 + US1 content indexed | US2, US4, US5 |
| US4 (Urdu) | Phase 2 + US1 structure | US2, US3, US5 |
| US5 (Progress) | Phase 2 only | US2, US3, US4 |

### Within Each User Story

1. Backend routes/services before frontend components
2. Core implementation before integration
3. Verification tasks last

---

## Parallel Execution Examples

### Phase 1 Setup (Maximum Parallelism)

```
Parallel Group A:
  T002: Initialize Python backend
  T003: Initialize Docusaurus frontend

Parallel Group B (after A):
  T004: backend/requirements.txt
  T005: frontend/package.json
  T006: backend/.env.example
  T007: frontend/docusaurus.config.ts
  T008: backend pyproject.toml
  T009: frontend .eslintrc.js
```

### Phase 3 US1 Content (Parallel Chapter Creation)

```
Parallel Group:
  T025: Chapter 1 metadata
  T027: Chapter 2 metadata
  T028: Chapter 3 metadata
  T029: Chapter 4 metadata
  T030: Chapter 5 metadata
  T031: Chapter 6 metadata
```

### Phase 4 US2 Components (Parallel React Components)

```
Parallel Group:
  T045: ChatBot.tsx
  T046: ChatInput.tsx
  T047: ChatMessage.tsx
  T048: Citation.tsx
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: US1 (Content) → **Deliverable: Readable textbook**
4. Complete Phase 4: US2 (Chatbot) → **Deliverable: AI-native textbook MVP**
5. **STOP and VALIDATE**: Full MVP is functional

### Incremental Delivery

| Increment | User Stories | Deliverable |
|-----------|--------------|-------------|
| MVP | US1 + US2 | Textbook with RAG chatbot |
| +Search | US3 | Full-text search |
| +Urdu | US4 | Bilingual support |
| +Personal | US5 | Progress tracking |

### Suggested MVP Scope

**For a hackathon or initial deployment, complete only:**

- Phase 1: Setup (T001-T010)
- Phase 2: Foundational (T011-T024)
- Phase 3: US1 Content (T025-T037)
- Phase 4: US2 Chatbot (T038-T058)

**Total MVP tasks**: 58 tasks
**Post-MVP**: 43 tasks (US3, US4, US5, Polish)

---

## Summary

| Phase | Tasks | Parallel Opportunities |
|-------|-------|------------------------|
| Phase 1: Setup | 10 | 8 tasks parallelizable |
| Phase 2: Foundational | 14 | 5 tasks parallelizable |
| Phase 3: US1 Content | 13 | 7 tasks parallelizable |
| Phase 4: US2 Chatbot | 21 | 4 tasks parallelizable |
| Phase 5: US3 Search | 7 | 0 tasks parallelizable |
| Phase 6: US4 Urdu | 12 | 3 tasks parallelizable |
| Phase 7: US5 Progress | 13 | 3 tasks parallelizable |
| Phase 8: Polish | 11 | 4 tasks parallelizable |
| **Total** | **101** | **34 parallel opportunities** |

---

## Notes

- [P] tasks can run in parallel (different files, no dependencies)
- [Story] label maps task to specific user story
- Each user story is independently testable after completion
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
