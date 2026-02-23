# Convonet Team Collaboration System - Technology Stack

## 📋 Complete Technology Inventory

---

## 🐍 Programming Languages

### **Primary:**
- **Python 3.12** - Backend, AI agent, MCP servers, migrations
- **JavaScript (ES6+)** - Frontend interactivity, AJAX, JWT handling
- **HTML5** - Web structure and templates
- **CSS3** - Styling (with Tailwind utility classes)
- **SQL** - Database queries and migrations
- **Bash** - Deployment scripts (`build.sh`)

---

## 🎨 Frontend Technologies

### **Frameworks & Libraries:**
- **Vanilla JavaScript** - No framework dependency, lightweight
- **Tailwind CSS** - Utility-first CSS framework for styling
- **Fetch API** - Async HTTP requests
- **LocalStorage API** - JWT token persistence

### **UI Components:**
- Custom modals (Login, Register, Add Member, Create Team, Create Todo)
- Dynamic team selection dropdowns
- Real-time form validation
- Responsive design (mobile-friendly)

---

## 🔧 Backend Frameworks & Libraries

### **Core Framework:**
- **Flask 3.0+** - Python web framework
  - `Flask-CORS` - Cross-origin resource sharing
  - `Flask` blueprints for modular routing
  - Template rendering with Jinja2

### **AI & Agent:**
- **LangGraph** - AI agent state management and workflow orchestration
- **LangChain** - LLM framework and utilities
  - `langchain-anthropic` - Anthropic Claude integration
  - `langchain-mcp-adapters` - MCP tool integration
- **Anthropic Claude API** - Claude 3.5 Sonnet for natural language understanding

### **MCP (Model Context Protocol):**
- **FastMCP** - MCP server implementation
- **MCP Client** - Tool orchestration
- **MultiServerMCPClient** - Multiple MCP server management
- Custom stdio transport for JSONRPC communication

### **Database ORM:**
- **SQLAlchemy 2.0+** - Python SQL toolkit and ORM
  - Declarative base models
  - Relationship mapping
  - Query builder
  - Migration support

### **Authentication & Security:**
- **bcrypt** - Password hashing (Blowfish cipher)
- **PyJWT** - JSON Web Token encoding/decoding
- **Python secrets** - Cryptographically strong random tokens

### **API Integrations:**
- **google-api-python-client** - Google APIs client library
- **google-auth** - Google authentication
- **google-auth-oauthlib** - OAuth 2.0 flow
- **google-auth-httplib2** - HTTP transport for Google APIs
- **twilio** - Twilio Voice API SDK

### **Data & Utilities:**
- **pandas** - Data manipulation (for query results)
- **python-dotenv** - Environment variable management
- **pydantic** - Data validation and settings
- **asyncio** - Asynchronous programming

---

## 🗄️ Database

### **Primary Database:**
- **PostgreSQL 14+** - Production relational database
  - UUID primary keys with `gen_random_uuid()`
  - JSONB columns for flexible data
  - Full-text search capabilities
  - Transaction support
  - Connection pooling

### **Database Clients:**
- **psycopg2** - PostgreSQL adapter for Python
- **SQLAlchemy** - ORM layer on top of psycopg2

### **Schema:**
- 7 tables with relationships
- Foreign keys with cascading deletes
- Indexes on frequently queried columns
- Unique constraints for data integrity

---

## ☁️ Cloud Services & Hosting

### **Hosting Platform:**
- **Render.com** - Cloud application platform
  - Web service hosting
  - Automatic deployments from GitHub
  - Environment variable management
  - Build hooks and scripts
  - Persistent disk storage
  - Free PostgreSQL database (shared)

### **Domain & SSL:**
- **hjlees.com** - Custom domain
- **Let's Encrypt SSL** - HTTPS encryption (auto-managed by Render)

### **Version Control:**
- **GitHub** - Source code repository
  - Automatic deployments on push to main
  - Protected branches
  - Push protection for secrets

---

## 📞 Communication APIs

### **Voice & Telephony:**
- **Twilio Voice API** - Phone call infrastructure
  - Programmable Voice
  - TwiML (Twilio Markup Language)
  - Speech recognition (Gather with `input="speech"`)
  - DTMF (keypad) input
  - Call recording
  - Webhooks for call events
  - Real-time call control

### **Voice Features:**
- **Amazon Polly** - Text-to-speech (via Twilio)
  - Voice: Polly.Amy (British English female)
- **Google Speech Recognition** - Speech-to-text (via Twilio)

---

## 📅 Calendar & Productivity APIs

### **Google Calendar API v3:**
- **OAuth 2.0** - User authentication
- **Service Accounts** - Backend automation
- **Calendar Events API**
  - Create, read, update, delete events
  - Recurring events
  - Reminders and notifications
- **Calendar List API** - Access multiple calendars

### **Google Cloud Platform:**
- **Google Cloud Console** - API management
- **OAuth 2.0 Credentials** - Client ID/Secret
- **Service Account Keys** - JSON credentials

---

## 🤖 AI & Machine Learning

### **Language Models:**
- **Anthropic Claude 3.5 Sonnet**
  - Temperature: 0.7 (balanced creativity/determinism)
  - Max tokens: Context-aware
  - Streaming responses
  - Function calling / Tool use

### **AI Frameworks:**
- **LangGraph**
  - State management (AgentState)
  - Conditional edges
  - Tool nodes
  - Conversation memory
  - Workflow orchestration

### **Natural Language Processing:**
- **Anthropic Claude Embeddings** - (Future: semantic search)
- **Token management** - Cost optimization
- **Prompt engineering** - System prompts with guidelines

---

## 🔐 Authentication Technologies

### **Web Authentication:**
- **JWT (JSON Web Tokens)**
  - HS256 algorithm
  - 24-hour expiry
  - Bearer token in Authorization header
  - LocalStorage persistence

### **Voice Authentication:**
- **PIN-based authentication**
  - 4-6 digit PINs
  - Speech-to-digit conversion
  - DTMF (keypad) support
  - Secure storage (varchar unique column)

### **API Authentication:**
- **OAuth 2.0** - Google Calendar
  - Authorization Code flow
  - Refresh tokens
  - Access token management
- **API Keys** - Anthropic Claude, Deepgram, Twilio
- **Service Accounts** - Google Cloud

---

## 🛠️ Development Tools

### **Code Quality:**
- **Python type hints** - Static type checking
- **Pydantic models** - Runtime validation
- **SQLAlchemy validators** - Data integrity
- **Try-except blocks** - Error handling

### **Debugging:**
- **Python logging module** - Structured logging
- **print() statements** - (Removed from MCP servers)
- **Render.com logs** - Cloud log aggregation
- **Twilio logs** - Call debugging

### **Testing:**
- **Manual testing** - Voice call testing
- **Database testing** - `test_database()` MCP tool
- **Integration testing** - `test_google_calendar()`, `test_connection()`
- **Authentication testing** - `check_admin_user.py`

---

## 📦 Package Management

### **Python:**
- **pip** - Package installer
- **requirements.txt** - Dependency specification
- **venv** - Virtual environment

### **Key Dependencies (requirements.txt):**
```
flask==3.0.0
flask-cors==4.0.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dotenv==1.0.0
twilio==8.10.0
google-api-python-client==2.108.0
google-auth==2.25.2
google-auth-oauthlib==1.1.0
anthropic==0.34.0
langchain==0.1.0
langchain-anthropic==0.1.0
langgraph==0.0.20
langchain-mcp-adapters==0.1.0
fastmcp==0.1.0
bcrypt==4.0.1
pyjwt==2.8.0
pandas==2.1.4
pydantic==2.5.3
```

---

## 🏗️ Architecture Patterns

### **Design Patterns:**
- **MVC (Model-View-Controller)** - Flask structure
- **Repository Pattern** - Database access layer
- **Factory Pattern** - Agent initialization
- **Singleton Pattern** - Database engine
- **Strategy Pattern** - Authentication methods
- **Observer Pattern** - Webhook callbacks

### **Architectural Styles:**
- **REST API** - HTTP endpoints
- **Webhook Architecture** - Twilio callbacks
- **Event-Driven** - LangGraph state transitions
- **Microservices-inspired** - MCP servers as services

---

## 📊 Data Formats

### **Serialization:**
- **JSON** - API requests/responses
- **JSONRPC 2.0** - MCP protocol
- **XML (TwiML)** - Twilio responses
- **Base64** - Credential encoding
- **Pickle** - OAuth token serialization

### **Date/Time:**
- **ISO 8601** - Datetime format
- **UTC timezone** - All timestamps
- **Python datetime** - Date handling

---

## 🔄 DevOps & Deployment

### **CI/CD:**
- **GitHub** - Version control
- **Render.com** - Automatic deployments
- **build.sh** - Build script
- **deploy_setup.py** - Deployment automation

### **Environment Management:**
- **.env files** - Local development
- **Render.com Environment Variables** - Production secrets
- **mcp_config.json** - MCP server configuration

### **Database Migrations:**
- **Custom migration scripts** - Python-based
- **deploy_setup.py** - Auto-run on deployment
- **SQLAlchemy DDL** - Schema changes

### **Monitoring:**
- **Render.com Logs** - Application logs
- **Twilio Console** - Call logs and debugging
- **Google Cloud Console** - API usage and quotas
- **PostgreSQL logs** - Database queries

---

## 🌐 Protocols & Standards

### **Network Protocols:**
- **HTTP/HTTPS** - Web communication
- **WebSocket** - (Future: real-time updates)
- **TLS 1.3** - Encryption
- **JSONRPC 2.0** - MCP communication

### **API Standards:**
- **REST** - API design
- **OpenAPI** - (Future: API documentation)
- **OAuth 2.0** - Authorization framework
- **JWT (RFC 7519)** - Token standard

### **Telephony Standards:**
- **SIP** - Session Initiation Protocol (Twilio backend)
- **RTP** - Real-time Transport Protocol (audio)
- **DTMF (RFC 4733)** - Keypad tones

---

## 🔧 Specialized Libraries

### **Google APIs:**
- `googleapiclient.discovery.build()` - API client factory
- `google.oauth2.service_account` - Service account auth
- `google.oauth2.credentials` - OAuth credentials
- `google.auth.transport.requests` - Token refresh

### **Twilio:**
- `twilio.rest.Client` - Twilio API client
- `twilio.twiml.voice_response.VoiceResponse` - TwiML generation
- `twilio.twiml.voice_response.Gather` - Speech/DTMF collection

### **LangChain:**
- `langchain_anthropic.ChatAnthropic` - LLM wrapper
- `langchain_core.messages` - Message types
- `langchain_core.tools` - Tool definitions
- `langgraph.graph` - State graph builder

---

## 📱 Future Technologies (Roadmap)

### **Planned Integrations:**
- **Redis** - Caching and session storage
- **Celery** - Background task queue
- **WebSocket** - Real-time updates
- **Docker** - Containerization
- **Kubernetes** - Orchestration
- **React/Vue.js** - Modern frontend framework
- **React Native** - Mobile app
- **Elasticsearch** - Full-text search
- **Prometheus + Grafana** - Monitoring
- **Sentry** - Error tracking
- **Stripe** - Payment processing
- **SendGrid** - Email notifications
- **Slack API** - Team chat integration
- **Microsoft Teams API** - Enterprise chat
- **Jira API** - Project management
- **GitHub API** - Code repository integration

---

## 🏆 Technology Highlights

### **Why This Stack?**

✅ **Python Ecosystem** - Rich AI/ML libraries, mature frameworks  
✅ **PostgreSQL** - ACID compliance, complex queries, scalability  
✅ **LangGraph** - Stateful AI agents, complex workflows  
✅ **Twilio** - Reliable telephony, global reach  
✅ **Render.com** - Easy deployment, automatic SSL, database included  
✅ **Anthropic Claude** - State-of-the-art language understanding  
✅ **Flask** - Lightweight, flexible, Pythonic  
✅ **SQLAlchemy** - Database abstraction, easy migrations  
✅ **JWT** - Stateless authentication, mobile-friendly  
✅ **Google Calendar** - Universal calendar integration  

---

## 📊 Technology Stats

- **Languages**: 6 (Python, JavaScript, HTML, CSS, SQL, Bash)
- **Major Frameworks**: 5 (Flask, LangGraph, LangChain, SQLAlchemy, Tailwind)
- **Cloud Services**: 4 (Render.com, Twilio, Google Cloud, GitHub)
- **Databases**: 1 (PostgreSQL)
- **APIs**: 3 major (Twilio, Google Calendar, Anthropic Claude)
- **Authentication Methods**: 3 (JWT, PIN, OAuth2)
- **MCP Tools**: 35+
- **Python Packages**: 20+
- **Total Lines of Code**: ~5,000+

---

## 🎯 Technology Decisions

### **Key Choices:**

1. **Python over Node.js**: Better AI/ML ecosystem, type hints, sync/async flexibility
2. **PostgreSQL over MongoDB**: ACID transactions, complex relationships, mature
3. **Flask over Django**: Lightweight, flexible, no ORM lock-in
4. **LangGraph over Raw Claude**: State management, tool orchestration, workflow control
5. **Render.com over AWS**: Simpler deployment, free tier, automatic SSL
6. **JWT over Sessions**: Stateless, mobile-friendly, scalable
7. **MCP over Direct Tool Calls**: Standardized protocol, reusable tools, modularity
8. **Twilio over Vonage**: Better documentation, more reliable, richer features
9. **OAuth2 over Service Accounts**: User calendar access, better UX
10. **Vanilla JS over React**: Simpler, faster load, no build step needed

---

## 🚀 Deployment Stack

```
Local Development:
├── Python 3.12 (venv)
├── PostgreSQL (local or cloud)
├── .env file (secrets)
└── Flask development server

Production (Render.com):
├── Ubuntu Linux
├── Python 3.12 (managed)
├── PostgreSQL (managed)
├── Gunicorn (WSGI server)
├── Nginx (reverse proxy, SSL)
├── Environment variables (secrets)
└── Automatic deployments (GitHub)
```

---

**Built with modern, scalable, production-ready technologies** 🚀

*Last Updated: October 2025*

