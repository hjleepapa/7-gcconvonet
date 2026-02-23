# FusionPBX Dialplan Form Fields - Complete Guide

## Form Fields for Twilio-to-Extension-2001 Dialplan

### Required Fields

1. **Name:**
   - Value: `Twilio-to-Extension-2001`
   - Description: Descriptive name for this dialplan entry

2. **Context:**
   - Value: `public`
   - Description: The dialplan context (you already set this)

3. **Domain:**
   - Value: Select `Global` (recommended) OR your main domain (`pbx.hjlees.com` or `136.115.41.45`)
   - Why: `Global` applies to all domains, which is best for external calls

4. **Enabled:**
   - Value: `True` (select from dropdown or type `true`)
   - Description: Must be enabled for dialplan to work

### Optional but Recommended Fields

5. **Order:**
   - Value: `200` (default is fine, or use `100` for higher priority)
   - Description: Lower numbers execute first. 200 is fine.

6. **Description:**
   - Value: `Route Twilio calls to extension 2001`
   - Description: Helpful for documentation

7. **Hostname:**
   - Value: Leave **empty** OR use your domain (`pbx.hjlees.com` or `136.115.41.45`)
   - Description: Usually left empty for global dialplans

8. **Number:**
   - Value: Leave **empty**
   - Description: Not needed for this type of dialplan

9. **Destination:**
   - Value: `False` (default is fine)
   - Description: Usually `False` for routing dialplans

10. **Continue:**
    - Value: `True` (default)
    - Description: Continue processing after this dialplan

## Complete Form Values Summary

```
Name:        Twilio-to-Extension-2001
Number:       (empty)
Hostname:     (empty)
Context:      public
Continue:     True
Order:        200
Destination:  False
Domain:       Global (or pbx.hjlees.com)
Enabled:      True
Description:  Route Twilio calls to extension 2001
```

## Step-by-Step Instructions

1. **Fill in the form:**
   - Name: `Twilio-to-Extension-2001`
   - Context: `public` (you already have this)
   - Domain: Select `Global` from dropdown
   - Enabled: Select `True` from dropdown
   - Description: `Route Twilio calls to extension 2001` (optional)
   - Leave other fields as default or empty

2. **Click "SAVE"** button

3. **After saving, you'll be taken to add Conditions and Actions:**
   - Click "Continue" or look for "Conditions" section

4. **Add Condition:**
   - Condition 1: `destination_number`
   - Expression: `^2001$`
   - Click blue arrow (←) to add

5. **Add Action:**
   - Action 1: Type `transfer` (manually)
   - Value: `2001 XML internal`
   - Click blue arrow (←) to add

6. **Save again**

## Domain Selection Guide

**Option 1: Use "Global"** (Recommended)
- Applies to all domains
- Best for external calls from Twilio
- Simplest configuration

**Option 2: Use your domain** (`pbx.hjlees.com` or `136.115.41.45`)
- More specific, applies only to that domain
- Use if you have multiple domains and want domain-specific routing

**Recommendation:** Use `Global` for this use case.

## After Saving

After you save and add conditions/actions:

```bash
# Reload XML
fs_cli -x "reloadxml"

# Test the transfer
```

