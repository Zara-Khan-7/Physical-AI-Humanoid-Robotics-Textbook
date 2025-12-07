# Research: AI-Native Textbook with RAG Chatbot

**Feature**: 001-textbook-generation
**Date**: 2025-12-07
**Status**: Complete

---

## Research Summary

This document consolidates research findings for building the AI-native textbook platform with RAG chatbot capabilities.

---

## 1. Docusaurus Chatbot Integration

### Decision: Swizzle Footer Component (Wrap Mode)

**Rationale**:
- Non-invasive integration that maintains Docusaurus upgrade compatibility
- Chatbot loads after main content, ensuring fast initial page load
- Wrap mode preserves original Footer functionality while adding chatbot

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Eject Footer | Breaks upgrade path, requires manual merge on Docusaurus updates |
| Plugin-based | No official chatbot plugin, third-party options add dependencies |
| Navbar integration | Poor UX - chatbot competes with navigation elements |

**Implementation Pattern**:
```bash
npm run swizzle @docusaurus/theme-classic Footer -- --wrap
```
Creates `src/theme/Footer/index.tsx` wrapper for chatbot injection.

---

## 2. Content Chunking Strategy

### Decision: Markdown-Aware Chunking (Header-Based)

**Rationale**:
- Preserves document structure and semantic meaning
- Headers provide natural breakpoints for educational content
- Maintains context within each chunk for better RAG retrieval

**Parameters**:
- **Chunk size**: 512-1000 tokens
- **Overlap**: 10% (50-100 tokens)
- **Split points**: Markdown headers (`#`, `##`, `###`)
- **Metadata preserved**: Chapter, section, page path

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Fixed-size (character) | Breaks mid-sentence, loses semantic coherence |
| Sentence-based | Too granular for technical content, loses context |
| Paragraph-based | Inconsistent chunk sizes, some paragraphs too long |

---

## 3. Embedding Model Selection

### Decision: Google text-embedding-004 at 768 Dimensions

**Rationale**:
- Same provider as LLM (Gemini) - single API key, unified billing
- Matryoshka Representation Learning allows dimension reduction without retraining
- 768 dimensions = ~1M vectors in Qdrant free tier (vs 250K at 3072)

**Specifications**:
- Model: `models/text-embedding-004`
- Dimensions: 768 (configurable via `output_dimensionality`)
- Max input: 2,048 tokens
- Task types: `RETRIEVAL_QUERY` (questions), `RETRIEVAL_DOCUMENT` (content)

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| OpenAI text-embedding-3-small | Different provider, usage-based pricing |
| Cohere embed-v3 | Additional API dependency, free tier limits uncertain |
| Self-hosted sentence-transformers | Requires compute resources, operational complexity |

---

## 4. Vector Database Configuration

### Decision: Qdrant Cloud Free Tier

**Rationale**:
- 1GB free forever (no credit card required)
- Supports ~1M vectors at 768 dimensions
- Built-in filtering, multi-vector support
- Available on AWS/GCP/Azure

**Configuration**:
- Collection: `textbook_chunks`
- Distance metric: Cosine similarity
- Payload fields: `content`, `chapter`, `section`, `path`

**Limits**:
- 1GB storage
- Inactivity: suspended after 1 week unused, deleted after 4 weeks
- Recommendation: Ping endpoint weekly to maintain cluster

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Pinecone | Free tier more restrictive (100K vectors) |
| Weaviate Cloud | Requires credit card for sandbox |
| Self-hosted Qdrant | Operational overhead, hosting costs |

---

## 5. LLM for Response Generation

### Decision: Google Gemini (Free Tier)

**Rationale**:
- Generous free quota (up to 1,500 requests/day)
- High quality responses for educational content
- Same provider as embeddings - unified API management

**Configuration**:
- Model: `gemini-2.0-flash-001` (fast, cost-effective)
- Rate limit: 15 requests/minute (free tier)
- Max context: 1M tokens (more than sufficient)

**System Prompt Strategy**:
```
You are a helpful tutor for the Physical AI and Humanoid Robotics textbook.
Answer questions ONLY using the provided context from the textbook.
Always cite the source section for each fact.
If the answer is not in the context, say "I don't have information about that in the textbook."
```

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| OpenAI GPT-4 | Higher cost, no free tier |
| Groq (Llama) | Less consistent quality for educational content |
| Claude | Usage-based pricing, no free tier |

---

## 6. Conversation Context Management

### Decision: Browser localStorage Only

**Rationale**:
- No server-side storage needed - simpler architecture
- Privacy-friendly - data stays on user's device
- Aligns with "no authentication" constraint
- Sufficient for session-based conversations

**Implementation**:
- Key: `textbook_chat_history`
- Format: JSON array of `{role, content, timestamp}`
- Limit: Last 10 exchanges (prevent context overflow)
- Clear: On browser close or explicit reset

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Neon PostgreSQL | Adds server complexity, requires user identification |
| Redis | Additional service to manage, overkill for session data |
| IndexedDB | More complex API, no benefit over localStorage for this use case |

---

## 7. Rate Limiting Strategy

### Decision: SlowAPI with Per-IP Limits

**Rationale**:
- Protects backend from abuse
- Matches Gemini free tier limits (15 RPM)
- Simple to implement with FastAPI

**Configuration**:
- Chat endpoint: 5 requests/minute per IP
- Search endpoint: 20 requests/minute per IP
- Global: 100 requests/minute total

**Fallback Behavior**:
- HTTP 429 with `Retry-After` header
- Frontend shows friendly message with countdown

---

## 8. Neon PostgreSQL Assessment

### Decision: NOT Required for MVP

**Rationale**:
- Original spec mentioned Neon, but localStorage handles all user data needs
- Neon free tier (0.5GB) would only add complexity without benefit
- Can add later if cross-device sync or analytics needed

**When to Add**:
- User authentication implemented
- Analytics/telemetry requirements
- Cross-device progress sync requested

---

## 9. Urdu Translation Approach

### Decision: Docusaurus i18n Plugin

**Rationale**:
- Built-in Docusaurus feature - no additional dependencies
- Supports RTL layout out of the box
- Translations stored alongside English content

**Configuration**:
- Default locale: `en`
- Additional locale: `ur`
- Translation directory: `i18n/ur/docusaurus-plugin-content-docs/`

**Chatbot Urdu Support**:
- Gemini natively supports Urdu
- Detect language from user input
- Respond in same language as query

---

## 10. Select-Text → Ask AI Feature

### Decision: Custom React Hook with Selection API

**Rationale**:
- Native browser Selection API - no dependencies
- Floating button appears on text selection
- Sends selected text as context to chatbot

**Implementation**:
- `useTextSelection` hook monitors selection events
- Floating button positioned near selection
- Click opens chatbot with pre-filled context

---

## Unresolved Items

None - all NEEDS CLARIFICATION items resolved through research and clarification session.

---

## References

- [Docusaurus Swizzling Documentation](https://docusaurus.io/docs/swizzling)
- [Google Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [Google Text Embeddings Guide](https://ai.google.dev/gemini-api/docs/embeddings)
- [Qdrant Cloud Pricing](https://qdrant.tech/pricing/)
- [FastAPI CORS Documentation](https://fastapi.tiangolo.com/tutorial/cors/)
- [SlowAPI Rate Limiting](https://slowapi.readthedocs.io/)
