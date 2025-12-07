<!-- Sync Impact Report -->
<!--
Version change: 0.0.0 -> 0.0.1 (PATCH: Initial creation of constitution)
Modified principles: None (initial creation)
Added sections: Scope and Constraints, Key Features and Success Criteria
Removed sections: None
Templates requiring updates:
- .specify/templates/plan-template.md: ✅ updated
- .specify/templates/spec-template.md: ✅ updated
- .specify/templates/tasks-template.md: ✅ updated
- .specify/templates/commands/*.md: ✅ updated
Follow-up TODOs:
- TODO(Success Criteria): User input for success criteria was incomplete ("Bu"). Need to confirm full success criteria.
-->
# Physical AI & Humanoid Robotics — Essentials Constitution

## Core Principles

### Simplicity
The book and its associated tools must be easy to understand and use, focusing on clear, direct explanations and intuitive interfaces.

### Accuracy
All technical information, code examples, and explanations must be precise, up-to-date, and thoroughly verified to ensure correctness.

### Minimalism
Prioritize essential content and features, avoiding unnecessary complexity or bloat to maintain a lightweight and focused learning experience.

### Fast Builds
The Docusaurus site should have optimized build times to ensure quick deployments and updates.

### Free-tier Architecture
The entire system, including the RAG chatbot, must be designed to operate within the limits of free-tier services (e.g., Qdrant, Neon, FastAPI) to minimize costs.

### RAG Answers Only from Book Text
The RAG chatbot must strictly use the book's content as its sole source for generating answers, preventing hallucination and ensuring content relevance.

## Scope and Constraints

### In Scope:
- 6 short chapters: Introduction to Physical AI, Basics of Humanoid Robotics, ROS 2 Fundamentals, Digital Twin Simulation (Gazebo + Isaac), Vision-Language-Action Systems, Capstone: Simple AI-Robot Pipeline
- Clean UI for Docusaurus textbook
- Free-tier friendly design
- Lightweight embeddings
- Docusaurus textbook with RAG chatbot (Qdrant + Neon + FastAPI)
- Select-text → Ask AI feature
- Optional Urdu / Personalize features

### Out of Scope:
- None explicitly mentioned, but implied by focus on "Essentials".

### External Dependencies:
- Qdrant (vector database)
- Neon (PostgreSQL)
- FastAPI (API framework)

### Constraints:
- No heavy GPU usage
- Minimal embeddings

## Key Features and Success Criteria

### Key Features:
- Docusaurus textbook
- RAG chatbot (Qdrant + Neon + FastAPI)
- Select-text → Ask AI
- Optional Urdu / Personalize features

### Success Criteria:
- Successful deployment of the Docusaurus site with all 6 chapters.
- Full integration and functionality of the RAG chatbot using Qdrant, Neon, and FastAPI.
- The "Select-text → Ask AI" feature works as expected.
- All core principles and constraints are met (Simplicity, Accuracy, Minimalism, Fast Builds, Free-tier Architecture, RAG Answers Only from Book Text, No heavy GPU usage, Minimal embeddings).
- The "Bu" in the user's prompt is interpreted as "Build successfully" and is included in this broader success criteria.

## Governance

This constitution supersedes all other practices. Amendments require documentation, approval, and a migration plan. All PRs/reviews must verify compliance with these principles. Complexity must be justified.

**Version**: 0.0.1 | **Ratified**: 2025-12-07 | **Last Amended**: 2025-12-07
