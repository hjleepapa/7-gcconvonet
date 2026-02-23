# FusionPBX Dialplan Verification Steps

## Current Status

From your output:
- ✅ SIP profile `internal` uses **Context: public** - calls will land in `public` context
- ❓ Dialplan entry for extension 2001 may not exist or is not configured correctly

## Step 1: Check if Dialplan Entry Exists

Run these commands to verify:

```bash
# Check if 2001 exists in public dialplan
fs_cli -x "xml_locate dialplan public 2001"

# If that doesn't work, try:
fs_cli -x "show dialplan public" | grep 2001

# Or check all extensions in public context
fs_cli -x "show dialplan public"
```

**Expected Output:**
- If dialplan exists: Should show XML with `<extension>` and `<condition>` for 2001
- If dialplan doesn't exist: Will show error or no match

## Step 2: Create Dialplan Entry via Web UI

If dialplan doesn't exist, create it:

1. **Login to FusionPBX:** `https://136.115.41.45`
2. **Navigate:** Advanced → Dialplan Manager
3. **Click:** "+" (Add) button
4. **Fill in:**
   - **Name:** `Twilio-to-Extension-2001`
   - **Context:** `public` (IMPORTANT!)
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

## Step 3: Verify Dialplan After Creation

After creating, verify:

```bash
# Check if dialplan was created
fs_cli -x "xml_locate dialplan public 2001"

# Reload XML if needed
fs_cli -x "reloadxml"

# Check again
fs_cli -x "xml_locate dialplan public 2001"
```

## Step 4: Test Dialplan

Test if dialplan works:

```bash
# Test dialplan routing (this will try to call extension 2001)
fs_cli -x "originate sofia/internal/2001@internal &echo"
```

## Common Issues

### Issue 1: Dialplan Not Showing Up

If `xml_locate dialplan public 2001` returns nothing:

1. **Check FusionPBX Web UI:**
   - Go to: Advanced → Dialplan Manager
   - Verify entry exists and is **Enabled**
   - Check **Context** is set to `public`

2. **Reload XML:**
   ```bash
   fs_cli -x "reloadxml"
   ```

3. **Check FusionPBX logs:**
   ```bash
   tail -f /var/log/freeswitch/freeswitch.log | grep -i dialplan
   ```

### Issue 2: Wrong Context

If calls still fail:

1. **Verify SIP profile context:**
   ```bash
   fs_cli -x "sofia status profile internal" | grep -i context
   ```
   Should show: `Context: public`

2. **If context is wrong, fix in Web UI:**
   - Advanced → SIP Profiles → internal
   - Settings → Context → Set to `public`

### Issue 3: Action Format Wrong

If `transfer` doesn't work, try `bridge`:

- **Action 1:** `bridge`
- **Value:** `user/2001@internal`

## Quick Command Reference

```bash
# Check dialplan entry
fs_cli -x "xml_locate dialplan public 2001"

# Reload XML
fs_cli -x "reloadxml"

# Check SIP profile context
fs_cli -x "sofia status profile internal" | grep Context

# Check if extension 2001 is registered
fs_cli -x "sofia status" | grep 2001

# View recent logs
tail -50 /var/log/freeswitch/freeswitch.log | grep -i 2001
```

