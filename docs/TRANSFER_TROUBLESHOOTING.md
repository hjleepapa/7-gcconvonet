# Transfer Troubleshooting Guide

## Current Issue: Transfer Not Working

### Symptoms
- ✅ Twilio calls are being created successfully (201 status)
- ✅ URL is correct: `https://convonet-anthropic.onrender.com/anthropic/convonet_todo/twilio/voice_assistant/transfer_bridge?extension=2001`
- ❌ No logs from `transfer_bridge` endpoint (suggests Twilio can't reach it)
- ❌ Extension 2001 doesn't ring

## Diagnostic Steps

### 1. Test Endpoint Accessibility

After deployment, test the endpoint directly:

```bash
# Test GET request (should return JSON)
curl https://convonet-anthropic.onrender.com/anthropic/convonet_todo/twilio/voice_assistant/transfer_bridge?extension=2001

# Test POST request (simulating Twilio)
curl -X POST https://convonet-anthropic.onrender.com/anthropic/convonet_todo/twilio/voice_assistant/transfer_bridge?extension=2001 \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "CallSid=test123&From=+1234567890"
```

**Expected Response:**
- GET: JSON with status "ok"
- POST: TwiML XML with `<Dial><Sip>` instructions

### 2. Check Twilio Console

1. Go to Twilio Console → Monitor → Logs → Calls
2. Find the call SID (e.g., `CA450cf4bde9f377bb0a319847d63dbb83`)
3. Check the call details:
   - **Status**: Should show "in-progress" or "completed"
   - **To**: Should show `sip:2001@136.115.41.45;transport=udp`
   - **URL**: Should show the transfer_bridge URL
   - **Error**: Check for any error messages

### 3. Check Twilio SIP Logs

1. Go to Twilio Console → Monitor → Logs → SIP
2. Filter by your account
3. Look for:
   - SIP INVITE messages to `sip:2001@136.115.41.45`
   - Any error responses (4xx, 5xx)
   - Authentication failures

### 4. Check Render Logs

After triggering a transfer, check Render logs for:
- `[VoiceAssistantBridge] ===== TRANSFER BRIDGE CALLED =====`
- Any error messages
- Request details (Call SID, extension, etc.)

### 5. Verify FusionPBX Configuration

1. **Check Extension 2001 Status:**
   ```bash
   # On FusionPBX server
   fs_cli -x "sofia status"
   # Look for extension 2001 in the registered users list
   ```

2. **Check FusionPBX Logs:**
   ```bash
   tail -f /var/log/fusionpbx/freeswitch.log
   # Look for SIP INVITE from Twilio IPs
   ```

3. **Verify Twilio IP Whitelisting:**
   - Go to FusionPBX Admin → Access Control → ACL
   - Ensure these IP ranges are whitelisted:
     - `54.172.60.0/23`
     - `54.244.51.0/24`
     - `177.71.206.192/26`
     - `54.252.254.64/26`
     - `54.169.127.128/26`

### 6. Common Issues and Solutions

#### Issue: Endpoint Not Being Called

**Symptoms:**
- No logs from `transfer_bridge` endpoint
- Twilio call created but no TwiML response

**Possible Causes:**
1. **URL Not Accessible**: Twilio can't reach the endpoint
   - **Solution**: Verify the URL is publicly accessible
   - **Test**: Use `curl` to test the endpoint

2. **SSL Certificate Issue**: Twilio requires HTTPS with valid certificate
   - **Solution**: Ensure Render provides valid SSL certificate
   - **Check**: Render automatically provides SSL for `.onrender.com` domains

3. **Timeout**: Endpoint takes too long to respond
   - **Solution**: Check Render logs for slow responses
   - **Default**: Twilio waits 30 seconds for TwiML response

#### Issue: SIP Connection Fails

**Symptoms:**
- Endpoint is called (logs appear)
- But FusionPBX doesn't receive SIP INVITE

**Possible Causes:**
1. **Firewall Blocking**: FusionPBX firewall blocking Twilio IPs
   - **Solution**: Whitelist Twilio IP ranges in FusionPBX ACL

2. **SIP Authentication Required**: FusionPBX requires SIP auth
   - **Solution**: Set `FREEPBX_SIP_USERNAME` and `FREEPBX_SIP_PASSWORD` env vars

3. **Wrong Domain/IP**: `FREEPBX_DOMAIN` is incorrect
   - **Solution**: Verify `FREEPBX_DOMAIN=136.115.41.45` is correct

#### Issue: Extension Doesn't Ring

**Symptoms:**
- SIP INVITE reaches FusionPBX
- But extension 2001 doesn't ring

**Possible Causes:**
1. **Extension Not Registered**: Extension 2001 is not logged in
   - **Solution**: Check FusionPBX → Users → Extension 2001 status
   - **Verify**: Extension is registered and active

2. **Extension Busy**: Extension is already on a call
   - **Solution**: Check extension status in FusionPBX

3. **Call Routing Issue**: FusionPBX routing not configured correctly
   - **Solution**: Check FusionPBX dialplan for extension 2001

## Debugging Commands

### Test Transfer Endpoint Directly

```bash
# Test GET (should work)
curl https://convonet-anthropic.onrender.com/anthropic/convonet_todo/twilio/voice_assistant/transfer_bridge?extension=2001

# Test POST (simulating Twilio)
curl -X POST \
  https://convonet-anthropic.onrender.com/anthropic/convonet_todo/twilio/voice_assistant/transfer_bridge?extension=2001 \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "CallSid=test123&From=+1234567890"
```

### Check Twilio Call Status

```bash
# Using Twilio CLI (if installed)
twilio api:core:calls:fetch CA450cf4bde9f377bb0a319847d63dbb83
```

### Check FusionPBX Extension Status

```bash
# SSH into FusionPBX server
ssh user@136.115.41.45

# Check FreeSWITCH status
fs_cli -x "sofia status"

# Check specific extension
fs_cli -x "user_data 2001@internal var"

# Check recent calls
fs_cli -x "show calls"
```

## Expected Log Flow

When transfer works correctly, you should see:

1. **WebRTC Server:**
   ```
   🔄 Transfer requested: Extension=2001, Department=support, Reason=...
   📞 Initiated agent call via Twilio (Call SID: CA...) to sip:2001@...
   ```

2. **Twilio API:**
   ```
   POST https://api.twilio.com/.../Calls.json
   Response: 201 Created
   ```

3. **Transfer Bridge Endpoint:**
   ```
   [VoiceAssistantBridge] ===== TRANSFER BRIDGE CALLED =====
   [VoiceAssistantBridge] Call SID: CA...
   [VoiceAssistantBridge] Extension: 2001
   [VoiceAssistantBridge] Dialing sip:2001@136.115.41.45;transport=udp
   ```

4. **Transfer Callback:**
   ```
   Transfer callback for call CA...: status=completed, extension=2001
   ✅ Transfer successful
   ```

## Next Steps

1. **After deployment**, test the endpoint with `curl`
2. **Check Twilio Console** for call details and errors
3. **Check Render logs** for `[VoiceAssistantBridge]` messages
4. **Verify FusionPBX** extension 2001 is registered
5. **Check FusionPBX logs** for SIP INVITE messages

## Environment Variables Checklist

Ensure these are set in Render:

```bash
# FusionPBX
FREEPBX_DOMAIN=136.115.41.45
FREEPBX_SIP_USERNAME=  # Optional
FREEPBX_SIP_PASSWORD=  # Optional
TRANSFER_TIMEOUT=30

# Twilio
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_TRANSFER_CALLER_ID=+1234567890  # Optional

# URLs (should use Render URL)
PUBLIC_BASE_URL=https://convonet-anthropic.onrender.com
# OR let it auto-detect from RENDER_EXTERNAL_URL
```

