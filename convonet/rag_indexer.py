"""
Document Indexing Utility for RAG System
Handles document chunking, preprocessing, and indexing.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import re

from .rag_service import RAGService, Document, get_rag_service

logger = logging.getLogger(__name__)


class DocumentIndexer:
    """
    Utility for indexing documents into the RAG system.
    Supports various document formats and chunking strategies.
    """
    
    def __init__(self, rag_service: Optional[RAGService] = None):
        """
        Initialize document indexer.
        
        Args:
            rag_service: RAG service instance (creates new if None)
        """
        self.rag_service = rag_service or get_rag_service()
        if not self.rag_service:
            logger.warning("⚠️ RAG service not available")
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        strategy: str = "sentence"
    ) -> List[str]:
        """
        Chunk text into smaller pieces for indexing.
        
        Args:
            text: Text to chunk
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks
            strategy: Chunking strategy ("sentence", "paragraph", "fixed")
            
        Returns:
            List of text chunks
        """
        if strategy == "sentence":
            return self._chunk_by_sentence(text, chunk_size, chunk_overlap)
        elif strategy == "paragraph":
            return self._chunk_by_paragraph(text, chunk_size, chunk_overlap)
        else:
            return self._chunk_fixed(text, chunk_size, chunk_overlap)
    
    def _chunk_by_sentence(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Chunk text by sentences."""
        # Split by sentence endings
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _chunk_by_paragraph(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Chunk text by paragraphs."""
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) <= chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _chunk_fixed(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Chunk text into fixed-size pieces."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        return chunks
    
    def index_text(
        self,
        text: str,
        title: str,
        source: str = "manual",
        category: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Index a text document.
        
        Args:
            text: Document text
            title: Document title
            source: Source of the document
            category: Document category
            metadata: Additional metadata
            
        Returns:
            True if successful
        """
        if not self.rag_service:
            logger.error("❌ RAG service not available")
            return False
        
        # Chunk the text
        chunks = self.chunk_text(text, chunk_size=500, chunk_overlap=50)
        
        # Create documents
        documents = []
        for i, chunk in enumerate(chunks):
            doc_id = self._generate_doc_id(title, i)
            
            doc_metadata = {
                "title": title,
                "source": source,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "indexed_at": datetime.now().isoformat()
            }
            
            if category:
                doc_metadata["category"] = category
            
            if metadata:
                doc_metadata.update(metadata)
            
            documents.append(Document(
                id=doc_id,
                content=chunk,
                metadata=doc_metadata
            ))
        
        # Index documents
        return self.rag_service.index_documents(documents)
    
    def index_file(
        self,
        file_path: str,
        title: Optional[str] = None,
        category: Optional[str] = None
    ) -> bool:
        """
        Index a file (text, markdown, etc.).
        
        Args:
            file_path: Path to the file
            title: Document title (defaults to filename)
            category: Document category
            
        Returns:
            True if successful
        """
        if not os.path.exists(file_path):
            logger.error(f"❌ File not found: {file_path}")
            return False
        
        title = title or os.path.basename(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.index_text(
                text=content,
                title=title,
                source=f"file://{file_path}",
                category=category
            )
        except Exception as e:
            logger.error(f"❌ Failed to index file {file_path}: {e}")
            return False
    
    def index_knowledge_base(
        self,
        knowledge_base: Dict[str, str],
        category: Optional[str] = None
    ) -> bool:
        """
        Index a knowledge base (dict of title -> content).
        
        Args:
            knowledge_base: Dictionary mapping titles to content
            category: Category for all documents
            
        Returns:
            True if successful
        """
        if not self.rag_service:
            logger.error("❌ RAG service not available")
            return False
        
        success_count = 0
        for title, content in knowledge_base.items():
            if self.index_text(
                text=content,
                title=title,
                source="knowledge_base",
                category=category
            ):
                success_count += 1
        
        logger.info(f"✅ Indexed {success_count}/{len(knowledge_base)} documents")
        return success_count > 0
    
    def _generate_doc_id(self, title: str, chunk_index: int) -> str:
        """Generate a unique document ID."""
        base = f"{title}_{chunk_index}"
        return hashlib.md5(base.encode()).hexdigest()


def create_sample_knowledge_base() -> Dict[str, str]:
    """
    Create a sample knowledge base for demonstration.
    This can be replaced with actual knowledge base content.
    """
    return {
        "Convonet Voice Commands": """
        Convonet supports various voice commands for productivity:
        - "Create a todo" - Creates a new todo item
        - "Show my todos" - Lists all your todos
        - "Schedule a meeting" - Creates a calendar event
        - "Create a team" - Creates a new team
        - "Add member to team" - Adds a user to a team
        - "Transfer me" - Transfers voice call to human agent
        """,
        
        "Team Management": """
        Teams in Convonet allow collaborative task management:
        - Create teams with create_team tool
        - Add members with add_team_member tool
        - Assign team todos with create_team_todo tool
        - Team roles: owner, admin, member
        - Only team owners can delete teams
        """,
        
        "Calendar Integration": """
        Convonet integrates with Google Calendar:
        - Create events with create_calendar_event tool
        - Sync events with sync_google_calendar_events tool
        - Events support start and end times
        - Calendar events are linked to user accounts
        """,
        
        "Voice AI Features": """
        Convonet uses advanced voice AI:
        - Deepgram for speech-to-text with 30+ language support
        - ElevenLabs for text-to-speech with emotion detection
        - Automatic language detection
        - Voice cloning support
        - Emotion-aware responses
        """,
        
        "MCP Tools": """
        Convonet uses Model Context Protocol (MCP) for tool integration:
        - 36 tools available for various operations
        - Database tools: todos, reminders, calendar, teams
        - External integrations: Slack, GitHub, Gmail, Jira
        - Tools are executed via LangGraph orchestration
        """,
        
        "Multi-LLM Support": """
        Convonet supports multiple LLM providers:
        - Anthropic Claude 3.5 Sonnet
        - Google Gemini 2.5 Flash
        - OpenAI GPT-4o
        - Automatic fallback if one provider fails
        - Provider selection based on user preference
        """
    }


def initialize_sample_knowledge_base():
    """Initialize the RAG system with sample knowledge base."""
    indexer = DocumentIndexer()
    if not indexer.rag_service:
        logger.warning("⚠️ RAG service not available, skipping knowledge base initialization")
        return False
    
    knowledge_base = create_sample_knowledge_base()
    return indexer.index_knowledge_base(knowledge_base, category="documentation")

