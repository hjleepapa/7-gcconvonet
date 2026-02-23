# FusionPBX NO_ANSWER Issue - Solution

## Current Status

✅ **Good News:**
- Dialplan is working correctly!
- Call is being routed to extension 2001
- No more `WRONG_CALL_STATE` errors

❌ **Issue:**
- Call hangs up with `NO_ANSWER` after 60 seconds
- Extension 2001 is not answering

## What the Logs Show

```
New Channel sofia/internal/2001@internal
State: CS_NEW -> CS_INIT -> CS_ROUTING -> CS_CONSUME_MEDIA
[sending invite to 2001@internal]
[waits 60 seconds]
Hangup [CS_CONSUME_MEDIA] [NO_ANSWER]
```

This means:
1. ✅ Call arrived and was routed correctly
2. ✅ Dialplan matched extension 2001
3. ✅ FusionPBX tried to call extension 2001
4. ❌ Extension 2001 didn't answer (not registered or not online)

## Solution: Check Extension 2001 Registration

### Step 1: Check if Extension 2001 is Registered

```bash
# Check if extension 2001 is registered/online
fs_cli -x "sofia status" | grep 2001
```

**Expected output if registered:**
```
Registrations:
  2001@internal    sip:2001@<IP>:<PORT>    <status>
```

**If nothing shows:**
- Extension 2001 is not registered
- You need to register it first

### Step 2: Check All Registered Extensions

```bash
# See all registered extensions
fs_cli -x "sofia status"
```

Look for extension 2001 in the registrations list.

### Step 3: Register Extension 2001

If extension 2001 is not registered, you need to:

1. **Configure extension in FusionPBX:**
   - Login: `https://136.115.41.45`
   - Go to: **Advanced → Extensions**
   - Check if extension 2001 exists
   - If not, create it

2. **Register extension on a device:**
   - Use a SIP client (softphone, mobile app, etc.)
   - Configure with:
     - **Server:** `136.115.41.45` or `pbx.hjlees.com`
     - **Username:** `2001`
     - **Password:** (extension password from FusionPBX)
     - **Domain:** `internal` or `pbx.hjlees.com`

3. **Test registration:**
   ```bash
   fs_cli -x "sofia status" | grep 2001
   ```

## Alternative: Test with Echo Application

To verify the dialplan works without needing a registered extension:

1. **Modify dialplan action temporarily:**
   - Change Action from: `transfer=2001 XML internal`
   - To: `answer`
   - Then: `echo`
   - This will echo back audio (for testing)

2. **Or use a test extension:**
   - Create a test extension that's always registered
   - Or use a voicemail box

## Quick Verification

```bash
# Check registration
fs_cli -x "sofia status" | grep 2001

# If registered, you should see:
# 2001@internal    sip:2001@<IP>:<PORT>    <status>

# If not registered, you'll see nothing
```

## Summary

**The dialplan is working!** ✅

The only issue now is that extension 2001 needs to be:
1. **Created** in FusionPBX (if not exists)
2. **Registered** on a device (SIP client)
3. **Online** when the call comes in

Once extension 2001 is registered and online, the call should connect successfully!

