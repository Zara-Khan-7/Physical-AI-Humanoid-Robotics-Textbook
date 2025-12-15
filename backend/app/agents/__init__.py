"""
Multi-Agent Architecture for Physical AI Textbook
================================================

This module provides a reusable multi-agent system with specialized agents
for content generation, code execution, RAG queries, personalization,
translation, authentication, history tracking, and UI theming.

Agents:
- ContentAgent: Generate chapter explanations, diagrams, quizzes, summaries
- CodeAgent: Produce runnable code samples and validate correctness
- RAGAgent: Answer user questions with citations from the vector database
- PersonalizationAgent: Modify content based on user background
- TranslationAgent: Translate English → Urdu with RTL formatting
- AuthAgent: Manage user authentication and profiles
- HistoryAgent: Manage Persistent History Records (PHR) for auditing
- UIAgent: Manage UI theming and visual consistency with neon aesthetics
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
from .history_agent import HistoryAgent
from .ui_agent import UIAgent

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
    "HistoryAgent",
    "UIAgent",
]
