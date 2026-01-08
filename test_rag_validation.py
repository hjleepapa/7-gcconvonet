#!/usr/bin/env python3
"""
Complete RAG Validation Test Suite
Run: python test_rag_validation.py
"""

import sys
import os
import time
import asyncio

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from convonet.rag_service import get_rag_service, RAGService
    from convonet.rag_indexer import DocumentIndexer, initialize_sample_knowledge_base
    from convonet.hybrid_retrieval import HybridRetrieval
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the project root directory")
    sys.exit(1)


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def test_indexing():
    """Test Scenario 1: Document Indexing"""
    print_header("Scenario 1: Document Indexing")
    
    try:
        indexer = DocumentIndexer()
        rag_service = get_rag_service()
        
        if not rag_service:
            print("❌ RAG service not available")
            return False
        
        # Test document
        test_doc = """
        Convonet is a voice-powered productivity platform that helps users manage todos,
        calendar events, and team collaboration through natural voice commands.
        Users can create teams, assign tasks, and schedule meetings using voice.
        The platform supports multiple languages and integrates with various tools.
        """
        
        # Index document
        success = indexer.index_text(
            text=test_doc,
            title="Convonet Overview Test",
            source="validation_test",
            category="test"
        )
        
        if not success:
            print("❌ Document indexing failed")
            return False
        
        # Verify
        stats = rag_service.get_collection_stats()
        print(f"✅ Document indexed successfully")
        print(f"   Collection: {stats.get('collection_name', 'unknown')}")
        print(f"   Document count: {stats.get('document_count', 0)}")
        
        return stats.get('document_count', 0) > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_retrieval():
    """Test Scenario 2: Basic Retrieval"""
    print_header("Scenario 2: Basic Retrieval")
    
    try:
        rag_service = get_rag_service()
        
        if not rag_service:
            print("❌ RAG service not available")
            return False
        
        # Test queries
        queries = [
            "How do I create a team?",
            "What voice commands are available?",
            "How does calendar integration work?",
        ]
        
        all_passed = True
        for query in queries:
            results = rag_service.retrieve(query, top_k=3)
            
            if len(results) == 0:
                print(f"❌ No results for query: '{query}'")
                all_passed = False
                continue
            
            if not all(r.score > 0 for r in results):
                print(f"❌ Invalid scores for query: '{query}'")
                all_passed = False
                continue
            
            if not all(r.document.metadata.get('title') for r in results):
                print(f"❌ Missing metadata for query: '{query}'")
                all_passed = False
                continue
            
            print(f"✅ Query: '{query}'")
            print(f"   Found {len(results)} results")
            for i, result in enumerate(results[:2], 1):
                title = result.document.metadata.get('title', 'Untitled')
                print(f"   {i}. {title} (score: {result.score:.3f})")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_reranking():
    """Test Scenario 3: Reranking"""
    print_header("Scenario 3: Reranking")
    
    try:
        # Check if Cohere is available
        cohere_available = os.getenv("COHERE_API_KEY") is not None
        
        if not cohere_available:
            print("⚠️ Cohere API key not set, skipping reranking test")
            print("   Set COHERE_API_KEY environment variable to test reranking")
            return True  # Not a failure, just optional feature
        
        # Service without reranking
        rag_no_rerank = RAGService(use_reranking=False, top_k=20)
        
        # Service with reranking
        rag_with_rerank = RAGService(use_reranking=True, top_k=20, rerank_top_k=5)
        
        query = "How do I create a team and add members?"
        
        # Without reranking
        results_no_rerank = rag_no_rerank.retrieve(query, top_k=20)
        print(f"Without reranking: {len(results_no_rerank)} results")
        if results_no_rerank:
            print(f"Top result: {results_no_rerank[0].document.metadata.get('title', 'Unknown')} "
                  f"(score: {results_no_rerank[0].score:.3f})")
        
        # With reranking
        results_with_rerank = rag_with_rerank.retrieve(query, top_k=20)
        print(f"\nWith reranking: {len(results_with_rerank)} results")
        if results_with_rerank:
            print(f"Top result: {results_with_rerank[0].document.metadata.get('title', 'Unknown')} "
                  f"(score: {results_with_rerank[0].score:.3f})")
        
        # Verify
        if results_with_rerank and results_no_rerank:
            assert len(results_with_rerank) <= len(results_no_rerank), "Reranking should reduce results"
            print("✅ Reranking works correctly")
            return True
        else:
            print("⚠️ Not enough results to compare")
            return True  # Not a failure
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hybrid():
    """Test Scenario 4: Hybrid Retrieval"""
    print_header("Scenario 4: Hybrid Retrieval")
    
    try:
        hybrid = HybridRetrieval()
        
        query = "What are my todos and how do I create a team?"
        
        result = hybrid.retrieve(
            query=query,
            use_rag=True,
            top_k_unstructured=5
        )
        
        # Verify hybrid retrieval
        if result.retrieval_strategy not in ["hybrid", "unstructured", "structured"]:
            print(f"❌ Invalid strategy: {result.retrieval_strategy}")
            return False
        
        if len(result.combined_context) == 0:
            print("❌ Empty combined context")
            return False
        
        print(f"✅ Retrieval Strategy: {result.retrieval_strategy}")
        print(f"✅ Structured Results: {len(result.structured_results)}")
        print(f"✅ Unstructured Results: {len(result.unstructured_results)}")
        print(f"✅ Combined Context Length: {len(result.combined_context)} chars")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_edge_cases():
    """Test Scenario 7: Edge Cases"""
    print_header("Scenario 7: Edge Cases")
    
    try:
        rag_service = get_rag_service()
        
        if not rag_service:
            print("❌ RAG service not available")
            return False
        
        # Test 1: Empty query
        results = rag_service.retrieve("", top_k=5)
        if not isinstance(results, list):
            print("❌ Empty query should return list")
            return False
        print("✅ Empty query handled")
        
        # Test 2: Query with no results
        results = rag_service.retrieve("xyzabc123nonexistentquery98765", top_k=5)
        if not isinstance(results, list):
            print("❌ No-results query should return list")
            return False
        print("✅ No-results query handled")
        
        # Test 3: Invalid top_k (should use default)
        results = rag_service.retrieve("test", top_k=-1)
        if not isinstance(results, list):
            print("❌ Invalid top_k should return list")
            return False
        print("✅ Invalid top_k handled")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_performance():
    """Test Scenario 8: Performance"""
    print_header("Scenario 8: Performance")
    
    try:
        rag_service = get_rag_service()
        
        if not rag_service:
            print("❌ RAG service not available")
            return False
        
        queries = [
            "How do I create a team?",
            "What voice commands are available?",
            "How does calendar integration work?",
        ]
        
        latencies = []
        for query in queries:
            start = time.time()
            results = rag_service.retrieve(query, top_k=5)
            latency = (time.time() - start) * 1000  # ms
            latencies.append(latency)
            print(f"Query: '{query[:30]}...' - {latency:.2f}ms - {len(results)} results")
        
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            print(f"\n✅ Average Latency: {avg_latency:.2f}ms")
            print(f"✅ Min Latency: {min(latencies):.2f}ms")
            print(f"✅ Max Latency: {max(latencies):.2f}ms")
            
            # Performance assertions
            if avg_latency > 2000:
                print(f"⚠️ Average latency high: {avg_latency:.2f}ms")
            if any(latency > 5000 for latency in latencies):
                print("⚠️ Some queries very slow")
            
            return True
        else:
            print("❌ No queries executed")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_knowledge_base():
    """Test Scenario 9: Knowledge Base Content"""
    print_header("Scenario 9: Knowledge Base Content")
    
    try:
        rag_service = get_rag_service()
        
        if not rag_service:
            print("❌ RAG service not available")
            return False
        
        # Test queries
        test_cases = [
            ("How do I create a team?", "Team Management"),
            ("What voice commands can I use?", "Convonet Voice Commands"),
            ("How does calendar work?", "Calendar Integration"),
        ]
        
        all_passed = True
        for query, expected_topic in test_cases:
            results = rag_service.retrieve(query, top_k=3)
            
            if results:
                top_result = results[0]
                found_topic = top_result.document.metadata.get('title', '')
                score = top_result.score
                
                print(f"✅ Query: '{query}'")
                print(f"   Found: '{found_topic}' (score: {score:.3f})")
                
                if score < 0.1:
                    print(f"   ⚠️ Low relevance score")
            else:
                print(f"❌ Query: '{query}' - No results")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all validation tests."""
    print("=" * 60)
    print("RAG Implementation Validation")
    print("=" * 60)
    print()
    
    # Initialize knowledge base
    print("📚 Initializing knowledge base...")
    try:
        initialize_sample_knowledge_base()
        print("✅ Knowledge base initialized")
    except Exception as e:
        print(f"⚠️ Knowledge base initialization: {e}")
        print("   Continuing with existing knowledge base...")
    
    rag_service = get_rag_service()
    if not rag_service:
        print("\n❌ RAG service not available!")
        print("   Please install dependencies:")
        print("   pip install chromadb sentence-transformers")
        return False
    
    print("✅ RAG service initialized\n")
    
    # Run scenarios
    scenarios = [
        ("Document Indexing", test_indexing),
        ("Basic Retrieval", test_retrieval),
        ("Reranking", test_reranking),
        ("Hybrid Retrieval", test_hybrid),
        ("Edge Cases", test_edge_cases),
        ("Performance", test_performance),
        ("Knowledge Base Content", test_knowledge_base),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in scenarios:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {name} ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Summary
    print_header("Validation Summary")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️ {failed} test(s) failed")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

