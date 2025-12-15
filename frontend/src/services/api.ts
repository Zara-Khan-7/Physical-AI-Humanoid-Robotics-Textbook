/**
 * API client for textbook backend services.
 */

// Types for API requests and responses
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface Citation {
  chapter_id: string;
  chapter_title: string;
  section_id: string;
  section_title: string;
  path: string;
}

export interface ChatRequest {
  message: string;
  session_id: string;
  language?: 'en' | 'ur';
  history?: ChatMessage[];
  context?: string;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
  model: string;
  language: string;
}

export interface SearchRequest {
  query: string;
  limit?: number;
  language?: 'en' | 'ur';
  chapter_filter?: string;
}

export interface SearchResult {
  id: string;
  score: number;
  content: string;
  chapter_id: string;
  chapter_title: string;
  section_id: string;
  section_title: string;
  path: string;
}

export interface SearchResponse {
  results: SearchResult[];
  query: string;
  total: number;
}

export interface HealthStatus {
  qdrant: string;
  embeddings: string;
  gemini: string;
}

export interface HealthResponse {
  status: string;
  services: HealthStatus;
}

export interface ApiError {
  detail: string;
}

// API configuration
// Production API URL on HuggingFace Spaces
const API_BASE_URL = 'https://zaraa7-physical-ai-textbook-api.hf.space/api/v1';

/**
 * Custom error class for API errors.
 */
export class ApiClientError extends Error {
  status: number;
  detail: string;

  constructor(message: string, status: number, detail: string) {
    super(message);
    this.name = 'ApiClientError';
    this.status = status;
    this.detail = detail;
  }
}

/**
 * Safely parse JSON response, handling HTML error pages from HuggingFace
 */
async function safeJsonParse<T>(response: Response): Promise<T> {
  const text = await response.text();
  try {
    return JSON.parse(text);
  } catch {
    // If JSON parsing fails, it might be HTML (HF Space sleeping/error page)
    if (text.includes('<!DOCTYPE') || text.includes('<html') || text.includes('Your space')) {
      throw new ApiClientError(
        'Service temporarily unavailable',
        503,
        'The API service is waking up. Please try again in a moment.'
      );
    }
    throw new ApiClientError(
      'Invalid response',
      500,
      'Received invalid response from server'
    );
  }
}

/**
 * Make a fetch request with error handling.
 */
async function fetchWithErrorHandling<T>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    const data = await safeJsonParse<T | ApiError>(response);

    if (!response.ok) {
      const errorData = data as ApiError;
      throw new ApiClientError(
        `API request failed: ${response.status}`,
        response.status,
        errorData.detail || 'Unknown error'
      );
    }

    return data as T;
  } catch (error) {
    if (error instanceof ApiClientError) {
      throw error;
    }
    // Network error or other fetch error
    throw new ApiClientError(
      'Network error',
      0,
      'Unable to connect to the server. Please check your connection.'
    );
  }
}

/**
 * API client for the textbook backend.
 */
export const apiClient = {
  /**
   * Send a chat message and get an AI response.
   */
  async chat(request: ChatRequest): Promise<ChatResponse> {
    return fetchWithErrorHandling<ChatResponse>(`${API_BASE_URL}/chat`, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  /**
   * Search for relevant content in the textbook.
   */
  async search(request: SearchRequest): Promise<SearchResponse> {
    return fetchWithErrorHandling<SearchResponse>(`${API_BASE_URL}/search`, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  /**
   * Check the health status of backend services.
   */
  async health(): Promise<HealthResponse> {
    return fetchWithErrorHandling<HealthResponse>(`${API_BASE_URL}/health`);
  },

  /**
   * Check if the API is reachable.
   */
  async isAvailable(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      // Check if we got a valid JSON response
      const text = await response.text();
      try {
        JSON.parse(text);
        return response.ok;
      } catch {
        // HTML response means service is sleeping
        return false;
      }
    } catch {
      return false;
    }
  },
};

/**
 * LocalStorage helpers for conversation history.
 */
export const conversationStorage = {
  STORAGE_KEY: 'textbook_chat_history',
  MAX_MESSAGES: 50,

  /**
   * Get stored conversation history.
   */
  getHistory(): ChatMessage[] {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      if (stored) {
        return JSON.parse(stored);
      }
    } catch {
      console.warn('Failed to load chat history from localStorage');
    }
    return [];
  },

  /**
   * Save conversation history.
   */
  saveHistory(messages: ChatMessage[]): void {
    try {
      // Keep only the last MAX_MESSAGES
      const trimmed = messages.slice(-this.MAX_MESSAGES);
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(trimmed));
    } catch {
      console.warn('Failed to save chat history to localStorage');
    }
  },

  /**
   * Add a message to history.
   */
  addMessage(role: 'user' | 'assistant', content: string): ChatMessage[] {
    const history = this.getHistory();
    history.push({ role, content });
    this.saveHistory(history);
    return history;
  },

  /**
   * Clear conversation history.
   */
  clearHistory(): void {
    try {
      localStorage.removeItem(this.STORAGE_KEY);
    } catch {
      console.warn('Failed to clear chat history from localStorage');
    }
  },
};

/**
 * LocalStorage helpers for user preferences.
 */
export const preferencesStorage = {
  STORAGE_KEY: 'textbook_preferences',

  /**
   * Get stored preferences.
   */
  getPreferences(): Record<string, unknown> {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      if (stored) {
        return JSON.parse(stored);
      }
    } catch {
      console.warn('Failed to load preferences from localStorage');
    }
    return {};
  },

  /**
   * Save preferences.
   */
  savePreferences(prefs: Record<string, unknown>): void {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(prefs));
    } catch {
      console.warn('Failed to save preferences to localStorage');
    }
  },

  /**
   * Get a specific preference.
   */
  get<T>(key: string, defaultValue: T): T {
    const prefs = this.getPreferences();
    return (prefs[key] as T) ?? defaultValue;
  },

  /**
   * Set a specific preference.
   */
  set(key: string, value: unknown): void {
    const prefs = this.getPreferences();
    prefs[key] = value;
    this.savePreferences(prefs);
  },
};

export default apiClient;
