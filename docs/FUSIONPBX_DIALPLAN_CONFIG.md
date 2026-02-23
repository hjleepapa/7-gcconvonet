# FusionPBX Dialplan Configuration for Twilio Transfers

## Problem

Twilio sends SIP INVITE to `sip:2001@136.115.41.45`, but FusionPBX abandons the call with `WRONG_CALL_STATE` because the dialplan doesn't know how to route external SIP calls to extensions.

## Solution: Configure FusionPBX Dialplan

FusionPBX needs a dialplan entry to route external SIP calls (from Twilio) to internal extensions.

### Step 1: Access FusionPBX Dialplan Manager

1. Login to FusionPBX: `https://136.115.41.45`
2. Navigate to: **Advanced → Dialplan Manager**

### Step 2: Create Dialplan Entry for External SIP Calls

1. Click **"Add"** to create a new dialplan entry
2. Configure the form fields as follows:

   **Name:**
   - Enter: `Twilio-to-Extensions` (or any descriptive name)

   **Context:**
   - **IMPORTANT**: Change from `10.128.0.10` to: `public`
   - This is the context for external calls (like from Twilio)

   **Condition 1:**
   - Field: `destination_number`
   - Operator: `=` (equals)
   - Value: `2001`
   - Click the blue arrow button to add the condition
   - *Note: For all extensions, use regex: `destination_number` = `^(\d+)$`*

   **Action 1:**
   - Field: `transfer`
   - Value: `2001@internal`
   - Click the blue arrow button to add the action
   - *Note: For dynamic routing, use: `${destination_number}@internal`*

   **Order:**
   - Set to: `100` (or lower number for higher priority)
   - Lower numbers are processed first

   **Enabled:**
   - Keep as: `True`

   **Description:**
   - Enter: `Route Twilio SIP calls to extension 2001` (optional but helpful)

3. Click **"SAVE"** to save the dialplan entry

**For Multiple Extensions (Optional):**

If you want to route any extension number, create a second condition:
- **Condition 1**: `destination_number` = `^(\d+)$` (regex to match any digits)
- **Action 1**: `transfer` = `${destination_number}@internal` (dynamic routing)

### Step 3: Verify Dialplan

Test the dialplan:

```bash
# On FusionPBX server
fs_cli -x "dialplan xml public 2001"
```

Should return XML showing the dialplan routing to `2001@internal`.

### Step 4: Test with fs_cli

```bash
# Test dialplan routing
fs_cli -x "originate sofia/internal/2001@internal &echo"
```

## Alternative: Use SIP Trunk with Outbound Routes

If dialplan doesn't work, configure Twilio as a SIP trunk:

1. **Go to**: Advanced → Trunks → Add
2. **Trunk Type**: SIP
3. **Trunk Name**: `Twilio`
4. **SIP Profile**: `external`
5. **Register**: `false`
6. **Gateway**: Configure with Twilio IP ranges

Then create outbound route:
1. **Go to**: Advanced → Outbound Routes → Add
2. **Route Name**: `Twilio-to-Extensions`
3. **Dial Patterns**: `^2001$` (or `^(\d+)$`)
4. **Trunk**: Select `Twilio` trunk
5. **Gateway**: Your FusionPBX gateway

## Verification

After configuration, test the transfer:

1. Trigger transfer from WebRTC voice assistant
2. Check FusionPBX logs:
   ```bash
   tail -f /var/log/freeswitch/freeswitch.log | grep 2001
   ```
3. Should see:
   - SIP INVITE received
   - Call routed to `2001@internal`
   - Extension 2001 rings
   - Call answered

## Expected Log Flow (After Fix)

```
[INFO] receiving invite from 54.172.60.0:5060
[DEBUG] State NEW -> INIT
[DEBUG] Dialplan: public -> 2001@internal
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

## Troubleshooting

### Issue: Dialplan Not Matching

**Check dialplan:**
```bash
fs_cli -x "dialplan show public"
# Look for your dialplan entry
```

**Test pattern matching:**
```bash
fs_cli -x "regex ^2001$ ^(\d+)$"
# Should return: true
```

### Issue: Extension Not Found

**Check extension exists:**
```bash
fs_cli -x "user_data 2001@internal var"
# Should return extension data
```

**Check extension is registered:**
```bash
fs_cli -x "sofia status"
# Look for 2001@internal in registered users
```

### Issue: Context Routing Fails

**Check internal context dialplan:**
```bash
fs_cli -x "dialplan xml internal 2001"
# Should show routing to extension 2001
```

## Quick Reference

**SIP URI Format:**
- ✅ Correct: `sip:2001@136.115.41.45;transport=udp` (for Twilio)
- ❌ Wrong: `sip:2001@internal;transport=udp` (Twilio can't resolve `internal`)

**FusionPBX Routing:**
- External calls come in via `public` context
- Dialplan must transfer to `2001@internal` context
- Internal context routes to registered extension

