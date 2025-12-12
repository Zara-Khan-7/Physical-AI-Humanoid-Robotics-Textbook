"""
Agent Registry
==============

Centralized registry for managing agent instances.
Provides singleton access to agents and handles dependency injection.
"""

from typing import Dict, List, Optional, Type
import logging
from .base import BaseAgent, AgentContext

logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Centralized registry for managing agent instances.

    The registry maintains a collection of agent instances and provides
    methods for registering, retrieving, and listing agents.

    Usage:
        registry = AgentRegistry()
        registry.register(ContentAgent(llm_service=llm))
        agent = registry.get("ContentAgent")
        response = await agent.execute_skill("createContent", context, topic="AI")
    """

    _instance: Optional["AgentRegistry"] = None

    def __new__(cls) -> "AgentRegistry":
        """Singleton pattern for global registry access."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._agents: Dict[str, BaseAgent] = {}
            cls._instance._initialized = False
        return cls._instance

    def register(self, agent: BaseAgent) -> None:
        """
        Register an agent instance.

        Args:
            agent: Agent instance to register
        """
        self._agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name} with skills: {list(agent.skills.keys())}")

    def unregister(self, agent_name: str) -> bool:
        """
        Unregister an agent by name.

        Args:
            agent_name: Name of the agent to unregister

        Returns:
            True if agent was unregistered, False if not found
        """
        if agent_name in self._agents:
            del self._agents[agent_name]
            logger.info(f"Unregistered agent: {agent_name}")
            return True
        return False

    def get(self, agent_name: str) -> Optional[BaseAgent]:
        """
        Get an agent by name.

        Args:
            agent_name: Name of the agent to retrieve

        Returns:
            Agent instance or None if not found
        """
        return self._agents.get(agent_name)

    def get_by_skill(self, skill_name: str) -> Optional[BaseAgent]:
        """
        Find an agent that has a specific skill.

        Args:
            skill_name: Name of the skill to find

        Returns:
            First agent with the skill, or None if not found
        """
        for agent in self._agents.values():
            if agent.has_skill(skill_name):
                return agent
        return None

    def list_agents(self) -> List[Dict[str, any]]:
        """
        List all registered agents with their skills.

        Returns:
            List of agent info dictionaries
        """
        return [
            {
                "name": agent.name,
                "description": agent.description,
                "skills": agent.get_skills(),
                "status": agent.status.value,
            }
            for agent in self._agents.values()
        ]

    def list_all_skills(self) -> List[Dict[str, str]]:
        """
        List all available skills across all agents.

        Returns:
            List of skill info with agent names
        """
        skills = []
        for agent in self._agents.values():
            for skill_info in agent.get_skills():
                skills.append({
                    **skill_info,
                    "agent": agent.name,
                })
        return skills

    def clear(self) -> None:
        """Clear all registered agents."""
        self._agents.clear()
        logger.info("Cleared all agents from registry")

    @property
    def agent_count(self) -> int:
        """Return the number of registered agents."""
        return len(self._agents)

    def __contains__(self, agent_name: str) -> bool:
        """Check if an agent is registered."""
        return agent_name in self._agents

    def __iter__(self):
        """Iterate over registered agents."""
        return iter(self._agents.values())


# Global registry instance
_global_registry: Optional[AgentRegistry] = None


def get_registry() -> AgentRegistry:
    """Get the global agent registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = AgentRegistry()
    return _global_registry


def initialize_agents(
    llm_service=None,
    embedding_service=None,
    vector_store=None,
) -> AgentRegistry:
    """
    Initialize all agents and register them in the global registry.

    Args:
        llm_service: LLM service instance
        embedding_service: Embedding service instance
        vector_store: Vector store service instance

    Returns:
        Configured AgentRegistry instance
    """
    from .content_agent import ContentAgent
    from .code_agent import CodeAgent
    from .rag_agent import RAGAgent
    from .personalization_agent import PersonalizationAgent
    from .translation_agent import TranslationAgent
    from .auth_agent import AuthAgent

    registry = get_registry()

    # Clear existing agents
    registry.clear()

    # Register all agents with their services
    registry.register(ContentAgent(
        llm_service=llm_service,
        embedding_service=embedding_service,
        vector_store=vector_store,
    ))

    registry.register(CodeAgent(
        llm_service=llm_service,
    ))

    registry.register(RAGAgent(
        llm_service=llm_service,
        embedding_service=embedding_service,
        vector_store=vector_store,
    ))

    registry.register(PersonalizationAgent(
        llm_service=llm_service,
    ))

    registry.register(TranslationAgent(
        llm_service=llm_service,
    ))

    registry.register(AuthAgent())

    logger.info(f"Initialized {registry.agent_count} agents")
    return registry
