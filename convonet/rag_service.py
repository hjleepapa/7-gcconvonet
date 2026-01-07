"""
RAG (Retrieval-Augmented Generation) Service
Implements vector embeddings, semantic search, and hybrid retrieval for unstructured documents.
"""

import os
import logging
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Try to import vector database and embedding libraries
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("⚠️ ChromaDB not available. Install with: pip install chromadb")

try:
    from langchain_openai import OpenAIEmbeddings
    OPENAI_EMBEDDINGS_AVAILABLE = True
except ImportError:
    OPENAI_EMBEDDINGS_AVAILABLE = False
    logger.warning("⚠️ OpenAI Embeddings not available. Install with: pip install langchain-openai")

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    HF_EMBEDDINGS_AVAILABLE = True
except ImportError:
    HF_EMBEDDINGS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Reranking
try:
    import cohere
    COHERE_AVAILABLE = True
except ImportError:
    COHERE_AVAILABLE = False
    logger.warning("⚠️ Cohere not available for reranking. Install with: pip install cohere")


@dataclass
class Document:
    """Represents a document in the knowledge base."""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


@dataclass
class RetrievalResult:
    """Result from retrieval operation."""
    document: Document
    score: float
    rank: int


class RAGService:
    """
    RAG Service for unstructured document retrieval.
    Supports vector embeddings, semantic search, and reranking.
    """
    
    def __init__(
        self,
        collection_name: str = "convonet_knowledge_base",
        embedding_model: str = "openai",  # "openai", "huggingface", "sentence-transformers"
        use_reranking: bool = True,
        top_k: int = 20,
        rerank_top_k: int = 5
    ):
        """
        Initialize RAG service.
        
        Args:
            collection_name: Name of the ChromaDB collection
            embedding_model: Embedding model to use
            use_reranking: Whether to use reranking
            top_k: Number of documents to retrieve before reranking
            rerank_top_k: Number of documents to return after reranking
        """
        self.collection_name = collection_name
        self.embedding_model_type = embedding_model
        self.use_reranking = use_reranking
        self.top_k = top_k
        self.rerank_top_k = rerank_top_k
        
        # Initialize vector database
        self.client = None
        self.collection = None
        if CHROMADB_AVAILABLE:
            try:
                # Use persistent storage in a local directory
                chroma_dir = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
                os.makedirs(chroma_dir, exist_ok=True)
                
                self.client = chromadb.PersistentClient(
                    path=chroma_dir,
                    settings=Settings(anonymized_telemetry=False)
                )
                self.collection = self.client.get_or_create_collection(
                    name=collection_name,
                    metadata={"hnsw:space": "cosine"}  # Use cosine similarity
                )
                logger.info(f"✅ ChromaDB initialized: {collection_name}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize ChromaDB: {e}")
                self.client = None
                self.collection = None
        
        # Initialize embedding model
        self.embedder = None
        self._init_embedder()
        
        # Initialize reranker
        self.reranker = None
        if use_reranking:
            self._init_reranker()
    
    def _init_embedder(self):
        """Initialize embedding model."""
        if self.embedding_model_type == "openai" and OPENAI_EMBEDDINGS_AVAILABLE:
            try:
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self.embedder = OpenAIEmbeddings(
                        model="text-embedding-3-small",  # Cost-effective option
                        openai_api_key=api_key
                    )
                    logger.info("✅ OpenAI embeddings initialized")
                else:
                    logger.warning("⚠️ OPENAI_API_KEY not set, falling back to HuggingFace")
                    self._init_hf_embedder()
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize OpenAI embeddings: {e}")
                self._init_hf_embedder()
        elif self.embedding_model_type == "huggingface" and HF_EMBEDDINGS_AVAILABLE:
            self._init_hf_embedder()
        elif SENTENCE_TRANSFORMERS_AVAILABLE:
            self._init_sentence_transformer()
        else:
            logger.error("❌ No embedding model available")
    
    def _init_hf_embedder(self):
        """Initialize HuggingFace embeddings."""
        if HF_EMBEDDINGS_AVAILABLE:
            try:
                self.embedder = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    model_kwargs={'device': 'cpu'}
                )
                logger.info("✅ HuggingFace embeddings initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize HuggingFace embeddings: {e}")
    
    def _init_sentence_transformer(self):
        """Initialize SentenceTransformer embeddings."""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("✅ SentenceTransformer embeddings initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize SentenceTransformer: {e}")
    
    def _init_reranker(self):
        """Initialize reranker model."""
        if COHERE_AVAILABLE:
            try:
                api_key = os.getenv("COHERE_API_KEY")
                if api_key:
                    self.reranker = cohere.Client(api_key=api_key)
                    logger.info("✅ Cohere reranker initialized")
                else:
                    logger.warning("⚠️ COHERE_API_KEY not set, reranking disabled")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Cohere reranker: {e}")
    
    def is_available(self) -> bool:
        """Check if RAG service is available."""
        return (
            self.collection is not None and
            self.embedder is not None
        )
    
    def index_documents(
        self,
        documents: List[Document],
        batch_size: int = 100
    ) -> bool:
        """
        Index documents into the vector database.
        
        Args:
            documents: List of documents to index
            batch_size: Number of documents to process in each batch
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            logger.error("❌ RAG service not available")
            return False
        
        try:
            logger.info(f"📚 Indexing {len(documents)} documents...")
            
            # Generate embeddings
            texts = [doc.content for doc in documents]
            embeddings = self._generate_embeddings(texts)
            
            if not embeddings:
                logger.error("❌ Failed to generate embeddings")
                return False
            
            # Prepare data for ChromaDB
            ids = [doc.id for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            
            # Add embeddings to ChromaDB in batches
            for i in range(0, len(documents), batch_size):
                batch_ids = ids[i:i+batch_size]
                batch_embeddings = embeddings[i:i+batch_size]
                batch_texts = texts[i:i+batch_size]
                batch_metadatas = metadatas[i:i+batch_size]
                
                self.collection.add(
                    ids=batch_ids,
                    embeddings=batch_embeddings,
                    documents=batch_texts,
                    metadatas=batch_metadatas
                )
            
            logger.info(f"✅ Indexed {len(documents)} documents successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to index documents: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _generate_embeddings(self, texts: List[str]) -> Optional[List[List[float]]]:
        """Generate embeddings for texts."""
        if not self.embedder:
            return None
        
        try:
            if hasattr(self.embedder, 'embed_documents'):
                # LangChain embeddings
                embeddings = self.embedder.embed_documents(texts)
            elif hasattr(self.embedder, 'encode'):
                # SentenceTransformer
                embeddings = self.embedder.encode(texts, convert_to_numpy=False).tolist()
            else:
                logger.error("❌ Unknown embedder type")
                return None
            
            return embeddings
        except Exception as e:
            logger.error(f"❌ Failed to generate embeddings: {e}")
            return None
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Query string
            top_k: Number of documents to retrieve (defaults to self.top_k)
            filter_metadata: Optional metadata filters
            
        Returns:
            List of retrieval results sorted by relevance
        """
        if not self.is_available():
            logger.error("❌ RAG service not available")
            return []
        
        top_k = top_k or self.top_k
        
        try:
            # Generate query embedding
            query_embedding = self._generate_query_embedding(query)
            if not query_embedding:
                logger.error("❌ Failed to generate query embedding")
                return []
            
            # Retrieve from vector database
            where_clause = filter_metadata if filter_metadata else None
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_clause
            )
            
            # Parse results
            retrieval_results = []
            if results['ids'] and len(results['ids'][0]) > 0:
                for i, doc_id in enumerate(results['ids'][0]):
                    content = results['documents'][0][i] if results['documents'] else ""
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    distance = results['distances'][0][i] if results['distances'] else 1.0
                    
                    # Convert distance to similarity score (cosine distance -> similarity)
                    score = 1.0 - distance
                    
                    doc = Document(
                        id=doc_id,
                        content=content,
                        metadata=metadata,
                        embedding=None
                    )
                    
                    retrieval_results.append(RetrievalResult(
                        document=doc,
                        score=score,
                        rank=i + 1
                    ))
            
            # Rerank if enabled
            if self.use_reranking and self.reranker and len(retrieval_results) > 0:
                retrieval_results = self._rerank(query, retrieval_results)
            
            return retrieval_results[:self.rerank_top_k if self.use_reranking else top_k]
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve documents: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _generate_query_embedding(self, query: str) -> Optional[List[float]]:
        """Generate embedding for a single query."""
        if not self.embedder:
            return None
        
        try:
            if hasattr(self.embedder, 'embed_query'):
                # LangChain embeddings
                embedding = self.embedder.embed_query(query)
            elif hasattr(self.embedder, 'encode'):
                # SentenceTransformer
                embedding = self.embedder.encode([query], convert_to_numpy=False)[0].tolist()
            else:
                logger.error("❌ Unknown embedder type")
                return None
            
            return embedding
        except Exception as e:
            logger.error(f"❌ Failed to generate query embedding: {e}")
            return None
    
    def _rerank(
        self,
        query: str,
        results: List[RetrievalResult]
    ) -> List[RetrievalResult]:
        """
        Rerank retrieval results using Cohere reranker.
        
        Args:
            query: Original query
            results: Initial retrieval results
            
        Returns:
            Reranked results
        """
        if not self.reranker or len(results) == 0:
            return results
        
        try:
            # Prepare documents for reranking
            documents = [r.document.content for r in results]
            
            # Rerank using Cohere
            rerank_response = self.reranker.rerank(
                model="rerank-english-v3.0",
                query=query,
                documents=documents,
                top_n=self.rerank_top_k
            )
            
            # Reorder results based on reranking
            reranked_results = []
            for result in rerank_response.results:
                original_result = results[result.index]
                # Update score with rerank relevance score
                original_result.score = result.relevance_score
                reranked_results.append(original_result)
            
            # Sort by new score
            reranked_results.sort(key=lambda x: x.score, reverse=True)
            
            # Update ranks
            for i, result in enumerate(reranked_results):
                result.rank = i + 1
            
            logger.info(f"✅ Reranked {len(results)} results to top {len(reranked_results)}")
            return reranked_results
            
        except Exception as e:
            logger.warning(f"⚠️ Reranking failed, returning original results: {e}")
            return results
    
    def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents from the vector database."""
        if not self.is_available():
            return False
        
        try:
            self.collection.delete(ids=document_ids)
            logger.info(f"✅ Deleted {len(document_ids)} documents")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete documents: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        if not self.is_available():
            return {"error": "RAG service not available"}
        
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "embedding_model": self.embedding_model_type,
                "reranking_enabled": self.use_reranking and self.reranker is not None
            }
        except Exception as e:
            logger.error(f"❌ Failed to get collection stats: {e}")
            return {"error": str(e)}


# Global RAG service instance
_rag_service: Optional[RAGService] = None


def get_rag_service() -> Optional[RAGService]:
    """Get or create global RAG service instance."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service if _rag_service.is_available() else None

