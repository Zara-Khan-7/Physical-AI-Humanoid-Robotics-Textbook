"""
Multi-Agent Architecture for Physical AI Textbook
================================================

This module provides a reusable multi-agent system with specialized agents
for content generation, code execution, RAG queries, personalization,
translation, and authentication.

Agents:
- ContentAgent: Generate chapter explanations, diagrams, quizzes, summaries
- CodeAgent: Produce runnable code samples and validate correctness
- RAGAgent: Answer user questions with citations from the vector database
- PersonalizationAgent: Modify content based on user background
- TranslationAgent: Translate English → Urdu with RTL formatting
- AuthAgent: Manage user authentication and profiles
"""

from .base import BaseAgent, AgentContext, AgentResponse, Skill
from .registry import AgentRegistry
from .router import AgentRouter
from .content_agent import ContentAgent
from .code_agent import CodeAgent
from .rag_agent import RAGAgent
from .personalization_agent import PersonalizationAgent
from .translation_agent import TranslationAgent
from .auth_agent import AuthAgent

__all__ = [
    "BaseAgent",
    "AgentContext",
    "AgentResponse",
    "Skill",
    "AgentRegistry",
    "AgentRouter",
    "ContentAgent",
    "CodeAgent",
    "RAGAgent",
    "PersonalizationAgent",
    "TranslationAgent",
    "AuthAgent",
]
