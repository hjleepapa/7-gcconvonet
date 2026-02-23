# FusionPBX Log Analysis Guide

## Current Log Status

### ✅ Good Signs:
- `IP [12.94.132.170] passed ACL check [Twilio-SIP]` - Twilio IPs are being allowed
- Internal profile is working (no errors for internal profile)

### ⚠️ External Profile Error (Not Critical):
```
Error Creating SIP UA for profile: external
```
**This is OK to ignore** if:
- Internal profile is working
- Calls are coming through
- You're only using the internal profile for Twilio

## What to Look For in Transfer Logs

When a transfer happens, you should see:

### 1. Incoming Call from Twilio:
```
receiving invite from 54.172.60.2:5060
sofia/internal/+12344007818@sip.twilio.com
```

### 2. Dialplan Matching:
```
destination_number = 2001
```

### 3. Bridge/Transfer Action:
```
bridge user/2001@pbx.hjlees.com
```
or
```
transfer 2001@pbx.hjlees.com XML internal
```

### 4. Outgoing Call to Extension:
```
sofia/internal/2001@pbx.hjlees.com
sending invite to 2001@pbx.hjlees.com
```

### 5. Call Result:
- ✅ `200 OK` - Call connected
- ❌ `NO_ANSWER` - Extension didn't answer
- ❌ `USER_NOT_FOUND` - Extension not registered
- ❌ `WRONG_CALL_STATE` - Routing issue

## Commands to Check Recent Transfer Attempts

### Check for Recent Calls:
```bash
# Check last 100 lines for any 2001 activity
tail -100 /var/log/freeswitch/freeswitch.log | grep -i 2001

# Check for Twilio calls
tail -100 /var/log/freeswitch/freeswitch.log | grep -i "54.172.60.2\|twilio"

# Check for bridge/transfer actions
tail -100 /var/log/freeswitch/freeswitch.log | grep -i "bridge\|transfer"

# Check for dialplan matching
tail -100 /var/log/freeswitch/freeswitch.log | grep -i "destination_number"
```

### Real-Time Monitoring:
```bash
# Watch for 2001 calls in real-time
tail -f /var/log/freeswitch/freeswitch.log | grep -i "2001\|twilio\|bridge\|transfer"
```

## If No Calls Appear in Logs

If you don't see any call attempts:

1. **Check if Twilio is calling:**
   - Check your application logs for transfer initiation
   - Verify Twilio call status in Twilio console

2. **Check FusionPBX ACL:**
   ```bash
   # Verify Twilio IPs are whitelisted
   fs_cli -x "acl show"
   ```

3. **Check SIP Profile Status:**
   ```bash
   fs_cli -x "sofia status profile internal"
   ```

4. **Test Dialplan:**
   ```bash
   # Reload XML
   fs_cli -x "reloadxml"
   ```

## Expected Log Flow for Successful Transfer

```
1. [INFO] receiving invite from 54.172.60.2:5060
2. [DEBUG] verifying acl "providers" for ip/port 54.172.60.2:0
3. [NOTICE] New Channel sofia/internal/+12344007818@sip.twilio.com
4. [DEBUG] destination_number = 2001
5. [DEBUG] bridge user/2001@pbx.hjlees.com
6. [NOTICE] New Channel sofia/internal/2001@pbx.hjlees.com
7. [INFO] sending invite to 2001@pbx.hjlees.com
8. [INFO] 200 OK (if extension answers)
```

## Troubleshooting

### If External Profile Error Bothers You:

You can disable the external profile if not needed:
1. Login to FusionPBX: `https://136.115.41.45`
2. Go to: Advanced → SIP Profiles → external
3. Set **Enabled** to `False`
4. Save

Or fix the binding issue:
- Check if port 5060 is already in use
- Verify the IP address `10.128.0.8` is correct
- Check firewall rules

### If Calls Still Show NO_ANSWER:

1. **Verify extension is registered:**
   - Check FusionPBX → Registrations
   - Should show `2001@pbx.hjlees.com` as registered

2. **Check dialplan action format:**
   - Should be: `bridge user/2001@pbx.hjlees.com`
   - NOT: `bridge user/2001@internal`

3. **Test extension manually:**
   ```bash
   fs_cli -x "originate sofia/internal/2001@pbx.hjlees.com &echo"
   ```

## Summary

The external profile error is **not blocking transfers**. Focus on:
- ✅ Internal profile working (it is)
- ✅ ACL allowing Twilio (it is)
- ✅ Dialplan configured correctly
- ✅ Extension 2001 registered
- ✅ Dialplan action uses correct domain (`pbx.hjlees.com`)











