"""
Content Agent
=============

Generates chapter explanations, diagrams, quizzes, and summaries.

Skills:
- createContent: Generate educational content for a topic
- generateQuizzes: Create quiz questions for a chapter
- explainConcepts: Explain concepts at the user's level
"""

from typing import Any, Dict, List, Optional
import logging
from .base import BaseAgent, AgentContext, Skill

logger = logging.getLogger(__name__)


class ContentAgent(BaseAgent):
    """
    Agent specialized for generating educational content.

    This agent can create explanations, quizzes, summaries, and
    other educational materials based on the textbook content.
    """

    @property
    def name(self) -> str:
        return "ContentAgent"

    @property
    def description(self) -> str:
        return "Generates chapter explanations, diagrams, quizzes, and summaries for the Physical AI textbook."

    def _register_skills(self) -> None:
        """Register content generation skills."""

        # Skill: Create Content
        async def create_content_handler(
            context: AgentContext,
            topic: str,
            content_type: str = "explanation",
            **kwargs
        ) -> Dict[str, Any]:
            """Generate educational content for a topic."""

            content_prompts = {
                "explanation": f"""Create a clear, educational explanation of the following topic from the Physical AI and Humanoid Robotics textbook:

Topic: {topic}

Provide:
1. A brief introduction (2-3 sentences)
2. Key concepts with clear definitions
3. Real-world applications or examples
4. Summary points

Keep the explanation accessible for students.""",

                "summary": f"""Provide a concise summary of the following topic:

Topic: {topic}

Include:
- Main ideas (3-5 bullet points)
- Key takeaways
- Important terminology""",

                "diagram_description": f"""Describe a diagram that would help explain:

Topic: {topic}

Include:
- What the diagram should show
- Key components to label
- Relationships between elements
- Suggested diagram type (flowchart, block diagram, etc.)""",
            }

            prompt = content_prompts.get(content_type, content_prompts["explanation"])

            if self.llm_service:
                response = await self.llm_service.generate_response(
                    query=prompt,
                    context="",
                    history=[],
                    language=context.language,
                )
                return {
                    "content": response,
                    "topic": topic,
                    "content_type": content_type,
                    "language": context.language,
                }

            return {
                "content": f"Content generation for '{topic}' - LLM service not available",
                "topic": topic,
                "content_type": content_type,
            }

        self.register_skill(Skill(
            name="createContent",
            description="Generate educational content (explanations, summaries, diagram descriptions) for a topic",
            handler=create_content_handler,
            output_type="dict",
        ))

        # Skill: Generate Quizzes
        async def generate_quizzes_handler(
            context: AgentContext,
            topic: str,
            num_questions: int = 5,
            difficulty: str = None,
            **kwargs
        ) -> Dict[str, Any]:
            """Generate quiz questions for a topic."""

            # Use user's experience level if difficulty not specified
            if difficulty is None:
                difficulty = context.get_user_experience_level()

            difficulty_instructions = {
                "beginner": "Create simple, foundational questions focusing on definitions and basic concepts.",
                "intermediate": "Create questions that test understanding and application of concepts.",
                "advanced": "Create challenging questions that require analysis, synthesis, and deep understanding.",
            }

            prompt = f"""Generate {num_questions} quiz questions about the following topic from the Physical AI textbook:

Topic: {topic}

Difficulty Level: {difficulty}
{difficulty_instructions.get(difficulty, difficulty_instructions["intermediate"])}

For each question, provide:
1. The question text
2. Four multiple choice options (A, B, C, D)
3. The correct answer
4. A brief explanation of why the answer is correct

Format as a structured list."""

            if self.llm_service:
                response = await self.llm_service.generate_response(
                    query=prompt,
                    context="",
                    history=[],
                    language=context.language,
                )
                return {
                    "questions": response,
                    "topic": topic,
                    "num_questions": num_questions,
                    "difficulty": difficulty,
                }

            return {
                "questions": f"Quiz generation for '{topic}' - LLM service not available",
                "topic": topic,
                "num_questions": num_questions,
                "difficulty": difficulty,
            }

        self.register_skill(Skill(
            name="generateQuizzes",
            description="Create quiz questions for a chapter or topic with adjustable difficulty",
            handler=generate_quizzes_handler,
            output_type="dict",
        ))

        # Skill: Explain Concepts
        async def explain_concepts_handler(
            context: AgentContext,
            message: str,
            concepts: List[str] = None,
            **kwargs
        ) -> Dict[str, Any]:
            """Explain concepts at the user's level."""

            experience_level = context.get_user_experience_level()

            # Build user context
            user_context = ""
            if context.user_profile:
                sw_exp = context.user_profile.get("software_experience", "unknown")
                hw_exp = context.user_profile.get("hardware_experience", "unknown")
                goals = context.user_profile.get("learning_goals", "")
                user_context = f"""
User Background:
- Software Experience: {sw_exp}
- Hardware Experience: {hw_exp}
- Learning Goals: {goals}
"""

            level_instructions = {
                "beginner": "Use simple language, avoid jargon, provide many examples, and explain foundational concepts first.",
                "intermediate": "Balance technical depth with clarity, assume basic knowledge, focus on practical applications.",
                "advanced": "Use technical terminology freely, focus on nuances and advanced applications, discuss trade-offs.",
            }

            prompt = f"""Explain the following concept(s) from the Physical AI and Humanoid Robotics textbook:

Query: {message}
{f"Specific concepts: {', '.join(concepts)}" if concepts else ""}

{user_context}

Experience Level: {experience_level}
Instructions: {level_instructions.get(experience_level, level_instructions["intermediate"])}

Provide a clear, educational explanation tailored to the user's background."""

            if self.llm_service:
                response = await self.llm_service.generate_response(
                    query=prompt,
                    context="",
                    history=context.conversation_history,
                    language=context.language,
                )
                return {
                    "explanation": response,
                    "concepts": concepts or [message],
                    "experience_level": experience_level,
                    "language": context.language,
                }

            return {
                "explanation": f"Explanation for '{message}' - LLM service not available",
                "concepts": concepts or [message],
                "experience_level": experience_level,
            }

        self.register_skill(Skill(
            name="explainConcepts",
            description="Explain concepts at the user's experience level with personalized context",
            handler=explain_concepts_handler,
            output_type="dict",
        ))
