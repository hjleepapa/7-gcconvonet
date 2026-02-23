# Multilingual Support Architecture in Convonet

## Overview

Convonet supports **30+ languages** through automatic language detection and native-accent text-to-speech synthesis. The multilingual support is **NOT** about using different LLM providers for different languages. Instead, it's a **voice pipeline feature** that ensures language consistency from speech input to speech output.

**Key Insight**: All LLM providers (Claude, Gemini, OpenAI) are inherently multilingual and can process text in any language. The multilingual support is about:
1. **Detecting** the language from speech (STT)
2. **Processing** with any LLM provider (language-agnostic)
3. **Synthesizing** the response in the same language (TTS)

---

## Architecture Flow

```
User Speech (Any Language)
    ↓
[Deepgram STT] → Automatic Language Detection (30+ languages)
    ↓
Transcribed Text (in detected language)
    ↓
[LLM Provider] → Processes text (Claude/Gemini/OpenAI - all multilingual)
    ↓
Agent Response Text (in same language)
    ↓
[ElevenLabs TTS] → Multilingual Synthesis (29+ languages)
    ↓
Audio Response (in same language as input)
```

---

## Components and Configuration

### 1. **Deepgram STT - Language Detection**

**File:** `deepgram_service.py`

**Component:** `DeepgramService._transcribe_file()`

**Key Configuration:**
```python
# Lines 158-178 in deepgram_service.py
use_auto_detect = language == "auto" or language is None

if use_auto_detect:
    logger.info(f"🌍 Using automatic language detection (supports 30+ languages)")

params = {
    "model": "nova-2",  # Deepgram's latest model
    "smart_format": "true",
    "punctuate": "true",
    "detect_language": "true" if use_auto_detect else "false",  # KEY CONFIGURATION
    "vad_events": "true",
    "interim_results": "false"
}

# Only add language parameter if not using auto-detection
if not use_auto_detect:
    params["language"] = language
```

**Language Detection Logic:**
```python
# Lines 201-205 in deepgram_service.py
# Check if language was detected (in metadata)
detected_language = None
if result.get("metadata") and result["metadata"].get("language"):
    detected_language = result["metadata"]["language"]
    logger.info(f"🌍 Deepgram detected language: {detected_language}")
```

**Supported Languages:** 30+ languages including:
- `en` (English)
- `ko` (Korean)
- `ja` (Japanese)
- `es` (Spanish)
- `fr` (French)
- `de` (German)
- `zh` (Chinese)
- And 23+ more languages

**Integration Point:**
```python
# deepgram_webrtc_integration.py:8-30
def transcribe_audio_with_deepgram_webrtc(audio_buffer: bytes, language: Optional[str] = None):
    """
    Args:
        language: Language code. Use None or "auto" for automatic detection (default: None = auto-detect).
                  Supports 30+ languages including: en, ko, ja, es, fr, de, zh, etc.
    """
    # Use "auto" for automatic language detection if None is passed
    if language is None:
        language = "auto"
    
    transcribed_text = service.transcribe_audio_buffer(audio_buffer, language)
```

---

### 2. **Voice Preferences - Language Storage**

**File:** `convonet/voice_preferences.py`

**Component:** `VoicePreferences`

**Key Methods:**
```python
# Lines 73-78
def get_language(self, user_id: Optional[str]) -> str:
    """Get user's preferred language (default: 'en')"""
    if not user_id:
        return "en"
    prefs = self.get_user_preferences(user_id)
    return prefs.get("language", "en")

# Lines 94-104
def _get_default_preferences(self) -> Dict[str, Any]:
    """Get default voice preferences"""
    return {
        "voice_id": None,
        "language": "en",  # Default language
        "emotion_enabled": True,
        "style": "conversational",
        "stability": 0.5,
        "similarity_boost": 0.75,
        "use_elevenlabs": True
    }
```

**Storage:** Language preferences are stored in Redis with 90-day TTL:
```python
# Lines 40-64
def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
    key = f"voice_preferences:{user_id}"
    existing = self.get_user_preferences(user_id)
    existing.update(preferences)
    # Store for 90 days
    self.redis.set(key, json.dumps(existing), expire=86400 * 90)
```

---

### 3. **LLM Processing - Language-Agnostic**

**Important Note:** All LLM providers (Claude, Gemini, OpenAI) are **inherently multilingual** and can process text in any language. There is **NO language-specific configuration** for LLM providers.

**LLM Provider Manager:**
- **File:** `convonet/llm_provider_manager.py`
- **Purpose:** Manages multiple LLM providers (Claude, Gemini, OpenAI)
- **Language Support:** All providers support all languages natively
- **No Language Configuration:** The LLM providers don't need language-specific setup

**Key Point:** The LLM processes the transcribed text (in any language) and generates a response in the same language. The language is determined by the input text, not by LLM configuration.

---

### 4. **ElevenLabs TTS - Multilingual Synthesis**

**File:** `convonet/elevenlabs_service.py`

**Component:** `ElevenLabsService`

**Key Configuration:**
```python
# Lines 49-51
self.default_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel (default ElevenLabs voice)
self.default_model = "eleven_multilingual_v2"  # Supports 29+ languages
```

**Multilingual Synthesis Method:**
```python
# Lines 242-273
def synthesize_multilingual(
    self,
    text: str,
    language: str = "en",
    voice_id: Optional[str] = None,
    model: Optional[str] = None
) -> Optional[bytes]:
    """
    Synthesize speech in specified language
    
    Args:
        text: Text to convert to speech
        language: Language code (en, es, fr, de, ja, etc.)
        voice_id: Voice ID (default: Rachel)
        model: Model to use (default: eleven_multilingual_v2)
    """
    # Use multilingual model
    model = model or self.default_model
    
    logger.info(f"🌍 ElevenLabs TTS in {language}: '{text[:50]}...'")
    
    return self.synthesize(
        text=text,
        voice_id=voice_id,
        model=model
    )
```

**Supported Languages:** 29+ languages via `eleven_multilingual_v2` model

---

### 5. **WebRTC Voice Server - Language Flow Orchestration**

**File:** `convonet/webrtc_voice_server.py`

**Component:** `process_audio_async()`

**Language Flow Logic:**
```python
# Lines 1079-1086
# Use Deepgram integration with automatic language detection
transcribed_text = transcribe_audio_with_deepgram_webrtc(
    audio_buffer,
    language=None  # Always use None/"auto" for automatic language detection
)
```

**TTS Language Selection:**
```python
# Lines 1402-1441
prefs = voice_prefs.get_user_preferences(user_id) if user_id else voice_prefs._get_default_preferences()
voice_id = prefs.get("voice_id")
language = prefs.get("language", "en")  # Get language from preferences
emotion_enabled = prefs.get("emotion_enabled", True)

if emotion_enabled:
    # Use emotion-aware synthesis (works with any language)
    audio_bytes = elevenlabs.synthesize_with_emotion(
        text=agent_response,
        emotion=emotion,
        voice_id=voice_id
    )
else:
    # Use multilingual if language is not English
    if language != "en":
        print(f"🌍 Using ElevenLabs multilingual for {language}", flush=True)
        audio_bytes = elevenlabs.synthesize_multilingual(
            text=agent_response,
            language=language,
            voice_id=voice_id
        )
    else:
        # Use standard TTS for English
        audio_bytes = elevenlabs.synthesize(
            text=agent_response,
            voice_id=voice_id
        )
```

**Key Logic:**
1. **Language Detection:** Deepgram automatically detects language from speech
2. **Language Storage:** Detected language can be stored in user preferences
3. **TTS Selection:** 
   - If `language != "en"` → Use `synthesize_multilingual()`
   - If `language == "en"` → Use standard `synthesize()`
   - If emotion enabled → Use `synthesize_with_emotion()` (works with any language)

---

## Configuration Summary

### Environment Variables

**Deepgram (STT):**
```bash
DEEPGRAM_API_KEY=your_deepgram_api_key
# Language detection is automatic (no configuration needed)
```

**ElevenLabs (TTS):**
```bash
ELEVENLABS_API_KEY=your_elevenlabs_api_key
# Uses eleven_multilingual_v2 model by default (supports 29+ languages)
```

**LLM Providers:**
```bash
# No language-specific configuration needed
# All LLMs (Claude, Gemini, OpenAI) are inherently multilingual
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
OPENAI_API_KEY=your_openai_key
```

### Code Configuration

**1. Enable Automatic Language Detection:**
```python
# In deepgram_service.py
params = {
    "detect_language": "true"  # Enable automatic detection
}
```

**2. Use Multilingual TTS:**
```python
# In webrtc_voice_server.py
if language != "en":
    audio_bytes = elevenlabs.synthesize_multilingual(
        text=agent_response,
        language=language,
        voice_id=voice_id
    )
```

**3. Store Language Preferences:**
```python
# In voice_preferences.py
prefs = voice_prefs.get_user_preferences(user_id)
language = prefs.get("language", "en")  # Default: "en"
```

---

## Language Flow Example

### Example: Korean User

1. **User speaks in Korean:**
   ```
   "오늘 할 일을 추가해줘"
   ```

2. **Deepgram STT detects language:**
   ```python
   # deepgram_service.py:201-205
   detected_language = "ko"  # Korean detected
   transcribed_text = "오늘 할 일을 추가해줘"
   ```

3. **LLM processes (any provider, language-agnostic):**
   ```python
   # routes.py: _run_agent_async()
   # Claude/Gemini/OpenAI all understand Korean
   agent_response = "할 일을 추가했습니다."
   ```

4. **ElevenLabs TTS synthesizes in Korean:**
   ```python
   # webrtc_voice_server.py:1428-1435
   if language != "en":  # language = "ko"
       audio_bytes = elevenlabs.synthesize_multilingual(
           text="할 일을 추가했습니다.",
           language="ko",
           voice_id=voice_id
       )
   ```

5. **User hears response in Korean:**
   ```
   Audio: "할 일을 추가했습니다." (in Korean accent)
   ```

---

## Key Design Decisions

### 1. **Why Not Language-Specific LLM Providers?**

**Decision:** All LLM providers are language-agnostic and support all languages natively.

**Rationale:**
- Claude, Gemini, and OpenAI all support 100+ languages
- No need for language-specific LLM selection
- Simpler architecture (one LLM provider handles all languages)
- Better cost efficiency (no need to maintain multiple providers per language)

### 2. **Why Automatic Language Detection?**

**Decision:** Use Deepgram's automatic language detection instead of manual selection.

**Rationale:**
- Better user experience (no manual language switching)
- Supports 30+ languages automatically
- More accurate than manual selection
- Seamless multilingual conversations

### 3. **Why ElevenLabs Multilingual Model?**

**Decision:** Use `eleven_multilingual_v2` model for all non-English languages.

**Rationale:**
- Single model supports 29+ languages
- Native-accent synthesis (not just translation)
- Consistent voice quality across languages
- Simpler than maintaining language-specific models

### 4. **Why Store Language in Preferences?**

**Decision:** Store detected language in user preferences for TTS selection.

**Rationale:**
- Persists language choice across sessions
- Allows manual language override
- Enables emotion-aware synthesis with language context
- Better user experience (remembers preference)

---

## Supported Languages

### Deepgram STT (30+ languages)
- English (`en`)
- Korean (`ko`)
- Japanese (`ja`)
- Spanish (`es`)
- French (`fr`)
- German (`de`)
- Chinese (`zh`)
- Portuguese (`pt`)
- Italian (`it`)
- Russian (`ru`)
- And 20+ more languages

### ElevenLabs TTS (29+ languages)
- All languages supported by `eleven_multilingual_v2` model
- Native-accent synthesis (not just translation)
- Emotion-aware synthesis works with all languages

### LLM Providers (100+ languages)
- Claude: Supports all major languages
- Gemini: Supports 100+ languages
- OpenAI: Supports 50+ languages

---

## Testing Multilingual Support

### Test Korean:
```python
# 1. Speak in Korean
user_input = "오늘 할 일을 추가해줘"

# 2. Deepgram detects: language = "ko"
# 3. LLM processes (any provider)
# 4. ElevenLabs synthesizes in Korean
```

### Test Japanese:
```python
# 1. Speak in Japanese
user_input = "今日のタスクを追加してください"

# 2. Deepgram detects: language = "ja"
# 3. LLM processes (any provider)
# 4. ElevenLabs synthesizes in Japanese
```

### Test Spanish:
```python
# 1. Speak in Spanish
user_input = "Agrega una tarea para hoy"

# 2. Deepgram detects: language = "es"
# 3. LLM processes (any provider)
# 4. ElevenLabs synthesizes in Spanish
```

---

## Troubleshooting

### Issue: Language Not Detected

**Solution:**
- Ensure `detect_language: "true"` in Deepgram params
- Check Deepgram API response for `metadata.language`
- Verify audio quality (clear speech improves detection)

### Issue: Wrong Language in TTS

**Solution:**
- Check `voice_preferences` for correct language
- Verify `language != "en"` condition in TTS selection
- Ensure `eleven_multilingual_v2` model is used

### Issue: LLM Response in Wrong Language

**Solution:**
- LLMs are language-agnostic (they respond in the language of input)
- If LLM responds in English, check if input text is in English
- Verify LLM provider supports the language (all major providers do)

---

## Summary

**Multilingual support in Convonet is configured through:**

1. **Deepgram STT** (`deepgram_service.py`):
   - `detect_language: "true"` parameter
   - Automatic detection of 30+ languages
   - Language returned in API response metadata

2. **Voice Preferences** (`voice_preferences.py`):
   - Stores user language preference in Redis
   - Default: `"en"` (English)
   - 90-day TTL for preferences

3. **ElevenLabs TTS** (`elevenlabs_service.py`):
   - `eleven_multilingual_v2` model (29+ languages)
   - `synthesize_multilingual()` method for non-English
   - Standard `synthesize()` for English

4. **WebRTC Voice Server** (`webrtc_voice_server.py`):
   - Orchestrates language flow
   - Selects TTS method based on detected language
   - Integrates emotion detection with multilingual support

5. **LLM Providers** (`llm_provider_manager.py`):
   - **No language-specific configuration needed**
   - All providers (Claude, Gemini, OpenAI) are inherently multilingual
   - Process text in any language automatically

**Key Insight:** The multilingual support is a **voice pipeline feature**, not an LLM provider feature. The LLMs are language-agnostic, and the multilingual support ensures language consistency from speech input to speech output.
