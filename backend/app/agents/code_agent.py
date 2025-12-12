"""
Code Agent
==========

Produces runnable code samples and validates correctness.

Skills:
- generateCode: Generate code examples for robotics concepts
- fixCode: Debug and fix code issues
- explainCode: Explain code functionality
"""

from typing import Any, Dict, List, Optional
import logging
import re
from .base import BaseAgent, AgentContext, Skill

logger = logging.getLogger(__name__)


class CodeAgent(BaseAgent):
    """
    Agent specialized for code generation and analysis.

    This agent can generate code examples, fix bugs, and explain
    code related to Physical AI and robotics concepts.
    """

    @property
    def name(self) -> str:
        return "CodeAgent"

    @property
    def description(self) -> str:
        return "Produces runnable code samples, debugs code, and explains code functionality for robotics applications."

    def _register_skills(self) -> None:
        """Register code-related skills."""

        # Skill: Generate Code
        async def generate_code_handler(
            context: AgentContext,
            message: str,
            language: str = "python",
            concept: str = None,
            **kwargs
        ) -> Dict[str, Any]:
            """Generate code examples for a concept."""

            prompt = f"""Generate a code example for the following robotics/AI concept:

Request: {message}
{f"Concept: {concept}" if concept else ""}
Programming Language: {language}

Requirements:
1. Write clean, well-commented code
2. Include necessary imports
3. Add docstrings explaining the purpose
4. Provide example usage
5. Keep the code runnable and practical

Focus on Physical AI and Humanoid Robotics applications.

Format the code in a code block with the language specified."""

            if self.llm_service:
                response = await self.llm_service.generate_response(
                    query=prompt,
                    context="",
                    history=[],
                    language="en",  # Code should be in English
                )

                # Extract code blocks from response
                code_blocks = self._extract_code_blocks(response)

                return {
                    "code": code_blocks[0] if code_blocks else response,
                    "explanation": response,
                    "language": language,
                    "concept": concept or message,
                }

            return {
                "code": f"# Code generation for '{message}' - LLM service not available",
                "explanation": "LLM service not available",
                "language": language,
            }

        self.register_skill(Skill(
            name="generateCode",
            description="Generate code examples for robotics and AI concepts",
            handler=generate_code_handler,
            output_type="dict",
        ))

        # Skill: Fix Code
        async def fix_code_handler(
            context: AgentContext,
            code: str,
            error_message: str = None,
            **kwargs
        ) -> Dict[str, Any]:
            """Debug and fix code issues."""

            prompt = f"""Debug and fix the following code:

```
{code}
```

{f"Error message: {error_message}" if error_message else ""}

Please:
1. Identify the issue(s) in the code
2. Explain what's wrong
3. Provide the corrected code
4. Explain the fix

Focus on common issues in robotics/AI code like:
- Sensor data handling
- Motor control logic
- Timing/synchronization issues
- Data type mismatches"""

            if self.llm_service:
                response = await self.llm_service.generate_response(
                    query=prompt,
                    context="",
                    history=[],
                    language="en",
                )

                code_blocks = self._extract_code_blocks(response)

                return {
                    "fixed_code": code_blocks[0] if code_blocks else "",
                    "explanation": response,
                    "original_code": code,
                    "error_message": error_message,
                }

            return {
                "fixed_code": code,
                "explanation": "LLM service not available",
                "original_code": code,
            }

        self.register_skill(Skill(
            name="fixCode",
            description="Debug and fix code issues with explanations",
            handler=fix_code_handler,
            output_type="dict",
        ))

        # Skill: Explain Code
        async def explain_code_handler(
            context: AgentContext,
            code: str,
            detail_level: str = "medium",
            **kwargs
        ) -> Dict[str, Any]:
            """Explain code functionality."""

            # Adjust explanation based on user level
            user_level = context.get_user_experience_level()

            detail_instructions = {
                "brief": "Provide a brief, high-level explanation in 2-3 sentences.",
                "medium": "Explain the main components and logic flow. Include key concepts.",
                "detailed": "Provide a line-by-line explanation with all concepts explained.",
            }

            level_adjustments = {
                "beginner": "Explain every concept, avoid assumptions about prior knowledge.",
                "intermediate": "Focus on the robotics-specific aspects and interesting patterns.",
                "advanced": "Focus on performance considerations, best practices, and potential improvements.",
            }

            prompt = f"""Explain the following code:

```
{code}
```

Detail Level: {detail_level}
{detail_instructions.get(detail_level, detail_instructions["medium"])}

User Experience Level: {user_level}
{level_adjustments.get(user_level, "")}

Include:
1. Overall purpose of the code
2. Key components/functions explained
3. How it relates to Physical AI/robotics concepts
4. Any important notes or caveats"""

            if self.llm_service:
                response = await self.llm_service.generate_response(
                    query=prompt,
                    context="",
                    history=[],
                    language=context.language,
                )

                return {
                    "explanation": response,
                    "code": code,
                    "detail_level": detail_level,
                    "user_level": user_level,
                }

            return {
                "explanation": "LLM service not available",
                "code": code,
            }

        self.register_skill(Skill(
            name="explainCode",
            description="Explain code functionality at the user's level",
            handler=explain_code_handler,
            output_type="dict",
        ))

    def _extract_code_blocks(self, text: str) -> List[str]:
        """Extract code blocks from markdown-formatted text."""
        # Match code blocks with or without language specification
        pattern = r"```(?:\w+)?\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        return [match.strip() for match in matches] if matches else []
