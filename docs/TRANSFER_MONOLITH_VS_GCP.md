# Transfer to Human Agent (2001@FusionPBX): Monolith vs GCP

## Main difference: Twilio REST API + transfer_bridge (monolith flow you saw)

On the **monolith**, when the user requested transfer, the server did **not** only return TwiML for the current call. It also (or instead) called the **Twilio REST API** to **create a new outbound call**:

1. **POST** to `https://api.twilio.com/2010-04-01/Accounts/.../Calls.json`  
   - `To`: `sip:2001@136.115.41.45;transport=udp`  
   - `From`: caller number (e.g. `+12344007818`)  
   - `Url`: `https://.../convonet_todo/twilio/voice_assistant/transfer_bridge?extension=2001`  
   - `Method`: POST  

2. Twilio creates that call and dials `sip:2001@...`. When that **SIP leg connects** (call status becomes "in-progress"), **Twilio’s servers** make an **HTTP POST** to the `Url` (transfer_bridge) to get the next TwiML. So **Twilio** is who POSTs to transfer_bridge — not our app.

3. Our server (monolith or voice-gateway) **receives** that POST and **returns** TwiML (`<Dial><Sip>...</Sip></Dial>`, `action=transfer_callback`). When the Dial ends, Twilio POSTs to transfer_callback.

So you see in Twilio logs: (1) **Calls.json** (REST create), (2) **POST to transfer_bridge**, (3) **POST to transfer_callback**. On GCP we were **not** calling the Twilio REST API or exposing **transfer_bridge**, so you saw no Twilio API request.

## What we added on GCP to match the monolith

| Piece | Monolith | GCP (now) |
|-------|----------|-----------|
| **Twilio REST create call** | `initiate_agent_transfer()` → `client.calls.create(to=sip:2001@..., from_=caller_id, url=transfer_bridge)` | **voice-gateway:** `_initiate_twilio_transfer_call(extension)` → same `client.calls.create(...)` with `url=https://v2.convonetai.com/twilio/voice_assistant/transfer_bridge?extension=2001` |
| **transfer_bridge endpoint** | `GET/POST /convonet_todo/twilio/voice_assistant/transfer_bridge` returns TwiML Dial to 2001 + callback | **voice-gateway:** `GET/POST /twilio/voice_assistant/transfer_bridge` — same TwiML (Dial to extension, action=transfer_callback) |
| **When we call REST** | On transfer (WebRTC/Socket.IO path and/or Twilio path) | On transfer: (1) **WebSocket** pipeline when we get `transfer_marker` we call `_initiate_twilio_transfer_call(ext)`; (2) **Twilio** `process_audio` when we have `transfer_marker` we also call it, then return TwiML for the inbound call |

So on GCP you should now see the same Twilio activity: **Calls.json** (create outbound) and **POST to transfer_bridge** when 2001 connects.

## Required config (voice-gateway-service)

For the REST create-call and for transfer_bridge to be reachable by Twilio:

- **TWILIO_ACCOUNT_SID**, **TWILIO_AUTH_TOKEN** — so we can call `client.calls.create(...)`.
- **TWILIO_TRANSFER_CALLER_ID** or **TWILIO_CALLER_ID** or **TWILIO_PHONE_NUMBER** — used as `From` for the created call.
- **VOICE_GATEWAY_PUBLIC_URL** or **WEBHOOK_BASE_URL** — must be `https://v2.convonetai.com` so the `Url` we pass to Twilio is `https://v2.convonetai.com/twilio/voice_assistant/transfer_bridge?extension=2001`. If this is wrong, Twilio will not find transfer_bridge.
- **FREEPBX_DOMAIN** or **FUSIONPBX_SIP_DOMAIN** — so we build `sip:2001@<domain>;transport=udp`.

## Other differences (unchanged)

- **Twilio webhook (A call comes in):** Must be `https://v2.convonetai.com/twilio/call` (not `/convonet_todo/twilio`).
- **Keyword shortcut:** In `/twilio/process_audio`, `has_transfer_intent(transcription)` still returns TwiML Dial immediately (no agent call).
- **Browser (WebSocket):** We still send “I’ll connect you…” and cache context; we **also** call the Twilio REST API so 2001 receives a call and Twilio will POST to transfer_bridge.

## Summary

- **Monolith:** On transfer, server called **Twilio REST API** to create an outbound call to `sip:2001@...` with `Url=transfer_bridge`. Twilio then POSTed to **transfer_bridge** and got Dial TwiML. You saw Calls.json + transfer_bridge in Twilio.
- **GCP (before):** We did not call the REST API or expose transfer_bridge → no Twilio API request.
- **GCP (now):** We call **Twilio REST API** on transfer (WebSocket and Twilio flow) and expose **/twilio/voice_assistant/transfer_bridge** so the same Calls.json + transfer_bridge flow runs as on the monolith.

## Troubleshooting: "Transfer still not working"

### If you see REST 201 + "Twilio REST transfer initiated" but no "transfer_bridge called"

Your logs show:
- Voice-gateway: `Twilio REST: created outbound call to sip:2001@136.115.41.45;transport=udp (Call SID: CA...)` and `Twilio REST transfer initiated for extension 2001`.
- No line `transfer_bridge called: CallSid=...` in voice-gateway.

So the **app and Twilio REST are working**. Twilio **never POSTs to transfer_bridge** because it only does that when the **outbound call to 2001 connects** (e.g. 2001 answers). So the **SIP leg from Twilio to 136.115.41.45 (extension 2001) is not connecting**. The problem is between Twilio and FusionPBX, not GCP.

**FusionPBX hostname vs IP:** The call-center UI logs into **pbx.hjlees.com**; the server is the same as **136.115.41.45**. Extensions are often registered as `2001@pbx.hjlees.com`. If transfer fails when using the IP, set **FREEPBX_DOMAIN** (or **FUSIONPBX_SIP_DOMAIN**) to **pbx.hjlees.com** on voice-gateway so Twilio uses `sip:2001@pbx.hjlees.com`. Ensure `pbx.hjlees.com` resolves to 136.115.41.45 from the public internet (DNS) and that FusionPBX accepts SIP to that hostname.

**Fix on the SIP/FusionPBX side:**
1. **Extension 2001** must be registered (e.g. call-center/JsSIP at pbx.hjlees.com) so it can receive the call.
2. **FusionPBX** must accept SIP from Twilio: allow Twilio IP ranges (see [Twilio SIP](https://www.twilio.com/docs/voice/ip-addresses)) or use a SIP trunk that Twilio can reach.
3. **Dialplan** on the PBX (136.115.41.45 / pbx.hjlees.com) must route incoming SIP calls to extension 2001 (e.g. from a "public" or "twilio" context to 2001 or to `user/2001@pbx.hjlees.com`).
4. **Firewall**: UDP (and TCP if used) for SIP/RTP from Twilio to the PBX (136.115.41.45 or pbx.hjlees.com) must be open.

**Voice-gateway does not talk to FusionPBX.** The only traffic to your FusionPBX VM is from **Twilio** (SIP and RTP when Twilio places the call to 2001). So you do **not** need a firewall rule “from voice-gateway to FusionPBX.” You need **inbound** rules on the **FusionPBX VM’s network** (GCP VPC or host firewall) allowing **Twilio’s IP ranges** to reach the VM. See below.

---

## Firewall on the FusionPBX GCP VM

FusionPBX runs on a GCP VM (e.g. 136.115.41.45). **Twilio** sends SIP and RTP to that VM when placing the transfer call. Configure the VM’s firewall (GCP VPC firewall rules or the VM’s iptables) to allow **inbound** from Twilio:

- **SIP signaling:** Twilio regional gateways — allow **inbound** to the VM on ports **5060** (UDP/TCP) and **5061** (TLS). Source IPs: Twilio’s [SIP trunking / Programmable Voice IP ranges](https://www.twilio.com/docs/voice/ip-addresses) (e.g. for North America: `54.172.60.0/23`, `54.244.51.0/24`; other regions in the same doc). Allowlist all regions you may use.
- **RTP (media):** Allow **inbound** UDP **10000–60000** (or the range your FreeSWITCH uses) from Twilio media range **168.86.128.0/18** (see [Twilio voice media IPs](https://www.twilio.com/docs/voice/voice-media-ip-expansion-security-faq)).

Example (GCP style): one rule allowing TCP/UDP 5060,5061 from the Twilio signaling CIDRs, and one rule allowing UDP 10000–60000 from 168.86.128.0/18, both to the FusionPBX VM’s tag or IP. No rule from Cloud Run (voice-gateway) to the VM is required.

---

In Twilio Console → that call (CA...) → **Request Inspector**: if there is only the Calls.json request and no second request to `transfer_bridge`, that confirms the call to 2001 never connected. Check the call **status** (e.g. failed, no-answer, canceled) and fix SIP/2001 as above.

**Success (monolith):** Call to `sip:2001@136.115.41.45` connected → Twilio POSTed to transfer_bridge (convonet-anthropic.onrender.com) → our server returned TwiML → later Twilio POSTed to transfer_callback. **Failed (GCloud):** Call to `sip:2001@pbx.hjlees.com` **Failed** (0 sec, Status Failed) → Twilio never got "in-progress" → Twilio **never** POSTed to v2.convonetai.com’s transfer_bridge. So the failure is the SIP leg to pbx.hjlees.com (DNS, reject, or timeout); use **136.115.41.45** for Twilio if that worked on the monolith.

---

1. **REST call succeeded (201) but no POST to transfer_bridge**
   - Twilio only POSTs to the `Url` when the **outbound call to 2001 connects** (e.g. 2001 answers or the leg is in progress). If the SIP call to `sip:2001@136.115.41.45` never connects (FusionPBX not answering, firewall, wrong IP/port), you will see Calls.json 201 but no transfer_bridge request.
   - **Check:** In Twilio Console → that call → **Request Inspector**: if there is no second request to `https://v2.convonetai.com/twilio/voice_assistant/transfer_bridge`, the SIP leg to 2001 did not connect. Fix FusionPBX/SIP (see above).

2. **Path routing (404 → "Sorry application error, good bye")**
   - Twilio POSTs to `https://v2.convonetai.com/twilio/voice_assistant/transfer_bridge?extension=2001` when the call to 2001 connects. If that request returns **HTTP 404** (e.g. `{"detail": "Not Found"}`), Twilio reports error **11200** and typically plays a message like **"Sorry, application error, good bye"** and hangs up.
   - **Cause:** The request was not reaching a service that has the `transfer_bridge` route. Two solutions:
     - **Option A (recommended):** In your GCP HTTP(S) load balancer, route **all** paths under **`/twilio/`** to **voice-gateway-service** (or add a rule for `/twilio/voice_assistant/*` to voice-gateway).
     - **Option B (fallback):** **call-center-service** now also implements **`/twilio/voice_assistant/transfer_bridge`** and **`/twilio/transfer_callback`**. If your LB sends these paths to call-center (e.g. as default backend), Twilio will get 200 and TwiML from call-center. Set on **call-center-service**: **FREEPBX_DOMAIN** or **FUSIONPBX_SIP_DOMAIN** (and optionally **WEBHOOK_BASE_URL** or **VOICE_GATEWAY_PUBLIC_URL** for the callback URL). Then redeploy **call-center** (e.g. `gcloud builds submit --config cloudbuild-callcenter.yaml .` or full build).
   - After either fix, Twilio’s POST should get **200** and TwiML, and the “application error” message should stop.

3. **Voice-gateway logs**
   - After the change, on transfer you should see: `Attempting Twilio REST transfer to extension 2001` and either `Twilio REST transfer initiated for extension 2001 (Call SID: CA...)` or `Twilio REST transfer NOT initiated: <reason>`.
   - When Twilio POSTs to transfer_bridge you should see: `transfer_bridge called: CallSid=... From=... extension=2001` and `transfer_bridge returning TwiML (len=...)`. If the REST call succeeds but you never see `transfer_bridge called`, the request is not reaching voice-gateway (routing or Twilio never called the URL).
