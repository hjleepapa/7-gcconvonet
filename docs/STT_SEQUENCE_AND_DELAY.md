# Managing Delays and Sequencing Integrity in STT Transcription

This doc describes how the voice pipeline handles (and can improve) **delays** during STT and **sequencing integrity** of audio chunks.

---

## Current Behavior

- **Audio path**: Client or LiveKit → server → `StreamingSTTSession.audio_queue` (asyncio.Queue) → Deepgram streaming API → `_handle_message` → final/partial transcript.
- **Order today**: A single FIFO queue per session. Chunks are put in the order they are received and sent to Deepgram in that order. So **in-order delivery from the client** implies in-order processing.
- **Delays**: If Deepgram or the network is slow, the queue can grow. There is no backpressure, queue limit, or timeout; the process just waits.

---

## 1. Maintaining Sequencing Integrity

**Goal:** Ensure that the stream of audio chunks sent to STT is in the correct order even if chunks arrive out of order or with gaps (e.g. network jitter, packet reordering).

### Option A: Keep single queue, add sequence numbers (lightweight)

- **Producer (where chunks are received):** Tag each chunk with a **sequence number** (e.g. incrementing `seq` per session) and optionally a **timestamp** (e.g. capture or receive time).
- **Consumer (before sending to Deepgram):** Keep using one queue, but store chunks as `(seq, ts, payload)`. When taking from the queue, you still get FIFO order from the network. If you later add multiple producers or a reorder buffer, you use `seq` to sort and drop duplicates.
- **Integration:** In `StreamingSTTSession.send_audio(audio_chunk)`, you could change to `send_audio(seq, ts, audio_chunk)` and have the run_loop pass only the payload to Deepgram while logging or monitoring `seq`/`ts` for diagnostics and future reordering.

### Option B: Reorder buffer (for out-of-order arrival)

- **Producer:** Send chunks with `(seq, timestamp_ms, payload)`.
- **Consumer:** Maintain a small **reorder buffer** (e.g. by `seq`). When a chunk arrives, insert by `seq`. When the next expected `seq` is present, flush in order to the Deepgram connection. If a chunk is too old (e.g. timestamp older than N ms), drop it to avoid long delays.
- **Result:** Sequencing integrity is maintained even when packets arrive out of order; you only send ordered, in-sequence audio to STT.

---

## 2. Managing Delays During STT

**Goal:** Avoid unbounded latency when the queue backs up or Deepgram is slow.

### A. Bounded queue and backpressure

- **Queue max size:** Use a bounded `asyncio.Queue(maxsize=...)` (e.g. 100 chunks or ~2–3 seconds of audio). When the queue is full, `put` can block or you can drop the oldest chunk (or drop the new one) so the pipeline doesn’t grow without limit.
- **Effect:** Limits how far “behind” the STT can get; delays are capped and you can prioritize recent audio.

### B. Timeout on consumer side

- **Queue get with timeout:** Use `await asyncio.wait_for(self.audio_queue.get(), timeout=2.0)` in the run_loop. If no chunk arrives within 2 seconds, you can send a “flush” or “end of utterance” signal to Deepgram (if the API supports it) so you get a transcript for what you have so far, then continue. That prevents indefinite waits and keeps latency predictable.

### C. Drop stale chunks (prioritize freshness)

- **Per-chunk timestamp:** When you have timestamps on chunks, before sending to Deepgram, compare chunk time to “now.” If the chunk is older than a threshold (e.g. 500 ms or 1 s), drop it instead of sending. That keeps **sequence integrity** (you still send in order) while **reducing delay** by not sending very old audio.
- **Trade-off:** You may lose some words at the start of a burst; the rest of the stream stays in order and lower latency.

### D. STT response timeout

- **If Deepgram doesn’t return a result:** After sending a batch or a “speech end” signal, if no transcript arrives within N seconds, treat the segment as empty or retry according to your product needs. That avoids the pipeline hanging on a single slow or failed STT response.

---

## 3. Summary Table

| Concern | Approach | Where in code |
|--------|----------|----------------|
| **Sequence integrity** | Single FIFO queue (current); optional seq + reorder buffer if packets can arrive out of order | `StreamingSTTSession`: `send_audio`, `run_loop` |
| **Delay from queue growth** | Bounded queue; drop old or new chunks when full | `audio_queue = asyncio.Queue(maxsize=...)`; drop policy in `send_audio` or before `put` |
| **Delay from waiting for chunks** | Timeout on `queue.get()`; periodic flush to Deepgram | `run_loop`: `wait_for(queue.get(), timeout=...)` |
| **Delay from old audio** | Timestamp chunks; drop chunks older than threshold before sending to STT | Before `connection.send_media(...)` |
| **STT response delay** | Timeout in transcript handler or after “end of speech”; treat as complete or retry | `_handle_message` or the code that waits for final transcript |

---

## 4. Minimal Code Hooks (for implementation)

- **Sequence numbers:** In `send_audio`, add a session-local counter and attach `seq` to the chunk (e.g. store `(seq, chunk)` in the queue). Consumer passes only `chunk` to Deepgram; use `seq` for logging or reorder logic.
- **Bounded queue:** Replace `self.audio_queue = asyncio.Queue()` with `asyncio.Queue(maxsize=150)` and in `send_audio` use `put_nowait`; if full, drop oldest (e.g. get_nowait then put the new one) or drop new.
- **Timeout on get:** In the `while not self.stop_event.is_set()` loop, use `audio_chunk = await asyncio.wait_for(self.audio_queue.get(), timeout=2.0)` and on timeout, optionally send a control message to Deepgram to flush, then continue.
- **Timestamps:** When receiving audio (e.g. in `handle_audio_data` or LiveKit callback), set `ts = time.time()` and pass `(ts, chunk)` into the queue; in the consumer, if `time.time() - ts > 0.5` then skip sending that chunk to preserve low latency while keeping order for non-stale chunks.

These changes keep the existing architecture and add explicit **sequencing** and **delay management** around STT.
