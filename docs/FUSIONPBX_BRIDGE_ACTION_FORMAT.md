# FusionPBX Bridge Action Format - Correct Syntax

## Current Issue

The logs still show:
```
sofia/internal/2001@internal
```

This means the dialplan is still using `2001@internal` instead of `2001@pbx.hjlees.com`.

## Possible Causes

1. **XML not reloaded** after dialplan change
2. **Action format incorrect** in FusionPBX UI
3. **Dialplan entry not saved correctly**

## Correct Action Formats

### Option 1: Bridge with user/ format

**In FusionPBX Dialplan Manager:**
- **Action:** `bridge` (type manually)
- **Value:** `user/2001@pbx.hjlees.com`

**Note:** Make sure there's NO `=` sign, just space between action and value.

### Option 2: Bridge with sofia/ format

- **Action:** `bridge`
- **Value:** `sofia/internal/2001@pbx.hjlees.com`

### Option 3: Transfer with domain

- **Action:** `transfer`
- **Value:** `2001@pbx.hjlees.com XML internal`

## Step-by-Step Fix

### Step 1: Verify Current Dialplan

```bash
# Check if dialplan was saved correctly
# (This might not work, but try)
fs_cli -x "show dialplan public" | grep -i 2001
```

### Step 2: Edit Dialplan in FusionPBX

1. **Login:** `https://136.115.41.45`
2. **Go to:** Advanced → Dialplan Manager
3. **Find:** `Twilio-to-Extension-2001`
4. **Click:** Edit
5. **Check Action 1:**
   - Should be: `bridge` (not `bridge=`)
   - Value should be: `user/2001@pbx.hjlees.com` (exactly this)
6. **Save**

### Step 3: Reload XML

```bash
fs_cli -x "reloadxml"
```

### Step 4: Verify Action Format

Make sure in the FusionPBX UI, the action field shows:
- **Action:** `bridge`
- **Value:** `user/2001@pbx.hjlees.com`

**NOT:**
- ❌ `bridge=user/2001@pbx.hjlees.com` (all in one field)
- ❌ `bridge user/2001@pbx.hjlees.com` (if it's two separate fields, use them separately)

## Alternative: Check Dialplan XML Directly

If the UI isn't working, check the XML directly:

```bash
# Find dialplan XML
find /etc/freeswitch -name "*.xml" -path "*/dialplan/*" 2>/dev/null | grep -i public

# Or check FusionPBX dialplan directory
find /var/www/fusionpbx -name "*dialplan*" -type f 2>/dev/null
```

Then manually edit the XML to ensure it has:
```xml
<action application="bridge" data="user/2001@pbx.hjlees.com"/>
```

## Test After Fix

After making the change and reloading:

```bash
# Reload XML
fs_cli -x "reloadxml"

# Make a test call and check logs
tail -f /var/log/freeswitch/freeswitch.log | grep -i 2001
```

You should see it trying to call `2001@pbx.hjlees.com` instead of `2001@internal`.

## Most Likely Issue

The action format in FusionPBX UI might need to be:
- **Two separate fields:** Action = `bridge`, Value = `user/2001@pbx.hjlees.com`
- **NOT one field:** `bridge=user/2001@pbx.hjlees.com`

Check how FusionPBX displays the action - if it's two fields, use them separately.

