import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import AuthModal from './AuthModal';
import '../css/chapter-actions.css';

interface ChapterActionsProps {
  chapterId: string;
  chapterTitle: string;
}

export default function ChapterActions({ chapterId, chapterTitle }: ChapterActionsProps): JSX.Element {
  const { user, isAuthenticated } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isPersonalizing, setIsPersonalizing] = useState(false);
  const [isTranslating, setIsTranslating] = useState(false);
  const [personalizedContent, setPersonalizedContent] = useState<string | null>(null);
  const [translatedContent, setTranslatedContent] = useState<string | null>(null);
  const [showPersonalized, setShowPersonalized] = useState(false);
  const [showTranslated, setShowTranslated] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const API_BASE_URL = 'https://zaraa7-physical-ai-textbook-api.hf.space/api/v1';

  const handlePersonalize = async () => {
    if (!isAuthenticated) {
      setShowAuthModal(true);
      return;
    }

    if (personalizedContent) {
      setShowPersonalized(!showPersonalized);
      return;
    }

    setIsPersonalizing(true);
    setError(null);

    try {
      // Get the page content
      const pageContent = document.querySelector('.markdown')?.textContent || '';

      // Call the API to personalize content based on user background
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: `Please provide a personalized introduction and key concepts summary for this chapter content, tailored for someone with ${user?.software_experience} software experience and ${user?.hardware_experience} hardware experience. Focus on explaining concepts at their level. The user's learning goals are: ${user?.learning_goals || 'General understanding'}.

Chapter: ${chapterTitle}

Be concise and practical. Provide:
1. A personalized welcome (2-3 sentences)
2. Key concepts explained at their level (bullet points)
3. What to focus on based on their background
4. Suggested learning approach`,
          session_id: `personalize-${chapterId}-${user?.id}`,
          language: 'en',
          context: pageContent.slice(0, 2000),
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to personalize content');
      }

      const data = await response.json();
      setPersonalizedContent(data.answer);
      setShowPersonalized(true);
    } catch (err) {
      setError('Failed to personalize content. Please try again.');
      console.error('Personalization error:', err);
    } finally {
      setIsPersonalizing(false);
    }
  };

  const handleTranslate = async () => {
    if (!isAuthenticated) {
      setShowAuthModal(true);
      return;
    }

    if (translatedContent) {
      setShowTranslated(!showTranslated);
      return;
    }

    setIsTranslating(true);
    setError(null);

    try {
      // Get the page content
      const pageContent = document.querySelector('.markdown')?.textContent || '';

      // Call the API to translate content to Urdu
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: `Please translate the following chapter summary into Urdu. Provide a clear, educational translation that maintains technical accuracy while being accessible to Urdu-speaking students.

Chapter: ${chapterTitle}

Provide:
1. Chapter title in Urdu
2. A comprehensive summary of key concepts in Urdu (about 300-400 words)
3. Key terms with both English and Urdu versions
4. Study tips in Urdu

Make sure the translation is natural and educational.`,
          session_id: `translate-${chapterId}-${user?.id}`,
          language: 'ur',
          context: pageContent.slice(0, 2000),
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to translate content');
      }

      const data = await response.json();
      setTranslatedContent(data.answer);
      setShowTranslated(true);
    } catch (err) {
      setError('Failed to translate content. Please try again.');
      console.error('Translation error:', err);
    } finally {
      setIsTranslating(false);
    }
  };

  return (
    <>
      <div className="chapter-actions">
        <div className="chapter-actions-buttons">
          <button
            className={`chapter-action-btn chapter-action-btn--personalize ${showPersonalized ? 'active' : ''}`}
            onClick={handlePersonalize}
            disabled={isPersonalizing}
          >
            {isPersonalizing ? (
              <span className="chapter-action-loading" />
            ) : (
              <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
              </svg>
            )}
            {isPersonalizing ? 'Personalizing...' : showPersonalized ? 'Hide Personalized' : 'Personalize for Me'}
          </button>

          <button
            className={`chapter-action-btn chapter-action-btn--translate ${showTranslated ? 'active' : ''}`}
            onClick={handleTranslate}
            disabled={isTranslating}
          >
            {isTranslating ? (
              <span className="chapter-action-loading" />
            ) : (
              <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                <path d="M12.87 15.07l-2.54-2.51.03-.03c1.74-1.94 2.98-4.17 3.71-6.53H17V4h-7V2H8v2H1v2h11.17C11.5 7.92 10.44 9.75 9 11.35 8.07 10.32 7.3 9.19 6.69 8h-2c.73 1.63 1.73 3.17 2.98 4.56l-5.09 5.02L4 19l5-5 3.11 3.11.76-2.04zM18.5 10h-2L12 22h2l1.12-3h4.75L21 22h2l-4.5-12zm-2.62 7l1.62-4.33L19.12 17h-3.24z"/>
              </svg>
            )}
            {isTranslating ? 'Translating...' : showTranslated ? 'Hide Urdu' : 'اردو میں ترجمہ'}
          </button>
        </div>

        {!isAuthenticated && (
          <p className="chapter-actions-hint">
            Sign in to personalize content and access translations
          </p>
        )}

        {error && (
          <div className="chapter-actions-error">{error}</div>
        )}

        {showPersonalized && personalizedContent && (
          <div className="chapter-actions-content chapter-actions-content--personalized">
            <h4>
              <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
              </svg>
              Personalized for You
            </h4>
            <div className="chapter-actions-text">{personalizedContent}</div>
          </div>
        )}

        {showTranslated && translatedContent && (
          <div className="chapter-actions-content chapter-actions-content--translated" dir="rtl">
            <h4>
              <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                <path d="M12.87 15.07l-2.54-2.51.03-.03c1.74-1.94 2.98-4.17 3.71-6.53H17V4h-7V2H8v2H1v2h11.17C11.5 7.92 10.44 9.75 9 11.35 8.07 10.32 7.3 9.19 6.69 8h-2c.73 1.63 1.73 3.17 2.98 4.56l-5.09 5.02L4 19l5-5 3.11 3.11.76-2.04zM18.5 10h-2L12 22h2l1.12-3h4.75L21 22h2l-4.5-12zm-2.62 7l1.62-4.33L19.12 17h-3.24z"/>
              </svg>
              اردو ترجمہ
            </h4>
            <div className="chapter-actions-text">{translatedContent}</div>
          </div>
        )}
      </div>

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        initialMode="signin"
      />
    </>
  );
}
