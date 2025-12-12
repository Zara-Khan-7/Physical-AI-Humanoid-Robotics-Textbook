/**
 * Agent API Service
 * =================
 *
 * Client-side service for interacting with the multi-agent system.
 * Provides methods for querying agents, executing skills, and running pipelines.
 */

const API_BASE_URL = 'https://zaraa7-physical-ai-textbook-api.hf.space/api/v1';

// Types
export interface AgentSkill {
  name: string;
  description: string;
  output_type: string;
  agent?: string;
}

export interface AgentInfo {
  name: string;
  description: string;
  skills: AgentSkill[];
  status: string;
}

export interface AgentQueryRequest {
  message: string;
  session_id?: string;
  user_id?: string;
  language?: string;
  user_profile?: Record<string, any>;
  conversation_history?: Array<{ role: string; content: string }>;
  force_agent?: string;
  force_skill?: string;
}

export interface AgentResponse {
  success: boolean;
  data: any;
  agent: string;
  skill: string;
  citations?: Array<Record<string, any>>;
  metadata?: Record<string, any>;
  error?: string;
}

export interface PipelineStep {
  agent: string;
  skill: string;
  kwargs?: Record<string, any>;
  use_previous_output?: boolean;
  stop_on_error?: boolean;
}

// Agent API Client
export const agentApi = {
  /**
   * List all available agents
   */
  async listAgents(): Promise<AgentInfo[]> {
    const response = await fetch(`${API_BASE_URL}/agents/`);
    if (!response.ok) {
      throw new Error('Failed to list agents');
    }
    return response.json();
  },

  /**
   * List all available skills across all agents
   */
  async listAllSkills(): Promise<AgentSkill[]> {
    const response = await fetch(`${API_BASE_URL}/agents/skills`);
    if (!response.ok) {
      throw new Error('Failed to list skills');
    }
    return response.json();
  },

  /**
   * Get information about a specific agent
   */
  async getAgentInfo(agentName: string): Promise<AgentInfo> {
    const response = await fetch(`${API_BASE_URL}/agents/${agentName}`);
    if (!response.ok) {
      throw new Error(`Agent '${agentName}' not found`);
    }
    return response.json();
  },

  /**
   * Send a query to the agent system (auto-routed to best agent)
   */
  async query(request: AgentQueryRequest): Promise<AgentResponse> {
    const response = await fetch(`${API_BASE_URL}/agents/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      throw new Error('Agent query failed');
    }
    return response.json();
  },

  /**
   * Execute a specific skill on a specific agent
   */
  async executeSkill(
    agentName: string,
    skillName: string,
    params: Record<string, any> = {},
    context: Partial<AgentQueryRequest> = {}
  ): Promise<AgentResponse> {
    const response = await fetch(`${API_BASE_URL}/agents/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        agent_name: agentName,
        skill_name: skillName,
        params,
        ...context,
      }),
    });
    if (!response.ok) {
      throw new Error(`Skill execution failed: ${agentName}.${skillName}`);
    }
    return response.json();
  },

  /**
   * Execute a multi-agent pipeline
   */
  async executePipeline(
    steps: PipelineStep[],
    context: Partial<AgentQueryRequest> = {}
  ): Promise<AgentResponse[]> {
    const response = await fetch(`${API_BASE_URL}/agents/pipeline`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        steps,
        ...context,
      }),
    });
    if (!response.ok) {
      throw new Error('Pipeline execution failed');
    }
    return response.json();
  },

  // Convenience methods for common operations

  /**
   * Translate content to Urdu
   */
  async translateToUrdu(
    content: string,
    chapterTitle?: string,
    style: string = 'educational'
  ): Promise<AgentResponse> {
    const response = await fetch(`${API_BASE_URL}/agents/translate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content,
        chapter_title: chapterTitle,
        style,
      }),
    });
    if (!response.ok) {
      throw new Error('Translation failed');
    }
    return response.json();
  },

  /**
   * Personalize content for a user
   */
  async personalizeContent(
    content: string,
    chapterTitle?: string,
    userProfile?: Record<string, any>
  ): Promise<AgentResponse> {
    const response = await fetch(`${API_BASE_URL}/agents/personalize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content,
        chapter_title: chapterTitle,
        user_profile: userProfile,
      }),
    });
    if (!response.ok) {
      throw new Error('Personalization failed');
    }
    return response.json();
  },

  /**
   * Generate quiz questions
   */
  async generateQuiz(
    topic: string,
    numQuestions: number = 5,
    difficulty?: string,
    userProfile?: Record<string, any>
  ): Promise<AgentResponse> {
    const response = await fetch(`${API_BASE_URL}/agents/quiz`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        topic,
        num_questions: numQuestions,
        difficulty,
        user_profile: userProfile,
      }),
    });
    if (!response.ok) {
      throw new Error('Quiz generation failed');
    }
    return response.json();
  },

  /**
   * Generate code examples
   */
  async generateCode(
    requestText: string,
    language: string = 'python',
    concept?: string
  ): Promise<AgentResponse> {
    const response = await fetch(`${API_BASE_URL}/agents/code`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        request_text: requestText,
        language,
        concept,
      }),
    });
    if (!response.ok) {
      throw new Error('Code generation failed');
    }
    return response.json();
  },
};

export default agentApi;
