# LLM Provider Selection Guide

## 🎯 Overview

Convonet now supports multiple LLM providers! You can easily switch between **Claude (Anthropic)**, **Gemini (Google)**, and **OpenAI** through a simple UI interface.

---

## 🚀 Quick Start

### 1. Access the Provider Selector

Navigate to the homepage and you'll see the **"🤖 Select LLM Provider"** section with buttons for each available provider.

### 2. Select Your Provider

Click on your preferred provider:
- **🤖 Claude (Anthropic)** - Default, recommended for best tool calling
- **✨ Gemini (Google)** - Google's advanced AI model
- **🚀 OpenAI** - GPT-4 and other OpenAI models

### 3. Your Selection is Saved

Your preference is automatically saved and will be used for all future conversations.

---

## 🔧 Configuration

### Environment Variables

To enable each provider, set the corresponding API key:

#### Claude (Anthropic)
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-sonnet-4-20250514  # Optional, defaults to latest
```

#### Gemini (Google)
```bash
GOOGLE_API_KEY=your-google-api-key
GOOGLE_MODEL=gemini-3-pro-preview  # Optional, defaults to gemini-3-pro-preview
```

**Available Gemini Models** (as of Nov 2025, per [official documentation](https://ai.google.dev/gemini-api/docs/models)):

**Most Powerful:**
- `gemini-3-pro-preview` - Latest and most powerful model (Nov 2025), best for multimodal understanding and agentic tasks
- `gemini-3-pro-image-preview` - Image generation and understanding

**Best Price-Performance:**
- `gemini-2.5-flash` - Best price-performance, well-rounded capabilities (June 2025)
- `gemini-2.5-flash-preview-09-2025` - Preview version

**Fast & Efficient:**
- `gemini-2.0-flash` - Fast and efficient (Feb 2025)
- `gemini-2.0-flash-lite` - Cost-efficient option, 1M token context window

**Specialized:**
- `gemini-2.0-flash-live-001` - Live API with audio generation (deprecated Dec 2025)

See [Gemini API Models Documentation](https://ai.google.dev/gemini-api/docs/models) for complete list and capabilities.

#### OpenAI
```bash
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-4o  # Optional, defaults to gpt-4o
```

### Provider Availability

The UI automatically shows which providers are available based on configured API keys:
- ✅ **Available** - API key is configured, ready to use
- ⚠️ **Not Available** - API key not configured (button disabled)

---

## 📡 API Endpoints

### Get Available Providers
```
GET /anthropic/convonet_todo/api/llm-providers
```

**Response:**
```json
{
  "success": true,
  "providers": [
    {
      "id": "claude",
      "name": "Claude (Anthropic)",
      "available": true
    },
    {
      "id": "gemini",
      "name": "Gemini (Google)",
      "available": false
    },
    {
      "id": "openai",
      "name": "OpenAI",
      "available": true
    }
  ]
}
```

### Get User's Current Provider
```
GET /anthropic/convonet_todo/api/llm-provider?user_id=user-123
```

**Response:**
```json
{
  "success": true,
  "provider": "claude",
  "available": true
}
```

### Set User's Provider
```
POST /anthropic/convonet_todo/api/llm-provider
Content-Type: application/json

{
  "user_id": "user-123",
  "provider": "gemini"
}
```

**Response:**
```json
{
  "success": true,
  "provider": "gemini",
  "message": "LLM provider set to gemini"
}
```

---

## 💾 Storage

Provider preferences are stored in **Redis** with the key format:
```
user:{user_id}:llm_provider
```

- **Expiration**: 30 days
- **Scope**: Per-user (each user can have their own preference)
- **Fallback**: If no preference is set, defaults to Claude

---

## 🔄 How It Works

1. **User Selection**: User selects a provider via the UI
2. **Redis Storage**: Preference is saved to Redis with user ID
3. **Agent Initialization**: When a user makes a request, the system:
   - Checks Redis for user's provider preference
   - Falls back to environment variable `LLM_PROVIDER` if no preference
   - Defaults to Claude if nothing is set
4. **Graph Caching**: Agent graph is cached per provider/model combination
   - Cache is cleared when provider changes
   - Ensures correct LLM is used for each user

---

## 🎨 UI Features

### Provider Selector Component

Located on the homepage, the selector shows:
- **Provider buttons** with icons and names
- **Active indicator** (checkmark) for current selection
- **Availability status** (available/not available)
- **Status message** showing current provider

### Visual Indicators

- **Active Provider**: Ring highlight and checkmark
- **Available**: Full color button, clickable
- **Not Available**: Grayed out, disabled, shows "(Not Available)"

---

## 🔍 Technical Details

### Provider Manager

The `LLMProviderManager` class (`convonet/llm_provider_manager.py`) handles:
- Provider initialization and validation
- API key checking
- LLM instance creation
- Fallback logic

### TodoAgent Integration

The `TodoAgent` class now accepts a `provider` parameter:
```python
agent = TodoAgent(
    tools=tools,
    provider="gemini",  # or "claude", "openai"
    model="gemini-1.5-pro"  # Optional, provider-specific
)
```

### Routes Integration

The `_get_agent_graph()` function in `routes.py`:
- Accepts `provider` and `user_id` parameters
- Retrieves user preference from Redis
- Caches graphs per provider/model combination
- Clears cache when provider changes

---

## 🛠️ Troubleshooting

### Provider Not Available

**Issue**: Provider button shows "Not Available"

**Solution**: 
1. Check that the corresponding API key is set in environment variables
2. Verify the API key is valid
3. Restart the application after setting environment variables

### Provider Selection Not Working

**Issue**: Selection doesn't persist or doesn't take effect

**Solution**:
1. Check Redis connection
2. Verify user_id is being passed correctly
3. Check browser console for JavaScript errors
4. Ensure API endpoint is accessible

### Cache Not Clearing

**Issue**: Old provider still being used after switching

**Solution**:
- The cache should automatically clear when provider changes
- If not, restart the application
- Check logs for cache clearing messages

---

## 📝 Example Usage

### Python Code
```python
from convonet.llm_provider_manager import get_llm_provider_manager

# Get provider manager
manager = get_llm_provider_manager()

# Check available providers
providers = manager.get_available_providers()
print(providers)

# Create LLM instance
llm = manager.create_llm(
    provider="gemini",
    model="gemini-1.5-pro",
    temperature=0.0,
    tools=my_tools
)
```

### JavaScript/UI
```javascript
// Select provider
await fetch('/anthropic/convonet_todo/api/llm-provider', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        user_id: 'user-123',
        provider: 'gemini'
    })
});
```

---

## 🎯 Best Practices

1. **Default Provider**: Always configure at least one provider (Claude recommended)
2. **User Preferences**: Store per-user preferences for multi-tenant scenarios
3. **Cache Management**: Let the system handle cache clearing automatically
4. **Error Handling**: The system automatically falls back to available providers
5. **Testing**: Test each provider before deploying to production

---

## 🔐 Security Notes

- API keys are stored in environment variables, never in code
- User preferences are stored in Redis (secure, temporary storage)
- Provider selection is per-user, isolated by user_id
- No API keys are exposed in API responses or UI

---

**Now you can easily switch between LLM providers! 🎉**

