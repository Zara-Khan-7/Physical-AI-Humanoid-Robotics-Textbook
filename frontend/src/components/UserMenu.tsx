import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import AuthModal from './AuthModal';
import '../css/auth.css';

export default function UserMenu(): JSX.Element {
  const { user, isAuthenticated, isLoading, signOut } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState<'signin' | 'signup'>('signin');
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSignInClick = () => {
    setAuthMode('signin');
    setShowAuthModal(true);
  };

  const handleSignUpClick = () => {
    setAuthMode('signup');
    setShowAuthModal(true);
  };

  const handleSignOut = async () => {
    await signOut();
    setShowDropdown(false);
  };

  if (isLoading) {
    return <div className="user-menu-loading">...</div>;
  }

  if (!isAuthenticated) {
    return (
      <>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button className="sign-in-btn" onClick={handleSignInClick}>
            Sign In
          </button>
        </div>
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
          initialMode={authMode}
        />
      </>
    );
  }

  const initials = user?.name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  return (
    <>
      <div className="user-dropdown" ref={dropdownRef}>
        <button
          className="user-menu-btn"
          onClick={() => setShowDropdown(!showDropdown)}
          aria-expanded={showDropdown}
          aria-haspopup="true"
        >
          <span className="user-avatar">{initials}</span>
          <span>{user?.name.split(' ')[0]}</span>
        </button>

        {showDropdown && (
          <div className="user-dropdown-menu">
            <div className="user-dropdown-header">
              <strong>{user?.name}</strong>
              <span>{user?.email}</span>
            </div>
            <div>
              <div style={{ padding: '0.5rem 1rem', fontSize: '0.8rem', color: 'var(--ifm-color-emphasis-600)' }}>
                <div>Software: {user?.software_experience}</div>
                <div>Hardware: {user?.hardware_experience}</div>
              </div>
            </div>
            <button className="user-dropdown-item user-dropdown-item--danger" onClick={handleSignOut}>
              Sign Out
            </button>
          </div>
        )}
      </div>
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        initialMode={authMode}
      />
    </>
  );
}
