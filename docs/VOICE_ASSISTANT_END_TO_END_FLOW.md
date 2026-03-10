# Voice Assistant: End-to-End Data Flow and Protocols

This doc explains how data moves from the user’s browser to the LLM and back, and why you see **WebRTC**, **WSS**, and **HTTP** in the same system.

---

## 1. What You Use: One WebRTC/Voice-Assistant UI

- You open **one voice-assistant UI** in the browser (e.g. Convonet Todo or LiveKit-based page).
- You make **one “call”**: the browser captures your microphone and plays back the assistant’s voice.
- Under the hood, that single “call” uses **several connections** with **different protocols**, each for a different job. They are **complementary**, not alternatives.

---

## 2. The Three Kinds of Connections (and Why They Differ)

| Role | Protocol | Typical URL shape | Who uses it | Why this protocol? |
|------|----------|-------------------|-------------|---------------------|
| **Media (voice/video)** | **WebRTC** (over UDP or, in browser, often **WSS** for data channel / relay) | `wss://` for signaling; actual media is RTP/DTLS | Browser ↔ LiveKit (or SFU) | Low-latency, bidirectional **streaming**; not request/response. |
| **Signaling / control** | **WSS** (WebSocket Secure) | `wss://your-app/socket.io` or LiveKit’s signaling | Browser ↔ your app or LiveKit | Real-time **control**: join room, mute, hang up, app events (e.g. transfer). |
| **REST / one-off calls** | **HTTP/HTTPS** | `https://your-app/...` | Browser ↔ app; **app ↔ external APIs** (STT, TTS, LLM) | Request/response: tokens, config, **non-streaming** APIs (e.g. “transcribe this file”, “chat completions”). |

So:

- **WebRTC** = **streaming media** (your voice, assistant’s voice). In browsers, signaling for WebRTC often uses **WSS**; the media itself is still WebRTC (RTP).
- **WSS** = **streaming control and events** (signaling, Socket.IO, LiveKit signaling). So “streaming” in the control plane is indeed **WSS**, not plain HTTP.
- **HTTP/HTTPS** = **one request, one response** (REST). Used for tokens, webhooks, and for **server ↔ STT/TTS/LLM** when the API is request/response (e.g. “send this text to LLM”, “synthesize this sentence”).

**Short answer:** WebRTC is for **media** streaming; the **control/signaling** that sets up that stream is usually **WSS**. So “WebRTC is streaming” is correct, and the **signaling** part is indeed **WSS**, not plain HTTP. The **server’s** calls to STT/TTS/LLM may be **HTTP** (REST) or **WSS** (streaming API), depending on the provider.

---

## 3. End-to-End Data Flow (Single Voice-Assistant Call)

High level:

```
[You]  ←→  [Browser]  ←→  [Your App Server]  ←→  [STT / LLM / TTS]
```

### Step 1: Browser → App (join the “call”)

- **HTTPS**  
  - Browser loads the page: `https://your-app/...` (HTML/JS/CSS).
- **HTTPS (REST)**  
  - Browser asks your backend for a **LiveKit token** (or join token): `GET/POST https://your-app/.../token` (or similar).  
  - Backend returns a token (no streaming here).
- **WSS (signaling)**  
  - Browser connects to **LiveKit** (or your app) over **WSS** to **signal** “join room X”, “publish my mic”, “subscribe to assistant track”.  
  - If you use **Socket.IO**, the same browser also opens **WSS** to your app (`wss://your-app/socket.io`) for **app-level** events (e.g. “transfer to agent”, “session id”).

So at this stage you already have:

- **HTTP/HTTPS**: page load, token request.
- **WSS**: signaling (LiveKit and/or Socket.IO).

### Step 2: Your voice (mic) → server

- **WebRTC (media)**  
  - Browser captures mic → encodes audio → sends **WebRTC** media to LiveKit (or your app’s media endpoint).  
  - In many deployments this goes over **WSS** or **HTTPS** as the **transport** (e.g. when UDP is blocked), but the **logical** channel is still **WebRTC** (RTP/DTLS).  
  - So: **streaming = WebRTC**; the **underlying transport** can be WSS in the browser.
- **Your server** receives the media from LiveKit (or your own WebRTC stack), and gets **raw audio chunks** in order.

So: **your voice** flows as **WebRTC media** (often over WSS in the browser); the **server** sees a **stream of audio**.

### Step 3: Server → STT (speech-to-text)

- **Your app** has the audio stream (e.g. from LiveKit).
- It sends that stream to **Deepgram** (or another STT):
  - **Streaming STT**: usually **WSS** (`wss://api.deepgram.com/...`) or **HTTPS** streaming. So the **server ↔ STT** link is **WSS or HTTPS**, not WebRTC.  
- STT returns **text** (partial/final) over the same connection.
- So: **audio → text** uses **WSS (or HTTP)** between **your server** and **STT**; it is **streaming** on that WSS/HTTP connection, but it’s not WebRTC.

### Step 4: Server → LLM (text → text)

- Your app sends **text** (from STT) to the **LLM** (e.g. Claude, OpenAI):
  - Typically **HTTPS** REST (`https://api.anthropic.com/...` or similar).  
  - One request per turn (or streaming HTTP for token streaming).  
- So: **LLM** is almost always **HTTP/HTTPS** (or streaming over the same).

### Step 5: Server → TTS (text-to-speech)

- Your app sends **text** (LLM reply) to **TTS** (e.g. Deepgram TTS):
  - Often **HTTPS** (e.g. “synthesize this string”) or **WSS** if the TTS API is streaming.  
- TTS returns **audio bytes** (streaming or one response).
- So: **TTS** is **HTTP or WSS** between **your server** and **TTS**, not WebRTC.

### Step 6: Assistant’s voice back to you

- Your server gets **audio** from TTS, then:
  - Sends that audio **into the same LiveKit room** (or your WebRTC pipeline) as an **outgoing track**.  
- Browser receives it over **WebRTC** (the same media path as your mic, but in the other direction) and plays it.
- So: **playback** is again **WebRTC** (media); control/signaling stays **WSS**.

---

## 4. How They Work Together (Single “Call”)

- **One “call”** in the UI = one **WebRTC media path** (mic + speaker) and one **WSS** control/signaling path (LiveKit + optional Socket.IO).
- **Your server**:
  - Receives **audio** from WebRTC/LiveKit (streaming).
  - Converts **audio → text** via **STT (WSS/HTTPS)**.
  - Gets **text → text** from **LLM (HTTP/HTTPS)**.
  - Converts **text → audio** via **TTS (HTTP/WSS)**.
  - Sends **audio** back over **WebRTC/LiveKit** to the browser.
- So:
  - **Browser ↔ you**: WebRTC (media) + WSS (signaling).
  - **Server ↔ STT/TTS**: WSS or HTTP (streaming or REST).
  - **Server ↔ LLM**: HTTP (REST or streaming).

**WebRTC** is only between **browser and your media layer (e.g. LiveKit)**. Between **your server** and **STT/LLM/TTS**, you use **HTTP or WSS**, not WebRTC. So “WebRTC is streaming” is true for **media**; “WSS” is used for **signaling and for server↔STT/TTS streaming** where the provider supports it.

---

## 5. Quick Reference by “Who Talks to Whom”

| From → To | Protocol | Purpose |
|-----------|----------|---------|
| Browser → your app (page, token) | **HTTPS** | Load UI, get token. |
| Browser → LiveKit (signaling) | **WSS** | Join room, publish/subscribe. |
| Browser ↔ LiveKit (media) | **WebRTC** (often over WSS/UDP) | Your voice, assistant’s voice. |
| Browser → your app (events) | **WSS** (e.g. Socket.IO) | Control: transfer, session. |
| Your app → Deepgram STT | **WSS or HTTPS** | Stream audio → get text. |
| Your app → LLM | **HTTPS** | Send text, get reply. |
| Your app → Deepgram TTS | **HTTPS or WSS** | Send text, get audio. |
| Your app → LiveKit (inject audio) | **internal / SDK** | Send TTS audio into room. |

So: **one WebRTC “call”** in the UI is backed by **WebRTC (media) + WSS (signaling)** on the client side, and **HTTP/WSS** on the server side for STT, LLM, and TTS. They all work together; WebRTC is not “replaced” by WSS—they do different jobs (media vs control vs server-side APIs).

---

## 6. Diagram (Single Voice Call)

```
┌─────────────┐                    ┌─────────────────┐                    ┌──────────────┐
│   Browser   │  WebRTC (media)    │  Your app       │   WSS / HTTPS       │  STT / LLM   │
│ (1 UI call) │◄─────────────────►│  (LiveKit +     │◄──────────────────►│  / TTS       │
│             │  WSS (signaling)   │   backend)      │                    │  (e.g.       │
│             │◄─────────────────►│                 │                    │  Deepgram,   │
│             │  Socket.IO (WSS)   │                 │                    │  Claude)     │
└─────────────┘  optional          └─────────────────┘                    └──────────────┘
       │                                      │
       │  HTTPS (page, token)                  │  HTTP/WSS (streaming or REST)
       ▼                                      ▼
  Same origin (your domain)              External APIs
```

- **One connection type** in the UI = one **WebRTC call** (media) + **WSS** for signaling/control.
- **Different services, different protocols**: capability tables and function references (e.g. `SERVICE_FUNCTIONS_REFERENCE.md`) list **which URL and protocol** each feature uses (e.g. token = `https://`, Socket.IO = `wss://`, LiveKit = `wss://` for signaling). Use that table to see exactly which endpoint uses `http://` vs `wss://` for each capability.
