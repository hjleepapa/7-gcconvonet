# FusionPBX Domain Mismatch Issue

## Problem Identified

**Extension Registration:**
- Registered as: `2001@pbx.hjlees.com`
- Profile: `internal`
- Status: `Registered WSS-NAT` (WebSocket Secure)

**Call Routing:**
- Dialplan tries to call: `2001@internal`
- But extension is registered as: `2001@pbx.hjlees.com`

**Domain Mismatch!**

## The Issue

The extension is registered with domain `pbx.hjlees.com`, but the dialplan action `transfer=2001 XML internal` is trying to call `2001@internal` (without domain).

## Solutions

### Solution 1: Fix Dialplan Action (Recommended)

Change the dialplan action to include the domain:

**Current Action:**
- Action: `transfer`
- Value: `2001 XML internal`

**Change To:**
- Action: `transfer`
- Value: `2001@pbx.hjlees.com XML internal`

Or try:
- Action: `bridge`
- Value: `user/2001@pbx.hjlees.com`

### Solution 2: Check Registration Format

The extension might need to be registered differently, or we need to use the correct format in dialplan.

### Solution 3: Use Bridge Instead of Transfer

Try using `bridge` action with full user format:

**Action:**
- Action: `bridge`
- Value: `user/2001@pbx.hjlees.com`

## Check Current Registration

```bash
# Check all registrations (not just grep)
fs_cli -x "sofia status"

# Or check specific profile
fs_cli -x "sofia status profile internal"

# Or check registrations differently
fs_cli -x "sofia_contact 2001@pbx.hjlees.com"
```

## Verify Domain Configuration

The extension is registered as `2001@pbx.hjlees.com`, so the dialplan needs to match this format.

## Quick Fix Steps

1. **Edit Dialplan:**
   - Go to: Advanced → Dialplan Manager
   - Find: `Twilio-to-Extension-2001`
   - Edit Action 1:
     - Change from: `transfer=2001 XML internal`
     - Change to: `bridge=user/2001@pbx.hjlees.com`
   - Save

2. **Reload XML:**
   ```bash
   fs_cli -x "reloadxml"
   ```

3. **Test again**

## Alternative: Check What Format Works

Try these different action formats:

**Option A:**
- Action: `bridge`
- Value: `user/2001@pbx.hjlees.com`

**Option B:**
- Action: `transfer`
- Value: `2001@pbx.hjlees.com XML internal`

**Option C:**
- Action: `bridge`
- Value: `sofia/internal/2001@pbx.hjlees.com`

## Why This Happens

FusionPBX can register extensions with:
- Domain name: `2001@pbx.hjlees.com`
- Or just extension: `2001@internal`

The dialplan action needs to match the actual registration format.

