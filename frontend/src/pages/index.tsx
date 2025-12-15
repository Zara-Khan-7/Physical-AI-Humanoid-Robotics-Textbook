import React, { useState, useEffect } from 'react';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import '../css/enhanced-theme.css';

// Chapter data with icons
const chapters = [
  {
    number: '01',
    title: 'Introduction to Physical AI',
    description: 'Discover what Physical AI is, its revolutionary history, and why humanoid robots are reshaping our world.',
    link: '/docs/intro',
    icon: '🤖',
  },
  {
    number: '02',
    title: 'Foundations of Robotics',
    description: 'Master the core concepts of kinematics, dynamics, and control theory that bring robots to life.',
    link: '/docs/foundations',
    icon: '⚙️',
  },
  {
    number: '03',
    title: 'Sensors & Perception',
    description: 'Explore how robots perceive reality through cameras, LiDAR, touch sensors, and sensor fusion.',
    link: '/docs/sensors',
    icon: '👁️',
  },
  {
    number: '04',
    title: 'Actuators & Movement',
    description: 'From electric motors to artificial muscles — understand the mechanics of robotic motion.',
    link: '/docs/actuators',
    icon: '💪',
  },
  {
    number: '05',
    title: 'AI Integration',
    description: 'Dive into machine learning, deep learning, and reinforcement learning powering intelligent robots.',
    link: '/docs/ai-integration',
    icon: '🧠',
  },
  {
    number: '06',
    title: 'Applications & Future',
    description: 'Real-world applications in healthcare, manufacturing, and the exciting future of humanoid robotics.',
    link: '/docs/applications',
    icon: '🚀',
  },
];

// AI Features
const aiFeatures = [
  {
    icon: '💬',
    title: 'Ask Questions',
    description: 'Get instant, accurate answers from textbook content',
  },
  {
    icon: '🎯',
    title: 'Personalized Learning',
    description: 'Content adapts to your skill level automatically',
  },
  {
    icon: '📚',
    title: 'Smart Citations',
    description: 'Every answer links back to source chapters',
  },
];

// ARIA Welcome Component
function AriaWelcome({ onClose, onChat }: { onClose: () => void; onChat: () => void }) {
  const [displayText, setDisplayText] = useState('');
  const [showCursor, setShowCursor] = useState(true);
  const fullText = "Hi! I'm ARIA, your AI learning companion. Ready to explore the fascinating world of Physical AI and Humanoid Robotics?";

  useEffect(() => {
    let index = 0;
    const timer = setInterval(() => {
      if (index <= fullText.length) {
        setDisplayText(fullText.slice(0, index));
        index++;
      } else {
        clearInterval(timer);
        setTimeout(() => setShowCursor(false), 1000);
      }
    }, 30);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="aria-welcome">
      <div className="aria-bubble">
        <button className="aria-close" onClick={onClose} aria-label="Close">
          ×
        </button>
        <div className="aria-header">
          <div className="aria-avatar">
            <div className="aria-face">
              <div className="aria-eye aria-eye--left"></div>
              <div className="aria-eye aria-eye--right"></div>
              <div className="aria-mouth"></div>
            </div>
          </div>
          <div>
            <div className="aria-name">ARIA</div>
            <div className="aria-title">AI Robotics Interactive Assistant</div>
          </div>
        </div>
        <div className="aria-message">
          <span className="typing-text">{displayText}</span>
          {showCursor && <span className="cursor"></span>}
        </div>
        <div className="aria-actions">
          <button className="aria-btn aria-btn--primary" onClick={onChat}>
            Start Chat
          </button>
          <button className="aria-btn aria-btn--secondary" onClick={onClose}>
            Later
          </button>
        </div>
      </div>
    </div>
  );
}

// Particles Background
function Particles() {
  return (
    <div className="particles-container">
      {[...Array(12)].map((_, i) => (
        <div key={i} className="particle" />
      ))}
    </div>
  );
}

// Orbs Background
function Orbs() {
  return (
    <>
      <div className="orb orb-1" />
      <div className="orb orb-2" />
      <div className="orb orb-3" />
    </>
  );
}

// Hero Section
function HeroSection() {
  return (
    <header className="hero--enhanced">
      <Particles />
      <Orbs />
      <div className="hero-content">
        <h1 className="hero-title">Physical AI & Humanoid Robotics</h1>
        <p className="hero-subtitle">Essentials for the AI-Native Era</p>
        <p className="hero-tagline">
          An interactive, AI-powered textbook exploring the cutting-edge world of
          intelligent machines and humanoid robots
        </p>
        <Link to="/docs/intro" className="cta-button">
          <span>Begin Your Journey</span>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z" />
          </svg>
        </Link>
      </div>
    </header>
  );
}

// Chapters Section
function ChaptersSection() {
  return (
    <section className="chapters-section">
      <div className="container">
        <h2 className="section-title">Explore the Chapters</h2>
        <div className="chapters-grid">
          {chapters.map((chapter, idx) => (
            <Link key={idx} to={chapter.link} className="chapter-card">
              <span className="chapter-number">{chapter.number}</span>
              <div className="chapter-icon">{chapter.icon}</div>
              <h3 className="chapter-title">{chapter.title}</h3>
              <p className="chapter-description">{chapter.description}</p>
              <span className="chapter-link">
                Explore Chapter
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z" />
                </svg>
              </span>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}

// AI Features Section
function AIFeaturesSection() {
  return (
    <section className="ai-features-section">
      <div className="container">
        <h2 className="section-title">AI-Powered Learning</h2>
        <p style={{ textAlign: 'center', color: 'rgba(255,255,255,0.7)', marginBottom: '3rem', fontSize: '1.1rem' }}>
          Meet ARIA — your intelligent companion for exploring Physical AI
        </p>
        <div className="ai-features-grid">
          {aiFeatures.map((feature, idx) => (
            <div key={idx} className="ai-feature-card">
              <div className="ai-feature-icon">{feature.icon}</div>
              <h3 className="ai-feature-title">{feature.title}</h3>
              <p className="ai-feature-desc">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// Main Component
export default function Home(): JSX.Element {
  const { siteConfig } = useDocusaurusContext();
  const [showAria, setShowAria] = useState(false);
  const [ariaDismissed, setAriaDismissed] = useState(false);

  useEffect(() => {
    // Check if ARIA was already dismissed this session
    const dismissed = sessionStorage.getItem('aria_dismissed');
    if (dismissed) {
      setAriaDismissed(true);
      return;
    }

    // Show ARIA after a short delay
    const timer = setTimeout(() => {
      setShowAria(true);
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  const handleAriaClose = () => {
    setShowAria(false);
    setAriaDismissed(true);
    sessionStorage.setItem('aria_dismissed', 'true');
  };

  const handleAriaChat = () => {
    setShowAria(false);
    setAriaDismissed(true);
    sessionStorage.setItem('aria_dismissed', 'true');
    // Find and click the chatbot toggle
    const chatToggle = document.querySelector('.chatbot-toggle') as HTMLButtonElement;
    if (chatToggle) {
      chatToggle.click();
    }
  };

  return (
    <Layout
      title="Welcome"
      description="Physical AI and Humanoid Robotics - An AI-Native Textbook with ARIA, your intelligent learning companion">
      <main>
        <HeroSection />
        <ChaptersSection />
        <AIFeaturesSection />
      </main>
      {showAria && !ariaDismissed && (
        <AriaWelcome onClose={handleAriaClose} onChat={handleAriaChat} />
      )}
    </Layout>
  );
}
