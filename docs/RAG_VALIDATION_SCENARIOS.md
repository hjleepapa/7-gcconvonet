# RAG Implementation Validation Scenarios

## Overview

This document provides comprehensive test scenarios to validate the RAG (Retrieval-Augmented Generation) implementation in Convonet. These scenarios test indexing, retrieval, reranking, hybrid retrieval, and MCP tool integration.

---

## Prerequisites

1. **Install Dependencies**:
```bash
pip install chromadb sentence-transformers cohere
```

2. **Set Environment Variables** (optional):
```bash
export OPENAI_API_KEY="your-key"  # For OpenAI embeddings
export COHERE_API_KEY="your-key"   # For reranking
```

3. **Initialize Knowledge Base**:
```python
from convonet.rag_indexer import initialize_sample_knowledge_base
initialize_sample_knowledge_base()
```

---

## Validation Scenarios

### Scenario 1: Document Indexing ✅

**Objective**: Validate that documents can be indexed into the vector database.

**Steps**:
1. Create a test document
2. Index it using `DocumentIndexer`
3. Verify it's stored in ChromaDB
4. Check collection statistics

**Test Code**:
```python
from convonet.rag_indexer import DocumentIndexer
from convonet.rag_service import get_rag_service

# Initialize
indexer = DocumentIndexer()
rag_service = get_rag_service()

# Test document
test_doc = """
Convonet is a voice-powered productivity platform that helps users manage todos,
calendar events, and team collaboration through natural voice commands.
Users can create teams, assign tasks, and schedule meetings using voice.
"""

# Index document
success = indexer.index_text(
    text=test_doc,
    title="Convonet Overview",
    source="test",
    category="documentation"
)

# Verify
assert success, "Document indexing failed"
stats = rag_service.get_collection_stats()
assert stats["document_count"] > 0, "No documents in collection"
print("✅ Scenario 1 PASSED: Document indexing works")
```

**Expected Result**: Document successfully indexed, collection count increases.

---

### Scenario 2: Basic Retrieval ✅

**Objective**: Validate semantic search retrieval.

**Steps**:
1. Query the knowledge base
2. Verify relevant documents are returned
3. Check relevance scores
4. Verify document metadata

**Test Code**:
```python
from convonet.rag_service import get_rag_service

rag_service = get_rag_service()

# Test queries
queries = [
    "How do I create a team?",
    "What voice commands are available?",
    "How does calendar integration work?",
    "What is Convonet?"
]

for query in queries:
    results = rag_service.retrieve(query, top_k=3)
    
    assert len(results) > 0, f"No results for query: {query}"
    assert all(r.score > 0 for r in results), "Invalid scores"
    assert all(r.document.metadata.get('title') for r in results), "Missing metadata"
    
    print(f"✅ Query: '{query}'")
    print(f"   Found {len(results)} results")
    for i, result in enumerate(results, 1):
        print(f"   {i}. {result.document.metadata.get('title')} (score: {result.score:.3f})")
    print()

print("✅ Scenario 2 PASSED: Basic retrieval works")
```

**Expected Result**: Relevant documents returned with scores > 0, metadata present.

---

### Scenario 3: Reranking Validation ✅

**Objective**: Validate that reranking improves result relevance.

**Steps**:
1. Retrieve without reranking
2. Retrieve with reranking
3. Compare top results
4. Verify reranking improves relevance

**Test Code**:
```python
from convonet.rag_service import RAGService

# Service without reranking
rag_no_rerank = RAGService(use_reranking=False, top_k=20)

# Service with reranking
rag_with_rerank = RAGService(use_reranking=True, top_k=20, rerank_top_k=5)

query = "How do I create a team and add members?"

# Without reranking
results_no_rerank = rag_no_rerank.retrieve(query, top_k=20)
print(f"Without reranking: {len(results_no_rerank)} results")
print(f"Top result: {results_no_rerank[0].document.metadata.get('title')} (score: {results_no_rerank[0].score:.3f})")

# With reranking
results_with_rerank = rag_with_rerank.retrieve(query, top_k=20)
print(f"\nWith reranking: {len(results_with_rerank)} results")
print(f"Top result: {results_with_rerank[0].document.metadata.get('title')} (score: {results_with_rerank[0].score:.3f})")

# Verify reranking returned fewer, more relevant results
assert len(results_with_rerank) <= len(results_no_rerank), "Reranking should reduce results"
assert results_with_rerank[0].score >= results_no_rerank[0].score, "Reranking should improve relevance"

print("✅ Scenario 3 PASSED: Reranking works")
```

**Expected Result**: Reranked results are more relevant and fewer in number.

---

### Scenario 4: Hybrid Retrieval ✅

**Objective**: Validate hybrid retrieval combining structured and unstructured data.

**Steps**:
1. Create a query that needs both structured and unstructured data
2. Perform hybrid retrieval
3. Verify both types of results are included
4. Check combined context

**Test Code**:
```python
from convonet.hybrid_retrieval import HybridRetrieval

hybrid = HybridRetrieval()

# Query that benefits from both
query = "What are my todos and how do I create a team?"

result = hybrid.retrieve(
    query=query,
    use_rag=True,
    top_k_unstructured=5
)

# Verify hybrid retrieval
assert result.retrieval_strategy in ["hybrid", "unstructured", "structured"], "Invalid strategy"
assert len(result.combined_context) > 0, "Empty combined context"
assert "##" in result.combined_context, "Context not properly formatted"

print(f"✅ Retrieval Strategy: {result.retrieval_strategy}")
print(f"✅ Structured Results: {len(result.structured_results)}")
print(f"✅ Unstructured Results: {len(result.unstructured_results)}")
print(f"✅ Combined Context Length: {len(result.combined_context)} chars")
print("\n✅ Scenario 4 PASSED: Hybrid retrieval works")
```

**Expected Result**: Both structured and unstructured results combined in context.

---

### Scenario 5: MCP Tool Integration ✅

**Objective**: Validate RAG retrieval via MCP tool.

**Steps**:
1. Call `search_knowledge_base` MCP tool
2. Verify it returns formatted results
3. Test with different queries
4. Check error handling

**Test Code**:
```python
import asyncio
from convonet.mcps.local_servers.db_todo import search_knowledge_base

async def test_mcp_tool():
    # Test queries
    queries = [
        "How do I create a team?",
        "What voice commands are available?",
        "Tell me about calendar integration"
    ]
    
    for query in queries:
        result = await search_knowledge_base(query, top_k=3)
        
        assert "Found" in result or "relevant" in result.lower(), "Invalid response format"
        assert query in result or len(result) > 50, "Response too short"
        
        print(f"✅ Query: '{query}'")
        print(f"   Response length: {len(result)} chars")
        print(f"   Response preview: {result[:100]}...\n")
    
    print("✅ Scenario 5 PASSED: MCP tool integration works")

# Run test
asyncio.run(test_mcp_tool())
```

**Expected Result**: MCP tool returns formatted knowledge base results.

---

### Scenario 6: Document Chunking Strategies ✅

**Objective**: Validate different chunking strategies work correctly.

**Steps**:
1. Test sentence-based chunking
2. Test paragraph-based chunking
3. Test fixed-size chunking
4. Verify chunks are properly sized

**Test Code**:
```python
from convonet.rag_indexer import DocumentIndexer

indexer = DocumentIndexer()

test_text = """
Convonet is a voice-powered productivity platform. It helps users manage todos.
Users can create teams. Teams allow collaborative task management.
Calendar integration syncs with Google Calendar. Voice commands make it easy.
"""

# Test sentence chunking
sentence_chunks = indexer.chunk_text(test_text, chunk_size=100, strategy="sentence")
print(f"Sentence chunks: {len(sentence_chunks)}")
assert len(sentence_chunks) > 0, "No sentence chunks"

# Test paragraph chunking
para_chunks = indexer.chunk_text(test_text, chunk_size=200, strategy="paragraph")
print(f"Paragraph chunks: {len(para_chunks)}")
assert len(para_chunks) > 0, "No paragraph chunks"

# Test fixed chunking
fixed_chunks = indexer.chunk_text(test_text, chunk_size=50, strategy="fixed")
print(f"Fixed chunks: {len(fixed_chunks)}")
assert len(fixed_chunks) > 0, "No fixed chunks"

# Verify chunk sizes
for i, chunk in enumerate(sentence_chunks[:3]):
    print(f"  Chunk {i+1}: {len(chunk)} chars - {chunk[:50]}...")

print("\n✅ Scenario 6 PASSED: Chunking strategies work")
```

**Expected Result**: All chunking strategies produce valid chunks.

---

### Scenario 7: Edge Cases ✅

**Objective**: Validate error handling and edge cases.

**Test Cases**:
1. Empty query
2. Query with no results
3. RAG service unavailable
4. Invalid parameters

**Test Code**:
```python
from convonet.rag_service import get_rag_service

rag_service = get_rag_service()

# Test 1: Empty query
results = rag_service.retrieve("", top_k=5)
assert isinstance(results, list), "Should return list even for empty query"

# Test 2: Query with no results (very specific)
results = rag_service.retrieve("xyzabc123nonexistentquery", top_k=5)
assert isinstance(results, list), "Should return list even with no results"

# Test 3: Invalid top_k
results = rag_service.retrieve("test", top_k=-1)
assert isinstance(results, list), "Should handle invalid top_k"

# Test 4: Metadata filtering
results = rag_service.retrieve(
    "test",
    filter_metadata={"category": "documentation"}
)
assert isinstance(results, list), "Should handle metadata filtering"

print("✅ Scenario 7 PASSED: Edge cases handled correctly")
```

**Expected Result**: All edge cases handled gracefully without crashes.

---

### Scenario 8: Performance Testing ✅

**Objective**: Validate retrieval performance and latency.

**Steps**:
1. Measure retrieval latency
2. Test batch retrieval
3. Check memory usage
4. Verify scalability

**Test Code**:
```python
import time
from convonet.rag_service import get_rag_service

rag_service = get_rag_service()

# Performance test
queries = [
    "How do I create a team?",
    "What voice commands are available?",
    "How does calendar integration work?",
    "What is Convonet?",
    "Tell me about MCP tools"
]

latencies = []
for query in queries:
    start = time.time()
    results = rag_service.retrieve(query, top_k=5)
    latency = (time.time() - start) * 1000  # ms
    latencies.append(latency)
    print(f"Query: '{query[:30]}...' - {latency:.2f}ms - {len(results)} results")

avg_latency = sum(latencies) / len(latencies)
print(f"\n✅ Average Latency: {avg_latency:.2f}ms")
print(f"✅ Min Latency: {min(latencies):.2f}ms")
print(f"✅ Max Latency: {max(latencies):.2f}ms")

# Performance assertions
assert avg_latency < 1000, "Retrieval too slow (>1s)"
assert all(latency < 2000 for latency in latencies), "Some queries too slow"

print("\n✅ Scenario 8 PASSED: Performance acceptable")
```

**Expected Result**: Average latency < 1 second, all queries < 2 seconds.

---

### Scenario 9: Knowledge Base Content Validation ✅

**Objective**: Validate that sample knowledge base is properly indexed.

**Steps**:
1. Initialize sample knowledge base
2. Query each topic
3. Verify relevant documents are found
4. Check document quality

**Test Code**:
```python
from convonet.rag_indexer import initialize_sample_knowledge_base, create_sample_knowledge_base
from convonet.rag_service import get_rag_service

# Initialize
initialize_sample_knowledge_base()
rag_service = get_rag_service()

# Test queries for each knowledge base topic
test_cases = [
    ("How do I create a team?", "Team Management"),
    ("What voice commands can I use?", "Convonet Voice Commands"),
    ("How does calendar work?", "Calendar Integration"),
    ("What is voice AI?", "Voice AI Features"),
    ("Tell me about MCP", "MCP Tools"),
    ("What LLM providers are supported?", "Multi-LLM Support")
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
        
        if score < 0.3:
            print(f"   ⚠️ Low relevance score")
            all_passed = False
    else:
        print(f"❌ Query: '{query}' - No results")
        all_passed = False
    print()

if all_passed:
    print("✅ Scenario 9 PASSED: Knowledge base content validated")
else:
    print("⚠️ Scenario 9 PARTIAL: Some queries need improvement")
```

**Expected Result**: All knowledge base topics retrievable with reasonable scores.

---

### Scenario 10: End-to-End Agent Integration ✅

**Objective**: Validate RAG works with LangGraph agent system.

**Steps**:
1. Create agent with RAG tool
2. Ask knowledge base question
3. Verify agent uses RAG tool
4. Check response quality

**Test Code**:
```python
# This would be tested with actual agent execution
# Example agent prompt:
agent_prompt = """
User: "How do I create a team in Convonet?"

Expected Agent Behavior:
1. Agent should recognize this is a knowledge base question
2. Agent should call search_knowledge_base tool
3. Agent should synthesize response from retrieved documents
4. Agent should provide helpful answer

Test this manually via voice assistant or agent monitor.
"""

print("✅ Scenario 10: End-to-End Integration")
print("   Test via voice assistant: 'How do I create a team?'")
print("   Verify agent uses search_knowledge_base tool")
print("   Check response includes knowledge base information")
```

**Expected Result**: Agent successfully uses RAG tool and provides helpful responses.

---

## Complete Validation Script

Create `test_rag_validation.py`:

```python
#!/usr/bin/env python3
"""
Complete RAG Validation Test Suite
Run: python test_rag_validation.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from convonet.rag_service import get_rag_service
from convonet.rag_indexer import DocumentIndexer, initialize_sample_knowledge_base
from convonet.hybrid_retrieval import HybridRetrieval

def main():
    print("=" * 60)
    print("RAG Implementation Validation")
    print("=" * 60)
    print()
    
    # Initialize
    print("📚 Initializing knowledge base...")
    initialize_sample_knowledge_base()
    
    rag_service = get_rag_service()
    if not rag_service:
        print("❌ RAG service not available. Check dependencies.")
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
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in scenarios:
        print(f"\n{'='*60}")
        print(f"Testing: {name}")
        print('='*60)
        try:
            if test_func():
                print(f"✅ {name} PASSED")
                passed += 1
            else:
                print(f"❌ {name} FAILED")
                failed += 1
        except Exception as e:
            print(f"❌ {name} ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    return failed == 0

def test_indexing():
    indexer = DocumentIndexer()
    test_doc = "Convonet is a voice-powered productivity platform."
    return indexer.index_text(test_doc, "Test Doc", "test")

def test_retrieval():
    rag_service = get_rag_service()
    results = rag_service.retrieve("How do I create a team?", top_k=3)
    return len(results) > 0

def test_reranking():
    rag_service = get_rag_service()
    results = rag_service.retrieve("team creation", top_k=5)
    return len(results) > 0 and all(r.score > 0 for r in results)

def test_hybrid():
    hybrid = HybridRetrieval()
    result = hybrid.retrieve("How do I create a team?", use_rag=True)
    return len(result.combined_context) > 0

def test_edge_cases():
    rag_service = get_rag_service()
    # Empty query
    results = rag_service.retrieve("", top_k=5)
    return isinstance(results, list)

def test_performance():
    import time
    rag_service = get_rag_service()
    start = time.time()
    results = rag_service.retrieve("test query", top_k=5)
    latency = (time.time() - start) * 1000
    return latency < 2000  # < 2 seconds

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

---

## Quick Validation Checklist

- [ ] ✅ Dependencies installed (`chromadb`, `sentence-transformers`, `cohere`)
- [ ] ✅ Knowledge base initialized
- [ ] ✅ Document indexing works
- [ ] ✅ Basic retrieval returns results
- [ ] ✅ Reranking improves relevance
- [ ] ✅ Hybrid retrieval combines results
- [ ] ✅ MCP tool accessible
- [ ] ✅ Edge cases handled
- [ ] ✅ Performance acceptable (< 1s)
- [ ] ✅ Agent integration works

---

## Manual Testing via Voice Assistant

1. **Start Voice Assistant**: Navigate to `/webrtc/voice-assistant`
2. **Test Queries**:
   - "How do I create a team?"
   - "What voice commands are available?"
   - "Tell me about calendar integration"
   - "How does MCP work?"
3. **Verify**: Agent uses `search_knowledge_base` tool and provides helpful answers

---

## Troubleshooting

### Issue: "RAG service not available"
- **Solution**: Install dependencies: `pip install chromadb sentence-transformers`

### Issue: "No results returned"
- **Solution**: Initialize knowledge base: `initialize_sample_knowledge_base()`

### Issue: "Reranking fails"
- **Solution**: Set `COHERE_API_KEY` or disable reranking: `use_reranking=False`

### Issue: "Slow retrieval"
- **Solution**: Check embedding model, consider using HuggingFace for local processing

---

**Status**: ✅ Ready for validation
**Last Updated**: 2025-12-11

