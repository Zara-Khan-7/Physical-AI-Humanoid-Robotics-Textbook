import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import AuthModal from './AuthModal';
import { agentApi } from '../services/agentApi';
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
  const [agentInfo, setAgentInfo] = useState<{ agent: string; skill: string } | null>(null);

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

      // Use the PersonalizationAgent via the agent API
      const response = await agentApi.executeSkill(
        'PersonalizationAgent',
        'personalizeContent',
        {
          content: pageContent.slice(0, 2000),
          chapter_title: chapterTitle,
          message: `Personalize this chapter for me`,
        },
        {
          user_profile: {
            software_experience: user?.software_experience || 'beginner',
            hardware_experience: user?.hardware_experience || 'beginner',
            learning_goals: user?.learning_goals || 'General understanding',
          },
          session_id: `personalize-${chapterId}-${user?.id}`,
          language: 'en',
        }
      );

      if (response.success && response.data) {
        setPersonalizedContent(response.data.personalized_content || response.data);
        setAgentInfo({ agent: response.agent, skill: response.skill });
        setShowPersonalized(true);
      } else {
        throw new Error(response.error || 'Failed to personalize content');
      }
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

      // Use the TranslationAgent via the agent API
      const response = await agentApi.executeSkill(
        'TranslationAgent',
        'translateToUrdu',
        {
          content: pageContent.slice(0, 3000),
          chapter_title: chapterTitle,
          translation_style: 'educational',
        },
        {
          session_id: `translate-${chapterId}-${user?.id}`,
          language: 'ur',
        }
      );

      if (response.success && response.data) {
        setTranslatedContent(response.data.translation || response.data);
        setAgentInfo({ agent: response.agent, skill: response.skill });
        setShowTranslated(true);
      } else {
        throw new Error(response.error || 'Failed to translate content');
      }
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
              {agentInfo && (
                <span className="agent-badge">via {agentInfo.agent}</span>
              )}
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
              {agentInfo && (
                <span className="agent-badge" dir="ltr">via {agentInfo.agent}</span>
              )}
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
