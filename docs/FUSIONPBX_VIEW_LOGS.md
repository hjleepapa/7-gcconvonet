# FusionPBX Log Viewing Commands

## Main Log File Location

FusionPBX uses FreeSWITCH, and logs are typically located at:
```bash
/var/log/freeswitch/freeswitch.log
```

## View Logs Commands

### 1. View Recent Logs (Last 100 lines)

```bash
tail -100 /var/log/freeswitch/freeswitch.log
```

### 2. Follow Logs in Real-Time (Like `tail -f`)

```bash
tail -f /var/log/freeswitch/freeswitch.log
```

Press `Ctrl+C` to stop following.

### 3. Search for Extension 2001

```bash
tail -100 /var/log/freeswitch/freeswitch.log | grep -i 2001
```

### 4. Search for Twilio IP Address

```bash
tail -100 /var/log/freeswitch/freeswitch.log | grep -i "54.172.60.2"
```

### 5. Search for Call SID

```bash
tail -100 /var/log/freeswitch/freeswitch.log | grep -i "CAd942e2fef5a66921e14daf4e6ed86320"
```

### 6. Search for "transfer" or "bridge" Actions

```bash
tail -100 /var/log/freeswitch/freeswitch.log | grep -i "transfer\|bridge"
```

### 7. Search for "WRONG_CALL_STATE" Errors

```bash
tail -100 /var/log/freeswitch/freeswitch.log | grep -i "WRONG_CALL_STATE"
```

### 8. Search for Dialplan Matching

```bash
tail -100 /var/log/freeswitch/freeswitch.log | grep -i "destination_number\|dialplan"
```

### 9. View Last 50 Lines with Timestamps

```bash
tail -50 /var/log/freeswitch/freeswitch.log
```

### 10. Search for Recent INVITE Messages

```bash
tail -100 /var/log/freeswitch/freeswitch.log | grep -i "invite\|INVITE"
```

## Alternative Log Locations

If the main log file doesn't exist, check:

```bash
# Alternative locations
/var/log/freeswitch/freeswitch.log.1
/var/log/freeswitch.log
/usr/local/freeswitch/log/freeswitch.log

# Or find it
find /var/log -name "*freeswitch*" -o -name "*free*" 2>/dev/null
```

## View Logs with More Context

### Show Last 200 Lines with Line Numbers

```bash
tail -200 /var/log/freeswitch/freeswitch.log | nl
```

### Search and Show 10 Lines Before/After Match

```bash
tail -200 /var/log/freeswitch/freeswitch.log | grep -i 2001 -A 10 -B 10
```

## Quick Commands for Your Current Issue

### Check if Call Arrived

```bash
tail -100 /var/log/freeswitch/freeswitch.log | grep -i "54.172.60.2\|invite"
```

### Check if Dialplan Matched

```bash
tail -100 /var/log/freeswitch/freeswitch.log | grep -i "2001\|destination_number"
```

### Check for Errors

```bash
tail -100 /var/log/freeswitch/freeswitch.log | grep -i "error\|WRONG_CALL_STATE\|failed"
```

## Real-Time Monitoring

To watch logs in real-time while testing:

```bash
# Terminal 1: Follow logs
tail -f /var/log/freeswitch/freeswitch.log

# Terminal 2: Make a test call
# Then watch Terminal 1 for the call logs
```

## Filter by Time (Recent Calls)

If logs are very large, you can filter by recent time:

```bash
# Last 5 minutes
tail -1000 /var/log/freeswitch/freeswitch.log | grep "$(date '+%Y-%m-%d %H:%M')"

# Or just view last 200 lines (usually covers recent activity)
tail -200 /var/log/freeswitch/freeswitch.log
```

## Most Useful Command for Your Issue

**To see recent call activity for extension 2001:**

```bash
tail -200 /var/log/freeswitch/freeswitch.log | grep -i 2001
```

This will show:
- If calls arrived for extension 2001
- If dialplan matched
- If transfer executed
- Any errors

