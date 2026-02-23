# FusionPBX: SIP Profiles vs Dialplan Contexts

## Important Distinction

**SIP Profiles** and **Dialplan Contexts** are different things:

### SIP Profiles (Network Interfaces)
- These are the **network interfaces** that FreeSWITCH listens on
- Examples: `external`, `internal`, `wss`
- They handle **incoming SIP connections**
- You saw these in the SIP Profiles page

### Dialplan Contexts (Routing Rules)
- These are **routing contexts** where dialplan rules are stored
- Examples: `public`, `internal`
- They define **how calls are routed** after they arrive
- These are in **Dialplan Manager**, not SIP Profiles

## How They Work Together

1. **SIP Profile receives call** → `internal` profile receives Twilio call
2. **SIP Profile routes to Context** → `internal` profile routes to `public` context
3. **Dialplan Context processes call** → `public` context dialplan rules execute

## Your Current Setup

From your earlier command output:
```bash
fs_cli -x "sofia status profile internal"
```

Showed:
```
Context                 public
```

This means:
- ✅ **SIP Profile:** `internal` (receives Twilio calls)
- ✅ **Dialplan Context:** `public` (where routing rules are)
- ✅ **Configuration is correct!**

## Where to Create Dialplan

Since the `internal` SIP profile routes to `public` context, you need to create the dialplan in:

**Dialplan Manager → Context: `public`**

NOT in SIP Profiles!

## Step-by-Step: Create Dialplan Entry

1. **Login to FusionPBX:** `https://136.115.41.45`
2. **Go to:** Advanced → **Dialplan Manager** (NOT SIP Profiles!)
3. **Click:** "+" (Add) button
4. **Fill in:**
   - **Name:** `Twilio-to-Extension-2001`
   - **Context:** `public` ⚠️ **This is the dialplan context, not SIP profile!**
   - **Enabled:** `True`
   - **Continue:** Click "Continue"
5. **Add Condition:**
   - **Condition 1:** `destination_number`
   - **Expression:** `^2001$`
   - Click blue arrow (←) to add
6. **Add Action:**
   - **Action 1:** Type `transfer` (manually)
   - **Value:** `2001 XML internal`
   - Click blue arrow (←) to add
7. **Save:** Click "Save" button

## Summary

- **SIP Profiles** = Network interfaces (external, internal, wss)
- **Dialplan Contexts** = Routing rules (public, internal)
- Your `internal` SIP profile routes to `public` dialplan context
- Create dialplan entry in **Dialplan Manager** with context = `public`

