# FusionPBX Dialplan Debugging Guide

## Current Issue

From the logs:
- ✅ Twilio sends SIP INVITE successfully
- ✅ FusionPBX receives it: `receiving invite from 54.172.60.2:5060`
- ✅ ACL check passes: `verifying acl "providers"`
- ❌ Call abandoned: `Hangup [CS_NEW] [WRONG_CALL_STATE]`
- ❌ Dialplan command failed: `dialplan xml public 2001 Command not found!`

## Key Observations

1. **SIP Profile:** The call comes through `sofia/internal/+12344007818@sip.twilio.com`
   - This suggests it's using the `internal` SIP profile
   - But we configured dialplan in `public` context

2. **Dialplan Command:** The command syntax might be wrong
   - Try: `fs_cli -x "xml_locate dialplan public 2001"`
   - Or: `fs_cli -x "show dialplan public"`
   - Or: `fs_cli` (interactive mode), then `xml_locate dialplan public 2001`

## Correct fs_cli Commands

### Check Dialplan Configuration

```bash
# CORRECT: From command line (one-liner)
fs_cli -x "xml_locate dialplan public 2001"

# CORRECT: Inside fs_cli (interactive mode)
fs_cli
# Then type (NO quotes, NO -x):
xml_locate dialplan public 2001

# Check if dialplan entry exists (shows all extensions in public context)
fs_cli -x "show dialplan public" | grep -i 2001

# Or check dialplan XML directly
fs_cli -x "xml_locate dialplan public 2001"
```

### Check What Context the Call Lands In

```bash
# Check SIP profile settings
fs_cli -x "sofia status profile internal"

# Check dialplan contexts
fs_cli -x "show dialplan"
```

### Test Dialplan Matching

```bash
# Test if dialplan matches
fs_cli -x "regex 2001 ^2001$"
```

## Possible Issues

### Issue 1: Dialplan Not Created or Not Enabled

**Check:**
1. Login to FusionPBX web UI
2. Go to: **Advanced → Dialplan Manager**
3. Verify your dialplan entry exists
4. Check that **Enabled** is set to `True`
5. Check that **Context** is set to `public`

### Issue 2: Wrong Context

The call might be landing in a different context. Check:

```bash
# See what contexts exist
fs_cli -x "show dialplan"

# Check internal context dialplan
fs_cli -x "xml_locate dialplan internal 2001"
```

### Issue 3: SIP Profile Routing

The SIP profile might be routing to `internal` context instead of `public`. Check:

1. **FusionPBX Web UI:**
   - Go to: **Advanced → SIP Profiles → internal**
   - Check **Settings** for `context` or `dialplan-context`
   - Should be set to `public` for external calls

2. **Or check via CLI:**
   ```bash
   fs_cli -x "sofia status profile internal"
   ```

### Issue 4: Dialplan Action Format

The action format might be wrong. Try these alternatives:

**Option A: Use `bridge` instead of `transfer`:**
- **Action 1:** `bridge`
- **Value:** `user/2001@internal`

**Option B: Use `set` + `transfer`:**
- **Action 1:** `set`
- **Value:** `transfer_after_bridge=true`
- **Action 2:** `transfer`
- **Value:** `2001 XML internal`

**Option C: Use `set` + `bridge`:**
- **Action 1:** `set`
- **Value:** `hangup_after_bridge=true`
- **Action 2:** `bridge`
- **Value:** `user/2001@internal`

## Step-by-Step Debugging

### Step 1: Verify Dialplan Exists

```bash
# Check if dialplan entry exists
fs_cli -x "show dialplan public"
```

### Step 2: Check Dialplan XML

```bash
# Get dialplan XML for extension 2001
fs_cli -x "xml_locate dialplan public 2001"
```

Should show XML with your dialplan entry.

### Step 3: Check SIP Profile Context

```bash
# Check what context the SIP profile uses
fs_cli -x "sofia status profile internal"
# Look for "context" or "dialplan-context" setting
```

### Step 4: Test Dialplan Manually

```bash
# Test dialplan routing
fs_cli -x "originate sofia/internal/2001@internal &echo"
```

### Step 5: Check Extension Registration

```bash
# Check if extension 2001 is registered
fs_cli -x "sofia status"
# Look for 2001@internal in registered users
```

## Recommended Fix

Based on the logs showing `sofia/internal`, try creating the dialplan in **BOTH** contexts:

1. **Create dialplan in `public` context** (for external calls)
2. **Also create dialplan in `internal` context** (as backup)

Or, configure the SIP profile to use `public` context for external calls.

## Alternative: Direct XML Edit

If the GUI doesn't work, edit XML directly:

1. SSH to FusionPBX server
2. Find dialplan directory:
   ```bash
   find /etc -name "public.xml" -o -name "*dialplan*" | grep -i public
   ```
3. Edit the file and add:
   ```xml
   <extension name="Twilio-to-Extensions">
     <condition field="destination_number" expression="^2001$">
       <action application="transfer" data="2001 XML internal"/>
     </condition>
   </extension>
   ```
4. Reload: `fs_cli -x "reloadxml"`

