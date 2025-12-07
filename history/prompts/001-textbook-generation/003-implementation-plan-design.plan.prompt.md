---
id: 003
title: Implementation Plan for AI Textbook
stage: plan
date: 2025-12-07
surface: agent
model: claude-opus-4-5-20251101
feature: 001-textbook-generation
branch: 001-textbook-generation
user: hp
command: /sp.plan
labels: ["architecture", "rag", "docusaurus", "fastapi", "qdrant", "gemini"]
links:
  spec: specs/001-textbook-generation/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-textbook-generation/plan.md
  - specs/001-textbook-generation/research.md
  - specs/001-textbook-generation/data-model.md
  - specs/001-textbook-generation/contracts/openapi.yaml
  - specs/001-textbook-generation/quickstart.md
tests:
  - null
---

## Prompt

/sp.plan textbook-generation

## Response snapshot

Created comprehensive implementation plan for the AI-Native Textbook with RAG Chatbot:

**Architecture**:
- Frontend: Docusaurus 3.x with swizzled Footer for chatbot injection
- Backend: FastAPI with RAG pipeline (embed → search → generate)
- Vector DB: Qdrant Cloud (free tier, 768-dim embeddings)
- LLM: Google Gemini (free tier)
- Embeddings: Google text-embedding-004

**Phase 0 - Research** (research.md):
- 10 technical decisions documented with rationale
- All NEEDS CLARIFICATION items resolved
- Alternatives considered for each decision

**Phase 1 - Design** (data-model.md, contracts/):
- 5 entities defined: ContentChunk, ChatMessage, UserProgress, UserPreferences, Chapter
- Storage architecture: Qdrant (vectors), localStorage (user data), filesystem (content)
- OpenAPI 3.1 contract with 3 endpoints: /chat, /search, /health

**Constitution Check**: All 6 principles PASSED
- Simplicity, Accuracy, Minimalism, Fast Builds, Free-tier Architecture, RAG Answers Only

**Quickstart Guide**: Complete setup instructions for development and production deployment.

## Outcome

- Impact: Complete architectural blueprint enabling task generation
- Tests: N/A (planning phase)
- Files: 5 files created (plan.md, research.md, data-model.md, openapi.yaml, quickstart.md)
- Next prompts: `/sp.tasks` to generate implementation tasks
- Reflection: Single-provider strategy (Google) reduces complexity; localStorage eliminates need for Neon in MVP

## Evaluation notes (flywheel)

- Failure modes observed: None - all technical decisions resolved through research
- Graders run and results (PASS/FAIL): Constitution Check - 6/6 PASS
- Prompt variant (if applicable): Standard /sp.plan workflow
- Next experiment: None required - proceed to task generation
