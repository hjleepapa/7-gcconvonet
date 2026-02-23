# FusionPBX Dialplan Commands - Correct Syntax

## Problem
The `xml_locate dialplan public 2001` command returns "bad args". This means the command syntax is incorrect or the dialplan doesn't exist.

## Alternative Commands to Check Dialplan

### Option 1: Check Dialplan via XML Files Directly

```bash
# Find dialplan XML files
find /etc/freeswitch -name "*.xml" | grep -i dialplan

# Or check FusionPBX dialplan directory
ls -la /etc/freeswitch/dialplan/
ls -la /etc/freeswitch/dialplan/public/

# View public context dialplan
cat /etc/freeswitch/dialplan/public.xml
# Or if FusionPBX uses different structure:
cat /var/www/fusionpbx/app/dialplan/resources/dialplan.php
```

### Option 2: Use FreeSWITCH CLI Commands

```bash
# List all dialplan contexts
fs_cli -x "show dialplan"

# Show dialplan for specific context (if command exists)
fs_cli -x "show dialplan public"

# Try different xml_locate syntax
fs_cli -x "xml_locate dialplan public" 
fs_cli -x "xml_locate dialplan" 
```

### Option 3: Check via FusionPBX Database

FusionPBX stores dialplan in database. Check directly:

```bash
# Connect to PostgreSQL (if FusionPBX uses PostgreSQL)
psql -U fusionpbx -d fusionpbx -c "SELECT * FROM v_dialplans WHERE dialplan_context = 'public' AND dialplan_name LIKE '%2001%';"

# Or check all public dialplans
psql -U fusionpbx -d fusionpbx -c "SELECT dialplan_name, dialplan_context, dialplan_enabled FROM v_dialplans WHERE dialplan_context = 'public';"
```

### Option 4: Check via FusionPBX Web UI (Easiest)

1. **Login:** `https://136.115.41.45`
2. **Navigate:** Advanced → Dialplan Manager
3. **Filter:** Set context to `public`
4. **Look for:** Entry with extension `2001` or condition matching `^2001$`

## Most Likely Issue: Dialplan Doesn't Exist

The "bad args" error suggests the dialplan entry for `2001` in `public` context doesn't exist yet.

## Solution: Create Dialplan via Web UI

Since CLI commands aren't working, use the web UI:

1. **Login to FusionPBX:** `https://136.115.41.45`
2. **Go to:** Advanced → Dialplan Manager
3. **Click:** "+" (Add) button
4. **Fill in:**
   - **Name:** `Twilio-to-Extension-2001`
   - **Context:** `public` ⚠️ **MUST BE public** (matches SIP profile)
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
8. **Reload:** After saving, reload XML:
   ```bash
   fs_cli -x "reloadxml"
   ```

## Verify After Creation

After creating the dialplan:

```bash
# Reload XML
fs_cli -x "reloadxml"

# Check if extension 2001 is registered
fs_cli -x "sofia status" | grep 2001

# Check recent logs for 2001
tail -50 /var/log/freeswitch/freeswitch.log | grep -i 2001
```

## Alternative: Direct XML Edit

If web UI doesn't work, edit XML directly:

```bash
# Find dialplan XML file
find /etc -name "public.xml" 2>/dev/null
find /var/www/fusionpbx -name "*dialplan*" -type f 2>/dev/null

# Or check FusionPBX structure
ls -la /var/www/fusionpbx/app/dialplan/
```

Then manually add the dialplan entry to the XML file and reload.

