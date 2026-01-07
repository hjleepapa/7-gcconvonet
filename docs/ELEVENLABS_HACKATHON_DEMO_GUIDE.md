# ElevenLabs Hackathon Demo Guide

## 🌐 Demo URLs

### Main Voice Assistant (Primary Demo)
**URL**: `https://www.convonetai.com/webrtc/voice-assistant`

This is the main interface for testing all ElevenLabs features:
- Real-time voice interaction
- Emotional voice responses
- Multi-language support
- Voice preferences

### API Endpoints (For Testing/Integration)

1. **Voice Cloning**
   - **POST** `https://www.convonetai.com/api/voice/clone`
   - Upload audio samples to clone a voice

2. **Voice Preferences**
   - **GET** `https://www.convonetai.com/api/voice/preferences`
   - **POST** `https://www.convonetai.com/api/voice/preferences`
   - Get/update user voice preferences

3. **List Available Voices**
   - **GET** `https://www.convonetai.com/api/voice/list`
   - Get list of available ElevenLabs voices

---

## 🎬 Demo Scenarios

### Scenario 1: Emotional Voice Response Demo ⭐⭐⭐
**Goal**: Show how the assistant adapts its voice tone based on user emotion

**Step-by-Step**:
1. Navigate to: `https://www.convonetai.com/webrtc/voice-assistant`
2. Click "Allow" microphone access
3. Enter PIN: `1237` (for admin user)
4. Wait for welcome greeting (uses ElevenLabs with neutral emotion)
5. **Test Happy Emotion**:
   - Say: *"I'm so excited! Schedule a team meeting for tomorrow at 3 PM!"*
   - **Expected**: Assistant responds with happy, excited voice tone
   - **Look for**: Status message "Generating speech with ElevenLabs..."
   - **Listen for**: More energetic, upbeat voice quality
6. **Test Stressed Emotion**:
   - Say: *"I'm really stressed and overwhelmed with all these meetings!"*
   - **Expected**: Assistant responds with calm, reassuring voice tone
   - **Listen for**: Softer, more empathetic voice quality
7. **Test Neutral/Professional**:
   - Say: *"Create a calendar event for the quarterly review on December 30th."*
   - **Expected**: Assistant responds with professional, neutral voice tone

**What to Highlight**:
- ✅ Voice tone adapts to user's emotional state
- ✅ Emotion detection from both user input and context
- ✅ Natural, human-like voice responses

---

### Scenario 2: Multi-Language Support Demo ⭐⭐⭐
**Goal**: Show how the assistant responds in the user's language

**Step-by-Step**:
1. Navigate to: `https://www.convonetai.com/webrtc/voice-assistant`
2. Click "Allow" microphone access
3. Enter PIN: `1237`
4. **Test Korean Language**:
   - Say (in Korean): *"캘린더 이벤트를 만들어주세요. 한국 팀 미팅, 12/24/2025, 7PM to 9PM"*
   - **Expected**: 
     - System detects Korean language
     - Assistant responds in Korean with native accent
     - Status shows "Generating speech with ElevenLabs..."
   - **Listen for**: Natural Korean pronunciation and accent
5. **Test Japanese Language** (if supported):
   - Say (in Japanese): *"カレンダーイベントを作成してください"*
   - **Expected**: Assistant responds in Japanese
6. **Test English**:
   - Say: *"Schedule a meeting for tomorrow at 2 PM"*
   - **Expected**: Assistant responds in English

**What to Highlight**:
- ✅ Automatic language detection
- ✅ Native accent and pronunciation
- ✅ Seamless language switching
- ✅ Supports 29+ languages via ElevenLabs multilingual model

---

### Scenario 3: Voice Cloning Demo ⭐⭐⭐
**Goal**: Show how users can clone their voice for personalized responses

**Step-by-Step**:
1. **Clone Voice** (via API or UI):
   - **Option A - API**:
     ```bash
     curl -X POST https://www.convonetai.com/api/voice/clone \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer YOUR_TOKEN" \
       -d '{
         "voice_name": "My Voice",
         "audio_samples": [base64_encoded_audio1, base64_encoded_audio2]
       }'
     ```
   - **Option B - UI** (if implemented):
     - Go to Voice Settings page
     - Upload 1-minute audio sample
     - Click "Clone Voice"
2. **Use Cloned Voice**:
   - Navigate to: `https://www.convonetai.com/webrtc/voice-assistant`
   - Enter PIN: `1237`
   - Say: *"Create a todo for team standup"*
   - **Expected**: Assistant responds in your cloned voice
   - **Listen for**: Your own voice speaking the response

**What to Highlight**:
- ✅ Personal voice cloning in < 1 minute
- ✅ Responses in user's own voice
- ✅ Team-specific voice avatars
- ✅ Brand voice for organizations

---

### Scenario 4: Voice Preferences Demo ⭐⭐
**Goal**: Show how users can customize voice settings

**Step-by-Step**:
1. **Get Current Preferences**:
   ```bash
   curl -X GET https://www.convonetai.com/api/voice/preferences \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```
   - **Expected Response**:
     ```json
     {
       "use_elevenlabs": true,
       "voice_id": "21m00Tcm4TlvDq8ikWAM",
       "language": "en",
       "emotion_enabled": true,
       "style": "conversational"
     }
     ```
2. **Update Preferences**:
   ```bash
   curl -X POST https://www.convonetai.com/api/voice/preferences \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "voice_id": "pNInz6obpgDQGcFmaJgB",
       "language": "ko",
       "emotion_enabled": true,
       "style": "professional"
     }'
     ```
3. **Test Updated Preferences**:
   - Navigate to: `https://www.convonetai.com/webrtc/voice-assistant`
   - Enter PIN: `1237`
   - Say: *"What's on my calendar today?"*
   - **Expected**: Uses new voice settings (Korean, professional style)

**What to Highlight**:
- ✅ Per-user voice customization
- ✅ Persistent preferences across sessions
- ✅ Team-level voice settings
- ✅ Easy API for integration

---

### Scenario 5: Complete Workflow Demo ⭐⭐⭐
**Goal**: Show end-to-end workflow with all features

**Step-by-Step**:
1. Navigate to: `https://www.convonetai.com/webrtc/voice-assistant`
2. Click "Allow" microphone access
3. Enter PIN: `1237`
4. **Multi-language Calendar Creation**:
   - Say (in Korean): *"한국 팀 미팅을 12/24/2025, 7PM to 9PM에 일정을 잡아주세요"*
   - **Expected**:
     - ✅ Language detected: Korean
     - ✅ Assistant responds in Korean
     - ✅ Calendar event created
     - ✅ Emotional tone matches context (professional/helpful)
5. **Emotional Response**:
   - Say: *"I'm so happy! The project is going great!"*
   - **Expected**:
     - ✅ Emotion detected: Happy
     - ✅ Assistant responds with happy, excited voice
6. **Professional Task**:
   - Say: *"Create a todo for the quarterly review presentation"*
   - **Expected**:
     - ✅ Neutral/professional voice tone
     - ✅ Task created successfully

**What to Highlight**:
- ✅ Seamless integration of all features
- ✅ Context-aware voice adaptation
- ✅ Natural conversation flow
- ✅ Multi-language support in real-time

---

## 🎯 Quick Demo Checklist

### Before Demo:
- [ ] Test microphone access
- [ ] Verify PIN authentication works
- [ ] Check ElevenLabs API key is configured
- [ ] Test at least one scenario end-to-end
- [ ] Prepare backup (Deepgram fallback works)

### During Demo:
- [ ] Show status messages ("Generating speech with ElevenLabs...")
- [ ] Demonstrate emotion detection (happy, stressed, neutral)
- [ ] Show multi-language support (Korean, Japanese, English)
- [ ] Highlight voice quality difference vs Deepgram
- [ ] Show real-time response (low latency)

### Key Talking Points:
1. **Emotion Detection**: "The assistant adapts its voice tone based on your emotional state"
2. **Multi-Language**: "Supports 29+ languages with native accents"
3. **Voice Cloning**: "Clone your voice in under 1 minute"
4. **Real-Time**: "Low latency, natural conversation flow"
5. **Fallback**: "Robust fallback to Deepgram if ElevenLabs unavailable"

---

## 🔍 Testing & Verification

### Check ElevenLabs is Working:
1. Look for status message: `"Generating speech with ElevenLabs..."`
2. Check logs for: `"✅ ElevenLabs TTS successful: X bytes"`
3. Listen for: Higher quality, more natural voice
4. Verify emotion: `"🎭 Using ElevenLabs with emotion: happy"`

### Check Fallback (if ElevenLabs fails):
1. Look for status message: `"Generating speech with Deepgram..."`
2. Check logs for: `"⚠️ ElevenLabs TTS failed, falling back to Deepgram"`
3. System should still work (graceful degradation)

### Debug Commands:
```bash
# Check if ElevenLabs is available
curl https://www.convonetai.com/api/voice/list

# Check user preferences
curl -X GET https://www.convonetai.com/api/voice/preferences \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 Success Metrics to Show

1. **Voice Quality**: Compare ElevenLabs vs Deepgram side-by-side
2. **Emotion Accuracy**: Show emotion detection working correctly
3. **Language Support**: Demonstrate multiple languages
4. **Latency**: Show real-time response (no noticeable delay)
5. **Reliability**: Show fallback mechanism works

---

## 🎥 Demo Script (2-minute pitch)

**Opening** (30 seconds):
- "Convonet now uses ElevenLabs for natural, emotional voice responses"
- "The assistant adapts its voice tone based on your emotional state"
- "Supports 29+ languages with native accents"

**Live Demo** (60 seconds):
1. Show happy emotion detection (20s)
2. Show Korean language support (20s)
3. Show voice quality difference (20s)

**Closing** (30 seconds):
- "Voice cloning available for personalization"
- "Robust fallback ensures reliability"
- "All features work in real-time"

---

## 🚨 Troubleshooting

### If ElevenLabs not working:
1. Check `ELEVENLABS_API_KEY` environment variable
2. Check logs for: `"⚠️ ElevenLabs SDK not available"`
3. Verify `elevenlabs>=1.0.0` in requirements.txt
4. System will automatically fallback to Deepgram

### If voice cloning fails:
1. Ensure audio samples are at least 1 minute total
2. Check audio format (MP3, WAV supported)
3. Verify API key has cloning permissions

### If emotion not detected:
1. Check emotion detection is enabled in preferences
2. Try more explicit emotional language
3. Check logs for: `"🎭 Detected emotion: X"`

---

## 📝 Notes

- **Default Voice**: Rachel (21m00Tcm4TlvDq8ikWAM)
- **Default Model**: eleven_multilingual_v2
- **Supported Languages**: 29+ languages via multilingual model
- **Emotion Types**: happy, sad, excited, calm, empathetic, professional, casual, neutral
- **Fallback**: Deepgram TTS if ElevenLabs unavailable

---

## 🏆 Hackathon Presentation Tips

1. **Start with emotion demo** - Most impressive, quick to show
2. **Show multi-language** - Highlights global appeal
3. **Mention voice cloning** - Unique feature, high WOW factor
4. **Emphasize real-time** - Low latency, natural conversation
5. **Show fallback** - Demonstrates reliability and production-ready

**Key Differentiators**:
- ✅ Emotion-aware voice responses
- ✅ Multi-language with native accents
- ✅ Voice cloning for personalization
- ✅ Real-time, low-latency
- ✅ Robust fallback mechanism

