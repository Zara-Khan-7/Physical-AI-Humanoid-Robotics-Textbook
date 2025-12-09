---
title: Physical AI Textbook API
emoji: 📚
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# Physical AI Textbook - RAG Chatbot API

FastAPI backend for the AI-native Physics textbook with RAG-powered chatbot.

## Features
- RAG pipeline with Qdrant vector database
- Google Gemini LLM for response generation
- Physics-focused educational content

## API Endpoints
- `GET /` - Health check
- `GET /health` - Detailed health status
- `POST /api/chat` - Chat with the AI tutor
