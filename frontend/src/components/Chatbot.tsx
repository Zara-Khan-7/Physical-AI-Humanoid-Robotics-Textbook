import React, { useState, useRef, useEffect, useCallback } from 'react';
import { apiClient, conversationStorage, ChatMessage, Citation } from '../services/api';
import '../css/chatbot.css';

// Icons as SVG components
const ChatIcon = () => (
  <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z" />
  </svg>
);

const CloseIcon = () => (
  <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
  </svg>
);

const SendIcon = () => (
  <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
  </svg>
);

const ClearIcon = () => (
  <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z" />
  </svg>
);

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  isLoading?: boolean;
  error?: string;
}

interface ChatbotProps {
  language?: 'en' | 'ur';
}

const SUGGESTED_QUESTIONS = [
  'What is Physical AI?',
  'How do robots maintain balance?',
  'What sensors do humanoid robots use?',
  'Explain reinforcement learning',
];

const SUGGESTED_QUESTIONS_UR = [
  'فزیکل اے آئی کیا ہے؟',
  'روبوٹ توازن کیسے برقرار رکھتے ہیں؟',
  'ہیومنائڈ روبوٹ کون سے سینسر استعمال کرتے ہیں؟',
];

export default function Chatbot({ language = 'en' }: ChatbotProps): JSX.Element {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'loading'>('loading');

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Load history on mount
  useEffect(() => {
    const history = conversationStorage.getHistory();
    if (history.length > 0) {
      setMessages(
        history.map((msg, idx) => ({
          id: `history-${idx}`,
          role: msg.role,
          content: msg.content,
        }))
      );
    }
  }, []);

  // Check API connection
  useEffect(() => {
    const checkConnection = async () => {
      setConnectionStatus('loading');
      const available = await apiClient.isAvailable();
      setConnectionStatus(available ? 'connected' : 'disconnected');
    };
    checkConnection();
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
    }
  }, [isOpen]);

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text.trim(),
    };

    // Add user message
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Save to localStorage
    conversationStorage.addMessage('user', text.trim());

    // Add loading message
    const loadingId = `loading-${Date.now()}`;
    setMessages(prev => [
      ...prev,
      { id: loadingId, role: 'assistant', content: '', isLoading: true },
    ]);

    try {
      // Get conversation history for context
      const history: ChatMessage[] = messages
        .filter(m => !m.isLoading && !m.error)
        .map(m => ({ role: m.role, content: m.content }));

      const response = await apiClient.chat({
        query: text.trim(),
        language,
        history: history.slice(-10), // Last 10 messages for context
      });

      // Replace loading message with response
      setMessages(prev =>
        prev.map(m =>
          m.id === loadingId
            ? {
                id: `assistant-${Date.now()}`,
                role: 'assistant',
                content: response.answer,
                citations: response.citations,
              }
            : m
        )
      );

      // Save to localStorage
      conversationStorage.addMessage('assistant', response.answer);
    } catch (error) {
      // Replace loading message with error
      setMessages(prev =>
        prev.map(m =>
          m.id === loadingId
            ? {
                id: `error-${Date.now()}`,
                role: 'assistant',
                content: '',
                error: error instanceof Error ? error.message : 'An error occurred',
              }
            : m
        )
      );
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, language, messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  const handleClear = () => {
    setMessages([]);
    conversationStorage.clearHistory();
  };

  const handleSuggestionClick = (question: string) => {
    sendMessage(question);
  };

  const suggestions = language === 'ur' ? SUGGESTED_QUESTIONS_UR : SUGGESTED_QUESTIONS;

  return (
    <div className="chatbot-container">
      {/* Toggle Button */}
      <button
        className="chatbot-toggle"
        onClick={() => setIsOpen(!isOpen)}
        aria-label={isOpen ? 'Close chat' : 'Open chat'}
      >
        {isOpen ? <CloseIcon /> : <ChatIcon />}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="chatbot-window">
          {/* Header */}
          <div className="chatbot-header">
            <h3>{language === 'ur' ? 'ٹیکسٹ بک اسسٹنٹ' : 'Textbook Assistant'}</h3>
            <div className="chatbot-header-actions">
              <button onClick={handleClear} aria-label="Clear chat">
                <ClearIcon />
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="chatbot-messages">
            {messages.length === 0 && (
              <>
                <div className="chatbot-welcome">
                  <h4>
                    {language === 'ur'
                      ? 'خوش آمدید!'
                      : 'Welcome!'}
                  </h4>
                  <p>
                    {language === 'ur'
                      ? 'ٹیکسٹ بک کے بارے میں کوئی سوال پوچھیں'
                      : 'Ask me anything about the textbook content'}
                  </p>
                </div>
                <div className="chatbot-suggestions">
                  {suggestions.map((q, idx) => (
                    <button
                      key={idx}
                      className="chatbot-suggestion"
                      onClick={() => handleSuggestionClick(q)}
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </>
            )}

            {messages.map(message => (
              <div
                key={message.id}
                className={`chatbot-message chatbot-message--${message.role}`}
              >
                {message.isLoading ? (
                  <div className="chatbot-message--loading">
                    <span />
                    <span />
                    <span />
                  </div>
                ) : message.error ? (
                  <div className="chatbot-error">{message.error}</div>
                ) : (
                  <>
                    <div>{message.content}</div>
                    {message.citations && message.citations.length > 0 && (
                      <div className="chatbot-citations">
                        {message.citations.map((citation, idx) => (
                          <a
                            key={idx}
                            href={`/${citation.chapter_id.replace('-en', '').replace('-ur', '')}#${citation.section_id}`}
                            className="citation"
                          >
                            {citation.chapter_title}: {citation.section_title}
                          </a>
                        ))}
                      </div>
                    )}
                  </>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Status */}
          <div className="chatbot-status">
            <span
              className={`chatbot-status-dot chatbot-status-dot--${connectionStatus}`}
            />
            <span>
              {connectionStatus === 'connected'
                ? language === 'ur'
                  ? 'منسلک'
                  : 'Connected'
                : connectionStatus === 'loading'
                ? language === 'ur'
                  ? 'جڑ رہا ہے...'
                  : 'Connecting...'
                : language === 'ur'
                ? 'منقطع'
                : 'Disconnected'}
            </span>
          </div>

          {/* Input */}
          <form className="chatbot-input" onSubmit={handleSubmit}>
            <textarea
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                language === 'ur'
                  ? 'اپنا سوال یہاں لکھیں...'
                  : 'Type your question...'
              }
              rows={1}
              disabled={isLoading || connectionStatus === 'disconnected'}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading || connectionStatus === 'disconnected'}
              aria-label="Send message"
            >
              <SendIcon />
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
