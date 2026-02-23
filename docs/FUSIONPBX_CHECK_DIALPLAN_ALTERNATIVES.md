# Alternative Ways to Check FusionPBX Dialplan

## Problem
The `xml_locate dialplan public 2001` command returns "bad args", which likely means:
1. The dialplan entry doesn't exist yet, OR
2. The command syntax is different for this FreeSWITCH version

## Solution: Check via Web UI (Easiest)

Since CLI commands aren't working reliably, **use the FusionPBX web UI** to check and create the dialplan:

1. **Login:** `https://136.115.41.45`
2. **Go to:** Advanced → Dialplan Manager
3. **Check Context dropdown:** Make sure you can select `public`
4. **Look for existing entry:** Check if there's already an entry for extension `2001`
5. **If not found:** Create it (see steps below)

## Alternative CLI Methods (If You Want to Try)

### Method 1: Check Database Directly

```bash
# Check if dialplan exists in FusionPBX database
psql -U fusionpbx -d fusionpbx -c "SELECT dialplan_name, dialplan_context, dialplan_enabled FROM v_dialplans WHERE dialplan_context = 'public' AND dialplan_name LIKE '%2001%';"

# Or see all public dialplans
psql -U fusionpbx -d fusionpbx -c "SELECT dialplan_name, dialplan_context, dialplan_enabled FROM v_dialplans WHERE dialplan_context = 'public';"
```

### Method 2: Check XML Files Directly

```bash
# Find dialplan XML files
find /etc/freeswitch -name "*.xml" -path "*/dialplan/*" 2>/dev/null

# Or check FusionPBX dialplan directory
ls -la /etc/freeswitch/dialplan/public/ 2>/dev/null

# Or check if public.xml exists
cat /etc/freeswitch/dialplan/public.xml 2>/dev/null | grep -i 2001
```

### Method 3: Use Different FreeSWITCH Commands

```bash
# Try different command syntax
fs_cli -x "show dialplan public"

# Or try to test dialplan matching
fs_cli -x "originate sofia/internal/2001@internal &echo"
```

## Most Important: Create the Dialplan Entry

Since the CLI check isn't working, **just create the dialplan entry via web UI**. The "bad args" error strongly suggests the dialplan doesn't exist yet.

### Step-by-Step: Create Dialplan Entry

1. **Login to FusionPBX:** `https://136.115.41.45`
2. **Navigate:** Advanced → **Dialplan Manager**
3. **Click:** "+" (Add) button
4. **Fill in:**
   - **Name:** `Twilio-to-Extension-2001`
   - **Context:** Select `public` from dropdown ⚠️ **This is the dialplan context**
   - **Enabled:** `True`
   - **Continue:** Click "Continue"
5. **Add Condition:**
   - **Condition 1:** `destination_number`
   - **Expression:** `^2001$`
   - Click blue arrow (←) to add
6. **Add Action:**
   - **Action 1:** Type `transfer` (manually, not from dropdown)
   - **Value:** `2001 XML internal`
   - Click blue arrow (←) to add
7. **Save:** Click "Save" button
8. **Reload XML:**
   ```bash
   fs_cli -x "reloadxml"
   ```

## Verify After Creation

After creating the dialplan:

```bash
# Reload XML
fs_cli -x "reloadxml"

# Check recent logs
tail -50 /var/log/freeswitch/freeswitch.log | grep -i 2001

# Test a call transfer from Twilio
```

## Why "bad args" Error?

The "bad args" error typically means:
- The dialplan entry doesn't exist (most likely)
- The command syntax is wrong for this FreeSWITCH version
- The context name is incorrect

Since we know:
- SIP profile `internal` routes to context `public` (from earlier check)
- The dialplan entry for `2001` in `public` context likely doesn't exist

**Solution:** Create it via web UI, then test the transfer again.

