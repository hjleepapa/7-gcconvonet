# FusionPBX Transfer Verification Steps

## Current Status from Logs

✅ **Twilio call created successfully:**
- Call SID: `CAd942e2fef5a66921e14daf4e6ed86320`
- Status: `queued`
- To: `sip:2001@136.115.41.45;transport=udp`
- URL: `https://convonet-anthropic.onrender.com/anthropic/convonet_todo/twilio/voice_assistant/transfer_bridge?extension=2001`

## What to Check Next

### Step 1: Check if transfer_bridge Endpoint Was Called

Look for logs showing the POST request to `transfer_bridge`:

```bash
# In your application logs, look for:
[VoiceAssistantBridge] ===== TRANSFER BRIDGE CALLED =====
```

If you don't see this, Twilio hasn't called the endpoint yet (call might still be ringing).

### Step 2: Check FusionPBX Logs

On FusionPBX server, check if the call arrived:

```bash
# Check recent logs for the call
tail -100 /var/log/freeswitch/freeswitch.log | grep -i 2001

# Or check for Twilio IP (54.172.60.2)
tail -100 /var/log/freeswitch/freeswitch.log | grep -i "54.172.60.2"

# Or check for the Call SID
tail -100 /var/log/freeswitch/freeswitch.log | grep -i "CAd942e2fef5a66921e14daf4e6ed86320"
```

**What to look for:**
- ✅ `receiving invite from 54.172.60.2` - Call arrived
- ✅ `destination_number = 2001` - Dialplan matched
- ✅ `transfer` or `bridge` action executed
- ❌ `WRONG_CALL_STATE` - Still an issue
- ❌ `Unresolvable destination` - Extension not found

### Step 3: Check if Extension 2001 is Registered

```bash
# Check if extension 2001 is registered
fs_cli -x "sofia status" | grep 2001

# Or check all registered users
fs_cli -x "sofia status"
```

**If extension 2001 is not registered:**
- The call will fail
- Extension needs to be registered/online to receive calls

### Step 4: Check Twilio Call Status

Check the Twilio console or use API to see call status:

```bash
# If you have twilio CLI or can check via API
# Call SID: CAd942e2fef5a66921e14daf4e6ed86320
```

**Possible statuses:**
- `queued` - Call is queued (waiting)
- `ringing` - Call is ringing
- `in-progress` - Call connected
- `completed` - Call finished
- `failed` - Call failed
- `busy` - Extension busy
- `no-answer` - Extension didn't answer

## Expected Flow

1. ✅ **Twilio creates call** → `queued` status
2. ⏳ **Twilio calls transfer_bridge** → Should see POST request logs
3. ⏳ **TwiML returned** → Twilio dials SIP URI
4. ⏳ **FusionPBX receives INVITE** → Should see in FusionPBX logs
5. ⏳ **Dialplan matches** → Should see `destination_number = 2001`
6. ⏳ **Transfer executes** → Should see `transfer` or `bridge` action
7. ⏳ **Extension 2001 rings** → If registered
8. ⏳ **Call connects** → If extension answers

## Troubleshooting

### If transfer_bridge Not Called

The call might still be in `queued` status. Wait a few seconds and check:
- Twilio call logs
- Application logs for POST request

### If FusionPBX Doesn't Receive Call

Check:
1. **Firewall:** Is port 5060 (UDP) open?
2. **ACL:** Is Twilio IP whitelisted in FusionPBX?
3. **SIP Profile:** Is `internal` profile enabled and listening?

### If Dialplan Doesn't Match

Check:
1. **Dialplan exists:** Verify in Dialplan Manager
2. **Context correct:** Should be `public`
3. **Condition correct:** `destination_number = ^2001$`
4. **Enabled:** Must be `True`
5. **XML reloaded:** `fs_cli -x "reloadxml"`

### If Extension Not Found

Check:
1. **Extension registered:** `fs_cli -x "sofia status" | grep 2001`
2. **Extension exists:** Check in FusionPBX → Extensions
3. **Context correct:** Extension should be in `internal` context

## Quick Test Commands

```bash
# Check if dialplan exists
fs_cli -x "show dialplan public" | grep -i 2001

# Check if extension is registered
fs_cli -x "sofia status" | grep 2001

# Check recent call attempts
tail -50 /var/log/freeswitch/freeswitch.log | grep -i 2001

# Reload XML (if you made changes)
fs_cli -x "reloadxml"
```

## Next Steps

1. **Check FusionPBX logs** for the call attempt
2. **Check if extension 2001 is registered**
3. **Verify dialplan is enabled and correct**
4. **Check Twilio call status** in Twilio console

Share the FusionPBX logs and we can see what's happening!

