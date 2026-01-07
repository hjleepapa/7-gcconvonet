# RAG Validation Quick Start Guide

## Quick Validation (5 minutes)

### Step 1: Install Dependencies
```bash
pip install chromadb sentence-transformers
# Optional for reranking:
pip install cohere
```

### Step 2: Set Environment Variables (Optional)
```bash
export OPENAI_API_KEY="your-key"  # For OpenAI embeddings (optional)
export COHERE_API_KEY="your-key"  # For reranking (optional)
```

### Step 3: Run Validation Script
```bash
python test_rag_validation.py
```

### Expected Output
```
============================================================
RAG Implementation Validation
============================================================

📚 Initializing knowledge base...
✅ Knowledge base initialized
✅ RAG service initialized

============================================================
Scenario 1: Document Indexing
============================================================
✅ Document indexed successfully
   Collection: convonet_knowledge_base
   Document count: 6
✅ Scenario 1 PASSED

============================================================
Scenario 2: Basic Retrieval
============================================================
✅ Query: 'How do I create a team?'
   Found 3 results
   1. Team Management (score: 0.856)
   2. Convonet Voice Commands (score: 0.723)
✅ Scenario 2 PASSED

...

============================================================
Validation Summary
============================================================
✅ Passed: 7
❌ Failed: 0
📊 Total: 7
📈 Success Rate: 100.0%

🎉 All tests passed!
```

---

## Manual Testing via Voice Assistant

### Step 1: Start the Application
```bash
python app.py
```

### Step 2: Navigate to Voice Assistant
Open: `http://localhost:5000/webrtc/voice-assistant`

### Step 3: Test RAG Queries
Ask the following questions:
1. "How do I create a team?"
2. "What voice commands are available?"
3. "Tell me about calendar integration"
4. "How does MCP work?"
5. "What LLM providers are supported?"

### Step 4: Verify Agent Behavior
- Check agent monitor: `http://localhost:5000/agent-monitor`
- Look for `search_knowledge_base` tool calls
- Verify responses include knowledge base information

---

## Individual Test Scenarios

### Test 1: Basic Retrieval
```python
from convonet.rag_service import get_rag_service

rag_service = get_rag_service()
results = rag_service.retrieve("How do I create a team?", top_k=5)

for result in results:
    print(f"{result.document.metadata.get('title')}: {result.score:.3f}")
```

### Test 2: Document Indexing
```python
from convonet.rag_indexer import DocumentIndexer

indexer = DocumentIndexer()
indexer.index_text(
    text="Your document content here...",
    title="Document Title",
    source="manual",
    category="documentation"
)
```

### Test 3: Hybrid Retrieval
```python
from convonet.hybrid_retrieval import HybridRetrieval

hybrid = HybridRetrieval()
result = hybrid.retrieve(
    query="What are my todos and how do I create a team?",
    use_rag=True
)

print(result.combined_context)
```

### Test 4: MCP Tool
```python
import asyncio
from convonet.mcps.local_servers.db_todo import search_knowledge_base

async def test():
    result = await search_knowledge_base("How do I create a team?", top_k=3)
    print(result)

asyncio.run(test())
```

---

## Troubleshooting

### Issue: "RAG service not available"
**Solution**: Install ChromaDB:
```bash
pip install chromadb
```

### Issue: "No results returned"
**Solution**: Initialize knowledge base:
```python
from convonet.rag_indexer import initialize_sample_knowledge_base
initialize_sample_knowledge_base()
```

### Issue: "Import errors"
**Solution**: Make sure you're in the project root:
```bash
cd "/Users/hj/Web Development Projects/2. Convonet-Anthropic"
python test_rag_validation.py
```

### Issue: "Slow retrieval"
**Solution**: 
- Use HuggingFace embeddings (local, faster)
- Reduce `top_k` parameter
- Disable reranking if not needed

---

## Validation Checklist

- [ ] Dependencies installed
- [ ] Knowledge base initialized
- [ ] Basic retrieval works
- [ ] Document indexing works
- [ ] Hybrid retrieval works
- [ ] MCP tool accessible
- [ ] Performance acceptable (< 1s)
- [ ] Agent integration works

---

## Next Steps

1. **Add Your Own Documents**: Index your documentation
2. **Customize Embeddings**: Choose embedding model based on your needs
3. **Fine-tune Reranking**: Adjust reranking parameters
4. **Monitor Performance**: Track retrieval latency and accuracy
5. **Evaluate Results**: Use RAGAS framework for automated evaluation

---

**Status**: ✅ Ready for validation
**Last Updated**: 2025-12-11

