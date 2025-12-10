import React from 'react';
import clsx from 'clsx';
import {ThemeClassNames} from '@docusaurus/theme-common';
import {useDoc} from '@docusaurus/plugin-content-docs/client';
import Heading from '@theme/Heading';
import MDXContent from '@theme/MDXContent';
import ChapterActions from '../../../components/ChapterActions';

function useSyntheticTitle(): string | null {
  const {metadata, frontMatter, contentTitle} = useDoc();
  const shouldRender =
    !frontMatter.hide_title && typeof contentTitle === 'undefined';
  if (!shouldRender) {
    return null;
  }
  return metadata.title;
}

export default function DocItemContent({children}: {children: React.ReactNode}): JSX.Element {
  const syntheticTitle = useSyntheticTitle();
  const {metadata} = useDoc();

  // Determine if this is a main chapter page (index page)
  const isChapterPage = metadata.slug?.includes('/') === false ||
                        metadata.slug === 'intro' ||
                        metadata.slug === 'foundations' ||
                        metadata.slug === 'sensors' ||
                        metadata.slug === 'actuators' ||
                        metadata.slug === 'ai-integration' ||
                        metadata.slug === 'applications';

  return (
    <div className={clsx(ThemeClassNames.docs.docMarkdown, 'markdown')}>
      {syntheticTitle && (
        <header>
          <Heading as="h1">{syntheticTitle}</Heading>
        </header>
      )}

      {/* Add ChapterActions for main chapter pages */}
      {isChapterPage && (
        <ChapterActions
          chapterId={metadata.id || metadata.slug || 'unknown'}
          chapterTitle={metadata.title}
        />
      )}

      <MDXContent>{children}</MDXContent>
    </div>
  );
}
