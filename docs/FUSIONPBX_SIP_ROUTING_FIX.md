# FusionPBX SIP Routing Fix for WRONG_CALL_STATE Error

## Problem Identified

From FusionPBX logs:
- ✅ Twilio SIP INVITE is received (`receiving invite from 54.172.60.0:5060`)
- ✅ ACL check passes (`IP [157.131.169.78] passed ACL check [Twilio-SIP]`)
- ❌ Call abandoned with `WRONG_CALL_STATE` after 10 seconds
- ❌ Call stays in `CS_NEW` state (never progresses)

## Root Cause

FusionPBX receives the SIP INVITE but **doesn't know how to route it** because:
1. The **To header** in the SIP INVITE might not match FusionPBX's expected format
2. The **dialplan context** might not be configured to handle external SIP calls to extensions
3. The **SIP URI format** might need to specify a context (e.g., `@internal`)

## Solution Options

### Option 1: Use Internal Context (Recommended)

Change the SIP URI to use FusionPBX's internal context:

```python
# Instead of: sip:2001@136.115.41.45;transport=udp
# Use: sip:2001@internal;transport=udp
sip_uri = f"sip:{extension}@internal;transport=udp"
```

**Why this works:**
- FusionPBX uses `internal` context for extension-to-extension calls
- External SIP calls need to be routed through the internal context
- The dialplan in `internal` context knows how to route to extensions

### Option 2: Configure FusionPBX Dialplan

If you want to keep using `sip:2001@136.115.41.45`, you need to configure FusionPBX dialplan:

1. **Go to FusionPBX Admin → Dialplan Manager**
2. **Create or edit a dialplan for external SIP calls:**
   - **Context**: `public` (for external calls)
   - **Destination Number**: `2001` (or use regex `^(\d+)$` for any extension)
   - **Action**: `transfer` or `bridge`
   - **Destination**: `${destination_number}@internal`

### Option 3: Use SIP Trunk with Outbound Routes

Configure FusionPBX to treat Twilio as a SIP trunk:

1. **Go to FusionPBX Admin → Trunks → Add**
2. **Create SIP Trunk for Twilio:**
   - **Trunk Name**: `Twilio`
   - **SIP Profile**: `external`
   - **Register**: `false` (Twilio doesn't register)
   - **Outbound Caller ID**: Your Twilio number
3. **Create Outbound Route:**
   - **Route Name**: `Twilio-to-Extensions`
   - **Dial Patterns**: `^2001$` (or `^(\d+)$` for any extension)
   - **Trunk**: `Twilio`
   - **Gateway**: Your FusionPBX gateway

## Quick Fix (Try This First)

Update the SIP URI in `convonet/routes.py` to use `@internal`:

```python
# In voice_assistant_transfer_bridge() function
sip_uri = f"sip:{extension}@internal;transport=udp"
```

**Note:** You may need to configure FusionPBX to accept SIP calls to `@internal` from Twilio IPs, or create a separate context for external SIP calls.

## Verification Steps

After making changes:

1. **Check FusionPBX Dialplan:**
   ```bash
   fs_cli -x "dialplan show internal"
   # Look for extension 2001 routing
   ```

2. **Test SIP URI Format:**
   ```bash
   # On FusionPBX server
   fs_cli -x "sofia status"
   # Check if extension 2001 is registered
   
   # Test dialplan
   fs_cli -x "dialplan xml internal 2001"
   # Should show XML dialplan for extension 2001
   ```

3. **Check SIP Headers:**
   - Look for `To:` header in FusionPBX logs
   - Should be: `To: <sip:2001@internal>` or `To: <sip:2001@136.115.41.45>`
   - The format must match what FusionPBX expects

## Expected Log Flow (After Fix)

When working correctly, you should see:

```
[NOTICE] New Channel sofia/internal/2001@internal [uuid]
[INFO] receiving invite from 54.172.60.0:5060
[DEBUG] State NEW -> INIT
[DEBUG] State INIT -> RINGING
[NOTICE] Extension 2001 is ringing
[DEBUG] State RINGING -> ANSWERED
[NOTICE] Call answered by extension 2001
```

Instead of:
```
[WARNING] Abandoned
[NOTICE] Hangup [CS_NEW] [WRONG_CALL_STATE]
```

## Recommended Action

**Try Option 1 first** (use `@internal` context). If that doesn't work, check FusionPBX dialplan configuration.

