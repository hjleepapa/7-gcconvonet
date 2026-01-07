# Hackathon Submission Text

## Project Description

**Convonet: Voice-Powered Agentic AI Productivity Platform**

Convonet is a production-ready, enterprise-grade voice AI productivity platform that transforms browsers, voices, clouds, and tools into cohesive, intelligent agents. The system enables users to interact naturally through voice commands to manage todos, calendar events, team collaboration, and external integrations—all orchestrated by a sophisticated multi-agent AI system powered by LangGraph. The platform seamlessly integrates ElevenLabs for emotion-aware, multilingual voice synthesis, Deepgram for automatic language detection and transcription, and orchestrates 36+ tools via the Model Context Protocol (MCP) to deliver a complete agentic AI experience that understands context, executes complex workflows, and adapts to user emotions and languages in real-time.

**Working Prototype Stability**: Deployed and running in production on Render.com with 99%+ uptime. Features comprehensive error handling with multi-layer fallbacks (ElevenLabs → Deepgram TTS, Gemini → Claude → OpenAI), Redis checkpointing for state recovery, Sentry monitoring, and real-world testing across 30+ languages including Korean, Japanese, and English.

**Technical Complexity**: Multimodal architecture combining Deepgram STT (automatic language detection), ElevenLabs TTS (emotion-aware, multilingual), and multi-LLM support (Claude 3.5 Sonnet, Gemini 2.5 Flash, GPT-4o). Orchestrates 36 MCP tools via LangGraph with conditional routing, multi-step execution, and complete tool result tracking. Hybrid streaming implementation optimized for different LLM providers, WebRTC real-time voice interaction, and enterprise-grade state management.

**Innovation & Creativity**: 
1. **Emotion-Aware Voice AI** - First-of-its-kind integration detecting user emotions and adapting ElevenLabs TTS voice tone accordingly
2. **Hybrid Retrieval System** - Combines structured tool-based retrieval (MCP) with unstructured vector search capability
3. **Multi-Language Pipeline** - Automatic language detection → Native-accent TTS in 29+ languages without manual switching
4. **Unified Agent Architecture** - Single codebase supporting multiple LLM providers with consistent LangGraph orchestration
5. **Voice Cloning Integration** - Personal voice cloning in < 1 minute for unique user experiences

**Real-World Impact**: Enables hands-free productivity for enterprise teams, supports global collaboration through multi-language voice interaction, automates complex multi-step workflows, and integrates seamlessly with existing tools (Google Calendar, Slack, GitHub). Demonstrates production-ready patterns for MCP integration, multi-provider LLM orchestration, and enterprise-scale agentic AI deployment.

**Theme Alignment - Browsers, Voices, Clouds, and Tools → Cohesive Agents**:

- **🌐 Browsers**: WebRTC voice assistant, real-time agent monitor dashboard, tool execution GUI, responsive web interface
- **🎤 Voices**: ElevenLabs emotion-aware multilingual TTS, Deepgram STT with automatic language detection (30+ languages), voice cloning, real-time streaming
- **☁️ Clouds**: Render.com production hosting, Redis Cloud 5.0+ for distributed caching, session management, state persistence, and agent graph caching, PostgreSQL database, Sentry monitoring, Google Cloud APIs
- **🔧 Tools**: Redis 5.0+ for state management, 36 MCP tools (database, calendar, teams, external APIs), LangGraph orchestration, Composio integrations (Slack, GitHub, Gmail, Jira)
- **🤖 Cohesive Agents**: Unified system that understands (multi-language voice), reasons (multi-LLM), acts (tool orchestration), responds (emotion-aware voice), remembers (Redis state), and adapts (user preferences)

---

## Complete Technology Stack

### Core Frameworks & Libraries
- **Flask 3.0+** - Web framework
- **LangGraph 0.4.5+** - Agent orchestration and state management
- **LangChain Core 0.3.0+** - LLM framework
- **SQLAlchemy 2.0+** - Database ORM
- **Flask-SocketIO 5.0+** - WebSocket support
- **Eventlet 0.33.0+** - Async networking
- **Redis 5.0+** - Distributed caching, session management, state persistence, agent graph caching, voice preferences storage
- **Sentry SDK** - Error tracking and monitoring

### AI & LLM Providers
- **Anthropic Claude 3.5 Sonnet** (via langchain-anthropic 0.3.0+)
- **Google Gemini 2.5 Flash** (via google-genai 0.2.0+)
- **OpenAI GPT-4o** (via langchain-openai 0.2.0+)

### Voice AI Services
- **ElevenLabs SDK 1.0+** - TTS with voice cloning, emotions, multilingual support
  - Model: `eleven_multilingual_v2`
  - Features: Voice cloning, emotion-aware synthesis, 29+ languages
- **Deepgram SDK 3.0+** - STT with automatic language detection
  - Model: `nova-2`
  - Features: Real-time transcription, 30+ language support, automatic detection

### MCP (Model Context Protocol)
- **FastMCP 1.9.0+** - MCP server implementation
- **langchain-mcp-adapters 0.1.1+** - MCP tool integration
- **36 Custom MCP Tools**: Database operations, calendar management, team collaboration, external APIs

### Database
- **PostgreSQL 14+** - Primary database
- **psycopg2-binary 2.9.10+** - PostgreSQL adapter
- **Alembic 1.16.1** - Database migrations

### External APIs & Integrations
- **Google Calendar API v3** (google-api-python-client 2.181.0+)
- **Google OAuth 2.0** (google-auth 2.28.2, google-auth-oauthlib 1.2.2+)
- **Twilio Voice API 8.0+** - Telephony and voice calls
- **Composio Core 0.3.0+** - External tool integration (Slack, GitHub, Gmail, Jira, Notion)

### Authentication & Security
- **PyJWT 2.10.1** - JSON Web Tokens
- **bcrypt 4.0.1** - Password hashing
- **Flask-Login 0.6.3** - Session management

### Web Technologies
- **WebRTC** (aiortc 1.11.0) - Real-time browser communication
- **WebSocket** (websockets 15.0.1) - Real-time updates
- **Tailwind CSS** - Utility-first CSS framework
- **Vanilla JavaScript** - Frontend interactivity

### Deployment & Infrastructure
- **Render.com** - Cloud hosting platform
- **Gunicorn 21.2.0** - WSGI server
- **Docker 7.1.0** - Containerization support
- **GitHub** - Version control and CI/CD

### Additional Libraries
- **asyncio** - Asynchronous programming
- **nest-asyncio 1.6.0** - Nested event loop support
- **aiohttp 3.12.15** - Async HTTP client
- **httpx 0.28.1** - Modern HTTP client
- **requests 2.32.3** - HTTP library
- **pydantic 2.11.4+** - Data validation
- **pandas 2.2.3+** - Data manipulation
- **numpy 2.2.4** - Numerical computing
- **scipy 1.15.3+** - Scientific computing
- **tiktoken 0.9.0** - Token counting
- **python-dotenv 1.1.0+** - Environment management

**Total: 50+ Python packages, 36 MCP tools, 3 LLM providers, 2 voice services, 30+ languages supported**

---

## Demo URL
**https://www.convonetai.com/webrtc/voice-assistant**

## GitHub Repository
**https://github.com/hjleepapa/convonet-anthropic**

