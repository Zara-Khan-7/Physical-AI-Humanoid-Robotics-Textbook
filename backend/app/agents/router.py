"""
Agent Router
============

Intelligent routing of requests to appropriate agents based on
intent classification and skill matching.
"""

from typing import Dict, List, Optional, Tuple
import logging
import re
from .base import BaseAgent, AgentContext, AgentResponse
from .registry import AgentRegistry, get_registry

logger = logging.getLogger(__name__)


# Intent patterns for routing
INTENT_PATTERNS = {
    "translation": [
        r"translat(e|ion)",
        r"اردو",
        r"urdu",
        r"ترجم",
        r"convert.*to.*urdu",
    ],
    "personalization": [
        r"personaliz(e|ation)",
        r"adapt.*for.*me",
        r"my.*level",
        r"based.*on.*my.*background",
        r"customize",
        r"tailor",
    ],
    "code": [
        r"code",
        r"program",
        r"implement",
        r"write.*function",
        r"python",
        r"javascript",
        r"fix.*bug",
        r"debug",
        r"syntax",
    ],
    "content": [
        r"explain",
        r"what.*is",
        r"describe",
        r"summary",
        r"summarize",
        r"quiz",
        r"question",
        r"diagram",
        r"chapter",
        r"topic",
    ],
    "rag": [
        r"search",
        r"find",
        r"where.*in.*book",
        r"cite",
        r"reference",
        r"according.*to",
        r"textbook.*says",
    ],
    "auth": [
        r"sign.*in",
        r"sign.*up",
        r"login",
        r"logout",
        r"profile",
        r"account",
        r"password",
    ],
}

# Map intents to agents and default skills
INTENT_TO_AGENT = {
    "translation": ("TranslationAgent", "translateToUrdu"),
    "personalization": ("PersonalizationAgent", "personalizeContent"),
    "code": ("CodeAgent", "generateCode"),
    "content": ("ContentAgent", "explainConcepts"),
    "rag": ("RAGAgent", "ragQuery"),
    "auth": ("AuthAgent", "getProfile"),
}


class AgentRouter:
    """
    Routes requests to appropriate agents based on intent analysis.

    The router analyzes incoming requests to determine the user's intent
    and routes to the most appropriate agent and skill.

    Usage:
        router = AgentRouter(registry)
        response = await router.route(context, message="Explain transformers")
    """

    def __init__(self, registry: AgentRegistry = None):
        """
        Initialize the router.

        Args:
            registry: Agent registry instance (uses global if not provided)
        """
        self.registry = registry or get_registry()

    def classify_intent(self, message: str) -> Tuple[str, float]:
        """
        Classify the intent of a message.

        Args:
            message: User message to classify

        Returns:
            Tuple of (intent_name, confidence_score)
        """
        message_lower = message.lower()
        scores: Dict[str, int] = {}

        for intent, patterns in INTENT_PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    score += 1
            scores[intent] = score

        # Get highest scoring intent
        if not scores or max(scores.values()) == 0:
            # Default to RAG for general questions
            return ("rag", 0.5)

        best_intent = max(scores, key=scores.get)
        confidence = min(scores[best_intent] / 3, 1.0)  # Normalize to 0-1

        return (best_intent, confidence)

    def get_agent_for_intent(self, intent: str) -> Tuple[Optional[BaseAgent], str]:
        """
        Get the appropriate agent and skill for an intent.

        Args:
            intent: Classified intent name

        Returns:
            Tuple of (agent_instance, skill_name)
        """
        if intent not in INTENT_TO_AGENT:
            # Default to RAG agent
            agent = self.registry.get("RAGAgent")
            return (agent, "ragQuery")

        agent_name, skill_name = INTENT_TO_AGENT[intent]
        agent = self.registry.get(agent_name)

        return (agent, skill_name)

    async def route(
        self,
        context: AgentContext,
        message: str,
        force_agent: str = None,
        force_skill: str = None,
        **kwargs
    ) -> AgentResponse:
        """
        Route a request to the appropriate agent.

        Args:
            context: Agent context with user/session info
            message: User message/query
            force_agent: Force routing to specific agent (optional)
            force_skill: Force execution of specific skill (optional)
            **kwargs: Additional arguments passed to the skill

        Returns:
            AgentResponse from the executed skill
        """
        # If forcing specific agent/skill
        if force_agent:
            agent = self.registry.get(force_agent)
            if not agent:
                return AgentResponse(
                    success=False,
                    data=None,
                    agent_name=force_agent,
                    skill_name=force_skill or "unknown",
                    error=f"Agent '{force_agent}' not found",
                )

            skill_name = force_skill or list(agent.skills.keys())[0]
            return await agent.execute_skill(skill_name, context, message=message, **kwargs)

        # Classify intent and route
        intent, confidence = self.classify_intent(message)
        logger.info(f"Classified intent: {intent} (confidence: {confidence:.2f})")

        agent, skill_name = self.get_agent_for_intent(intent)

        if not agent:
            return AgentResponse(
                success=False,
                data=None,
                agent_name="unknown",
                skill_name="unknown",
                error="No agent available for this request",
            )

        # Add routing metadata
        context.metadata["routed_intent"] = intent
        context.metadata["routing_confidence"] = confidence

        # Execute the skill
        return await agent.execute_skill(skill_name, context, message=message, **kwargs)

    async def route_to_skill(
        self,
        skill_name: str,
        context: AgentContext,
        **kwargs
    ) -> AgentResponse:
        """
        Route directly to a specific skill (finds agent automatically).

        Args:
            skill_name: Name of the skill to execute
            context: Agent context
            **kwargs: Arguments for the skill

        Returns:
            AgentResponse from the skill execution
        """
        agent = self.registry.get_by_skill(skill_name)

        if not agent:
            return AgentResponse(
                success=False,
                data=None,
                agent_name="unknown",
                skill_name=skill_name,
                error=f"No agent found with skill '{skill_name}'",
            )

        return await agent.execute_skill(skill_name, context, **kwargs)

    async def multi_agent_pipeline(
        self,
        context: AgentContext,
        steps: List[Dict[str, any]],
    ) -> List[AgentResponse]:
        """
        Execute a pipeline of agent skills in sequence.

        Args:
            context: Shared context for all steps
            steps: List of step definitions, each with:
                   - agent: Agent name
                   - skill: Skill name
                   - kwargs: Arguments for the skill

        Returns:
            List of AgentResponses from each step
        """
        responses = []

        for i, step in enumerate(steps):
            agent_name = step.get("agent")
            skill_name = step.get("skill")
            step_kwargs = step.get("kwargs", {})

            # Add previous response to kwargs if needed
            if responses and step.get("use_previous_output"):
                step_kwargs["previous_output"] = responses[-1].data

            agent = self.registry.get(agent_name)
            if not agent:
                responses.append(AgentResponse(
                    success=False,
                    data=None,
                    agent_name=agent_name,
                    skill_name=skill_name,
                    error=f"Agent '{agent_name}' not found at step {i}",
                ))
                if step.get("stop_on_error", True):
                    break
                continue

            response = await agent.execute_skill(skill_name, context, **step_kwargs)
            responses.append(response)

            if not response.success and step.get("stop_on_error", True):
                break

        return responses


# Global router instance
_global_router: Optional[AgentRouter] = None


def get_router() -> AgentRouter:
    """Get the global agent router instance."""
    global _global_router
    if _global_router is None:
        _global_router = AgentRouter()
    return _global_router
