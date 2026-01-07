# Interview Quick Reference - Cheat Sheet

## 🎯 Your Convonet Project → Interview Topics Mapping

### RAG System Design

| RAG Component | Your Current Implementation | ✅ IMPLEMENTED |
|--------------|----------------------------|---------------|
| **Indexing** | Database tables (todos, calendar_events) | ✅ Vector embeddings + ChromaDB |
| **Retrieval** | Tool-based (get_todos, get_calendar_events) | ✅ Semantic search + SQL hybrid |
| **Reranking** | N/A (direct tool results) | ✅ Cohere Rerank (optional) |
| **Generation** | LLM with tool results as context | ✅ LLM with retrieved documents |
| **Evaluation** | Manual testing | Manual testing (RAGAS framework can be added) |
| **Hybrid Retrieval** | Structured only | ✅ Structured + Unstructured combined |
| **Document Chunking** | N/A | ✅ Sentence/paragraph/fixed chunking |
| **Embedding Models** | N/A | ✅ OpenAI/HuggingFace/SentenceTransformers |
| **MCP Tool** | 36 tools | ✅ 37 tools (added search_knowledge_base) |

### ML System Design

| ML Component | Your Implementation |
|--------------|---------------------|
| **Pipeline** | STT → LLM → Emotion → TTS |
| **Models** | Deepgram (STT), Claude/Gemini/OpenAI (LLM), ElevenLabs (TTS) |
| **Latency** | Async processing, Redis caching, streaming |
| **Fallback** | Deepgram TTS if ElevenLabs fails |
| **Monitoring** | Sentry, custom logging |
| **State** | Redis checkpointing, conversation threads |

### Agentic AI

| Agent Feature | Your Implementation |
|---------------|---------------------|
| **Orchestration** | LangGraph with conditional routing |
| **Tools** | 36 MCP tools (database, calendar, teams, external APIs) |
| **State Management** | Redis checkpointer, thread-based conversations |
| **Multi-Step** | Sequential tool execution with state |
| **Error Handling** | Try-catch, fallback, retry logic |

---

## 💬 Key Talking Points

### 1. RAG System Design

**"How would you design a RAG system?"**
- Hybrid approach: Structured (SQL) + Unstructured (Vector)
- Two-stage retrieval: Semantic search → Rerank
- Evaluation: RAGAS framework, human evaluation
- Fine-tuning: Domain-specific SLMs for cost/latency

**"How do you handle retrieval for different data types?"**
- **Structured**: Direct SQL queries via MCP tools (get_todos, get_calendar_events, etc.)
- **Unstructured**: Vector embeddings (OpenAI/HuggingFace) + ChromaDB semantic search
- **Hybrid**: `HybridRetrieval` class intelligently combines both approaches
- **Reranking**: Cohere rerank-english-v3.0 for precision (top_k=20 → top_k=5)
- **MCP Integration**: `search_knowledge_base` tool for agent-based RAG retrieval

### 2. ML System Design

**"Walk me through your ML pipeline."**
- End-to-end: Voice → STT → LLM → Emotion → TTS
- Optimization: Streaming, caching, async processing
- Reliability: Fallback mechanisms, error handling
- Monitoring: Sentry, logging, metrics

**"How do you handle model selection?"**
- Multi-provider support (avoid vendor lock-in)
- Cost vs quality trade-offs
- Latency optimization
- Fallback strategies

### 3. Agentic AI

**"How do you orchestrate agents?"**
- LangGraph for workflow management
- Conditional routing (tools vs response)
- State management with Redis
- Multi-step tool execution

**"How would you design a multi-agent system?"**
- Specialized agents (productivity, team, calendar)
- Coordinator agent for routing
- Agent communication and context sharing
- Parallel vs sequential execution

---

## 📊 Architecture Diagrams to Draw

### Current System (What You Have)
```
User Voice
    ↓
[Deepgram STT] → Text
    ↓
[LangGraph Agent] → Tool Selection
    ↓
[MCP Tools] → Data Retrieval
    ↓
[LLM] → Response Generation
    ↓
[Emotion Detection] → Emotion
    ↓
[ElevenLabs TTS] → Voice Output
```

### ✅ IMPLEMENTED RAG System
```
User Query
    ↓
[Query Understanding] → Intent Detection
    ↓
[Hybrid Retrieval System]
    ├─ [Structured Retrieval] → MCP Tools (get_todos, get_calendar_events)
    └─ [Unstructured Retrieval] → RAG Service (ChromaDB + Embeddings)
    ↓
[Reranking] → Cohere Rerank (optional, top_k=20 → top_k=5)
    ↓
[Context Assembly] → Combined structured + unstructured context
    ↓
[LLM] → Generated Response with citations
    ↓
[Response] → Voice output with emotion
```

**Implementation Details:**
- **Vector DB**: ChromaDB with persistent storage
- **Embeddings**: OpenAI text-embedding-3-small (fallback: HuggingFace all-MiniLM-L6-v2)
- **Chunking**: Sentence/paragraph/fixed strategies (500 chars, 50 overlap)
- **Reranking**: Cohere rerank-english-v3.0 (optional)
- **MCP Tool**: `search_knowledge_base(query, top_k=5)` - 37th tool
- **Hybrid Retrieval**: `HybridRetrieval` class combines both approaches

### Proposed Multi-Agent System
```
User Query
    ↓
[Coordinator Agent] → Intent Detection
    ↓
[Route to Specialized Agent]
    ├─ Productivity Agent → Todos, Reminders
    ├─ Team Agent → Team management
    ├─ Calendar Agent → Scheduling
    └─ Knowledge Agent → RAG retrieval
    ↓
[Agent Collaboration] → Share context
    ↓
[Response Synthesis] → Final response
```

---

## 🔑 Key Code Examples to Reference

### 1. LangGraph Agent Orchestration
```python
# From assistant_graph_todo.py
builder = StateGraph(AgentState)
builder.add_node("assistant", self.assistant)
builder.add_node("tools", self.tools)
builder.add_conditional_edges("assistant", self.should_continue)
```

### 2. Hybrid Retrieval (Structured + Unstructured)
```python
# Structured retrieval via MCP tools
get_calendar_events()  # Structured retrieval
get_todos()  # User-specific retrieval
query_db()  # SQL-based retrieval

# Unstructured retrieval via RAG
from convonet.rag_service import get_rag_service
rag_service = get_rag_service()
results = rag_service.retrieve("How do I create a team?", top_k=5)

# Hybrid retrieval combining both
from convonet.hybrid_retrieval import HybridRetrieval
hybrid = HybridRetrieval()
result = hybrid.retrieve(query, structured_tools=tools, use_rag=True)
```

### 2b. RAG Service Implementation
```python
# From rag_service.py
class RAGService:
    def index_documents(self, documents: List[Document]) -> bool:
        # Generate embeddings and store in ChromaDB
        embeddings = self._generate_embeddings(texts)
        self.collection.add(ids=ids, embeddings=embeddings, documents=texts)
    
    def retrieve(self, query: str, top_k: int = 5) -> List[RetrievalResult]:
        # Semantic search with optional reranking
        query_embedding = self._generate_query_embedding(query)
        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
        if self.use_reranking:
            results = self._rerank(query, results)
        return results
```

### 3. Multi-Stage Pipeline
```python
# Voice AI pipeline
STT → LLM → Emotion → TTS
# Each stage is a separate model/service
```

### 4. State Management
```python
# Redis checkpointing
checkpointer = RedisSaver(redis_client)
graph = builder.compile(checkpointer=checkpointer)
```

### 5. RAG Implementation Files
```python
# convonet/rag_service.py - Core RAG service
rag_service = RAGService(
    collection_name="convonet_knowledge_base",
    embedding_model="openai",  # or "huggingface", "sentence-transformers"
    use_reranking=True,
    top_k=20,
    rerank_top_k=5
)

# convonet/rag_indexer.py - Document indexing
indexer = DocumentIndexer()
indexer.index_text(text, title, source="knowledge_base", category="documentation")

# convonet/hybrid_retrieval.py - Hybrid retrieval
hybrid = HybridRetrieval()
result = hybrid.retrieve(query, structured_tools=tools, use_rag=True)

# convonet/mcps/local_servers/db_todo.py - MCP tool
@mcp.tool()
async def search_knowledge_base(query: str, top_k: int = 5) -> str:
    # RAG retrieval via MCP tool
```

---

## 🎤 Sample Answers

### Q: "How would you improve your current system for RAG?"

**A:** "I've actually implemented a complete RAG system in Convonet! Here's what I built:
1. ✅ **Document Indexing**: ChromaDB vector database with OpenAI/HuggingFace embeddings
2. ✅ **Semantic Search**: Vector similarity search with cosine distance
3. ✅ **Reranking**: Cohere rerank-english-v3.0 for precision (optional)
4. ✅ **Hybrid Retrieval**: Combines structured (MCP tools) + unstructured (RAG) retrieval
5. ✅ **MCP Integration**: Added `search_knowledge_base` as the 37th tool
6. **Future Enhancement**: RAGAS evaluation framework for metrics

The system uses ChromaDB for persistence, supports multiple embedding models, and intelligently combines structured SQL queries with semantic vector search for comprehensive retrieval."

### Q: "How do you handle production ML systems?"

**A:** "In my Convonet project, I focus on:
1. **Reliability**: Fallback mechanisms (Deepgram if ElevenLabs fails)
2. **Latency**: Async processing, Redis caching, streaming
3. **Monitoring**: Sentry for errors, custom metrics for performance
4. **State Management**: Redis for conversation state and caching
5. **Multi-Provider**: Support multiple LLMs to avoid vendor lock-in"

### Q: "How would you design a multi-agent system?"

**A:** "I'd extend my current LangGraph architecture:
1. **Specialized Agents**: One for productivity, one for teams, one for calendar
2. **Coordinator**: Routes queries to appropriate agent
3. **Agent Communication**: Share context via shared state
4. **Orchestration**: Use LangGraph's multi-agent patterns
5. **Evaluation**: Track agent performance and routing accuracy"

---

## ⚡ Quick Facts About Your Project

- **Agent Framework**: LangGraph with conditional routing
- **Tools**: 37 MCP tools (36 original + 1 RAG tool: `search_knowledge_base`)
- **RAG System**: ✅ ChromaDB + OpenAI/HuggingFace embeddings + Cohere reranking
- **Hybrid Retrieval**: ✅ Structured (SQL/tools) + Unstructured (vector search)
- **LLM Providers**: Claude, Gemini, OpenAI (multi-provider support)
- **State Management**: Redis checkpointing and caching
- **Voice Pipeline**: STT (Deepgram) → LLM → Emotion → TTS (ElevenLabs)
- **Error Handling**: Fallback mechanisms, retry logic
- **Monitoring**: Sentry integration, custom logging
- **Architecture**: Async processing, streaming, WebRTC
- **Document Chunking**: Sentence/paragraph/fixed strategies (500 chars, 50 overlap)

---

## 🎯 Interview Success Tips

1. **Start with Your Experience**: "In my Convonet project, I built..."
2. **Show Thinking Process**: Walk through your reasoning
3. **Discuss Trade-offs**: Cost vs quality, latency vs accuracy
4. **Propose Enhancements**: "For RAG, I would add..."
5. **Ask Questions**: Show you think about edge cases
6. **Reference Code**: "In my implementation, I did X because..."

---

## 📝 Questions to Ask Interviewer

1. "What's your current RAG architecture? Vector-only or hybrid?"
2. "How do you handle multi-agent orchestration?"
3. "What's your strategy for model fine-tuning and SLMs?"
4. "How do you evaluate RAG system performance?"
5. "What are the biggest challenges in production ML systems?"

Good luck! 🚀

