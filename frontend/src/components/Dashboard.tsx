import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import '../css/dashboard.css';

interface ProgressData {
  chaptersRead: number;
  totalChapters: number;
  quizzesTaken: number;
  avgQuizScore: number;
  personalizations: number;
  translations: number;
  lastActivity: string;
}

interface ActivityItem {
  id: string;
  type: 'read' | 'quiz' | 'personalize' | 'translate' | 'chat';
  title: string;
  timestamp: string;
}

const MOCK_PROGRESS: ProgressData = {
  chaptersRead: 5,
  totalChapters: 12,
  quizzesTaken: 3,
  avgQuizScore: 85,
  personalizations: 8,
  translations: 4,
  lastActivity: new Date().toISOString(),
};

const MOCK_ACTIVITIES: ActivityItem[] = [
  { id: '1', type: 'read', title: 'Introduction to Physical AI', timestamp: new Date(Date.now() - 3600000).toISOString() },
  { id: '2', type: 'personalize', title: 'Humanoid Robotics Fundamentals', timestamp: new Date(Date.now() - 7200000).toISOString() },
  { id: '3', type: 'quiz', title: 'Sensors & Perception Quiz', timestamp: new Date(Date.now() - 86400000).toISOString() },
  { id: '4', type: 'translate', title: 'Motion Control Chapter', timestamp: new Date(Date.now() - 172800000).toISOString() },
  { id: '5', type: 'chat', title: 'Asked about reinforcement learning', timestamp: new Date(Date.now() - 259200000).toISOString() },
];

export default function Dashboard(): JSX.Element {
  const { user, isAuthenticated } = useAuth();
  const [progress, setProgress] = useState<ProgressData>(MOCK_PROGRESS);
  const [activities, setActivities] = useState<ActivityItem[]>(MOCK_ACTIVITIES);
  const [activeTab, setActiveTab] = useState<'overview' | 'activity' | 'achievements'>('overview');

  // Calculate progress percentage
  const readingProgress = Math.round((progress.chaptersRead / progress.totalChapters) * 100);

  const formatTimeAgo = (timestamp: string): string => {
    const now = new Date();
    const then = new Date(timestamp);
    const diffMs = now.getTime() - then.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  const getActivityIcon = (type: ActivityItem['type']) => {
    switch (type) {
      case 'read':
        return (
          <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
            <path d="M21 5c-1.11-.35-2.33-.5-3.5-.5-1.95 0-4.05.4-5.5 1.5-1.45-1.1-3.55-1.5-5.5-1.5S2.45 4.9 1 6v14.65c0 .25.25.5.5.5.1 0 .15-.05.25-.05C3.1 20.45 5.05 20 6.5 20c1.95 0 4.05.4 5.5 1.5 1.35-.85 3.8-1.5 5.5-1.5 1.65 0 3.35.3 4.75 1.05.1.05.15.05.25.05.25 0 .5-.25.5-.5V6c-.6-.45-1.25-.75-2-1zm0 13.5c-1.1-.35-2.3-.5-3.5-.5-1.7 0-4.15.65-5.5 1.5V8c1.35-.85 3.8-1.5 5.5-1.5 1.2 0 2.4.15 3.5.5v11.5z"/>
          </svg>
        );
      case 'quiz':
        return (
          <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
            <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
          </svg>
        );
      case 'personalize':
        return (
          <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
          </svg>
        );
      case 'translate':
        return (
          <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
            <path d="M12.87 15.07l-2.54-2.51.03-.03c1.74-1.94 2.98-4.17 3.71-6.53H17V4h-7V2H8v2H1v2h11.17C11.5 7.92 10.44 9.75 9 11.35 8.07 10.32 7.3 9.19 6.69 8h-2c.73 1.63 1.73 3.17 2.98 4.56l-5.09 5.02L4 19l5-5 3.11 3.11.76-2.04zM18.5 10h-2L12 22h2l1.12-3h4.75L21 22h2l-4.5-12zm-2.62 7l1.62-4.33L19.12 17h-3.24z"/>
          </svg>
        );
      case 'chat':
        return (
          <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
            <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
          </svg>
        );
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="dashboard dashboard--guest">
        <div className="dashboard-guest-content">
          <div className="dashboard-guest-icon">
            <svg viewBox="0 0 24 24" width="64" height="64" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          </div>
          <h2>Sign in to view your dashboard</h2>
          <p>Track your learning progress, achievements, and activity history</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div className="dashboard-header-info">
          <div className="dashboard-avatar">
            <span>{user?.name?.charAt(0) || 'U'}</span>
            <div className="dashboard-avatar-ring" />
          </div>
          <div className="dashboard-user-info">
            <h1>Welcome back, {user?.name || 'Learner'}</h1>
            <p className="dashboard-subtitle">Continue your Physical AI journey</p>
          </div>
        </div>
        <div className="dashboard-header-stats">
          <div className="dashboard-stat-mini">
            <span className="dashboard-stat-value">{readingProgress}%</span>
            <span className="dashboard-stat-label">Complete</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="dashboard-tabs">
        <button
          className={`dashboard-tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`dashboard-tab ${activeTab === 'activity' ? 'active' : ''}`}
          onClick={() => setActiveTab('activity')}
        >
          Activity
        </button>
        <button
          className={`dashboard-tab ${activeTab === 'achievements' ? 'active' : ''}`}
          onClick={() => setActiveTab('achievements')}
        >
          Achievements
        </button>
      </div>

      {/* Content */}
      <div className="dashboard-content">
        {activeTab === 'overview' && (
          <>
            {/* Progress Cards */}
            <div className="dashboard-progress-grid">
              <div className="dashboard-card dashboard-card--primary">
                <div className="dashboard-card-header">
                  <h3>Reading Progress</h3>
                  <span className="dashboard-card-badge">{progress.chaptersRead}/{progress.totalChapters}</span>
                </div>
                <div className="dashboard-progress-bar-container">
                  <div className="dashboard-progress-bar">
                    <div
                      className="dashboard-progress-fill dashboard-progress-fill--primary"
                      style={{ width: `${readingProgress}%` }}
                    />
                  </div>
                  <span className="dashboard-progress-text">{readingProgress}% Complete</span>
                </div>
              </div>

              <div className="dashboard-card dashboard-card--secondary">
                <div className="dashboard-card-icon">
                  <svg viewBox="0 0 24 24" width="32" height="32" fill="currentColor">
                    <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
                  </svg>
                </div>
                <div className="dashboard-card-content">
                  <span className="dashboard-card-value">{progress.quizzesTaken}</span>
                  <span className="dashboard-card-label">Quizzes Taken</span>
                </div>
                <div className="dashboard-card-meta">
                  Avg: {progress.avgQuizScore}%
                </div>
              </div>

              <div className="dashboard-card dashboard-card--accent">
                <div className="dashboard-card-icon">
                  <svg viewBox="0 0 24 24" width="32" height="32" fill="currentColor">
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                  </svg>
                </div>
                <div className="dashboard-card-content">
                  <span className="dashboard-card-value">{progress.personalizations}</span>
                  <span className="dashboard-card-label">Personalizations</span>
                </div>
              </div>

              <div className="dashboard-card dashboard-card--success">
                <div className="dashboard-card-icon">
                  <svg viewBox="0 0 24 24" width="32" height="32" fill="currentColor">
                    <path d="M12.87 15.07l-2.54-2.51.03-.03c1.74-1.94 2.98-4.17 3.71-6.53H17V4h-7V2H8v2H1v2h11.17C11.5 7.92 10.44 9.75 9 11.35 8.07 10.32 7.3 9.19 6.69 8h-2c.73 1.63 1.73 3.17 2.98 4.56l-5.09 5.02L4 19l5-5 3.11 3.11.76-2.04zM18.5 10h-2L12 22h2l1.12-3h4.75L21 22h2l-4.5-12zm-2.62 7l1.62-4.33L19.12 17h-3.24z"/>
                  </svg>
                </div>
                <div className="dashboard-card-content">
                  <span className="dashboard-card-value">{progress.translations}</span>
                  <span className="dashboard-card-label">Translations</span>
                </div>
              </div>
            </div>

            {/* Recent Activity Preview */}
            <div className="dashboard-section">
              <div className="dashboard-section-header">
                <h3>Recent Activity</h3>
                <button
                  className="dashboard-link"
                  onClick={() => setActiveTab('activity')}
                >
                  View all
                </button>
              </div>
              <div className="dashboard-activity-list">
                {activities.slice(0, 3).map(activity => (
                  <div key={activity.id} className={`dashboard-activity-item dashboard-activity-item--${activity.type}`}>
                    <div className="dashboard-activity-icon">
                      {getActivityIcon(activity.type)}
                    </div>
                    <div className="dashboard-activity-content">
                      <span className="dashboard-activity-title">{activity.title}</span>
                      <span className="dashboard-activity-time">{formatTimeAgo(activity.timestamp)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {activeTab === 'activity' && (
          <div className="dashboard-section">
            <h3>Activity History</h3>
            <div className="dashboard-activity-list dashboard-activity-list--full">
              {activities.map(activity => (
                <div key={activity.id} className={`dashboard-activity-item dashboard-activity-item--${activity.type}`}>
                  <div className="dashboard-activity-icon">
                    {getActivityIcon(activity.type)}
                  </div>
                  <div className="dashboard-activity-content">
                    <span className="dashboard-activity-title">{activity.title}</span>
                    <span className="dashboard-activity-time">{formatTimeAgo(activity.timestamp)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'achievements' && (
          <div className="dashboard-section">
            <h3>Achievements</h3>
            <div className="dashboard-achievements-grid">
              <div className="dashboard-achievement dashboard-achievement--unlocked">
                <div className="dashboard-achievement-icon">
                  <svg viewBox="0 0 24 24" width="40" height="40" fill="currentColor">
                    <path d="M12 2L4 5v6.09c0 5.05 3.41 9.76 8 10.91 4.59-1.15 8-5.86 8-10.91V5l-8-3zm-1.06 13.54L7.4 12l1.41-1.41 2.12 2.12 4.24-4.24 1.41 1.41-5.64 5.66z"/>
                  </svg>
                </div>
                <span className="dashboard-achievement-title">First Steps</span>
                <span className="dashboard-achievement-desc">Read your first chapter</span>
              </div>
              <div className="dashboard-achievement dashboard-achievement--unlocked">
                <div className="dashboard-achievement-icon">
                  <svg viewBox="0 0 24 24" width="40" height="40" fill="currentColor">
                    <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
                  </svg>
                </div>
                <span className="dashboard-achievement-title">Quick Learner</span>
                <span className="dashboard-achievement-desc">Complete 5 chapters</span>
              </div>
              <div className="dashboard-achievement dashboard-achievement--locked">
                <div className="dashboard-achievement-icon">
                  <svg viewBox="0 0 24 24" width="40" height="40" fill="currentColor">
                    <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z"/>
                  </svg>
                </div>
                <span className="dashboard-achievement-title">Scholar</span>
                <span className="dashboard-achievement-desc">Complete all chapters</span>
              </div>
              <div className="dashboard-achievement dashboard-achievement--locked">
                <div className="dashboard-achievement-icon">
                  <svg viewBox="0 0 24 24" width="40" height="40" fill="currentColor">
                    <path d="M12.87 15.07l-2.54-2.51.03-.03c1.74-1.94 2.98-4.17 3.71-6.53H17V4h-7V2H8v2H1v2h11.17C11.5 7.92 10.44 9.75 9 11.35 8.07 10.32 7.3 9.19 6.69 8h-2c.73 1.63 1.73 3.17 2.98 4.56l-5.09 5.02L4 19l5-5 3.11 3.11.76-2.04z"/>
                  </svg>
                </div>
                <span className="dashboard-achievement-title">Bilingual</span>
                <span className="dashboard-achievement-desc">Translate 10 chapters</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
