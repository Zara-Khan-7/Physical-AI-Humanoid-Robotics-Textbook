import React from 'react';
import { useLocation } from '@docusaurus/router';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Chatbot from '../components/Chatbot';

interface RootProps {
  children: React.ReactNode;
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
    <>
      {children}
      {isDocsPage && <Chatbot language={language} />}
    </>
  );
}
