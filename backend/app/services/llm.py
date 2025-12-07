"""LLM service for Google Gemini response generation."""

import google.generativeai as genai
from typing import Any

# System prompt that restricts answers to book content only
SYSTEM_PROMPT = """You are a helpful tutor for the Physical AI and Humanoid Robotics textbook.

IMPORTANT RULES:
1. Answer questions ONLY using the provided context from the textbook.
2. Always cite the source section for each fact you mention.
3. If the answer cannot be found in the context, say: "I don't have information about that in the textbook. Here are some topics I can help with: [list relevant topics from context]"
4. Keep responses clear, educational, and concise.
5. Use the same language as the user's question (English or Urdu).
6. Format code examples with proper syntax highlighting hints.
7. For mathematical concepts, use clear notation.

When citing sources, use this format: [Chapter: Section]
"""


class LLMService:
    """Service for generating responses using Google Gemini."""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash-001",
    ):
        """Initialize the LLM service.

        Args:
            api_key: Google AI API key
            model: Gemini model name
        """
        self.api_key = api_key
        self.model_name = model

        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name=model,
                system_instruction=SYSTEM_PROMPT,
            )
        else:
            self.model = None

    def is_configured(self) -> bool:
        """Check if the service is properly configured."""
        return bool(self.api_key) and self.model is not None

    async def generate_response(
        self,
        query: str,
        context_docs: list[dict[str, Any]],
        history: list[dict[str, str]] | None = None,
        language: str = "en",
    ) -> str:
        """Generate a response using RAG context.

        Args:
            query: User's question
            context_docs: Retrieved context documents from vector search
            history: Previous conversation messages
            language: Response language preference

        Returns:
            Generated response text
        """
        if not self.is_configured():
            raise ValueError("LLM service not configured: missing API key")

        # Build context from retrieved documents
        context = self._format_context(context_docs)

        # Build conversation history
        history_text = self._format_history(history) if history else "None"

        # Build the prompt
        prompt = f"""Context from the textbook:
{context}

Conversation History:
{history_text}

User Question ({language}): {query}

Please provide a helpful, accurate answer based on the context above. Remember to cite sources."""

        # Generate response
        response = self.model.generate_content(prompt)

        return response.text

    def _format_context(self, docs: list[dict[str, Any]]) -> str:
        """Format context documents for the prompt."""
        if not docs:
            return "No relevant context found."

        formatted = []
        for doc in docs:
            section_ref = f"[{doc.get('chapter_title', 'Unknown')}: {doc.get('section_title', 'Unknown')}]"
            content = doc.get("content", "")
            formatted.append(f"{section_ref}\n{content}")

        return "\n\n---\n\n".join(formatted)

    def _format_history(self, history: list[dict[str, str]]) -> str:
        """Format conversation history for the prompt."""
        if not history:
            return "None"

        # Limit to last 10 exchanges (20 messages)
        recent = history[-20:] if len(history) > 20 else history

        formatted = []
        for msg in recent:
            role = "User" if msg.get("role") == "user" else "Assistant"
            content = msg.get("content", "")
            formatted.append(f"{role}: {content}")

        return "\n".join(formatted)

    async def check_availability(self) -> bool:
        """Check if Gemini API is available."""
        if not self.is_configured():
            return False

        try:
            # Simple test generation
            response = self.model.generate_content("Say 'ok' in one word.")
            return bool(response.text)
        except Exception:
            return False
