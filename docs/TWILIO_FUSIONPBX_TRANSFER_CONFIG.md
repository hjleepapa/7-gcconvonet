# Twilio Configuration for Transferring WebRTC Voice Assistant Calls to FusionPBX

This guide explains how to configure Twilio to transfer calls from the Anthropic WebRTC Voice Assistant (`https://convonet-anthropic.onrender.com/anthropic/webrtc/voice-assistant`) to FusionPBX extension 2001.

## Overview

The transfer flow works as follows:
1. User interacts with WebRTC Voice Assistant (browser-based)
2. User requests transfer (e.g., "transfer me" or "speak to agent")
3. Agent detects transfer intent and triggers transfer
4. Twilio receives TwiML redirect to transfer endpoint
5. Twilio dials FusionPBX extension 2001 via SIP
6. Call is connected to the agent

## Required Twilio Configuration

### 1. Twilio Account Setup

Ensure you have:
- ✅ Twilio Account SID
- ✅ Twilio Auth Token
- ✅ Twilio Phone Number (for caller ID)

### 2. Twilio SIP Configuration

Twilio supports SIP dialing out of the box. No special SIP trunk configuration is needed in Twilio Console. The SIP dialing happens programmatically via TwiML.

### 3. Environment Variables (Render.com)

Set these environment variables in your Render.com service:

```bash
# FusionPBX Configuration
FREEPBX_DOMAIN=your-fusionpbx-ip-or-domain.com  # e.g., 136.115.41.45
FREEPBX_SIP_USERNAME=your_sip_username          # Optional: if FusionPBX requires SIP auth
FREEPBX_SIP_PASSWORD=your_sip_password          # Optional: if FusionPBX requires SIP auth

# Transfer Settings
TRANSFER_TIMEOUT=30                              # Seconds to wait for agent to answer

# Twilio Configuration (if not already set)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890                 # Your Twilio number for caller ID
TWILIO_TRANSFER_CALLER_ID=+1234567890           # Optional: specific caller ID for transfers

# Base URL (for webhooks) - IMPORTANT: Use Render service URL, not custom domain
# Option 1: Use Render's automatic RENDER_EXTERNAL_URL (recommended)
# Render automatically sets RENDER_EXTERNAL_URL to your service URL
# No need to set this manually if using Render's default

# Option 2: Explicitly set the Render service URL
PUBLIC_BASE_URL=https://convonet-anthropic.onrender.com
# OR
VOICE_ASSISTANT_TRANSFER_BASE_URL=https://convonet-anthropic.onrender.com

# ⚠️ DO NOT use custom domain (hjlees.com) here - use the Render service URL
# Custom domains may have routing issues with Twilio webhooks
```

## FusionPBX Configuration

### 1. SIP Trunk Setup

FusionPBX needs to accept SIP calls from Twilio. You have two options:

#### Option A: IP-Based Authentication (Recommended for Simplicity)

1. **Whitelist Twilio IP Ranges in FusionPBX:**
   - Go to FusionPBX Admin → Access Control → ACL
   - Add the following Twilio IP ranges:
     ```
     54.172.60.0/23
     54.244.51.0/24
     177.71.206.192/26
     54.252.254.64/26
     54.169.127.128/26
     ```
   - Set these as "Allow" for SIP traffic

2. **Configure SIP Profile:**
   - Go to Admin → SIP Profiles
   - Edit your SIP profile (usually "internal" or "external")
   - Ensure "Accept Blind Transfer" is enabled
   - Ensure "Accept Replaces" is enabled

#### Option B: SIP Authentication (More Secure)

1. **Create SIP User in FusionPBX:**
   - Go to Admin → Users → Add
   - Create a user specifically for Twilio
   - Set username and password
   - Assign appropriate permissions

2. **Set Environment Variables:**
   ```bash
   FREEPBX_SIP_USERNAME=twilio_user
   FREEPBX_SIP_PASSWORD=secure_password
   ```

### 2. Extension 2001 Configuration

Ensure extension 2001 is:
- ✅ Active and registered
- ✅ Can receive incoming calls
- ✅ Has a registered SIP device (softphone or desk phone)

### 3. Firewall Configuration

Ensure your FusionPBX server allows:
- ✅ UDP port 5060 (SIP) from Twilio IP ranges
- ✅ RTP ports (typically 10000-20000) for audio

## How Transfer Works

### Method 1: Direct Transfer (Current Implementation)

When the agent detects transfer intent, it redirects to:
```
POST /anthropic/convonet_todo/twilio/transfer?extension=2001
```

This endpoint:
1. Generates TwiML with `<Dial>` verb
2. Uses `<Sip>` to dial `sip:2001@your-fusionpbx-domain;transport=udp`
3. Waits for agent to answer (`answer_on_bridge=True`)
4. Connects the call

### Method 2: Conference Bridge Transfer (Alternative)

For more complex scenarios, the code also supports conference bridge transfers via:
```
/anthropic/convonet_todo/twilio/voice_assistant/transfer_bridge?extension=2001
```

This creates a conference room and bridges both parties.

## Testing the Transfer

### 1. Test SIP Connectivity

From your server, test if FusionPBX accepts SIP from Twilio IPs:
```bash
# Test SIP connection (requires sip-tester or similar tool)
sip-tester -s your-fusionpbx-ip -u 2001
```

### 2. Test Transfer Endpoint

Test the transfer endpoint directly:
```bash
curl -X POST https://convonet-anthropic.onrender.com/anthropic/convonet_todo/twilio/transfer?extension=2001 \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "CallSid=test123&From=+1234567890"
```

You should receive TwiML XML with `<Dial><Sip>` instructions.

### 3. Test from Voice Assistant

1. Open `https://convonet-anthropic.onrender.com/anthropic/webrtc/voice-assistant`
2. Authenticate with PIN
3. Say: "Transfer me" or "I need to speak to an agent"
4. The call should transfer to extension 2001

## Troubleshooting

### Transfer Fails with "No Answer"

**Possible Causes:**
- Extension 2001 is not registered
- FusionPBX firewall blocking Twilio IPs
- SIP authentication required but not configured

**Solutions:**
1. Check FusionPBX logs: `tail -f /var/log/fusionpbx/freeswitch.log`
2. Verify extension 2001 is registered: `fs_cli -x "sofia status"`
3. Check Twilio call logs in Twilio Console for error details

### Transfer Fails with "Busy"

**Possible Causes:**
- Extension 2001 is already on a call
- Extension 2001 has "Do Not Disturb" enabled

**Solutions:**
1. Check extension status in FusionPBX
2. Test with a different extension

### Transfer Fails with "Invalid Request"

**Possible Causes:**
- SIP URI format incorrect
- FusionPBX domain not reachable from Twilio

**Solutions:**
1. Verify `FREEPBX_DOMAIN` is correct (IP or FQDN)
2. Test DNS resolution: `nslookup your-fusionpbx-domain`
3. Check Twilio SIP logs in Twilio Console

### No Audio After Transfer

**Possible Causes:**
- RTP ports blocked by firewall
- Codec mismatch

**Solutions:**
1. Open RTP port range (10000-20000) in firewall
2. Configure FusionPBX to use compatible codecs (PCMU, PCMA, G.722)

## Twilio Console Configuration

### 1. Verify Phone Number

1. Go to Twilio Console → Phone Numbers → Manage → Active Numbers
2. Select your Twilio number
3. Ensure "Voice" is enabled
4. Set webhook URL (if using Twilio Voice API, not needed for WebRTC)

### 2. Monitor Calls

1. Go to Twilio Console → Monitor → Logs → Calls
2. Filter by your phone number
3. Check call details for transfer attempts
4. Review SIP traces for connection issues

### 3. SIP Debugging

1. Go to Twilio Console → Monitor → Logs → SIP
2. Filter by your account
3. Review SIP INVITE, 200 OK, and BYE messages
4. Check for authentication failures or connection errors

## Code Flow

The transfer is triggered in two ways:

### 1. Agent-Initiated Transfer

When the AI agent detects transfer intent:
```python
# In convonet/routes.py
if transfer_marker:
    target_extension = "2001"  # or from transfer_marker
    response.redirect(f'{webhook_base_url}/anthropic/convonet_todo/twilio/transfer?extension={target_extension}')
```

### 2. Direct User Request

When user explicitly says "transfer me":
```python
# In convonet/routes.py - verify_pin_webhook
if transfer_requested:
    response.redirect(f'{webhook_base_url}/anthropic/convonet_todo/twilio/transfer?extension=2001')
```

## Security Considerations

1. **SIP Authentication**: Use SIP username/password for production
2. **IP Whitelisting**: Restrict FusionPBX to only accept SIP from Twilio IPs
3. **HTTPS**: Ensure all webhook URLs use HTTPS
4. **Rate Limiting**: Implement rate limiting on transfer endpoints

## Additional Resources

- [Twilio SIP Dial Documentation](https://www.twilio.com/docs/voice/twiml/dial#sip)
- [FusionPBX SIP Configuration](https://docs.fusionpbx.com/en/latest/configuration/sip_profiles.html)
- [Twilio IP Ranges](https://www.twilio.com/docs/voice/ip-address-whitelisting)

## Support

If transfer still fails after following this guide:
1. Check Render.com logs for transfer endpoint errors
2. Check Twilio Console → Monitor → Logs for SIP errors
3. Check FusionPBX logs: `/var/log/fusionpbx/freeswitch.log`
4. Review the code in `convonet/routes.py` lines 242-311 for transfer logic

