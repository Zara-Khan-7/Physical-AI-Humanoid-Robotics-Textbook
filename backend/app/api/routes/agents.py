"""
Agent API Routes
================

REST API endpoints for the multi-agent system.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import logging

from ...agents import (
    AgentContext,
    AgentResponse,
)
from ...agents.registry import get_registry, initialize_agents
from ...agents.router import get_router, AgentRouter
from ..dependencies import get_llm_service, get_embedding_service, get_vector_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["agents"])

# Flag to track initialization
_agents_initialized = False


# Request/Response Models
class AgentQueryRequest(BaseModel):
    """Request for agent query."""
    message: str = Field(..., description="User message/query")
    session_id: Optional[str] = Field(None, description="Session ID for tracking")
    user_id: Optional[str] = Field(None, description="User ID for personalization")
    language: str = Field("en", description="Response language (en/ur)")
    user_profile: Optional[Dict[str, Any]] = Field(None, description="User profile data")
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    force_agent: Optional[str] = Field(None, description="Force specific agent")
    force_skill: Optional[str] = Field(None, description="Force specific skill")


class SkillExecuteRequest(BaseModel):
    """Request to execute a specific skill."""
    agent_name: str = Field(..., description="Name of the agent")
    skill_name: str = Field(..., description="Name of the skill to execute")
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    language: str = "en"
    user_profile: Optional[Dict[str, Any]] = None
    params: Dict[str, Any] = Field(default_factory=dict)


class PipelineStep(BaseModel):
    """Single step in a pipeline."""
    agent: str
    skill: str
    kwargs: Dict[str, Any] = Field(default_factory=dict)
    use_previous_output: bool = False
    stop_on_error: bool = True


class PipelineRequest(BaseModel):
    """Request to execute a multi-agent pipeline."""
    steps: List[PipelineStep]
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    language: str = "en"
    user_profile: Optional[Dict[str, Any]] = None


class AgentInfo(BaseModel):
    """Agent information response."""
    name: str
    description: str
    skills: List[Dict[str, str]]
    status: str


class AgentQueryResponse(BaseModel):
    """Response from agent query."""
    success: bool
    data: Any
    agent: str
    skill: str
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


def ensure_agents_initialized(
    llm_service=Depends(get_llm_service),
    embedding_service=Depends(get_embedding_service),
    vector_store=Depends(get_vector_store),
):
    """Dependency to ensure agents are initialized."""
    global _agents_initialized
    if not _agents_initialized:
        initialize_agents(
            llm_service=llm_service,
            embedding_service=embedding_service,
            vector_store=vector_store,
        )
        _agents_initialized = True
    return get_registry()


@router.get("/", response_model=List[AgentInfo])
async def list_agents(registry=Depends(ensure_agents_initialized)):
    """
    List all available agents and their skills.

    Returns information about each registered agent including
    their name, description, available skills, and current status.
    """
    return registry.list_agents()


@router.get("/skills", response_model=List[Dict[str, str]])
async def list_all_skills(registry=Depends(ensure_agents_initialized)):
    """
    List all available skills across all agents.

    Returns a flat list of all skills that can be executed,
    including which agent provides each skill.
    """
    return registry.list_all_skills()


@router.get("/{agent_name}", response_model=AgentInfo)
async def get_agent_info(agent_name: str, registry=Depends(ensure_agents_initialized)):
    """
    Get information about a specific agent.

    Args:
        agent_name: Name of the agent to retrieve

    Returns:
        Agent information including skills and status
    """
    agent = registry.get(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")

    return {
        "name": agent.name,
        "description": agent.description,
        "skills": agent.get_skills(),
        "status": agent.status.value,
    }


@router.post("/query", response_model=AgentQueryResponse)
async def query_agents(
    request: AgentQueryRequest,
    registry=Depends(ensure_agents_initialized),
):
    """
    Send a query to the agent system.

    The router will automatically determine the best agent
    to handle the request based on intent classification.

    Optionally force a specific agent/skill using force_agent and force_skill.
    """
    # Build context
    context = AgentContext(
        user_id=request.user_id,
        session_id=request.session_id,
        language=request.language,
        user_profile=request.user_profile,
        conversation_history=request.conversation_history,
    )

    # Get router and process query
    agent_router = get_router()

    response = await agent_router.route(
        context=context,
        message=request.message,
        force_agent=request.force_agent,
        force_skill=request.force_skill,
    )

    return AgentQueryResponse(
        success=response.success,
        data=response.data,
        agent=response.agent_name,
        skill=response.skill_name,
        citations=response.citations,
        metadata=response.metadata,
        error=response.error,
    )


@router.post("/execute", response_model=AgentQueryResponse)
async def execute_skill(
    request: SkillExecuteRequest,
    registry=Depends(ensure_agents_initialized),
):
    """
    Execute a specific skill on a specific agent.

    This bypasses the router and directly executes the requested skill.
    """
    agent = registry.get(request.agent_name)
    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{request.agent_name}' not found"
        )

    if not agent.has_skill(request.skill_name):
        raise HTTPException(
            status_code=404,
            detail=f"Skill '{request.skill_name}' not found in agent '{request.agent_name}'"
        )

    # Build context
    context = AgentContext(
        user_id=request.user_id,
        session_id=request.session_id,
        language=request.language,
        user_profile=request.user_profile,
    )

    # Execute skill
    response = await agent.execute_skill(
        skill_name=request.skill_name,
        context=context,
        **request.params,
    )

    return AgentQueryResponse(
        success=response.success,
        data=response.data,
        agent=response.agent_name,
        skill=response.skill_name,
        citations=response.citations,
        metadata=response.metadata,
        error=response.error,
    )


@router.post("/pipeline", response_model=List[AgentQueryResponse])
async def execute_pipeline(
    request: PipelineRequest,
    registry=Depends(ensure_agents_initialized),
):
    """
    Execute a multi-agent pipeline.

    Runs a sequence of agent skills, optionally passing
    output from one step to the next.
    """
    # Build context
    context = AgentContext(
        user_id=request.user_id,
        session_id=request.session_id,
        language=request.language,
        user_profile=request.user_profile,
    )

    # Convert steps to dict format
    steps = [
        {
            "agent": step.agent,
            "skill": step.skill,
            "kwargs": step.kwargs,
            "use_previous_output": step.use_previous_output,
            "stop_on_error": step.stop_on_error,
        }
        for step in request.steps
    ]

    # Execute pipeline
    agent_router = get_router()
    responses = await agent_router.multi_agent_pipeline(context, steps)

    return [
        AgentQueryResponse(
            success=r.success,
            data=r.data,
            agent=r.agent_name,
            skill=r.skill_name,
            citations=r.citations,
            metadata=r.metadata,
            error=r.error,
        )
        for r in responses
    ]


# Convenience endpoints for common operations

@router.post("/translate", response_model=AgentQueryResponse)
async def translate_content(
    content: str,
    chapter_title: Optional[str] = None,
    style: str = "educational",
    registry=Depends(ensure_agents_initialized),
):
    """
    Translate content to Urdu.

    Convenience endpoint for the TranslationAgent.translateToUrdu skill.
    """
    context = AgentContext(language="ur")
    agent = registry.get("TranslationAgent")

    if not agent:
        raise HTTPException(status_code=500, detail="TranslationAgent not available")

    response = await agent.execute_skill(
        "translateToUrdu",
        context,
        content=content,
        chapter_title=chapter_title,
        translation_style=style,
    )

    return AgentQueryResponse(
        success=response.success,
        data=response.data,
        agent=response.agent_name,
        skill=response.skill_name,
        error=response.error,
    )


@router.post("/personalize", response_model=AgentQueryResponse)
async def personalize_content(
    content: str,
    chapter_title: Optional[str] = None,
    user_profile: Optional[Dict[str, Any]] = None,
    registry=Depends(ensure_agents_initialized),
):
    """
    Personalize content for a user.

    Convenience endpoint for the PersonalizationAgent.personalizeContent skill.
    """
    context = AgentContext(
        user_profile=user_profile or {
            "software_experience": "beginner",
            "hardware_experience": "beginner",
            "learning_goals": "General understanding",
        }
    )
    agent = registry.get("PersonalizationAgent")

    if not agent:
        raise HTTPException(status_code=500, detail="PersonalizationAgent not available")

    response = await agent.execute_skill(
        "personalizeContent",
        context,
        content=content,
        chapter_title=chapter_title,
    )

    return AgentQueryResponse(
        success=response.success,
        data=response.data,
        agent=response.agent_name,
        skill=response.skill_name,
        error=response.error,
    )


@router.post("/quiz", response_model=AgentQueryResponse)
async def generate_quiz(
    topic: str,
    num_questions: int = 5,
    difficulty: Optional[str] = None,
    user_profile: Optional[Dict[str, Any]] = None,
    registry=Depends(ensure_agents_initialized),
):
    """
    Generate quiz questions for a topic.

    Convenience endpoint for the ContentAgent.generateQuizzes skill.
    """
    context = AgentContext(user_profile=user_profile)
    agent = registry.get("ContentAgent")

    if not agent:
        raise HTTPException(status_code=500, detail="ContentAgent not available")

    response = await agent.execute_skill(
        "generateQuizzes",
        context,
        topic=topic,
        num_questions=num_questions,
        difficulty=difficulty,
    )

    return AgentQueryResponse(
        success=response.success,
        data=response.data,
        agent=response.agent_name,
        skill=response.skill_name,
        error=response.error,
    )


@router.post("/code", response_model=AgentQueryResponse)
async def generate_code(
    request_text: str,
    language: str = "python",
    concept: Optional[str] = None,
    registry=Depends(ensure_agents_initialized),
):
    """
    Generate code examples.

    Convenience endpoint for the CodeAgent.generateCode skill.
    """
    context = AgentContext()
    agent = registry.get("CodeAgent")

    if not agent:
        raise HTTPException(status_code=500, detail="CodeAgent not available")

    response = await agent.execute_skill(
        "generateCode",
        context,
        message=request_text,
        language=language,
        concept=concept,
    )

    return AgentQueryResponse(
        success=response.success,
        data=response.data,
        agent=response.agent_name,
        skill=response.skill_name,
        error=response.error,
    )
