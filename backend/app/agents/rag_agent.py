"""
RAG Agent
=========

Answers user questions with citations from the vector database.

Skills:
- ragQuery: Answer questions using RAG with citations
- searchChapters: Search for relevant chapters
- retrieveSections: Retrieve specific sections
"""

from typing import Any, Dict, List, Optional
import logging
from .base import BaseAgent, AgentContext, Skill

logger = logging.getLogger(__name__)


class RAGAgent(BaseAgent):
    """
    Agent specialized for Retrieval-Augmented Generation.

    This agent searches the vector database for relevant content
    and generates answers with citations from the textbook.
    """

    @property
    def name(self) -> str:
        return "RAGAgent"

    @property
    def description(self) -> str:
        return "Answers questions using RAG with citations from the Physical AI textbook vector database."

    def _register_skills(self) -> None:
        """Register RAG-related skills."""

        # Skill: RAG Query
        async def rag_query_handler(
            context: AgentContext,
            message: str,
            num_results: int = 5,
            chapter_filter: str = None,
            **kwargs
        ) -> Dict[str, Any]:
            """Answer questions using RAG with citations."""

            citations = []
            retrieved_context = ""

            # Search vector store if available
            if self.embedding_service and self.vector_store:
                try:
                    # Generate embedding for the query
                    query_embedding = await self.embedding_service.embed_query(message)

                    # Build filter if chapter specified
                    search_filter = None
                    if chapter_filter:
                        search_filter = {"chapter_id": chapter_filter}

                    # Search vector store
                    results = await self.vector_store.search(
                        query_vector=query_embedding,
                        limit=num_results,
                        filter_conditions=search_filter,
                    )

                    # Format context and citations
                    context_parts = []
                    for i, result in enumerate(results):
                        payload = result.payload
                        context_parts.append(f"[{i+1}] {payload.get('content', '')}")
                        citations.append({
                            "chapter_id": payload.get("chapter_id", ""),
                            "chapter_title": payload.get("chapter_title", ""),
                            "section_id": payload.get("section_id", ""),
                            "section_title": payload.get("section_title", ""),
                            "path": payload.get("path", ""),
                            "score": result.score,
                        })

                    retrieved_context = "\n\n".join(context_parts)

                except Exception as e:
                    logger.error(f"RAG search error: {e}")
                    retrieved_context = ""

            # Generate response with context
            if self.llm_service:
                system_prompt = """You are an AI assistant for the Physical AI and Humanoid Robotics textbook.
Answer questions based ONLY on the provided context from the textbook.
If the context doesn't contain relevant information, say so.
Always cite your sources using [1], [2], etc."""

                response = await self.llm_service.generate_response(
                    query=message,
                    context=retrieved_context,
                    history=context.conversation_history,
                    language=context.language,
                )

                return {
                    "answer": response,
                    "citations": citations,
                    "query": message,
                    "num_results": len(citations),
                    "language": context.language,
                }

            return {
                "answer": "RAG service not fully available",
                "citations": citations,
                "query": message,
            }

        self.register_skill(Skill(
            name="ragQuery",
            description="Answer questions using RAG with citations from the textbook",
            handler=rag_query_handler,
            output_type="dict",
        ))

        # Skill: Search Chapters
        async def search_chapters_handler(
            context: AgentContext,
            query: str,
            limit: int = 10,
            **kwargs
        ) -> Dict[str, Any]:
            """Search for relevant chapters."""

            results = []

            if self.embedding_service and self.vector_store:
                try:
                    query_embedding = await self.embedding_service.embed_query(query)

                    search_results = await self.vector_store.search(
                        query_vector=query_embedding,
                        limit=limit,
                    )

                    # Group by chapter
                    chapters_seen = set()
                    for result in search_results:
                        payload = result.payload
                        chapter_id = payload.get("chapter_id", "")

                        if chapter_id not in chapters_seen:
                            chapters_seen.add(chapter_id)
                            results.append({
                                "chapter_id": chapter_id,
                                "chapter_title": payload.get("chapter_title", ""),
                                "path": payload.get("path", ""),
                                "relevance_score": result.score,
                                "preview": payload.get("content", "")[:200] + "...",
                            })

                except Exception as e:
                    logger.error(f"Chapter search error: {e}")

            return {
                "chapters": results,
                "query": query,
                "total_found": len(results),
            }

        self.register_skill(Skill(
            name="searchChapters",
            description="Search for relevant chapters in the textbook",
            handler=search_chapters_handler,
            output_type="dict",
        ))

        # Skill: Retrieve Sections
        async def retrieve_sections_handler(
            context: AgentContext,
            chapter_id: str = None,
            section_query: str = None,
            limit: int = 5,
            **kwargs
        ) -> Dict[str, Any]:
            """Retrieve specific sections from a chapter."""

            sections = []

            if self.embedding_service and self.vector_store:
                try:
                    # If section_query provided, search semantically
                    if section_query:
                        query_embedding = await self.embedding_service.embed_query(section_query)

                        search_filter = None
                        if chapter_id:
                            search_filter = {"chapter_id": chapter_id}

                        search_results = await self.vector_store.search(
                            query_vector=query_embedding,
                            limit=limit,
                            filter_conditions=search_filter,
                        )

                        for result in search_results:
                            payload = result.payload
                            sections.append({
                                "section_id": payload.get("section_id", ""),
                                "section_title": payload.get("section_title", ""),
                                "chapter_id": payload.get("chapter_id", ""),
                                "chapter_title": payload.get("chapter_title", ""),
                                "content": payload.get("content", ""),
                                "relevance_score": result.score,
                            })

                except Exception as e:
                    logger.error(f"Section retrieval error: {e}")

            return {
                "sections": sections,
                "chapter_id": chapter_id,
                "query": section_query,
                "total_found": len(sections),
            }

        self.register_skill(Skill(
            name="retrieveSections",
            description="Retrieve specific sections from a chapter",
            handler=retrieve_sections_handler,
            output_type="dict",
        ))
