"""
Document Ingestion Module
=========================

Handles loading documents from multiple source formats into a unified
internal representation. Supported formats:
- PDF files (via pypdf or pdfplumber)
- Web pages (via requests + BeautifulSoup)
- Markdown files (direct file reading with frontmatter parsing)

Each document is converted into a list of Document objects with content
and metadata (source, page number, URL, title, ingestion timestamp).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class SourceType(Enum):
    """Supported document source types."""

    PDF = "pdf"
    WEB = "web"
    MARKDOWN = "markdown"


@dataclass
class Document:
    """Internal representation of an ingested document.

    Attributes
    ----------
    content : str
        The raw text content of the document.
    metadata : dict
        Source information, page numbers, timestamps, etc.
    source_type : SourceType
        The type of source this document was ingested from.
    doc_id : str
        Unique identifier for the document.
    """

    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    source_type: SourceType = SourceType.PDF
    doc_id: str = ""


class DocumentIngester:
    """Ingest documents from PDF, web, and markdown sources.

    Parameters
    ----------
    source_type : SourceType
        The type of source to ingest from.
    config : dict, optional
        Source-specific configuration (e.g., headers for web requests,
        PDF extraction settings).

    Examples
    --------
    >>> ingester = DocumentIngester(source_type=SourceType.PDF)
    >>> docs = ingester.ingest("path/to/document.pdf")
    """

    def __init__(
        self,
        source_type: SourceType,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.source_type = source_type
        self.config = config or {}

    def ingest(self, source: Union[str, Path]) -> List[Document]:
        """Ingest a document from the given source.

        Parameters
        ----------
        source : str or Path
            File path or URL to ingest.

        Returns
        -------
        list of Document
            Parsed documents with content and metadata.
        """
        raise NotImplementedError

    def ingest_pdf(self, file_path: Union[str, Path]) -> List[Document]:
        """Extract text and metadata from a PDF file.

        Parameters
        ----------
        file_path : str or Path
            Path to the PDF file.

        Returns
        -------
        list of Document
            One Document per page.
        """
        raise NotImplementedError

    def ingest_web(self, url: str) -> List[Document]:
        """Scrape and parse content from a web page.

        Parameters
        ----------
        url : str
            URL to scrape.

        Returns
        -------
        list of Document
            Parsed web page content.
        """
        raise NotImplementedError

    def ingest_markdown(self, file_path: Union[str, Path]) -> List[Document]:
        """Load and parse a markdown file with optional frontmatter.

        Parameters
        ----------
        file_path : str or Path
            Path to the markdown file.

        Returns
        -------
        list of Document
            Parsed markdown content with frontmatter as metadata.
        """
        raise NotImplementedError

    def ingest_batch(
        self, sources: List[Union[str, Path]]
    ) -> List[Document]:
        """Ingest multiple documents in batch.

        Parameters
        ----------
        sources : list of str or Path
            List of file paths or URLs.

        Returns
        -------
        list of Document
            All ingested documents.
        """
        raise NotImplementedError
