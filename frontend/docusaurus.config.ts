import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

const config: Config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'Essentials for the AI-Native Era',
  favicon: 'img/favicon.ico',

  // Production URL - set via environment variable for different deployments
  // For Vercel: https://your-project.vercel.app
  // For GitHub Pages: https://<username>.github.io
  url: process.env.SITE_URL || 'https://physical-ai-textbook.vercel.app',
  // Base URL - '/' for Vercel, '/<projectName>/' for GitHub Pages
  baseUrl: process.env.BASE_URL || '/',

  // GitHub pages deployment config (used when deploying to GitHub Pages)
  organizationName: process.env.ORG_NAME || 'Zara-Khan-7',
  projectName: process.env.PROJECT_NAME || 'Physical-AI-Humanoid-Robotics-Textbook',
  trailingSlash: false,

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Custom fields for runtime configuration
  customFields: {
    apiUrl: process.env.API_URL || 'http://localhost:8000/api/v1',
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'ur'],
    localeConfigs: {
      en: {
        label: 'English',
        direction: 'ltr',
      },
      ur: {
        label: 'اردو',
        direction: 'rtl',
      },
    },
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: '/',
          remarkPlugins: [remarkMath],
          rehypePlugins: [rehypeKatex],
          showLastUpdateTime: false,
        },
        blog: false,
        theme: {
          customCss: [
            './src/css/custom.css',
            './src/css/chatbot.css',
          ],
        },
      } satisfies Preset.Options,
    ],
  ],

  themes: [
    [
      '@easyops-cn/docusaurus-search-local',
      {
        hashed: true,
        language: ['en'],
        highlightSearchTermsOnTargetPage: true,
        explicitSearchResultPath: true,
      },
    ],
  ],

  stylesheets: [
    {
      href: 'https://cdn.jsdelivr.net/npm/katex@0.16.0/dist/katex.min.css',
      type: 'text/css',
      integrity: 'sha384-Xi8rHCmBmhbuyyhbI88391ZKP2dmfnOl4rT9ZfRI7mLTdk1wblIUnrIq35nqwEvC',
      crossorigin: 'anonymous',
    },
  ],

  themeConfig: {
    image: 'img/social-card.jpg',
    navbar: {
      title: 'Physical AI Textbook',
      logo: {
        alt: 'Physical AI Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Chapters',
        },
        {
          type: 'localeDropdown',
          position: 'right',
        },
        {
          href: 'https://github.com/your-org/physical-ai-textbook',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Chapters',
          items: [
            {
              label: 'Introduction',
              to: '/intro',
            },
            {
              label: 'Foundations',
              to: '/foundations',
            },
            {
              label: 'Sensors',
              to: '/sensors',
            },
          ],
        },
        {
          title: 'More Chapters',
          items: [
            {
              label: 'Actuators',
              to: '/actuators',
            },
            {
              label: 'AI Integration',
              to: '/ai-integration',
            },
            {
              label: 'Applications',
              to: '/applications',
            },
          ],
        },
        {
          title: 'Resources',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/your-org/physical-ai-textbook',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Physical AI Textbook. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['python', 'bash', 'yaml', 'json', 'cpp', 'rust'],
    },
    tableOfContents: {
      minHeadingLevel: 2,
      maxHeadingLevel: 4,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
