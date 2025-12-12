"""
Translation Agent
=================

Translates English → Urdu with RTL formatting preserved.

Skills:
- translateToUrdu: Translate content to Urdu
- formatRTL: Format content for RTL display
"""

from typing import Any, Dict, List, Optional
import logging
from .base import BaseAgent, AgentContext, Skill

logger = logging.getLogger(__name__)


class TranslationAgent(BaseAgent):
    """
    Agent specialized for English to Urdu translation.

    This agent translates textbook content to Urdu while preserving
    technical accuracy and proper RTL formatting.
    """

    @property
    def name(self) -> str:
        return "TranslationAgent"

    @property
    def description(self) -> str:
        return "Translates textbook content from English to Urdu with RTL formatting support."

    def _register_skills(self) -> None:
        """Register translation skills."""

        # Skill: Translate to Urdu
        async def translate_to_urdu_handler(
            context: AgentContext,
            content: str = None,
            message: str = None,
            chapter_title: str = None,
            translation_style: str = "educational",
            **kwargs
        ) -> Dict[str, Any]:
            """Translate content to Urdu."""

            text_to_translate = content or message or ""

            style_instructions = {
                "educational": """آپ ایک ماہر اردو مترجم اور ٹیکنیکل رائٹر ہیں۔
سادہ اور آسان اردو استعمال کریں جو طلباء کے لیے سمجھنا آسان ہو۔
ٹیکنیکل اصطلاحات کو انگریزی میں رکھیں لیکن اردو میں وضاحت دیں۔""",

                "formal": """رسمی اور معیاری اردو استعمال کریں۔
علمی زبان اور تعلیمی انداز اپنائیں۔""",

                "conversational": """بول چال کی سادہ اردو استعمال کریں۔
دوستانہ اور آسان انداز میں لکھیں۔""",
            }

            prompt = f"""آپ ایک ماہر اردو مترجم اور ٹیکنیکل رائٹر ہیں۔ براہ کرم اس مواد کا اردو میں تفصیلی ترجمہ کریں۔

{f"باب کا عنوان: {chapter_title}" if chapter_title else ""}

ترجمے کی ہدایات:
{style_instructions.get(translation_style, style_instructions["educational"])}

1. باب کا عنوان اردو میں لکھیں
2. اہم تصورات کا خلاصہ اردو میں لکھیں (تقریباً 400-500 الفاظ)
3. اہم ٹیکنیکل اصطلاحات کو انگریزی اور اردو دونوں میں لکھیں
4. مطالعے کی تجاویز اردو میں دیں
5. سادہ اور آسان اردو استعمال کریں جو طلباء کے لیے سمجھنا آسان ہو

مواد جس کا ترجمہ کرنا ہے:
{text_to_translate[:3000]}

Please respond entirely in Urdu script. Use proper Urdu grammar and sentence structure. Keep technical terms in English with Urdu transliteration where helpful."""

            if self.llm_service:
                response = await self.llm_service.generate_response(
                    query=prompt,
                    context="",
                    history=[],
                    language="ur",
                )

                return {
                    "translation": response,
                    "original_text": text_to_translate[:500] + "..." if len(text_to_translate) > 500 else text_to_translate,
                    "chapter_title": chapter_title,
                    "translation_style": translation_style,
                    "direction": "rtl",
                    "language": "ur",
                }

            return {
                "translation": "ترجمہ کی خدمت دستیاب نہیں ہے",
                "original_text": text_to_translate,
                "error": "LLM service not available",
            }

        self.register_skill(Skill(
            name="translateToUrdu",
            description="Translate content from English to Urdu with technical accuracy",
            handler=translate_to_urdu_handler,
            output_type="dict",
        ))

        # Skill: Format RTL
        async def format_rtl_handler(
            context: AgentContext,
            content: str,
            include_english_terms: bool = True,
            **kwargs
        ) -> Dict[str, Any]:
            """Format content for RTL display."""

            # RTL formatting rules
            rtl_markers = {
                "start": "\u200F",  # Right-to-Left Mark
                "end": "\u200E",    # Left-to-Right Mark
                "embed": "\u202B",  # Right-to-Left Embedding
                "pop": "\u202C",    # Pop Directional Formatting
            }

            # Process content for proper RTL display
            formatted_content = content

            # Add RTL markers at the start
            formatted_content = f"{rtl_markers['embed']}{formatted_content}{rtl_markers['pop']}"

            # If including English terms, wrap them in LTR markers
            if include_english_terms:
                import re
                # Find English words/phrases and wrap them
                english_pattern = r'([A-Za-z][A-Za-z0-9\s\-\_\.]+)'

                def wrap_english(match):
                    term = match.group(1)
                    if len(term.strip()) > 2:  # Only wrap meaningful terms
                        return f"{rtl_markers['end']}{term}{rtl_markers['start']}"
                    return term

                formatted_content = re.sub(english_pattern, wrap_english, formatted_content)

            return {
                "formatted_content": formatted_content,
                "original_content": content,
                "direction": "rtl",
                "rtl_markers_used": True,
                "css_direction": "rtl",
                "css_text_align": "right",
            }

        self.register_skill(Skill(
            name="formatRTL",
            description="Format content for proper Right-to-Left display",
            handler=format_rtl_handler,
            output_type="dict",
        ))

        # Skill: Translate Technical Terms
        async def translate_terms_handler(
            context: AgentContext,
            terms: List[str],
            include_transliteration: bool = True,
            **kwargs
        ) -> Dict[str, Any]:
            """Translate technical terms with explanations."""

            terms_list = "\n".join([f"- {term}" for term in terms])

            prompt = f"""Translate the following technical terms from English to Urdu.
For each term provide:
1. The English term
2. Urdu translation (in Urdu script)
3. Transliteration (how to pronounce in Roman Urdu)
4. Brief explanation in Urdu

Terms to translate:
{terms_list}

Format each term clearly with all four components."""

            if self.llm_service:
                response = await self.llm_service.generate_response(
                    query=prompt,
                    context="",
                    history=[],
                    language="ur",
                )

                return {
                    "translations": response,
                    "original_terms": terms,
                    "include_transliteration": include_transliteration,
                }

            return {
                "translations": "Translation service not available",
                "original_terms": terms,
            }

        self.register_skill(Skill(
            name="translateTerms",
            description="Translate technical terms with transliteration and explanations",
            handler=translate_terms_handler,
            output_type="dict",
        ))
