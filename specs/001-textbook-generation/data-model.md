# Data Model: AI-Native Textbook with RAG Chatbot

**Feature**: 001-textbook-generation
**Date**: 2025-12-07

---

## Overview

This document defines the data entities, their attributes, relationships, and storage locations for the textbook platform.

---

## Storage Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Storage Layers                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────┐    ┌────────────────────────────┐   │
│  │  Qdrant Cloud      │    │  Browser localStorage      │   │
│  │  (Vector DB)       │    │  (Client-side)             │   │
│  ├────────────────────┤    ├────────────────────────────┤   │
│  │ • ContentChunk     │    │ • ChatHistory              │   │
│  │ • Vector embeddings│    │ • UserProgress             │   │
│  │ • Metadata         │    │ • UserPreferences          │   │
│  └────────────────────┘    └────────────────────────────┘   │
│                                                              │
│  ┌────────────────────┐    ┌────────────────────────────┐   │
│  │  Filesystem        │    │  Runtime (Memory)          │   │
│  │  (Static Content)  │    │  (Server-side)             │   │
│  ├────────────────────┤    ├────────────────────────────┤   │
│  │ • Markdown docs    │    │ • Active sessions          │   │
│  │ • Images/assets    │    │ • Rate limit counters      │   │
│  │ • Translations     │    │ • API client instances     │   │
│  └────────────────────┘    └────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Entities

### 1. ContentChunk (Qdrant)

Vector database entity storing embedded textbook content for RAG retrieval.

```typescript
interface ContentChunk {
  // Qdrant point ID (auto-generated UUID)
  id: string;

  // Vector embedding (768 dimensions)
  vector: number[];

  // Payload (searchable metadata)
  payload: {
    content: string;        // Raw text content (512-1000 tokens)
    chapter_id: string;     // e.g., "01-introduction"
    chapter_title: string;  // e.g., "Introduction to Physical AI"
    section_id: string;     // e.g., "what-is-physical-ai"
    section_title: string;  // e.g., "What is Physical AI?"
    path: string;           // URL path: "/docs/01-introduction/what-is-physical-ai"
    chunk_index: number;    // Position within section (0, 1, 2...)
    language: "en" | "ur";  // Content language
    created_at: string;     // ISO timestamp
  };
}
```

**Qdrant Collection Configuration**:
```json
{
  "collection_name": "textbook_chunks",
  "vectors": {
    "size": 768,
    "distance": "Cosine"
  },
  "payload_schema": {
    "chapter_id": "keyword",
    "section_id": "keyword",
    "language": "keyword",
    "content": "text"
  }
}
```

**Indexes**:
- Vector index: HNSW (default)
- Payload indexes: `chapter_id`, `section_id`, `language`

---

### 2. ChatMessage (localStorage)

Client-side entity for conversation history.

```typescript
interface ChatMessage {
  id: string;           // UUID v4
  role: "user" | "assistant";
  content: string;      // Message text
  citations?: Citation[];  // For assistant messages
  timestamp: string;    // ISO timestamp
}

interface Citation {
  chapter_title: string;
  section_title: string;
  path: string;         // Link to source
  snippet: string;      // Relevant quote (first 200 chars)
  score: number;        // Relevance score (0-1)
}
```

**localStorage Key**: `textbook_chat_history`

**Storage Format**:
```json
{
  "session_id": "uuid-v4",
  "messages": [
    {
      "id": "msg-uuid",
      "role": "user",
      "content": "What is ROS 2?",
      "timestamp": "2025-12-07T10:30:00Z"
    },
    {
      "id": "msg-uuid-2",
      "role": "assistant",
      "content": "ROS 2 (Robot Operating System 2) is...",
      "citations": [...],
      "timestamp": "2025-12-07T10:30:02Z"
    }
  ],
  "created_at": "2025-12-07T10:30:00Z",
  "updated_at": "2025-12-07T10:30:02Z"
}
```

**Constraints**:
- Max messages: 20 (last 10 exchanges)
- Max message length: 10,000 characters
- Auto-prune: Remove oldest when limit exceeded

---

### 3. UserProgress (localStorage)

Client-side entity tracking reading progress.

```typescript
interface UserProgress {
  chapters: {
    [chapterId: string]: ChapterProgress;
  };
  last_read: {
    path: string;
    timestamp: string;
  };
  total_completion: number;  // 0-100 percentage
}

interface ChapterProgress {
  chapter_id: string;
  chapter_title: string;
  sections_read: string[];   // Array of section IDs
  total_sections: number;
  completion: number;        // 0-100 percentage
  last_accessed: string;     // ISO timestamp
}
```

**localStorage Key**: `textbook_progress`

**Storage Format**:
```json
{
  "chapters": {
    "01-introduction": {
      "chapter_id": "01-introduction",
      "chapter_title": "Introduction to Physical AI",
      "sections_read": ["what-is-physical-ai", "history"],
      "total_sections": 5,
      "completion": 40,
      "last_accessed": "2025-12-07T10:00:00Z"
    }
  },
  "last_read": {
    "path": "/docs/01-introduction/history",
    "timestamp": "2025-12-07T10:00:00Z"
  },
  "total_completion": 15
}
```

---

### 4. UserPreferences (localStorage)

Client-side entity for user settings.

```typescript
interface UserPreferences {
  theme: "light" | "dark" | "system";
  language: "en" | "ur";
  chatbot_position: "right" | "left";
  chatbot_minimized: boolean;
  font_size: "small" | "medium" | "large";
}
```

**localStorage Key**: `textbook_preferences`

**Default Values**:
```json
{
  "theme": "system",
  "language": "en",
  "chatbot_position": "right",
  "chatbot_minimized": false,
  "font_size": "medium"
}
```

---

### 5. Chapter (Filesystem - Markdown)

Static content entity stored as Markdown files.

```typescript
interface Chapter {
  id: string;           // Directory name: "01-introduction"
  title: string;        // From frontmatter
  order: number;        // Numeric prefix
  description: string;  // From frontmatter
  sections: Section[];
}

interface Section {
  id: string;           // File name (without .md)
  title: string;        // From frontmatter or first H1
  path: string;         // Full URL path
  content: string;      // Markdown content
}
```

**File Structure**:
```
docs/
├── 01-introduction/
│   ├── _category_.json    # Chapter metadata
│   ├── index.md           # Chapter overview
│   ├── what-is-physical-ai.md
│   └── history.md
├── 02-humanoid-robotics/
│   └── ...
```

**Frontmatter Schema**:
```yaml
---
id: what-is-physical-ai
title: What is Physical AI?
sidebar_position: 1
description: Understanding embodied AI systems
---
```

---

## Relationships

```
┌─────────────────┐
│    Chapter      │
│  (Filesystem)   │
└────────┬────────┘
         │ 1:N
         ▼
┌─────────────────┐
│    Section      │
│  (Filesystem)   │
└────────┬────────┘
         │ 1:N (chunked)
         ▼
┌─────────────────┐
│  ContentChunk   │
│   (Qdrant)      │
└────────┬────────┘
         │ N:M (search results)
         ▼
┌─────────────────┐
│  ChatMessage    │
│ (localStorage)  │◄──── Citations reference ContentChunks
└─────────────────┘
```

---

## Data Flow

### Content Indexing (Build Time)

```
Markdown Files → Parse → Chunk → Embed → Store in Qdrant
     │              │        │        │           │
     │              │        │        │           └── Vector + metadata
     │              │        │        └── Google text-embedding-004
     │              │        └── 512-1000 tokens per chunk
     │              └── Extract frontmatter + content
     └── docs/**/*.md
```

### Query Processing (Runtime)

```
User Question → Embed → Search Qdrant → Retrieve Chunks → Generate Response
      │            │           │              │                  │
      │            │           │              │                  └── Gemini + context
      │            │           │              └── Top 5 by similarity
      │            │           └── Cosine similarity search
      │            └── Google text-embedding-004 (RETRIEVAL_QUERY)
      └── Chat input
```

---

## Validation Rules

### ContentChunk
- `content`: Required, 100-5000 characters
- `chapter_id`: Required, matches directory name pattern
- `path`: Required, valid URL path starting with `/docs/`
- `language`: Required, one of `["en", "ur"]`

### ChatMessage
- `content`: Required, 1-10000 characters
- `role`: Required, one of `["user", "assistant"]`
- `citations`: Optional for user, required for assistant

### UserProgress
- `completion`: Integer 0-100
- `sections_read`: Array of valid section IDs

---

## Migration Considerations

### Adding New Chapters
1. Add Markdown files to `docs/` directory
2. Run indexing script to generate chunks and embeddings
3. Upsert new vectors to Qdrant (idempotent by chunk ID)

### Updating Content
1. Modify Markdown files
2. Re-run indexing for affected chapters
3. Delete old chunks, insert new (by chapter_id filter)

### Adding Languages
1. Add translations to `i18n/{locale}/docusaurus-plugin-content-docs/`
2. Run indexing with `language` parameter
3. Store as separate vectors with language payload filter
