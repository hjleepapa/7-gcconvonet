# FusionPBX: Create "public" Context or Use Alternative

## Problem
The "public" context doesn't exist in the Dialplan Manager dropdown. We need to either:
1. Create the "public" context, OR
2. Use an existing context and configure SIP profile to use it

## Solution 1: Create "public" Context (Recommended)

### Step 1: Create the Context

1. **Login to FusionPBX:** `https://136.115.41.45`
2. **Navigate:** Advanced → **Dialplan Manager**
3. **Look for:** "Contexts" or "Add Context" button (usually at top or in menu)
4. **If not visible, try:**
   - Advanced → Dialplan → Contexts
   - Or check if there's a "Contexts" tab/section
5. **Create new context:**
   - **Name:** `public`
   - **Description:** `Public context for external calls`
   - **Save**

### Step 2: Verify SIP Profile Uses "public"

After creating the context, verify the SIP profile uses it:

```bash
# From command line
fs_cli -x "sofia status profile internal" | grep -i context
```

Should show: `Context: public`

If it doesn't, you may need to:
1. Edit SIP profile settings
2. Set the context to `public`

### Step 3: Create Dialplan Entry

Now create the dialplan entry:
1. **Dialplan Manager** → "+" (Add)
2. **Context:** Select `public` (should now appear in dropdown)
3. **Name:** `Twilio-to-Extension-2001`
4. **Enabled:** `True`
5. **Continue** → Add condition and action as before

## Solution 2: Use Existing Context (Alternative)

If you can't create "public" context, use an existing one:

### Option A: Use "internal" Context

1. **Check what context SIP profile uses:**
   ```bash
   fs_cli -x "sofia status profile internal" | grep -i context
   ```

2. **If it shows a different context** (like `internal` or a domain name):
   - Create dialplan in that context instead
   - Or change SIP profile to use that context

3. **Create dialplan entry:**
   - **Context:** Use the context shown in SIP profile status
   - **Condition:** `destination_number` = `^2001$`
   - **Action:** `transfer` = `2001 XML internal`

### Option B: Use Domain-Based Context

From your dropdown, I see domain names like:
- `pbx.hjlees.com`
- `136.115.41.45`

You might need to:
1. Check which context the SIP profile actually uses
2. Create dialplan in that context

## Solution 3: Check Current SIP Profile Context

First, let's verify what context the SIP profile is actually using:

```bash
# From command line
fs_cli -x "sofia status profile internal"
```

Look for the `Context:` line. It might show:
- A domain name (like `pbx.hjlees.com`)
- `internal`
- Or something else

Then create the dialplan entry in **that** context.

## Quick Check: What Context Does SIP Profile Use?

Run this command to see what context is actually configured:

```bash
fs_cli -x "sofia status profile internal" | grep -i context
```

Then create the dialplan entry in **that** context (whatever it shows).

## Alternative: Edit SIP Profile Context

If the SIP profile shows `Context: public` but "public" doesn't exist:

1. **Go to:** Advanced → SIP Profiles → internal
2. **Settings** → Look for "Context" or "Dialplan Context"
3. **Change to:** One of the existing contexts (like `internal` or a domain)
4. **Save**
5. **Create dialplan** in that context

## Recommended Approach

1. **First:** Check what context the SIP profile actually uses:
   ```bash
   fs_cli -x "sofia status profile internal" | grep Context
   ```

2. **Then:** 
   - If it shows a context that exists in dropdown → Use that
   - If it shows "public" but doesn't exist → Create "public" context first
   - If it shows something else → Use that context

3. **Create dialplan entry** in the correct context

