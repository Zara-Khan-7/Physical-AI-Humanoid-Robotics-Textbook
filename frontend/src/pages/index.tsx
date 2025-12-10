import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <h1 className="hero__title">{siteConfig.title}</h1>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            Start Learning
          </Link>
        </div>
      </div>
    </header>
  );
}

const FeatureList = [
  {
    title: 'Introduction to Physical AI',
    link: '/docs/intro',
    description: 'Understand what Physical AI is, its history, and why humanoid robots matter in the modern world.',
  },
  {
    title: 'Foundations of Robotics',
    link: '/docs/foundations',
    description: 'Learn the core concepts of kinematics, dynamics, and control theory that enable robot motion.',
  },
  {
    title: 'Sensors & Perception',
    link: '/docs/sensors',
    description: 'Discover how robots sense their environment through cameras, LiDAR, and force sensors.',
  },
  {
    title: 'Actuators & Movement',
    link: '/docs/actuators',
    description: 'From electric motors to artificial muscles - understand how robots generate motion.',
  },
  {
    title: 'AI Integration',
    link: '/docs/ai-integration',
    description: 'Explore machine learning, deep learning, and reinforcement learning applied to robotics.',
  },
  {
    title: 'Applications & Future',
    link: '/docs/applications',
    description: 'Real-world applications in manufacturing, healthcare, and the future of humanoid robotics.',
  },
];

function Feature({title, link, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className={styles.featureCard}>
        <h3>
          <Link to={link}>{title}</Link>
        </h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <h2 className={styles.sectionTitle}>Chapters</h2>
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}

function ChatbotSection() {
  return (
    <section className={styles.chatbotSection}>
      <div className="container">
        <h2 className={styles.sectionTitle}>AI-Powered Learning Assistant</h2>
        <p className={styles.chatbotDescription}>
          This textbook features an intelligent chatbot that can answer your questions about Physical AI and Humanoid Robotics.
          Look for the chat icon in the bottom-right corner of any page to start asking questions!
        </p>
        <div className={styles.chatbotFeatures}>
          <div className={styles.chatbotFeature}>
            <strong>Ask Questions</strong>
            <p>Get instant answers based on textbook content</p>
          </div>
          <div className={styles.chatbotFeature}>
            <strong>Concept Explanations</strong>
            <p>Complex topics explained in simple terms</p>
          </div>
          <div className={styles.chatbotFeature}>
            <strong>Citations Included</strong>
            <p>Every answer links back to relevant chapters</p>
          </div>
        </div>
      </div>
    </section>
  );
}

export default function Home(): JSX.Element {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Welcome`}
      description="Physical AI and Humanoid Robotics - An AI-Native Textbook">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
        <ChatbotSection />
      </main>
    </Layout>
  );
}
