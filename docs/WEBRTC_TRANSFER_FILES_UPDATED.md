# Files Updated for WebRTC Transfer to Human Agent

This document lists all files that were modified to enable WebRTC voice assistant calls to transfer to human agents in the call center desktop.

---

## Summary

The WebRTC transfer functionality allows users in the voice assistant to request a human agent, which then:
1. Detects transfer intent from user speech
2. Initiates a Twilio call to the agent's extension (FusionPBX)
3. Caches customer profile data (conversation history, activities, user info) in Redis
4. Displays customer information in a popup window on the agent's desktop
5. Bridges the WebRTC call with the agent's SIP call

---

## Files Updated

### 1. **Backend - WebRTC Voice Server**

#### `convonet/webrtc_voice_server.py`

**Purpose:** Core WebRTC voice server that handles transfer logic, customer profile building, and caching.

**Key Functions Modified/Added:**

1. **`build_customer_profile_from_session()`** (lines 75-310)
   - Builds customer profile from session data
   - Retrieves conversation history from LangGraph
   - Extracts activities (calendar events, todos) from tool calls
   - Parses `HumanMessage`, `AIMessage`, and `ToolMessage` from LangGraph state

2. **`cache_call_center_profile()`** (lines 313-359)
   - Caches customer profile in Redis
   - **NEW:** Uses unique cache keys with `call_sid` or `call_id` to prevent overwrites
   - Maintains backward compatibility with extension-only key
   - Cache keys:
     - `callcenter:customer:{extension}` (most recent call)
     - `callcenter:customer:{extension}:{call_sid}` (Twilio calls)
     - `callcenter:customer:{extension}:{call_id}` (WebRTC calls)

3. **`initiate_agent_transfer()`** (lines 396-550)
   - Initiates Twilio call to agent extension
   - Creates conference bridge
   - **NEW:** Calls `cache_call_center_profile()` with `call_sid` after getting Call SID
   - Handles both agent leg and user leg (optional)

4. **`process_audio_async()`** (lines 1250-1507)
   - Processes audio from WebRTC sessions
   - Detects transfer intent
   - **NEW:** Calls `cache_call_center_profile()` with `call_id=session_id` for WebRTC calls
   - Initiates transfer flow via `start_transfer_flow()`

**Key Changes:**
- Added unique cache key support to prevent profile overwrites when multiple calls from same user transfer to same extension
- Integrated customer profile building with LangGraph conversation history
- Added activity extraction from tool calls (calendar events, todos)

---

### 2. **Backend - Call Center Routes**

#### `call_center/routes.py`

**Purpose:** API endpoints for the call center agent dashboard.

**Key Functions Modified:**

1. **`get_customer_data()`** (lines 358-423)
   - Fetches customer data for popup display
   - **NEW:** Accepts `call_sid` and `call_id` as query parameters
   - **NEW:** Prioritizes unique cache keys before falling back to extension-only key
   - Lookup order:
     1. `callcenter:customer:{extension}:{call_sid}` (if `call_sid` provided)
     2. `callcenter:customer:{extension}:{call_id}` (if `call_id` provided)
     3. `callcenter:customer:{extension}` (fallback)

**Key Changes:**
- Added support for unique call identifiers in customer data lookup
- Prevents showing wrong customer profile when multiple calls are active

---

### 3. **Backend - Twilio Routes**

#### `convonet/routes.py`

**Purpose:** Twilio webhook handlers for voice calls.

**Key Functions Modified:**

1. **`process_audio_webhook()`** (lines 450-650)
   - Handles Twilio audio webhooks
   - **NEW:** Calls `cache_call_center_profile()` with `call_sid` when transfer is requested
   - Ensures customer profile is cached before redirect to transfer endpoint

**Key Changes:**
- Added customer profile caching during Twilio call transfers
- Ensures profile is available when agent receives the call

---

### 4. **Frontend - Call Center JavaScript**

#### `call_center/static/js/call_center.js`

**Purpose:** Client-side logic for the call center agent dashboard.

**Key Functions Modified/Added:**

1. **`showCustomerPopup()`** (lines 1122-1188)
   - Displays customer popup with "Accept Call" button
   - Fetches customer data from `/api/customer/data`
   - **NEW:** Passes `call_sid` or `call_id` in query parameters

2. **`showCustomerInfoWindow()`** (NEW, lines ~1200-1300)
   - Displays read-only customer information window
   - Opens after "Accept Call" is clicked
   - Stays open during the call
   - Closes only when call ends

3. **`onCallEstablished()`** (lines ~800-900)
   - Called when call is connected
   - **NEW:** Opens `customerInfoWindow` if not already open
   - Ensures customer info is displayed even if initial popup was closed

4. **`onCallEnded()`** (lines ~900-1000)
   - Called when call ends
   - **NEW:** Closes `customerInfoWindow`
   - Cleans up customer data

5. **`initModalDragAndResize()`** (NEW, lines ~1400-1600)
   - Makes customer popup and info window draggable and resizable
   - Handles mouse events for dragging
   - Handles resize handles

6. **Event Listeners:**
   - **"Accept Call" button:** Closes popup, opens info window, answers call
   - **Close button:** Closes info window manually
   - **Call events:** Opens/closes info window based on call state

**Key Changes:**
- Added separate read-only customer info window
- Added drag and resize functionality
- Added unique call identifier support in API calls
- Improved call state management for customer info display

---

### 5. **Frontend - Call Center HTML Template**

#### `call_center/templates/call_center.html`

**Purpose:** HTML structure for the call center agent dashboard.

**Key Sections Added:**

1. **Customer Info Window** (NEW, lines ~400-450)
   ```html
   <!-- Customer Info Window (Read-only) -->
   <div id="customerInfoWindow" class="modal">
       <div class="modal-content">
           <div class="modal-header">
               <h3><i class="fas fa-user"></i> Customer Information</h3>
               <span class="close-modal" id="closeCustomerInfoWindow">&times;</span>
           </div>
           <div class="modal-body" id="customerInfoData">
               <!-- Customer data populated here -->
           </div>
       </div>
   </div>
   ```

**Key Changes:**
- Added new `customerInfoWindow` div (separate from `customerPopup`)
- No "Accept Call" button in info window (read-only)
- Same structure as popup but for persistent display

---

### 6. **Frontend - Call Center CSS**

#### `call_center/static/css/call_center.css`

**Purpose:** Styling for the call center agent dashboard.

**Key Styles Added/Modified:**

1. **`.modal-content`** (lines ~200-250)
   - **NEW:** `resize: both` - Makes modals resizable
   - **NEW:** `overflow: auto` - Handles content overflow
   - **NEW:** `min-width`, `max-width`, `min-height`, `max-height` - Resize constraints

2. **`.modal-header`** (lines ~250-300)
   - **NEW:** `cursor: move` - Indicates draggable area
   - **NEW:** User-select disabled for better dragging

3. **`#customerInfoWindow`** (NEW, lines ~400-450)
   - Styles for the read-only customer info window
   - Similar to `#customerPopup` but without accept button styling

4. **`.modal-overlay`** (NEW, lines ~500-550)
   - Prevents interference with dragging
   - Proper z-index layering

**Key Changes:**
- Added resizable and draggable styles
- Added styles for customer info window
- Improved modal layering and interaction

---

## Data Flow

### Transfer Flow

```
1. User in WebRTC voice assistant says "transfer to agent"
   ↓
2. Deepgram transcribes: "transfer to agent"
   ↓
3. LangGraph detects transfer intent
   ↓
4. webrtc_voice_server.py:
   - build_customer_profile_from_session() → Builds profile with history & activities
   - cache_call_center_profile(extension, session_data, call_id=session_id) → Caches in Redis
   - initiate_agent_transfer() → Creates Twilio call to extension
   ↓
5. Twilio calls FusionPBX extension (e.g., 2001)
   ↓
6. Agent desktop receives incoming call
   ↓
7. call_center.js:
   - onIncomingCall() → Detects incoming call
   - showCustomerPopup() → Fetches customer data with call_id
   - User clicks "Accept Call"
   - showCustomerInfoWindow() → Opens persistent info window
   - answerCall() → Answers the call
   ↓
8. Call connected → onCallEstablished() → Ensures info window is open
   ↓
9. Call ends → onCallEnded() → Closes info window
```

### Customer Data Lookup Flow

```
1. Agent receives call with Call-ID or Call SID
   ↓
2. call_center.js calls: GET /api/customer/data?call_id={call_id}
   ↓
3. call_center/routes.py:
   - get_customer_data() extracts call_id from query
   - Looks up Redis key: callcenter:customer:{extension}:{call_id}
   - Falls back to: callcenter:customer:{extension}
   ↓
4. Returns customer profile (name, email, conversation history, activities)
   ↓
5. call_center.js displays in popup/info window
```

---

## Key Features Implemented

### 1. **Unique Customer Profile Caching**
- Prevents profile overwrites when multiple calls from same user transfer to same extension
- Uses `call_sid` (Twilio) or `call_id` (WebRTC) as unique identifier
- Maintains backward compatibility with extension-only key

### 2. **Customer Information Display**
- Initial popup with "Accept Call" button
- Persistent read-only info window after call accepted
- Displays:
  - Customer name, email, phone
  - Conversation history (user and assistant messages)
  - Activities (calendar events, todos created/updated/completed)

### 3. **Draggable and Resizable Windows**
- Customer popup and info window can be moved
- Windows can be resized
- Maintains position during call

### 4. **Call State Management**
- Info window opens when call is established
- Info window closes when call ends
- Manual close option available

---

## Configuration Required

### Environment Variables

```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_TRANSFER_CALLER_ID=your_twilio_number
VOICE_ASSISTANT_TRANSFER_BASE_URL=https://your-domain.com

# FusionPBX Configuration
FREEPBX_DOMAIN=136.115.41.45

# Redis (for caching customer profiles)
REDIS_URL=redis://localhost:6379
```

### Redis Keys Used

- `callcenter:customer:{extension}` - Most recent call (backward compatibility)
- `callcenter:customer:{extension}:{call_sid}` - Twilio calls (unique)
- `callcenter:customer:{extension}:{call_id}` - WebRTC calls (unique)
- `session:{session_id}` - WebRTC session data

---

## Testing Checklist

- [ ] WebRTC call can request transfer to agent
- [ ] Customer profile is cached correctly with unique key
- [ ] Agent receives call on extension
- [ ] Customer popup appears with correct data
- [ ] "Accept Call" opens info window
- [ ] Info window stays open during call
- [ ] Info window closes when call ends
- [ ] Multiple calls from same user show correct profiles
- [ ] Windows are draggable and resizable
- [ ] Conversation history displays correctly
- [ ] Activities (calendar, todos) display correctly

---

## Migration Notes

If you're updating another project, you'll need to:

1. **Copy the modified functions** from each file
2. **Ensure Redis is configured** and accessible
3. **Update environment variables** with Twilio and FusionPBX settings
4. **Add the new HTML elements** for customer info window
5. **Update CSS** for draggable/resizable modals
6. **Test the transfer flow** end-to-end

---

## Related Documentation

- `WEBRTC_CALL_FLOW_DIAGRAM.md` - Complete call flow diagram
- `CALL_CENTER_TWO_POPUPS_ISSUE.md` - Explanation of two popups issue
- `THREAD_ID_LIFECYCLE.md` - How thread_id is managed
- `WEBRTC_ASR_TTS_COMPONENTS.md` - ASR/TTS components used

---

## Summary

**Total Files Updated: 6**

1. `convonet/webrtc_voice_server.py` - Core transfer logic and profile caching
2. `call_center/routes.py` - Customer data API with unique identifier support
3. `convonet/routes.py` - Twilio webhook handler with profile caching
4. `call_center/static/js/call_center.js` - Frontend logic for popups and windows
5. `call_center/templates/call_center.html` - HTML structure for info window
6. `call_center/static/css/call_center.css` - Styling for draggable/resizable windows

**Key Improvements:**
- ✅ Unique customer profile caching (prevents overwrites)
- ✅ Persistent customer info window during calls
- ✅ Draggable and resizable windows
- ✅ Conversation history and activities display
- ✅ Proper call state management

