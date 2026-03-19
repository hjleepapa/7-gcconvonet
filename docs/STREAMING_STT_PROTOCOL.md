# Streaming STT Protocol (Voice Gateway WebSocket)

## Overview

The voice gateway WebSocket (`/webrtc/ws`) supports two modes:

- **Batch (default):** Client sends `start_recording` → `audio_chunk`(s) → `stop_recording`. Server runs STT on the full blob once.
- **Streaming (Phase 1):** Client sends `start_recording` with `stt_mode: "streaming"` → `audio_frame`(s) → `end_utterance`. Server buffers frames, then runs **batch STT** on the concatenated buffer and the same LLM+TTS pipeline. True streaming STT (e.g. Deepgram streaming) is Phase 2.

## Client → Server message types (streaming)


| Type            | Purpose                                                                                       |
| --------------- | --------------------------------------------------------------------------------------------- |
| `audio_frame`   | Small audio chunk (base64). Server appends to per-session buffer.                             |
| `end_utterance` | Signal end of current utterance; server runs STT on buffer, then LLM+TTS, then clears buffer. |
| `stream_reset`  | Discard buffered frames and reset for the next utterance.                                     |


## Flow

1. **Start streaming:** Send `start_recording` with `stt_mode: "streaming"` and same `session_id` / `language` as batch.
2. **Send audio:** Send repeated `audio_frame` messages with `session_id`, `sequence`, and `data_b64`.
3. **End utterance:** Send `end_utterance` with `session_id`. Server concatenates buffered frames, runs existing batch STT + LLM + TTS, sends back transcript/audio as today. Buffer is cleared; client can send more `audio_frame` and another `end_utterance` for the next turn.
4. **Optional:** Send `stream_reset` to discard the current buffer without running STT.

## Constraints

- `end_utterance` is only valid when the session was started with `stt_mode: "streaming"`.
- If the buffer is shorter than ~0.1 s, server responds with an error and does not run the pipeline.
- Only one utterance is processed at a time; if the client sends `end_utterance` while the previous one is still processing, server returns a `busy` error.

## Schemas

See `convonet/schemas.py`: `AudioFrameMessage`, `EndUtteranceMessage`, `StreamResetMessage`, and `ClientMessageType.AUDIO_FRAME` / `END_UTTERANCE` / `STREAM_RESET`.

## Validation

The **`/vad`** page uses the streaming protocol: after auth it sends `start_recording` with `stt_mode: "streaming"` once, then for each detected utterance it sends `audio_frame` (from MediaRecorder `ondataavailable` every 250 ms while VAD sees speech) and `end_utterance` when VAD detects silence. Use `/vad` to validate Phase 1.

## Phases

- **Phase 1 (current):** Protocol + server-side buffering + batch STT on buffer. ✅ Validated via `/vad`.
- **Phase 2:** Replace buffered run with real streaming STT (e.g. Deepgram streaming).
- **Phase 3:** Dedicated streaming UI (e.g. `/streaming-voice`) — optional; `/vad` already exercises streaming.
- **Phase 4:** Polish and docs.

