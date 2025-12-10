import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import '../css/auth.css';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialMode?: 'signin' | 'signup';
}

type ExperienceLevel = 'beginner' | 'intermediate' | 'advanced';

interface SignUpFormData {
  email: string;
  password: string;
  confirmPassword: string;
  name: string;
  software_experience: ExperienceLevel;
  hardware_experience: ExperienceLevel;
  learning_goals: string;
}

const EXPERIENCE_OPTIONS = [
  { value: 'beginner', label: 'Beginner', description: 'New to the topic' },
  { value: 'intermediate', label: 'Intermediate', description: 'Some experience' },
  { value: 'advanced', label: 'Advanced', description: 'Extensive experience' },
];

export default function AuthModal({ isOpen, onClose, initialMode = 'signin' }: AuthModalProps): JSX.Element | null {
  const { signIn, signUp } = useAuth();
  const [mode, setMode] = useState<'signin' | 'signup'>(initialMode);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<1 | 2>(1); // For multi-step signup

  // Sign In form state
  const [signInEmail, setSignInEmail] = useState('');
  const [signInPassword, setSignInPassword] = useState('');

  // Sign Up form state
  const [signUpData, setSignUpData] = useState<SignUpFormData>({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
    software_experience: 'beginner',
    hardware_experience: 'beginner',
    learning_goals: '',
  });

  if (!isOpen) return null;

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await signIn(signInEmail, signInPassword);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sign in failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignUpStep1 = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (signUpData.password !== signUpData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (signUpData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setStep(2);
  };

  const handleSignUpStep2 = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await signUp({
        email: signUpData.email,
        password: signUpData.password,
        name: signUpData.name,
        software_experience: signUpData.software_experience,
        hardware_experience: signUpData.hardware_experience,
        learning_goals: signUpData.learning_goals,
      });
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sign up failed');
    } finally {
      setIsLoading(false);
    }
  };

  const switchMode = (newMode: 'signin' | 'signup') => {
    setMode(newMode);
    setStep(1);
    setError(null);
  };

  return (
    <div className="auth-modal-overlay" onClick={onClose}>
      <div className="auth-modal" onClick={(e) => e.stopPropagation()}>
        <button className="auth-modal-close" onClick={onClose} aria-label="Close">
          &times;
        </button>

        {mode === 'signin' ? (
          <>
            <h2>Sign In</h2>
            <p className="auth-modal-subtitle">Welcome back! Sign in to personalize your learning.</p>

            <form onSubmit={handleSignIn}>
              <div className="auth-form-group">
                <label htmlFor="signin-email">Email</label>
                <input
                  id="signin-email"
                  type="email"
                  value={signInEmail}
                  onChange={(e) => setSignInEmail(e.target.value)}
                  required
                  placeholder="your@email.com"
                />
              </div>

              <div className="auth-form-group">
                <label htmlFor="signin-password">Password</label>
                <input
                  id="signin-password"
                  type="password"
                  value={signInPassword}
                  onChange={(e) => setSignInPassword(e.target.value)}
                  required
                  placeholder="Your password"
                />
              </div>

              {error && <div className="auth-error">{error}</div>}

              <button type="submit" className="auth-submit-btn" disabled={isLoading}>
                {isLoading ? 'Signing in...' : 'Sign In'}
              </button>
            </form>

            <div className="auth-switch">
              Don't have an account?{' '}
              <button onClick={() => switchMode('signup')}>Sign Up</button>
            </div>
          </>
        ) : (
          <>
            <h2>Create Account</h2>
            {step === 1 ? (
              <>
                <p className="auth-modal-subtitle">Step 1 of 2: Account details</p>

                <form onSubmit={handleSignUpStep1}>
                  <div className="auth-form-group">
                    <label htmlFor="signup-name">Full Name</label>
                    <input
                      id="signup-name"
                      type="text"
                      value={signUpData.name}
                      onChange={(e) => setSignUpData({ ...signUpData, name: e.target.value })}
                      required
                      placeholder="Your name"
                    />
                  </div>

                  <div className="auth-form-group">
                    <label htmlFor="signup-email">Email</label>
                    <input
                      id="signup-email"
                      type="email"
                      value={signUpData.email}
                      onChange={(e) => setSignUpData({ ...signUpData, email: e.target.value })}
                      required
                      placeholder="your@email.com"
                    />
                  </div>

                  <div className="auth-form-group">
                    <label htmlFor="signup-password">Password</label>
                    <input
                      id="signup-password"
                      type="password"
                      value={signUpData.password}
                      onChange={(e) => setSignUpData({ ...signUpData, password: e.target.value })}
                      required
                      placeholder="At least 6 characters"
                      minLength={6}
                    />
                  </div>

                  <div className="auth-form-group">
                    <label htmlFor="signup-confirm-password">Confirm Password</label>
                    <input
                      id="signup-confirm-password"
                      type="password"
                      value={signUpData.confirmPassword}
                      onChange={(e) => setSignUpData({ ...signUpData, confirmPassword: e.target.value })}
                      required
                      placeholder="Confirm your password"
                    />
                  </div>

                  {error && <div className="auth-error">{error}</div>}

                  <button type="submit" className="auth-submit-btn">
                    Continue
                  </button>
                </form>
              </>
            ) : (
              <>
                <p className="auth-modal-subtitle">Step 2 of 2: Tell us about your background</p>
                <p className="auth-modal-info">This helps us personalize the textbook content for you.</p>

                <form onSubmit={handleSignUpStep2}>
                  <div className="auth-form-group">
                    <label>Software Experience</label>
                    <p className="auth-form-hint">Your experience with programming and software development</p>
                    <div className="auth-radio-group">
                      {EXPERIENCE_OPTIONS.map((option) => (
                        <label key={option.value} className="auth-radio-option">
                          <input
                            type="radio"
                            name="software_experience"
                            value={option.value}
                            checked={signUpData.software_experience === option.value}
                            onChange={(e) => setSignUpData({
                              ...signUpData,
                              software_experience: e.target.value as ExperienceLevel
                            })}
                          />
                          <span className="auth-radio-content">
                            <strong>{option.label}</strong>
                            <span>{option.description}</span>
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>

                  <div className="auth-form-group">
                    <label>Hardware Experience</label>
                    <p className="auth-form-hint">Your experience with electronics, robotics, or mechanical systems</p>
                    <div className="auth-radio-group">
                      {EXPERIENCE_OPTIONS.map((option) => (
                        <label key={option.value} className="auth-radio-option">
                          <input
                            type="radio"
                            name="hardware_experience"
                            value={option.value}
                            checked={signUpData.hardware_experience === option.value}
                            onChange={(e) => setSignUpData({
                              ...signUpData,
                              hardware_experience: e.target.value as ExperienceLevel
                            })}
                          />
                          <span className="auth-radio-content">
                            <strong>{option.label}</strong>
                            <span>{option.description}</span>
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>

                  <div className="auth-form-group">
                    <label htmlFor="learning-goals">Learning Goals (Optional)</label>
                    <textarea
                      id="learning-goals"
                      value={signUpData.learning_goals}
                      onChange={(e) => setSignUpData({ ...signUpData, learning_goals: e.target.value })}
                      placeholder="What do you hope to learn from this textbook?"
                      rows={3}
                    />
                  </div>

                  {error && <div className="auth-error">{error}</div>}

                  <div className="auth-button-group">
                    <button type="button" className="auth-back-btn" onClick={() => setStep(1)}>
                      Back
                    </button>
                    <button type="submit" className="auth-submit-btn" disabled={isLoading}>
                      {isLoading ? 'Creating account...' : 'Create Account'}
                    </button>
                  </div>
                </form>
              </>
            )}

            <div className="auth-switch">
              Already have an account?{' '}
              <button onClick={() => switchMode('signin')}>Sign In</button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
