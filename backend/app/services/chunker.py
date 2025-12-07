"""Markdown chunker for textbook content."""

import re
from typing import Any
from dataclasses import dataclass, field


@dataclass
class Chunk:
    """A chunk of text from a Markdown document."""

    content: str
    chapter_id: str
    chapter_title: str
    section_id: str
    section_title: str
    path: str
    language: str = "en"
    token_estimate: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class MarkdownChunker:
    """Chunker for Markdown documents using header-based splitting.

    Splits Markdown content into chunks based on headers while respecting
    token limits (512-1000 tokens target range).
    """

    def __init__(
        self,
        min_tokens: int = 512,
        max_tokens: int = 1000,
        overlap_tokens: int = 50,
    ):
        """Initialize the chunker.

        Args:
            min_tokens: Minimum tokens per chunk (target)
            max_tokens: Maximum tokens per chunk
            overlap_tokens: Token overlap between chunks for context
        """
        self.min_tokens = min_tokens
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens

        # Header pattern to detect Markdown headers
        self.header_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (roughly 4 chars per token for English).

        Args:
            text: Text to estimate tokens for

        Returns:
            Estimated token count
        """
        # Simple estimation: ~4 characters per token for English
        # Slightly higher for Urdu/mixed content
        return len(text) // 4

    def chunk_document(
        self,
        content: str,
        chapter_id: str,
        chapter_title: str,
        path: str,
        language: str = "en",
    ) -> list[Chunk]:
        """Chunk a Markdown document into smaller pieces.

        Args:
            content: Markdown content to chunk
            chapter_id: Chapter identifier
            chapter_title: Chapter title
            path: File path of the document
            language: Language code (en or ur)

        Returns:
            List of Chunk objects
        """
        sections = self._split_by_headers(content)
        chunks = []

        for section in sections:
            section_chunks = self._chunk_section(
                section_content=section["content"],
                chapter_id=chapter_id,
                chapter_title=chapter_title,
                section_id=section["id"],
                section_title=section["title"],
                path=path,
                language=language,
            )
            chunks.extend(section_chunks)

        return chunks

    def _split_by_headers(self, content: str) -> list[dict[str, str]]:
        """Split content by Markdown headers.

        Args:
            content: Markdown content

        Returns:
            List of sections with id, title, and content
        """
        sections = []
        lines = content.split("\n")
        current_section = {
            "id": "intro",
            "title": "Introduction",
            "content": [],
            "level": 0,
        }

        for line in lines:
            header_match = self.header_pattern.match(line)
            if header_match:
                # Save previous section if it has content
                if current_section["content"]:
                    sections.append(
                        {
                            "id": self._slugify(current_section["title"]),
                            "title": current_section["title"],
                            "content": "\n".join(current_section["content"]).strip(),
                        }
                    )

                # Start new section
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                current_section = {
                    "id": self._slugify(title),
                    "title": title,
                    "content": [line],  # Include header in content
                    "level": level,
                }
            else:
                current_section["content"].append(line)

        # Don't forget the last section
        if current_section["content"]:
            sections.append(
                {
                    "id": self._slugify(current_section["title"]),
                    "title": current_section["title"],
                    "content": "\n".join(current_section["content"]).strip(),
                }
            )

        return sections

    def _chunk_section(
        self,
        section_content: str,
        chapter_id: str,
        chapter_title: str,
        section_id: str,
        section_title: str,
        path: str,
        language: str,
    ) -> list[Chunk]:
        """Chunk a section into appropriately sized pieces.

        Args:
            section_content: Section text content
            chapter_id: Chapter identifier
            chapter_title: Chapter title
            section_id: Section identifier
            section_title: Section title
            path: File path
            language: Language code

        Returns:
            List of Chunk objects for this section
        """
        tokens = self.estimate_tokens(section_content)

        # If section fits in one chunk, return as-is
        if tokens <= self.max_tokens:
            return [
                Chunk(
                    content=section_content,
                    chapter_id=chapter_id,
                    chapter_title=chapter_title,
                    section_id=section_id,
                    section_title=section_title,
                    path=path,
                    language=language,
                    token_estimate=tokens,
                )
            ]

        # Split large sections by paragraphs
        return self._split_by_paragraphs(
            content=section_content,
            chapter_id=chapter_id,
            chapter_title=chapter_title,
            section_id=section_id,
            section_title=section_title,
            path=path,
            language=language,
        )

    def _split_by_paragraphs(
        self,
        content: str,
        chapter_id: str,
        chapter_title: str,
        section_id: str,
        section_title: str,
        path: str,
        language: str,
    ) -> list[Chunk]:
        """Split content by paragraphs to fit token limits.

        Args:
            content: Text content to split
            chapter_id: Chapter identifier
            chapter_title: Chapter title
            section_id: Section identifier
            section_title: Section title
            path: File path
            language: Language code

        Returns:
            List of Chunk objects
        """
        paragraphs = re.split(r"\n\s*\n", content)
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            para_tokens = self.estimate_tokens(para)

            # If single paragraph exceeds max, split by sentences
            if para_tokens > self.max_tokens:
                # Save current chunk first
                if current_chunk:
                    chunk_content = "\n\n".join(current_chunk)
                    chunks.append(
                        Chunk(
                            content=chunk_content,
                            chapter_id=chapter_id,
                            chapter_title=chapter_title,
                            section_id=section_id,
                            section_title=section_title,
                            path=path,
                            language=language,
                            token_estimate=self.estimate_tokens(chunk_content),
                        )
                    )
                    current_chunk = []
                    current_tokens = 0

                # Split large paragraph by sentences
                sentence_chunks = self._split_by_sentences(
                    para,
                    chapter_id,
                    chapter_title,
                    section_id,
                    section_title,
                    path,
                    language,
                )
                chunks.extend(sentence_chunks)
                continue

            # Check if adding this paragraph exceeds limit
            if current_tokens + para_tokens > self.max_tokens:
                # Save current chunk
                if current_chunk:
                    chunk_content = "\n\n".join(current_chunk)
                    chunks.append(
                        Chunk(
                            content=chunk_content,
                            chapter_id=chapter_id,
                            chapter_title=chapter_title,
                            section_id=section_id,
                            section_title=section_title,
                            path=path,
                            language=language,
                            token_estimate=self.estimate_tokens(chunk_content),
                        )
                    )

                # Start new chunk with overlap
                if self.overlap_tokens > 0 and current_chunk:
                    # Add last paragraph as overlap
                    overlap_para = current_chunk[-1]
                    current_chunk = [overlap_para, para]
                    current_tokens = self.estimate_tokens(overlap_para) + para_tokens
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        # Save remaining content
        if current_chunk:
            chunk_content = "\n\n".join(current_chunk)
            chunks.append(
                Chunk(
                    content=chunk_content,
                    chapter_id=chapter_id,
                    chapter_title=chapter_title,
                    section_id=section_id,
                    section_title=section_title,
                    path=path,
                    language=language,
                    token_estimate=self.estimate_tokens(chunk_content),
                )
            )

        return chunks

    def _split_by_sentences(
        self,
        content: str,
        chapter_id: str,
        chapter_title: str,
        section_id: str,
        section_title: str,
        path: str,
        language: str,
    ) -> list[Chunk]:
        """Split content by sentences as last resort.

        Args:
            content: Text content to split
            chapter_id: Chapter identifier
            chapter_title: Chapter title
            section_id: Section identifier
            section_title: Section title
            path: File path
            language: Language code

        Returns:
            List of Chunk objects
        """
        # Simple sentence splitting (handles English and basic punctuation)
        sentences = re.split(r"(?<=[.!?])\s+", content)
        chunks = []
        current_chunk = []
        current_tokens = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            sent_tokens = self.estimate_tokens(sentence)

            if current_tokens + sent_tokens > self.max_tokens:
                if current_chunk:
                    chunk_content = " ".join(current_chunk)
                    chunks.append(
                        Chunk(
                            content=chunk_content,
                            chapter_id=chapter_id,
                            chapter_title=chapter_title,
                            section_id=section_id,
                            section_title=section_title,
                            path=path,
                            language=language,
                            token_estimate=self.estimate_tokens(chunk_content),
                        )
                    )
                current_chunk = [sentence]
                current_tokens = sent_tokens
            else:
                current_chunk.append(sentence)
                current_tokens += sent_tokens

        if current_chunk:
            chunk_content = " ".join(current_chunk)
            chunks.append(
                Chunk(
                    content=chunk_content,
                    chapter_id=chapter_id,
                    chapter_title=chapter_title,
                    section_id=section_id,
                    section_title=section_title,
                    path=path,
                    language=language,
                    token_estimate=self.estimate_tokens(chunk_content),
                )
            )

        return chunks

    def _slugify(self, text: str) -> str:
        """Convert text to a URL-friendly slug.

        Args:
            text: Text to slugify

        Returns:
            Slugified string
        """
        # Remove special characters and convert to lowercase
        slug = re.sub(r"[^\w\s-]", "", text.lower())
        # Replace whitespace with hyphens
        slug = re.sub(r"[\s_]+", "-", slug)
        # Remove leading/trailing hyphens
        slug = slug.strip("-")
        return slug or "untitled"

    def chunk_to_dict(self, chunk: Chunk) -> dict[str, Any]:
        """Convert a Chunk to a dictionary for storage.

        Args:
            chunk: Chunk object

        Returns:
            Dictionary representation
        """
        return {
            "content": chunk.content,
            "chapter_id": chunk.chapter_id,
            "chapter_title": chunk.chapter_title,
            "section_id": chunk.section_id,
            "section_title": chunk.section_title,
            "path": chunk.path,
            "language": chunk.language,
            "token_estimate": chunk.token_estimate,
            **chunk.metadata,
        }
