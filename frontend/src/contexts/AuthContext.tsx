import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

// Types
export interface User {
  id: number;
  email: string;
  name: string;
  software_experience: 'beginner' | 'intermediate' | 'advanced';
  hardware_experience: 'beginner' | 'intermediate' | 'advanced';
  learning_goals: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (data: SignUpData) => Promise<void>;
  signOut: () => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<void>;
}

interface SignUpData {
  email: string;
  password: string;
  name: string;
  software_experience: 'beginner' | 'intermediate' | 'advanced';
  hardware_experience: 'beginner' | 'intermediate' | 'advanced';
  learning_goals: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// API Base URL
const API_BASE_URL = 'https://zaraa7-physical-ai-textbook-api.hf.space/api/v1';

// Token storage
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';

function getStoredToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

function setStoredToken(token: string): void {
  try {
    localStorage.setItem(TOKEN_KEY, token);
  } catch {
    console.warn('Failed to store token');
  }
}

function removeStoredToken(): void {
  try {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  } catch {
    console.warn('Failed to remove token');
  }
}

function getStoredUser(): User | null {
  try {
    const stored = localStorage.getItem(USER_KEY);
    return stored ? JSON.parse(stored) : null;
  } catch {
    return null;
  }
}

function setStoredUser(user: User): void {
  try {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  } catch {
    console.warn('Failed to store user');
  }
}

// Helper function to safely parse JSON response
async function safeJsonParse(response: Response): Promise<any> {
  const text = await response.text();
  try {
    return JSON.parse(text);
  } catch {
    // If JSON parsing fails, it might be HTML (HF Space sleeping/error page)
    if (text.includes('<!DOCTYPE') || text.includes('<html') || text.includes('Your space')) {
      throw new Error('SERVER_SLEEPING');
    }
    throw new Error('Invalid response from server');
  }
}

// Helper function to fetch with retry for HuggingFace cold starts
async function fetchWithRetry(
  url: string,
  options: RequestInit,
  maxRetries: number = 6,
  delayMs: number = 5000
): Promise<Response> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const response = await fetch(url, options);

      // Check if we got an HTML response (server sleeping)
      const contentType = response.headers.get('content-type');
      if (contentType && !contentType.includes('application/json')) {
        // Server might be sleeping, wait and retry
        if (attempt < maxRetries - 1) {
          await new Promise(resolve => setTimeout(resolve, delayMs));
          continue;
        }
      }

      return response;
    } catch (error) {
      lastError = error instanceof Error ? error : new Error('Network error');
      if (attempt < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, delayMs));
      }
    }
  }

  throw lastError || new Error('Failed to connect after multiple attempts');
}

export function AuthProvider({ children }: { children: React.ReactNode }): JSX.Element {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load user from storage on mount
  useEffect(() => {
    const loadUser = async () => {
      const token = getStoredToken();
      const storedUser = getStoredUser();

      if (token && storedUser) {
        // Immediately use stored user to avoid UI flicker
        setUser(storedUser);
        setIsLoading(false);

        // Then verify token is still valid in background
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 5000); // 5s timeout

          const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
            signal: controller.signal,
          });

          clearTimeout(timeoutId);

          if (response.ok) {
            const userData = await safeJsonParse(response);
            setUser(userData);
            setStoredUser(userData);
          } else {
            // Token invalid, clear storage
            removeStoredToken();
            setUser(null);
          }
        } catch {
          // API unavailable, keep using stored user (already set)
        }
      } else {
        setIsLoading(false);
      }
    };

    loadUser();
  }, []);

  const signIn = useCallback(async (email: string, password: string) => {
    try {
      const response = await fetchWithRetry(
        `${API_BASE_URL}/auth/signin`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email, password }),
        },
        6, // 6 retries
        5000 // 5 seconds between retries
      );

      const data = await safeJsonParse(response);

      if (!response.ok) {
        throw new Error(data.detail || 'Sign in failed');
      }

      setUser(data.user);
      setStoredToken(data.token);
      setStoredUser(data.user);
    } catch (error) {
      if (error instanceof Error && error.message === 'SERVER_SLEEPING') {
        throw new Error('Server is waking up. Please wait 30-60 seconds and try again.');
      }
      throw error;
    }
  }, []);

  const signUp = useCallback(async (data: SignUpData) => {
    try {
      const response = await fetchWithRetry(
        `${API_BASE_URL}/auth/signup`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data),
        },
        6, // 6 retries
        5000 // 5 seconds between retries
      );

      const result = await safeJsonParse(response);

      if (!response.ok) {
        throw new Error(result.detail || 'Sign up failed');
      }

      setUser(result.user);
      setStoredToken(result.token);
      setStoredUser(result.user);
    } catch (error) {
      if (error instanceof Error && error.message === 'SERVER_SLEEPING') {
        throw new Error('Server is waking up. Please wait 30-60 seconds and try again.');
      }
      throw error;
    }
  }, []);

  const signOut = useCallback(async () => {
    const token = getStoredToken();
    if (token) {
      try {
        await fetch(`${API_BASE_URL}/auth/signout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
      } catch {
        // Ignore errors during sign out
      }
    }

    setUser(null);
    removeStoredToken();
  }, []);

  const updateProfile = useCallback(async (data: Partial<User>) => {
    const token = getStoredToken();
    if (!token) {
      throw new Error('Not authenticated');
    }

    const response = await fetch(`${API_BASE_URL}/auth/profile`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });

    const updatedUser = await safeJsonParse(response);

    if (!response.ok) {
      throw new Error(updatedUser.detail || 'Update failed');
    }

    setUser(updatedUser);
    setStoredUser(updatedUser);
  }, []);

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    signIn,
    signUp,
    signOut,
    updateProfile,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
