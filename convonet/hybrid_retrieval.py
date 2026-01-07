"""
Hybrid Retrieval System
Combines structured (SQL/tool-based) and unstructured (vector/RAG) retrieval.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from .rag_service import RAGService, RetrievalResult, get_rag_service

logger = logging.getLogger(__name__)


@dataclass
class HybridRetrievalResult:
    """Result from hybrid retrieval combining structured and unstructured data."""
    structured_results: List[Dict[str, Any]]  # Results from tools/SQL
    unstructured_results: List[RetrievalResult]  # Results from RAG
    combined_context: str  # Combined context for LLM
    retrieval_strategy: str  # "structured", "unstructured", or "hybrid"


class HybridRetrieval:
    """
    Hybrid retrieval system that combines:
    - Structured retrieval: SQL queries, tool-based data access
    - Unstructured retrieval: Vector search, semantic search
    """
    
    def __init__(self, rag_service: Optional[RAGService] = None):
        """
        Initialize hybrid retrieval system.
        
        Args:
            rag_service: RAG service instance
        """
        self.rag_service = rag_service or get_rag_service()
    
    def retrieve(
        self,
        query: str,
        structured_tools: Optional[List[Any]] = None,
        use_rag: bool = True,
        top_k_structured: int = 5,
        top_k_unstructured: int = 5
    ) -> HybridRetrievalResult:
        """
        Perform hybrid retrieval combining structured and unstructured sources.
        
        Args:
            query: User query
            structured_tools: List of tools to use for structured retrieval
            use_rag: Whether to use RAG for unstructured retrieval
            top_k_structured: Number of structured results
            top_k_unstructured: Number of unstructured results
            
        Returns:
            HybridRetrievalResult with combined results
        """
        structured_results = []
        unstructured_results = []
        strategy = "hybrid"
        
        # Structured retrieval (if tools provided)
        if structured_tools:
            structured_results = self._retrieve_structured(query, structured_tools, top_k_structured)
            if structured_results:
                strategy = "hybrid" if use_rag else "structured"
        
        # Unstructured retrieval (RAG)
        if use_rag and self.rag_service:
            unstructured_results = self.rag_service.retrieve(query, top_k=top_k_unstructured)
            if unstructured_results and not structured_results:
                strategy = "unstructured"
        elif use_rag and not self.rag_service:
            logger.warning("⚠️ RAG service not available, skipping unstructured retrieval")
        
        # Combine results into context
        combined_context = self._combine_context(structured_results, unstructured_results)
        
        return HybridRetrievalResult(
            structured_results=structured_results,
            unstructured_results=unstructured_results,
            combined_context=combined_context,
            retrieval_strategy=strategy
        )
    
    def _retrieve_structured(
        self,
        query: str,
        tools: List[Any],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Retrieve structured data using tools.
        This is a placeholder - actual implementation would call tools.
        
        Args:
            query: User query
            tools: List of available tools
            top_k: Number of results
            
        Returns:
            List of structured results
        """
        # In a real implementation, this would:
        # 1. Analyze query to determine which tools to use
        # 2. Execute relevant tools (get_todos, get_calendar_events, etc.)
        # 3. Format results
        
        results = []
        # Placeholder - actual implementation would call tools
        logger.info(f"🔍 Structured retrieval: {len(tools)} tools available for query: {query[:50]}...")
        
        return results[:top_k]
    
    def _combine_context(
        self,
        structured_results: List[Dict[str, Any]],
        unstructured_results: List[RetrievalResult]
    ) -> str:
        """
        Combine structured and unstructured results into a single context string.
        
        Args:
            structured_results: Structured data results
            unstructured_results: RAG retrieval results
            
        Returns:
            Combined context string
        """
        context_parts = []
        
        # Add structured results
        if structured_results:
            context_parts.append("## Structured Data:")
            for i, result in enumerate(structured_results, 1):
                context_parts.append(f"\n### Result {i}:")
                if isinstance(result, dict):
                    context_parts.append(str(result))
                else:
                    context_parts.append(str(result))
        
        # Add unstructured results
        if unstructured_results:
            context_parts.append("\n## Knowledge Base Documents:")
            for result in unstructured_results:
                doc = result.document
                context_parts.append(f"\n### {doc.metadata.get('title', 'Document')} (Relevance: {result.score:.2f}):")
                context_parts.append(doc.content)
        
        return "\n".join(context_parts)
    
    def should_use_rag(self, query: str) -> bool:
        """
        Determine if query should use RAG (unstructured retrieval).
        
        Args:
            query: User query
            
        Returns:
            True if RAG should be used
        """
        # Keywords that suggest knowledge base queries
        rag_keywords = [
            "how", "what", "explain", "tell me about", "documentation",
            "guide", "help", "information", "knowledge", "learn"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in rag_keywords)
    
    def should_use_structured(self, query: str) -> bool:
        """
        Determine if query should use structured retrieval.
        
        Args:
            query: User query
            
        Returns:
            True if structured retrieval should be used
        """
        # Keywords that suggest data queries
        structured_keywords = [
            "show", "list", "get", "find", "search", "my", "create", "add",
            "todo", "calendar", "event", "team", "member", "reminder"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in structured_keywords)

