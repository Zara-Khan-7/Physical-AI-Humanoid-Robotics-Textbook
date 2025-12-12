"""
Personalization Agent
=====================

Modifies content based on user background (experience, hardware/software skill).

Skills:
- personalizeContent: Adapt content for user's background
- adaptDifficulty: Adjust difficulty level of explanations
- recommendChapters: Recommend chapters based on user goals
"""

from typing import Any, Dict, List, Optional
import logging
from .base import BaseAgent, AgentContext, Skill

logger = logging.getLogger(__name__)


class PersonalizationAgent(BaseAgent):
    """
    Agent specialized for personalizing content based on user background.

    This agent adapts explanations, difficulty, and recommendations
    based on the user's software/hardware experience and learning goals.
    """

    @property
    def name(self) -> str:
        return "PersonalizationAgent"

    @property
    def description(self) -> str:
        return "Personalizes textbook content based on user's software/hardware experience and learning goals."

    def _register_skills(self) -> None:
        """Register personalization skills."""

        # Skill: Personalize Content
        async def personalize_content_handler(
            context: AgentContext,
            content: str = None,
            message: str = None,
            chapter_title: str = None,
            **kwargs
        ) -> Dict[str, Any]:
            """Adapt content for user's background."""

            # Get user profile info
            user_profile = context.user_profile or {}
            sw_exp = user_profile.get("software_experience", "beginner")
            hw_exp = user_profile.get("hardware_experience", "beginner")
            goals = user_profile.get("learning_goals", "General understanding of Physical AI")

            experience_level = context.get_user_experience_level()

            # Build personalization prompt
            prompt = f"""You are a personalized AI tutor for the Physical AI and Humanoid Robotics textbook.

User Background:
- Software Experience: {sw_exp}
- Hardware Experience: {hw_exp}
- Learning Goals: {goals}
- Overall Level: {experience_level}

{f"Chapter: {chapter_title}" if chapter_title else ""}
{f"Content to personalize: {content[:2000]}" if content else ""}
{f"User request: {message}" if message else ""}

Please provide a personalized introduction and key concepts summary tailored to this user's background:

1. A personalized welcome (2-3 sentences acknowledging their background)
2. Key concepts explained at their level (bullet points)
3. What to focus on based on their experience
4. Suggested learning approach
5. Prerequisites they should review (if any)

Make the content {
    "simple and foundational with lots of analogies" if experience_level == "beginner"
    else "practical with real-world applications" if experience_level == "intermediate"
    else "technically deep with advanced insights"
}."""

            if self.llm_service:
                response = await self.llm_service.generate_response(
                    query=prompt,
                    context="",
                    history=[],
                    language=context.language,
                )

                return {
                    "personalized_content": response,
                    "user_level": experience_level,
                    "software_experience": sw_exp,
                    "hardware_experience": hw_exp,
                    "learning_goals": goals,
                    "chapter_title": chapter_title,
                }

            return {
                "personalized_content": "Personalization service not available",
                "user_level": experience_level,
            }

        self.register_skill(Skill(
            name="personalizeContent",
            description="Adapt content for user's software/hardware background",
            handler=personalize_content_handler,
            required_context=["user_profile"],
            output_type="dict",
        ))

        # Skill: Adapt Difficulty
        async def adapt_difficulty_handler(
            context: AgentContext,
            content: str,
            target_level: str = None,
            **kwargs
        ) -> Dict[str, Any]:
            """Adjust difficulty level of explanations."""

            # Use target level or infer from user profile
            if target_level is None:
                target_level = context.get_user_experience_level()

            adaptations = {
                "beginner": """Simplify the content:
- Replace technical jargon with everyday language
- Add analogies from daily life
- Break complex concepts into smaller steps
- Add "Think of it like..." examples
- Define all technical terms""",

                "intermediate": """Balance the content:
- Keep essential technical terms but explain them
- Focus on practical applications
- Add code examples where relevant
- Connect concepts to real robotics systems
- Include "why this matters" sections""",

                "advanced": """Enhance the content:
- Use precise technical terminology
- Discuss edge cases and limitations
- Add mathematical foundations where relevant
- Compare different approaches
- Include research references and advanced topics""",
            }

            prompt = f"""Adapt the following content for a {target_level} level reader:

Original Content:
{content}

{adaptations.get(target_level, adaptations["intermediate"])}

Provide the adapted version maintaining the core information."""

            if self.llm_service:
                response = await self.llm_service.generate_response(
                    query=prompt,
                    context="",
                    history=[],
                    language=context.language,
                )

                return {
                    "adapted_content": response,
                    "original_content": content[:500] + "..." if len(content) > 500 else content,
                    "target_level": target_level,
                }

            return {
                "adapted_content": content,
                "target_level": target_level,
                "error": "LLM service not available",
            }

        self.register_skill(Skill(
            name="adaptDifficulty",
            description="Adjust the difficulty level of content explanations",
            handler=adapt_difficulty_handler,
            output_type="dict",
        ))

        # Skill: Recommend Chapters
        async def recommend_chapters_handler(
            context: AgentContext,
            current_chapter: str = None,
            interests: List[str] = None,
            **kwargs
        ) -> Dict[str, Any]:
            """Recommend chapters based on user goals and progress."""

            user_profile = context.user_profile or {}
            goals = user_profile.get("learning_goals", "")
            sw_exp = user_profile.get("software_experience", "beginner")
            hw_exp = user_profile.get("hardware_experience", "beginner")

            # Chapter structure of the textbook
            chapters = [
                {"id": "01", "title": "Introduction to Physical AI", "prereqs": [], "focus": ["overview", "basics"]},
                {"id": "02", "title": "Humanoid Robot Anatomy", "prereqs": ["01"], "focus": ["hardware", "mechanics"]},
                {"id": "03", "title": "Sensors and Perception", "prereqs": ["01", "02"], "focus": ["hardware", "sensors"]},
                {"id": "04", "title": "Motion and Control", "prereqs": ["02", "03"], "focus": ["software", "control"]},
                {"id": "05", "title": "AI and Machine Learning", "prereqs": ["01"], "focus": ["software", "AI"]},
                {"id": "06", "title": "Applications and Future", "prereqs": ["01-05"], "focus": ["applications"]},
            ]

            prompt = f"""Based on the user's profile, recommend the best chapters to study next:

User Profile:
- Software Experience: {sw_exp}
- Hardware Experience: {hw_exp}
- Learning Goals: {goals}
- Current/Last Chapter: {current_chapter or "None"}
- Interests: {', '.join(interests) if interests else "Not specified"}

Available Chapters:
{chr(10).join([f"- Chapter {c['id']}: {c['title']} (Focus: {', '.join(c['focus'])})" for c in chapters])}

Provide:
1. Top 3 recommended chapters to study next
2. Why each chapter is recommended for this user
3. Suggested study order
4. Any chapters to review first based on prerequisites"""

            if self.llm_service:
                response = await self.llm_service.generate_response(
                    query=prompt,
                    context="",
                    history=[],
                    language=context.language,
                )

                return {
                    "recommendations": response,
                    "user_level": context.get_user_experience_level(),
                    "current_chapter": current_chapter,
                    "learning_goals": goals,
                }

            return {
                "recommendations": "Recommendation service not available",
                "user_level": context.get_user_experience_level(),
            }

        self.register_skill(Skill(
            name="recommendChapters",
            description="Recommend chapters based on user goals and progress",
            handler=recommend_chapters_handler,
            output_type="dict",
        ))
