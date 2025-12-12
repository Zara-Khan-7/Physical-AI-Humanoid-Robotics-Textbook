"""
Base Agent Infrastructure
=========================

Provides the foundational classes for the multi-agent system:
- BaseAgent: Abstract base class for all agents
- AgentContext: Shared context passed between agents
- AgentResponse: Standardized response format
- Skill: Decorator and class for defining agent skills
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, TypeVar, Generic
from enum import Enum
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Status of an agent execution."""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    WAITING = "waiting"


@dataclass
class AgentContext:
    """
    Shared context passed between agents during execution.

    Attributes:
        user_id: Optional user identifier for personalization
        session_id: Session identifier for conversation tracking
        language: Current language (en/ur)
        user_profile: User background information
        conversation_history: List of previous messages
        metadata: Additional context data
        trace: Execution trace for debugging
    """
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    language: str = "en"
    user_profile: Optional[Dict[str, Any]] = None
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    trace: List[Dict[str, Any]] = field(default_factory=list)

    def add_trace(self, agent_name: str, skill_name: str, input_data: Any, output_data: Any):
        """Add an execution trace entry."""
        self.trace.append({
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent_name,
            "skill": skill_name,
            "input": str(input_data)[:500],  # Truncate for logging
            "output": str(output_data)[:500],
        })

    def get_user_experience_level(self) -> str:
        """Get user's experience level from profile."""
        if not self.user_profile:
            return "beginner"

        sw_exp = self.user_profile.get("software_experience", "none")
        hw_exp = self.user_profile.get("hardware_experience", "none")

        exp_levels = {"none": 0, "beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
        avg_level = (exp_levels.get(sw_exp, 0) + exp_levels.get(hw_exp, 0)) / 2

        if avg_level >= 3:
            return "advanced"
        elif avg_level >= 1.5:
            return "intermediate"
        return "beginner"


@dataclass
class AgentResponse:
    """
    Standardized response from an agent execution.

    Attributes:
        success: Whether the execution was successful
        data: The response data/content
        agent_name: Name of the agent that produced this response
        skill_name: Name of the skill that was executed
        citations: Optional list of citations/sources
        metadata: Additional response metadata
        error: Error message if execution failed
    """
    success: bool
    data: Any
    agent_name: str
    skill_name: str
    citations: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "success": self.success,
            "data": self.data,
            "agent": self.agent_name,
            "skill": self.skill_name,
            "citations": self.citations,
            "metadata": self.metadata,
            "error": self.error,
        }


@dataclass
class Skill:
    """
    Represents a skill that an agent can perform.

    Attributes:
        name: Unique skill identifier
        description: Human-readable description
        handler: Async function that executes the skill
        required_context: List of required context fields
        output_type: Expected output type description
    """
    name: str
    description: str
    handler: Callable
    required_context: List[str] = field(default_factory=list)
    output_type: str = "any"

    async def execute(self, context: AgentContext, **kwargs) -> Any:
        """Execute the skill with the given context."""
        # Validate required context
        for field_name in self.required_context:
            if not hasattr(context, field_name) or getattr(context, field_name) is None:
                raise ValueError(f"Missing required context field: {field_name}")

        return await self.handler(context, **kwargs)


def skill(name: str, description: str, required_context: List[str] = None, output_type: str = "any"):
    """
    Decorator for defining agent skills.

    Usage:
        @skill("my_skill", "Does something useful", required_context=["user_id"])
        async def my_skill_handler(context: AgentContext, param1: str) -> str:
            return f"Result for {param1}"
    """
    def decorator(func: Callable) -> Skill:
        return Skill(
            name=name,
            description=description,
            handler=func,
            required_context=required_context or [],
            output_type=output_type,
        )
    return decorator


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.

    Agents are specialized processors that can execute skills to perform
    specific tasks. Each agent has a name, description, and a set of skills.

    Subclasses must implement:
        - _register_skills(): Register all skills the agent can perform
    """

    def __init__(self, llm_service=None, embedding_service=None, vector_store=None):
        """
        Initialize the agent with optional services.

        Args:
            llm_service: LLM service for text generation
            embedding_service: Service for generating embeddings
            vector_store: Vector database service
        """
        self.llm_service = llm_service
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.skills: Dict[str, Skill] = {}
        self.status = AgentStatus.IDLE
        self._register_skills()

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the agent's name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return the agent's description."""
        pass

    @abstractmethod
    def _register_skills(self) -> None:
        """Register all skills this agent can perform."""
        pass

    def register_skill(self, skill_obj: Skill) -> None:
        """Register a skill with the agent."""
        self.skills[skill_obj.name] = skill_obj
        logger.debug(f"Agent {self.name}: Registered skill '{skill_obj.name}'")

    def get_skills(self) -> List[Dict[str, str]]:
        """Get list of available skills with descriptions."""
        return [
            {"name": s.name, "description": s.description, "output_type": s.output_type}
            for s in self.skills.values()
        ]

    def has_skill(self, skill_name: str) -> bool:
        """Check if agent has a specific skill."""
        return skill_name in self.skills

    async def execute_skill(
        self,
        skill_name: str,
        context: AgentContext,
        **kwargs
    ) -> AgentResponse:
        """
        Execute a specific skill.

        Args:
            skill_name: Name of the skill to execute
            context: Agent context with user/session info
            **kwargs: Additional arguments for the skill

        Returns:
            AgentResponse with the execution result
        """
        if skill_name not in self.skills:
            return AgentResponse(
                success=False,
                data=None,
                agent_name=self.name,
                skill_name=skill_name,
                error=f"Skill '{skill_name}' not found in agent '{self.name}'"
            )

        skill_obj = self.skills[skill_name]
        self.status = AgentStatus.RUNNING

        try:
            logger.info(f"Agent {self.name}: Executing skill '{skill_name}'")
            result = await skill_obj.execute(context, **kwargs)

            # Add to trace
            context.add_trace(self.name, skill_name, kwargs, result)

            self.status = AgentStatus.SUCCESS
            return AgentResponse(
                success=True,
                data=result,
                agent_name=self.name,
                skill_name=skill_name,
            )

        except Exception as e:
            logger.error(f"Agent {self.name}: Skill '{skill_name}' failed: {str(e)}")
            self.status = AgentStatus.ERROR
            return AgentResponse(
                success=False,
                data=None,
                agent_name=self.name,
                skill_name=skill_name,
                error=str(e),
            )

    async def process(self, context: AgentContext, **kwargs) -> AgentResponse:
        """
        Default processing method - can be overridden by subclasses.

        This method provides a high-level interface for the agent to
        automatically select and execute the appropriate skill based
        on the input.
        """
        # Default implementation - subclasses can override
        if not self.skills:
            return AgentResponse(
                success=False,
                data=None,
                agent_name=self.name,
                skill_name="process",
                error="No skills registered",
            )

        # Execute first skill by default
        first_skill = list(self.skills.keys())[0]
        return await self.execute_skill(first_skill, context, **kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, skills={list(self.skills.keys())})"
