# Transfer Call Fix v2 - Preventing Duplicate Prompts & UI Clarity

## Issues Reported

### Problem 1: Multiple Screen-Pops for Accept Button
- User reported seeing multiple "accept the call" buttons appearing simultaneously
- Each transfer INVITE was potentially triggering the prompt display multiple times
- No guard against duplicate transfer handling events

### Problem 2: Confusion Between Calls
- User couldn't distinguish between which call was the first (current) and which was the second (transfer)
- No clear labeling of "Current Call" vs "Incoming Transfer Call"
- Both calls appeared to be in similar visual format

### Problem 3: No Ringing Tone on Wrong Call
- After accepting one call, user heard no ringing tone
- Suggested the wrong session was being activated
- Likely result: Agent accepted transfer call but system didn't properly route audio

### Root Causes

1. **No Deduplication Guards**: The previous implementation didn't prevent multiple `handleTransferCall()` invocations for the same INVITE
2. **Event Listener Proliferation**: Multiple event listeners were attached to the same button elements across different prompt instances
3. **No Unique Identification**: Transfer prompts could accumulate in DOM without unique identifiers
4. **Lack of Visual Hierarchy**: Current call and transfer call were displayed with equal prominence
5. **No Timeout Handling**: If user didn't respond, transfer stayed pending indefinitely

---

## Solution Implemented

### 1. Deduplication Guards (Prevent Duplicate Handling)

```javascript
// Add new state tracking properties
this.isHandlingTransfer = false;           // Is any transfer currently being handled?
this.transferTimeoutId = null;             // Timeout for auto-reject
this.lastProcessedTransferId = null;       // Track last processed transfer ID

// In handleTransferCall():
const transferId = identity.callId || session.id;
if (this.isHandlingTransfer || this.lastProcessedTransferId === transferId) {
    console.warn('Transfer already being handled or duplicate event');
    return;  // Exit early to prevent duplicate handling
}
this.isHandlingTransfer = true;
this.lastProcessedTransferId = transferId;
```

**Effect**: Multiple INVITE events for the same transfer call are ignored. Only the first one is processed.

### 2. Single Transfer Notification (Prevent DOM Proliferation)

```javascript
// Remove any existing transfer notification FIRST
const existingAlert = document.querySelector('.transfer-notification');
if (existingAlert) {
    console.log('Removing existing transfer notification');
    existingAlert.remove();
}

// Give the notification a unique ID for later reference
const transferNotification = document.createElement('div');
transferNotification.id = 'transferNotificationPrompt';
```

**Effect**: Only one transfer prompt can exist at a time in the DOM. Old ones are removed before creating new ones.

### 3. Auto-Reject Timeout (30 Seconds)

```javascript
// Set a timeout for transfer acceptance (30 seconds)
if (this.transferTimeoutId) clearTimeout(this.transferTimeoutId);
this.transferTimeoutId = setTimeout(() => {
    if (this.pendingTransferSession) {
        console.log('Transfer acceptance timeout - auto-rejecting');
        this.rejectTransferCall(session);
    }
}, 30000);  // 30 seconds match Twilio default
```

**Effect**: If agent doesn't accept/reject within 30 seconds, the transfer is automatically rejected.

### 4. Improved UI with Call Distinction

Before:
```
Call Transfer Incoming
AgentName (123-456-7890) is calling

[Accept Transfer] [Reject]
```

After:
```
📞 Incoming Call Transfer

Current Call: Original Caller (their number)

Transfer From: New Caller (their number)
Accept to answer the transfer call, or reject to keep current call

[✓ Accept Transfer] [✕ Reject]
```

**HTML Implementation**:
```javascript
const currentCallInfo = oldSession ? 
    `<div class="current-call-info">
        <p><strong>Current Call:</strong> ${this.currentCall?.caller_name} (${this.currentCall?.caller_number})</p>
    </div>` : '';

const incoming = `
    <div class="incoming-call-info">
        <p><strong>Transfer From:</strong> <span style="color: #ff6b35;">${callerName}</span> (${callerNumber})</p>
    </div>
`;
```

### 5. Improved CSS Styling

**Color Coding**:
- **Green border/background** for current call info (active call stays active)
- **Red border** for transfer notification (incoming/pending action required)  
- **Yellow/Orange gradient** background for alert prominence

**Key Styles**:
```css
.current-call-info {
    border-left: 4px solid #10b981;  /* Green - keep active */
    background: rgba(255, 255, 255, 0.3);
}

.incoming-call-info {
    border-left: 4px solid #dc2626;  /* Red - requires action */
    background: rgba(255, 255, 255, 0.2);
}

.transfer-notification {
    border: 3px solid #dc2626;  /* Bold red border */
    box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
}
```

### 6. Improved Event Handling (Prevent Double-Firing)

```javascript
// Use local 'handled' flag to ensure button clicks only fire once
let handled = false;

acceptBtn.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopImmediatePropagation();  // Stop event from bubbling
    if (!handled) {
        handled = true;  // Lock this handler
        console.log('Accept transfer button clicked');
        transferNotification.remove();
        onAccept();
    }
});
```

**Effect**: Even if multiple listeners somehow exist, only the first click is processed.

### 7. Clear Flag Management

```javascript
// In acceptTransferCall():
this.isHandlingTransfer = false;  // Release lock
this.lastProcessedTransferId = null;  // Clear processed ID

// In rejectTransferCall():
this.isHandlingTransfer = false;  // Release lock
if (this.transferTimeoutId) {
    clearTimeout(this.transferTimeoutId);  // Clear timeout
    this.transferTimeoutId = null;
}
```

---

## Testing Scenarios

### Scenario 1: Slow User Response
1. First call arrives and connects ✓
2. Transfer INVITE arrives 7 seconds later
3. Agent sees ONE clear transfer prompt with:
   - Current call info (Original Caller - Green labeled)
   - Transfer pending (New Caller - Red labeled)
4. Agent takes 20 seconds to decide (within 30-second timeout)
5. Agent clicks Accept ✓
   - Old call terminates
   - New call becomes active
   - Audio plays for new session

### Scenario 2: User Rejects Transfer
1. First call active ✓
2. Transfer INVITE arrives
3. Prompt shows both calls
4. Agent clicks Reject
5. Transfer call terminated ✓
6. Original call continues (no interruption) ✓

### Scenario 3: Rapid Fire Events (Network Glitch)
1. First call active ✓
2. Transfer INVITE arrives at T=0
3. Duplicate INVITE arrives at T=50ms (network retransmit)
4. First INVITE: Creates pending transfer, shows prompt ✓
5. Second INVITE: Ignored due to `isHandlingTransfer` flag ✓
6. Only ONE prompt appears ✓

### Scenario 4: Timeout Auto-Reject
1. First call active ✓
2. Transfer INVITE arrives
3. Prompt displays
4. Agent walks away (doesn't answer for 32 seconds)
5. At T=30s: Auto-reject triggers ✓
6. Transfer session terminates ✓
7. Original call still active ✓

---

## Key Improvements

| Aspect | Before | After |
|--------|--------|-------|
| Multiple Prompts | ❌ Possible | ✅ Prevented |
| Call Clarity | ❌ Confusing | ✅ Clear distinction |
| Timeout Handling | ❌ None | ✅ 30-second auto-reject |
| Event Deduplication | ❌ None | ✅ Full protection |
| UI Labels | ❌ Generic | ✅ Current vs Transfer |
| Visual Hierarchy | ❌ Flat | ✅ Color-coded |
| Button Safety | ❌ Could fire twice | ✅ Protected with flag |

---

## Technical Details

### State Machine Transitions

```
NORMAL CALL IN PROGRESS
    ↓
First INVITE arrives (Transfer request)
    ↓
isHandlingTransfer = true ← LOCK
showTransferPrompt() ← Only once due to unique ID
    ↓
User sees:
├─ Current Call (green) - stays active
└─ Incoming Transfer (red) - pending decision
    ↓
[User accepts] OR [30 sec timeout]
    ↓
acceptTransferCall() / rejectTransferCall()
    ↓
isHandlingTransfer = false ← UNLOCK
Flags cleared
    ↓
NEW STATE (call accepted OR original call continues)
```

### Duplicate Detection Flow

```
Event 1 (INVITE): isHandlingTransfer=F → set T → Process ✓
Event 1b (INVITE retry): isHandlingTransfer=T → Return ✗
Event 2 (PRACK): isHandlingTransfer=T → Already locked ✗
User clicks: Button handler has handled=F → set T → Fire ✓
User clicks again: Button handler has handled=T → Skip ✗
```

---

## Files Modified

1. **call_center/static/js/call_center.js**
   - Added deduplication flags to constructor
   - Enhanced `handleTransferCall()` with guards
   - Rewrote `showTransferPrompt()` with improved UI and event handling
   - Enhanced `acceptTransferCall()` with flag management
   - Enhanced `rejectTransferCall()` with cleanup

2. **call_center/static/css/call_center.css**
   - Added `.current-call-info` styles
   - Added `.incoming-call-info` styles
   - Enhanced `.transfer-notification` styling
   - Improved button hover/active states
   - Added better visual hierarchy

---

## Deployment

**Commit**: `eaf5c45`  
**Branch**: `main`  
**Date**: 2026-02-14  

Changes successfully pushed to GitHub hjleepapa/convonet-anthropic
