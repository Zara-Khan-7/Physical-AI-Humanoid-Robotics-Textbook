#!/usr/bin/env python3
"""Script to index Markdown content into Qdrant vector store."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import get_settings
from app.services.chunker import MarkdownChunker
from app.services.embeddings import EmbeddingService
from app.services.vector_store import VectorStoreService


async def index_markdown_file(
    file_path: Path,
    chapter_id: str,
    chapter_title: str,
    language: str,
    chunker: MarkdownChunker,
    embedding_service: EmbeddingService,
    vector_store: VectorStoreService,
) -> int:
    """Index a single Markdown file.

    Args:
        file_path: Path to the Markdown file
        chapter_id: Chapter identifier
        chapter_title: Chapter title
        language: Language code (en or ur)
        chunker: MarkdownChunker instance
        embedding_service: EmbeddingService instance
        vector_store: VectorStoreService instance

    Returns:
        Number of chunks indexed
    """
    print(f"  Processing: {file_path}")

    # Read file content
    content = file_path.read_text(encoding="utf-8")

    # Chunk the document
    chunks = chunker.chunk_document(
        content=content,
        chapter_id=chapter_id,
        chapter_title=chapter_title,
        path=str(file_path),
        language=language,
    )

    if not chunks:
        print(f"    No chunks generated from {file_path}")
        return 0

    print(f"    Generated {len(chunks)} chunks")

    # Convert chunks to dictionaries
    chunk_dicts = [chunker.chunk_to_dict(chunk) for chunk in chunks]

    # Generate embeddings for all chunks
    print(f"    Generating embeddings...")
    texts = [chunk.content for chunk in chunks]
    vectors = await embedding_service.embed_documents(texts)

    # Store in vector database
    print(f"    Storing in Qdrant...")
    count = await vector_store.upsert_chunks(chunk_dicts, vectors)

    print(f"    Indexed {count} chunks")
    return count


async def index_chapter(
    chapter_path: Path,
    chapter_id: str,
    chapter_title: str,
    language: str,
    chunker: MarkdownChunker,
    embedding_service: EmbeddingService,
    vector_store: VectorStoreService,
) -> int:
    """Index all Markdown files in a chapter directory.

    Args:
        chapter_path: Path to chapter directory
        chapter_id: Chapter identifier
        chapter_title: Chapter title
        language: Language code
        chunker: MarkdownChunker instance
        embedding_service: EmbeddingService instance
        vector_store: VectorStoreService instance

    Returns:
        Total chunks indexed
    """
    total_chunks = 0

    # Find all Markdown files
    md_files = list(chapter_path.glob("**/*.md")) + list(chapter_path.glob("**/*.mdx"))

    for md_file in md_files:
        count = await index_markdown_file(
            file_path=md_file,
            chapter_id=chapter_id,
            chapter_title=chapter_title,
            language=language,
            chunker=chunker,
            embedding_service=embedding_service,
            vector_store=vector_store,
        )
        total_chunks += count

    return total_chunks


async def main():
    """Main indexing function."""
    settings = get_settings()

    # Initialize services
    chunker = MarkdownChunker(
        min_tokens=512,
        max_tokens=1000,
        overlap_tokens=50,
    )

    embedding_service = EmbeddingService(
        api_key=settings.google_api_key,
        model=settings.embedding_model,
        dimensions=settings.embedding_dim,
    )

    vector_store = VectorStoreService(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        collection_name=settings.qdrant_collection,
    )

    # Check services
    if not embedding_service.is_configured():
        print("ERROR: Embedding service not configured. Set GOOGLE_API_KEY.")
        sys.exit(1)

    if not await vector_store.health_check():
        print("ERROR: Cannot connect to Qdrant. Check QDRANT_URL.")
        sys.exit(1)

    print("Services initialized successfully")

    # Define content paths (relative to frontend/docs)
    frontend_path = Path(__file__).parent.parent.parent / "frontend"
    docs_path = frontend_path / "docs"
    i18n_path = frontend_path / "i18n" / "ur" / "docusaurus-plugin-content-docs" / "current"

    # Chapter definitions
    chapters = [
        ("01-intro", "Introduction to Physical AI"),
        ("02-foundations", "Foundations of Humanoid Robotics"),
        ("03-sensors", "Sensors and Perception"),
        ("04-actuators", "Actuators and Movement"),
        ("05-ai-integration", "AI Integration"),
        ("06-applications", "Applications and Future"),
    ]

    total_indexed = 0

    # Index English content
    print("\n=== Indexing English Content ===")
    for chapter_id, chapter_title in chapters:
        chapter_path = docs_path / chapter_id
        if chapter_path.exists():
            print(f"\nChapter: {chapter_title}")
            # Delete existing chapter data first
            await vector_store.delete_by_chapter(f"{chapter_id}-en")
            count = await index_chapter(
                chapter_path=chapter_path,
                chapter_id=f"{chapter_id}-en",
                chapter_title=chapter_title,
                language="en",
                chunker=chunker,
                embedding_service=embedding_service,
                vector_store=vector_store,
            )
            total_indexed += count
        else:
            print(f"\nSkipping {chapter_id} (path not found: {chapter_path})")

    # Index Urdu content if available
    print("\n=== Indexing Urdu Content ===")
    for chapter_id, chapter_title in chapters:
        chapter_path = i18n_path / chapter_id
        if chapter_path.exists():
            print(f"\nChapter: {chapter_title} (Urdu)")
            # Delete existing chapter data first
            await vector_store.delete_by_chapter(f"{chapter_id}-ur")
            count = await index_chapter(
                chapter_path=chapter_path,
                chapter_id=f"{chapter_id}-ur",
                chapter_title=chapter_title,
                language="ur",
                chunker=chunker,
                embedding_service=embedding_service,
                vector_store=vector_store,
            )
            total_indexed += count
        else:
            print(f"\nSkipping {chapter_id} Urdu (path not found)")

    # Print summary
    print("\n=== Indexing Complete ===")
    print(f"Total chunks indexed: {total_indexed}")

    # Get collection info
    info = await vector_store.get_collection_info()
    print(f"Collection '{info['name']}' now has {info['points_count']} points")


if __name__ == "__main__":
    asyncio.run(main())
