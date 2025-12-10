import React, { useEffect } from 'react';
import { useLocation } from '@docusaurus/router';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Chatbot from '../components/Chatbot';
import { AuthProvider } from '../contexts/AuthContext';
import UserMenu from '../components/UserMenu';
import { createPortal } from 'react-dom';

interface RootProps {
  children: React.ReactNode;
}

function UserMenuPortal(): JSX.Element | null {
  const [container, setContainer] = React.useState<HTMLElement | null>(null);

  useEffect(() => {
    // Find the navbar right items container
    const findNavbarContainer = () => {
      const navbarItems = document.querySelector('.navbar__items--right');
      if (navbarItems && !document.getElementById('user-menu-portal')) {
        const portalContainer = document.createElement('div');
        portalContainer.id = 'user-menu-portal';
        portalContainer.style.display = 'flex';
        portalContainer.style.alignItems = 'center';
        portalContainer.style.marginLeft = '0.5rem';
        navbarItems.appendChild(portalContainer);
        setContainer(portalContainer);
      }
    };

    // Try immediately and then with a delay
    findNavbarContainer();
    const timeout = setTimeout(findNavbarContainer, 100);

    return () => clearTimeout(timeout);
  }, []);

  if (!container) return null;

  return createPortal(<UserMenu />, container);
}

export default function Root({ children }: RootProps): JSX.Element {
  const { i18n } = useDocusaurusContext();
  const location = useLocation();

  // Determine language from i18n context or URL
  const currentLocale = i18n.currentLocale;
  const language = currentLocale === 'ur' ? 'ur' : 'en';

  // Only show chatbot on docs pages
  const isDocsPage = location.pathname.includes('/docs') ||
                     location.pathname === '/' ||
                     location.pathname.startsWith('/01-') ||
                     location.pathname.startsWith('/02-') ||
                     location.pathname.startsWith('/03-') ||
                     location.pathname.startsWith('/04-') ||
                     location.pathname.startsWith('/05-') ||
                     location.pathname.startsWith('/06-');

  return (
    <AuthProvider>
      {children}
      <UserMenuPortal />
      {isDocsPage && <Chatbot language={language} />}
    </AuthProvider>
  );
}
