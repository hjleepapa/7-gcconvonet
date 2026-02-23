## FUSIONPBX_ADD_MISSING_SETTINGS

# Add Missing Settings to External SIP Profile

## 🔴 Missing Settings

The following settings don't exist in your FusionPBX external profile yet:
- `bypass-media` = `false`
- `media-bypass` = `false`
- `sip-force-contact` = `136.115.41.45:5060`
- `rtp-force-contact` = `136.115.41.45`
- `accept-blind-reg` = `false`

## ✅ Method 1: Add via FusionPBX GUI (Recommended)

1. **Login to FusionPBX:**
   ```
   https://136.115.41.45
   ```

2. **Navigate to SIP Profile:**
   ```
   Advanced → SIP Profiles → external
   ```

3. **Click on "Settings" tab** (or find the Settings section)

4. **For each missing setting, click "Add" or "+" button** and add:

### Setting 1: bypass-media
- **Setting Name:** `bypass-media`
- **Value:** `false`
- **Enabled:** ✅ Checked
- **Description:** `Disable media bypass for proper RTP handling`

### Setting 2: media-bypass
- **Setting Name:** `media-bypass`
- **Value:** `false`
- **Enabled:** ✅ Checked
- **Description:** `Disable media bypass for proper RTP handling`

### Setting 3: sip-force-contact
- **Setting Name:** `sip-force-contact`
- **Value:** `136.115.41.45:5060`
- **Enabled:** ✅ Checked
- **Description:** `Force SIP Contact header to use public IP`

### Setting 4: rtp-force-contact
- **Setting Name:** `rtp-force-contact`
- **Value:** `136.115.41.45`
- **Enabled:** ✅ Checked
- **Description:** `Force RTP Contact to use public IP`

### Setting 5: accept-blind-reg
- **Setting Name:** `accept-blind-reg`
- **Value:** `false`
- **Enabled:** ✅ Checked
- **Description:** `Don't accept unauthenticated registrations`

5. **Save all changes:**
   - Click "Save" button at the bottom

6. **Reload FreeSWITCH:**
   - Go to: `Status → SIP Status`
   - Find "external" profile
   - Click "Reload XML"
   - Click "Restart"

## ✅ Method 2: Add via Database (If GUI Doesn't Work)

If the GUI doesn't allow adding new settings, use the database:

```bash
# SSH into FusionPBX server
ssh root@136.115.41.45

# Connect to PostgreSQL
sudo -u postgres psql fusionpbx
```

### Add bypass-media

```sql
INSERT INTO v_sip_profile_settings (
    sip_profile_setting_uuid,
    sip_profile_uuid,
    sip_profile_setting_name,
    sip_profile_setting_value,
    sip_profile_setting_enabled
) 
SELECT 
    gen_random_uuid(),
    (SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'external'),
    'bypass-media',
    'false',
    true
WHERE NOT EXISTS (
    SELECT 1 FROM v_sip_profile_settings sps
    JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
    WHERE sp.sip_profile_name = 'external'
    AND sps.sip_profile_setting_name = 'bypass-media'
);
```

### Add media-bypass

```sql
INSERT INTO v_sip_profile_settings (
    sip_profile_setting_uuid,
    sip_profile_uuid,
    sip_profile_setting_name,
    sip_profile_setting_value,
    sip_profile_setting_enabled
) 
SELECT 
    gen_random_uuid(),
    (SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'external'),
    'media-bypass',
    'false',
    true
WHERE NOT EXISTS (
    SELECT 1 FROM v_sip_profile_settings sps
    JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
    WHERE sp.sip_profile_name = 'external'
    AND sps.sip_profile_setting_name = 'media-bypass'
);
```

### Add sip-force-contact

```sql
INSERT INTO v_sip_profile_settings (
    sip_profile_setting_uuid,
    sip_profile_uuid,
    sip_profile_setting_name,
    sip_profile_setting_value,
    sip_profile_setting_enabled
) 
SELECT 
    gen_random_uuid(),
    (SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'external'),
    'sip-force-contact',
    '136.115.41.45:5060',
    true
WHERE NOT EXISTS (
    SELECT 1 FROM v_sip_profile_settings sps
    JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
    WHERE sp.sip_profile_name = 'external'
    AND sps.sip_profile_setting_name = 'sip-force-contact'
);
```

### Add rtp-force-contact

```sql
INSERT INTO v_sip_profile_settings (
    sip_profile_setting_uuid,
    sip_profile_uuid,
    sip_profile_setting_name,
    sip_profile_setting_value,
    sip_profile_setting_enabled
) 
SELECT 
    gen_random_uuid(),
    (SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'external'),
    'rtp-force-contact',
    '136.115.41.45',
    true
WHERE NOT EXISTS (
    SELECT 1 FROM v_sip_profile_settings sps
    JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
    WHERE sp.sip_profile_name = 'external'
    AND sps.sip_profile_setting_name = 'rtp-force-contact'
);
```

### Add accept-blind-reg

```sql
INSERT INTO v_sip_profile_settings (
    sip_profile_setting_uuid,
    sip_profile_uuid,
    sip_profile_setting_name,
    sip_profile_setting_value,
    sip_profile_setting_enabled
) 
SELECT 
    gen_random_uuid(),
    (SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'external'),
    'accept-blind-reg',
    'false',
    true
WHERE NOT EXISTS (
    SELECT 1 FROM v_sip_profile_settings sps
    JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
    WHERE sp.sip_profile_name = 'external'
    AND sps.sip_profile_setting_name = 'accept-blind-reg'
);
```

### All-in-One Script

```sql
-- Add all missing settings at once
DO $$
DECLARE
    v_profile_uuid UUID;
BEGIN
    -- Get external profile UUID
    SELECT sip_profile_uuid INTO v_profile_uuid 
    FROM v_sip_profiles 
    WHERE sip_profile_name = 'external';

    -- Add bypass-media
    INSERT INTO v_sip_profile_settings (
        sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name,
        sip_profile_setting_value, sip_profile_setting_enabled
    )
    SELECT gen_random_uuid(), v_profile_uuid, 'bypass-media', 'false', true
    WHERE NOT EXISTS (
        SELECT 1 FROM v_sip_profile_settings 
        WHERE sip_profile_uuid = v_profile_uuid 
        AND sip_profile_setting_name = 'bypass-media'
    );

    -- Add media-bypass
    INSERT INTO v_sip_profile_settings (
        sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name,
        sip_profile_setting_value, sip_profile_setting_enabled
    )
    SELECT gen_random_uuid(), v_profile_uuid, 'media-bypass', 'false', true
    WHERE NOT EXISTS (
        SELECT 1 FROM v_sip_profile_settings 
        WHERE sip_profile_uuid = v_profile_uuid 
        AND sip_profile_setting_name = 'media-bypass'
    );

    -- Add sip-force-contact
    INSERT INTO v_sip_profile_settings (
        sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name,
        sip_profile_setting_value, sip_profile_setting_enabled
    )
    SELECT gen_random_uuid(), v_profile_uuid, 'sip-force-contact', '136.115.41.45:5060', true
    WHERE NOT EXISTS (
        SELECT 1 FROM v_sip_profile_settings 
        WHERE sip_profile_uuid = v_profile_uuid 
        AND sip_profile_setting_name = 'sip-force-contact'
    );

    -- Add rtp-force-contact
    INSERT INTO v_sip_profile_settings (
        sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name,
        sip_profile_setting_value, sip_profile_setting_enabled
    )
    SELECT gen_random_uuid(), v_profile_uuid, 'rtp-force-contact', '136.115.41.45', true
    WHERE NOT EXISTS (
        SELECT 1 FROM v_sip_profile_settings 
        WHERE sip_profile_uuid = v_profile_uuid 
        AND sip_profile_setting_name = 'rtp-force-contact'
    );

    -- Add accept-blind-reg
    INSERT INTO v_sip_profile_settings (
        sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name,
        sip_profile_setting_value, sip_profile_setting_enabled
    )
    SELECT gen_random_uuid(), v_profile_uuid, 'accept-blind-reg', 'false', true
    WHERE NOT EXISTS (
        SELECT 1 FROM v_sip_profile_settings 
        WHERE sip_profile_uuid = v_profile_uuid 
        AND sip_profile_setting_name = 'accept-blind-reg'
    );

    RAISE NOTICE 'All settings added successfully';
END $$;
```

After running the SQL commands:

```sql
\q
```

```bash
# Reload FreeSWITCH
fs_cli -x "reloadxml"
fs_cli -x "sofia profile external restart"
```

## 🔍 Verify Settings Were Added

```bash
# Check if all settings exist now
fs_cli -x "sofia xmlstatus profile external" | grep -E "bypass-media|media-bypass|sip-force-contact|rtp-force-contact|accept-blind-reg"
```

**Or check via database:**
```sql
SELECT 
    sip_profile_setting_name,
    sip_profile_setting_value,
    sip_profile_setting_enabled
FROM v_sip_profile_settings sps
JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
WHERE sp.sip_profile_name = 'external'
AND sip_profile_setting_name IN ('bypass-media', 'media-bypass', 'sip-force-contact', 'rtp-force-contact', 'accept-blind-reg')
ORDER BY sip_profile_setting_name;
```

## 📝 What Each Setting Does

### bypass-media = false
- **Purpose:** Disables media bypass, forcing all media to flow through FreeSWITCH
- **Why:** Ensures proper RTP handling and prevents media negotiation issues with Twilio

### media-bypass = false
- **Purpose:** Same as bypass-media (alternative name)
- **Why:** Ensures RTP streams go through FreeSWITCH for proper NAT traversal

### sip-force-contact = 136.115.41.45:5060
- **Purpose:** Forces SIP Contact header to use public IP instead of private IP
- **Why:** Twilio needs to see the public IP in Contact headers to route calls correctly

### rtp-force-contact = 136.115.41.45
- **Purpose:** Forces RTP media to use public IP in SDP (Session Description Protocol)
- **Why:** Ensures Twilio sends RTP packets to your public IP, not private IP

### accept-blind-reg = false
- **Purpose:** Rejects unauthenticated SIP REGISTER requests
- **Why:** Security - prevents unauthorized SIP phones from registering

## 🎯 Summary

Add these 5 settings to your external SIP profile:
1. `bypass-media` = `false`
2. `media-bypass` = `false`
3. `sip-force-contact` = `136.115.41.45:5060`
4. `rtp-force-contact` = `136.115.41.45`
5. `accept-blind-reg` = `false`

Use FusionPBX GUI (Method 1) if possible, or database (Method 2) if GUI doesn't work.

## FUSIONPBX_AGENT_PHONE_REJECTING

# Fix Agent Phone Rejecting Calls (SIP 603 Decline)

## 🔍 About external.xml

**Which component uses `external.xml`?**

The `external.xml` file is used by **FreeSWITCH's Sofia SIP stack** (the `mod_sofia` module). However, since you're using **FusionPBX**, FusionPBX actually:

1. **Stores SIP profile settings in its PostgreSQL database** (table: `v_sip_profile_settings`)
2. **Generates the XML files** (like `external.xml`) from the database when FreeSWITCH reloads
3. **Overwrites manual XML edits** when you click "Reload XML" in FusionPBX GUI

**Therefore:**
- ✅ **Manual edits to `external.xml` may be overwritten** by FusionPBX
- ✅ **Use FusionPBX GUI** to change SIP profile settings (recommended)
- ✅ **Or update the database directly** if GUI doesn't work

**Location:**
- `/etc/freeswitch/sip_profiles/external.xml` - Generated by FusionPBX
- FusionPBX stores settings in: `v_sip_profile_settings` table

**To see current settings:**
```bash
fs_cli -x "sofia xmlstatus profile external"
```

This shows what FreeSWITCH is actually using, regardless of what's in the XML file.

---

## 🔴 Problem: Agent's Phone Explicitly Rejects the Call

**From your logs:**
- ✅ Codec negotiation works (PCMU matched)
- ✅ Call reaches extension 2001
- ✅ Extension rings (Ring-Ready, proceeding[180])
- ❌ **Agent's phone sends SIP 603 Decline** → `CALL_REJECTED`
- ❌ Call drops ~2.6 seconds after ringing

**Key Log Evidence:**
```
2025-11-03 22:34:13.551108 - Ring-Ready sofia/internal/2001@198.27.217.12:55965!
2025-11-03 22:34:13.551108 - Callstate Change DOWN -> RINGING
2025-11-03 22:34:16.191107 - Channel entering state [terminated][603]  ← SIP 603 = Decline
2025-11-03 22:34:16.191107 - Hangup sofia/internal/2001@198.27.217.12:55965 [CS_CONSUME_MEDIA] [CALL_REJECTED]

# IMPORTANT: Dialplan is setting caller ID to extension itself:
set(caller_id_name=2001)
set(caller_id_number=2001)
```

**Agent's Phone IP:** `198.27.217.12:55965`

## 🎯 Most Likely Root Cause: Caller ID Issue

**Your logs show:**
```
set(caller_id_name=2001)
set(caller_id_number=2001)
```

**This means the call is coming FROM extension 2001 TO extension 2001**, which might cause the agent's phone to reject it as a loop or unknown caller.

**Fix:** The FusionPBX dialplan should preserve the original caller ID from Twilio instead of setting it to the extension number.

## FUSIONPBX_ANALYZE_403_LOGS

# Analyze 403 Forbidden Logs - Extension-to-Extension Calling

## 🔍 What the Logs Show

Your logs show:
1. ✅ Extension 2001 is making the call
2. ✅ Dialplan is processing the call to extension 2002
3. ✅ Bridge command is executed: `bridge(user/2002@136.115.41.45)`
4. ❌ **No logs showing what happens when trying to reach extension 2002**

The logs stop at the bridge command, which means we need to see what happens when FreeSWITCH tries to actually contact extension 2002.

## 🔎 Get More Specific Logs

### Check 1: Look for SIP INVITE to Extension 2002

```bash
# Get logs showing SIP INVITE messages to extension 2002
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "2002|sofia.*2002|invite.*2002" | tail -30
```

### Check 2: Look for Channel Creation for Extension 2002

```bash
# Look for new channel creation for extension 2002
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "New Channel.*2002|sofia.*2002" | tail -30
```

### Check 3: Check if Extension 2002 is Registered

```bash
# Check if extension 2002 is registered
fs_cli -x "sofia status profile internal reg" | grep "2002"

# Should show registration details if it's registered
```

### Check 4: Get Full Call Flow with Timestamps

```bash
# Get logs around the call time (adjust timestamp as needed)
grep -iE "536ad1aa-f360-42b1-b3bd-5e843842d965|2002" /var/log/freeswitch/freeswitch.log | tail -50
```

### Check 5: Look for 403 Response Codes

```bash
# Search for 403 SIP response codes
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "403|SIP/2.0 403|Forbidden"
```

### Check 6: Check ACL/Authentication Messages

```bash
# Look for ACL or auth errors
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "denied|acl|auth.*2002|permission.*2002"
```

## 🎯 Key Questions to Answer

Run these commands to get the missing information:

### 1. Is Extension 2002 Registered?

```bash
fs_cli -x "sofia status profile internal reg" | grep -A 5 "2002"
```

**Expected:** Should show extension 2002 registered
**If not:** Extension 2002 needs to register

### 2. Does Extension 2002 Exist?

```bash
sudo -u postgres psql fusionpbx -c "SELECT extension, enabled, user_context FROM v_extensions WHERE extension = '2002';"
```

### 3. What Happens When Bridge Tries to Contact Extension 2002?

```bash
# Get logs after the bridge command
grep -A 20 "bridge(user/2002@136.115.41.45)" /var/log/freeswitch/freeswitch.log | tail -30
```

### 4. Check for SIP Response Codes

```bash
# Look for SIP response codes (403, 404, 486, etc.)
tail -500 /var/log/freeswitch/freeswitch.log | grep -E "SIP/2.0 [4-6][0-9][0-9]|^[0-9]{3} " | tail -20
```

## 🔍 What to Look For

Based on your logs, the bridge command is executed but we need to see:

1. **SIP INVITE to extension 2002** - Is FreeSWITCH sending the INVITE?
2. **SIP Response from extension 2002** - What response comes back?
3. **Channel creation** - Does a channel get created for extension 2002?
4. **ACL check** - Is an ACL blocking the call?
5. **Registration status** - Is extension 2002 actually registered?

## 🎯 Recommended Next Steps

### Step 1: Enable Maximum Logging and Try Again

```bash
# Enable maximum logging
fs_cli -x "sofia loglevel all 9"
fs_cli -x "console loglevel debug"

# Clear previous logs (optional)
# tail -0 /var/log/freeswitch/freeswitch.log > /dev/null

# Watch logs in real-time with more context
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "2002|403|forbidden|deny|acl|invite|bridge.*2002"
```

Then make the call again from 2001 to 2002.

### Step 2: Check Extension 2002 Status

```bash
# Check if extension 2002 exists and is enabled
sudo -u postgres psql fusionpbx -c "SELECT extension, enabled, user_context, do_not_disturb FROM v_extensions WHERE extension = '2002';"

# Check if extension 2002 is registered
fs_cli -x "sofia status profile internal reg" | grep -A 10 "2002"
```

### Step 3: Try Originating from CLI

Test if FreeSWITCH can call extension 2002 directly:

```bash
# Test calling extension 2002 from FreeSWITCH CLI
fs_cli -x "originate user/2002@136.115.41.45 &echo()"
```

**If this works:** The issue is with how the SIP client (2001) is making the call
**If this fails:** The issue is with extension 2002 configuration or registration

## 📋 Complete Diagnostic Script

Run this to get all relevant information:

```bash
#!/bin/bash
echo "=== Extension 2002 Diagnostic ==="
echo ""

echo "1. Extension 2002 Database Check:"
sudo -u postgres psql fusionpbx -c "SELECT extension, enabled, user_context, do_not_disturb FROM v_extensions WHERE extension = '2002';"
echo ""

echo "2. Extension 2002 Registration Status:"
fs_cli -x "sofia status profile internal reg" | grep -A 10 "2002"
echo ""

echo "3. Recent Logs with Extension 2002:"
tail -100 /var/log/freeswitch/freeswitch.log | grep -i "2002" | tail -20
echo ""

echo "4. Recent 403/Forbidden Errors:"
tail -200 /var/log/freeswitch/freeswitch.log | grep -iE "403|forbidden" | tail -10
echo ""

echo "5. Recent Bridge Attempts to 2002:"
grep -i "bridge.*2002" /var/log/freeswitch/freeswitch.log | tail -5
echo ""

echo "6. Test Originate from CLI:"
echo "   (This will attempt to call extension 2002)"
fs_cli -x "originate user/2002@136.115.41.45 &echo()"
```

## 🔍 Most Likely Issues Based on Missing Logs

Since we don't see any SIP INVITE messages to extension 2002 in your logs, the issue is likely:

1. **Extension 2002 not registered** - FreeSWITCH can't reach it
2. **Extension 2002 doesn't exist** - Not configured in FusionPBX
3. **Extension 2002 disabled** - Disabled in FusionPBX
4. **SIP client issue** - The SIP client isn't properly sending the call

## 🎯 Immediate Actions

**Run these commands and share the output:**

```bash
# 1. Check if extension 2002 is registered
fs_cli -x "sofia status profile internal reg" | grep "2002"

# 2. Check if extension 2002 exists
sudo -u postgres psql fusionpbx -c "SELECT extension, enabled FROM v_extensions WHERE extension = '2002';"

# 3. Get logs showing what happens after bridge command
grep -A 30 "bridge(user/2002@136.115.41.45)" /var/log/freeswitch/freeswitch.log | tail -40
```

These will help identify why the bridge to extension 2002 is failing!

## FUSIONPBX_APPLY_REGISTER_ACL

# apply-register-acl Setting for External SIP Profile

## ✅ Recommended Value

**Set `apply-register-acl` to:**
```
domains
```

## 🔍 What Each ACL Setting Does

### `apply-inbound-acl`
- **Controls:** Who can send **SIP INVITE** requests (make calls)
- **Your setting:** `Twilio-SIP` ✅
- **Purpose:** Allows Twilio IP ranges to send calls to your FusionPBX

### `apply-register-acl`
- **Controls:** Who can send **SIP REGISTER** requests (register SIP phones)
- **Recommended:** `domains`
- **Purpose:** Allows SIP phones to register from configured domains

## 📝 Why `domains`?

The `domains` ACL:
1. **References domains configured in FusionPBX** - FusionPBX automatically creates this ACL based on your configured domains
2. **Allows legitimate registrations** - SIP phones from your configured domains can register
3. **Provides security** - Blocks registrations from unknown/unconfigured domains
4. **Standard for external profile** - This is the typical setting for the external SIP profile

## ⚙️ Configuration

### Via FusionPBX GUI

1. **Login to FusionPBX:**
   ```
   https://136.115.41.45
   ```

2. **Navigate to SIP Profile:**
   ```
   Advanced → SIP Profiles → external
   ```

3. **Find `apply-register-acl` setting:**
   - In the Settings table, find the row: `apply-register-acl`
   - Set **Value** to: `domains`
   - Make sure **Enabled** is checked ✅
   - **Description** can be: "Allow registrations from configured domains"

4. **Save:**
   - Click "Save" at the bottom
   - Go to: `Status → SIP Status`
   - Find "external" profile
   - Click "Reload XML"
   - Click "Restart"

### Via Database

```bash
# SSH into FusionPBX server
ssh root@136.115.41.45

# Connect to PostgreSQL
sudo -u postgres psql fusionpbx

# Update apply-register-acl setting
UPDATE v_sip_profile_settings sps
SET sip_profile_setting_value = 'domains',
    sip_profile_setting_enabled = true
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-register-acl';

# If setting doesn't exist, INSERT it
INSERT INTO v_sip_profile_settings (
    sip_profile_setting_uuid,
    sip_profile_uuid,
    sip_profile_setting_name,
    sip_profile_setting_value,
    sip_profile_setting_enabled
) 
SELECT 
    gen_random_uuid(),
    (SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'external'),
    'apply-register-acl',
    'domains',
    true
WHERE NOT EXISTS (
    SELECT 1 FROM v_sip_profile_settings sps
    JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
    WHERE sp.sip_profile_name = 'external'
    AND sps.sip_profile_setting_name = 'apply-register-acl'
);

\q

# Reload FreeSWITCH
fs_cli -x "reloadxml"
fs_cli -x "sofia profile external restart"
```

## 🔍 Verify Setting

```bash
# Check if apply-register-acl is set correctly
fs_cli -x "sofia xmlstatus profile external" | grep -i "apply-register-acl"
```

**Should show:**
```
<apply-register-acl>domains</apply-register-acl>
```

## 📊 Complete ACL Configuration Summary

For your external SIP profile, you should have:

| Setting | Value | Purpose |
|---------|-------|---------|
| `apply-inbound-acl` | `Twilio-SIP` | Allow Twilio IPs to send calls |
| `apply-register-acl` | `domains` | Allow registrations from configured domains |
| `accept-blind-reg` | `false` | Don't accept unauthenticated registrations |

## 🔐 Security Notes

### Why Not Allow All Registrations?

**Don't set `apply-register-acl` to:**
- ❌ Empty/null - Would allow anyone to register (security risk)
- ❌ `any` or `all` - Would allow anyone to register (security risk)
- ❌ `Twilio-SIP` - Twilio doesn't register, so this wouldn't help

**Use `domains` because:**
- ✅ Allows legitimate SIP phones from your configured domains
- ✅ Blocks unknown/unconfigured domains
- ✅ Standard security practice for external SIP profiles

### About `domains` ACL

The `domains` ACL is automatically maintained by FusionPBX based on:
- Domains configured in `Advanced → Domains`
- Each domain you add creates entries in the `domains` ACL
- When a SIP REGISTER request comes in, FusionPBX checks if the domain matches a configured domain

## 🎯 Summary

- **Setting:** `apply-register-acl`
- **Value:** `domains`
- **Location:** FusionPBX GUI → `Advanced → SIP Profiles → external → Settings`
- **Why:** Allows registrations from configured FusionPBX domains while blocking unknown domains

## FUSIONPBX_CALL_DROPS_AFTER_ANSWER

# Fix Call Drops After Agent Answers (CALL_REJECTED)

## 🔴 Problem: Call Transfers Successfully, But Drops When Agent Answers

**Symptoms:**
- ✅ Twilio call connects to voice agent
- ✅ Call transfers to extension 2001
- ✅ Extension 2001 rings
- ❌ Call drops immediately when agent answers
- ❌ Logs show: `CALL_REJECTED` on extension 2001 leg

**Example Log:**
```
[NOTICE] sofia.c:8736 Hangup sofia/internal/2001@198.27.217.12:55965 [CS_CONSUME_MEDIA] [CALL_REJECTED]
[NOTICE] switch_cpp.cpp:752 Hangup sofia/internal/+19259897818@sip.twilio.com [CS_EXECUTE] [NORMAL_CLEARING]
```

## 🔍 Root Causes

The `CALL_REJECTED` error with `CS_CONSUME_MEDIA` typically indicates:

1. **Media (RTP) Negotiation Failure** - Most common
   - Codec mismatch between Twilio and agent's phone
   - RTP ports blocked by firewall
   - NAT traversal issues
   - Incorrect RTP IP addresses

2. **Agent's Phone Rejecting Call**
   - Phone client configuration issue
   - Network connectivity problem from agent's device
   - Codec not supported by agent's phone

3. **FreeSWITCH Media Handling**
   - Media bypass/disabling issues
   - Incorrect media mode settings

## ✅ Diagnostic Steps

### Step 1: Check Media Negotiation in Logs

```bash
# Watch logs during transfer and answer
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "rtp|media|codec|2001|reject"

# Look for:
# - "RTP Statistics" or "Media Statistics"
# - Codec negotiation messages
# - RTP port assignments
# - Media stream creation/teardown
```

**What to look for:**
- RTP ports being assigned
- Codec negotiation (should see PCMU or PCMA)
- Any "reject" or "decline" messages
- Media stream establishment messages

### Step 2: Enable Detailed Media Debugging

```bash
# Enable RTP debugging
fs_cli -x "console loglevel debug"

# Enable SOFIA (SIP) debugging
fs_cli -x "sofia loglevel all 9"

# Watch logs
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "rtp|media|codec|2001"
```

### Step 3: Check Codec Compatibility

```bash
# Check what codecs Twilio leg supports
fs_cli -x "sofia status profile external" | grep -i "codec"

# Check what codecs extension 2001 supports
fs_cli -x "user_data 2001@136.115.41.45 var" | grep -i "codec"

# Check what codecs are negotiated for the call
# (Run this while call is active, before it drops)
fs_cli -x "show channels" | grep -A 10 "2001"
```

**Expected:** Both should support PCMU (G.711 μ-law) or PCMA (G.711 A-law)

### Step 4: Check RTP IP Addresses

```bash
# Check external SIP profile RTP settings
fs_cli -x "sofia xmlstatus profile external" | grep -i "rtp"

# Verify external RTP IP is correct
fs_cli -x "sofia xmlstatus profile external" | grep -E "ext-rtp-ip|rtp-ip"
```

**Should show:**
- `ext-rtp-ip`: `136.115.41.45` (public IP)
- `rtp-ip`: `10.128.0.8` (internal IP)

### Step 5: Test Internal Call (Extension to Extension)

```bash
# Test if extension 2001 can make/receive internal calls
fs_cli -x "originate user/2002@136.115.41.45 &echo()"

# Then have extension 2002 call 2001
fs_cli -x "originate user/2001@136.115.41.45 &echo()"
```

**If internal calls work but Twilio transfers don't:** The issue is with Twilio ↔ FusionPBX media path, not the extension itself.

### Step 6: Check Firewall Rules for RTP

```bash
# Check if RTP ports (10000-20000) are open
netstat -tuln | grep -E ":(10[0-9]{3}|1[1-9][0-9]{3}|20000)"

# Or use iptables
iptables -L -n | grep -E "5060|10000:20000"
```

**RTP uses UDP ports 10000-20000.** These must be open for media to flow.

### Step 7: Check Agent's Phone Configuration

Ask the agent to check their SIP phone settings:

1. **Codec Settings:**
   - Ensure PCMU (G.711 μ-law) or PCMA (G.711 A-law) is enabled
   - Disable video codecs if enabled

2. **NAT Settings:**
   - Enable "NAT Traversal" or "STUN"
   - Set "STUN Server" to: `stun:stun.l.google.com:19302`

3. **Network:**
   - Check if phone can reach FusionPBX IP `136.115.41.45`
   - Test from agent's network: `telnet 136.115.41.45 5060`

### Step 8: Check Media Mode in FreeSWITCH

```bash
# Check media mode for extension 2001
fs_cli -x "user_data 2001@136.115.41.45 var" | grep -i "media"

# Check if media bypass is enabled (should be disabled for Twilio)
fs_cli -x "sofia xmlstatus profile external" | grep -i "bypass"
```

## 🔧 Solutions

### Solution 1: Fix Codec Mismatch (Most Common)

**Force PCMU/PCMA on External Profile:**

1. **Via FusionPBX GUI:**
   ```
   Advanced → SIP Profiles → external → Edit
   → Settings tab
   → Find "Codec Preferences"
   → Set:
       Inbound Codec Preferences: PCMU,PCMA
       Outbound Codec Preferences: PCMU,PCMA
   → Save → Apply Config
   ```

2. **Via CLI (edit `/etc/freeswitch/sip_profiles/external.xml`):**
   ```xml
   <param name="inbound-codec-prefs" value="PCMU,PCMA"/>
   <param name="outbound-codec-prefs" value="PCMU,PCMA"/>
   ```

3. **Reload SIP Profile:**
   ```bash
   fs_cli -x "reload mod_sofia"
   # Or via FusionPBX GUI: Status → SIP Status → external → Reload XML → Restart
   ```

### Solution 2: Fix RTP IP Addresses

**Ensure External Profile Advertises Correct Public IP:**

1. **Check `/etc/freeswitch/sip_profiles/external.xml`:**
   ```xml
   <param name="ext-sip-ip" value="136.115.41.45"/>
   <param name="ext-rtp-ip" value="136.115.41.45"/>
   <param name="sip-force-contact" value="136.115.41.45:5060"/>
   <param name="rtp-force-contact" value="136.115.41.45"/>
   ```

2. **Reload:**
   ```bash
   fs_cli -x "reload mod_sofia"
   ```

### Solution 3: Open Firewall Ports for RTP

```bash
# Open RTP port range (UDP 10000-20000)
ufw allow 10000:20000/udp

# Or with iptables
iptables -A INPUT -p udp --dport 10000:20000 -j ACCEPT
iptables-save

# Also ensure SIP port is open
ufw allow 5060/udp
ufw allow 5060/tcp
```

### Solution 4: Disable Media Bypass

Media bypass can cause issues with Twilio transfers:

```bash
# Check current setting
fs_cli -x "sofia xmlstatus profile external" | grep -i "bypass"

# Edit `/etc/freeswitch/sip_profiles/external.xml`
# Ensure these are set:
<param name="bypass-media" value="false"/>
<param name="media-bypass" value="false"/>

# Reload
fs_cli -x "reload mod_sofia"
```

### Solution 5: Configure NAT Traversal

```xml
<!-- In external.xml -->
<param name="aggressive-nat-detection" value="true"/>
<param name="local-network-acl" value="localnet.auto"/>
<param name="apply-nat-acl" value="nat.auto"/>
<param name="rtp-ip" value="10.128.0.8"/>
<param name="ext-rtp-ip" value="136.115.41.45"/>
```

### Solution 6: Check Extension 2001's Media Settings

1. **Via FusionPBX GUI:**
   ```
   Accounts → Extensions → 2001 → Advanced tab
   → Check "Codec" settings
   → Ensure PCMU or PCMA is selected
   → Save
   ```

2. **Check Extension's Domain:**
   ```
   Accounts → Extensions → 2001 → Advanced tab
   → Ensure "Domain" is set to: 136.115.41.45 (or your domain)
   ```

### Solution 7: Test with Direct SIP Call

Test if the issue is specific to Twilio transfers:

```bash
# From another SIP client, make a direct call to extension 2001
# Using sip:2001@136.115.41.45:5060

# If this works, the issue is Twilio-specific
# If this also drops, the issue is with extension 2001 or FusionPBX configuration
```

## 📊 Detailed Log Analysis

When reviewing logs, look for these specific patterns:

### Good Signs (Call Should Work):
```
[NOTICE] sofia.c:xxxx Channel [sofia/internal/2001@...] has been answered
[DEBUG] switch_rtp.c:xxxx RTP Server Ready [external IP:136.115.41.45:xxxx]
[DEBUG] switch_rtp.c:xxxx Starting timer [soft] 160 bytes [60]ms
[INFO] switch_core_media.c:xxxx Media Codec [PCMU] Negotiation Complete
```

### Bad Signs (Call Will Drop):
```
[WARNING] sofia.c:xxxx Failed to establish RTP stream
[ERROR] switch_rtp.c:xxxx RTP timeout waiting for media
[NOTICE] sofia.c:xxxx Hangup sofia/internal/2001@... [CS_CONSUME_MEDIA] [CALL_REJECTED]
[WARNING] switch_core_media.c:xxxx Codec negotiation failed
```

## 🎯 Quick Fix Checklist

Run through these in order:

- [ ] **Codec mismatch:** Force PCMU/PCMA on external profile
- [ ] **RTP IPs:** Verify `ext-rtp-ip` is `136.115.41.45`
- [ ] **Firewall:** Open UDP ports 10000-20000
- [ ] **Media bypass:** Disable media bypass on external profile
- [ ] **Extension codec:** Ensure extension 2001 supports PCMU/PCMA
- [ ] **NAT settings:** Enable aggressive NAT detection
- [ ] **Test internal:** Verify extension 2001 works for internal calls
- [ ] **Agent phone:** Check agent's SIP phone codec and NAT settings

## 🔍 Still Not Working?

If the call still drops after trying all solutions:

1. **Capture Full SIP Trace:**
   ```bash
   fs_cli -x "sofia loglevel all 9"
   # Attempt transfer and capture full output
   tail -f /var/log/freeswitch/freeswitch.log > /tmp/sip_trace.log
   ```

2. **Check Twilio Call Logs:**
   - Go to Twilio Console → Monitor → Logs → Calls
   - Find the failed transfer call
   - Check "Media Streams" section
   - Look for RTP/STUN errors

3. **Test with Different Extension:**
   ```bash
   # Try transferring to extension 2002
   # If 2002 works, the issue is specific to extension 2001
   ```

4. **Check FreeSWITCH Version:**
   ```bash
   freeswitch -version
   # Older versions may have media handling bugs
   ```

## 📝 Summary

The most common cause of `CALL_REJECTED` after answer is **media negotiation failure**. Focus on:

1. **Codec compatibility** (PCMU/PCMA)
2. **RTP IP addresses** (must advertise public IP)
3. **Firewall rules** (RTP ports 10000-20000 UDP)
4. **NAT traversal** (aggressive NAT detection)

Start with Solution 1 (codec mismatch) as it's the most common issue.

## FUSIONPBX_CHECK_ENDPOINTS

# Checking FusionPBX Endpoints and Profile Status

## Understanding the "No Registrations" Message

The `external` SIP profile shows 0 registrations, which is **NORMAL** for Twilio transfers because:

1. ✅ **Twilio doesn't register** - it uses direct SIP INVITE calls
2. ✅ **Your WebRTC extensions register** to the `internal` profile, not `external`
3. ✅ **Twilio calls go to `external`** profile without registration

## What to Check Instead

### 1. Check All SIP Profiles

```bash
fs_cli -x "sofia status"
```

**You should see both profiles:**
- `internal` → For internal phones/extensions (2001)
- `external` → For external SIP calls from Twilio

### 2. Check if Extension 2001 Exists in FusionPBX

```bash
# Via FusionPBX CLI
fs_cli -x "user_exists id 2001 domain-name default"

# Or check PostgreSQL/MariaDB
sudo -u postgres psql fusionpbx
SELECT * FROM v_extensions WHERE extension = '2001';
```

### 3. Check SIP Profile Status

```bash
# See all profiles and their status
fs_cli -x "sofia status"

# See external profile details
fs_cli -x "sofia status profile external"

# See internal profile details (where 2001 would be)
fs_cli -x "sofia status profile internal"
```

### 4. Check if Extension 2001 is Registered to INTERNAL Profile

```bash
# This is where your extension should show up
fs_cli -x "sofia status profile internal reg"

# Should show:
# call-id: xxx@internal
# user: 2001
# contact: sip:2001@...
# registered: true
```

### 5. Check Dial Plan Context

```bash
# See dialplan contexts
fs_cli -x "dialplan_reload"
fs_cli -x "dialplan_loglevel 9"

# Test if extension 2001 is in dialplan
fs_cli -x "dialplan_lookup context=from-external number=2001"
```

## Critical Configuration Check

Since Twilio is calling extension 2001 on the `external` profile, you need:

### Check Dial Plan for Twilio Calls

```bash
# Check what context external calls go to
fs_cli -x "sofia xmlstatus profile external" | grep context

# Should show something like:
# <context>public</context>
# OR
# <context>from-external</context>
```

### Verify Extension 2001 Context

Twilio calls come in on `external` profile → need to route to extension 2001

```bash
# Check the dialplan context for external calls
fs_cli -x "xml_locate directory domain default 2001"
```

## Next Steps

1. **Check extension 2001 exists:**
   ```bash
   sudo -u postgres psql fusionpbx -c "SELECT * FROM v_extensions WHERE extension = '2001';"
   ```

2. **Check which profile extension 2001 uses:**
   - Go to FusionPBX GUI: `Accounts → Extensions → 2001`
   - Check "SIP Profile" setting

3. **Check external profile ACL is configured:**
   ```bash
   fs_cli -x "sofia xmlstatus profile external" | grep apply-inbound-acl
   ```
   Should show: `<apply-inbound-acl>Twilio-SIP</apply-inbound-acl>`

## If Extension 2001 Doesn't Exist

You need to create it in FusionPBX:

1. Login to FusionPBX: `https://136.115.41.45`
2. Go to: `Accounts → Extensions → Add Extension`
3. Create extension:
   - Extension: `2001`
   - Password: (set a secure password)
   - Display Name: "Support Agent"
   - SIP Profile: `internal` (for registration)
   - Context: (usually `default`)
   - Save

4. Create a SIP phone registration or configure a device to use it

## Common Issues

### Issue: Extension Not Reachable from External

**Problem:** Extension 2001 is in `internal` profile, but Twilio calls come to `external` profile

**Solution:** Check dial plan routes external → internal calls

### Issue: "Extension Not Found"

**Check:**
```bash
fs_cli -x "user_exists id 2001 domain-name default"
```

**If false, create the extension in FusionPBX GUI**

### Issue: No Audio After Transfer

**Problem:** RTP ports not open or NAT issues

**Solution:**
- Check firewall allows UDP 10000-20000
- Verify `ext-rtp-ip` is set to public IP in SIP profile


## FUSIONPBX_DISABLE_MADDR_FIX


## FUSIONPBX_ENABLE_WEBRTC_PROFILE

# FusionPBX WebRTC Profile Setup - Detailed Steps

## Overview

This guide provides detailed step-by-step instructions to enable and configure the WebRTC (wss) SIP profile in FusionPBX, which allows WebRTC clients to connect directly to FusionPBX.

**Your Configuration:**
- FusionPBX IP: `136.115.41.45`
- WebRTC Port: `7443` (default)
- Domain: `136.115.41.45`

---

## Step-by-Step Instructions

### Step 1: Access FusionPBX Admin Panel

1. **Open your web browser**
2. **Navigate to:** `https://136.115.41.45`
3. **Log in** with your admin credentials
4. **Verify you're in the admin interface**

---

### Step 2: Navigate to SIP Profiles

1. **Click on "Advanced"** in the top menu bar
2. **Click on "SIP Profiles"** from the dropdown menu
3. **You should see a list of SIP profiles** including:
   - `internal` - For internal phones/extensions
   - `external` - For external SIP calls
   - `wss` - WebRTC profile (may not be visible if not enabled)

---

### Step 3: Check Current WebRTC Profile Status

#### Option A: If "wss" profile is already listed:

1. **Look for "wss" in the profile list**
2. **Click on "wss"** to view/edit its settings
3. **Skip to Step 4** to configure settings

#### Option B: If "wss" profile is NOT listed:

The profile exists in FreeSWITCH but may not be enabled in FusionPBX. You need to enable it:

1. **Click on "Default Settings"** (if available) or check System Settings
2. **Look for WebRTC/WSS profile settings**
3. **OR proceed to enable it via database** (see Step 3B below)

#### Option B (Alternative): Enable via FreeSWITCH CLI

```bash
# SSH into your FusionPBX server
ssh root@136.115.41.45

# Access FreeSWITCH CLI
fs_cli

# Check if wss profile exists
sofia status

# If it shows "wss" profile, it's already configured
# If not, you may need to enable it
```

---

### Enable wss Profile via FreeSWITCH CLI - Detailed Steps

If the wss profile doesn't appear in the FusionPBX GUI, or you prefer to enable it via command line, follow these detailed steps:

#### Step 1: SSH into FusionPBX Server

```bash
ssh root@136.115.41.45
```

#### Step 2: Access FreeSWITCH CLI

```bash
# Method 1: Direct fs_cli command
fs_cli

# Method 2: With specific command (non-interactive)
fs_cli -x "sofia status"

# Method 3: One-time command execution
fs_cli -x "command_here"
```

**Note:** If `fs_cli` is not in your PATH, you may need to use the full path:
```bash
/usr/local/freeswitch/bin/fs_cli
# OR
/opt/freeswitch/bin/fs_cli
# OR (if installed via package)
/usr/bin/fs_cli
```

#### Step 3: Check Current Profile Status

```bash
# Check all SIP profiles
sofia status

# Expected output should show profiles like:
# Name         Type      Data        State
# =================================================================
# internal     profile   sip:mod_sofia@127.0.0.1:5060   RUNNING
# external     profile   sip:mod_sofia@127.0.0.1:5080   RUNNING
# wss          profile   sip:mod_sofia@127.0.0.1:7443   STOPPED  ← May show STOPPED or not appear
```

#### Step 4: Check if wss Profile Configuration Exists

```bash
# Check if wss profile configuration file exists
ls -la /etc/freeswitch/sip_profiles/wss.xml

# Or check FusionPBX database
sudo -u postgres psql fusionpbx -c "SELECT * FROM v_sip_profiles WHERE sip_profile_name = 'wss';"

# Check FreeSWITCH XML directory
ls -la /usr/local/freeswitch/conf/sip_profiles/wss.xml
# OR
ls -la /opt/freeswitch/conf/sip_profiles/wss.xml
```

#### Step 5: Start/Restart wss Profile

If the profile exists but is stopped:

```bash
# Start the wss profile
sofia profile wss start

# OR restart it if it's already running
sofia profile wss restart

# Check status after starting
sofia status profile wss
```

**Expected output after starting:**
```
Profile Name: wss
PROFILE STATE: RUNNING
```

#### Step 6: Create wss Profile if It Doesn't Exist

If the profile doesn't exist, you need to create it. There are two approaches:

##### Option A: Create via FusionPBX Database (Recommended)

```bash
# Connect to FusionPBX database
sudo -u postgres psql fusionpbx

# Insert wss profile into database
INSERT INTO v_sip_profiles (sip_profile_uuid, sip_profile_name, sip_profile_enabled, sip_profile_description)
VALUES (gen_random_uuid(), 'wss', 'true', 'WebRTC WebSocket Secure Profile');

# Exit database
\q

# Reload FreeSWITCH XML from database
fs_cli -x "reloadxml"
fs_cli -x "sofia profile wss start"
```

##### Option B: Create Configuration File Manually

```bash
# Create wss.xml configuration file
cat > /etc/freeswitch/sip_profiles/wss.xml << 'EOF'
<profile name="wss">
  <settings>
    <param name="name" value="wss"/>
    <param name="sip-ip" value="0.0.0.0"/>
    <param name="sip-port" value="7443"/>
    <param name="tls" value="true"/>
    <param name="tls-bind-params" value="transport=wss"/>
    <param name="ext-sip-ip" value="136.115.41.45"/>
    <param name="ext-rtp-ip" value="136.115.41.45"/>
    <param name="domain" value="136.115.41.45"/>
    <param name="codec-prefs" value="G722,PCMU,PCMA"/>
    <param name="rtp-ip" value="0.0.0.0"/>
    <param name="rtp-min-port" value="16384"/>
    <param name="rtp-max-port" value="32768"/>
    <param name="local-network-acl" value="localnet.auto"/>
    <param name="apply-nat-acl" value="nat.auto"/>
    <param name="apply-inbound-acl" value="domains"/>
    <param name="apply-register-acl" value="domains"/>
    <param name="bypass-media" value="false"/>
    <param name="media-bypass" value="false"/>
  </settings>
</profile>
EOF

# Set proper permissions
chown freeswitch:freeswitch /etc/freeswitch/sip_profiles/wss.xml
chmod 644 /etc/freeswitch/sip_profiles/wss.xml

# Reload XML configuration
fs_cli -x "reloadxml"

# Start the profile
fs_cli -x "sofia profile wss start"
```

#### Step 7: Verify wss Profile is Running

```bash
# Check profile status
fs_cli -x "sofia status profile wss"

# Expected output:
# Profile Name: wss
# PROFILE STATE: RUNNING
# ...
```

#### Step 8: Check Port is Listening

```bash
# Check if port 7443 is listening
netstat -tlnp | grep 7443

# OR using ss command
ss -tlnp | grep 7443

# Expected output:
# tcp  0  0 0.0.0.0:7443  0.0.0.0:*  LISTEN  12345/freeswitch
# OR
# tcp6  0  0 :::7443  :::*  LISTEN  12345/freeswitch
```

#### Step 9: View Detailed Profile Information

```bash
# Get detailed XML status
fs_cli -x "sofia xmlstatus profile wss"

# This will show comprehensive configuration including:
# - All settings
# - Codecs
# - ACLs
# - TLS configuration
# - RTP settings
```

#### Step 10: Enable wss Profile to Start Automatically

To ensure the profile starts automatically on FreeSWITCH restart:

```bash
# Check if profile is enabled in FusionPBX database
sudo -u postgres psql fusionpbx -c "SELECT sip_profile_name, sip_profile_enabled FROM v_sip_profiles WHERE sip_profile_name = 'wss';"

# If enabled is false, update it:
sudo -u postgres psql fusionpbx -c "UPDATE v_sip_profiles SET sip_profile_enabled = 'true' WHERE sip_profile_name = 'wss';"

# Verify
sudo -u postgres psql fusionpbx -c "SELECT sip_profile_name, sip_profile_enabled FROM v_sip_profiles WHERE sip_profile_name = 'wss';"
```

#### Step 11: Configure TLS Certificate (If Not Already Done)

The wss profile requires a TLS certificate. Check and configure:

```bash
# Check if certificate exists
ls -la /etc/freeswitch/tls/*.pem
ls -la /etc/freeswitch/tls/wss.*

# If certificate doesn't exist, generate one:
cd /etc/freeswitch/tls
openssl req -x509 -newkey rsa:4096 -keyout wss.pem -out wss.pem -days 365 -nodes -subj "/CN=136.115.41.45"

# Set permissions
chown freeswitch:freeswitch wss.pem
chmod 600 wss.pem

# Restart the profile to load certificate
fs_cli -x "sofia profile wss restart"
```

#### Step 12: Test WebRTC Connection

```bash
# Check for WebSocket connections (after a client connects)
fs_cli -x "sofia status profile wss reg"

# Should show registrations if any clients are connected
```

#### Troubleshooting Commands

If the profile won't start, use these diagnostic commands:

```bash
# Check FreeSWITCH logs for errors
tail -100 /var/log/freeswitch/freeswitch.log | grep -i wss
tail -100 /var/log/freeswitch/freeswitch.log | grep -i 7443

# Check for port conflicts
lsof -i :7443
netstat -tlnp | grep 7443

# Verify FreeSWITCH has permissions
ps aux | grep freeswitch
ls -la /etc/freeswitch/sip_profiles/

# Check configuration syntax
fs_cli -x "reloadxml"
# If errors appear, they will be shown

# Try starting with verbose logging
fs_cli -x "console loglevel debug"
fs_cli -x "sofia loglevel all 9"
fs_cli -x "sofia profile wss start"
# Then check logs
tail -f /var/log/freeswitch/freeswitch.log
```

#### Common Issues and Solutions

**Issue 1: Profile shows as STOPPED**
```bash
# Check logs for errors
tail -100 /var/log/freeswitch/freeswitch.log | grep -i error | grep -i wss

# Try restarting
fs_cli -x "sofia profile wss restart"

# Check if port is in use
lsof -i :7443
```

**Issue 2: Port 7443 already in use**
```bash
# Find what's using the port
lsof -i :7443

# Kill the process if it's not FreeSWITCH
kill -9 <PID>

# Or change port in configuration (not recommended)
```

**Issue 3: TLS certificate errors**
```bash
# Check certificate exists and is valid
openssl x509 -in /etc/freeswitch/tls/wss.pem -text -noout

# Regenerate if needed (see Step 11 above)
```

**Issue 4: Permission denied**
```bash
# Check file ownership
ls -la /etc/freeswitch/sip_profiles/wss.xml

# Fix ownership
chown freeswitch:freeswitch /etc/freeswitch/sip_profiles/wss.xml

# Fix certificate permissions
chown freeswitch:freeswitch /etc/freeswitch/tls/wss.pem
chmod 600 /etc/freeswitch/tls/wss.pem
```

#### Quick Reference Commands

```bash
# Start wss profile
fs_cli -x "sofia profile wss start"

# Stop wss profile
fs_cli -x "sofia profile wss stop"

# Restart wss profile
fs_cli -x "sofia profile wss restart"

# Check status
fs_cli -x "sofia status profile wss"

# Check all profiles
fs_cli -x "sofia status"

# Reload XML configuration
fs_cli -x "reloadxml"

# View registrations on wss profile
fs_cli -x "sofia status profile wss reg"

# Get XML status
fs_cli -x "sofia xmlstatus profile wss"
```

---

### Step 4: Configure WebRTC Profile Settings

Once you're on the **wss profile settings page**, configure the following:

#### 4.1 General Settings

**Find the "Settings" table** and configure these parameters:

| Setting Name | Value | Enabled | Description |
|-------------|-------|---------|-------------|
| **name** | `wss` | ✅ Yes | Profile name |
| **hostname** | `136.115.41.45` | ✅ Yes | Your public IP or domain |
| **domain** | `136.115.41.45` | ✅ Yes | SIP domain |

#### 4.2 Network Settings

| Setting Name | Value | Enabled | Description |
|-------------|-------|---------|-------------|
| **sip-ip** | `0.0.0.0` | ✅ Yes | Listen on all interfaces |
| **sip-port** | `7443` | ✅ Yes | WSS port (default) |
| **tls** | `true` | ✅ Yes | Enable TLS (required for WSS) |
| **tls-bind-params** | `transport=wss` | ✅ Yes | WSS transport |
| **ext-sip-ip** | `136.115.41.45` | ✅ Yes | External SIP IP |
| **ext-rtp-ip** | `136.115.41.45` | ✅ Yes | External RTP IP |

#### 4.3 WebRTC-Specific Settings

| Setting Name | Value | Enabled | Description |
|-------------|-------|---------|-------------|
| **enable-100rel** | `true` | ✅ Yes | Enable reliable provisional responses |
| **disable-register** | `false` | ✅ Yes | Allow registrations |
| **rtp-ip** | `0.0.0.0` | ✅ Yes | RTP bind IP |
| **rtp-min-port** | `16384` | ✅ Yes | RTP port range start |
| **rtp-max-port** | `32768` | ✅ Yes | RTP port range end |

#### 4.4 Codec Settings

| Setting Name | Value | Enabled | Description |
|-------------|-------|---------|-------------|
| **codec-prefs** | `G722,PCMU,PCMA` | ✅ Yes | Preferred codecs |
| **inbound-codec-prefs** | `G722,PCMU,PCMA` | ✅ Yes | Inbound codec preference |
| **outbound-codec-prefs** | `PCMU,PCMA` | ✅ Yes | Outbound codec preference |

**Codec Order:**
- **G722** - High-quality wideband audio (preferred for WebRTC)
- **PCMU** - G.711 μ-law (ULAW) - Standard codec
- **PCMA** - G.711 A-law (ALAW) - Standard codec

#### 4.5 NAT and Firewall Settings

| Setting Name | Value | Enabled | Description |
|-------------|-------|---------|-------------|
| **local-network-acl** | `localnet.auto` | ✅ Yes | Local network ACL |
| **apply-nat-acl** | `nat.auto` | ✅ Yes | NAT handling |
| **rtp-rewrite-timestamps** | `false` | ✅ Yes | RTP timestamp handling |
| **disable-transcoding** | `false` | ✅ Yes | Allow codec transcoding |

#### 4.6 ACL (Access Control) Settings

| Setting Name | Value | Enabled | Description |
|-------------|-------|---------|-------------|
| **apply-inbound-acl** | `domains` | ✅ Yes | Allow registered domains |
| **apply-register-acl** | `domains` | ✅ Yes | Allow domain registrations |

**Important:** For WebRTC, you typically want to allow connections from any domain, but you can restrict this if needed.

#### 4.7 Media Settings

| Setting Name | Value | Enabled | Description |
|-------------|-------|---------|-------------|
| **bypass-media** | `false` | ✅ Yes | Don't bypass media |
| **media-bypass** | `false` | ✅ Yes | Don't bypass media |
| **media-bypass-to** | (empty) | ❌ No | - |
| **media-bypass-from** | (empty) | ❌ No | - |

---

### Step 5: Configure TLS/SSL Certificate

WebRTC requires WSS (WebSocket Secure), which needs a valid TLS certificate.

#### Option A: Use Existing Certificate

If FusionPBX already has an SSL certificate configured:

1. **Check "tls" setting** is set to `true`
2. **Verify certificate path** in system settings
3. **Ensure certificate is valid** for `136.115.41.45`

#### Option B: Generate Self-Signed Certificate (Testing Only)

```bash
# SSH into FusionPBX server
ssh root@136.115.41.45

# Navigate to FreeSWITCH certs directory
cd /etc/freeswitch/tls

# Generate self-signed certificate (for testing)
openssl req -x509 -newkey rsa:4096 -keyout wss.pem -out wss.pem -days 365 -nodes -subj "/CN=136.115.41.45"

# Set permissions
chown freeswitch:freeswitch wss.pem
chmod 600 wss.pem

# Restart FreeSWITCH
systemctl restart freeswitch
```

#### Option C: Use Let's Encrypt Certificate (Production)

```bash
# Install certbot if not already installed
apt-get install certbot

# Obtain certificate
certbot certonly --standalone -d 136.115.41.45

# Certificate will be in: /etc/letsencrypt/live/136.115.41.45/
# Copy to FreeSWITCH directory
cp /etc/letsencrypt/live/136.115.41.45/fullchain.pem /etc/freeswitch/tls/wss.crt
cp /etc/letsencrypt/live/136.115.41.45/privkey.pem /etc/freeswitch/tls/wss.key

# Set permissions
chown freeswitch:freeswitch /etc/freeswitch/tls/wss.*
chmod 600 /etc/freeswitch/tls/wss.*

# Configure in FusionPBX or wss.xml
```

**In FusionPBX GUI:**
- Find **tls-cert-file** setting
- Set value to: `/etc/freeswitch/tls/wss.crt`
- Find **tls-key-file** setting
- Set value to: `/etc/freeswitch/tls/wss.key`

---

### Step 6: Save and Apply Settings

1. **Click "Save" button** at the bottom of the settings page
2. **Wait for confirmation message**

---

### Step 7: Reload SIP Profile

After saving, you need to reload the SIP profile:

#### Via FusionPBX GUI:

1. **Go to:** **Status → SIP Status**
2. **Find the "wss" profile** in the list
3. **Click "Reload XML"** button for the wss profile
4. **Click "Restart"** button for the wss profile
5. **Verify status shows "RUNNING"**

#### Via FreeSWITCH CLI:

```bash
# SSH into FusionPBX
ssh root@136.115.41.45

# Access FreeSWITCH CLI
fs_cli

# Reload profile
sofia profile wss restart

# Check status
sofia status profile wss
```

**Expected output:**
```
Name    wss
Domain  internal    internal
Auto-NAT    false
DBName  wss
Presence    enabled
Timer-T1    500
Timer-T2    4000
...
```

---

### Step 8: Verify WebRTC Profile is Running

#### Check 1: Via FusionPBX GUI

1. **Go to:** **Status → SIP Status**
2. **Look for "wss" profile**
3. **Status should be:** `RUNNING` (green)
4. **Listen IP:** `0.0.0.0:7443`

#### Check 2: Via FreeSWITCH CLI

```bash
fs_cli -x "sofia status profile wss"
```

**Expected output:**
```
Profile Name: wss
PROFILE STATE: RUNNING
...
```

#### Check 3: Check Port is Listening

```bash
# Check if port 7443 is listening
netstat -tlnp | grep 7443

# Or using ss
ss -tlnp | grep 7443

# Expected output:
# LISTEN  0  ... :::7443  ... freeswitch
```

#### Check 4: Test WebRTC Connection

You can test WebRTC connectivity using:

1. **FusionPBX WebRTC Client:**
   - Navigate to: `https://136.115.41.45/app/calls/`
   - Try to register an extension

2. **Browser Console:**
   - Open browser developer tools
   - Check for WebSocket connections to `wss://136.115.41.45:7443`

---

### Step 9: Firewall Configuration

Ensure port 7443 (WSS) is open in your firewall:

#### UFW (Uncomplicated Firewall):

```bash
sudo ufw allow 7443/tcp
sudo ufw allow 16384:32768/udp  # RTP port range
sudo ufw status
```

#### iptables:

```bash
# Allow WSS port
sudo iptables -A INPUT -p tcp --dport 7443 -j ACCEPT

# Allow RTP port range
sudo iptables -A INPUT -p udp --dport 16384:32768 -j ACCEPT

# Save rules
sudo iptables-save > /etc/iptables/rules.v4
```

#### Cloud Provider Firewall:

If using a cloud provider (AWS, GCP, Azure):
- **Add inbound rule:** TCP port 7443
- **Add inbound rule:** UDP ports 16384-32768

---

### Step 10: Configure Extensions for WebRTC

To use WebRTC, extensions need to be configured:

1. **Go to:** **Accounts → Extensions**
2. **Click on an extension** (e.g., 2001)
3. **Advanced tab → SIP Profile:**
   - Ensure it can use `wss` profile
   - Or allow both `internal` and `wss`

4. **Settings to check:**
   - **User Context:** `default` (or appropriate context)
   - **Transport:** Allow `wss` transport
   - **Codecs:** Match profile codecs (G722, PCMU, PCMA)

---

## Verification Checklist

After completing all steps, verify:

- [ ] wss profile exists in SIP Profiles list
- [ ] wss profile status is "RUNNING"
- [ ] Port 7443 is listening (check with `netstat` or `ss`)
- [ ] TLS certificate is configured and valid
- [ ] Firewall allows port 7443 (TCP) and 16384-32768 (UDP)
- [ ] External IP `136.115.41.45` is set correctly
- [ ] Codecs G722, PCMU, PCMA are configured
- [ ] ACL settings allow registrations
- [ ] Extension can register via WebRTC

---

## Troubleshooting

### Issue 1: Profile Not Appearing

**Symptom:** wss profile doesn't show in FusionPBX GUI

**Solution:**
```bash
# Check if profile exists in FreeSWITCH
fs_cli -x "sofia status"

# If it exists, it may need to be enabled in database
# Check database:
sudo -u postgres psql fusionpbx -c "SELECT * FROM v_sip_profiles WHERE sip_profile_name = 'wss';"
```

### Issue 2: Profile Won't Start

**Symptom:** wss profile shows "STOPPED" or won't start

**Check logs:**
```bash
tail -100 /var/log/freeswitch/freeswitch.log | grep -i wss
tail -100 /var/log/freeswitch/freeswitch.log | grep -i 7443
```

**Common issues:**
- Port 7443 already in use
- Invalid TLS certificate
- Missing configuration parameters

### Issue 3: Cannot Connect from Browser

**Symptom:** WebRTC client cannot connect

**Check:**
1. Browser console for WebSocket errors
2. Firewall rules
3. TLS certificate validity
4. CORS settings (if applicable)

**Test connection:**
```bash
# Test WebSocket connection
wscat -c wss://136.115.41.45:7443

# Or using curl
curl -k https://136.115.41.45:7443
```

### Issue 4: No Audio After Connection

**Symptom:** WebRTC connects but no audio

**Check:**
1. RTP port range is open in firewall
2. Codec compatibility between client and server
3. NAT traversal settings
4. Media bypass settings

---

## Complete Configuration Example

Here's a complete example of all settings for the wss profile:

```xml
<!-- This is what the configuration should look like internally -->
<profile name="wss">
  <settings>
    <param name="name" value="wss"/>
    <param name="sip-ip" value="0.0.0.0"/>
    <param name="sip-port" value="7443"/>
    <param name="tls" value="true"/>
    <param name="tls-bind-params" value="transport=wss"/>
    <param name="ext-sip-ip" value="136.115.41.45"/>
    <param name="ext-rtp-ip" value="136.115.41.45"/>
    <param name="domain" value="136.115.41.45"/>
    <param name="codec-prefs" value="G722,PCMU,PCMA"/>
    <param name="rtp-ip" value="0.0.0.0"/>
    <param name="rtp-min-port" value="16384"/>
    <param name="rtp-max-port" value="32768"/>
    <param name="local-network-acl" value="localnet.auto"/>
    <param name="apply-nat-acl" value="nat.auto"/>
    <param name="apply-inbound-acl" value="domains"/>
    <param name="apply-register-acl" value="domains"/>
    <param name="bypass-media" value="false"/>
    <param name="media-bypass" value="false"/>
  </settings>
</profile>
```

---

## Next Steps

After enabling the WebRTC profile:

1. **Test WebRTC connection** using FusionPBX's built-in client
2. **Configure extensions** to allow WebRTC registration
3. **Implement server-side bridge** (if needed for direct transfer)
4. **Update your application** to use WSS endpoint: `wss://136.115.41.45:7443`

---

## Additional Resources

- **FusionPBX Documentation:** https://docs.fusionpbx.com/
- **FreeSWITCH WebRTC Guide:** https://freeswitch.org/confluence/display/FREESWITCH/WebRTC
- **FusionPBX Forum:** https://www.fusionpbx.com/

---

**Need Help?**

If you encounter issues, check:
1. FreeSWITCH logs: `/var/log/freeswitch/freeswitch.log`
2. FusionPBX logs: `/var/log/fusionpbx/`
3. Browser console for WebSocket errors
4. Firewall rules and port accessibility

## FUSIONPBX_EXTERNAL_XML_LOCATION

# Where to Put external.xml - Important Notes

## ⚠️ IMPORTANT: Don't Manually Edit external.xml if Using FusionPBX

If you're using **FusionPBX**, the `external.xml` file is **automatically generated** from FusionPBX's database. Any manual edits will be **overwritten** when you:
- Click "Reload XML" in FusionPBX GUI
- Restart FreeSWITCH
- FusionPBX regenerates the config

## 📍 File Location (For Reference Only)

If you were to manually edit it (not recommended for FusionPBX), the file location is:

```
/etc/freeswitch/sip_profiles/external.xml
```

**On your FusionPBX server:**
```bash
# The actual file used by FreeSWITCH
/etc/freeswitch/sip_profiles/external.xml

# Your project template file (in your repo)
convonet/external.xml  # This is just a reference/template
```

## ✅ Correct Way: Configure via FusionPBX GUI

**Instead of copying the XML file, configure via FusionPBX:**

1. **Login to FusionPBX:**
   ```
   https://136.115.41.45
   ```

2. **Navigate to SIP Profile:**
   ```
   Advanced → SIP Profiles → external
   ```

3. **Edit Settings:**
   - Click on the "external" profile
   - Go to "Settings" tab
   - Find each setting from `external.xml` and update it:
     - `ext-sip-ip` → Set to `136.115.41.45`
     - `ext-rtp-ip` → Set to `136.115.41.45`
     - `sip-ip` → Set to `10.128.0.8` (internal IP)
     - `rtp-ip` → Set to `10.128.0.8` (internal IP)
     - `inbound-codec-prefs` → Set to `PCMU,PCMA`
     - `outbound-codec-prefs` → Set to `PCMU,PCMA`
     - `apply-inbound-acl` → Set to `Twilio-SIP`
     - `bypass-media` → Set to `false`
     - etc.

4. **Save and Reload:**
   - Click "Save" at the bottom
   - Go to: `Status → SIP Status`
   - Find "external" profile
   - Click "Reload XML"
   - Click "Restart"

5. **Verify:**
   ```bash
   fs_cli -x "sofia xmlstatus profile external" | grep -E "ext-sip-ip|ext-rtp-ip"
   ```

## ✅ Alternative: Update Database Directly

If the GUI doesn't work, update the database:

```bash
# SSH into FusionPBX server
ssh root@136.115.41.45

# Connect to PostgreSQL
sudo -u postgres psql fusionpbx

# Update settings (example for ext-sip-ip)
UPDATE v_sip_profile_settings sps
SET sip_profile_setting_value = '136.115.41.45',
    sip_profile_setting_enabled = true
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'ext-sip-ip';

# Repeat for other settings:
# - ext-rtp-ip → 136.115.41.45
# - inbound-codec-prefs → PCMU,PCMA
# - outbound-codec-prefs → PCMU,PCMA
# - apply-inbound-acl → Twilio-SIP
# - bypass-media → false
# - media-bypass → false

\q

# Reload FreeSWITCH
fs_cli -x "reloadxml"
fs_cli -x "sofia profile external restart"
```

## 🔍 Verify Current Settings

To see what FreeSWITCH is actually using (regardless of what's in the XML file):

```bash
fs_cli -x "sofia xmlstatus profile external"
```

This shows the actual active configuration.

## 📝 Why convonet/external.xml Exists

The `convonet/external.xml` file in your project is:
- **A template/reference** for what the configuration should look like
- **Documentation** of the required settings
- **Not meant to be copied directly** to the server if using FusionPBX

If you were setting up a **standalone FreeSWITCH** (not FusionPBX), then you would:
1. Copy `convonet/external.xml` to `/etc/freeswitch/sip_profiles/external.xml`
2. Edit it as needed
3. Reload: `fs_cli -x "reloadxml"`

But since you're using FusionPBX, always configure via the GUI or database.

## 🎯 Summary

- **File location:** `/etc/freeswitch/sip_profiles/external.xml` (on FusionPBX server)
- **Don't edit it manually** - FusionPBX will overwrite it
- **Use FusionPBX GUI** instead: `Advanced → SIP Profiles → external → Settings`
- **Or update database:** `v_sip_profile_settings` table
- **Verify:** `fs_cli -x "sofia xmlstatus profile external"`

## FUSIONPBX_FIX_603_DECLINE_CALLER_ID

# Fix SIP 603 Decline - Extension 2003 Rejecting Calls

## 🔍 Problem Identified

**Error:** `SIP 603 Decline` / `CALL_REJECTED` when extension 2003 answers

**Evidence from logs:**
```
[DEBUG] sofia.c:7493 Channel sofia/internal/2003@198.27.217.12:61342 entering state [terminated][603]
[NOTICE] sofia.c:8736 Hangup sofia/internal/2003@198.27.217.12:61342 [CS_CONSUME_MEDIA] [CALL_REJECTED]
[DEBUG] mod_sofia.c:463 sofia/internal/2001@136.115.41.45 Overriding SIP cause 480 with 603 from the other leg
```

**Root Cause:** Extension 2003's phone is explicitly rejecting the call with SIP 603. Most likely causes:
1. **Caller ID is the extension itself** (e.g., 2001 calling shows as "2001" as caller ID)
2. **Phone has auto-reject enabled** for certain caller IDs
3. **Phone settings** configured to reject calls

## 🎯 Solution 1: Fix Caller ID in FusionPBX Dialplan

The FusionPBX dialplan might be setting the caller ID to the extension number, which phones often reject. We need to set proper caller ID.

### Check Current Caller ID Settings

```bash
# Check what caller ID is being sent
tail -200 /var/log/freeswitch/freeswitch.log | grep -iE "caller.*id|effective.*caller|origination.*caller" | grep -iE "2001|2003"
```

### Fix Caller ID via Database

Check and update extension 2001's caller ID:

```bash
# Check current caller ID settings for extension 2001
sudo -u postgres psql fusionpbx -c "SELECT extension, effective_caller_id_name, effective_caller_id_number, outbound_caller_id_name, outbound_caller_id_number FROM v_extensions WHERE extension = '2001';"

# Check extension 2003 settings too
sudo -u postgres psql fusionpbx -c "SELECT extension, effective_caller_id_name, effective_caller_id_number, outbound_caller_id_name, outbound_caller_id_number FROM v_extensions WHERE extension = '2003';"
```

### Fix via FusionPBX GUI

1. **Log into FusionPBX web interface**
2. Go to **Accounts** → **Extensions**
3. Click on extension **2001** (the one making the call)
4. Find **Caller ID** section
5. Set:
   - **Effective Caller ID Name:** Something descriptive like "Extension 2001" or "Agent 2001"
   - **Effective Caller ID Number:** `2001` (can keep as extension, or set to a display number)
   - **Outbound Caller ID Name:** Same as above
   - **Outbound Caller ID Number:** `2001` or a display number
6. **Save**
7. **Reload FreeSWITCH:**
   ```bash
   fs_cli -x "reload mod_sofia"
   fs_cli -x "reloadxml"
   ```

### Fix via SQL (If needed)

```bash
# Update extension 2001's caller ID
sudo -u postgres psql fusionpbx << EOF
UPDATE v_extensions 
SET 
  effective_caller_id_name = 'Extension 2001',
  outbound_caller_id_name = 'Extension 2001'
WHERE extension = '2001';
EOF

# Reload FreeSWITCH
fs_cli -x "reload mod_sofia"
fs_cli -x "reloadxml"
```

## 🎯 Solution 2: Check Phone Settings for Extension 2003

The phone itself might have settings causing it to reject calls.

### Common Phone Settings to Check:

1. **Call Rejection / Blacklist:**
   - Check if extension 2001 is in a blacklist
   - Disable auto-reject features

2. **Call Filtering:**
   - Check if the phone has call filtering enabled
   - Verify it's not set to reject calls from specific numbers

3. **Do Not Disturb (DND):**
   - Make sure DND is disabled on extension 2003's phone

4. **Call Settings:**
   - Check if "Reject anonymous calls" is enabled (might reject if caller ID is missing)
   - Check if "Reject calls from blocked numbers" is enabled

### Test from FusionPBX CLI:

Test if FreeSWITCH can successfully call extension 2003:

```bash
# Test calling extension 2003 directly from FreeSWITCH CLI
fs_cli -x "originate {origination_caller_id_name='Test Call',origination_caller_id_number='9999'}user/2003@136.115.41.45 &echo()"
```

**If this works:** The issue is with the caller ID from extension 2001
**If this also fails:** The issue is with extension 2003's phone settings or configuration

## 🎯 Solution 3: Check Dialplan Caller ID Export

Check if the dialplan is properly exporting caller ID:

```bash
# Check dialplan for caller ID exports
grep -r "caller.*id" /usr/share/freeswitch/conf/dialplan/default/
grep -r "effective.*caller" /usr/share/freeswitch/conf/dialplan/default/
```

Or check in FusionPBX:
1. Go to **Advanced** → **Dialplans**
2. Find the dialplan for `136.115.41.45` domain
3. Look for **Actions** that set caller ID

## 🎯 Solution 4: Force Caller ID in Dialplan Action

If needed, we can force caller ID in the dialplan action. Check what action is being used for extension-to-extension calls:

```bash
# Find the dialplan context and action
grep -A 10 "bridge(user/" /usr/share/freeswitch/conf/dialplan/default/*.xml
```

In FusionPBX dialplan, modify the bridge action to include caller ID:

**Original:**
```xml
<action application="bridge" data="user/${destination_number}@${domain_name}"/>
```

**Modified (if needed):**
```xml
<action application="set" data="effective_caller_id_name=Extension ${caller_id_number}"/>
<action application="set" data="effective_caller_id_number=${caller_id_number}"/>
<action application="bridge" data="user/${destination_number}@${domain_name}"/>
```

**Note:** Be careful modifying dialplans directly - FusionPBX generates them. It's better to fix via GUI or database.

## 🔍 Diagnostic Commands

### Check What Caller ID Is Being Sent

```bash
# Enable detailed logging and make a call
fs_cli -x "sofia loglevel all 9"
fs_cli -x "console loglevel debug"

# Then make the call and check logs for caller ID
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "caller|From:|effective.*caller" | grep -iE "2001|2003"
```

### Check SIP INVITE Message

Look for the SIP INVITE message sent to extension 2003:

```bash
# Get SIP INVITE details
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "INVITE|From:|To:" | grep -iE "2003" | tail -20
```

## 📋 Quick Fix Checklist

- [ ] Check extension 2001's caller ID settings in FusionPBX
- [ ] Set proper Caller ID Name (not just number)
- [ ] Check extension 2003's phone settings for auto-reject
- [ ] Disable any blacklist or call filtering on extension 2003's phone
- [ ] Test call with different caller ID from CLI
- [ ] Verify caller ID in SIP INVITE messages
- [ ] Reload FreeSWITCH after making changes

## 🎯 Most Likely Fix

Based on the logs, the most likely issue is that **extension 2001 is calling with its extension number as caller ID**, and extension 2003's phone is rejecting it (possibly because it thinks it's calling itself, or due to phone settings).

**Quick fix:**
1. Set extension 2001's **Effective Caller ID Name** to something descriptive like "Extension 2001" in FusionPBX GUI
2. Make sure it's not just the number
3. Reload FreeSWITCH
4. Test the call again

## ✅ Verification

After making changes:

1. **Reload FreeSWITCH:**
   ```bash
   fs_cli -x "reload mod_sofia"
   fs_cli -x "reloadxml"
   ```

2. **Make a test call** from 2001 to 2003

3. **Check logs** for caller ID:
   ```bash
   tail -100 /var/log/freeswitch/freeswitch.log | grep -iE "caller|2001.*2003|603|CALL_REJECTED"
   ```

4. **Expected result:** No more 603 Decline, call should connect successfully

## FUSIONPBX_FIX_BINDING_CORRECT_METHOD

# Correct Method to Fix FreeSWITCH Binding on Google Cloud

## Why Alias IP Won't Work in GCP

**The error you saw is correct:** "Alias IP range must belong to the selected subnet IP range"

In Google Cloud:
- **Public IPs** (like `136.115.41.45`) are **NAT'd** at the network edge
- **Alias IP ranges** can only be **internal IPs** from your VPC subnet (like `10.128.0.0/20`)
- You **cannot** add a public IP as an alias IP range

**Even if you add it via `ip addr add` on the VM:**
- It won't work properly because the IP isn't actually routed to your VM
- Google Cloud handles NAT at the network edge, not on the VM interface
- FreeSWITCH still won't be able to bind to the public IP directly

## ✅ Correct Solution: Fix FreeSWITCH Configuration Only

Since we can't change the VM's network interface, we must configure FreeSWITCH properly:

### The Key: Use `ext-sip-ip` Correctly

FreeSWITCH can:
- **Bind to `0.0.0.0`** (all interfaces) - This allows external connections
- **Advertise `ext-sip-ip`** in SIP headers - This tells clients your public IP

The `sip-ip=0.0.0.0` is correct - it means "listen on all interfaces". The problem is FreeSWITCH is detecting the interface and adding `maddr=10.128.0.10`.

---

## Step-by-Step Fix (FreeSWITCH Configuration Only)

### Step 1: First, Restore FreeSWITCH to Working State

```bash
# Restore backups if FreeSWITCH isn't running
cp /etc/freeswitch/vars.xml.backup /etc/freeswitch/vars.xml
cp /etc/freeswitch/sip_profiles/wss.xml.backup /etc/freeswitch/sip_profiles/wss.xml

# Start FreeSWITCH
systemctl start freeswitch
sleep 3

# Verify it's running
systemctl status freeswitch
fs_cli -x "status"
```

### Step 2: Check Current Configuration

```bash
# Check what FreeSWITCH sees
fs_cli -x "global_getvar local_ip_v4"
fs_cli -x "sofia status profile wss" | grep -E "SIP-IP|BIND-URL"
netstat -tlnp | grep 7443
```

### Step 3: Update vars.xml Correctly

```bash
# Backup
cp /etc/freeswitch/vars.xml /etc/freeswitch/vars.xml.backup2

# Edit vars.xml
nano /etc/freeswitch/vars.xml
```

**Find or add this line (must be inside `<configuration>` tags, before `</configuration>`):**

```xml
<X-PRE-PROCESS cmd="set" data="local_ip_v4=0.0.0.0"/>
```

**Important:** 
- Must have closing `/>`
- Must be inside `<configuration>` ... `</configuration>` tags
- No duplicate entries

### Step 4: Verify vars.xml Syntax

```bash
# Check if it was added correctly
grep "local_ip_v4" /etc/freeswitch/vars.xml

# Should show something like:
# <X-PRE-PROCESS cmd="set" data="local_ip_v4=0.0.0.0"/>
```

### Step 5: Restart FreeSWITCH (Full Restart Required)

```bash
# Restart service (vars.xml is only read at startup)
systemctl restart freeswitch
sleep 5

# Check if it started
systemctl status freeswitch

# Verify the change took effect
fs_cli -x "global_getvar local_ip_v4"
# Should show: 0.0.0.0
```

### Step 6: Check Binding

```bash
# Check if binding changed
netstat -tlnp | grep 7443
# Should show: 0.0.0.0:7443 (or tcp6 with :::7443)

# Check sofia status
fs_cli -x "sofia status profile wss" | grep -E "SIP-IP|BIND-URL"
# SIP-IP should show: 0.0.0.0
# BIND-URL should NOT contain: maddr=10.128.0.10
```

---

## Alternative: If vars.xml Edit Still Doesn't Work

If updating `vars.xml` still doesn't work, try updating via the database (FusionPBX method):

### Method 1: Update via FusionPBX Database

```bash
# Check if there's a variables table
sudo -u postgres psql fusionpbx -c "\dt" | grep -i var

# If not, check system settings
sudo -u postgres psql fusionpbx -c "SELECT * FROM v_default_settings WHERE default_setting_category = 'sip' LIMIT 10;"
```

### Method 2: Force via wss.xml with Explicit Bind Parameters

Edit `/etc/freeswitch/sip_profiles/wss.xml` and ensure these are in the `<settings>` section:

```xml
<param name="sip-ip" value="0.0.0.0"/>
<param name="rtp-ip" value="0.0.0.0"/>
<param name="ext-sip-ip" value="136.115.41.45"/>
<param name="ext-rtp-ip" value="136.115.41.45"/>
<!-- Force binding without maddr -->
<param name="bind-params" value="transport=wss"/>
```

**Note:** FusionPBX may regenerate this file from the database, so also update the database settings.

---

## Testing External Connection

After fixing, test from outside the VM:

```bash
# From your local machine (not the VM):
telnet 136.115.41.45 7443
# Should connect (you'll see SSL/TLS negotiation)

# Or test with openssl
openssl s_client -connect 136.115.41.45:7443 -brief

# Or test WebSocket from browser console:
# let ws = new WebSocket('wss://136.115.41.45:7443');
```

---

## Why This Works

1. **`sip-ip=0.0.0.0`** tells FreeSWITCH to bind to all interfaces
2. **`local_ip_v4=0.0.0.0` in vars.xml** prevents FreeSWITCH from auto-detecting the interface IP
3. **`ext-sip-ip=136.115.41.45`** tells clients to connect to your public IP
4. **No `maddr` in bind-params** prevents override of the binding

The key insight: **You don't need the public IP on the interface**. FreeSWITCH binds to `0.0.0.0`, which accepts connections on all interfaces, and Google Cloud's NAT routes the public IP to your VM's internal IP.

---

## Summary

❌ **Don't try:** Adding public IP as alias (won't work in GCP)  
✅ **Do this:** Fix FreeSWITCH vars.xml and wss.xml configuration  
✅ **Key fix:** Set `local_ip_v4=0.0.0.0` in vars.xml and restart FreeSWITCH

The binding to `0.0.0.0:7443` will accept connections, and Google Cloud's NAT will route `136.115.41.45:7443` to your VM.

## FUSIONPBX_FIX_EXTENSION_CALLING

# Fix 403 Forbidden Error: Extension-to-Extension Calling

## 🔴 Problem

**Error:** `403 Forbidden` when trying to call between extensions
- Calling from: `2002@136.115.41.45`
- Calling to: `2001@1361154145` (note: domain format issue)
- Result: `403 Forbidden`

## 🔍 Root Causes of 403 Forbidden

A **403 Forbidden** error means the call is being **blocked/denied**, not a network issue. Common causes:

1. **ACL (Access Control List) blocking** - Extension doesn't have permission to make calls
2. **Wrong domain format** - Notice the called number: `2001@1361154145` (missing dots)
3. **Dialplan context mismatch** - Extension trying to call from wrong context
4. **Extension permissions** - Extension settings blocking outbound calls
5. **SIP profile ACL** - Internal profile ACL blocking calls

## ✅ Diagnostic Steps

### Step 1: Check Domain Format Issue

**Notice the error shows:** `2001@1361154145` (no dots)

**Should be:** `2001@136.115.41.45` (with dots)

This suggests the SIP client is using wrong domain format.

### Step 2: Check Extension 2002 Settings

```bash
# Check if extension 2002 exists and is enabled
sudo -u postgres psql fusionpbx -c "SELECT extension, enabled, description FROM v_extensions WHERE extension = '2002';"
```

**Via FusionPBX GUI:**
1. Login: `https://136.115.41.45`
2. Go to: `Accounts → Extensions → 2002`
3. Check:
   - **Enabled:** Should be ✅ Enabled
   - **Caller ID:** Should have valid caller ID
   - **Context:** Should be `default` or appropriate context

### Step 3: Check ACL Settings for Extension 2002

**Via FusionPBX GUI:**
1. Go to: `Accounts → Extensions → 2002`
2. Go to: **Advanced** tab
3. Check:
   - **Caller ID Inbound:** Should allow calls
   - **Caller ID Outbound:** Should allow calls
   - **Reject Caller ID:** Should be empty
   - **Accept Caller ID:** Should allow calls or be empty

### Step 4: Check Internal SIP Profile ACL

The `internal` SIP profile might have ACL blocking:

```bash
# Check internal profile ACL settings
fs_cli -x "sofia xmlstatus profile internal" | grep -i "apply.*acl"
```

**Via FusionPBX GUI:**
1. Go to: `Advanced → SIP Profiles → internal`
2. Check Settings:
   - `apply-inbound-acl` - Should be `domains` or allow extensions
   - `apply-register-acl` - Should be `domains`

### Step 5: Check Dialplan Context

```bash
# Check what context extension 2002 is in
fs_cli -x "user_data 2002@136.115.41.45 var" | grep context

# Check if extension 2001 is accessible from that context
fs_cli -x "xml_locate dialplan default extension 2001"
```

### Step 6: Check Extension Registration

```bash
# Check if extension 2002 is registered
fs_cli -x "sofia status profile internal reg" | grep "2002"

# Should show:
# user: 2002
# contact: sip:2002@...
# registered: true
```

## 🔧 Solutions

### Solution 1: Fix SIP Client Domain Configuration (Most Likely)

The SIP client for extension 2002 is using wrong domain format: `1361154145` instead of `136.115.41.45`

**Fix on the SIP phone/client:**
1. Check SIP account settings
2. Ensure **Domain/Realm** is set to: `136.115.41.45` (with dots)
3. Not: `1361154145` (no dots)
4. Re-register the phone

**Common SIP client settings:**
- **Domain:** `136.115.41.45`
- **Realm:** `136.115.41.45`
- **Proxy:** `136.115.41.45`
- **Username:** `2002`
- **Password:** (your extension password)

### Solution 2: Check Extension 2002 Call Permissions

**Via FusionPBX GUI:**
1. Go to: `Accounts → Extensions → 2002`
2. **Settings** tab:
   - **Outbound CID:** Should be set
   - **Caller ID Name:** Should be set
3. **Advanced** tab:
   - **Reject Caller ID:** (leave empty)
   - **Accept Caller ID:** (leave empty or allow all)
   - **Toll Allow:** Check if there are restrictions

### Solution 3: Check Internal Profile ACL

**Via FusionPBX GUI:**
1. Go to: `Advanced → SIP Profiles → internal`
2. Settings tab:
   - Find: `apply-inbound-acl`
   - Value should be: `domains` (not blocking)
   - Find: `apply-register-acl`
   - Value should be: `domains`

**Or via database:**
```bash
sudo -u postgres psql fusionpbx -c "
SELECT sip_profile_setting_name, sip_profile_setting_value 
FROM v_sip_profile_settings sps
JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
WHERE sp.sip_profile_name = 'internal'
AND sip_profile_setting_name LIKE '%acl%';
"
```

### Solution 4: Check Extension Call Forwarding/Blocking

**Via FusionPBX GUI:**
1. Go to: `Accounts → Extensions → 2002`
2. Check:
   - **Do Not Disturb:** Should be **OFF**
   - **Call Forward:** Check if enabled and blocking
   - **Follow Me:** Check if enabled

### Solution 5: Test Extension 2002 Can Make Calls

```bash
# Test if extension 2002 can originate calls
fs_cli -x "originate user/2002@136.115.41.45 &echo()"

# Or test calling extension 2001 from FreeSWITCH CLI
fs_cli -x "originate {origination_caller_id_number=2002,origination_caller_id_name=2002}user/2001@136.115.41.45 &echo()"
```

**If this works:** The issue is with the SIP client configuration
**If this fails:** The issue is with FusionPBX extension settings

### Solution 6: Check Dialplan Permissions

**Via FusionPBX GUI:**
1. Go to: `Dialplan → Destinations`
2. Check if extension 2002 has permission to dial extension 2001

**Or check via database:**
```bash
sudo -u postgres psql fusionpbx -c "
SELECT * FROM v_dialplan_details 
WHERE dialplan_detail_tag = 'action' 
AND dialplan_detail_data LIKE '%2001%';
"
```

### Solution 7: Enable Call Logging

Enable detailed logging to see why 403 is happening:

```bash
# Enable SIP debugging
fs_cli -x "sofia loglevel all 9"

# Enable console logging
fs_cli -x "console loglevel debug"

# Watch logs while attempting call
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "2002|2001|403|forbidden|deny|acl"
```

**Look for:**
- ACL deny messages
- Authentication failures
- Context/permission errors

## 🎯 Most Likely Fix

Based on the error showing `2001@1361154145` (wrong domain format), **the most likely issue is:**

1. **SIP client domain misconfiguration** - Client is using `1361154145` instead of `136.115.41.45`
2. **Fix:** Update SIP client settings to use correct domain format with dots

## 🔍 Quick Verification Checklist

Run through these in order:

- [ ] **Domain format:** SIP client uses `136.115.41.45` (with dots), not `1361154145`
- [ ] **Extension enabled:** Extension 2002 is enabled in FusionPBX
- [ ] **Extension registered:** Extension 2002 shows as registered
- [ ] **Internal profile ACL:** `apply-inbound-acl` is set to `domains` (not blocking)
- [ ] **Extension permissions:** Extension 2002 has outbound call permissions
- [ ] **Do Not Disturb:** DND is OFF for extension 2002
- [ ] **Call blocking:** No call forwarding or blocking enabled
- [ ] **Test from CLI:** Test if FreeSWITCH CLI can make the call successfully

## 📝 Expected Working Configuration

### Extension 2002 SIP Client Settings:
```
Domain/Realm: 136.115.41.45  ← Must have dots!
Username: 2002
Password: (your extension password)
Proxy: 136.115.41.45 (optional)
Transport: UDP (or WSS if using WebRTC)
Port: 5060 (or 7443 for WSS)
```

### FusionPBX Extension 2002 Settings:
```
Extension: 2002
Enabled: ✅ Yes
Context: default
Domain: 136.115.41.45
Do Not Disturb: ❌ No
Call Forward: (disabled or configured correctly)
```

### Internal SIP Profile ACL:
```
apply-inbound-acl: domains
apply-register-acl: domains
```

## 🐛 Still Getting 403?

If you still get 403 after checking everything:

1. **Enable detailed logging** (Solution 7 above)
2. **Attempt the call again**
3. **Check logs for specific deny/block reason**
4. **Look for ACL entries blocking the call**
5. **Check if there's a custom dialplan blocking calls**

Share the log output and I can help identify the specific blocking rule.

## FUSIONPBX_FIX_USER_NOT_REGISTERED

# Fix USER_NOT_REGISTERED Error - Extension 2002

## 🔍 Problem Identified

**Error:** `Cannot create outgoing channel of type [user] cause: [USER_NOT_REGISTERED]`

**Root Cause:** Extension 2002 exists in the database but is **not registered** with FreeSWITCH.

**Evidence:**
- ✅ Extension 2002 exists in database: `enabled = true`, `user_context = default`
- ❌ Extension 2002 NOT registered: `sofia status profile internal reg` shows nothing for 2002

## 🎯 Solution: Register Extension 2002

### Step 1: Verify Current Registration Status

```bash
# Check all registered extensions
fs_cli -x "sofia status profile internal reg"

# Check specifically for extension 2002 (should show nothing)
fs_cli -x "sofia status profile internal reg" | grep "2002"
```

### Step 2: Check Extension 2002 Configuration

```bash
# Verify extension exists and is enabled
sudo -u postgres psql fusionpbx -c "SELECT extension, enabled, user_context, password, auth_acl FROM v_extensions WHERE extension = '2002';"
```

### Step 3: Check SIP Profile Settings

Make sure the `internal` SIP profile is running and configured correctly:

```bash
# Check if internal profile is running
fs_cli -x "sofia status"

# Check internal profile details
fs_cli -x "sofia status profile internal"
```

### Step 4: Configure SIP Phone for Extension 2002

Your SIP phone/softphone needs to register with FusionPBX. Use these settings:

#### SIP Account Settings:
- **SIP Server / Proxy:** `136.115.41.45` (or your FusionPBX IP)
- **SIP Port:** `5060` (default)
- **Username / Extension:** `2002`
- **Password:** (Check in FusionPBX GUI or database)
- **Domain / Realm:** `136.115.41.45`
- **Transport:** `UDP` (or `TCP` if configured)
- **Register:** `Yes` / `Enabled`

#### Get Extension 2002 Password:

**Option A: FusionPBX GUI**
1. Log into FusionPBX web interface
2. Go to **Accounts** → **Extensions**
3. Find extension **2002**
4. Check the **Password** field

**Option B: Database Query**
```bash
sudo -u postgres psql fusionpbx -c "SELECT extension, password FROM v_extensions WHERE extension = '2002';"
```

**Option C: Check Extension Details**
```bash
sudo -u postgres psql fusionpbx -c "SELECT extension, password, auth_acl, effective_caller_id_name, effective_caller_id_number FROM v_extensions WHERE extension = '2002';"
```

### Step 5: Verify Registration

After configuring the SIP phone, wait a few seconds and check:

```bash
# Check if extension 2002 is now registered
fs_cli -x "sofia status profile internal reg" | grep -A 5 "2002"

# Should show something like:
# reg_user=2002@136.115.41.45
# Contact: <sip:2002@192.168.x.x:5060>
```

### Step 6: Test the Call Again

Once extension 2002 is registered, try calling from extension 2001 again.

## 🔍 Troubleshooting Registration Issues

### Issue 1: SIP Phone Not Registering

**Check 1: Firewall Rules**
```bash
# Make sure UDP port 5060 is open
sudo ufw status | grep 5060

# If not, open it
sudo ufw allow 5060/udp
```

**Check 2: ACL Settings**
```bash
# Check if internal profile has proper ACL
fs_cli -x "sofia status profile internal" | grep -i acl

# Check ACL in database
sudo -u postgres psql fusionpbx -c "SELECT * FROM v_access_control_nodes WHERE node_type = 'allow' AND node_cidr LIKE '%192.168%' OR node_cidr LIKE '%10.%';"
```

**Check 3: Registration Logs**
```bash
# Watch registration attempts in real-time
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "register|2002|auth"
```

### Issue 2: Wrong Password

If the password is incorrect, you'll see authentication errors:

```bash
# Check for auth failures
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "401|403|unauthorized|2002"
```

**Fix:** Update the password in FusionPBX GUI or reset it.

### Issue 3: Wrong Domain/Context

Make sure extension 2002 is using the correct domain:

```bash
# Check extension domain and context
sudo -u postgres psql fusionpbx -c "SELECT extension, domain_name, user_context FROM v_extensions WHERE extension = '2002';"

# Should match your SIP profile domain
fs_cli -x "sofia status profile internal" | grep "Domain"
```

### Issue 4: SIP Profile Not Accepting Registrations

Check if the internal profile has `apply-register-acl` set correctly:

```bash
# Check internal profile ACL settings
fs_cli -x "sofia xmlstatus profile internal" | grep -i "apply.*acl"
```

In FusionPBX:
1. Go to **Advanced** → **SIP Profiles**
2. Click on **internal**
3. Check **Apply Register ACL** - should be set to allow your network
4. Check **Apply Inbound ACL** - should allow registrations

## 📋 Quick Registration Test

Test if extension 2002 can register by manually checking registration:

```bash
# Force a registration check
fs_cli -x "sofia status profile internal reg 2002@136.115.41.45"

# Check all registrations
fs_cli -x "sofia status profile internal reg"
```

## 🎯 Expected Result

After extension 2002 registers successfully:

1. **Registration Check:**
   ```bash
   fs_cli -x "sofia status profile internal reg" | grep "2002"
   ```
   Should show:
   ```
   reg_user=2002@136.115.41.45
   ```

2. **Call Test:**
   - Call from extension 2001 to 2002 should work
   - No more `USER_NOT_REGISTERED` errors

## 🔧 Common SIP Phone Configuration Examples

### Grandstream Phones:
- **Account:** 2002
- **SIP Server:** 136.115.41.45
- **SIP User ID:** 2002
- **Authenticate ID:** 2002
- **Authenticate Password:** [password from FusionPBX]
- **Name:** Extension 2002

### Softphones (X-Lite, Zoiper, etc.):
- **Display Name:** 2002
- **User Name:** 2002
- **Password:** [password from FusionPBX]
- **Domain:** 136.115.41.45
- **Server / Proxy:** 136.115.41.45

### WebRTC Clients:
- **SIP URI:** `2002@136.115.41.45`
- **Password:** [password from FusionPBX]
- **Server:** `wss://136.115.41.45:7443` (for secure WebSocket)

## ✅ Verification Checklist

- [ ] Extension 2002 exists in database and is enabled
- [ ] Extension 2002 password is correct
- [ ] SIP phone is configured with correct settings
- [ ] SIP phone shows "Registered" status
- [ ] `fs_cli -x "sofia status profile internal reg"` shows 2002
- [ ] Firewall allows UDP port 5060
- [ ] Internal SIP profile ACL allows registration
- [ ] Call from 2001 to 2002 works without errors

## 🎯 Next Steps

1. **Configure SIP phone** for extension 2002 with correct credentials
2. **Verify registration** using `fs_cli` command
3. **Test call** from extension 2001 to 2002
4. If still not working, check the troubleshooting section above

## FUSIONPBX_FIX_WSS_PORT_MISMATCH

# Fix WSS Profile Port Mismatch

## Problem

The WSS profile shows:
- **XML config:** `sip-port` = `7443`
- **TLS-BIND-URL:** Port `5061` (not 7443!)
- **Port 7443 is listening** but WebSocket connections fail

The TLS-BIND-URL should show port 7443, not 5061.

---

## Root Cause

FreeSWITCH is binding WebSocket to port 5061 (TLS port) instead of 7443 (WSS port). This is because the TLS configuration might be overriding the sip-port setting.

---

## Solution: Fix TLS Certificate Configuration

The WSS profile needs TLS certificates configured properly. Check if they exist:

```bash
# Check TLS certificates
ls -la /etc/freeswitch/tls/*.pem
ls -la /etc/freeswitch/tls/wss.pem

# Check certificate content
openssl x509 -in /etc/freeswitch/tls/wss.pem -text -noout | head -20
```

---

## Fix: Update WSS Profile to Use Port 7443 for TLS/WSS

The issue is that FreeSWITCH might be using the default TLS port (5061) instead of the configured WSS port (7443).

### Step 1: Verify TLS Certificate Configuration in XML

```bash
# Check if TLS certificates are in wss.xml
grep -i "tls-cert\|tls-key\|tls-dir" /etc/freeswitch/sip_profiles/wss.xml
```

If missing, add them to the XML or database.

### Step 2: Update Database Settings

```bash
PROFILE_UUID=$(sudo -u postgres psql fusionpbx -t -c "SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'wss';" | xargs)

# Ensure TLS certificate paths are set
sudo -u postgres psql fusionpbx << EOF
-- Add TLS certificate directory if missing
INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'tls-cert-dir', '\$\${base_dir}/conf/tls', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'tls-cert-dir');

-- Add TLS certificate file if missing
INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'tls-cert-file', '\$\${base_dir}/conf/tls/wss.pem', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'tls-cert-file');

-- Add TLS key file if missing
INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'tls-key-file', '\$\${base_dir}/conf/tls/wss.pem', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'tls-key-file');

-- Ensure sip-port is 7443
UPDATE v_sip_profile_settings 
SET sip_profile_setting_value = '7443' 
WHERE sip_profile_uuid = '$PROFILE_UUID' 
AND sip_profile_setting_name = 'sip-port';
EOF
```

### Step 3: Add TLS Certificates to XML Manually

If the database method doesn't work, add directly to XML:

```bash
# Backup
cp /etc/freeswitch/sip_profiles/wss.xml /etc/freeswitch/sip_profiles/wss.xml.backup

# Add TLS certificate parameters before closing </settings> tag
sed -i '/<\/settings>/i\
                <param name="tls-cert-dir" value="$${base_dir}/conf/tls"/>\
                <param name="tls-cert-file" value="$${base_dir}/conf/tls/wss.pem"/>\
                <param name="tls-key-file" value="$${base_dir}/conf/tls/wss.pem"/>' /etc/freeswitch/sip_profiles/wss.xml

# Set permissions
FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
FS_USER=${FS_USER:-www-data}
chown $FS_USER:$FS_USER /etc/freeswitch/sip_profiles/wss.xml
```

### Step 4: Restart Profile

```bash
fs_cli -x "reloadxml"
fs_cli -x "sofia profile wss stop"
sleep 2
fs_cli -x "sofia profile wss start"
sleep 3

# Verify
fs_cli -x "sofia status profile wss" | grep -E "TLS-BIND-URL|sip-port"
```

**Expected:** TLS-BIND-URL should show port 7443, not 5061.

---

## Alternative: Test with Port 5061

If the above doesn't work immediately, try connecting to port 5061 instead:

```javascript
// In browser console
const socket = new JsSIP.WebSocketInterface('wss://136.115.41.45:5061');
const ua = new JsSIP.UA({
    sockets: [socket],
    uri: 'sip:test@136.115.41.45',
    register: false
});
ua.on('connected', () => console.log('Connected!'));
ua.start();
```

But ideally, we want port 7443 to work.

---

## Complete Fix Script

```bash
#!/bin/bash
# Fix WSS profile to use port 7443 correctly

PROFILE_UUID=$(sudo -u postgres psql fusionpbx -t -c "SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'wss';" | xargs)

echo "Profile UUID: $PROFILE_UUID"

# Add TLS certificate settings
sudo -u postgres psql fusionpbx << EOF
INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'tls-cert-dir', '\$\${base_dir}/conf/tls', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'tls-cert-dir');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'tls-cert-file', '\$\${base_dir}/conf/tls/wss.pem', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'tls-cert-file');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'tls-key-file', '\$\${base_dir}/conf/tls/wss.pem', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'tls-key-file');
EOF

# Also add to XML
WSS_XML="/etc/freeswitch/sip_profiles/wss.xml"
cp "$WSS_XML" "$WSS_XML.backup.$(date +%Y%m%d_%H%M%S)"

if ! grep -q "tls-cert-dir" "$WSS_XML"; then
    sed -i '/<\/settings>/i\
                <param name="tls-cert-dir" value="$${base_dir}/conf/tls"/>\
                <param name="tls-cert-file" value="$${base_dir}/conf/tls/wss.pem"/>\
                <param name="tls-key-file" value="$${base_dir}/conf/tls/wss.pem"/>' "$WSS_XML"
fi

# Set permissions
FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
FS_USER=${FS_USER:-www-data}
chown $FS_USER:$FS_USER "$WSS_XML"

# Restart
fs_cli -x "reloadxml"
fs_cli -x "sofia profile wss stop"
sleep 2
fs_cli -x "sofia profile wss start"
sleep 3

# Verify
echo ""
echo "=== Verification ==="
fs_cli -x "sofia status profile wss" | grep -E "TLS-BIND-URL|sip-port"
```

---

## After Fix

After applying the fix, check:

```bash
# Should show port 7443 in TLS-BIND-URL
fs_cli -x "sofia status profile wss" | grep "TLS-BIND-URL"

# Should show port 7443 listening
ss -tlnp | grep 7443
```

Then test WebSocket connection again from browser.


## FUSIONPBX_FORCE_BIND_0.0.0.0

# Force FreeSWITCH WSS Profile to Bind to 0.0.0.0 on Google Cloud VM

## Problem

Even with `sip-ip=0.0.0.0` in the XML, FreeSWITCH is binding to the internal IP (`10.128.0.10:7443`) instead of `0.0.0.0:7443`. This is common on Google Cloud VMs due to interface auto-detection.

## Root Cause

FreeSWITCH is detecting the network interface and using `maddr` (multicast address) parameter, which forces binding to the detected interface IP (`10.128.0.10`) instead of honoring `sip-ip=0.0.0.0`.

**From `sofia status`:**
```
SIP-IP: 10.128.0.10
BIND-URL: sip:mod_sofia@136.115.41.45:7443;maddr=10.128.0.10
```

The `maddr=10.128.0.10` parameter is overriding the `sip-ip=0.0.0.0` setting.

---

## Solution 1: Disable maddr in FreeSWITCH Global Config (Recommended)

FreeSWITCH has a global setting to disable `maddr` auto-detection:

### Step 1: Check FreeSWITCH Global Variables

```bash
fs_cli -x "global_getvar local_ip_v4"
fs_cli -x "global_getvar external_ip"
fs_cli -x "global_getvar local_ip"
```

### Step 2: Set Global Variables to Force 0.0.0.0

Edit the FreeSWITCH `vars.xml` to prevent interface auto-detection:

```bash
# Find FreeSWITCH vars.xml location
fs_cli -x "global_getvar conf_dir"
# Usually: /etc/freeswitch

# Backup
cp /etc/freeswitch/vars.xml /etc/freeswitch/vars.xml.backup

# Edit vars.xml
nano /etc/freeswitch/vars.xml
```

Add or modify these variables:

```xml
<!-- Disable maddr auto-detection -->
<X-PRE-PROCESS cmd="set" data="local_ip_v4=0.0.0.0"/>
<X-PRE-PROCESS cmd="set" data="external_ip_v4=136.115.41.45"/>
<X-PRE-PROCESS cmd="set" data="rtp_ip=0.0.0.0"/>
```

**OR** if these variables are already set, comment them out or change to:

```xml
<!-- Force bind to all interfaces -->
<X-PRE-PROCESS cmd="set" data="local_ip_v4=0.0.0.0"/>
```

### Step 3: Add Profile-Specific Override

Add explicit binding parameters to the WSS profile XML:

```bash
nano /etc/freeswitch/sip_profiles/wss.xml
```

Add these parameters **inside `<settings>` section**:

```xml
<!-- Force binding to 0.0.0.0, disable maddr -->
<param name="sip-ip" value="0.0.0.0"/>
<param name="rtp-ip" value="0.0.0.0"/>
<param name="bind-params" value="transport=wss;maddr="/>
<param name="disable-maddr" value="true"/>
```

The key is `bind-params` with empty `maddr=` to override auto-detection.

### Step 4: Restart FreeSWITCH (Not Just Profile)

```bash
# Restart the entire FreeSWITCH service to reload vars.xml
systemctl restart freeswitch

# Wait a moment
sleep 5

# Check if profile is running
fs_cli -x "sofia status profile wss"

# Verify binding
netstat -tlnp | grep 7443
```

---

## Solution 2: Use sofia.conf.xml to Override

FreeSWITCH may have a `sofia.conf.xml` that controls global Sofia settings:

```bash
# Check if sofia.conf.xml exists
ls -la /etc/freeswitch/autoload_configs/sofia.conf.xml

# If it exists, edit it
nano /etc/freeswitch/autoload_configs/sofia.conf.xml
```

Add or modify:

```xml
<configuration name="sofia.conf" description="Sofia Configuration">
  <global_settings>
    <param name="auto-maddr" value="false"/>
    <param name="force-bind" value="true"/>
  </global_settings>
</configuration>
```

---

## Solution 3: VM-Level Network Configuration (Safe)

**This won't break existing setup** - it only affects how FreeSWITCH sees the network.

### Option A: Create Alias Interface (Recommended for Google Cloud)

On Google Cloud VMs, you can configure the network interface to advertise the public IP:

```bash
# Check current network configuration
ip addr show
ip route show

# On Google Cloud, the interface is typically 'ens4'
# Add IP alias (this is safe and doesn't break existing setup)
sudo ip addr add 136.115.41.45/32 dev ens4

# Make it persistent (add to network configuration)
# Edit network config (Debian/Ubuntu)
nano /etc/netplan/50-cloud-init.yaml
# Or if using ifupdown
nano /etc/network/interfaces
```

**For Debian/Ubuntu with netplan:**

```yaml
network:
  version: 2
  ethernets:
    ens4:
      dhcp4: true
      addresses:
        - 136.115.41.45/32  # Add public IP as alias
```

**For ifupdown (`/etc/network/interfaces`):**

```
auto ens4
iface ens4 inet dhcp

auto ens4:0
iface ens4:0 inet static
  address 136.115.41.45
  netmask 255.255.255.255
```

**Note:** This adds the public IP as an alias on the interface. It's safe because:
- ✅ Doesn't remove existing configuration
- ✅ Doesn't break DHCP
- ✅ Only adds an additional IP address
- ✅ Can be removed easily if needed

### Option B: Configure IP Forwarding (Usually Already Enabled)

```bash
# Check if IP forwarding is enabled
sysctl net.ipv4.ip_forward

# Enable if not (usually already enabled on Google Cloud)
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

---

## Solution 4: Use External SIP IP Binding Parameter

Add explicit external binding parameters that override interface detection:

```bash
nano /etc/freeswitch/sip_profiles/wss.xml
```

In the `<settings>` section, ensure you have:

```xml
<param name="sip-ip" value="0.0.0.0"/>
<param name="ext-sip-ip" value="136.115.41.45"/>
<param name="rtp-ip" value="0.0.0.0"/>
<param name="ext-rtp-ip" value="136.115.41.45"/>
<!-- Force binding without maddr -->
<param name="bind-params" value="transport=wss"/>
<!-- Disable interface auto-detection -->
<param name="force-register-domain" value="136.115.41.45"/>
```

The key is having `bind-params` without `maddr` parameter.

---

## Solution 5: Modify sofia.c to Disable maddr (Advanced)

If all else fails, you may need to patch FreeSWITCH or use a workaround:

### Workaround: Bind to Public IP Directly

Instead of `0.0.0.0`, try binding directly to the public IP:

```xml
<param name="sip-ip" value="136.115.41.45"/>
```

However, this may cause issues if the public IP isn't actually assigned to the interface.

**Better approach:** Use the alias interface method from Solution 3.

---

## Recommended Approach: Combined Solution

**Step 1:** Add IP alias (Solution 3A) - Safe and won't break existing setup
**Step 2:** Update vars.xml (Solution 1) - Force FreeSWITCH to use 0.0.0.0
**Step 3:** Update wss.xml with bind-params override (Solution 4)
**Step 4:** Restart FreeSWITCH service (not just profile)

### Complete Script:

```bash
#!/bin/bash

echo "=== Step 1: Add Public IP Alias to Interface ==="
# Get interface name (usually ens4 on Google Cloud)
INTERFACE=$(ip route | grep default | awk '{print $5}' | head -1)
echo "Interface: $INTERFACE"

# Add IP alias
sudo ip addr add 136.115.41.45/32 dev $INTERFACE 2>/dev/null || echo "IP alias may already exist"

# Make persistent (netplan - Debian/Ubuntu)
if [ -d /etc/netplan ]; then
    echo "Configuring netplan..."
    # Backup
    sudo cp /etc/netplan/50-cloud-init.yaml /etc/netplan/50-cloud-init.yaml.backup
    # Add to netplan (you'll need to edit manually or use a script)
    echo "⚠️  Please manually edit /etc/netplan/50-cloud-init.yaml to add:"
    echo "    addresses:"
    echo "      - 136.115.41.45/32"
fi

echo ""
echo "=== Step 2: Update FreeSWITCH vars.xml ==="
VARS_XML="/etc/freeswitch/vars.xml"
sudo cp $VARS_XML $VARS_XML.backup

# Add or modify local_ip_v4
sudo sed -i 's/<X-PRE-PROCESS cmd="set" data="local_ip_v4=[^"]*"\/>/<X-PRE-PROCESS cmd="set" data="local_ip_v4=0.0.0.0"\/>/' $VARS_XML

# If not found, add it
if ! grep -q 'local_ip_v4=0.0.0.0' $VARS_XML; then
    sudo sed -i '/<\/X-PRE-PROCESS>/a <X-PRE-PROCESS cmd="set" data="local_ip_v4=0.0.0.0"/>' $VARS_XML
fi

echo ""
echo "=== Step 3: Update WSS Profile XML ==="
WSS_XML="/etc/freeswitch/sip_profiles/wss.xml"
sudo cp $WSS_XML $WSS_XML.backup

# Update bind-params to remove maddr
sudo sed -i 's/<param name="bind-params" value="[^"]*"\/>/<param name="bind-params" value="transport=wss"\/>/' $WSS_XML

# If bind-params doesn't exist, add it
if ! grep -q 'bind-params' $WSS_XML; then
    sudo sed -i '/<param name="tls-bind-params"/a\                <param name="bind-params" value="transport=wss"/>' $WSS_XML
fi

echo ""
echo "=== Step 4: Restart FreeSWITCH ==="
sudo systemctl restart freeswitch
sleep 5

echo ""
echo "=== Verification ==="
echo "Checking binding..."
netstat -tlnp | grep 7443
echo ""
echo "Checking profile status..."
fs_cli -x "sofia status profile wss" | grep -E "SIP-IP|BIND-URL"

echo ""
echo "=== Done ==="
```

---

## Testing After Fix

```bash
# 1. Check binding
netstat -tlnp | grep 7443
# Should show: 0.0.0.0:7443

# 2. Check sofia status
fs_cli -x "sofia status profile wss" | grep "SIP-IP"
# Should show: SIP-IP: 0.0.0.0 (not 10.128.0.10)

# 3. Check BIND-URL (should NOT have maddr)
fs_cli -x "sofia status profile wss" | grep "BIND-URL"
# Should NOT contain: maddr=10.128.0.10

# 4. Test external connection
# From your local machine (not the VM):
telnet 136.115.41.45 7443
# Should connect
```

---

## Why This Happens on Google Cloud

Google Cloud VMs have:
- **Internal IP:** `10.128.0.10` (assigned to interface)
- **Public IP:** `136.115.41.45` (NAT'd, not on interface)

FreeSWITCH detects the interface IP (`10.128.0.10`) and uses it for `maddr`, which overrides `sip-ip=0.0.0.0`.

**Solutions work by:**
1. ✅ Adding public IP as alias (makes it available on interface)
2. ✅ Disabling `maddr` auto-detection (forces FreeSWITCH to ignore interface)
3. ✅ Setting global vars to 0.0.0.0 (overrides detection)

---

## Rollback (If Something Breaks)

```bash
# Restore backups
sudo cp /etc/freeswitch/vars.xml.backup /etc/freeswitch/vars.xml
sudo cp /etc/freeswitch/sip_profiles/wss.xml.backup /etc/freeswitch/sip_profiles/wss.xml

# Remove IP alias (if added)
sudo ip addr del 136.115.41.45/32 dev ens4

# Restart FreeSWITCH
sudo systemctl restart freeswitch
```

All changes are reversible and won't break your existing setup.

## FUSIONPBX_FREESWITCH_RECOVERY

# FreeSWITCH Service Recovery Guide

## Immediate Recovery Steps

If FreeSWITCH failed to start after configuration changes:

### Step 1: Check the Error

```bash
# Check systemd status
systemctl status freeswitch.service

# Check detailed logs
journalctl -xeu freeswitch.service | tail -50

# Check FreeSWITCH logs
tail -100 /var/log/freeswitch/freeswitch.log
```

### Step 2: Restore Backups (If Needed)

```bash
# Restore vars.xml from backup
cp /etc/freeswitch/vars.xml.backup /etc/freeswitch/vars.xml

# Restore wss.xml from backup
cp /etc/freeswitch/sip_profiles/wss.xml.backup /etc/freeswitch/sip_profiles/wss.xml

# Try starting again
systemctl start freeswitch
systemctl status freeswitch
```

### Step 3: Verify XML Syntax

If FreeSWITCH still won't start, check for XML syntax errors:

```bash
# Check vars.xml syntax (if xmllint is installed)
xmllint --noout /etc/freeswitch/vars.xml 2>&1 || echo "xmllint not installed, checking manually"

# Check wss.xml syntax
xmllint --noout /etc/freeswitch/sip_profiles/wss.xml 2>&1 || echo "Checking manually"
```

### Step 4: Check for Common Issues

```bash
# Check if vars.xml has proper XML structure
grep -A 5 "local_ip_v4" /etc/freeswitch/vars.xml

# Check if wss.xml has proper XML structure
grep -A 5 "bind-params" /etc/freeswitch/sip_profiles/wss.xml
```

---

## Safe Configuration Method

Instead of editing files directly, use a safer approach:

### Method 1: Check What Was Added to vars.xml

```bash
# View the vars.xml file to see what was added
cat /etc/freeswitch/vars.xml | grep -A 2 -B 2 "local_ip_v4"
```

**Common issues:**
- Missing closing tag `/>`
- Incorrect XML structure
- Duplicate entries

### Method 2: Manual Edit with Proper XML Structure

```bash
# Edit vars.xml safely
nano /etc/freeswitch/vars.xml
```

**Look for the `<X-PRE-PROCESS>` section and ensure:**
1. Each `<X-PRE-PROCESS>` line is properly closed with `/>`
2. It's inside the `<configuration>` tags
3. No duplicate `local_ip_v4` entries

**Correct format:**
```xml
<X-PRE-PROCESS cmd="set" data="local_ip_v4=0.0.0.0"/>
```

**Incorrect formats:**
```xml
<X-PRE-PROCESS cmd="set" data="local_ip_v4=0.0.0.0">  <!-- Missing closing /> -->
<X-PRE-PROCESS cmd="set" data="local_ip_v4=0.0.0.0"></X-PRE-PROCESS>  <!-- Wrong -->
```

---

## Alternative: Update vars.xml Using Database (Safer)

If FusionPBX is managing vars.xml, update via database instead:

```bash
# Check if there's a database table for variables
sudo -u postgres psql fusionpbx -c "\dt" | grep -i var
```

Or update vars.xml more carefully:

```bash
# Find the exact location in vars.xml
grep -n "local_ip_v4\|</configuration>" /etc/freeswitch/vars.xml

# Edit manually with care
nano /etc/freeswitch/vars.xml
```

---

## Quick Fix Script

```bash
#!/bin/bash
# Quick recovery and safe fix

echo "=== Step 1: Restore Backups ==="
cp /etc/freeswitch/vars.xml.backup /etc/freeswitch/vars.xml
cp /etc/freeswitch/sip_profiles/wss.xml.backup /etc/freeswitch/sip_profiles/wss.xml

echo "=== Step 2: Start FreeSWITCH ==="
systemctl start freeswitch
sleep 3

if systemctl is-active --quiet freeswitch; then
    echo "✅ FreeSWITCH started successfully"
    echo ""
    echo "Now applying safe configuration changes..."
    
    # Safe vars.xml update
    echo ""
    echo "=== Step 3: Safe vars.xml Update ==="
    # Check if local_ip_v4 exists
    if grep -q 'local_ip_v4=' /etc/freeswitch/vars.xml; then
        # Update existing
        sed -i 's/<X-PRE-PROCESS cmd="set" data="local_ip_v4=[^"]*"\/>/<X-PRE-PROCESS cmd="set" data="local_ip_v4=0.0.0.0"\/>/' /etc/freeswitch/vars.xml
    else
        # Add before </configuration> tag
        sed -i 's|</configuration>|<X-PRE-PROCESS cmd="set" data="local_ip_v4=0.0.0.0"/>\n</configuration>|' /etc/freeswitch/vars.xml
    fi
    
    # Verify XML is still valid (basic check)
    if grep -q '<X-PRE-PROCESS cmd="set" data="local_ip_v4=0.0.0.0"/>' /etc/freeswitch/vars.xml; then
        echo "✅ vars.xml updated successfully"
        
        # Restart to apply
        echo ""
        echo "=== Step 4: Restart FreeSWITCH ==="
        systemctl restart freeswitch
        sleep 5
        
        if systemctl is-active --quiet freeswitch; then
            echo "✅ FreeSWITCH restarted with new config"
            echo ""
            echo "=== Verification ==="
            fs_cli -x "global_getvar local_ip_v4"
            netstat -tlnp | grep 7443
        else
            echo "❌ FreeSWITCH failed to restart after vars.xml change"
            echo "Restoring backup..."
            cp /etc/freeswitch/vars.xml.backup /etc/freeswitch/vars.xml
            systemctl restart freeswitch
        fi
    else
        echo "❌ Failed to update vars.xml correctly"
    fi
else
    echo "❌ FreeSWITCH failed to start even with backups restored"
    echo ""
    echo "=== Diagnostic Information ==="
    systemctl status freeswitch.service
    echo ""
    echo "=== Recent Logs ==="
    journalctl -xeu freeswitch.service | tail -30
fi
```

---

## Manual Recovery Steps

If the script doesn't work:

1. **Restore backups:**
   ```bash
   cp /etc/freeswitch/vars.xml.backup /etc/freeswitch/vars.xml
   cp /etc/freeswitch/sip_profiles/wss.xml.backup /etc/freeswitch/sip_profiles/wss.xml
   ```

2. **Start FreeSWITCH:**
   ```bash
   systemctl start freeswitch
   ```

3. **Verify it's running:**
   ```bash
   systemctl status freeswitch
   fs_cli -x "status"
   ```

4. **Check what went wrong:**
   ```bash
   # Compare original vs modified
   diff /etc/freeswitch/vars.xml.backup /etc/freeswitch/vars.xml
   ```

5. **Apply changes more carefully:**
   - Edit vars.xml manually
   - Check XML syntax after each change
   - Test starting FreeSWITCH after each change

## FUSIONPBX_GET_CALL_DROP_LOGS

# Get FusionPBX Logs for Call Drops When Answering

## 🔍 Problem
- ✅ Call dials and rings (registration working)
- ❌ Call drops immediately when answered

## 📋 Quick Commands to Get Logs

### Method 1: Real-Time Monitoring (Recommended)

Enable maximum logging and watch in real-time, then make the call:

```bash
# Enable maximum logging
fs_cli -x "sofia loglevel all 9"
fs_cli -x "console loglevel debug"

# Watch logs in real-time - make the call now!
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "2001|2003|answer|bridge|media|rtp|codec|hangup|486|603|decline|reject|failed"
```

### Method 2: Capture Full Call Flow

Get logs for the specific call after it happens:

```bash
# Get recent logs with extensions 2001 and 2003
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "2001|2003" | tail -100

# Get logs with answer/bridge/hangup events
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "answer|bridge|hangup|2001|2003" | tail -100
```

### Method 3: Get Call-Specific Logs by Call UUID

1. First, get the call UUID from recent logs:
```bash
# Find the most recent call UUID involving 2001 and 2003
tail -200 /var/log/freeswitch/freeswitch.log | grep -E "New Channel.*2001|New Channel.*2003" | tail -1
```

2. Then get all logs for that call:
```bash
# Replace CALL_UUID with the actual UUID from step 1
grep "CALL_UUID" /var/log/freeswitch/freeswitch.log | tail -200
```

### Method 4: Get Logs with Context (Before/After Answer)

Get logs showing what happens right before and after answering:

```bash
# Get logs with 5 lines before and after matches
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "2001|2003" -A 5 -B 5 | tail -150

# Focus on answer/bridge events
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "answer|bridge|hangup" -A 10 -B 10 | grep -iE "2001|2003" | tail -100
```

## 🎯 Specific Log Searches

### 1. Look for Answer Events

```bash
# Look for answer/bridge events
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "ANSWER|CHANNEL_ANSWER|bridge.*2003" | tail -30
```

### 2. Look for Media/RTP Issues

```bash
# Look for RTP and media negotiation issues
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "rtp|media|codec|sdp|ice" | grep -iE "2001|2003" | tail -50
```

### 3. Look for Hangup/Call End Reasons

```bash
# Look for hangup causes
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "hangup|HANGUP|terminated|NORMAL|CALL_REJECTED|486|603" | grep -iE "2001|2003" | tail -30
```

### 4. Look for SIP Response Codes

```bash
# Look for SIP error codes
tail -500 /var/log/freeswitch/freeswitch.log | grep -E "SIP/2.0 [4-6][0-9][0-9]|^[0-9]{3} " | grep -iE "2001|2003" | tail -30
```

### 5. Look for Bridge Failures

```bash
# Look for bridge or media bridge failures
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "bridge.*fail|media.*fail|unable.*bridge" | grep -iE "2001|2003" | tail -30
```

## 📊 Complete Diagnostic Command

Run this to capture everything in real-time:

```bash
# Step 1: Clear previous logs (optional - be careful!)
# tail -0 /var/log/freeswitch/freeswitch.log > /dev/null

# Step 2: Enable maximum logging
fs_cli -x "sofia loglevel all 9"
fs_cli -x "console loglevel debug"

# Step 3: Start monitoring in real-time
tail -f /var/log/freeswitch/freeswitch.log | tee /tmp/call_log_$(date +%Y%m%d_%H%M%S).txt | grep -iE "2001|2003|answer|bridge|media|rtp|codec|hangup|486|603|decline|reject|failed|error|SIP/2.0"
```

**Then:**
1. Make the call from 2001 to 2003
2. Let it ring
3. Answer on 2003
4. Watch the logs as it drops
5. Stop with `Ctrl+C`
6. The full log will be saved to `/tmp/call_log_*.txt`

## 🔍 Most Important Log Sections to Check

After getting the logs, look for these specific patterns:

### 1. Answer Event
```
CHANNEL_ANSWER|CHANNEL_EXECUTE.*answer|answered
```

### 2. Media Negotiation
```
SDP|codec|RTP|media-bypass|bypass-media
```

### 3. RTP Setup
```
Starting RTP|RTP|RTCP|UDP port|media.*start
```

### 4. Hangup Cause
```
HANGUP|hangup_cause|NORMAL_CLEARING|CALL_REJECTED|486|603
```

### 5. Bridge Status
```
Bridge|bridge.*2003|unable.*bridge|bridge.*fail
```

## 📋 Extract Logs by Time Range

If you know approximately when the call happened:

```bash
# Get logs from last 10 minutes
tail -n +$(($(wc -l < /var/log/freeswitch/freeswitch.log) - 5000)) /var/log/freeswitch/freeswitch.log | grep -iE "2001|2003" | tail -100

# Or use journalctl if using systemd (alternative log location)
journalctl -u freeswitch -n 500 --no-pager | grep -iE "2001|2003"
```

## 🎯 Quick One-Liner for Immediate Log Capture

Run this command, then make the call:

```bash
fs_cli -x "sofia loglevel all 9" && fs_cli -x "console loglevel debug" && echo "Logging enabled. Make your call now..." && tail -f /var/log/freeswitch/freeswitch.log | grep --line-buffered -iE "2001|2003|answer|bridge|hangup|486|603|rtp|media|codec"
```

## 📝 Save Logs to File

To save logs to a file for later analysis:

```bash
# Save to file with timestamp
LOG_FILE="/tmp/fusionpbx_call_drop_$(date +%Y%m%d_%H%M%S).log"

# Enable logging and save
fs_cli -x "sofia loglevel all 9"
fs_cli -x "console loglevel debug"

# Start capturing
tail -f /var/log/freeswitch/freeswitch.log | tee "$LOG_FILE" | grep -iE "2001|2003"
```

After the call, check the file:
```bash
cat "$LOG_FILE" | grep -iE "answer|bridge|hangup|486|603|rtp|media"
```

## 🔍 Common Issues to Look For

Based on the symptoms (drops when answered), check for:

1. **Codec Mismatch:**
   ```bash
   tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "codec|no.*codec|codec.*fail" | grep -iE "2001|2003"
   ```

2. **RTP Port Issues:**
   ```bash
   tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "RTP|rtp.*port|UDP.*port" | grep -iE "2001|2003"
   ```

3. **Media Bypass Issues:**
   ```bash
   tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "bypass.*media|media.*bypass" | grep -iE "2001|2003"
   ```

4. **SIP Reject (486/603):**
   ```bash
   tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "486|603|Busy|Decline" | grep -iE "2001|2003"
   ```

## ✅ Next Steps

1. **Run the real-time monitoring command** above
2. **Make the call** from 2001 to 2003
3. **Answer on 2003** and watch the logs
4. **Share the logs** showing what happens when you answer
5. Look specifically for:
   - Answer events
   - Media negotiation
   - RTP setup
   - Hangup causes

This will help identify why the call drops when answered!

## FUSIONPBX_GET_LOGS_FOR_403

# Get Logs for 403 Forbidden Error

## 🎯 Quick Commands to Get Logs

### Method 1: Watch Logs in Real-Time (Recommended)

**Before making the call:**
```bash
# Enable detailed SIP logging
fs_cli -x "sofia loglevel all 9"

# Enable console/debug logging
fs_cli -x "console loglevel debug"

# Watch logs in real-time (run this, then make the call)
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "2002|2001|403|forbidden|deny|acl|reject"
```

**Then make the call from extension 2002 to 2001, and watch the output.**

### Method 2: Save Logs to File

```bash
# Enable logging
fs_cli -x "sofia loglevel all 9"
fs_cli -x "console loglevel debug"

# Save logs to file (run this, then make the call)
tail -f /var/log/freeswitch/freeswitch.log > /tmp/403_error.log 2>&1

# After the call fails, stop with Ctrl+C, then view:
cat /tmp/403_error.log | grep -iE "2002|2001|403|forbidden|deny|acl|reject"
```

### Method 3: Get Last 100 Lines of Log

```bash
# Get recent log entries
tail -100 /var/log/freeswitch/freeswitch.log | grep -iE "2002|2001|403|forbidden|deny"
```

### Method 4: Search Logs for Specific Timeframe

```bash
# Get logs from last 5 minutes
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "2002|2001|403|forbidden"

# Or search all logs for today
grep -iE "2002.*2001|403|forbidden" /var/log/freeswitch/freeswitch.log | tail -50
```

## 🔍 Detailed Logging Commands

### Enable Maximum Debugging

```bash
# Connect to FreeSWITCH CLI
fs_cli

# Then run these commands in fs_cli:
sofia loglevel all 9
console loglevel debug
loglevel debug

# Exit fs_cli
/exit
```

### Watch All SIP Messages

```bash
# Watch all SIP messages (very verbose)
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "sofia|sip|invite|2002|2001"
```

### Watch for ACL/Authorization Messages

```bash
# Focus on ACL and authorization messages
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "acl|deny|allow|403|forbidden|authorization|auth"
```

## 📊 What to Look For in Logs

When you get the logs, look for these patterns:

### Good Signs (Should See):
```
[INFO] sofia.c: Received SIP INVITE from 2002@...
[DEBUG] sofia.c: ACL check for IP ...: ALLOW
[INFO] mod_dialplan_xml.c: Processing 2002 -> 2001 in context ...
```

### Bad Signs (403 Forbidden Causes):
```
[WARNING] sofia.c: IP ... Denied by acl "..."
[ERROR] sofia.c: 403 Forbidden
[NOTICE] sofia.c: Rejecting INVITE from ... - ACL deny
[WARNING] sofia.c: Authentication failed for 2002@...
[ERROR] switch_ivr_originate.c: Permission denied
```

## 🎯 Complete Logging Script

Save this as a script to capture everything:

```bash
#!/bin/bash
# Save as: capture_403_logs.sh

echo "=== Starting Log Capture ==="
echo "Make a call from 2002 to 2001 now..."
echo "Press Ctrl+C when call fails to stop logging"
echo ""

# Enable logging
fs_cli -x "sofia loglevel all 9" > /dev/null 2>&1
fs_cli -x "console loglevel debug" > /dev/null 2>&1

# Capture logs
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/tmp/403_error_${TIMESTAMP}.log"

echo "Logging to: $LOG_FILE"
echo ""

tail -f /var/log/freeswitch/freeswitch.log | tee "$LOG_FILE" | grep -iE "2002|2001|403|forbidden|deny|acl|reject|sofia|invite|auth"
```

**Usage:**
```bash
chmod +x capture_403_logs.sh
./capture_403_logs.sh
# Make the call, wait for error, then Ctrl+C
# Check the log file:
cat /tmp/403_error_*.log
```

## 📋 One-Liner Commands (Copy & Paste)

### Get logs for last call attempt:
```bash
tail -200 /var/log/freeswitch/freeswitch.log | grep -A 5 -B 5 -iE "2002.*2001|403|forbidden"
```

### Get all 403 errors from today:
```bash
grep -i "403\|forbidden" /var/log/freeswitch/freeswitch.log | tail -20
```

### Get ACL deny messages:
```bash
grep -i "deny\|acl" /var/log/freeswitch/freeswitch.log | grep -iE "2002|2001" | tail -20
```

### Get full call flow for debugging:
```bash
fs_cli -x "sofia loglevel all 9" && tail -f /var/log/freeswitch/freeswitch.log | grep -iE "2002|2001"
```

## 🔍 Alternative: Check FreeSWITCH Console Directly

```bash
# Connect to FreeSWITCH console
fs_cli

# Enable verbose logging
sofia loglevel all 9
console loglevel debug

# Watch console output directly
# Then make the call and watch the output in real-time
```

## 📝 After Getting Logs

Once you have the logs, share them and look for:

1. **ACL deny messages** - Shows which ACL is blocking
2. **Authentication failures** - Shows auth issues
3. **Context/permission errors** - Shows dialplan issues
4. **Domain mismatch errors** - Shows domain format issues

**Common log patterns that cause 403:**
- `Denied by acl "..."` - ACL blocking
- `403 Forbidden` - Explicit rejection
- `Authentication failed` - Auth issue
- `Permission denied` - Extension permissions
- `Invalid domain` - Domain format issue

## 🎯 Recommended Command

**Run this before making the call:**
```bash
fs_cli -x "sofia loglevel all 9" && fs_cli -x "console loglevel debug" && tail -f /var/log/freeswitch/freeswitch.log | grep -iE "2002|2001|403|forbidden|deny|acl|reject|auth"
```

Then make the call from 2002 to 2001 and watch the output!

## FUSIONPBX_LOGGING_GUIDE

# FusionPBX/FreeSWITCH Logging Guide

## Finding Logs for Failed Dialing

### Main Log Locations

**FreeSWITCH Main Log:**
```bash
# Main log file
/var/log/freeswitch/freeswitch.log

# Rotated logs (daily)
/var/log/freeswitch/freeswitch.log.2024-01-15

# CDR (Call Detail Records) - shows all call attempts
/var/log/freeswitch/cdr-csv/Master.csv
```

### Quick Log Commands

```bash
# SSH into FusionPBX server
ssh root@136.115.41.45

# View recent log entries (last 100 lines)
tail -100 /var/log/freeswitch/freeswitch.log

# Follow log in real-time (press Ctrl+C to stop)
tail -f /var/log/freeswitch/freeswitch.log

# Search for extension 2001 or 2002
grep -i "2001\|2002" /var/log/freeswitch/freeswitch.log | tail -50

# Search for errors related to extensions
grep -i "error\|fail\|reject" /var/log/freeswitch/freeswitch.log | grep -i "2001\|2002" | tail -50

# Check CDR for call attempts
tail -50 /var/log/freeswitch/cdr-csv/Master.csv | grep -i "2001\|2002"
```

### Enable Detailed Logging via fs_cli

```bash
# Connect to FreeSWITCH CLI
fs_cli

# Enable debug logging (level 9 = most verbose)
fs_cli> console loglevel 9

# Enable SIP debug logging
fs_cli> sofia loglevel all 9

# Enable dialplan debug
fs_cli> dialplan_loglevel 9

# Watch logs in real-time
fs_cli> /log level 9

# Exit fs_cli
fs_cli> /exit
```

### Check Specific Extension Issues

```bash
# Check if extension 2001 exists in directory
fs_cli -x "user_exists id 2001 domain-name default"

# Check extension details
fs_cli -x "xml_locate directory domain default 2001"

# Check dialplan for extension
fs_cli -x "dialplan_lookup context=public number=2001"

# Check what happens when dialing extension
fs_cli -x "originate user/2001@default &echo"
```

### Search for Twilio Transfer Failures

```bash
# Search for Twilio-related logs
grep -i "twilio\|136.115.41.45\|sip:2001" /var/log/freeswitch/freeswitch.log | tail -50

# Search for SIP INVITE failures
grep -i "invite\|487\|404\|408\|503" /var/log/freeswitch/freeswitch.log | grep -i "2001\|2002" | tail -50

# Search for authentication failures
grep -i "auth\|401\|403" /var/log/freeswitch/freeswitch.log | tail -50
```

### Check SIP Profile Logs

```bash
# Check external profile status
fs_cli -x "sofia status profile external"

# Check SIP traces (if enabled)
ls -la /var/log/freeswitch/sip-traces/

# Enable SIP trace capture
fs_cli -x "sofia global siptrace on"
```

### Common Error Messages to Look For

**Extension Not Found (404):**
```
NOT_FOUND [sofia_contact(2001@default)]
```
**Solution:** Extension doesn't exist or wrong domain

**User Not Registered:**
```
USER_NOT_REGISTERED [2001@default]
```
**Solution:** Extension exists but phone isn't registered

**Invalid Gateway:**
```
INVALID_GATEWAY
```
**Solution:** SIP profile configuration issue

**Call Rejected:**
```
CALL_REJECTED
```
**Solution:** ACL or firewall blocking

**Timeout:**
```
TIMEOUT
```
**Solution:** Network or routing issue

### Real-Time Monitoring During Transfer

```bash
# Terminal 1: Follow main log
tail -f /var/log/freeswitch/freeswitch.log

# Terminal 2: Follow SIP log
fs_cli -x "/log level 7"
fs_cli -x "sofia loglevel all 7"

# Terminal 3: Watch for calls
watch -n 1 'fs_cli -x "show channels"'
```

### Check Extension Registration Status

```bash
# Check if extension 2001 is registered
fs_cli -x "sofia status profile internal reg" | grep -i 2001

# Check all registrations
fs_cli -x "sofia status profile internal reg"

# Check if extension is active
fs_cli -x "user_data 2001@default var presence_id"
```

### Check Dialplan Context

```bash
# List all dialplan contexts
fs_cli -x "dialplan_reload"
fs_cli -x "xml_locate dialplan"

# Test dialplan for extension 2001
fs_cli -x "dialplan_lookup context=public number=2001"
fs_cli -x "dialplan_lookup context=from-external number=2001"
fs_cli -x "dialplan_lookup context=default number=2001"
```

### FusionPBX Web GUI Logs

1. **Login to FusionPBX:**
   ```
   https://136.115.41.45
   ```

2. **View Logs:**
   - `Status → System Logs → FreeSWITCH Log`
   - `Status → SIP Status → Logs`
   - `Status → System Status → Log Viewer`

3. **CDR (Call Detail Records):**
   - `Reports → CDR → Search`
   - Filter by extension: `2001` or `2002`
   - Check call status and duration

### Enable Verbose Logging in FusionPBX GUI

1. **Go to:** `Advanced → System → Settings`
2. **Find:** `Log Level` or `Debug Level`
3. **Set to:** `DEBUG` or `9`
4. **Save**
5. **Reload FreeSWITCH:** `Status → SIP Status → Reload`

### Export Logs for Analysis

```bash
# Export last 1000 lines of log with errors
grep -i "error\|fail\|2001\|2002" /var/log/freeswitch/freeswitch.log | tail -1000 > /tmp/dialing_errors.log

# Export all SIP INVITE attempts
grep -i "invite.*2001\|invite.*2002" /var/log/freeswitch/freeswitch.log > /tmp/sip_invites.log

# Export CDR for last 24 hours
tail -100 /var/log/freeswitch/cdr-csv/Master.csv > /tmp/cdr_export.csv
```

### Most Useful Command for Your Issue

Run this single command to see recent failures:

```bash
# SSH into FusionPBX
ssh root@136.115.41.45

# One command to rule them all
tail -200 /var/log/freeswitch/freeswitch.log | grep -iE "2001|2002|error|fail|invite" | tail -50
```

This will show the last 50 relevant log entries about extensions 2001/2002, errors, failures, and INVITE attempts.

## FUSIONPBX_MADDR_WORKAROUND

# FreeSWITCH maddr Workaround - Connection May Still Work

## Current Situation

Despite all configuration attempts:
- ✅ `local_ip_v4=0.0.0.0` in vars.xml
- ✅ `sip-ip=136.115.41.45` in database
- ✅ `auto-maddr=false` in sofia.conf.xml
- ✅ Public IP alias on interface

FreeSWITCH **still binds to `10.128.0.10:7443`** and adds `maddr=10.128.0.10` to BIND-URL.

**However, this might still work!** The `maddr` parameter in the BIND-URL is primarily for **advertising** in SIP headers, not necessarily blocking connections.

---

## Test: Does It Actually Work?

Even though it binds to `10.128.0.10:7443`, Google Cloud's NAT should route external connections correctly.

### Test 1: Check if Port is Accessible Externally

**From your local machine (NOT the VM):**

```bash
# Test if port 7443 is accessible
telnet 136.115.41.45 7443

# Or with openssl (for WSS)
openssl s_client -connect 136.115.41.45:7443 -brief

# Or from browser console:
# let ws = new WebSocket('wss://136.115.41.45:7443');
```

**If this connects**, the binding is working despite showing `10.128.0.10:7443` internally.

### Test 2: Check Google Cloud Firewall

```bash
# On the VM, check if firewall allows port 7443
# Check UFW rules
ufw status | grep 7443

# Check if port is listening on all interfaces (even if netstat shows 10.128.0.10)
ss -tlnp | grep 7443

# Check iptables
iptables -L -n | grep 7443
```

### Test 3: Test from WebRTC Client

Try connecting from your WebRTC client:
- URL: `wss://136.115.41.45:7443`
- Check browser console for connection status

---

## Why This Might Still Work

On Google Cloud:
1. **Internal binding:** FreeSWITCH binds to `10.128.0.10:7443` (internal interface)
2. **NAT routing:** Google Cloud routes `136.115.41.45:7443` → `10.128.0.10:7443`
3. **Connection accepted:** FreeSWITCH accepts the connection because it's listening on that interface

The `maddr=10.128.0.10` in BIND-URL is just what's **advertised** in SIP headers, not necessarily what blocks connections.

---

## Alternative Solutions

### Solution 1: Accept the Binding (If It Works)

If external connections work, the binding to `10.128.0.10:7443` is fine. The `maddr` parameter won't block connections.

**Verify it works:**
- Test WebSocket connection from browser
- Test SIP registration from WebRTC client
- If both work, you're done!

### Solution 2: Use a Reverse Proxy (nginx/haproxy)

If the binding is causing issues, use a reverse proxy:

```nginx
# nginx configuration
server {
    listen 7443 ssl;
    server_name 136.115.41.45;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://10.128.0.10:7443;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Solution 3: Check FreeSWITCH Version and Compile Options

The `auto-maddr` parameter might not be supported in your FreeSWITCH version:

```bash
# Check FreeSWITCH version
freeswitch -version

# Check if sofia.conf.xml is being loaded
fs_cli -x "module_exists mod_sofia"
fs_cli -x "reload mod_sofia"

# Check sofia settings
fs_cli -x "sofia global" | grep -i maddr
```

### Solution 4: Patch wss.xml Directly (Last Resort)

If FusionPBX regenerates the XML, we might need to patch it after each regeneration:

```bash
# Create a script to patch wss.xml after reload
cat > /usr/local/bin/patch-wss.sh << 'EOF'
#!/bin/bash
# Patch wss.xml to remove maddr from bind-params

WSS_XML="/etc/freeswitch/sip_profiles/wss.xml"

# Remove maddr from bind-params if it exists
sed -i 's/;maddr=[0-9.]*//g' "$WSS_XML"
sed -i 's/maddr=[0-9.]*;//g' "$WSS_XML"

# Reload profile
fs_cli -x "sofia profile wss restart"
EOF

chmod +x /usr/local/bin/patch-wss.sh
```

**Note:** This is a workaround and may not work if Sofia adds maddr at runtime.

---

## Recommended: Test If It Works First

**Before trying more complex solutions, test if the connection actually works:**

1. **From your local machine:**
   ```bash
   openssl s_client -connect 136.115.41.45:7443 -brief
   ```

2. **From WebRTC client:**
   - Try connecting to `wss://136.115.41.45:7443`
   - Check browser console for errors

3. **If it works:**
   - ✅ You're done! The binding is fine.
   - The `maddr` parameter is just informational.

4. **If it doesn't work:**
   - Check Google Cloud firewall rules
   - Check if port 7443 is open in Google Cloud Console
   - Try the reverse proxy solution

---

## Check Google Cloud Firewall Rules

Make sure port 7443 is open in Google Cloud:

1. Go to Google Cloud Console
2. **VPC Network** → **Firewall Rules**
3. Create a rule allowing:
   - **Protocol:** TCP
   - **Ports:** 7443
   - **Source:** 0.0.0.0/0 (or your specific IPs)
   - **Target:** Your VM instance

Or via command line:

```bash
# List existing firewall rules
gcloud compute firewall-rules list | grep 7443

# Create firewall rule if missing
gcloud compute firewall-rules create allow-wss-7443 \
  --allow tcp:7443 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow WSS on port 7443"
```

---

## Summary

1. **Test first:** Try connecting from outside - it might work despite the binding
2. **Check firewall:** Ensure port 7443 is open in Google Cloud
3. **If it works:** Accept the binding - it's fine
4. **If it doesn't:** Use reverse proxy or check firewall rules

The `maddr` parameter is often just informational and won't block connections.


## FUSIONPBX_QUICK_SETUP

# FusionPBX Quick Setup for Twilio Transfer

## The One Thing You're Missing

Based on your error logs and screenshots, you have:
- ✅ Access Control List `Twilio-SIP` created correctly
- ❌ **SIP Profile not configured to USE the ACL**

## Quick Fix

### Via FusionPBX GUI (Easiest)

1. Login: `https://136.115.41.45`
2. Go to: `Advanced → SIP Profiles → external`
3. Find the row labeled: `apply-inbound-acl`
4. Change its **Value** to: `Twilio-SIP`
5. Make sure **Enabled** is checked ✅
6. Click **Save** at the bottom
7. Go to: `Status → SIP Status`
8. Find "external" profile
9. Click **Reload XML**
10. Click **Restart**

That's it! The SIP profile now knows to use your `Twilio-SIP` ACL.

### Via Database (If GUI Doesn't Work)

```bash
ssh root@136.115.41.45

# PostgreSQL
sudo -u postgres psql fusionpbx

UPDATE v_sip_profile_settings sps
SET sip_profile_setting_value = 'Twilio-SIP'
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

UPDATE v_sip_profile_settings sps
SET sip_profile_setting_enabled = true
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

\q

fs_cli -x "reload"
```

---

## What's Happening?

1. You created the **Access Control List** → ✅ Twilio IPs are whitelisted
2. But the **SIP Profile** doesn't know to **apply** that ACL → ❌ Still rejecting calls
3. You need to tell the SIP profile: "Use the Twilio-SIP ACL" → Missing step!

**Think of it like this:**
- ACL = A list of allowed guests
- SIP Profile = The bouncer at the door
- You created the guest list ✅
- But forgot to tell the bouncer to check it ❌

---

## Verify It Worked

```bash
ssh root@136.115.41.45
fs_cli -x "sofia xmlstatus profile external" | grep -i "apply-inbound-acl"
```

Should show:
```
<apply-inbound-acl>Twilio-SIP</apply-inbound-acl>
```

---

## Then Test

Make a test transfer call. Watch logs:

```bash
ssh root@136.115.41.45
fs_cli -x "console loglevel 9"
```

You should see SIP INVITE from Twilio IP being accepted, not rejected.


## FUSIONPBX_TROUBLESHOOT_EXTENSIONS

# FusionPBX Extension Troubleshooting Guide

## Your Current Situation

✅ **Extension 2001 IS registered** (shows Contact: `sip:2001@198.27.217.12:55965`)  
❌ **But `user_exists` returns false** - likely a domain mismatch issue

## Correct Commands for Your Setup

### Check Extension Registration (CORRECT)

```bash
# Check ALL registered extensions on internal profile
fs_cli -x "sofia status profile internal reg"

# Check specific extension registration
fs_cli -x "sofia status profile internal reg" | grep -i "2001\|2002"

# Your extension is registered to domain: 136.115.41.45 (your IP)
# So check with that domain:
fs_cli -x "user_exists id 2001 domain-name 136.115.41.45"
```

### Check Extension in Directory (Multiple Methods)

```bash
# Method 1: Check with IP as domain
fs_cli -x "user_exists id 2001 domain-name 136.115.41.45"

# Method 2: Check with 'default' domain (if configured)
fs_cli -x "user_exists id 2001 domain-name default"

# Method 3: Check all domains and find where 2001 exists
fs_cli -x "user_data 2001@136.115.41.45 var"

# Method 4: List all users in directory
fs_cli -x "xml_locate directory"
```

### Check Dialplan (CORRECT Syntax)

```bash
# FreeSWITCH doesn't use "dialplan_lookup context=..." syntax
# Instead, use these commands:

# Reload dialplan first
fs_cli -x "reloadxml"

# Check what dialplan contexts exist
fs_cli -x "xml_locate dialplan"

# Test dialing extension 2001 from external context
fs_cli -x "originate {origination_caller_id_number=Twilio,origination_caller_id_name=Twilio,context=public,domain_name=136.115.41.45}user/2001@136.115.41.45 &echo"

# Or simpler test
fs_cli -x "originate user/2001@136.115.41.45 &echo"
```

### Find CDR Logs (Correct Locations)

```bash
# CDR location might be different - check these:
ls -la /var/log/freeswitch/cdr-csv/
ls -la /var/log/freeswitch/cdr-csv/*.csv

# Or check FusionPBX database for CDR
sudo -u postgres psql fusionpbx -c "SELECT * FROM v_xml_cdr ORDER BY start_stamp DESC LIMIT 10;"

# Or via FusionPBX GUI:
# Reports → CDR → Search (filter by extension 2001)
```

### Check Extension Details from Database

```bash
# Check if extension exists in FusionPBX database
sudo -u postgres psql fusionpbx -c "SELECT extension, enabled, description FROM v_extensions WHERE extension IN ('2001', '2002');"

# Check extension user details
sudo -u postgres psql fusionpbx -c "SELECT extension, user_uuid, domain_uuid FROM v_extensions WHERE extension IN ('2001', '2002');"

# Check what domain the extensions belong to
sudo -u postgres psql fusionpbx -c "SELECT e.extension, d.domain_name FROM v_extensions e JOIN v_domains d ON e.domain_uuid = d.domain_uuid WHERE e.extension IN ('2001', '2002');"
```

### Check Extension Registration Details

```bash
# Get detailed registration info for 2001
fs_cli -x "sofia status profile internal reg" | grep -A 10 "2001"

# Check user data
fs_cli -x "user_data 2001@136.115.41.45 var presence_id"
fs_cli -x "user_data 2001@136.115.41.45 var contact"

# Check if extension can receive calls
fs_cli -x "user_callcenter 2001@136.115.41.45 status"
```

## Why Dialing Might Fail

### 1. Domain Mismatch

Your extension is registered as `2001@136.115.41.45`, but your transfer code might be using:
- `sip:2001@136.115.41.45` ✅ Correct
- `sip:2001@default` ❌ Wrong domain

**Check your transfer code:**
```bash
# Check what SIP URI your code is sending
grep -r "sip:2001" convonet/
grep -r "2001@" convonet/
```

### 2. Context Mismatch

Twilio calls come in on `external` profile, which uses context `public` or `from-external`.  
Extension 2001 might be in context `default` or `from-internal`.

**Check contexts:**
```bash
# Check what context external profile uses
fs_cli -x "sofia xmlstatus profile external" | grep context

# Check extension's context in database
sudo -u postgres psql fusionpbx -c "SELECT extension, user_context FROM v_extensions WHERE extension = '2001';"

# Check dialplan for external → extension routing
fs_cli -x "reloadxml"
fs_cli -x "xml_locate dialplan public"
```

### 3. Extension Not Reachable from External Profile

**Test if extension can be dialed from external context:**

```bash
# This simulates a call from external profile
fs_cli -x "originate {origination_caller_id_number=Twilio,context=public,domain_name=136.115.41.45}user/2001@136.115.41.45 &echo"
```

### 4. Check Main Log for Actual Errors

```bash
# Watch logs in real-time while attempting transfer
tail -f /var/log/freeswitch/freeswitch.log

# Or search for recent errors
tail -200 /var/log/freeswitch/freeswitch.log | grep -iE "2001|2002|error|fail|NOT_FOUND|USER_NOT_REGISTERED"
```

## Quick Diagnostic Script

Run this to check everything at once:

```bash
#!/bin/bash
echo "=== Extension 2001 Diagnostic ==="
echo ""
echo "1. Check registration:"
fs_cli -x "sofia status profile internal reg" | grep -i "2001"
echo ""
echo "2. Check database:"
sudo -u postgres psql fusionpbx -c "SELECT extension, enabled, user_context, domain_uuid FROM v_extensions WHERE extension = '2001';"
echo ""
echo "3. Check domain:"
sudo -u postgres psql fusionpbx -c "SELECT e.extension, d.domain_name FROM v_extensions e JOIN v_domains d ON e.domain_uuid = d.domain_uuid WHERE e.extension = '2001';"
echo ""
echo "4. Check external profile context:"
fs_cli -x "sofia xmlstatus profile external" | grep -i context
echo ""
echo "5. Recent log errors:"
tail -50 /var/log/freeswitch/freeswitch.log | grep -iE "2001|error|NOT_FOUND" | tail -10
```

## Most Likely Issue

Based on your output, extension 2001 **IS registered** and working. The failure is likely:

1. **Wrong SIP URI format** in your transfer code
2. **Context routing issue** - external calls can't reach extension
3. **Domain mismatch** - using wrong domain in SIP URI

**Next Steps:**
1. Check what SIP URI your code sends: `grep -r "sip:2001" convonet/`
2. Check extension's context: `sudo -u postgres psql fusionpbx -c "SELECT extension, user_context FROM v_extensions WHERE extension = '2001';"`
3. Check dialplan routing from `public` context to extension

## FUSIONPBX_TWILIO_CONFIG_GUIDE

# FusionPBX Configuration for Twilio Call Transfer

## Overview

This guide configures FusionPBX at **136.115.41.45** to accept SIP transfers from Twilio voice calls.

**Flow:**
```
Twilio Voice Call → AI Agent → Transfer to FusionPBX Extension 2001
```

## Required Configuration Steps

### Step 1: Create Access Control List (ACL) ✅ DONE

You've already created the `Twilio-SIP` access list in FusionPBX:

**Access Control Configuration:**
- **Name**: `Twilio-SIP`
- **Default**: `allow`
- **IP Ranges (CIDR)**:
  ```
  54.172.60.0/23
  54.244.51.0/24
  177.71.206.192/26
  54.252.254.64/26
  54.169.127.128/26
  ```
- **Description**: `Twilio-SIP`

This is **correctly configured**. ✅

---

### Step 2: Configure SIP Profile to Apply the ACL

**This is the critical missing step!** You need to apply the `Twilio-SIP` ACL to your SIP profile.

#### Option A: Via FusionPBX Web GUI (Recommended)

1. **Login to FusionPBX:**
   ```
   https://136.115.41.45
   ```

2. **Navigate to SIP Profiles:**
   ```
   Advanced → SIP Profiles → external
   ```

3. **Find the `external` SIP Profile Settings**

4. **Locate "Settings" Section:**
   Look for a setting called `apply-inbound-acl` in the Settings table.

5. **Update the Setting:**
   - Find the row: `apply-inbound-acl`
   - Change its **Value** from whatever it currently is to: `Twilio-SIP`
   - Make sure **Enabled** is set to `True`
   - Keep **Description** empty or add "Allow Twilio SIP traffic"

6. **Also Check These Settings:**
   - `apply-nat-acl`: Should be `nat.auto` or empty (Enabled: True)
   - `local-network-acl`: Should be `localnet.auto` (Enabled: True)
   - `ext-sip-ip`: Should be your public IP `136.115.41.45` (Enabled: True)
   - `ext-rtp-ip`: Should be your public IP `136.115.41.45` (Enabled: True)

7. **Save and Apply:**
   - Click "Save" button at the bottom
   - Go to: `Status → SIP Status`
   - Find the "external" profile
   - Click "Reload XML" button
   - Click "Restart" button

#### Option B: Via Database (If GUI Doesn't Work)

If the FusionPBX GUI doesn't allow you to modify the setting, update it via database:

**For PostgreSQL:**
```bash
# SSH into FusionPBX
ssh root@136.115.41.45

# Connect to PostgreSQL
sudo -u postgres psql fusionpbx

# Check current apply-inbound-acl setting
SELECT 
    sps.sip_profile_setting_name,
    sps.sip_profile_setting_value,
    sps.sip_profile_setting_enabled
FROM v_sip_profile_settings sps
JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
WHERE sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

# Update to use Twilio-SIP ACL
UPDATE v_sip_profile_settings sps
SET sip_profile_setting_value = 'Twilio-SIP'
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

# Make sure it's enabled
UPDATE v_sip_profile_settings sps
SET sip_profile_setting_enabled = true
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

# Verify the change
SELECT 
    sps.sip_profile_setting_name,
    sps.sip_profile_setting_value,
    sps.sip_profile_setting_enabled
FROM v_sip_profile_settings sps
JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
WHERE sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

# Exit PostgreSQL
\q

# Reload FreeSWITCH
fs_cli -x "reload"
fs_cli -x "reload mod_sofia"
```

**For MySQL/MariaDB:**
```bash
# Connect to MySQL
mysql -u root -p fusionpbx

# Update apply-inbound-acl setting
UPDATE v_sip_profile_settings sps
JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
SET sps.sip_profile_setting_value = 'Twilio-SIP',
    sps.sip_profile_setting_enabled = true
WHERE sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

# Verify
SELECT 
    sps.sip_profile_setting_name,
    sps.sip_profile_setting_value,
    sps.sip_profile_setting_enabled
FROM v_sip_profile_settings sps
JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
WHERE sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

# Exit MySQL
EXIT;
```

---

### Step 3: Open Firewall Ports

#### On the Server/VPS Level

**Open UDP Port 5060 for SIP:**
```bash
# Using ufw
sudo ufw allow 5060/udp

# Using iptables
sudo iptables -A INPUT -p udp --dport 5060 -j ACCEPT
sudo iptables -A INPUT -p udp --dport 10000:20000 -j ACCEPT

# Save iptables rules (on Debian/Ubuntu)
sudo iptables-save > /etc/iptables/rules.v4
```

**Open RTP Ports 10000-20000:**
```bash
sudo ufw allow 10000:20000/udp
```

#### If Using Cloud Provider (Google Cloud, AWS, Azure, etc.)

Create firewall rules to allow SIP traffic:

**Google Cloud:**
```bash
gcloud compute firewall-rules create allow-twilio-sip \
    --direction=INGRESS \
    --action=ALLOW \
    --rules=udp:5060 \
    --source-ranges=54.172.60.0/23,54.244.51.0/24,177.71.206.192/26,54.252.254.64/26,54.169.127.128/26 \
    --target-tags=freepbx

gcloud compute firewall-rules create allow-twilio-rtp \
    --direction=INGRESS \
    --action=ALLOW \
    --rules=udp:10000-20000 \
    --source-ranges=54.172.60.0/23,54.244.51.0/24,177.71.206.192/26,54.252.254.64/26,54.169.127.128/26 \
    --target-tags=freepbx
```

**AWS:**
```bash
# Create Security Group rules for SIP
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxx \
    --protocol udp \
    --port 5060 \
    --source-group sg-twilio \
    --cidr 54.172.60.0/23,54.244.51.0/24,177.71.206.192/26,54.252.254.64/26,54.169.127.128/26
```

---

### Step 4: Verify Extension 2001 Exists

**Via FusionPBX Web GUI:**
1. Login to `https://136.115.41.45`
2. Go to: `Accounts → Extensions`
3. Search for extension `2001`
4. Verify:
   - Extension is **active**
   - Has a valid **device/endpoint** assigned
   - Is assigned to a valid **dial plan context**

**Or check via SSH:**
```bash
ssh root@136.115.41.45

# Check FreeSWITCH endpoints
fs_cli -x "sofia status profile external reg"

# Or check via Asterisk (if using)
asterisk -rx "pjsip list endpoints" | grep 2001
```

---

### Step 5: Test Configuration

#### Test 1: Verify SIP Port is Open

From your local machine:
```bash
nc -zuv 136.115.41.45 5060
```

**Expected:** `Connection to 136.115.41.45 5060 port [udp/sip] succeeded!`

#### Test 2: Check FreeSWITCH SIP Profile

```bash
ssh root@136.115.41.45
fs_cli -x "sofia xmlstatus profile external"
```

Look for:
- `<ext-sip-ip>136.115.41.45</ext-sip-ip>` ✅
- `<apply-inbound-acl>Twilio-SIP</apply-inbound-acl>` ✅

#### Test 3: Monitor FreeSWITCH Logs in Real-Time

```bash
# SSH into FusionPBX
ssh root@136.115.41.45

# Watch FreeSWITCH logs
tail -f /var/log/freeswitch/freeswitch.log | grep -i twilio

# Or use FreeSWITCH CLI
fs_cli -x "console loglevel 7"
```

#### Test 4: Make Test Transfer from Twilio

1. Make a test call to your Twilio number
2. Say "transfer me to agent" or similar
3. Watch the logs in real-time:

```bash
# On FusionPBX server
fs_cli -x "console loglevel 9"
```

**Look for:**
- SIP INVITE from Twilio IP (54.172.x.x or 54.244.x.x)
- ACK from FusionPBX
- Extension 2001 receiving the call
- Call being bridged successfully

---

### Step 6: Monitor Transfer Logs

**Watch FreeSWITCH CLI during transfer:**
```bash
ssh root@136.115.41.45
fs_cli
```

In the FreeSWITCH CLI, you should see:
```
[SIP]
[INVITE] from 54.172.x.x:5060
[200 OK] sending to 54.172.x.x:5060
[ACK] received
Extension 2001 is ringing
Call answered
RTP media established
```

---

### Troubleshooting

#### Issue: "Transfer failed" - SIP INVITE Rejected

**Symptoms:** Logs show `status=failed` in transfer callback

**Causes & Solutions:**

1. **Twilio IP not whitelisted**
   - Verify `Twilio-SIP` ACL exists in `Advanced → Firewall → Access Lists`
   - Verify `apply-inbound-acl` setting in SIP profile = `Twilio-SIP`

2. **Firewall blocking SIP**
   - Check UDP 5060 is open: `nc -zuv 136.115.41.45 5060`
   - Check cloud provider firewall rules
   - Check fail2ban isn't blocking: `sudo fail2ban-client status sshd`

3. **Extension 2001 doesn't exist**
   - Verify extension exists in `Accounts → Extensions`
   - Check extension is active and has valid device
   - Test extension from internal phone first

4. **FreeSWITCH not reloaded**
   - Go to `Status → SIP Status`
   - Click "Reload XML"
   - Click "Restart" for external profile

#### Issue: "403 Forbidden" or "401 Unauthorized"

**Cause:** SIP authentication required

**Solution:**
1. Set SIP authentication in your app's `.env`:
   ```
   FREEPBX_SIP_USERNAME=twilio
   FREEPBX_SIP_PASSWORD=your_secure_password
   ```
2. Create a SIP user in FusionPBX for Twilio
3. Or configure the extension to allow anonymous calls

#### Issue: "No audio" or "One-way audio"

**Cause:** RTP/NAT issues

**Solution:**
1. Verify RTP ports 10000-20000 are open in firewall
2. Check `ext-sip-ip` and `ext-rtp-ip` settings in SIP profile
3. Enable `rtp-symmetric` in SIP profile
4. Check NAT settings in cloud provider

#### Issue: "Extension not found" or "408 Request Timeout"

**Cause:** Extension 2001 doesn't exist, isn't registered, or wrong context

**Solution:**
1. Verify extension exists: `Accounts → Extensions → 2001`
2. Check extension device is online: `Status → Registrations`
3. Verify dial plan context is correct
4. Test from internal phone first

---

### Summary Checklist

- [x] ✅ **Step 1**: Access Control List `Twilio-SIP` created with 5 Twilio IP ranges
- [ ] ⚠️ **Step 2**: SIP Profile `external` → `apply-inbound-acl` set to `Twilio-SIP` ← **CRITICAL MISSING STEP**
- [ ] **Step 3**: UDP port 5060 open in server firewall
- [ ] **Step 4**: UDP ports 10000-20000 open for RTP
- [ ] **Step 5**: UDP ports open in cloud provider firewall (if applicable)
- [ ] **Step 6**: Extension 2001 exists and is active
- [ ] **Step 7**: FreeSWITCH reloaded after configuration changes
- [ ] **Step 8**: Test transfer successful

**Current Status:**
- FusionPBX IP: `136.115.41.45`
- Extension: `2001`
- SIP URI: `sip:2001@136.115.41.45;transport=udp`
- Access List: `Twilio-SIP` ✅ Created
- Missing: SIP Profile ACL configuration ⚠️

**Next Step:** Configure the `apply-inbound-acl` setting in your SIP profile (Step 2).

## FUSIONPBX_TWILIO_INVITE_FIX

# Fix Twilio SIP INVITE to FusionPBX Extensions

## ✅ Good News: Your Extension Works!

Your test call was **successful**:
- Extension 2001 exists and is registered ✅
- Extension can receive calls ✅  
- Dialplan routing works ✅
- RTP/media path works ✅

## 🔴 Problem: Twilio SIP INVITE Not Reaching FusionPBX

Since the internal call works but Twilio transfers fail, the issue is that **Twilio's SIP INVITE requests are either:**
1. Not reaching FusionPBX (firewall/network)
2. Being rejected by FusionPBX (ACL/authentication)
3. Using wrong SIP profile or context

## Diagnostic Steps

### Step 1: Monitor Logs During Twilio Transfer

```bash
# Watch logs in real-time while attempting a Twilio transfer
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "twilio|invite|2001|external"
```

**What to look for:**
- SIP INVITE from Twilio IP addresses (54.172.x.x, 54.244.x.x, etc.)
- "ACL" or "deny" messages
- "NOT_FOUND" or "USER_NOT_REGISTERED" errors
- Any errors related to `external` profile

### Step 2: Check if Twilio INVITE Reaches FusionPBX

```bash
# Enable SIP debugging
fs_cli -x "sofia loglevel all 9"

# Watch for SIP messages from Twilio IPs
tail -f /var/log/freeswitch/freeswitch.log | grep -E "54\.172\.|54\.244\.|177\.71\.|54\.252\.|54\.169\."
```

**If you see INVITE from Twilio IPs:** The issue is ACL or dialplan routing  
**If you DON'T see any INVITE:** The issue is firewall/network (Twilio can't reach FusionPBX)

### Step 3: Verify ACL Configuration

```bash
# Check if ACL is applied to external profile
fs_cli -x "sofia xmlstatus profile external" | grep -i "apply-inbound-acl"

# Should show:
# <apply-inbound-acl>Twilio-SIP</apply-inbound-acl>
```

**If it shows something else or is missing:**
- Go to FusionPBX GUI: `Advanced → SIP Profiles → external → Settings`
- Find `apply-inbound-acl` and set to `Twilio-SIP`
- Reload: `Status → SIP Status → external → Reload XML → Restart`

### Step 4: Test Direct SIP INVITE from External IP

```bash
# This simulates what Twilio does - sends INVITE to external profile
fs_cli -x "originate {origination_caller_id_number=Twilio,origination_caller_id_name=Twilio,context=public,domain_name=136.115.41.45}sofia/external/sip:2001@136.115.41.45 &echo"
```

**Note:** This uses `sofia/external/` instead of `user/` to simulate external SIP call.

## Most Likely Issues & Fixes

### Issue 1: ACL Not Applied to External Profile ❌

**Symptom:** No INVITE messages in logs, or ACL deny messages

**Fix:**
```bash
# Via Database (PostgreSQL)
sudo -u postgres psql fusionpbx

UPDATE v_sip_profile_settings sps
SET sip_profile_setting_value = 'Twilio-SIP',
    sip_profile_setting_enabled = true
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

# If setting doesn't exist, INSERT it
INSERT INTO v_sip_profile_settings (
    sip_profile_setting_uuid,
    sip_profile_uuid,
    sip_profile_setting_name,
    sip_profile_setting_value,
    sip_profile_setting_enabled
) VALUES (
    gen_random_uuid(),
    (SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'external'),
    'apply-inbound-acl',
    'Twilio-SIP',
    true
);

\q

# Reload FreeSWITCH
fs_cli -x "reload"
fs_cli -x "sofia profile external restart"

# Verify
fs_cli -x "sofia xmlstatus profile external" | grep apply-inbound-acl
```

### Issue 2: Context Mismatch

**Problem:** External profile uses `public` context, but dialplan doesn't route `public` → extension 2001

**Check dialplan:**
```bash
# Check what dialplan exists for public context
fs_cli -x "xml_locate dialplan public extension 2001"

# Or check via FusionPBX GUI:
# Dialplan → Inbound Routes → Check routes for public context
```

**Fix:** Ensure there's a dialplan route in `public` context that routes to extension 2001:

```xml
<!-- In public context, add extension 2001 -->
<extension name="extension_2001">
  <condition field="destination_number" expression="^2001$">
    <action application="transfer" data="2001 XML default"/>
  </condition>
</extension>
```

### Issue 3: Firewall Blocking Twilio IPs

**Check firewall:**
```bash
# Check if firewall is blocking UDP 5060
sudo iptables -L -n | grep 5060

# Temporarily disable firewall for testing (NOT for production!)
sudo systemctl stop ufw
# OR
sudo iptables -F
```

**Permanent fix:** Configure firewall to allow Twilio IPs:
```bash
# Allow Twilio IP ranges
sudo ufw allow from 54.172.60.0/23 to any port 5060 proto udp
sudo ufw allow from 54.244.51.0/24 to any port 5060 proto udp
sudo ufw allow from 177.71.206.192/26 to any port 5060 proto udp
sudo ufw allow from 54.252.254.64/26 to any port 5060 proto udp
sudo ufw allow from 54.169.127.128/26 to any port 5060 proto udp
```

### Issue 4: External Profile Not Listening on Public IP

**Check:**
```bash
# Check what IP the external profile is bound to
fs_cli -x "sofia status profile external"

# Should show it's listening on 136.115.41.45:5060 (or 0.0.0.0:5060)
```

**If it's only listening on private IP (10.128.x.x):**
```bash
# Check external profile settings
fs_cli -x "sofia xmlstatus profile external" | grep -E "sip-ip|ext-sip-ip"

# Should show:
# <sip-ip>10.128.0.8</sip-ip> (binds to private)
# <ext-sip-ip>136.115.41.45</ext-sip-ip> (advertises public)
```

## Quick Test: Enable Verbose Logging and Try Transfer

```bash
# Terminal 1: Watch logs
tail -f /var/log/freeswitch/freeswitch.log

# Terminal 2: Enable verbose logging
fs_cli -x "console loglevel 9"
fs_cli -x "sofia loglevel all 9"

# Terminal 3: Now attempt a Twilio transfer
# (Make a call to your Twilio number and request transfer)

# Watch Terminal 1 for:
# - SIP INVITE from Twilio IP
# - ACL allow/deny messages
# - Dialplan routing
# - Extension lookup
```

## Expected Log Flow for Successful Transfer

When working correctly, you should see:

```
[INFO] sofia.c: Received SIP INVITE from 54.172.x.x:5060
[DEBUG] sofia.c: ACL check for 54.172.x.x: ALLOW (Twilio-SIP)
[INFO] sofia.c: Routing INVITE to extension 2001
[DEBUG] switch_core_state_machine.c: Dialing user/2001@136.115.41.45
[NOTICE] sofia.c: Channel [sofia/internal/2001@...] has been answered
[INFO] switch_channel.c: Callstate Change RINGING -> ACTIVE
```

## Most Likely Fix Based on Your Setup

Given that:
- ✅ Extension works internally
- ✅ External profile context is `public`
- ❌ Twilio transfers fail

**The most likely issue is:** `apply-inbound-acl` is not set to `Twilio-SIP` on the external profile.

**Run this to fix:**
```bash
sudo -u postgres psql fusionpbx -c "
UPDATE v_sip_profile_settings sps
SET sip_profile_setting_value = 'Twilio-SIP',
    sip_profile_setting_enabled = true
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';
"

fs_cli -x "reload"
fs_cli -x "sofia profile external restart"
```

Then test a Twilio transfer again!

## FUSIONPBX_WSS_BINDING_FIX

# Fix FusionPBX WSS Profile Binding to Internal IP

## Problem

The WSS profile is binding to an internal IP address (`10.128.0.10:7443`) instead of `0.0.0.0:7443`, preventing external WebSocket connections.

**Symptom:**
```bash
netstat -tlnp | grep 7443
# Shows: tcp6  0  0  10.128.0.10:7443  ...  freeswitch
# Should show: tcp6  0  0  0.0.0.0:7443  ...  freeswitch
```

**Impact:**
- WebRTC clients cannot connect from outside the server
- Only internal connections work
- Connection errors: `WebSocket is closed before the connection is established`

---

## Root Causes

1. **`sip-ip` setting in database is correct (`0.0.0.0`) but not being applied**
2. **FreeSWITCH is auto-detecting network interface** and binding to internal IP
3. **`wss.xml` file not regenerating properly** from database
4. **Network configuration** (FreeSWITCH may prefer internal interface)

---

## Solution: Force WSS Profile to Bind to 0.0.0.0

### Step 1: Verify Current Configuration

```bash
# Check what IP the profile is actually binding to
netstat -tlnp | grep 7443

# Check database settings
PROFILE_UUID=$(sudo -u postgres psql fusionpbx -t -c "SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'wss';" | xargs)
sudo -u postgres psql fusionpbx -c "SELECT sip_profile_setting_name, sip_profile_setting_value FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name IN ('sip-ip', 'sip-port', 'ext-sip-ip');"
```

### Step 2: Update Database Settings

Ensure `sip-ip` is set to `0.0.0.0`:

```bash
PROFILE_UUID=$(sudo -u postgres psql fusionpbx -t -c "SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'wss';" | xargs)

# Update sip-ip to 0.0.0.0
sudo -u postgres psql fusionpbx << EOF
UPDATE v_sip_profile_settings 
SET sip_profile_setting_value = '0.0.0.0' 
WHERE sip_profile_uuid = '$PROFILE_UUID' 
AND sip_profile_setting_name = 'sip-ip';
EOF
```

### Step 3: Check Generated XML File

```bash
# Check if XML file exists and has correct sip-ip
cat /etc/freeswitch/sip_profiles/wss.xml | grep -E "sip-ip|sip-port"

# Should show:
# <param name="sip-ip" value="0.0.0.0"/>
# <param name="sip-port" value="7443"/>
```

### Step 4: Regenerate XML from Database

```bash
# Reload XML (FusionPBX regenerates from database)
fs_cli -x "reloadxml"

# Wait a moment for regeneration
sleep 2

# Verify the XML file was updated
cat /etc/freeswitch/sip_profiles/wss.xml | grep "sip-ip"
```

### Step 5: Stop and Restart WSS Profile

```bash
# Stop the profile
fs_cli -x "sofia profile wss stop"

# Wait for it to fully stop
sleep 2

# Start the profile
fs_cli -x "sofia profile wss start"

# Check status
fs_cli -x "sofia status profile wss"
```

### Step 6: Verify Binding

```bash
# Check what IP/port the profile is now binding to
netstat -tlnp | grep 7443

# Should show:
# tcp6  0  0  0.0.0.0:7443  ...  freeswitch
# or
# tcp  0  0  0.0.0.0:7443  ...  freeswitch
```

---

## Alternative: Manually Edit XML (If Database Update Doesn't Work)

If the database update doesn't work, you can manually edit the XML file (but note: FusionPBX may overwrite it):

```bash
# Backup original
cp /etc/freeswitch/sip_profiles/wss.xml /etc/freeswitch/sip_profiles/wss.xml.backup

# Edit the file
nano /etc/freeswitch/sip_profiles/wss.xml

# Find the line:
# <param name="sip-ip" value="10.128.0.10"/>
# Change to:
# <param name="sip-ip" value="0.0.0.0"/>

# Set proper permissions
FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
FS_USER=${FS_USER:-www-data}
chown $FS_USER:$FS_USER /etc/freeswitch/sip_profiles/wss.xml
chmod 644 /etc/freeswitch/sip_profiles/wss.xml

# Reload and restart
fs_cli -x "reloadxml"
fs_cli -x "sofia profile wss restart"
```

**Note:** If FusionPBX overwrites this file, you'll need to fix the database settings (see Step 2).

---

## Force Network Binding with Additional Settings

**If the profile still binds to the wrong IP** (e.g., `10.128.0.10` instead of `0.0.0.0`), FreeSWITCH may be using `maddr` (multicast address) which overrides `sip-ip`. Try these solutions:

### Solution 1: Add Explicit TLS Certificate and Binding Parameters

FreeSWITCH needs explicit TLS certificate configuration to properly bind to `0.0.0.0`:

```bash
PROFILE_UUID=$(sudo -u postgres psql fusionpbx -t -c "SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'wss';" | xargs)

# Add TLS certificate parameters (critical for WSS to bind correctly)
sudo -u postgres psql fusionpbx << EOF
-- Ensure sip-ip is 0.0.0.0
UPDATE v_sip_profile_settings 
SET sip_profile_setting_value = '0.0.0.0' 
WHERE sip_profile_uuid = '$PROFILE_UUID' 
AND sip_profile_setting_name = 'sip-ip';

-- Add TLS certificate directory (required)
INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'tls-cert-dir', '\$\${base_dir}/conf/tls', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'tls-cert-dir');

-- Add TLS certificate file
INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'tls-cert-file', '\$\${base_dir}/conf/tls/wss.pem', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'tls-cert-file');

-- Add TLS key file
INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'tls-key-file', '\$\${base_dir}/conf/tls/wss.pem', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'tls-key-file');

-- Ensure rtp-ip is also 0.0.0.0
UPDATE v_sip_profile_settings 
SET sip_profile_setting_value = '0.0.0.0' 
WHERE sip_profile_uuid = '$PROFILE_UUID' 
AND sip_profile_setting_name = 'rtp-ip';
EOF

# Reload and restart
fs_cli -x "reloadxml"
sleep 3
fs_cli -x "sofia profile wss stop"
sleep 2
fs_cli -x "sofia profile wss start"
sleep 2

# Verify binding
netstat -tlnp | grep 7443
# Should show: 0.0.0.0:7443
```

### Solution 2: Manually Edit XML and Disable Auto-Detection

If Solution 1 doesn't work, manually edit the XML to disable `maddr`:

```bash
# Backup
cp /etc/freeswitch/sip_profiles/wss.xml /etc/freeswitch/sip_profiles/wss.xml.backup

# Edit to add explicit bind-ip and disable maddr
nano /etc/freeswitch/sip_profiles/wss.xml
```

Add these parameters **inside the `<settings>` section**:

```xml
<param name="sip-ip" value="0.0.0.0"/>
<param name="rtp-ip" value="0.0.0.0"/>
<param name="bind-params" value="transport=wss"/>
<param name="tls-cert-dir" value="$${base_dir}/conf/tls"/>
<param name="tls-cert-file" value="$${base_dir}/conf/tls/wss.pem"/>
<param name="tls-key-file" value="$${base_dir}/conf/tls/wss.pem"/>
```

**Important:** Also check if there's an `X-PRE-PROCESS` directive that might be setting `maddr`. If the XML file has `<X-PRE-PROCESS cmd="set" data="bind_local_ip=10.128.0.10"/>` or similar, remove or comment it out.

```bash
# Set permissions
FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
FS_USER=${FS_USER:-www-data}
chown $FS_USER:$FS_USER /etc/freeswitch/sip_profiles/wss.xml
chmod 644 /etc/freeswitch/sip_profiles/wss.xml

# Restart
fs_cli -x "reloadxml"
fs_cli -x "sofia profile wss restart"
```

**Note:** FusionPBX may overwrite manual XML edits when regenerating from the database. After manual edit, disable auto-regeneration for this profile or ensure database settings match.

---

## Check Network Interface Configuration

FreeSWITCH may be auto-detecting the network interface. Check system network configuration:

```bash
# Check what IPs FreeSWITCH sees
fs_cli -x "global_getvar local_ip_v4"
fs_cli -x "global_getvar external_ip"

# Check network interfaces
ip addr show
ifconfig

# Check FreeSWITCH network ACLs
cat /etc/freeswitch/autoload_configs/acl.conf.xml | grep -A 10 "localnet.auto"
```

---

## Verify External Access

After fixing the binding:

```bash
# From your local machine (not the server), test if port is accessible
telnet 136.115.41.45 7443
# Should connect (you may see SSL negotiation)

# Or use openssl to test WSS
openssl s_client -connect 136.115.41.45:7443

# Or use curl (if installed)
curl -v -k https://136.115.41.45:7443
```

---

## Troubleshooting

### Issue: Profile still binds to internal IP after restart

**Solution:** Check if there are multiple `wss.xml` files or if FusionPBX is loading from a different location:

```bash
# Find all wss.xml files
find /etc/freeswitch -name "wss.xml"
find /usr/local/freeswitch -name "wss.xml" 2>/dev/null
find /opt/freeswitch -name "wss.xml" 2>/dev/null

# Check which directory FreeSWITCH is using
fs_cli -x "global_getvar conf_dir"
```

### Issue: Profile fails to start after changing sip-ip

**Solution:** Check logs for errors:

```bash
tail -100 /var/log/freeswitch/freeswitch.log | grep -iE "wss|error|fail"
```

Common issues:
- TLS certificate not found (check `tls-cert-file` parameter)
- Port already in use (check with `netstat -tlnp | grep 7443`)

### Issue: External connections still fail

**Solution:** Check firewall rules:

```bash
# Check if port is open in UFW
sudo ufw status | grep 7443

# Open port if needed
sudo ufw allow 7443/tcp

# Check if Google Cloud firewall allows port 7443
# (You'll need to check Google Cloud Console)
```

---

## Summary

The key fix is ensuring:
1. ✅ `sip-ip` is set to `0.0.0.0` in the database
2. ✅ XML file is regenerated from database (`reloadxml`)
3. ✅ Profile is restarted (`sofia profile wss restart`)
4. ✅ Port 7443 is open in firewall
5. ✅ Binding verified with `netstat -tlnp | grep 7443`

After these steps, the WSS profile should bind to `0.0.0.0:7443` and accept external WebSocket connections.

## FUSIONPBX_WSS_CONNECTION_DEBUG

# Debug WebSocket Connection to FreeSWITCH WSS Profile

## Current Status

✅ **Port 7443 is accessible** (telnet connects)  
❌ **WebSocket connection fails** (readyState = 0, stuck in CONNECTING)

This indicates:
- Firewall is OK (port is open)
- TCP connection works
- WebSocket handshake is failing

---

## Diagnostic Steps

### Step 1: Check FreeSWITCH Logs for Connection Attempts

```bash
# Enable verbose logging
fs_cli -x "console loglevel debug"
fs_cli -x "sofia loglevel all 9"

# Watch logs in real-time
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "wss|7443|websocket|sofia"
```

Then try connecting from browser again and watch for:
- Connection attempts
- WebSocket handshake errors
- SSL/TLS errors
- Sofia profile errors

### Step 2: Test WebSocket Connection with More Details

In browser console, run:

```javascript
// More detailed WebSocket test
let ws = new WebSocket('wss://136.115.41.45:7443');

ws.onopen = () => {
    console.log('✅ WebSocket Connected!');
    console.log('ReadyState:', ws.readyState);
};

ws.onerror = (error) => {
    console.error('❌ WebSocket Error:', error);
    console.log('ReadyState:', ws.readyState);
};

ws.onclose = (event) => {
    console.log('🔌 WebSocket Closed');
    console.log('Code:', event.code, 'Reason:', event.reason);
    console.log('Was Clean:', event.wasClean);
};

ws.onmessage = (event) => {
    console.log('📨 Message:', event.data);
};

// Check after 5 seconds
setTimeout(() => {
    console.log('Final ReadyState:', ws.readyState);
    if (ws.readyState === 0) {
        console.log('⚠️ Still connecting - likely timeout or protocol error');
    }
}, 5000);
```

### Step 3: Check WSS Profile Status

```bash
# Check if WSS profile is actually handling WebSocket connections
fs_cli -x "sofia status profile wss"

# Check for active connections
fs_cli -x "sofia status"

# Check for errors
fs_cli -x "sofia status profile wss" | grep -i error
```

### Step 4: Verify TLS Certificate

```bash
# Check certificate
openssl s_client -connect 136.115.41.45:7443 -showcerts < /dev/null

# Check certificate validity
openssl s_client -connect 136.115.41.45:7443 < /dev/null 2>&1 | grep -i "verify return code"
```

**Common issues:**
- Self-signed certificate (browser may reject)
- Certificate CN doesn't match IP
- Certificate expired

### Step 5: Test with JsSIP (SIP over WebSocket)

WebSocket alone might not work - FreeSWITCH expects SIP over WebSocket. Test with JsSIP:

```javascript
// Test SIP over WebSocket with JsSIP
const socket = new JsSIP.WebSocketInterface('wss://136.115.41.45:7443');
const configuration = {
    sockets: [socket],
    uri: 'sip:test@136.115.41.45',
    display_name: 'Test User',
    register: false
};

const ua = new JsSIP.UA(configuration);

ua.on('connected', () => {
    console.log('✅ JsSIP Connected!');
});

ua.on('disconnected', () => {
    console.log('❌ JsSIP Disconnected');
});

ua.on('registrationFailed', (e) => {
    console.error('❌ Registration Failed:', e);
});

ua.start();
```

---

## Common Issues and Fixes

### Issue 1: WebSocket Handshake Fails

**Symptoms:**
- WebSocket readyState = 0 (CONNECTING)
- No error events
- Connection times out

**Possible Causes:**
1. FreeSWITCH not configured for WebSocket
2. Protocol mismatch (expects SIP over WebSocket, not plain WebSocket)
3. TLS/SSL handshake failure

**Fix:**
- FreeSWITCH WSS profile expects **SIP over WebSocket**, not plain WebSocket
- Use JsSIP library instead of plain WebSocket API
- Check TLS certificate configuration

### Issue 2: Certificate Issues

**Symptoms:**
- Browser console shows SSL/TLS errors
- Certificate warnings

**Fix:**
```bash
# Regenerate certificate with proper CN
cd /etc/freeswitch/tls
openssl req -x509 -newkey rsa:4096 -keyout wss.pem -out wss.pem -days 365 -nodes \
  -subj "/CN=136.115.41.45"

# Set permissions
FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
chown $FS_USER:$FS_USER wss.pem
chmod 600 wss.pem

# Restart profile
fs_cli -x "sofia profile wss restart"
```

### Issue 3: Binding to Internal IP Causes Issues

**Symptoms:**
- Port accessible but WebSocket handshake fails
- maddr parameter in BIND-URL

**Possible Workaround:**
Since binding to `10.128.0.10:7443` might be causing WebSocket issues, try using a reverse proxy:

```nginx
# nginx configuration for WSS proxy
server {
    listen 7443 ssl;
    server_name 136.115.41.45;
    
    ssl_certificate /etc/freeswitch/tls/wss.pem;
    ssl_certificate_key /etc/freeswitch/tls/wss.pem;
    
    location / {
        proxy_pass http://10.128.0.10:7443;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket timeouts
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }
}
```

---

## Quick Test: Is It SIP Over WebSocket Issue?

FreeSWITCH WSS profile expects **SIP over WebSocket**, not plain WebSocket. The plain WebSocket test will fail.

**Test with proper SIP over WebSocket:**

1. Load JsSIP library in browser:
   ```html
   <script src="https://cdn.jsdelivr.net/npm/jssip@3.10.1/dist/jssip.min.js"></script>
   ```

2. Test connection:
   ```javascript
   const socket = new JsSIP.WebSocketInterface('wss://136.115.41.45:7443');
   const ua = new JsSIP.UA({
       sockets: [socket],
       uri: 'sip:test@136.115.41.45',
       display_name: 'Test',
       register: false
   });
   
   ua.on('connected', () => console.log('✅ Connected!'));
   ua.on('disconnected', () => console.log('❌ Disconnected'));
   ua.start();
   ```

If this works, the issue is that FreeSWITCH expects SIP over WebSocket, not plain WebSocket.

---

## Next Steps

1. **Check FreeSWITCH logs** while connecting from browser
2. **Test with JsSIP** (proper SIP over WebSocket client)
3. **Check certificate** validity
4. **Verify WSS profile** is actually handling WebSocket connections

The key insight: FreeSWITCH WSS profile is for **SIP over WebSocket**, not plain WebSocket connections.


## FUSIONPBX_WSS_CONNECTION_FAILING

# FreeSWITCH WSS Profile - Connection Failing

## Problem

WebSocket connection to `wss://136.115.41.45:7443` fails with:
- **Error:** "WebSocket is closed before the connection is established"
- **No logs** in FreeSWITCH showing connection attempts to WSS profile
- **Telnet works** (port is accessible)

This indicates the WebSocket handshake is failing **before** reaching FreeSWITCH or FreeSWITCH is rejecting it silently.

---

## Diagnostic Steps

### Step 1: Check if WSS Profile is Actually Listening for WebSocket Connections

```bash
# Check profile status
fs_cli -x "sofia status profile wss"

# Check for any errors
fs_cli -x "sofia status profile wss" | grep -i error

# Check if mod_sofia is handling WebSocket
fs_cli -x "module_exists mod_sofia"
```

### Step 2: Check FreeSWITCH Logs Without Filtering

```bash
# Watch ALL logs (not filtered) to see if connection attempts appear
tail -f /var/log/freeswitch/freeswitch.log
```

Then try connecting from browser and watch for ANY activity.

### Step 3: Test with curl (WebSocket Handshake)

```bash
# Test WebSocket handshake with curl
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: test" \
  --insecure \
  https://136.115.41.45:7443/
```

This will show if FreeSWITCH responds to WebSocket upgrade requests.

### Step 4: Check WSS Profile Configuration

```bash
# View actual wss.xml file
cat /etc/freeswitch/sip_profiles/wss.xml

# Check if it has proper WebSocket settings
grep -iE "wss|websocket|transport" /etc/freeswitch/sip_profiles/wss.xml
```

### Step 5: Verify TLS Certificate

```bash
# Test TLS handshake
openssl s_client -connect 136.115.41.45:7443 -showcerts < /dev/null

# Check certificate issues
openssl s_client -connect 136.115.41.45:7443 < /dev/null 2>&1 | grep -i "verify return code"
```

---

## Common Issues

### Issue 1: WSS Profile Not Configured for WebSocket Transport

The WSS profile might be configured for SIP over TLS (port 5061) but not WebSocket (port 7443).

**Check:**
```bash
# Check if wss profile has wss transport
fs_cli -x "sofia status profile wss" | grep -i "TLS-BIND-URL"
```

**Expected:** Should show `transport=wss` in TLS-BIND-URL

### Issue 2: Missing WebSocket Path

FreeSWITCH might need a specific path for WebSocket connections.

**Try connecting with path:**
```javascript
// In browser console, try with different paths
const socket = new JsSIP.WebSocketInterface('wss://136.115.41.45:7443/');
const socket2 = new JsSIP.WebSocketInterface('wss://136.115.41.45:7443/ws');
const socket3 = new JsSIP.WebSocketInterface('wss://136.115.41.45:7443/sip');
```

### Issue 3: Port 7443 Not Actually Listening for WSS

The profile might be bound to port 7443 but not configured for WebSocket.

**Check:**
```bash
# Verify what's actually listening
ss -tlnp | grep 7443

# Check if it's TLS or WSS
openssl s_client -connect 136.115.41.45:7443 < /dev/null
```

### Issue 4: TLS Certificate Rejection

Browser might be rejecting the self-signed certificate.

**Test:**
```bash
# Check certificate
openssl s_client -connect 136.115.41.45:7443 -showcerts < /dev/null | grep -A 5 "Certificate chain"
```

**Fix:** Accept certificate in browser or use a valid certificate.

---

## Quick Fix: Test with Different WebSocket URL Format

JsSIP might need a specific URL format. Try:

```javascript
// Option 1: With trailing slash
const socket = new JsSIP.WebSocketInterface('wss://136.115.41.45:7443/');

// Option 2: Without trailing slash  
const socket = new JsSIP.WebSocketInterface('wss://136.115.41.45:7443');

// Option 3: With explicit path
const socket = new JsSIP.WebSocketInterface('wss://136.115.41.45:7443/ws');
```

---

## Check WSS Profile XML Configuration

```bash
# View the actual XML
cat /etc/freeswitch/sip_profiles/wss.xml
```

**Key settings to check:**
- `sip-port` should be `7443`
- `tls` should be `true`
- `tls-bind-params` should include `transport=wss`
- TLS certificates should be configured

---

## Verify WSS Profile is Actually Running

```bash
# Check profile status
fs_cli -x "sofia status"

# Should show wss profile as RUNNING
# Check specifically:
fs_cli -x "sofia status profile wss" | head -20
```

**Expected output:**
```
Name: wss
...
Status: RUNNING
...
TLS-BIND-URL: sips:mod_sofia@136.115.41.45:5061;maddr=10.128.0.10;transport=wss;transport=tls
```

**If you see `transport=wss` in TLS-BIND-URL, the profile should accept WebSocket connections.**

---

## Test Directly with openssl

```bash
# Test if FreeSWITCH responds to TLS connection on 7443
openssl s_client -connect 136.115.41.45:7443 -showcerts

# After connection, try sending HTTP upgrade request:
# (Press Enter to send)
GET / HTTP/1.1
Host: 136.115.41.45:7443
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Version: 13
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==

```

If FreeSWITCH responds with HTTP 101 Switching Protocols, it's accepting WebSocket connections.

---

## Most Likely Issue

Based on the symptoms:
1. **Port is accessible** (telnet works)
2. **No FreeSWITCH logs** (connection rejected before reaching FreeSWITCH)
3. **WebSocket handshake fails immediately**

The issue is likely:
- **WSS profile not configured for WebSocket transport** (only TLS)
- **Port 7443 bound but not accepting WebSocket upgrades**
- **Missing WebSocket path configuration**

**Next step:** Check the WSS profile configuration and verify it's set up for WebSocket transport, not just TLS.


## FUSIONPBX_WSS_PROFILE_SUCCESS

# FusionPBX WSS Profile - Successfully Configured! ✅

## Status

The WebRTC WebSocket Secure (wss) SIP profile is now **RUNNING** on your FusionPBX server!

**Profile Details:**
- **WSS Port:** `7443` (WebSocket Secure)
- **TLS Port:** `5061` (SIP over TLS)
- **Domain:** `136.115.41.45`
- **Status:** RUNNING ✅

## What Fixed It

The key fix was adding **TLS certificate configuration parameters** to the `wss.xml` file:

```xml
<param name="tls-cert-dir" value="$${base_dir}/conf/tls"/>
<param name="tls-cert-file" value="$${base_dir}/conf/tls/wss.pem"/>
<param name="tls-key-file" value="$${base_dir}/conf/tls/wss.pem"/>
```

Without these TLS certificate paths, FreeSWITCH couldn't load the WSS profile properly.

## Verification

### Check Profile Status

```bash
# Check if wss profile is running
fs_cli -x "sofia status profile wss"

# Check all profiles
fs_cli -x "sofia status"
```

**Expected output:**
```
wss profile on port 7443 - RUNNING (WSS)
wss profile on port 5061 - RUNNING (TLS)
```

### Check Profile Details

```bash
# Get detailed wss profile information
fs_cli -x "sofia xmlstatus profile wss" | head -30

# Check TLS certificate status
fs_cli -x "sofia xmlstatus profile wss" | grep -i "tls\|cert"
```

### Test Port Accessibility

```bash
# Check if ports are listening
sudo netstat -tlnp | grep -E "7443|5061"

# Or using ss
sudo ss -tlnp | grep -E "7443|5061"
```

**Expected output:**
```
tcp  0  0  0.0.0.0:7443  0.0.0.0:*  LISTEN  freeswitch
tcp  0  0  0.0.0.0:5061  0.0.0.0:*  LISTEN  freeswitch
```

## Next Steps: Configure WebRTC Extensions

Now that the WSS profile is running, you need to configure extensions to use WebRTC:

### Step 1: Verify Extension Exists and is Enabled

**Important:** Extensions don't need to be explicitly assigned to the `wss` profile. WebRTC clients connect to the WSS profile directly using their extension credentials. The extension just needs to exist and be enabled.

For extensions that will use WebRTC (like extension 2001, 2002, etc.):

1. **Login to FusionPBX:** `https://136.115.41.45`
2. **Navigate to:** `Accounts → Extensions`
3. **Click on the extension** (e.g., 2001)
4. **Verify the extension is enabled and configured:**
   - Extension number is set (e.g., `2001`)
   - Password is set (needed for SIP authentication)
   - User is assigned to the extension
   - **Save** if you made any changes

**Note:** Extensions can register to **any** SIP profile (internal, external, or wss) as long as:
- The extension credentials are correct
- The extension exists in the directory
- The client connects to the correct profile/port

WebRTC clients automatically use the `wss` profile when connecting via `wss://domain:7443`.

### Step 2: Update WebRTC Client Configuration

Update your WebRTC client code to use the WSS profile:

**Example Configuration:**
```javascript
const sipConfig = {
    domain: '136.115.41.45',
    wss_port: 7443,        // WSS port
    transport: 'wss',      // Use WSS
    // ... other settings
};
```

**URL Format:**
```
wss://136.115.41.45:7443
```

### Step 3: Configure Firewall

Ensure ports are open in your firewall:

```bash
# Open WSS port
sudo ufw allow 7443/tcp

# Open TLS port (if needed)
sudo ufw allow 5061/tcp

# Verify
sudo ufw status | grep -E "7443|5061"
```

### Step 4: Test WebRTC Connection

Test with a WebRTC client:

1. **Use a WebRTC SIP client** (like SIP.js, JsSIP, or your custom client)
2. **Connect to:** `wss://136.115.41.45:7443`
3. **Register with extension:** e.g., `2001@136.115.41.45`
4. **Make a test call** to another extension

### Step 5: Test Direct Transfer from WebRTC to FusionPBX

Now you can test direct transfer from your WebRTC voice assistant to FusionPBX extensions:

**In your WebRTC code:**
```javascript
// Transfer to FusionPBX extension
socketio.emit('transfer_to_extension', {
    extension: '2001',
    domain: '136.115.41.45',
    transport: 'wss',
    wss_port: 7443
});
```

## Troubleshooting

### If Profile Stops Running

```bash
# Restart the profile
fs_cli -x "sofia profile wss restart"

# Check status
fs_cli -x "sofia status profile wss"

# Check logs
tail -50 /var/log/freeswitch/freeswitch.log | grep -i wss
```

### If WebRTC Client Can't Connect

1. **Check firewall:** Ensure port 7443 is open
2. **Check TLS certificate:** Verify `wss.pem` exists and is valid
3. **Check logs:** Look for connection errors in FreeSWITCH logs
4. **Verify domain:** Ensure client uses correct domain (`136.115.41.45`)

### Check WebRTC Registration

```bash
# Check if WebRTC clients are registered
fs_cli -x "sofia status profile wss reg"

# Should show registered endpoints if any WebRTC clients are connected
```

### WebSocket Connection Fails: "WebSocket is closed before the connection is established"

If you see this error in the browser console, check the following:

#### Step 1: Verify Firewall is Open

```bash
# On FusionPBX server
sudo ufw status | grep 7443

# If not open, add rule:
sudo ufw allow 7443/tcp

# Check if port is listening
sudo netstat -tlnp | grep 7443
# Should show: tcp  0  0  0.0.0.0:7443  0.0.0.0:*  LISTEN  freeswitch
```

#### Step 2: Test WebSocket Connection from Server

```bash
# Test if WebSocket port is accessible
curl -k https://136.115.41.45:7443
# Or use wscat if installed
wscat -c wss://136.115.41.45:7443
```

#### Step 3: Check Browser TLS Certificate

If using a self-signed certificate:
1. Open `https://136.115.41.45:7443` in your browser
2. Accept the security warning
3. Click "Advanced" → "Proceed to 136.115.41.45 (unsafe)"
4. Then try the WebRTC client again

#### Step 4: Check FreeSWITCH Logs

```bash
# Enable debug logging
fs_cli -x "console loglevel debug"
fs_cli -x "sofia loglevel all 9"

# Watch logs while attempting connection
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "wss|7443|websocket|tls"
```

Look for errors like:
- `TLS handshake failed`
- `ACL denied`
- `Connection refused`

#### Step 5: Verify WSS Profile ACL Settings

```bash
# Check ACL settings for wss profile
fs_cli -x "sofia xmlstatus profile wss" | grep -i "apply.*acl"

# Should show:
# apply-inbound-acl: domains
# apply-register-acl: domains
```

If ACL is blocking, update via FusionPBX GUI or database.

#### Step 6: Test with Browser Console

Open browser console and test directly:

```javascript
// Test WebSocket connection
let ws = new WebSocket('wss://136.115.41.45:7443');
ws.onopen = () => console.log('✓ WebSocket connected!');
ws.onerror = (err) => console.error('✗ WebSocket error:', err);
ws.onclose = (e) => console.log('WebSocket closed:', e.code, e.reason);
```

**Expected:**
- If firewall is open and certificate accepted: Connection opens
- If firewall blocked: Immediate close with code 1006
- If certificate rejected: Browser may show security warning first

#### Step 7: Check Cloud Provider Firewall (If Applicable)

If FusionPBX is on a cloud provider (AWS, GCP, Azure):

**Google Cloud:**
```bash
# Check firewall rules
gcloud compute firewall-rules list | grep 7443

# Create rule if missing
gcloud compute firewall-rules create allow-fusionpbx-wss \
    --allow tcp:7443 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow FusionPBX WSS WebRTC connections"
```

**AWS:**
- Check Security Groups
- Ensure inbound rule allows TCP port 7443 from 0.0.0.0/0

**Azure:**
- Check Network Security Groups
- Add inbound rule for port 7443

#### Step 8: Verify WSS Profile is Actually Listening

```bash
# Check what's actually listening on port 7443
sudo lsof -i :7443

# Should show freeswitch process
# If nothing shows, the profile isn't actually running
```

---

## Database Configuration Summary

Your wss profile has:
- ✅ **Profile exists:** `v_sip_profiles` table
- ✅ **18 settings configured:** `v_sip_profile_settings` table
- ✅ **Profile enabled:** `sip_profile_enabled = true`
- ✅ **XML file exists:** `/etc/freeswitch/sip_profiles/wss.xml`
- ✅ **TLS certificates configured:** `/etc/freeswitch/tls/wss.pem`

## Important Notes

1. **TLS Certificate:** The `wss.pem` certificate is self-signed. For production, consider using a proper SSL certificate from a CA.

2. **Profile Persistence:** The XML file is manually created. If FusionPBX regenerates profiles from the database, you may need to ensure the database settings are complete.

3. **Both Ports Running:** It's normal to see the wss profile on both port 7443 (WSS) and 5061 (TLS). Both are functional.

## Success Checklist

- ✅ WSS profile running on port 7443
- ✅ TLS profile running on port 5061
- ✅ TLS certificates configured
- ✅ Database settings complete (18 settings)
- ✅ Profile enabled in database
- ✅ XML file exists and is valid
- ✅ Firewall ports configured
- ⏭️ WebRTC client configuration (next step)
- ⏭️ Extension WebRTC setup (next step)
- ⏭️ Test WebRTC connections (next step)

---

**Congratulations! Your FusionPBX WebRTC profile is now operational!** 🎉

You can now configure WebRTC clients to connect directly to FusionPBX and transfer calls from your WebRTC voice assistant to FusionPBX extensions.

## FUSIONPBX_WSS_PROFILE_TROUBLESHOOTING

# FusionPBX WSS Profile Troubleshooting Guide

## Error: "No Such Profile 'wss'"

If you see `[WARNING] sofia.c:6383 No Such Profile 'wss'` even though:
- The profile exists in `v_sip_profiles` table
- The file `/etc/freeswitch/sip_profiles/wss.xml` exists

**The problem:** FreeSWITCH is not loading the profile because:
1. FreeSWITCH reads profiles from a different directory than `/etc/freeswitch/sip_profiles/`
2. The profile settings are missing from the database (`v_sip_profile_settings` table)
3. FreeSWITCH generates profile XML from the database, not from standalone files

**Solution:** Configure the profile via FusionPBX database, not just the file.

### Step 1: Find Where FreeSWITCH Actually Loads Profiles

```bash
# Get FreeSWITCH base directory
fs_cli -x "global_getvar base_dir"

# Check where profiles are actually loaded from
fs_cli -x "global_getvar conf_dir"

# List what profiles FreeSWITCH actually sees
fs_cli -x "sofia status"

# Check internal profile location for reference
ls -la /usr/local/freeswitch/conf/sip_profiles/internal.xml 2>/dev/null
ls -la /opt/freeswitch/conf/sip_profiles/internal.xml 2>/dev/null
ls -la $(fs_cli -x "global_getvar conf_dir" | tail -1)/sip_profiles/ 2>/dev/null
```

### Step 2: Check if Profile Settings Exist in Database

The profile may exist in `v_sip_profiles` but have no settings:

```bash
# Get the profile UUID
PROFILE_UUID=$(sudo -u postgres psql fusionpbx -t -c "SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'wss';" | xargs)
echo "Profile UUID: $PROFILE_UUID"

# Check if any settings exist
sudo -u postgres psql fusionpbx -c "SELECT COUNT(*) as setting_count FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID';"

# List all settings (should show multiple rows)
sudo -u postgres psql fusionpbx -c "SELECT sip_profile_setting_name, sip_profile_setting_value FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' ORDER BY sip_profile_setting_name;"
```

### Step 3: Add Missing Profile Settings to Database

If no settings exist, you need to add them. FusionPBX generates the XML from the database:

```bash
# Get profile UUID
PROFILE_UUID=$(sudo -u postgres psql fusionpbx -t -c "SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'wss';" | xargs)

# Insert all required settings at once
sudo -u postgres psql fusionpbx << EOF
-- Core settings
INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
VALUES 
  (gen_random_uuid(), '$PROFILE_UUID', 'name', 'wss', 'true')
  ON CONFLICT DO NOTHING;

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'sip-ip', '0.0.0.0', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'sip-ip');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'sip-port', '7443', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'sip-port');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'tls', 'true', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'tls');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'tls-bind-params', 'transport=wss', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'tls-bind-params');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'ext-sip-ip', '136.115.41.45', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'ext-sip-ip');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'ext-rtp-ip', '136.115.41.45', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'ext-rtp-ip');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'domain', '136.115.41.45', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'domain');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'codec-prefs', 'G722,PCMU,PCMA', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'codec-prefs');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'rtp-ip', '0.0.0.0', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'rtp-ip');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'rtp-min-port', '16384', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'rtp-min-port');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'rtp-max-port', '32768', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'rtp-max-port');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'local-network-acl', 'localnet.auto', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'local-network-acl');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'apply-nat-acl', 'nat.auto', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'apply-nat-acl');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'apply-inbound-acl', 'domains', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'apply-inbound-acl');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'apply-register-acl', 'domains', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'apply-register-acl');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'bypass-media', 'false', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'bypass-media');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'media-bypass', 'false', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'media-bypass');
EOF

echo "✅ Profile settings added to database"
```

### Step 4: Regenerate XML from Database

After adding settings, force FusionPBX to regenerate the XML:

```bash
# Reload XML (this should regenerate profiles from database)
fs_cli -x "reloadxml"

# Wait a moment
sleep 2

# Check if profile is now visible
fs_cli -x "sofia status" | grep -i wss

# Try to start
fs_cli -x "sofia profile wss start"
fs_cli -x "sofia status profile wss"
```

### Step 5: Verify Profile Location

Check where the profile XML was actually generated:

```bash
# Find where FreeSWITCH actually loads profiles from
CONF_DIR=$(fs_cli -x "global_getvar conf_dir" | tail -1)
echo "FreeSWITCH conf directory: $CONF_DIR"

# Check if wss.xml was generated there
ls -la "$CONF_DIR/sip_profiles/wss.xml"

# If it exists, check its contents
cat "$CONF_DIR/sip_profiles/wss.xml"
```

---

## Still Failing After Adding Database Settings?

If you've added all settings to the database but still get "Invalid Profile!" or "Failure starting wss", follow these diagnostic steps:

### Diagnostic Step 1: Check Where FreeSWITCH Actually Loads Profiles

```bash
# Get FreeSWITCH base and config directories
fs_cli -x "global_getvar base_dir"
fs_cli -x "global_getvar conf_dir"

# Check common locations
ls -la /etc/freeswitch/sip_profiles/wss.xml 2>/dev/null
ls -la /usr/local/freeswitch/conf/sip_profiles/wss.xml 2>/dev/null
ls -la /opt/freeswitch/conf/sip_profiles/wss.xml 2>/dev/null
ls -la $(fs_cli -x "global_getvar conf_dir" | tail -1)/sip_profiles/wss.xml 2>/dev/null
```

### Diagnostic Step 2: Check if FusionPBX Generated the XML

FusionPBX may need explicit triggering to generate the XML from the database:

```bash
# Check if FusionPBX has a PHP script to regenerate XML
find /var/www/fusionpbx -name "*.php" | xargs grep -l "sip_profiles\|sofia.*xml" | head -5

# Or check if there's a FusionPBX CLI command
fwconsole reload 2>/dev/null || echo "fwconsole not available"

# Check if there's a specific reload command
fs_cli -x "reload mod_sofia"
```

### Diagnostic Step 3: Check the Generated XML File

If the XML file exists, check if it's valid:

```bash
# Find the XML file (try all locations)
XML_FILE=$(find /etc/freeswitch /usr/local/freeswitch/conf /opt/freeswitch/conf 2>/dev/null | grep "sip_profiles/wss.xml" | head -1)

if [ -n "$XML_FILE" ]; then
    echo "Found XML file at: $XML_FILE"
    cat "$XML_FILE"
    
    # Check if it's valid XML
    xmllint --noout "$XML_FILE" 2>&1 || echo "⚠️ XML validation failed"
else
    echo "❌ XML file not found - FusionPBX may not have generated it"
fi
```

### Diagnostic Step 4: Get Detailed Error from Logs

```bash
# Enable maximum logging
fs_cli -x "console loglevel debug"
fs_cli -x "sofia loglevel all 9"

# Try to start the profile
fs_cli -x "sofia profile wss start"

# Immediately check logs for detailed error
tail -100 /var/log/freeswitch/freeswitch.log | grep -A 10 -B 10 -iE "wss|error|fail|invalid" | tail -30

# Check specifically for XML parsing errors
tail -200 /var/log/freeswitch/freeswitch.log | grep -iE "xml|parse|syntax" | tail -20
```

### Diagnostic Step 4A: Verify FreeSWITCH Sees the Profile During reloadxml

Even if the XML file exists, FreeSWITCH might not be loading it. Check if it's being parsed:

```bash
# Watch the log file in real-time while reloading
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "wss|profile|sip_profiles" &
TAIL_PID=$!

# Reload XML
fs_cli -x "reloadxml"

# Wait a moment
sleep 3

# Kill the tail process
kill $TAIL_PID 2>/dev/null

# Check what profiles FreeSWITCH actually sees
fs_cli -x "sofia status" | head -20
```

### Diagnostic Step 4B: Check sofia.conf.xml Configuration

FusionPBX may use `sofia.conf.xml` to control which profiles are loaded. Check if wss needs to be explicitly included:

```bash
# Find sofia.conf.xml
SOFIA_CONF=$(find /etc/freeswitch -name "sofia.conf.xml" 2>/dev/null | head -1)

if [ -n "$SOFIA_CONF" ]; then
    echo "Found sofia.conf.xml at: $SOFIA_CONF"
    echo "--- Contents ---"
    cat "$SOFIA_CONF"
    
    # Check if profiles are explicitly listed
    echo ""
    echo "--- Profile references ---"
    grep -iE "profile|external|internal|wss" "$SOFIA_CONF"
else
    echo "Could not find sofia.conf.xml in /etc/freeswitch"
    
    # Check autoload_configs directory
    ls -la /etc/freeswitch/autoload_configs/ | grep sofia
fi
```

### Diagnostic Step 4C: Check How FusionPBX Generates Profile XML

FusionPBX might use a PHP script to generate profiles. Check if it's generating them correctly:

```bash
# Find FusionPBX XML generation scripts
find /var/www/fusionpbx -name "*.php" 2>/dev/null | xargs grep -l "sip_profiles\|sofia.*profile" 2>/dev/null | head -5

# Check if there's a specific include mechanism
grep -r "wss\|external\|internal" /etc/freeswitch/autoload_configs/*.xml 2>/dev/null | head -10
```

### Diagnostic Step 4D: Verify XML is Actually Being Read

Check if FreeSWITCH is attempting to read the file:

```bash
# Use strace to see if FreeSWITCH opens the file (if available)
if command -v strace >/dev/null 2>&1; then
    FS_PID=$(pgrep freeswitch | head -1)
    if [ -n "$FS_PID" ]; then
        echo "Watching FreeSWITCH process $FS_PID for file operations..."
        timeout 5 strace -p $FS_PID -e open,openat 2>&1 | grep -i "wss.xml\|sip_profiles" || echo "No file operations detected"
    fi
else
    echo "strace not available"
fi

# Alternative: Check file access times
echo "File access time before reload:"
stat /etc/freeswitch/sip_profiles/wss.xml | grep Access

# Reload
fs_cli -x "reloadxml"

sleep 2

echo "File access time after reload:"
stat /etc/freeswitch/sip_profiles/wss.xml | grep Access
```

---

### Diagnostic Step 5: Check if Profile is Listed in sofia.conf.xml

FreeSWITCH might need the profile to be explicitly listed in `sofia.conf.xml`:

```bash
# Find sofia.conf.xml
SOFIA_CONF=$(find /etc/freeswitch /usr/local/freeswitch/conf /opt/freeswitch/conf 2>/dev/null | grep "autoload_configs/sofia.conf.xml" | head -1)

if [ -n "$SOFIA_CONF" ]; then
    echo "Found sofia.conf.xml at: $SOFIA_CONF"
    cat "$SOFIA_CONF" | grep -A 5 -B 5 "wss\|external\|internal"
else
    echo "Could not find sofia.conf.xml"
fi
```

### Diagnostic Step 6: Manually Generate XML from Database

If FusionPBX isn't generating the XML automatically, you can manually create it:

```bash
# Get all settings from database
PROFILE_UUID=$(sudo -u postgres psql fusionpbx -t -c "SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'wss';" | xargs)

# Generate XML file from database settings
sudo tee /etc/freeswitch/sip_profiles/wss.xml > /dev/null << 'XML_EOF'
<profile name="wss">
  <settings>
XML_EOF

# Add each setting from database
sudo -u postgres psql fusionpbx -t -c "SELECT '<param name=\"' || sip_profile_setting_name || '\" value=\"' || sip_profile_setting_value || '\"/>' FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_enabled = 'true' ORDER BY sip_profile_setting_name;" | sed 's/^/    /' >> /etc/freeswitch/sip_profiles/wss.xml

# Close the XML
sudo tee -a /etc/freeswitch/sip_profiles/wss.xml > /dev/null << 'XML_EOF'
  </settings>
</profile>
XML_EOF

# Fix permissions
FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
FS_USER=${FS_USER:-www-data}
sudo chown $FS_USER:$FS_USER /etc/freeswitch/sip_profiles/wss.xml
sudo chmod 644 /etc/freeswitch/sip_profiles/wss.xml

# Verify XML
cat /etc/freeswitch/sip_profiles/wss.xml
xmllint --noout /etc/freeswitch/sip_profiles/wss.xml && echo "✅ XML is valid"

# Reload and try again
fs_cli -x "reloadxml"
sleep 2
fs_cli -x "sofia profile wss start"
fs_cli -x "sofia status profile wss"
```

### Diagnostic Step 7: Check Profile is Enabled in Database

```bash
# Verify profile is enabled
sudo -u postgres psql fusionpbx -c "SELECT sip_profile_name, sip_profile_enabled FROM v_sip_profiles WHERE sip_profile_name = 'wss';"

# If not enabled, enable it
sudo -u postgres psql fusionpbx -c "UPDATE v_sip_profiles SET sip_profile_enabled = 'true' WHERE sip_profile_name = 'wss';"
```

### Diagnostic Step 8: Try via FusionPBX GUI

Sometimes the GUI trigger is needed for FusionPBX to recognize the profile:

1. **Login to FusionPBX:** `https://136.115.41.45`
2. **Navigate to:** `Advanced → SIP Profiles`
3. **Look for "wss" profile** - if it's there, click on it
4. **If it's NOT there**, the profile may not be fully recognized by FusionPBX
5. **Try clicking "Add" or "+"** to create a new profile named "wss"
6. **Or use the GUI to edit settings** - this might trigger XML regeneration
7. **Go to:** `Status → SIP Status`
8. **Find "wss" profile and click "Reload XML" and "Restart"**

---

# Troubleshooting: wss Profile Fails to Start

## Your Current Issue

- ✅ `wss.xml` file exists at `/etc/freeswitch/sip_profiles/wss.xml`
- ❌ Profile fails to start: "Failure starting wss"
- ❌ `chown freeswitch:freeswitch` fails (user doesn't exist)
- ❌ File not found in standard FreeSWITCH locations

## Diagnostic Steps

### Step 1: Find the Correct FreeSWITCH User

```bash
# Check what user FreeSWITCH runs as
ps aux | grep freeswitch | grep -v grep

# Check systemd service file
systemctl status freeswitch
cat /etc/systemd/system/freeswitch.service | grep User

# OR check init script
cat /etc/init.d/freeswitch | grep USER

# Common FreeSWITCH users:
# - www-data (Debian/Ubuntu with FusionPBX)
# - freeswitch (if installed from source)
# - daemon (some installations)
```

### Step 2: Find the Correct FreeSWITCH Configuration Directory

```bash
# Check where FreeSWITCH is actually installed
which freeswitch
whereis freeswitch

# Check FreeSWITCH CLI for config path
fs_cli -x "global_getvar base_dir"
fs_cli -x "global_getvar conf_dir"

# Check running process for config location
ps aux | grep freeswitch | grep -o '\-conf [^ ]*'

# Common locations:
# - /usr/local/freeswitch/
# - /opt/freeswitch/
# - /var/lib/freeswitch/
# - /etc/freeswitch/ (FusionPBX default)
```

### Step 3: Check FreeSWITCH Logs for Error Details

```bash
# Check recent errors
tail -100 /var/log/freeswitch/freeswitch.log | grep -i wss
tail -100 /var/log/freeswitch/freeswitch.log | grep -i error
tail -100 /var/log/freeswitch/freeswitch.log | grep -i 7443

# Check for TLS certificate errors
tail -100 /var/log/freeswitch/freeswitch.log | grep -i tls
tail -100 /var/log/freeswitch/freeswitch.log | grep -i certificate

# Enable debug logging and try again
fs_cli -x "console loglevel debug"
fs_cli -x "sofia loglevel all 9"
fs_cli -x "sofia profile wss start"
tail -50 /var/log/freeswitch/freeswitch.log
```

### Step 4: Check if wss Profile is in FusionPBX Database

```bash
# Complete the database query (if it was interrupted)
sudo -u postgres psql fusionpbx -c "SELECT * FROM v_sip_profiles WHERE sip_profile_name = 'wss';"

# If it doesn't exist, create it:
sudo -u postgres psql fusionpbx << EOF
INSERT INTO v_sip_profiles (sip_profile_uuid, sip_profile_name, sip_profile_enabled, sip_profile_description)
SELECT gen_random_uuid(), 'wss', 'true', 'WebRTC WebSocket Secure Profile'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profiles WHERE sip_profile_name = 'wss');
EOF
```

### Step 5: Verify File Location and Permissions

Since FusionPBX uses `/etc/freeswitch/` as the config directory, that's likely correct. But we need to fix permissions:

```bash
# Find the correct user (most likely www-data for FusionPBX)
FS_USER=$(ps aux | grep freeswitch | grep -v grep | awk '{print $1}' | head -1)
echo "FreeSWITCH runs as user: $FS_USER"

# Fix ownership
sudo chown $FS_USER:$FS_USER /etc/freeswitch/sip_profiles/wss.xml
sudo chmod 644 /etc/freeswitch/sip_profiles/wss.xml

# Verify
ls -la /etc/freeswitch/sip_profiles/wss.xml
```

### Step 6: Check TLS Certificate Configuration

The wss profile requires a TLS certificate. Check if it's configured:

```bash
# Check if TLS certificate exists
ls -la /etc/freeswitch/tls/*.pem
ls -la /etc/freeswitch/tls/wss.*

# Check FreeSWITCH TLS directory
find /etc/freeswitch -name "*.pem" -o -name "*.crt" -o -name "*.key" 2>/dev/null

# Check what certificate FreeSWITCH is using
fs_cli -x "sofia xmlstatus profile internal" | grep -i cert
```

### Step 7: Check Port 7443 Availability

```bash
# Check if port 7443 is already in use
sudo lsof -i :7443
sudo netstat -tlnp | grep 7443
sudo ss -tlnp | grep 7443

# If something else is using it, identify and stop it
```

## Solution Steps

### Fix 1: Correct File Permissions (Most Likely Issue)

```bash
# Determine the correct user
FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
FS_GROUP=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)

# If that doesn't work, try common ones:
# For FusionPBX on Debian/Ubuntu, it's usually www-data
FS_USER="www-data"
FS_GROUP="www-data"

# Fix ownership
sudo chown $FS_USER:$FS_GROUP /etc/freeswitch/sip_profiles/wss.xml
sudo chmod 644 /etc/freeswitch/sip_profiles/wss.xml

# Verify
ls -la /etc/freeswitch/sip_profiles/wss.xml
```

### Fix 2: Add TLS Certificate Configuration

The wss profile needs TLS certificate settings. Add them to the wss.xml file:

```bash
# Backup the current file
sudo cp /etc/freeswitch/sip_profiles/wss.xml /etc/freeswitch/sip_profiles/wss.xml.backup

# Check if certificate exists
if [ -f /etc/freeswitch/tls/wss.pem ]; then
    CERT_FILE="/etc/freeswitch/tls/wss.pem"
elif [ -f /etc/freeswitch/tls/cert.pem ]; then
    CERT_FILE="/etc/freeswitch/tls/cert.pem"
elif [ -f /etc/freeswitch/tls/tls.pem ]; then
    CERT_FILE="/etc/freeswitch/tls/tls.pem"
else
    echo "Certificate not found. Need to create one."
    CERT_FILE="/etc/freeswitch/tls/wss.pem"
fi

echo "Using certificate: $CERT_FILE"

# Generate certificate if it doesn't exist
if [ ! -f "$CERT_FILE" ]; then
    sudo mkdir -p /etc/freeswitch/tls
    cd /etc/freeswitch/tls
    sudo openssl req -x509 -newkey rsa:4096 -keyout wss.pem -out wss.pem -days 365 -nodes -subj "/CN=136.115.41.45"
    sudo chown $FS_USER:$FS_GROUP wss.pem
    sudo chmod 600 wss.pem
fi

# Update wss.xml to include TLS certificate settings
sudo tee /etc/freeswitch/sip_profiles/wss.xml > /dev/null << 'EOF'
<profile name="wss">
  <settings>
    <param name="name" value="wss"/>
    <param name="sip-ip" value="0.0.0.0"/>
    <param name="sip-port" value="7443"/>
    <param name="tls" value="true"/>
    <param name="tls-bind-params" value="transport=wss"/>
    <param name="tls-cert-dir" value="$${base_dir}/conf/tls"/>
    <param name="tls-cert-file" value="$${base_dir}/conf/tls/wss.pem"/>
    <param name="tls-key-file" value="$${base_dir}/conf/tls/wss.pem"/>
    <param name="tls-ca-file" value="$${base_dir}/conf/tls/cafile.pem"/>
    <param name="ext-sip-ip" value="136.115.41.45"/>
    <param name="ext-rtp-ip" value="136.115.41.45"/>
    <param name="domain" value="136.115.41.45"/>
    <param name="codec-prefs" value="G722,PCMU,PCMA"/>
    <param name="rtp-ip" value="0.0.0.0"/>
    <param name="rtp-min-port" value="16384"/>
    <param name="rtp-max-port" value="32768"/>
    <param name="local-network-acl" value="localnet.auto"/>
    <param name="apply-nat-acl" value="nat.auto"/>
    <param name="apply-inbound-acl" value="domains"/>
    <param name="apply-register-acl" value="domains"/>
    <param name="bypass-media" value="false"/>
    <param name="media-bypass" value="false"/>
  </settings>
</profile>
EOF

# Fix permissions again
sudo chown $FS_USER:$FS_GROUP /etc/freeswitch/sip_profiles/wss.xml
```

### Fix 3: Ensure Profile Exists in Database

```bash
# Check if profile exists in database
sudo -u postgres psql fusionpbx -c "SELECT sip_profile_name, sip_profile_enabled FROM v_sip_profiles WHERE sip_profile_name = 'wss';"

# If it doesn't exist, create it
sudo -u postgres psql fusionpbx << 'SQL'
INSERT INTO v_sip_profiles (sip_profile_uuid, sip_profile_name, sip_profile_enabled, sip_profile_description)
SELECT gen_random_uuid(), 'wss', 'true', 'WebRTC Profile' WHERE NOT EXISTS (SELECT 1 FROM v_sip_profiles WHERE sip_profile_name = 'wss');
SQL

# Verify it was created
sudo -u postgres psql fusionpbx -c "SELECT sip_profile_name, sip_profile_enabled FROM v_sip_profiles WHERE sip_profile_name = 'wss';"
```

### Fix 4: Reload and Start Profile

```bash
# Reload XML configuration
fs_cli -x "reloadxml"

# Try starting the profile
fs_cli -x "sofia profile wss start"

# Check status
fs_cli -x "sofia status profile wss"

# Check for errors in logs
tail -50 /var/log/freeswitch/freeswitch.log | grep -i wss
```

## Quick Diagnostic Script

Run this complete diagnostic script:

```bash
#!/bin/bash
echo "=== FreeSWITCH wss Profile Diagnostic ==="
echo ""

echo "1. FreeSWITCH Process Information:"
ps aux | grep '[f]reeswitch' | head -3
echo ""

echo "2. FreeSWITCH User:"
FS_USER=$(ps aux | grep '[f]reeswitch' | grep -v grep | awk '{print $1}' | head -1)
echo "   User: $FS_USER"
echo ""

echo "3. Configuration Directory:"
fs_cli -x "global_getvar base_dir" 2>/dev/null || echo "   Cannot determine (fs_cli may not be accessible)"
fs_cli -x "global_getvar conf_dir" 2>/dev/null || echo "   Cannot determine"
echo ""

echo "4. File Existence:"
ls -la /etc/freeswitch/sip_profiles/wss.xml 2>/dev/null && echo "   ✅ wss.xml exists" || echo "   ❌ wss.xml not found"
echo ""

echo "5. File Permissions:"
ls -la /etc/freeswitch/sip_profiles/wss.xml | awk '{print "   Owner: "$3":"$4" Permissions: "$1}'
echo ""

echo "6. TLS Certificate Check:"
if [ -f /etc/freeswitch/tls/wss.pem ]; then
    echo "   ✅ wss.pem exists"
    ls -la /etc/freeswitch/tls/wss.pem | awk '{print "   Permissions: "$1" Owner: "$3":"$4}'
else
    echo "   ❌ wss.pem not found"
    echo "   Checking for other certificates:"
    ls -la /etc/freeswitch/tls/*.pem 2>/dev/null || echo "   No .pem files found"
fi
echo ""

echo "7. Port 7443 Status:"
if lsof -i :7443 2>/dev/null | grep -q LISTEN; then
    echo "   ⚠️  Port 7443 is already in use:"
    lsof -i :7443
else
    echo "   ✅ Port 7443 is available"
fi
echo ""

echo "8. Profile Status:"
fs_cli -x "sofia status" 2>/dev/null | grep wss || echo "   wss profile not listed"
echo ""

echo "9. Recent Log Errors:"
tail -30 /var/log/freeswitch/freeswitch.log 2>/dev/null | grep -iE "wss|7443|error|failure" | tail -5 || echo "   No recent errors found"
echo ""

echo "10. Database Status:"
sudo -u postgres psql fusionpbx -t -c "SELECT sip_profile_name, sip_profile_enabled FROM v_sip_profiles WHERE sip_profile_name = 'wss';" 2>/dev/null || echo "   Cannot check database"
echo ""

echo "=== Diagnostic Complete ==="
```

Save this as `diagnose_wss.sh`, make it executable, and run it:
```bash
chmod +x diagnose_wss.sh
sudo ./diagnose_wss.sh
```

## Most Common Issues and Quick Fixes

### Issue 1: Wrong File Ownership

```bash
# Quick fix - set to www-data (common for FusionPBX)
sudo chown www-data:www-data /etc/freeswitch/sip_profiles/wss.xml
sudo chmod 644 /etc/freeswitch/sip_profiles/wss.xml
```

### Issue 2: Missing TLS Certificate

```bash
# Generate certificate
sudo mkdir -p /etc/freeswitch/tls
cd /etc/freeswitch/tls
FS_USER=$(ps aux | grep '[f]reeswitch' | grep -v grep | awk '{print $1}' | head -1)
FS_USER=${FS_USER:-www-data}
sudo openssl req -x509 -newkey rsa:4096 -keyout wss.pem -out wss.pem -days 365 -nodes -subj "/CN=136.115.41.45"
sudo chown $FS_USER:$FS_USER wss.pem
sudo chmod 600 wss.pem
```

### Issue 3: Profile Not in Database

```bash
# Add to database
sudo -u postgres psql fusionpbx -c "INSERT INTO v_sip_profiles (sip_profile_uuid, sip_profile_name, sip_profile_enabled, sip_profile_description) SELECT gen_random_uuid(), 'wss', 'true', 'WebRTC Profile' WHERE NOT EXISTS (SELECT 1 FROM v_sip_profiles WHERE sip_profile_name = 'wss');"
fs_cli -x "reloadxml"
```

### Issue 4: Port Conflict

```bash
# Find what's using port 7443
sudo lsof -i :7443
# Kill if needed (replace PID with actual process ID)
# sudo kill -9 <PID>
```

## Expected Resolution Steps

1. **Identify the correct FreeSWITCH user** (likely `www-data`)
2. **Fix file permissions** with the correct user
3. **Generate TLS certificate** if missing
4. **Add TLS certificate settings** to wss.xml
5. **Ensure profile exists in database**
6. **Reload and start the profile**

Run the diagnostic script first to identify the exact issue, then apply the appropriate fix.

---

## Profile Exists in Database But Still Fails to Start

If the wss profile exists in `v_sip_profiles` table but still fails to start, follow these steps:

### Step 1: Check the Actual Error from Logs

```bash
# Enable debug logging and try to start
fs_cli -x "console loglevel debug"
fs_cli -x "sofia loglevel all 9"
fs_cli -x "sofia profile wss start"

# Immediately check logs for the error
tail -100 /var/log/freeswitch/freeswitch.log | grep -iE "wss|7443|error|failure|certificate|tls" | tail -20
```

### Step 2: Fix File Permissions

```bash
# Find the correct FreeSWITCH user
FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
echo "FreeSWITCH user: $FS_USER"

# If empty or root, use www-data (common for FusionPBX)
if [ -z "$FS_USER" ] || [ "$FS_USER" = "root" ]; then
    FS_USER="www-data"
fi

# Fix ownership
sudo chown $FS_USER:$FS_USER /etc/freeswitch/sip_profiles/wss.xml
sudo chmod 644 /etc/freeswitch/sip_profiles/wss.xml

# Verify
ls -la /etc/freeswitch/sip_profiles/wss.xml
```

### Step 3: Check and Generate TLS Certificate

```bash
# Check if TLS certificate exists
ls -la /etc/freeswitch/tls/*.pem 2>/dev/null

# Check what certificates FreeSWITCH uses
fs_cli -x "sofia xmlstatus profile internal" | grep -i cert

# Generate wss.pem if it doesn't exist
if [ ! -f /etc/freeswitch/tls/wss.pem ]; then
    sudo mkdir -p /etc/freeswitch/tls
    cd /etc/freeswitch/tls
    
    FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
    FS_USER=${FS_USER:-www-data}
    
    sudo openssl req -x509 -newkey rsa:4096 -keyout wss.pem -out wss.pem -days 365 -nodes -subj "/CN=136.115.41.45"
    sudo chown $FS_USER:$FS_USER wss.pem
    sudo chmod 600 wss.pem
    
    echo "✅ Certificate created: /etc/freeswitch/tls/wss.pem"
else
    echo "✅ Certificate exists: /etc/freeswitch/tls/wss.pem"
fi
```

### Step 4: Update wss.xml with TLS Certificate Paths

The wss.xml file may need explicit TLS certificate paths. Update it:

```bash
# Backup current file
sudo cp /etc/freeswitch/sip_profiles/wss.xml /etc/freeswitch/sip_profiles/wss.xml.backup

# Find FreeSWITCH base directory
FS_BASE=$(fs_cli -x "global_getvar base_dir" 2>/dev/null)
FS_BASE=${FS_BASE:-/usr/local/freeswitch}

echo "FreeSWITCH base directory: $FS_BASE"

# Update wss.xml with complete configuration including TLS paths
sudo tee /etc/freeswitch/sip_profiles/wss.xml > /dev/null << 'EOF'
<profile name="wss">
  <settings>
    <param name="name" value="wss"/>
    <param name="sip-ip" value="0.0.0.0"/>
    <param name="sip-port" value="7443"/>
    <param name="tls" value="true"/>
    <param name="tls-bind-params" value="transport=wss"/>
    <param name="ext-sip-ip" value="136.115.41.45"/>
    <param name="ext-rtp-ip" value="136.115.41.45"/>
    <param name="domain" value="136.115.41.45"/>
    <param name="codec-prefs" value="G722,PCMU,PCMA"/>
    <param name="rtp-ip" value="0.0.0.0"/>
    <param name="rtp-min-port" value="16384"/>
    <param name="rtp-max-port" value="32768"/>
    <param name="local-network-acl" value="localnet.auto"/>
    <param name="apply-nat-acl" value="nat.auto"/>
    <param name="apply-inbound-acl" value="domains"/>
    <param name="apply-register-acl" value="domains"/>
    <param name="bypass-media" value="false"/>
    <param name="media-bypass" value="false"/>
  </settings>
</profile>
EOF

# Fix permissions again
FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
FS_USER=${FS_USER:-www-data}
sudo chown $FS_USER:$FS_USER /etc/freeswitch/sip_profiles/wss.xml
sudo chmod 644 /etc/freeswitch/sip_profiles/wss.xml
```

### Step 5: Reload XML and Start Profile

```bash
# Reload XML configuration
fs_cli -x "reloadxml"

# Wait a moment
sleep 2

# Try to start the profile
fs_cli -x "sofia profile wss start"

# Check status
fs_cli -x "sofia status profile wss"
```

### Step 6: If Still Failing, Check Detailed Error

```bash
# Get detailed error from logs
tail -200 /var/log/freeswitch/freeswitch.log | grep -A 5 -B 5 -iE "wss|7443" | tail -30

# Try with maximum logging
fs_cli -x "console loglevel debug"
fs_cli -x "sofia loglevel all 9"
fs_cli -x "reloadxml"
fs_cli -x "sofia profile wss start"
sleep 1
tail -50 /var/log/freeswitch/freeswitch.log | grep -iE "wss|error|fail"
```

### Step 7: Check Port Availability

```bash
# Check if port 7443 is available
sudo lsof -i :7443
sudo netstat -tlnp | grep 7443

# If something is using it, you'll need to stop it first
```

### Step 8: Alternative - Check if Profile is Enabled in Settings

Sometimes FusionPBX needs the profile settings to be configured even if the profile exists:

```bash
# Check if there are any settings for the wss profile
sudo -u postgres psql fusionpbx -c "SELECT sip_profile_setting_name, sip_profile_setting_value FROM v_sip_profile_settings WHERE sip_profile_uuid = (SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'wss');"
```

If no settings exist, you may need to add them via FusionPBX GUI or add them manually to the database.

---

## Complete Fix Script (Run All at Once)

If you want to run everything at once, use this script:

```bash
#!/bin/bash
echo "=== Fixing wss Profile ==="

# Step 1: Find FreeSWITCH user
FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
FS_USER=${FS_USER:-www-data}
echo "Using user: $FS_USER"

# Step 2: Fix file permissions
echo "Fixing file permissions..."
sudo chown $FS_USER:$FS_USER /etc/freeswitch/sip_profiles/wss.xml
sudo chmod 644 /etc/freeswitch/sip_profiles/wss.xml

# Step 3: Ensure TLS certificate exists
echo "Checking TLS certificate..."
if [ ! -f /etc/freeswitch/tls/wss.pem ]; then
    sudo mkdir -p /etc/freeswitch/tls
    cd /etc/freeswitch/tls
    sudo openssl req -x509 -newkey rsa:4096 -keyout wss.pem -out wss.pem -days 365 -nodes -subj "/CN=136.115.41.45"
    sudo chown $FS_USER:$FS_USER wss.pem
    sudo chmod 600 wss.pem
    echo "✅ Certificate created"
else
    echo "✅ Certificate exists"
fi

# Step 4: Reload and start
echo "Reloading XML..."
fs_cli -x "reloadxml"
sleep 2

echo "Starting wss profile..."
fs_cli -x "sofia profile wss start"
sleep 2

# Step 5: Check status
echo ""
echo "=== Status Check ==="
fs_cli -x "sofia status profile wss"

# Step 6: Check for errors
echo ""
echo "=== Recent Errors ==="
tail -30 /var/log/freeswitch/freeswitch.log | grep -iE "wss|7443|error" | tail -5

echo ""
echo "=== Fix Complete ==="
```

Save as `fix_wss.sh`, make executable, and run:
```bash
chmod +x fix_wss.sh
sudo ./fix_wss.sh
```

---

### Most Likely Fix: Ensure Database Settings Trigger XML Generation

Since FusionPBX generates profiles from the database, ensure all required settings exist and trigger regeneration:

```bash
# Verify all settings are in database
PROFILE_UUID=$(sudo -u postgres psql fusionpbx -t -c "SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'wss';" | xargs)
sudo -u postgres psql fusionpbx -c "SELECT sip_profile_setting_name, sip_profile_setting_value FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_enabled = 'true' ORDER BY sip_profile_setting_name;"

# Check if profile is enabled
sudo -u postgres psql fusionpbX -c "SELECT sip_profile_name, sip_profile_enabled FROM v_sip_profiles WHERE sip_profile_name = 'wss';"

# If profile is disabled, enable it
sudo -u postgres psql fusionpbx -c "UPDATE v_sip_profiles SET sip_profile_enabled = 'true' WHERE sip_profile_name = 'wss';"

# Then trigger regeneration via GUI or find the PHP script
```

### 🔧 DIRECT FIX: XML File Exists But Not Loading

If `wss.xml` exists in `/etc/freeswitch/sip_profiles/` but FreeSWITCH still can't see it, the XML might be failing to parse silently. Common issues:

#### Issue 1: Missing TLS Certificate Configuration

WSS profiles require TLS certificates. Add TLS certificate paths to your XML:

```bash
# Check if TLS certificates exist
ls -la /etc/freeswitch/tls/*.pem

# Get FreeSWITCH base directory for certificate paths
BASE_DIR=$(fs_cli -x "global_getvar base_dir" | tail -1)
echo "Base dir: $BASE_DIR"

# Update wss.xml with TLS certificate configuration
sudo tee /etc/freeswitch/sip_profiles/wss.xml > /dev/null << EOF
<profile name="wss">
  <settings>
    <param name="name" value="wss"/>
    <param name="sip-ip" value="0.0.0.0"/>
    <param name="sip-port" value="7443"/>
    <param name="tls" value="true"/>
    <param name="tls-bind-params" value="transport=wss"/>
    <param name="tls-cert-dir" value="\$\${base_dir}/conf/tls"/>
    <param name="tls-cert-file" value="\$\${base_dir}/conf/tls/wss.pem"/>
    <param name="tls-key-file" value="\$\${base_dir}/conf/tls/wss.pem"/>
    <param name="ext-sip-ip" value="136.115.41.45"/>
    <param name="ext-rtp-ip" value="136.115.41.45"/>
    <param name="domain" value="136.115.41.45"/>
    <param name="codec-prefs" value="G722,PCMU,PCMA"/>
    <param name="rtp-ip" value="0.0.0.0"/>
    <param name="rtp-min-port" value="16384"/>
    <param name="rtp-max-port" value="32768"/>
    <param name="local-network-acl" value="localnet.auto"/>
    <param name="apply-nat-acl" value="nat.auto"/>
    <param name="apply-inbound-acl" value="domains"/>
    <param name="apply-register-acl" value="domains"/>
    <param name="bypass-media" value="false"/>
    <param name="media-bypass" value="false"/>
  </settings>
</profile>
EOF

# Fix permissions
FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
FS_USER=${FS_USER:-www-data}
sudo chown $FS_USER:$FS_USER /etc/freeswitch/sip_profiles/wss.xml
sudo chmod 644 /etc/freeswitch/sip_profiles/wss.xml

# Reload and try
fs_cli -x "reloadxml"
sleep 2
fs_cli -x "sofia profile wss start"
fs_cli -x "sofia status profile wss"
```

#### Issue 2: Check for XML Parsing Errors

Enable XML debug logging to see if there are parsing errors:

```bash
# Enable XML debug
fs_cli -x "console loglevel debug"
fs_cli -x "loglevel 7"

# Reload XML and watch for errors
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "wss|xml|parse|error|syntax" &
TAIL_PID=$!

fs_cli -x "reloadxml"
sleep 3
kill $TAIL_PID

# Check for specific XML parsing errors
tail -100 /var/log/freeswitch/freeswitch.log | grep -A 5 -B 5 -iE "wss|xml.*error|parse.*error" | tail -20
```

#### Issue 3: Verify XML is Being Included

Check if the XML file is actually being read during reloadxml:

```bash
# Check file permissions
ls -la /etc/freeswitch/sip_profiles/wss.xml

# Verify the include pattern matches
echo "Checking if wss.xml matches include pattern..."
ls -1 /etc/freeswitch/sip_profiles/*.xml | grep -v "\.noload"

# Check if wss.xml is listed
ls -1 /etc/freeswitch/sip_profiles/*.xml | grep wss

# Test XML syntax manually (if xmllint is available)
which xmllint && xmllint --noout /etc/freeswitch/sip_profiles/wss.xml || echo "xmllint not available - checking manually..."

# Check for common XML issues
grep -n "<param\|</param\|<profile\|</profile\|<settings\|</settings" /etc/freeswitch/sip_profiles/wss.xml
```

#### Issue 4: Profile Not Appearing in sofia status After reloadxml

If `wss` doesn't appear in `sofia status` after `reloadxml`, the XML file isn't being parsed. This could mean:

1. **FusionPBX is overwriting the file** - FusionPBX regenerates profiles from the database and may overwrite manual XML files
2. **XML syntax error** - A syntax error prevents the file from being parsed, but no error is shown
3. **Include pattern issue** - The file doesn't match the include pattern

**Fix: Check if FusionPBX is regenerating the file:**

```bash
# Monitor if the file gets overwritten during reloadxml
md5sum /etc/freeswitch/sip_profiles/wss.xml
BEFORE_MD5=$(md5sum /etc/freeswitch/sip_profiles/wss.xml | awk '{print $1}')

fs_cli -x "reloadxml"
sleep 2

AFTER_MD5=$(md5sum /etc/freeswitch/sip_profiles/wss.xml | awk '{print $1}')

if [ "$BEFORE_MD5" != "$AFTER_MD5" ]; then
    echo "⚠️ WARNING: File was modified during reloadxml!"
    echo "FusionPBX is overwriting your manual XML file"
    echo "You need to configure via FusionPBX GUI or database instead"
else
    echo "✅ File was not modified"
fi
```

**Fix: Check if there's an XML parsing error that's silent:**

```bash
# Enable maximum XML logging
fs_cli -x "console loglevel debug"
fs_cli -x "loglevel 7"

# Watch for XML parsing errors
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "wss|xml|parse|error|sip_profiles" &
TAIL_PID=$!

fs_cli -x "reloadxml"
sleep 3
kill $TAIL_PID

# Check specifically for wss-related errors
tail -200 /var/log/freeswitch/freeswitch.log | grep -A 10 -B 10 -iE "wss|sip_profiles.*wss" | tail -30
```

**Fix: Try using FusionPBX GUI to create the profile**

Since FusionPBX generates profiles dynamically, the most reliable way is through the GUI:

1. **Login to FusionPBX:** `https://136.115.41.45`
2. **Navigate to:** `Advanced → SIP Profiles`
3. **Click "Add" or "+"** to create a new profile
4. **Set Profile Name:** `wss`
5. **Configure all settings via GUI**
6. **Save**
7. **Go to:** `Status → SIP Status`
8. **Click "Reload XML"** at the top
9. **Find "wss" profile and click "Restart"**

**Fix: Check if profile needs to be in a specific database state**

FusionPBX might require specific database entries beyond just the profile and settings:

```bash
# Check what tables are involved
sudo -u postgres psql fusionpbx -c "\dt" | grep -i "sip\|profile"

# Check if there are any constraints or triggers
sudo -u postgres psql fusionpbx -c "SELECT tablename, indexname FROM pg_indexes WHERE tablename LIKE '%sip%profile%';"

# Check if internal/external profiles have something wss doesn't
sudo -u postgres psql fusionpbx -c "SELECT * FROM v_sip_profiles WHERE sip_profile_name IN ('internal', 'external', 'wss') ORDER BY sip_profile_name;"

# Compare settings count
sudo -u postgres psql fusionpbx -c "
SELECT 
    sp.sip_profile_name,
    COUNT(sps.sip_profile_setting_uuid) as setting_count
FROM v_sip_profiles sp
LEFT JOIN v_sip_profile_settings sps ON sp.sip_profile_uuid = sps.sip_profile_uuid
WHERE sp.sip_profile_name IN ('internal', 'external', 'wss')
GROUP BY sp.sip_profile_name
ORDER BY sp.sip_profile_name;"
```

---

# FusionPBX Database Setup for External IP

## Problem
FusionPBX ignores XML changes because it stores SIP profile settings in the database. Manual XML edits are overwritten when FusionPBX rewrites config files.

## Solution 1: Use FusionPBX GUI (Recommended)

1. **Login to FusionPBX:**
   ```
   https://136.113.215.142
   Username: admin (or your FusionPBX admin user)
   ```

2. **Navigate to SIP Profile:**
   ```
   Advanced → SIP Profiles → external
   ```

3. **Edit Settings:**
   Look for these settings and update them:
   - **Name**: `external`
   - **Hostname**: (leave empty or set to domain)
   - **Local SIP IP**: `10.128.0.8`
   - **Local RTP IP**: `10.128.0.142` (or leave auto)
   - **External SIP IP**: `136.113.215.142` ⭐ **KEY SETTING**
   - **External RTP IP**: `136.113.215.142` ⭐ **KEY SETTING**
   - **SIP Port**: `5060`
   - **Apply-inbound-acl**: `twilio`

4. **Save Changes:**
   - Click "Save" button at bottom of page

5. **Reload FreeSWITCH:**
   ```
   Status → SIP Status
   ```
   - Find the "external" profile in the list
   - Click "Reload XML"
   - Click "Restart" button

6. **Verify:**
   ```bash
   fs_cli -x "sofia xmlstatus profile external" | grep -E "sip-ip|ext-sip-ip"
   ```
   Should now show:
   ```
   <sip-ip>10.128.0.8</sip-ip>
   <ext-sip-ip>136.113.215.142</ext-sip-ip>  ✅
   ```

## Solution 2: Update Database Directly (Advanced)

If GUI doesn't work, update the database directly:

```bash
# SSH into FusionPBX
ssh root@136.113.215.142

# Login to MySQL/MariaDB
mysql -u root -p
# Enter your MySQL password

# Use FusionPBX database
USE fusionpbx;  # or fusionswitch, check your DB name

# Check current settings
SELECT * FROM v_sip_profile_settings 
WHERE sip_profile_name = 'external' 
AND sip_profile_setting_name IN ('ext-sip-ip', 'ext-rtp-ip', 'sip-ip', 'rtp-ip');

# Update ext-sip-ip setting
UPDATE v_sip_profile_settings 
SET sip_profile_setting_value = '136.113.215.142'
WHERE sip_profile_name = 'external' 
AND sip_profile_setting_name = 'ext-sip-ip';

# Update ext-rtp-ip setting
UPDATE v_sip_profile_settings 
SET sip_profile_setting_value = '136.113.215.142'
WHERE sip_profile_name = 'external' 
AND sip_profile_setting_name = 'ext-rtp-ip';

# If settings don't exist, INSERT them
INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT 
  UUID(),
  (SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'external'),
  'ext-sip-ip',
  '136.113.215.142',
  'true'
WHERE NOT EXISTS (
  SELECT 1 FROM v_sip_profile_settings 
  WHERE sip_profile_name = 'external' 
  AND sip_profile_setting_name = 'ext-sip-ip'
);

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT 
  UUID(),
  (SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'external'),
  'ext-rtp-ip',
  '136.113.215.142',
  'true'
WHERE NOT EXISTS (
  SELECT 1 FROM v_sip_profile_settings 
  WHERE sip_profile_name = 'external' 
  AND sip_profile_setting_name = 'ext-rtp-ip'
);

# Exit MySQL
exit;
```

Then reload FreeSWITCH:
```bash
fs_cli -x "reloadxml"
fs_cli -x "sofia profile external restart"
fs_cli -x "sofia xmlstatus profile external" | grep -E "sip-ip|ext-sip-ip"
```

## Solution 3: Check Database Schema

Find the correct database and table names:

```bash
mysql -u root -p

# List databases
SHOW DATABASES;

# Common FusionPBX database names:
# - fusionpbx
# - freeswitch
# - switch
# - pbx

# Check SIP profile tables
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'fusionpbx' 
AND table_name LIKE '%sip%profile%';

# Check if settings are in different tables
DESCRIBE v_sip_profile_settings;
SHOW COLUMNS FROM v_sip_profile_settings;
```

## Solution 4: Use FusionPBX CLI

Some FusionPBX installations have a CLI tool:

```bash
# Try these commands
fwconsole ma list | grep sip
fs_cli -x "api reloadxml"
fs_cli -x "sofia profile external rescan reloadxml"
```

## Verification After Update

```bash
# Method 1: Check via fs_cli
fs_cli -x "sofia xmlstatus profile external" | grep -E "sip-ip|ext-sip-ip"

# Method 2: Check via database
mysql -u root -p fusionpbx -e "SELECT sip_profile_setting_name, sip_profile_setting_value FROM v_sip_profile_settings WHERE sip_profile_name = 'external' AND sip_profile_setting_name LIKE '%ip%';"

# Method 3: Check SIP INVITE headers
# Make a test call and capture SIP traffic
tcpdump -i any -n -s 0 -A 'port 5060 and udp' | grep -E "Contact:|SDP:"
```

## Expected Result

After applying one of the methods above, `sofia xmlstatus` should show:
```
<sip-ip>10.128.0.8</sip-ip>              ✅ Binds to private IP
<ext-sip-ip>136.113.215.142</ext-sip-ip> ✅ Advertises public IP to Twilio
```

## Troubleshooting

If `ext-sip-ip` still shows wrong value:

1. **Check for multiple profile definitions:**
   ```bash
   find /etc/freeswitch/sip_profiles -name "*.xml" -exec grep -l "profile name=\"external\"" {} \;
   ```

2. **Check FreeSWITCH logs:**
   ```bash
   tail -100 /var/log/freeswitch/freeswitch.log | grep -i "external\|ext-sip-ip"
   ```

3. **Force XML rewrite:**
   ```bash
   fs_cli -x "api reloadxml"
   fs_cli -x "api fsctl send_sighup"
   ```

4. **Check if FusionPBX is rewriting XML:**
   ```bash
   # Set up inotify to watch the file
   apt-get install inotify-tools -y
   inotifywait -m /etc/freeswitch/sip_profiles/external.xml -e modify
   ```
   If file changes automatically, FusionPBX is rewriting it from the database.

# FusionPBX PostgreSQL Setup for External IP

## Your Setup
- **Database**: PostgreSQL 15
- **Database Name**: `fusionpbx`
- **External IP**: `136.113.215.142`
- **Private IP**: `10.128.0.8`

## Update External IP via PostgreSQL

```bash
# Connect to PostgreSQL as postgres user
sudo -u postgres psql fusionpbx

# Check current SIP profile settings
SELECT sip_profile_setting_name, sip_profile_setting_value 
FROM v_sip_profile_settings 
WHERE sip_profile_name = 'external' 
AND sip_profile_setting_name LIKE '%ip%';

# Update ext-sip-ip
UPDATE v_sip_profile_settings 
SET sip_profile_setting_value = '136.113.215.142'
WHERE sip_profile_name = 'external' 
AND sip_profile_setting_name = 'ext-sip-ip';

# Update ext-rtp-ip
UPDATE v_sip_profile_settings 
SET sip_profile_setting_value = '136.113.215.142'
WHERE sip_profile_name = 'external' 
AND sip_profile_setting_name = 'ext-rtp-ip';

# Verify changes
SELECT sip_profile_setting_name, sip_profile_setting_value 
FROM v_sip_profile_settings 
WHERE sip_profile_name = 'external' 
AND sip_profile_setting_name LIKE '%ip%';

# Exit PostgreSQL
\q
```

## If Settings Don't Exist (INSERT them)

```bash
sudo -u postgres psql fusionpbx

# Get the profile UUID first
SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'external';

# Insert ext-sip-ip (replace 'YOUR-PROFILE-UUID' with actual UUID)
INSERT INTO v_sip_profile_settings (
    sip_profile_setting_uuid, 
    sip_profile_uuid, 
    sip_profile_setting_name, 
    sip_profile_setting_value, 
    sip_profile_setting_enabled
) VALUES (
    gen_random_uuid(),
    (SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'external'),
    'ext-sip-ip',
    '136.113.215.142',
    true
);

# Insert ext-rtp-ip
INSERT INTO v_sip_profile_settings (
    sip_profile_setting_uuid, 
    sip_profile_uuid, 
    sip_profile_setting_name, 
    sip_profile_setting_value, 
    sip_profile_setting_enabled
) VALUES (
    gen_random_uuid(),
    (SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'external'),
    'ext-rtp-ip',
    '136.113.215.142',
    true
);

# Verify
SELECT sip_profile_setting_name, sip_profile_setting_value 
FROM v_sip_profile_settings 
WHERE sip_profile_name = 'external' 
AND sip_profile_setting_name LIKE '%ip%';

\q
```

## Reload FreeSWITCH After Database Update

```bash
# Reload XML configuration
fs_cli -x "reloadxml"

# Restart the external profile
fs_cli -x "sofia profile external restart"

# Verify the settings
fs_cli -x "sofia xmlstatus profile external" | grep -E "sip-ip|ext-sip-ip"
```

Expected output:
```
<sip-ip>10.128.0.8</sip-ip>
<ext-sip-ip>136.113.215.142</ext-sip-ip>  ✅
```

## Quick One-Liner Commands

If the settings already exist, use these one-liners:

```bash
# Update both IPs in one go
sudo -u postgres psql fusionpbx -c "UPDATE v_sip_profile_settings SET sip_profile_setting_value = '136.113.215.142' WHERE sip_profile_name = 'external' AND sip_profile_setting_name IN ('ext-sip-ip', 'ext-rtp-ip');"

# Reload FreeSWITCH
fs_cli -x "reloadxml" && fs_cli -x "sofia profile external restart"

# Verify
fs_cli -x "sofia xmlstatus profile external" | grep -E "sip-ip|ext-sip-ip"
```

## Alternative: All-in-One Check and Update

```bash
#!/bin/bash
# This script checks and updates external IP settings

# Connect to PostgreSQL and update
sudo -u postgres psql fusionpbx << 'EOF'
-- Update ext-sip-ip
UPDATE v_sip_profile_settings 
SET sip_profile_setting_value = '136.113.215.142'
WHERE sip_profile_name = 'external' 
AND sip_profile_setting_name = 'ext-sip-ip';

-- Update ext-rtp-ip
UPDATE v_sip_profile_settings 
SET sip_profile_setting_value = '136.113.215.142'
WHERE sip_profile_name = 'external' 
AND sip_profile_setting_name = 'ext-rtp-ip';

-- Verify
SELECT 'Updated Settings:' as status;
SELECT sip_profile_setting_name, sip_profile_setting_value 
FROM v_sip_profile_settings 
WHERE sip_profile_name = 'external' 
AND sip_profile_setting_name LIKE '%ip%';
EOF

# Reload FreeSWITCH
echo "Reloading FreeSWITCH..."
fs_cli -x "reloadxml"
fs_cli -x "sofia profile external restart"

# Verify
echo "Verifying settings..."
fs_cli -x "sofia xmlstatus profile external" | grep -E "sip-ip|ext-sip-ip"
```

## Troubleshooting

If settings still don't work after database update:

1. **Check if FusionPBX rewrites the XML from database:**
   ```bash
   tail -f /var/log/freeswitch/freeswitch.log | grep -i "external\|sip-ip"
   ```

2. **Force XML rebuild:**
   ```bash
   fs_cli -x "api reloadxml"
   fs_cli -x "sofia profile external killgw all"
   fs_cli -x "sofia profile external rescan reloadxml"
   fs_cli -x "sofia profile external restart"
   ```

3. **Check for multiple profile definitions:**
   ```bash
   find /etc/freeswitch -name "*.xml" -exec grep -l "profile name=\"external\"" {} \;
   ```

4. **Verify ACL is applied:**
   ```bash
   fs_cli -x "sofia status profile external" | grep -i "acl\|twilio"
   ```

## Expected Flow After Configuration

1. **Transfer Initiated:** Twilio dials `sip:2001@136.113.215.142;transport=udp`
2. **SIP INVITE:** Twilio sends INVITE to `136.113.215.142:5060`
3. **FusionPBX:** Accepts call (ACL allows Twilio IPs)
4. **FreeSWITCH:** Routes to extension 2001
5. **Transfer Success:** `status=completed` in logs

# Fix FusionPBX PostgreSQL Query

## First, find the correct table structure

```bash
# Connect to PostgreSQL
sudo -u postgres psql fusionpbx

# List all tables related to SIP profiles
\d v_sip_profile_settings

# Check what columns exist
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'v_sip_profile_settings';

# Check for other related tables
\dt *sip*profile*

# Exit PostgreSQL
\q
```

## Likely fixes:

### Option 1: Join with v_sip_profiles

```bash
sudo -u postgres psql fusionpbx
```

```sql
-- Check current settings
SELECT 
    sp.sip_profile_name,
    sps.sip_profile_setting_name,
    sps.sip_profile_setting_value
FROM v_sip_profile_settings sps
JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
WHERE sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name LIKE '%ip%';

-- Update ext-sip-ip
UPDATE v_sip_profile_settings sps
SET sip_profile_setting_value = '136.113.215.142'
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'ext-sip-ip';

-- Update ext-rtp-ip
UPDATE v_sip_profile_settings sps
SET sip_profile_setting_value = '136.113.215.142'
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'ext-rtp-ip';

-- Verify
SELECT 
    sp.sip_profile_name,
    sps.sip_profile_setting_name,
    sps.sip_profile_setting_value
FROM v_sip_profile_settings sps
JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
WHERE sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name LIKE '%ip%';

\q
```

### Option 2: Use sip_profile_uuid directly

```sql
-- Get the UUID first
SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'external';

-- Then use that UUID (replace with actual UUID)
UPDATE v_sip_profile_settings 
SET sip_profile_setting_value = '136.113.215.142'
WHERE sip_profile_uuid = 'YOUR-UUID-HERE'
AND sip_profile_setting_name IN ('ext-sip-ip', 'ext-rtp-ip');
```

### Option 3: Alternative table names

FusionPBX might use different table names:
```sql
-- Try these table names instead
\d sip_profile_settings
\d v_sip_profile
\d v_sip_profile_setting
\dt sip*
```

## One-liner to explore structure first

```bash
sudo -u postgres psql fusionpbx -c "\d v_sip_profile_settings"
```

This will show all columns in the table, so we can write the correct UPDATE query.

# FusionPBX Variable Configuration

The external profile is using variables instead of hardcoded IPs:
- `ext-sip-ip` = `$${external_sip_ip}`
- `ext-rtp-ip` = `$${external_rtp_ip}`

These variables need to be set in FusionPBX's global configuration.

## Option 1: Set Global Variables via Database

```bash
sudo -u postgres psql fusionpbx
```

Look for a `variables` or `settings` table:

```sql
-- List all table names
\dt

-- Check for variables table
\dt *variable*
\dt *setting*
\dt *config*

-- Try to find where these variables are stored
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE '%variable%' OR table_name LIKE '%setting%';
```

## Option 2: Use FusionPBX GUI

1. **Login to FusionPBX:**
   ```
   https://136.113.215.142
   ```

2. **Navigate to Global Settings:**
   ```
   Advanced → Default Settings
   ```
   OR
   ```
   Settings → Default Settings
   ```
   OR
   ```
   Advanced → Variables
   ```

3. **Find and set:**
   - `external_sip_ip` = `136.113.215.142`
   - `external_rtp_ip` = `136.113.215.142`

4. **Save and reload:**
   ```
   Status → SIP Status → Reload XML → Restart external profile
   ```

## Option 3: Override at Profile Level

Instead of using the global variables, directly set the values in the profile:

```sql
-- Update to use literal IP instead of variable
UPDATE v_sip_profile_settings sps
SET sip_profile_setting_value = '136.113.215.142'
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name IN ('ext-sip-ip', 'ext-rtp-ip');
```

## Option 4: Check /etc/freeswitch/vars.xml

```bash
# Check if these variables are defined in vars.xml
cat /etc/freeswitch/vars.xml | grep -i "external.*ip"

# If they exist, update them
sudo nano /etc/freeswitch/vars.xml
# Find the X-PRE-PROCESS lines for external_sip_ip and external_rtp_ip
# Update to:
# <X-PRE-PROCESS cmd="set" data="external_sip_ip=136.113.215.142"/>
# <X-PRE-PROCESS cmd="set" data="external_rtp_ip=136.113.215.142"/>
```

## Recommended Quick Fix

Use **Option 3** to override at the profile level:

```bash
# Override the variables with literal IP
sudo -u postgres psql fusionpbx -c "UPDATE v_sip_profile_settings sps SET sip_profile_setting_value = '136.113.215.142' FROM v_sip_profiles sp WHERE sps.sip_profile_uuid = sp.sip_profile_uuid AND sp.sip_profile_name = 'external' AND sps.sip_profile_setting_name IN ('ext-sip-ip', 'ext-rtp-ip');"

# Reload
fs_cli -x "reloadxml" && fs_cli -x "sofia profile external restart"

# Verify
fs_cli -x "sofia xmlstatus profile external" | grep -E "sip-ip|ext-sip-ip"
```

Expected output:
```
<sip-ip>10.128.0.8</sip-ip>
<ext-sip-ip>136.113.215.142</ext-sip-ip>  ✅
```

# FusionPBX ext-sip-ip Troubleshooting

## Problem
After updating `/etc/freeswitch/sip_profiles/external.xml` with `ext-sip-ip=136.113.215.142`, FreeSWITCH still shows:
```
<sip-ip>10.128.0.8</sip-ip>
<ext-sip-ip>10.128.0.8</sip-ip>  ❌ Should be 136.113.215.142
```

## Solution Steps

### Step 1: Verify XML File is Correct

Check the actual content of the XML file:
```bash
cat /etc/freeswitch/sip_profiles/external.xml | grep -A 2 ext-sip-ip
```

Expected output:
```xml
<param name="ext-sip-ip" value="136.113.215.142"/>
```

### Step 2: Check for NAT Settings

FreeSWITCH might need NAT configuration. Add these to your external profile:

```xml
<profile name="external">
  <settings>
    <!-- Existing settings -->
    <param name="sip-ip" value="10.128.0.8"/>
    <param name="rtp-ip" value="10.128.0.8"/>
    
    <!-- Advertise public IP to Twilio -->
    <param name="ext-sip-ip" value="136.113.215.142"/>
    <param name="ext-rtp-ip" value="136.113.215.142"/>
    
    <!-- NAT Settings (ADD THESE) -->
    <param name="sip-force-contact" value="$${ext_sip_ip}:$${sip_port}"/>
    <param name="rtp-force-contact" value="$${ext_rtp_ip}"/>
    <param name="aggressive-nat-detection" value="true"/>
    <param name="rtp-timeout-sec" value="300"/>
    <param name="rtp-hold-timeout-sec" value="1800"/>
    
    <!-- Existing ACL and other settings -->
  </settings>
</profile>
```

### Step 3: Check Global NAT Settings

Check `/etc/freeswitch/autoload_configs/switch.conf.xml` for NAT settings:

```bash
cat /etc/freeswitch/autoload_configs/switch.conf.xml | grep -i nat
```

If it exists, verify or add:
```xml
<param name="external-rtp-ip" value="136.113.215.142"/>
<param name="external-sip-ip" value="136.113.215.142"/>
```

### Step 4: Force Reload Configuration

Instead of just reloading XML, try a complete restart:

```bash
# Stop FreeSWITCH
systemctl stop freeswitch
# OR
/etc/init.d/freeswitch stop

# Start FreeSWITCH
systemctl start freeswitch
# OR
/etc/init.d/freeswitch start

# Check status
fs_cli -x "sofia xmlstatus profile external" | grep -E "sip-ip|ext-sip-ip"
```

### Step 5: Verify Profile is Actually Running

Check if the profile is loaded and active:
```bash
fs_cli -x "sofia status profile external"
```

Look for:
- Profile status: `RUNNING`
- Name: `external`
- IP: Should show `136.113.215.142` in Contact header

### Step 6: Check for Multiple Profile Definitions

FreeSWITCH might be reading another profile definition. Search for all external profile definitions:

```bash
find /etc/freeswitch -name "*.xml" -exec grep -l "profile name=\"external\"" {} \;
```

If multiple files exist, ensure they all have the correct `ext-sip-ip`.

### Step 7: Use fs_cli to Set Directly (Temporary Fix)

If XML isn't working, you can set it directly in FreeSWITCH (temporary, until restart):

```bash
fs_cli -x "sofia profile external killgw all"
fs_cli -x "sofia profile external rescan"
fs_cli -x "sofia profile external restart"
```

### Step 8: Check FreeSWITCH Logs

Check FreeSWITCH logs for errors:
```bash
tail -100 /var/log/freeswitch/freeswitch.log | grep -i "external\|ext-sip-ip\|nat"
```

Look for:
- NAT detection messages
- Profile loading errors
- IP binding errors

## Expected Result After Fix

After applying the fixes:
```bash
fs_cli -x "sofia xmlstatus profile external" | grep sip-ip
```

Should show:
```
<sip-ip>10.128.0.8</sip-ip>              ✅ Correct (binds to private IP)
<ext-sip-ip>136.113.215.142</ext-sip-ip> ✅ Correct (advertises public IP)
```

## Alternative: Use FusionPBX GUI

If manual XML editing isn't working, use the FusionPBX web interface:

1. **Login to FusionPBX:**
   ```
   https://136.113.215.142
   ```

2. **Navigate to SIP Profile:**
   ```
   Advanced → SIP Profiles → external
   ```

3. **Edit Settings:**
   - Find "External SIP IP" setting
   - Set to: `136.113.215.142`
   - Find "External RTP IP" setting
   - Set to: `136.113.215.142`

4. **Save and Reload:**
   - Click "Save"
   - Go to Status → SIP Status
   - Click "Reload XML"
   - Click "Restart" for the external profile

## Summary

The most likely causes:
1. **Missing NAT settings** - Add `sip-force-contact` and `rtp-force-contact` parameters
2. **Profile not reloaded correctly** - Try full FreeSWITCH restart
3. **Global NAT settings override** - Check `switch.conf.xml`
4. **Multiple profile definitions** - Ensure all XML files are updated

After applying these fixes, the `ext-sip-ip` should show `136.113.215.142` and Twilio transfers should work.

# FusionPBX Call Transfer Setup Guide

## Problem
Call transfer from Twilio to FusionPBX fails with `status=failed`.

**Current Configuration:**
- FusionPBX Domain: `136.113.215.142`
- Extension: `2001`
- SIP URI: `sip:2001@136.113.215.142;transport=udp`

## Root Cause
Twilio cannot directly dial a SIP URI without proper configuration on the FusionPBX server. FusionPBX must be configured to:
1. Accept SIP calls from Twilio IP ranges
2. Allow SIP traffic through the firewall
3. Have the extension accessible

## Solution: Configure FusionPBX to Accept Twilio SIP Calls

### Step 1: Whitelist Twilio IP Ranges in FusionPBX

Twilio uses specific IP ranges for outbound SIP calls. You need to whitelist these in FusionPBX:

**Twilio IP Ranges:**
```
54.172.60.0/23
54.244.51.0/24
177.71.206.192/26
54.252.254.64/26
54.169.127.128/26
```

#### Option A: Configure via FusionPBX Web Interface

1. **Log into FusionPBX Admin Panel:**
   ```
   https://136.113.215.142
   ```

2. **Navigate to Firewall Settings:**
   ```
   Advanced → Firewall → Access Lists
   ```

3. **Create New Access List:**
   - Name: `Twilio-SIP`
   - Description: `Twilio SIP Trunk IP Ranges`
   - Add the IP ranges above

4. **Apply to SIP Context:**
   - Navigate to: `Advanced → SIP Profiles`
   - Edit your SIP profile
   - In "ACL" or "Permit" settings, add: `Twilio-SIP`

#### Option B: Configure via Asterisk Config Files (SSH)

1. **SSH into FusionPBX Server:**
   ```bash
   ssh root@136.113.215.142
   ```

2. **Edit PJSIP Config:**
   ```bash
   vi /etc/asterisk/pjsip.conf
   ```

3. **Add Twilio Endpoint Configuration:**
   ```ini
   [twilio-endpoint]
   type=endpoint
   context=from-trunk
   disallow=all
   allow=ulaw
   allow=alaw
   direct_media=no
   rtp_symmetric=yes

   [twilio-aor]
   type=aor
   contact=sip:twilio@127.0.0.1

   [twilio-identify]
   type=identify
   endpoint=twilio-endpoint
   match=54.172.60.0/23
   match=54.244.51.0/24
   match=177.71.206.192/26
   match=54.252.254.64/26
   match=54.169.127.128/26
   ```

4. **Create Context for Incoming Twilio Calls:**
   ```bash
   vi /etc/asterisk/extensions.conf
   ```
   
   Add or edit the `[from-trunk]` context:
   ```ini
   [from-trunk]
   exten => _X.,1,NoOp(Incoming SIP call from Twilio to extension ${EXTEN})
   exten => _X.,n,Goto(from-internal,${EXTEN},1)
   exten => _X.,n,Hangup()
   ```

5. **Reload Asterisk Configuration:**
   ```bash
   asterisk -rx "core reload"
   asterisk -rx "pjsip reload"
   ```

### Step 2: Configure Firewall to Allow SIP Traffic

**Open UDP Port 5060 for SIP:**
```bash
# On FusionPBX server
ufw allow 5060/udp
# OR
iptables -A INPUT -p udp --dport 5060 -j ACCEPT
```

**For WebRTC/SIP TLS (optional, port 5061):**
```bash
ufw allow 5061/tcp
```

### Step 3: Verify Extension 2001 Exists and Is Reachable

1. **Check Extension in FusionPBX:**
   ```
   Admin → Extensions → Check extension 2001 exists
   ```

2. **Verify Extension is Active:**
   - Extension must be registered (if using SIP phones)
   - Or extension must be assigned to a queue
   - Or extension must forward to another number

3. **Test Extension Manually:**
   - Use a SIP client (like Zoiper or Linphone)
   - Connect to: `sip:2001@136.113.215.142`
   - Verify you can reach the extension

### Step 4: Test SIP Connectivity from External IP

**From your local machine, test if FusionPBX accepts SIP:**
```bash
# Test SIP port
nc -zuv 136.113.215.142 5060

# Expected output:
# Connection to 136.113.215.142 5060 port [udp/sip] succeeded!
```

### Step 5: Configure SIP Authentication (Optional but Recommended)

If FusionPBX requires SIP authentication:

1. **Create SIP User for Twilio:**
   ```
   FusionPBX → Admin → Extensions → Add Extension
   ```
   - Extension: `9999` (or any unused number)
   - Secret: Generate strong password
   - Context: `from-trunk`

2. **Set Environment Variables:**
   ```bash
   FREEPBX_SIP_USERNAME=9999
   FREEPBX_SIP_PASSWORD=your_strong_password
   ```

3. **Update Transfer Code:**
   The code will automatically use SIP authentication if these variables are set.

### Step 6: Verify Transfer Works

1. **Make a test call via Twilio:**
   - Call your Twilio number
   - Say "transfer me to agent"
   - Check logs for detailed transfer status

2. **Check FusionPBX Logs:**
   ```bash
   ssh root@136.113.215.142
   tail -f /var/log/asterisk/full | grep "2001"
   ```

3. **Check Application Logs:**
   Look for:
   - `Transferring to SIP URI: sip:2001@136.113.215.142;transport=udp`
   - `Transfer callback for call ... status=completed` (success!)
   - Or error details if it fails

## Troubleshooting

### Transfer Still Fails?

1. **Check Application Logs for Error Details:**
   - Look for `❌ Transfer failed` messages
   - Check `Error Message` field
   - Review `Possible causes` list in logs

2. **Verify Twilio IP Ranges are Whitelisted:**
   ```bash
   # On FusionPBX server
   asterisk -rx "pjsip show endpoints" | grep twilio
   asterisk -rx "pjsip show identifies" | grep -A 5 twilio
   ```

3. **Check Firewall:**
   ```bash
   # On FusionPBX server
   ufw status | grep 5060
   iptables -L -n | grep 5060
   ```

4. **Test SIP Manually:**
   ```bash
   # From external machine
   sip-scan -s 136.113.215.142
   ```

5. **Check FusionPBX Asterisk Logs:**
   ```bash
   ssh root@136.113.215.142
   tail -100 /var/log/asterisk/full | grep -i "sip\|invite\|twilio"
   ```

## Expected Behavior After Configuration

When properly configured:

1. **Transfer Initiated:**
   ```
   Transferring to SIP URI: sip:2001@136.113.215.142;transport=udp
   ```

2. **Twilio Connects to FusionPBX:**
   - Twilio sends SIP INVITE to `136.113.215.142:5060`
   - FusionPBX accepts the call
   - Routes to extension 2001

3. **Transfer Success:**
   ```
   Transfer callback for call CA...: status=completed, extension=2001
   ✅ Transfer successful for call CA... to extension 2001
   ```

## Alternative: Use Twilio Elastic SIP Trunking

If direct SIP URI dialing doesn't work, you can set up Twilio Elastic SIP Trunking:

1. **Create SIP Trunk in Twilio Console:**
   - Navigate to: `Voice → Elastic SIP Trunking → Create Trunk`
   - Trunk Name: `FusionPBX-Trunk`

2. **Add Origination URI:**
   - URI: `sip:136.113.215.142`
   - Priority: 1
   - Weight: 1

3. **Add Termination URI:**
   - SIP URI: `136.113.215.142`
   - IP Access Control: Add FusionPBX IP

4. **Use Trunk in Transfer:**
   Update code to use trunk instead of direct SIP URI (requires code changes).

## Summary

**Required Configuration:**
1. ✅ Whitelist Twilio IP ranges in FusionPBX
2. ✅ Open UDP port 5060 in firewall
3. ✅ Verify extension 2001 exists and is reachable
4. ✅ (Optional) Configure SIP authentication if required

**Current Configuration:**
- FusionPBX Domain: `136.113.215.142`
- Extension: `2001`
- SIP URI Format: `sip:2001@136.113.215.142;transport=udp`


# FUSIONPBX_ADD_MISSING_SETTINGS

# Add Missing Settings to External SIP Profile

## 🔴 Missing Settings

The following settings don't exist in your FusionPBX external profile yet:
- `bypass-media` = `false`
- `media-bypass` = `false`
- `sip-force-contact` = `136.115.41.45:5060`
- `rtp-force-contact` = `136.115.41.45`
- `accept-blind-reg` = `false`

## ✅ Method 1: Add via FusionPBX GUI (Recommended)

1. **Login to FusionPBX:**
   ```
   https://136.115.41.45
   ```

2. **Navigate to SIP Profile:**
   ```
   Advanced → SIP Profiles → external
   ```

3. **Click on "Settings" tab** (or find the Settings section)

4. **For each missing setting, click "Add" or "+" button** and add:

### Setting 1: bypass-media
- **Setting Name:** `bypass-media`
- **Value:** `false`
- **Enabled:** ✅ Checked
- **Description:** `Disable media bypass for proper RTP handling`

### Setting 2: media-bypass
- **Setting Name:** `media-bypass`
- **Value:** `false`
- **Enabled:** ✅ Checked
- **Description:** `Disable media bypass for proper RTP handling`

### Setting 3: sip-force-contact
- **Setting Name:** `sip-force-contact`
- **Value:** `136.115.41.45:5060`
- **Enabled:** ✅ Checked
- **Description:** `Force SIP Contact header to use public IP`

### Setting 4: rtp-force-contact
- **Setting Name:** `rtp-force-contact`
- **Value:** `136.115.41.45`
- **Enabled:** ✅ Checked
- **Description:** `Force RTP Contact to use public IP`

### Setting 5: accept-blind-reg
- **Setting Name:** `accept-blind-reg`
- **Value:** `false`
- **Enabled:** ✅ Checked
- **Description:** `Don't accept unauthenticated registrations`

5. **Save all changes:**
   - Click "Save" button at the bottom

6. **Reload FreeSWITCH:**
   - Go to: `Status → SIP Status`
   - Find "external" profile
   - Click "Reload XML"
   - Click "Restart"

## ✅ Method 2: Add via Database (If GUI Doesn't Work)

If the GUI doesn't allow adding new settings, use the database:

```bash
# SSH into FusionPBX server
ssh root@136.115.41.45

# Connect to PostgreSQL
sudo -u postgres psql fusionpbx
```

### Add bypass-media

```sql
INSERT INTO v_sip_profile_settings (
    sip_profile_setting_uuid,
    sip_profile_uuid,
    sip_profile_setting_name,
    sip_profile_setting_value,
    sip_profile_setting_enabled
) 
SELECT 
    gen_random_uuid(),
    (SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'external'),
    'bypass-media',
    'false',
    true
WHERE NOT EXISTS (
    SELECT 1 FROM v_sip_profile_settings sps
    JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
    WHERE sp.sip_profile_name = 'external'
    AND sps.sip_profile_setting_name = 'bypass-media'
);
```

### Add media-bypass

```sql
INSERT INTO v_sip_profile_settings (
    sip_profile_setting_uuid,
    sip_profile_uuid,
    sip_profile_setting_name,
    sip_profile_setting_value,
    sip_profile_setting_enabled
) 
SELECT 
    gen_random_uuid(),
    (SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'external'),
    'media-bypass',
    'false',
    true
WHERE NOT EXISTS (
    SELECT 1 FROM v_sip_profile_settings sps
    JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
    WHERE sp.sip_profile_name = 'external'
    AND sps.sip_profile_setting_name = 'media-bypass'
);
```

### Add sip-force-contact

```sql
INSERT INTO v_sip_profile_settings (
    sip_profile_setting_uuid,
    sip_profile_uuid,
    sip_profile_setting_name,
    sip_profile_setting_value,
    sip_profile_setting_enabled
) 
SELECT 
    gen_random_uuid(),
    (SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'external'),
    'sip-force-contact',
    '136.115.41.45:5060',
    true
WHERE NOT EXISTS (
    SELECT 1 FROM v_sip_profile_settings sps
    JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
    WHERE sp.sip_profile_name = 'external'
    AND sps.sip_profile_setting_name = 'sip-force-contact'
);
```

### Add rtp-force-contact

```sql
INSERT INTO v_sip_profile_settings (
    sip_profile_setting_uuid,
    sip_profile_uuid,
    sip_profile_setting_name,
    sip_profile_setting_value,
    sip_profile_setting_enabled
) 
SELECT 
    gen_random_uuid(),
    (SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'external'),
    'rtp-force-contact',
    '136.115.41.45',
    true
WHERE NOT EXISTS (
    SELECT 1 FROM v_sip_profile_settings sps
    JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
    WHERE sp.sip_profile_name = 'external'
    AND sps.sip_profile_setting_name = 'rtp-force-contact'
);
```

### Add accept-blind-reg

```sql
INSERT INTO v_sip_profile_settings (
    sip_profile_setting_uuid,
    sip_profile_uuid,
    sip_profile_setting_name,
    sip_profile_setting_value,
    sip_profile_setting_enabled
) 
SELECT 
    gen_random_uuid(),
    (SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'external'),
    'accept-blind-reg',
    'false',
    true
WHERE NOT EXISTS (
    SELECT 1 FROM v_sip_profile_settings sps
    JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
    WHERE sp.sip_profile_name = 'external'
    AND sps.sip_profile_setting_name = 'accept-blind-reg'
);
```

### All-in-One Script

```sql
-- Add all missing settings at once
DO $$
DECLARE
    v_profile_uuid UUID;
BEGIN
    -- Get external profile UUID
    SELECT sip_profile_uuid INTO v_profile_uuid 
    FROM v_sip_profiles 
    WHERE sip_profile_name = 'external';

    -- Add bypass-media
    INSERT INTO v_sip_profile_settings (
        sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name,
        sip_profile_setting_value, sip_profile_setting_enabled
    )
    SELECT gen_random_uuid(), v_profile_uuid, 'bypass-media', 'false', true
    WHERE NOT EXISTS (
        SELECT 1 FROM v_sip_profile_settings 
        WHERE sip_profile_uuid = v_profile_uuid 
        AND sip_profile_setting_name = 'bypass-media'
    );

    -- Add media-bypass
    INSERT INTO v_sip_profile_settings (
        sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name,
        sip_profile_setting_value, sip_profile_setting_enabled
    )
    SELECT gen_random_uuid(), v_profile_uuid, 'media-bypass', 'false', true
    WHERE NOT EXISTS (
        SELECT 1 FROM v_sip_profile_settings 
        WHERE sip_profile_uuid = v_profile_uuid 
        AND sip_profile_setting_name = 'media-bypass'
    );

    -- Add sip-force-contact
    INSERT INTO v_sip_profile_settings (
        sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name,
        sip_profile_setting_value, sip_profile_setting_enabled
    )
    SELECT gen_random_uuid(), v_profile_uuid, 'sip-force-contact', '136.115.41.45:5060', true
    WHERE NOT EXISTS (
        SELECT 1 FROM v_sip_profile_settings 
        WHERE sip_profile_uuid = v_profile_uuid 
        AND sip_profile_setting_name = 'sip-force-contact'
    );

    -- Add rtp-force-contact
    INSERT INTO v_sip_profile_settings (
        sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name,
        sip_profile_setting_value, sip_profile_setting_enabled
    )
    SELECT gen_random_uuid(), v_profile_uuid, 'rtp-force-contact', '136.115.41.45', true
    WHERE NOT EXISTS (
        SELECT 1 FROM v_sip_profile_settings 
        WHERE sip_profile_uuid = v_profile_uuid 
        AND sip_profile_setting_name = 'rtp-force-contact'
    );

    -- Add accept-blind-reg
    INSERT INTO v_sip_profile_settings (
        sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name,
        sip_profile_setting_value, sip_profile_setting_enabled
    )
    SELECT gen_random_uuid(), v_profile_uuid, 'accept-blind-reg', 'false', true
    WHERE NOT EXISTS (
        SELECT 1 FROM v_sip_profile_settings 
        WHERE sip_profile_uuid = v_profile_uuid 
        AND sip_profile_setting_name = 'accept-blind-reg'
    );

    RAISE NOTICE 'All settings added successfully';
END $$;
```

After running the SQL commands:

```sql
\q
```

```bash
# Reload FreeSWITCH
fs_cli -x "reloadxml"
fs_cli -x "sofia profile external restart"
```

## 🔍 Verify Settings Were Added

```bash
# Check if all settings exist now
fs_cli -x "sofia xmlstatus profile external" | grep -E "bypass-media|media-bypass|sip-force-contact|rtp-force-contact|accept-blind-reg"
```

**Or check via database:**
```sql
SELECT 
    sip_profile_setting_name,
    sip_profile_setting_value,
    sip_profile_setting_enabled
FROM v_sip_profile_settings sps
JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
WHERE sp.sip_profile_name = 'external'
AND sip_profile_setting_name IN ('bypass-media', 'media-bypass', 'sip-force-contact', 'rtp-force-contact', 'accept-blind-reg')
ORDER BY sip_profile_setting_name;
```

## 📝 What Each Setting Does

### bypass-media = false
- **Purpose:** Disables media bypass, forcing all media to flow through FreeSWITCH
- **Why:** Ensures proper RTP handling and prevents media negotiation issues with Twilio

### media-bypass = false
- **Purpose:** Same as bypass-media (alternative name)
- **Why:** Ensures RTP streams go through FreeSWITCH for proper NAT traversal

### sip-force-contact = 136.115.41.45:5060
- **Purpose:** Forces SIP Contact header to use public IP instead of private IP
- **Why:** Twilio needs to see the public IP in Contact headers to route calls correctly

### rtp-force-contact = 136.115.41.45
- **Purpose:** Forces RTP media to use public IP in SDP (Session Description Protocol)
- **Why:** Ensures Twilio sends RTP packets to your public IP, not private IP

### accept-blind-reg = false
- **Purpose:** Rejects unauthenticated SIP REGISTER requests
- **Why:** Security - prevents unauthorized SIP phones from registering

## 🎯 Summary

Add these 5 settings to your external SIP profile:
1. `bypass-media` = `false`
2. `media-bypass` = `false`
3. `sip-force-contact` = `136.115.41.45:5060`
4. `rtp-force-contact` = `136.115.41.45`
5. `accept-blind-reg` = `false`

Use FusionPBX GUI (Method 1) if possible, or database (Method 2) if GUI doesn't work.


# FUSIONPBX_AGENT_PHONE_REJECTING

# Fix Agent Phone Rejecting Calls (SIP 603 Decline)

## 🔍 About external.xml

**Which component uses `external.xml`?**

The `external.xml` file is used by **FreeSWITCH's Sofia SIP stack** (the `mod_sofia` module). However, since you're using **FusionPBX**, FusionPBX actually:

1. **Stores SIP profile settings in its PostgreSQL database** (table: `v_sip_profile_settings`)
2. **Generates the XML files** (like `external.xml`) from the database when FreeSWITCH reloads
3. **Overwrites manual XML edits** when you click "Reload XML" in FusionPBX GUI

**Therefore:**
- ✅ **Manual edits to `external.xml` may be overwritten** by FusionPBX
- ✅ **Use FusionPBX GUI** to change SIP profile settings (recommended)
- ✅ **Or update the database directly** if GUI doesn't work

**Location:**
- `/etc/freeswitch/sip_profiles/external.xml` - Generated by FusionPBX
- FusionPBX stores settings in: `v_sip_profile_settings` table

**To see current settings:**
```bash
fs_cli -x "sofia xmlstatus profile external"
```

This shows what FreeSWITCH is actually using, regardless of what's in the XML file.

---

## 🔴 Problem: Agent's Phone Explicitly Rejects the Call

**From your logs:**
- ✅ Codec negotiation works (PCMU matched)
- ✅ Call reaches extension 2001
- ✅ Extension rings (Ring-Ready, proceeding[180])
- ❌ **Agent's phone sends SIP 603 Decline** → `CALL_REJECTED`
- ❌ Call drops ~2.6 seconds after ringing

**Key Log Evidence:**
```
2025-11-03 22:34:13.551108 - Ring-Ready sofia/internal/2001@198.27.217.12:55965!
2025-11-03 22:34:13.551108 - Callstate Change DOWN -> RINGING
2025-11-03 22:34:16.191107 - Channel entering state [terminated][603]  ← SIP 603 = Decline
2025-11-03 22:34:16.191107 - Hangup sofia/internal/2001@198.27.217.12:55965 [CS_CONSUME_MEDIA] [CALL_REJECTED]

# IMPORTANT: Dialplan is setting caller ID to extension itself:
set(caller_id_name=2001)
set(caller_id_number=2001)
```

**Agent's Phone IP:** `198.27.217.12:55965`

## 🎯 Most Likely Root Cause: Caller ID Issue

**Your logs show:**
```
set(caller_id_name=2001)
set(caller_id_number=2001)
```

**This means the call is coming FROM extension 2001 TO extension 2001**, which might cause the agent's phone to reject it as a loop or unknown caller.

**Fix:** The FusionPBX dialplan should preserve the original caller ID from Twilio instead of setting it to the extension number.


# FUSIONPBX_ANALYZE_403_LOGS

# Analyze 403 Forbidden Logs - Extension-to-Extension Calling

## 🔍 What the Logs Show

Your logs show:
1. ✅ Extension 2001 is making the call
2. ✅ Dialplan is processing the call to extension 2002
3. ✅ Bridge command is executed: `bridge(user/2002@136.115.41.45)`
4. ❌ **No logs showing what happens when trying to reach extension 2002**

The logs stop at the bridge command, which means we need to see what happens when FreeSWITCH tries to actually contact extension 2002.

## 🔎 Get More Specific Logs

### Check 1: Look for SIP INVITE to Extension 2002

```bash
# Get logs showing SIP INVITE messages to extension 2002
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "2002|sofia.*2002|invite.*2002" | tail -30
```

### Check 2: Look for Channel Creation for Extension 2002

```bash
# Look for new channel creation for extension 2002
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "New Channel.*2002|sofia.*2002" | tail -30
```

### Check 3: Check if Extension 2002 is Registered

```bash
# Check if extension 2002 is registered
fs_cli -x "sofia status profile internal reg" | grep "2002"

# Should show registration details if it's registered
```

### Check 4: Get Full Call Flow with Timestamps

```bash
# Get logs around the call time (adjust timestamp as needed)
grep -iE "536ad1aa-f360-42b1-b3bd-5e843842d965|2002" /var/log/freeswitch/freeswitch.log | tail -50
```

### Check 5: Look for 403 Response Codes

```bash
# Search for 403 SIP response codes
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "403|SIP/2.0 403|Forbidden"
```

### Check 6: Check ACL/Authentication Messages

```bash
# Look for ACL or auth errors
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "denied|acl|auth.*2002|permission.*2002"
```

## 🎯 Key Questions to Answer

Run these commands to get the missing information:

### 1. Is Extension 2002 Registered?

```bash
fs_cli -x "sofia status profile internal reg" | grep -A 5 "2002"
```

**Expected:** Should show extension 2002 registered
**If not:** Extension 2002 needs to register

### 2. Does Extension 2002 Exist?

```bash
sudo -u postgres psql fusionpbx -c "SELECT extension, enabled, user_context FROM v_extensions WHERE extension = '2002';"
```

### 3. What Happens When Bridge Tries to Contact Extension 2002?

```bash
# Get logs after the bridge command
grep -A 20 "bridge(user/2002@136.115.41.45)" /var/log/freeswitch/freeswitch.log | tail -30
```

### 4. Check for SIP Response Codes

```bash
# Look for SIP response codes (403, 404, 486, etc.)
tail -500 /var/log/freeswitch/freeswitch.log | grep -E "SIP/2.0 [4-6][0-9][0-9]|^[0-9]{3} " | tail -20
```

## 🔍 What to Look For

Based on your logs, the bridge command is executed but we need to see:

1. **SIP INVITE to extension 2002** - Is FreeSWITCH sending the INVITE?
2. **SIP Response from extension 2002** - What response comes back?
3. **Channel creation** - Does a channel get created for extension 2002?
4. **ACL check** - Is an ACL blocking the call?
5. **Registration status** - Is extension 2002 actually registered?

## 🎯 Recommended Next Steps

### Step 1: Enable Maximum Logging and Try Again

```bash
# Enable maximum logging
fs_cli -x "sofia loglevel all 9"
fs_cli -x "console loglevel debug"

# Clear previous logs (optional)
# tail -0 /var/log/freeswitch/freeswitch.log > /dev/null

# Watch logs in real-time with more context
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "2002|403|forbidden|deny|acl|invite|bridge.*2002"
```

Then make the call again from 2001 to 2002.

### Step 2: Check Extension 2002 Status

```bash
# Check if extension 2002 exists and is enabled
sudo -u postgres psql fusionpbx -c "SELECT extension, enabled, user_context, do_not_disturb FROM v_extensions WHERE extension = '2002';"

# Check if extension 2002 is registered
fs_cli -x "sofia status profile internal reg" | grep -A 10 "2002"
```

### Step 3: Try Originating from CLI

Test if FreeSWITCH can call extension 2002 directly:

```bash
# Test calling extension 2002 from FreeSWITCH CLI
fs_cli -x "originate user/2002@136.115.41.45 &echo()"
```

**If this works:** The issue is with how the SIP client (2001) is making the call
**If this fails:** The issue is with extension 2002 configuration or registration

## 📋 Complete Diagnostic Script

Run this to get all relevant information:

```bash
#!/bin/bash
echo "=== Extension 2002 Diagnostic ==="
echo ""

echo "1. Extension 2002 Database Check:"
sudo -u postgres psql fusionpbx -c "SELECT extension, enabled, user_context, do_not_disturb FROM v_extensions WHERE extension = '2002';"
echo ""

echo "2. Extension 2002 Registration Status:"
fs_cli -x "sofia status profile internal reg" | grep -A 10 "2002"
echo ""

echo "3. Recent Logs with Extension 2002:"
tail -100 /var/log/freeswitch/freeswitch.log | grep -i "2002" | tail -20
echo ""

echo "4. Recent 403/Forbidden Errors:"
tail -200 /var/log/freeswitch/freeswitch.log | grep -iE "403|forbidden" | tail -10
echo ""

echo "5. Recent Bridge Attempts to 2002:"
grep -i "bridge.*2002" /var/log/freeswitch/freeswitch.log | tail -5
echo ""

echo "6. Test Originate from CLI:"
echo "   (This will attempt to call extension 2002)"
fs_cli -x "originate user/2002@136.115.41.45 &echo()"
```

## 🔍 Most Likely Issues Based on Missing Logs

Since we don't see any SIP INVITE messages to extension 2002 in your logs, the issue is likely:

1. **Extension 2002 not registered** - FreeSWITCH can't reach it
2. **Extension 2002 doesn't exist** - Not configured in FusionPBX
3. **Extension 2002 disabled** - Disabled in FusionPBX
4. **SIP client issue** - The SIP client isn't properly sending the call

## 🎯 Immediate Actions

**Run these commands and share the output:**

```bash
# 1. Check if extension 2002 is registered
fs_cli -x "sofia status profile internal reg" | grep "2002"

# 2. Check if extension 2002 exists
sudo -u postgres psql fusionpbx -c "SELECT extension, enabled FROM v_extensions WHERE extension = '2002';"

# 3. Get logs showing what happens after bridge command
grep -A 30 "bridge(user/2002@136.115.41.45)" /var/log/freeswitch/freeswitch.log | tail -40
```

These will help identify why the bridge to extension 2002 is failing!


# FUSIONPBX_APPLY_REGISTER_ACL

# apply-register-acl Setting for External SIP Profile

## ✅ Recommended Value

**Set `apply-register-acl` to:**
```
domains
```

## 🔍 What Each ACL Setting Does

### `apply-inbound-acl`
- **Controls:** Who can send **SIP INVITE** requests (make calls)
- **Your setting:** `Twilio-SIP` ✅
- **Purpose:** Allows Twilio IP ranges to send calls to your FusionPBX

### `apply-register-acl`
- **Controls:** Who can send **SIP REGISTER** requests (register SIP phones)
- **Recommended:** `domains`
- **Purpose:** Allows SIP phones to register from configured domains

## 📝 Why `domains`?

The `domains` ACL:
1. **References domains configured in FusionPBX** - FusionPBX automatically creates this ACL based on your configured domains
2. **Allows legitimate registrations** - SIP phones from your configured domains can register
3. **Provides security** - Blocks registrations from unknown/unconfigured domains
4. **Standard for external profile** - This is the typical setting for the external SIP profile

## ⚙️ Configuration

### Via FusionPBX GUI

1. **Login to FusionPBX:**
   ```
   https://136.115.41.45
   ```

2. **Navigate to SIP Profile:**
   ```
   Advanced → SIP Profiles → external
   ```

3. **Find `apply-register-acl` setting:**
   - In the Settings table, find the row: `apply-register-acl`
   - Set **Value** to: `domains`
   - Make sure **Enabled** is checked ✅
   - **Description** can be: "Allow registrations from configured domains"

4. **Save:**
   - Click "Save" at the bottom
   - Go to: `Status → SIP Status`
   - Find "external" profile
   - Click "Reload XML"
   - Click "Restart"

### Via Database

```bash
# SSH into FusionPBX server
ssh root@136.115.41.45

# Connect to PostgreSQL
sudo -u postgres psql fusionpbx

# Update apply-register-acl setting
UPDATE v_sip_profile_settings sps
SET sip_profile_setting_value = 'domains',
    sip_profile_setting_enabled = true
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-register-acl';

# If setting doesn't exist, INSERT it
INSERT INTO v_sip_profile_settings (
    sip_profile_setting_uuid,
    sip_profile_uuid,
    sip_profile_setting_name,
    sip_profile_setting_value,
    sip_profile_setting_enabled
) 
SELECT 
    gen_random_uuid(),
    (SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'external'),
    'apply-register-acl',
    'domains',
    true
WHERE NOT EXISTS (
    SELECT 1 FROM v_sip_profile_settings sps
    JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
    WHERE sp.sip_profile_name = 'external'
    AND sps.sip_profile_setting_name = 'apply-register-acl'
);

\q

# Reload FreeSWITCH
fs_cli -x "reloadxml"
fs_cli -x "sofia profile external restart"
```

## 🔍 Verify Setting

```bash
# Check if apply-register-acl is set correctly
fs_cli -x "sofia xmlstatus profile external" | grep -i "apply-register-acl"
```

**Should show:**
```
<apply-register-acl>domains</apply-register-acl>
```

## 📊 Complete ACL Configuration Summary

For your external SIP profile, you should have:

| Setting | Value | Purpose |
|---------|-------|---------|
| `apply-inbound-acl` | `Twilio-SIP` | Allow Twilio IPs to send calls |
| `apply-register-acl` | `domains` | Allow registrations from configured domains |
| `accept-blind-reg` | `false` | Don't accept unauthenticated registrations |

## 🔐 Security Notes

### Why Not Allow All Registrations?

**Don't set `apply-register-acl` to:**
- ❌ Empty/null - Would allow anyone to register (security risk)
- ❌ `any` or `all` - Would allow anyone to register (security risk)
- ❌ `Twilio-SIP` - Twilio doesn't register, so this wouldn't help

**Use `domains` because:**
- ✅ Allows legitimate SIP phones from your configured domains
- ✅ Blocks unknown/unconfigured domains
- ✅ Standard security practice for external SIP profiles

### About `domains` ACL

The `domains` ACL is automatically maintained by FusionPBX based on:
- Domains configured in `Advanced → Domains`
- Each domain you add creates entries in the `domains` ACL
- When a SIP REGISTER request comes in, FusionPBX checks if the domain matches a configured domain

## 🎯 Summary

- **Setting:** `apply-register-acl`
- **Value:** `domains`
- **Location:** FusionPBX GUI → `Advanced → SIP Profiles → external → Settings`
- **Why:** Allows registrations from configured FusionPBX domains while blocking unknown domains


# FUSIONPBX_CALL_DROPS_AFTER_ANSWER

# Fix Call Drops After Agent Answers (CALL_REJECTED)

## 🔴 Problem: Call Transfers Successfully, But Drops When Agent Answers

**Symptoms:**
- ✅ Twilio call connects to voice agent
- ✅ Call transfers to extension 2001
- ✅ Extension 2001 rings
- ❌ Call drops immediately when agent answers
- ❌ Logs show: `CALL_REJECTED` on extension 2001 leg

**Example Log:**
```
[NOTICE] sofia.c:8736 Hangup sofia/internal/2001@198.27.217.12:55965 [CS_CONSUME_MEDIA] [CALL_REJECTED]
[NOTICE] switch_cpp.cpp:752 Hangup sofia/internal/+19259897818@sip.twilio.com [CS_EXECUTE] [NORMAL_CLEARING]
```

## 🔍 Root Causes

The `CALL_REJECTED` error with `CS_CONSUME_MEDIA` typically indicates:

1. **Media (RTP) Negotiation Failure** - Most common
   - Codec mismatch between Twilio and agent's phone
   - RTP ports blocked by firewall
   - NAT traversal issues
   - Incorrect RTP IP addresses

2. **Agent's Phone Rejecting Call**
   - Phone client configuration issue
   - Network connectivity problem from agent's device
   - Codec not supported by agent's phone

3. **FreeSWITCH Media Handling**
   - Media bypass/disabling issues
   - Incorrect media mode settings

## ✅ Diagnostic Steps

### Step 1: Check Media Negotiation in Logs

```bash
# Watch logs during transfer and answer
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "rtp|media|codec|2001|reject"

# Look for:
# - "RTP Statistics" or "Media Statistics"
# - Codec negotiation messages
# - RTP port assignments
# - Media stream creation/teardown
```

**What to look for:**
- RTP ports being assigned
- Codec negotiation (should see PCMU or PCMA)
- Any "reject" or "decline" messages
- Media stream establishment messages

### Step 2: Enable Detailed Media Debugging

```bash
# Enable RTP debugging
fs_cli -x "console loglevel debug"

# Enable SOFIA (SIP) debugging
fs_cli -x "sofia loglevel all 9"

# Watch logs
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "rtp|media|codec|2001"
```

### Step 3: Check Codec Compatibility

```bash
# Check what codecs Twilio leg supports
fs_cli -x "sofia status profile external" | grep -i "codec"

# Check what codecs extension 2001 supports
fs_cli -x "user_data 2001@136.115.41.45 var" | grep -i "codec"

# Check what codecs are negotiated for the call
# (Run this while call is active, before it drops)
fs_cli -x "show channels" | grep -A 10 "2001"
```

**Expected:** Both should support PCMU (G.711 μ-law) or PCMA (G.711 A-law)

### Step 4: Check RTP IP Addresses

```bash
# Check external SIP profile RTP settings
fs_cli -x "sofia xmlstatus profile external" | grep -i "rtp"

# Verify external RTP IP is correct
fs_cli -x "sofia xmlstatus profile external" | grep -E "ext-rtp-ip|rtp-ip"
```

**Should show:**
- `ext-rtp-ip`: `136.115.41.45` (public IP)
- `rtp-ip`: `10.128.0.8` (internal IP)

### Step 5: Test Internal Call (Extension to Extension)

```bash
# Test if extension 2001 can make/receive internal calls
fs_cli -x "originate user/2002@136.115.41.45 &echo()"

# Then have extension 2002 call 2001
fs_cli -x "originate user/2001@136.115.41.45 &echo()"
```

**If internal calls work but Twilio transfers don't:** The issue is with Twilio ↔ FusionPBX media path, not the extension itself.

### Step 6: Check Firewall Rules for RTP

```bash
# Check if RTP ports (10000-20000) are open
netstat -tuln | grep -E ":(10[0-9]{3}|1[1-9][0-9]{3}|20000)"

# Or use iptables
iptables -L -n | grep -E "5060|10000:20000"
```

**RTP uses UDP ports 10000-20000.** These must be open for media to flow.

### Step 7: Check Agent's Phone Configuration

Ask the agent to check their SIP phone settings:

1. **Codec Settings:**
   - Ensure PCMU (G.711 μ-law) or PCMA (G.711 A-law) is enabled
   - Disable video codecs if enabled

2. **NAT Settings:**
   - Enable "NAT Traversal" or "STUN"
   - Set "STUN Server" to: `stun:stun.l.google.com:19302`

3. **Network:**
   - Check if phone can reach FusionPBX IP `136.115.41.45`
   - Test from agent's network: `telnet 136.115.41.45 5060`

### Step 8: Check Media Mode in FreeSWITCH

```bash
# Check media mode for extension 2001
fs_cli -x "user_data 2001@136.115.41.45 var" | grep -i "media"

# Check if media bypass is enabled (should be disabled for Twilio)
fs_cli -x "sofia xmlstatus profile external" | grep -i "bypass"
```

## 🔧 Solutions

### Solution 1: Fix Codec Mismatch (Most Common)

**Force PCMU/PCMA on External Profile:**

1. **Via FusionPBX GUI:**
   ```
   Advanced → SIP Profiles → external → Edit
   → Settings tab
   → Find "Codec Preferences"
   → Set:
       Inbound Codec Preferences: PCMU,PCMA
       Outbound Codec Preferences: PCMU,PCMA
   → Save → Apply Config
   ```

2. **Via CLI (edit `/etc/freeswitch/sip_profiles/external.xml`):**
   ```xml
   <param name="inbound-codec-prefs" value="PCMU,PCMA"/>
   <param name="outbound-codec-prefs" value="PCMU,PCMA"/>
   ```

3. **Reload SIP Profile:**
   ```bash
   fs_cli -x "reload mod_sofia"
   # Or via FusionPBX GUI: Status → SIP Status → external → Reload XML → Restart
   ```

### Solution 2: Fix RTP IP Addresses

**Ensure External Profile Advertises Correct Public IP:**

1. **Check `/etc/freeswitch/sip_profiles/external.xml`:**
   ```xml
   <param name="ext-sip-ip" value="136.115.41.45"/>
   <param name="ext-rtp-ip" value="136.115.41.45"/>
   <param name="sip-force-contact" value="136.115.41.45:5060"/>
   <param name="rtp-force-contact" value="136.115.41.45"/>
   ```

2. **Reload:**
   ```bash
   fs_cli -x "reload mod_sofia"
   ```

### Solution 3: Open Firewall Ports for RTP

```bash
# Open RTP port range (UDP 10000-20000)
ufw allow 10000:20000/udp

# Or with iptables
iptables -A INPUT -p udp --dport 10000:20000 -j ACCEPT
iptables-save

# Also ensure SIP port is open
ufw allow 5060/udp
ufw allow 5060/tcp
```

### Solution 4: Disable Media Bypass

Media bypass can cause issues with Twilio transfers:

```bash
# Check current setting
fs_cli -x "sofia xmlstatus profile external" | grep -i "bypass"

# Edit `/etc/freeswitch/sip_profiles/external.xml`
# Ensure these are set:
<param name="bypass-media" value="false"/>
<param name="media-bypass" value="false"/>

# Reload
fs_cli -x "reload mod_sofia"
```

### Solution 5: Configure NAT Traversal

```xml
<!-- In external.xml -->
<param name="aggressive-nat-detection" value="true"/>
<param name="local-network-acl" value="localnet.auto"/>
<param name="apply-nat-acl" value="nat.auto"/>
<param name="rtp-ip" value="10.128.0.8"/>
<param name="ext-rtp-ip" value="136.115.41.45"/>
```

### Solution 6: Check Extension 2001's Media Settings

1. **Via FusionPBX GUI:**
   ```
   Accounts → Extensions → 2001 → Advanced tab
   → Check "Codec" settings
   → Ensure PCMU or PCMA is selected
   → Save
   ```

2. **Check Extension's Domain:**
   ```
   Accounts → Extensions → 2001 → Advanced tab
   → Ensure "Domain" is set to: 136.115.41.45 (or your domain)
   ```

### Solution 7: Test with Direct SIP Call

Test if the issue is specific to Twilio transfers:

```bash
# From another SIP client, make a direct call to extension 2001
# Using sip:2001@136.115.41.45:5060

# If this works, the issue is Twilio-specific
# If this also drops, the issue is with extension 2001 or FusionPBX configuration
```

## 📊 Detailed Log Analysis

When reviewing logs, look for these specific patterns:

### Good Signs (Call Should Work):
```
[NOTICE] sofia.c:xxxx Channel [sofia/internal/2001@...] has been answered
[DEBUG] switch_rtp.c:xxxx RTP Server Ready [external IP:136.115.41.45:xxxx]
[DEBUG] switch_rtp.c:xxxx Starting timer [soft] 160 bytes [60]ms
[INFO] switch_core_media.c:xxxx Media Codec [PCMU] Negotiation Complete
```

### Bad Signs (Call Will Drop):
```
[WARNING] sofia.c:xxxx Failed to establish RTP stream
[ERROR] switch_rtp.c:xxxx RTP timeout waiting for media
[NOTICE] sofia.c:xxxx Hangup sofia/internal/2001@... [CS_CONSUME_MEDIA] [CALL_REJECTED]
[WARNING] switch_core_media.c:xxxx Codec negotiation failed
```

## 🎯 Quick Fix Checklist

Run through these in order:

- [ ] **Codec mismatch:** Force PCMU/PCMA on external profile
- [ ] **RTP IPs:** Verify `ext-rtp-ip` is `136.115.41.45`
- [ ] **Firewall:** Open UDP ports 10000-20000
- [ ] **Media bypass:** Disable media bypass on external profile
- [ ] **Extension codec:** Ensure extension 2001 supports PCMU/PCMA
- [ ] **NAT settings:** Enable aggressive NAT detection
- [ ] **Test internal:** Verify extension 2001 works for internal calls
- [ ] **Agent phone:** Check agent's SIP phone codec and NAT settings

## 🔍 Still Not Working?

If the call still drops after trying all solutions:

1. **Capture Full SIP Trace:**
   ```bash
   fs_cli -x "sofia loglevel all 9"
   # Attempt transfer and capture full output
   tail -f /var/log/freeswitch/freeswitch.log > /tmp/sip_trace.log
   ```

2. **Check Twilio Call Logs:**
   - Go to Twilio Console → Monitor → Logs → Calls
   - Find the failed transfer call
   - Check "Media Streams" section
   - Look for RTP/STUN errors

3. **Test with Different Extension:**
   ```bash
   # Try transferring to extension 2002
   # If 2002 works, the issue is specific to extension 2001
   ```

4. **Check FreeSWITCH Version:**
   ```bash
   freeswitch -version
   # Older versions may have media handling bugs
   ```

## 📝 Summary

The most common cause of `CALL_REJECTED` after answer is **media negotiation failure**. Focus on:

1. **Codec compatibility** (PCMU/PCMA)
2. **RTP IP addresses** (must advertise public IP)
3. **Firewall rules** (RTP ports 10000-20000 UDP)
4. **NAT traversal** (aggressive NAT detection)

Start with Solution 1 (codec mismatch) as it's the most common issue.


# FUSIONPBX_CHECK_ENDPOINTS

# Checking FusionPBX Endpoints and Profile Status

## Understanding the "No Registrations" Message

The `external` SIP profile shows 0 registrations, which is **NORMAL** for Twilio transfers because:

1. ✅ **Twilio doesn't register** - it uses direct SIP INVITE calls
2. ✅ **Your WebRTC extensions register** to the `internal` profile, not `external`
3. ✅ **Twilio calls go to `external`** profile without registration

## What to Check Instead

### 1. Check All SIP Profiles

```bash
fs_cli -x "sofia status"
```

**You should see both profiles:**
- `internal` → For internal phones/extensions (2001)
- `external` → For external SIP calls from Twilio

### 2. Check if Extension 2001 Exists in FusionPBX

```bash
# Via FusionPBX CLI
fs_cli -x "user_exists id 2001 domain-name default"

# Or check PostgreSQL/MariaDB
sudo -u postgres psql fusionpbx
SELECT * FROM v_extensions WHERE extension = '2001';
```

### 3. Check SIP Profile Status

```bash
# See all profiles and their status
fs_cli -x "sofia status"

# See external profile details
fs_cli -x "sofia status profile external"

# See internal profile details (where 2001 would be)
fs_cli -x "sofia status profile internal"
```

### 4. Check if Extension 2001 is Registered to INTERNAL Profile

```bash
# This is where your extension should show up
fs_cli -x "sofia status profile internal reg"

# Should show:
# call-id: xxx@internal
# user: 2001
# contact: sip:2001@...
# registered: true
```

### 5. Check Dial Plan Context

```bash
# See dialplan contexts
fs_cli -x "dialplan_reload"
fs_cli -x "dialplan_loglevel 9"

# Test if extension 2001 is in dialplan
fs_cli -x "dialplan_lookup context=from-external number=2001"
```

## Critical Configuration Check

Since Twilio is calling extension 2001 on the `external` profile, you need:

### Check Dial Plan for Twilio Calls

```bash
# Check what context external calls go to
fs_cli -x "sofia xmlstatus profile external" | grep context

# Should show something like:
# <context>public</context>
# OR
# <context>from-external</context>
```

### Verify Extension 2001 Context

Twilio calls come in on `external` profile → need to route to extension 2001

```bash
# Check the dialplan context for external calls
fs_cli -x "xml_locate directory domain default 2001"
```

## Next Steps

1. **Check extension 2001 exists:**
   ```bash
   sudo -u postgres psql fusionpbx -c "SELECT * FROM v_extensions WHERE extension = '2001';"
   ```

2. **Check which profile extension 2001 uses:**
   - Go to FusionPBX GUI: `Accounts → Extensions → 2001`
   - Check "SIP Profile" setting

3. **Check external profile ACL is configured:**
   ```bash
   fs_cli -x "sofia xmlstatus profile external" | grep apply-inbound-acl
   ```
   Should show: `<apply-inbound-acl>Twilio-SIP</apply-inbound-acl>`

## If Extension 2001 Doesn't Exist

You need to create it in FusionPBX:

1. Login to FusionPBX: `https://136.115.41.45`
2. Go to: `Accounts → Extensions → Add Extension`
3. Create extension:
   - Extension: `2001`
   - Password: (set a secure password)
   - Display Name: "Support Agent"
   - SIP Profile: `internal` (for registration)
   - Context: (usually `default`)
   - Save

4. Create a SIP phone registration or configure a device to use it

## Common Issues

### Issue: Extension Not Reachable from External

**Problem:** Extension 2001 is in `internal` profile, but Twilio calls come to `external` profile

**Solution:** Check dial plan routes external → internal calls

### Issue: "Extension Not Found"

**Check:**
```bash
fs_cli -x "user_exists id 2001 domain-name default"
```

**If false, create the extension in FusionPBX GUI**

### Issue: No Audio After Transfer

**Problem:** RTP ports not open or NAT issues

**Solution:**
- Check firewall allows UDP 10000-20000
- Verify `ext-rtp-ip` is set to public IP in SIP profile



# FUSIONPBX_ENABLE_WEBRTC_PROFILE

# FusionPBX WebRTC Profile Setup - Detailed Steps

## Overview

This guide provides detailed step-by-step instructions to enable and configure the WebRTC (wss) SIP profile in FusionPBX, which allows WebRTC clients to connect directly to FusionPBX.

**Your Configuration:**
- FusionPBX IP: `136.115.41.45`
- WebRTC Port: `7443` (default)
- Domain: `136.115.41.45`

---

## Step-by-Step Instructions

### Step 1: Access FusionPBX Admin Panel

1. **Open your web browser**
2. **Navigate to:** `https://136.115.41.45`
3. **Log in** with your admin credentials
4. **Verify you're in the admin interface**

---

### Step 2: Navigate to SIP Profiles

1. **Click on "Advanced"** in the top menu bar
2. **Click on "SIP Profiles"** from the dropdown menu
3. **You should see a list of SIP profiles** including:
   - `internal` - For internal phones/extensions
   - `external` - For external SIP calls
   - `wss` - WebRTC profile (may not be visible if not enabled)

---

### Step 3: Check Current WebRTC Profile Status

#### Option A: If "wss" profile is already listed:

1. **Look for "wss" in the profile list**
2. **Click on "wss"** to view/edit its settings
3. **Skip to Step 4** to configure settings

#### Option B: If "wss" profile is NOT listed:

The profile exists in FreeSWITCH but may not be enabled in FusionPBX. You need to enable it:

1. **Click on "Default Settings"** (if available) or check System Settings
2. **Look for WebRTC/WSS profile settings**
3. **OR proceed to enable it via database** (see Step 3B below)

#### Option B (Alternative): Enable via FreeSWITCH CLI

```bash
# SSH into your FusionPBX server
ssh root@136.115.41.45

# Access FreeSWITCH CLI
fs_cli

# Check if wss profile exists
sofia status

# If it shows "wss" profile, it's already configured
# If not, you may need to enable it
```

---

### Enable wss Profile via FreeSWITCH CLI - Detailed Steps

If the wss profile doesn't appear in the FusionPBX GUI, or you prefer to enable it via command line, follow these detailed steps:

#### Step 1: SSH into FusionPBX Server

```bash
ssh root@136.115.41.45
```

#### Step 2: Access FreeSWITCH CLI

```bash
# Method 1: Direct fs_cli command
fs_cli

# Method 2: With specific command (non-interactive)
fs_cli -x "sofia status"

# Method 3: One-time command execution
fs_cli -x "command_here"
```

**Note:** If `fs_cli` is not in your PATH, you may need to use the full path:
```bash
/usr/local/freeswitch/bin/fs_cli
# OR
/opt/freeswitch/bin/fs_cli
# OR (if installed via package)
/usr/bin/fs_cli
```

#### Step 3: Check Current Profile Status

```bash
# Check all SIP profiles
sofia status

# Expected output should show profiles like:
# Name         Type      Data        State
# =================================================================
# internal     profile   sip:mod_sofia@127.0.0.1:5060   RUNNING
# external     profile   sip:mod_sofia@127.0.0.1:5080   RUNNING
# wss          profile   sip:mod_sofia@127.0.0.1:7443   STOPPED  ← May show STOPPED or not appear
```

#### Step 4: Check if wss Profile Configuration Exists

```bash
# Check if wss profile configuration file exists
ls -la /etc/freeswitch/sip_profiles/wss.xml

# Or check FusionPBX database
sudo -u postgres psql fusionpbx -c "SELECT * FROM v_sip_profiles WHERE sip_profile_name = 'wss';"

# Check FreeSWITCH XML directory
ls -la /usr/local/freeswitch/conf/sip_profiles/wss.xml
# OR
ls -la /opt/freeswitch/conf/sip_profiles/wss.xml
```

#### Step 5: Start/Restart wss Profile

If the profile exists but is stopped:

```bash
# Start the wss profile
sofia profile wss start

# OR restart it if it's already running
sofia profile wss restart

# Check status after starting
sofia status profile wss
```

**Expected output after starting:**
```
Profile Name: wss
PROFILE STATE: RUNNING
```

#### Step 6: Create wss Profile if It Doesn't Exist

If the profile doesn't exist, you need to create it. There are two approaches:

##### Option A: Create via FusionPBX Database (Recommended)

```bash
# Connect to FusionPBX database
sudo -u postgres psql fusionpbx

# Insert wss profile into database
INSERT INTO v_sip_profiles (sip_profile_uuid, sip_profile_name, sip_profile_enabled, sip_profile_description)
VALUES (gen_random_uuid(), 'wss', 'true', 'WebRTC WebSocket Secure Profile');

# Exit database
\q

# Reload FreeSWITCH XML from database
fs_cli -x "reloadxml"
fs_cli -x "sofia profile wss start"
```

##### Option B: Create Configuration File Manually

```bash
# Create wss.xml configuration file
cat > /etc/freeswitch/sip_profiles/wss.xml << 'EOF'
<profile name="wss">
  <settings>
    <param name="name" value="wss"/>
    <param name="sip-ip" value="0.0.0.0"/>
    <param name="sip-port" value="7443"/>
    <param name="tls" value="true"/>
    <param name="tls-bind-params" value="transport=wss"/>
    <param name="ext-sip-ip" value="136.115.41.45"/>
    <param name="ext-rtp-ip" value="136.115.41.45"/>
    <param name="domain" value="136.115.41.45"/>
    <param name="codec-prefs" value="G722,PCMU,PCMA"/>
    <param name="rtp-ip" value="0.0.0.0"/>
    <param name="rtp-min-port" value="16384"/>
    <param name="rtp-max-port" value="32768"/>
    <param name="local-network-acl" value="localnet.auto"/>
    <param name="apply-nat-acl" value="nat.auto"/>
    <param name="apply-inbound-acl" value="domains"/>
    <param name="apply-register-acl" value="domains"/>
    <param name="bypass-media" value="false"/>
    <param name="media-bypass" value="false"/>
  </settings>
</profile>
EOF

# Set proper permissions
chown freeswitch:freeswitch /etc/freeswitch/sip_profiles/wss.xml
chmod 644 /etc/freeswitch/sip_profiles/wss.xml

# Reload XML configuration
fs_cli -x "reloadxml"

# Start the profile
fs_cli -x "sofia profile wss start"
```

#### Step 7: Verify wss Profile is Running

```bash
# Check profile status
fs_cli -x "sofia status profile wss"

# Expected output:
# Profile Name: wss
# PROFILE STATE: RUNNING
# ...
```

#### Step 8: Check Port is Listening

```bash
# Check if port 7443 is listening
netstat -tlnp | grep 7443

# OR using ss command
ss -tlnp | grep 7443

# Expected output:
# tcp  0  0 0.0.0.0:7443  0.0.0.0:*  LISTEN  12345/freeswitch
# OR
# tcp6  0  0 :::7443  :::*  LISTEN  12345/freeswitch
```

#### Step 9: View Detailed Profile Information

```bash
# Get detailed XML status
fs_cli -x "sofia xmlstatus profile wss"

# This will show comprehensive configuration including:
# - All settings
# - Codecs
# - ACLs
# - TLS configuration
# - RTP settings
```

#### Step 10: Enable wss Profile to Start Automatically

To ensure the profile starts automatically on FreeSWITCH restart:

```bash
# Check if profile is enabled in FusionPBX database
sudo -u postgres psql fusionpbx -c "SELECT sip_profile_name, sip_profile_enabled FROM v_sip_profiles WHERE sip_profile_name = 'wss';"

# If enabled is false, update it:
sudo -u postgres psql fusionpbx -c "UPDATE v_sip_profiles SET sip_profile_enabled = 'true' WHERE sip_profile_name = 'wss';"

# Verify
sudo -u postgres psql fusionpbx -c "SELECT sip_profile_name, sip_profile_enabled FROM v_sip_profiles WHERE sip_profile_name = 'wss';"
```

#### Step 11: Configure TLS Certificate (If Not Already Done)

The wss profile requires a TLS certificate. Check and configure:

```bash
# Check if certificate exists
ls -la /etc/freeswitch/tls/*.pem
ls -la /etc/freeswitch/tls/wss.*

# If certificate doesn't exist, generate one:
cd /etc/freeswitch/tls
openssl req -x509 -newkey rsa:4096 -keyout wss.pem -out wss.pem -days 365 -nodes -subj "/CN=136.115.41.45"

# Set permissions
chown freeswitch:freeswitch wss.pem
chmod 600 wss.pem

# Restart the profile to load certificate
fs_cli -x "sofia profile wss restart"
```

#### Step 12: Test WebRTC Connection

```bash
# Check for WebSocket connections (after a client connects)
fs_cli -x "sofia status profile wss reg"

# Should show registrations if any clients are connected
```

#### Troubleshooting Commands

If the profile won't start, use these diagnostic commands:

```bash
# Check FreeSWITCH logs for errors
tail -100 /var/log/freeswitch/freeswitch.log | grep -i wss
tail -100 /var/log/freeswitch/freeswitch.log | grep -i 7443

# Check for port conflicts
lsof -i :7443
netstat -tlnp | grep 7443

# Verify FreeSWITCH has permissions
ps aux | grep freeswitch
ls -la /etc/freeswitch/sip_profiles/

# Check configuration syntax
fs_cli -x "reloadxml"
# If errors appear, they will be shown

# Try starting with verbose logging
fs_cli -x "console loglevel debug"
fs_cli -x "sofia loglevel all 9"
fs_cli -x "sofia profile wss start"
# Then check logs
tail -f /var/log/freeswitch/freeswitch.log
```

#### Common Issues and Solutions

**Issue 1: Profile shows as STOPPED**
```bash
# Check logs for errors
tail -100 /var/log/freeswitch/freeswitch.log | grep -i error | grep -i wss

# Try restarting
fs_cli -x "sofia profile wss restart"

# Check if port is in use
lsof -i :7443
```

**Issue 2: Port 7443 already in use**
```bash
# Find what's using the port
lsof -i :7443

# Kill the process if it's not FreeSWITCH
kill -9 <PID>

# Or change port in configuration (not recommended)
```

**Issue 3: TLS certificate errors**
```bash
# Check certificate exists and is valid
openssl x509 -in /etc/freeswitch/tls/wss.pem -text -noout

# Regenerate if needed (see Step 11 above)
```

**Issue 4: Permission denied**
```bash
# Check file ownership
ls -la /etc/freeswitch/sip_profiles/wss.xml

# Fix ownership
chown freeswitch:freeswitch /etc/freeswitch/sip_profiles/wss.xml

# Fix certificate permissions
chown freeswitch:freeswitch /etc/freeswitch/tls/wss.pem
chmod 600 /etc/freeswitch/tls/wss.pem
```

#### Quick Reference Commands

```bash
# Start wss profile
fs_cli -x "sofia profile wss start"

# Stop wss profile
fs_cli -x "sofia profile wss stop"

# Restart wss profile
fs_cli -x "sofia profile wss restart"

# Check status
fs_cli -x "sofia status profile wss"

# Check all profiles
fs_cli -x "sofia status"

# Reload XML configuration
fs_cli -x "reloadxml"

# View registrations on wss profile
fs_cli -x "sofia status profile wss reg"

# Get XML status
fs_cli -x "sofia xmlstatus profile wss"
```

---

### Step 4: Configure WebRTC Profile Settings

Once you're on the **wss profile settings page**, configure the following:

#### 4.1 General Settings

**Find the "Settings" table** and configure these parameters:

| Setting Name | Value | Enabled | Description |
|-------------|-------|---------|-------------|
| **name** | `wss` | ✅ Yes | Profile name |
| **hostname** | `136.115.41.45` | ✅ Yes | Your public IP or domain |
| **domain** | `136.115.41.45` | ✅ Yes | SIP domain |

#### 4.2 Network Settings

| Setting Name | Value | Enabled | Description |
|-------------|-------|---------|-------------|
| **sip-ip** | `0.0.0.0` | ✅ Yes | Listen on all interfaces |
| **sip-port** | `7443` | ✅ Yes | WSS port (default) |
| **tls** | `true` | ✅ Yes | Enable TLS (required for WSS) |
| **tls-bind-params** | `transport=wss` | ✅ Yes | WSS transport |
| **ext-sip-ip** | `136.115.41.45` | ✅ Yes | External SIP IP |
| **ext-rtp-ip** | `136.115.41.45` | ✅ Yes | External RTP IP |

#### 4.3 WebRTC-Specific Settings

| Setting Name | Value | Enabled | Description |
|-------------|-------|---------|-------------|
| **enable-100rel** | `true` | ✅ Yes | Enable reliable provisional responses |
| **disable-register** | `false` | ✅ Yes | Allow registrations |
| **rtp-ip** | `0.0.0.0` | ✅ Yes | RTP bind IP |
| **rtp-min-port** | `16384` | ✅ Yes | RTP port range start |
| **rtp-max-port** | `32768` | ✅ Yes | RTP port range end |

#### 4.4 Codec Settings

| Setting Name | Value | Enabled | Description |
|-------------|-------|---------|-------------|
| **codec-prefs** | `G722,PCMU,PCMA` | ✅ Yes | Preferred codecs |
| **inbound-codec-prefs** | `G722,PCMU,PCMA` | ✅ Yes | Inbound codec preference |
| **outbound-codec-prefs** | `PCMU,PCMA` | ✅ Yes | Outbound codec preference |

**Codec Order:**
- **G722** - High-quality wideband audio (preferred for WebRTC)
- **PCMU** - G.711 μ-law (ULAW) - Standard codec
- **PCMA** - G.711 A-law (ALAW) - Standard codec

#### 4.5 NAT and Firewall Settings

| Setting Name | Value | Enabled | Description |
|-------------|-------|---------|-------------|
| **local-network-acl** | `localnet.auto` | ✅ Yes | Local network ACL |
| **apply-nat-acl** | `nat.auto` | ✅ Yes | NAT handling |
| **rtp-rewrite-timestamps** | `false` | ✅ Yes | RTP timestamp handling |
| **disable-transcoding** | `false` | ✅ Yes | Allow codec transcoding |

#### 4.6 ACL (Access Control) Settings

| Setting Name | Value | Enabled | Description |
|-------------|-------|---------|-------------|
| **apply-inbound-acl** | `domains` | ✅ Yes | Allow registered domains |
| **apply-register-acl** | `domains` | ✅ Yes | Allow domain registrations |

**Important:** For WebRTC, you typically want to allow connections from any domain, but you can restrict this if needed.

#### 4.7 Media Settings

| Setting Name | Value | Enabled | Description |
|-------------|-------|---------|-------------|
| **bypass-media** | `false` | ✅ Yes | Don't bypass media |
| **media-bypass** | `false` | ✅ Yes | Don't bypass media |
| **media-bypass-to** | (empty) | ❌ No | - |
| **media-bypass-from** | (empty) | ❌ No | - |

---

### Step 5: Configure TLS/SSL Certificate

WebRTC requires WSS (WebSocket Secure), which needs a valid TLS certificate.

#### Option A: Use Existing Certificate

If FusionPBX already has an SSL certificate configured:

1. **Check "tls" setting** is set to `true`
2. **Verify certificate path** in system settings
3. **Ensure certificate is valid** for `136.115.41.45`

#### Option B: Generate Self-Signed Certificate (Testing Only)

```bash
# SSH into FusionPBX server
ssh root@136.115.41.45

# Navigate to FreeSWITCH certs directory
cd /etc/freeswitch/tls

# Generate self-signed certificate (for testing)
openssl req -x509 -newkey rsa:4096 -keyout wss.pem -out wss.pem -days 365 -nodes -subj "/CN=136.115.41.45"

# Set permissions
chown freeswitch:freeswitch wss.pem
chmod 600 wss.pem

# Restart FreeSWITCH
systemctl restart freeswitch
```

#### Option C: Use Let's Encrypt Certificate (Production)

```bash
# Install certbot if not already installed
apt-get install certbot

# Obtain certificate
certbot certonly --standalone -d 136.115.41.45

# Certificate will be in: /etc/letsencrypt/live/136.115.41.45/
# Copy to FreeSWITCH directory
cp /etc/letsencrypt/live/136.115.41.45/fullchain.pem /etc/freeswitch/tls/wss.crt
cp /etc/letsencrypt/live/136.115.41.45/privkey.pem /etc/freeswitch/tls/wss.key

# Set permissions
chown freeswitch:freeswitch /etc/freeswitch/tls/wss.*
chmod 600 /etc/freeswitch/tls/wss.*

# Configure in FusionPBX or wss.xml
```

**In FusionPBX GUI:**
- Find **tls-cert-file** setting
- Set value to: `/etc/freeswitch/tls/wss.crt`
- Find **tls-key-file** setting
- Set value to: `/etc/freeswitch/tls/wss.key`

---

### Step 6: Save and Apply Settings

1. **Click "Save" button** at the bottom of the settings page
2. **Wait for confirmation message**

---

### Step 7: Reload SIP Profile

After saving, you need to reload the SIP profile:

#### Via FusionPBX GUI:

1. **Go to:** **Status → SIP Status**
2. **Find the "wss" profile** in the list
3. **Click "Reload XML"** button for the wss profile
4. **Click "Restart"** button for the wss profile
5. **Verify status shows "RUNNING"**

#### Via FreeSWITCH CLI:

```bash
# SSH into FusionPBX
ssh root@136.115.41.45

# Access FreeSWITCH CLI
fs_cli

# Reload profile
sofia profile wss restart

# Check status
sofia status profile wss
```

**Expected output:**
```
Name    wss
Domain  internal    internal
Auto-NAT    false
DBName  wss
Presence    enabled
Timer-T1    500
Timer-T2    4000
...
```

---

### Step 8: Verify WebRTC Profile is Running

#### Check 1: Via FusionPBX GUI

1. **Go to:** **Status → SIP Status**
2. **Look for "wss" profile**
3. **Status should be:** `RUNNING` (green)
4. **Listen IP:** `0.0.0.0:7443`

#### Check 2: Via FreeSWITCH CLI

```bash
fs_cli -x "sofia status profile wss"
```

**Expected output:**
```
Profile Name: wss
PROFILE STATE: RUNNING
...
```

#### Check 3: Check Port is Listening

```bash
# Check if port 7443 is listening
netstat -tlnp | grep 7443

# Or using ss
ss -tlnp | grep 7443

# Expected output:
# LISTEN  0  ... :::7443  ... freeswitch
```

#### Check 4: Test WebRTC Connection

You can test WebRTC connectivity using:

1. **FusionPBX WebRTC Client:**
   - Navigate to: `https://136.115.41.45/app/calls/`
   - Try to register an extension

2. **Browser Console:**
   - Open browser developer tools
   - Check for WebSocket connections to `wss://136.115.41.45:7443`

---

### Step 9: Firewall Configuration

Ensure port 7443 (WSS) is open in your firewall:

#### UFW (Uncomplicated Firewall):

```bash
sudo ufw allow 7443/tcp
sudo ufw allow 16384:32768/udp  # RTP port range
sudo ufw status
```

#### iptables:

```bash
# Allow WSS port
sudo iptables -A INPUT -p tcp --dport 7443 -j ACCEPT

# Allow RTP port range
sudo iptables -A INPUT -p udp --dport 16384:32768 -j ACCEPT

# Save rules
sudo iptables-save > /etc/iptables/rules.v4
```

#### Cloud Provider Firewall:

If using a cloud provider (AWS, GCP, Azure):
- **Add inbound rule:** TCP port 7443
- **Add inbound rule:** UDP ports 16384-32768

---

### Step 10: Configure Extensions for WebRTC

To use WebRTC, extensions need to be configured:

1. **Go to:** **Accounts → Extensions**
2. **Click on an extension** (e.g., 2001)
3. **Advanced tab → SIP Profile:**
   - Ensure it can use `wss` profile
   - Or allow both `internal` and `wss`

4. **Settings to check:**
   - **User Context:** `default` (or appropriate context)
   - **Transport:** Allow `wss` transport
   - **Codecs:** Match profile codecs (G722, PCMU, PCMA)

---

## Verification Checklist

After completing all steps, verify:

- [ ] wss profile exists in SIP Profiles list
- [ ] wss profile status is "RUNNING"
- [ ] Port 7443 is listening (check with `netstat` or `ss`)
- [ ] TLS certificate is configured and valid
- [ ] Firewall allows port 7443 (TCP) and 16384-32768 (UDP)
- [ ] External IP `136.115.41.45` is set correctly
- [ ] Codecs G722, PCMU, PCMA are configured
- [ ] ACL settings allow registrations
- [ ] Extension can register via WebRTC

---

## Troubleshooting

### Issue 1: Profile Not Appearing

**Symptom:** wss profile doesn't show in FusionPBX GUI

**Solution:**
```bash
# Check if profile exists in FreeSWITCH
fs_cli -x "sofia status"

# If it exists, it may need to be enabled in database
# Check database:
sudo -u postgres psql fusionpbx -c "SELECT * FROM v_sip_profiles WHERE sip_profile_name = 'wss';"
```

### Issue 2: Profile Won't Start

**Symptom:** wss profile shows "STOPPED" or won't start

**Check logs:**
```bash
tail -100 /var/log/freeswitch/freeswitch.log | grep -i wss
tail -100 /var/log/freeswitch/freeswitch.log | grep -i 7443
```

**Common issues:**
- Port 7443 already in use
- Invalid TLS certificate
- Missing configuration parameters

### Issue 3: Cannot Connect from Browser

**Symptom:** WebRTC client cannot connect

**Check:**
1. Browser console for WebSocket errors
2. Firewall rules
3. TLS certificate validity
4. CORS settings (if applicable)

**Test connection:**
```bash
# Test WebSocket connection
wscat -c wss://136.115.41.45:7443

# Or using curl
curl -k https://136.115.41.45:7443
```

### Issue 4: No Audio After Connection

**Symptom:** WebRTC connects but no audio

**Check:**
1. RTP port range is open in firewall
2. Codec compatibility between client and server
3. NAT traversal settings
4. Media bypass settings

---

## Complete Configuration Example

Here's a complete example of all settings for the wss profile:

```xml
<!-- This is what the configuration should look like internally -->
<profile name="wss">
  <settings>
    <param name="name" value="wss"/>
    <param name="sip-ip" value="0.0.0.0"/>
    <param name="sip-port" value="7443"/>
    <param name="tls" value="true"/>
    <param name="tls-bind-params" value="transport=wss"/>
    <param name="ext-sip-ip" value="136.115.41.45"/>
    <param name="ext-rtp-ip" value="136.115.41.45"/>
    <param name="domain" value="136.115.41.45"/>
    <param name="codec-prefs" value="G722,PCMU,PCMA"/>
    <param name="rtp-ip" value="0.0.0.0"/>
    <param name="rtp-min-port" value="16384"/>
    <param name="rtp-max-port" value="32768"/>
    <param name="local-network-acl" value="localnet.auto"/>
    <param name="apply-nat-acl" value="nat.auto"/>
    <param name="apply-inbound-acl" value="domains"/>
    <param name="apply-register-acl" value="domains"/>
    <param name="bypass-media" value="false"/>
    <param name="media-bypass" value="false"/>
  </settings>
</profile>
```

---

## Next Steps

After enabling the WebRTC profile:

1. **Test WebRTC connection** using FusionPBX's built-in client
2. **Configure extensions** to allow WebRTC registration
3. **Implement server-side bridge** (if needed for direct transfer)
4. **Update your application** to use WSS endpoint: `wss://136.115.41.45:7443`

---

## Additional Resources

- **FusionPBX Documentation:** https://docs.fusionpbx.com/
- **FreeSWITCH WebRTC Guide:** https://freeswitch.org/confluence/display/FREESWITCH/WebRTC
- **FusionPBX Forum:** https://www.fusionpbx.com/

---

**Need Help?**

If you encounter issues, check:
1. FreeSWITCH logs: `/var/log/freeswitch/freeswitch.log`
2. FusionPBX logs: `/var/log/fusionpbx/`
3. Browser console for WebSocket errors
4. Firewall rules and port accessibility


# FUSIONPBX_EXTERNAL_XML_LOCATION

# Where to Put external.xml - Important Notes

## ⚠️ IMPORTANT: Don't Manually Edit external.xml if Using FusionPBX

If you're using **FusionPBX**, the `external.xml` file is **automatically generated** from FusionPBX's database. Any manual edits will be **overwritten** when you:
- Click "Reload XML" in FusionPBX GUI
- Restart FreeSWITCH
- FusionPBX regenerates the config

## 📍 File Location (For Reference Only)

If you were to manually edit it (not recommended for FusionPBX), the file location is:

```
/etc/freeswitch/sip_profiles/external.xml
```

**On your FusionPBX server:**
```bash
# The actual file used by FreeSWITCH
/etc/freeswitch/sip_profiles/external.xml

# Your project template file (in your repo)
convonet/external.xml  # This is just a reference/template
```

## ✅ Correct Way: Configure via FusionPBX GUI

**Instead of copying the XML file, configure via FusionPBX:**

1. **Login to FusionPBX:**
   ```
   https://136.115.41.45
   ```

2. **Navigate to SIP Profile:**
   ```
   Advanced → SIP Profiles → external
   ```

3. **Edit Settings:**
   - Click on the "external" profile
   - Go to "Settings" tab
   - Find each setting from `external.xml` and update it:
     - `ext-sip-ip` → Set to `136.115.41.45`
     - `ext-rtp-ip` → Set to `136.115.41.45`
     - `sip-ip` → Set to `10.128.0.8` (internal IP)
     - `rtp-ip` → Set to `10.128.0.8` (internal IP)
     - `inbound-codec-prefs` → Set to `PCMU,PCMA`
     - `outbound-codec-prefs` → Set to `PCMU,PCMA`
     - `apply-inbound-acl` → Set to `Twilio-SIP`
     - `bypass-media` → Set to `false`
     - etc.

4. **Save and Reload:**
   - Click "Save" at the bottom
   - Go to: `Status → SIP Status`
   - Find "external" profile
   - Click "Reload XML"
   - Click "Restart"

5. **Verify:**
   ```bash
   fs_cli -x "sofia xmlstatus profile external" | grep -E "ext-sip-ip|ext-rtp-ip"
   ```

## ✅ Alternative: Update Database Directly

If the GUI doesn't work, update the database:

```bash
# SSH into FusionPBX server
ssh root@136.115.41.45

# Connect to PostgreSQL
sudo -u postgres psql fusionpbx

# Update settings (example for ext-sip-ip)
UPDATE v_sip_profile_settings sps
SET sip_profile_setting_value = '136.115.41.45',
    sip_profile_setting_enabled = true
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'ext-sip-ip';

# Repeat for other settings:
# - ext-rtp-ip → 136.115.41.45
# - inbound-codec-prefs → PCMU,PCMA
# - outbound-codec-prefs → PCMU,PCMA
# - apply-inbound-acl → Twilio-SIP
# - bypass-media → false
# - media-bypass → false

\q

# Reload FreeSWITCH
fs_cli -x "reloadxml"
fs_cli -x "sofia profile external restart"
```

## 🔍 Verify Current Settings

To see what FreeSWITCH is actually using (regardless of what's in the XML file):

```bash
fs_cli -x "sofia xmlstatus profile external"
```

This shows the actual active configuration.

## 📝 Why convonet/external.xml Exists

The `convonet/external.xml` file in your project is:
- **A template/reference** for what the configuration should look like
- **Documentation** of the required settings
- **Not meant to be copied directly** to the server if using FusionPBX

If you were setting up a **standalone FreeSWITCH** (not FusionPBX), then you would:
1. Copy `convonet/external.xml` to `/etc/freeswitch/sip_profiles/external.xml`
2. Edit it as needed
3. Reload: `fs_cli -x "reloadxml"`

But since you're using FusionPBX, always configure via the GUI or database.

## 🎯 Summary

- **File location:** `/etc/freeswitch/sip_profiles/external.xml` (on FusionPBX server)
- **Don't edit it manually** - FusionPBX will overwrite it
- **Use FusionPBX GUI** instead: `Advanced → SIP Profiles → external → Settings`
- **Or update database:** `v_sip_profile_settings` table
- **Verify:** `fs_cli -x "sofia xmlstatus profile external"`


# FUSIONPBX_FIX_603_DECLINE_CALLER_ID

# Fix SIP 603 Decline - Extension 2003 Rejecting Calls

## 🔍 Problem Identified

**Error:** `SIP 603 Decline` / `CALL_REJECTED` when extension 2003 answers

**Evidence from logs:**
```
[DEBUG] sofia.c:7493 Channel sofia/internal/2003@198.27.217.12:61342 entering state [terminated][603]
[NOTICE] sofia.c:8736 Hangup sofia/internal/2003@198.27.217.12:61342 [CS_CONSUME_MEDIA] [CALL_REJECTED]
[DEBUG] mod_sofia.c:463 sofia/internal/2001@136.115.41.45 Overriding SIP cause 480 with 603 from the other leg
```

**Root Cause:** Extension 2003's phone is explicitly rejecting the call with SIP 603. Most likely causes:
1. **Caller ID is the extension itself** (e.g., 2001 calling shows as "2001" as caller ID)
2. **Phone has auto-reject enabled** for certain caller IDs
3. **Phone settings** configured to reject calls

## 🎯 Solution 1: Fix Caller ID in FusionPBX Dialplan

The FusionPBX dialplan might be setting the caller ID to the extension number, which phones often reject. We need to set proper caller ID.

### Check Current Caller ID Settings

```bash
# Check what caller ID is being sent
tail -200 /var/log/freeswitch/freeswitch.log | grep -iE "caller.*id|effective.*caller|origination.*caller" | grep -iE "2001|2003"
```

### Fix Caller ID via Database

Check and update extension 2001's caller ID:

```bash
# Check current caller ID settings for extension 2001
sudo -u postgres psql fusionpbx -c "SELECT extension, effective_caller_id_name, effective_caller_id_number, outbound_caller_id_name, outbound_caller_id_number FROM v_extensions WHERE extension = '2001';"

# Check extension 2003 settings too
sudo -u postgres psql fusionpbx -c "SELECT extension, effective_caller_id_name, effective_caller_id_number, outbound_caller_id_name, outbound_caller_id_number FROM v_extensions WHERE extension = '2003';"
```

### Fix via FusionPBX GUI

1. **Log into FusionPBX web interface**
2. Go to **Accounts** → **Extensions**
3. Click on extension **2001** (the one making the call)
4. Find **Caller ID** section
5. Set:
   - **Effective Caller ID Name:** Something descriptive like "Extension 2001" or "Agent 2001"
   - **Effective Caller ID Number:** `2001` (can keep as extension, or set to a display number)
   - **Outbound Caller ID Name:** Same as above
   - **Outbound Caller ID Number:** `2001` or a display number
6. **Save**
7. **Reload FreeSWITCH:**
   ```bash
   fs_cli -x "reload mod_sofia"
   fs_cli -x "reloadxml"
   ```

### Fix via SQL (If needed)

```bash
# Update extension 2001's caller ID
sudo -u postgres psql fusionpbx << EOF
UPDATE v_extensions 
SET 
  effective_caller_id_name = 'Extension 2001',
  outbound_caller_id_name = 'Extension 2001'
WHERE extension = '2001';
EOF

# Reload FreeSWITCH
fs_cli -x "reload mod_sofia"
fs_cli -x "reloadxml"
```

## 🎯 Solution 2: Check Phone Settings for Extension 2003

The phone itself might have settings causing it to reject calls.

### Common Phone Settings to Check:

1. **Call Rejection / Blacklist:**
   - Check if extension 2001 is in a blacklist
   - Disable auto-reject features

2. **Call Filtering:**
   - Check if the phone has call filtering enabled
   - Verify it's not set to reject calls from specific numbers

3. **Do Not Disturb (DND):**
   - Make sure DND is disabled on extension 2003's phone

4. **Call Settings:**
   - Check if "Reject anonymous calls" is enabled (might reject if caller ID is missing)
   - Check if "Reject calls from blocked numbers" is enabled

### Test from FusionPBX CLI:

Test if FreeSWITCH can successfully call extension 2003:

```bash
# Test calling extension 2003 directly from FreeSWITCH CLI
fs_cli -x "originate {origination_caller_id_name='Test Call',origination_caller_id_number='9999'}user/2003@136.115.41.45 &echo()"
```

**If this works:** The issue is with the caller ID from extension 2001
**If this also fails:** The issue is with extension 2003's phone settings or configuration

## 🎯 Solution 3: Check Dialplan Caller ID Export

Check if the dialplan is properly exporting caller ID:

```bash
# Check dialplan for caller ID exports
grep -r "caller.*id" /usr/share/freeswitch/conf/dialplan/default/
grep -r "effective.*caller" /usr/share/freeswitch/conf/dialplan/default/
```

Or check in FusionPBX:
1. Go to **Advanced** → **Dialplans**
2. Find the dialplan for `136.115.41.45` domain
3. Look for **Actions** that set caller ID

## 🎯 Solution 4: Force Caller ID in Dialplan Action

If needed, we can force caller ID in the dialplan action. Check what action is being used for extension-to-extension calls:

```bash
# Find the dialplan context and action
grep -A 10 "bridge(user/" /usr/share/freeswitch/conf/dialplan/default/*.xml
```

In FusionPBX dialplan, modify the bridge action to include caller ID:

**Original:**
```xml
<action application="bridge" data="user/${destination_number}@${domain_name}"/>
```

**Modified (if needed):**
```xml
<action application="set" data="effective_caller_id_name=Extension ${caller_id_number}"/>
<action application="set" data="effective_caller_id_number=${caller_id_number}"/>
<action application="bridge" data="user/${destination_number}@${domain_name}"/>
```

**Note:** Be careful modifying dialplans directly - FusionPBX generates them. It's better to fix via GUI or database.

## 🔍 Diagnostic Commands

### Check What Caller ID Is Being Sent

```bash
# Enable detailed logging and make a call
fs_cli -x "sofia loglevel all 9"
fs_cli -x "console loglevel debug"

# Then make the call and check logs for caller ID
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "caller|From:|effective.*caller" | grep -iE "2001|2003"
```

### Check SIP INVITE Message

Look for the SIP INVITE message sent to extension 2003:

```bash
# Get SIP INVITE details
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "INVITE|From:|To:" | grep -iE "2003" | tail -20
```

## 📋 Quick Fix Checklist

- [ ] Check extension 2001's caller ID settings in FusionPBX
- [ ] Set proper Caller ID Name (not just number)
- [ ] Check extension 2003's phone settings for auto-reject
- [ ] Disable any blacklist or call filtering on extension 2003's phone
- [ ] Test call with different caller ID from CLI
- [ ] Verify caller ID in SIP INVITE messages
- [ ] Reload FreeSWITCH after making changes

## 🎯 Most Likely Fix

Based on the logs, the most likely issue is that **extension 2001 is calling with its extension number as caller ID**, and extension 2003's phone is rejecting it (possibly because it thinks it's calling itself, or due to phone settings).

**Quick fix:**
1. Set extension 2001's **Effective Caller ID Name** to something descriptive like "Extension 2001" in FusionPBX GUI
2. Make sure it's not just the number
3. Reload FreeSWITCH
4. Test the call again

## ✅ Verification

After making changes:

1. **Reload FreeSWITCH:**
   ```bash
   fs_cli -x "reload mod_sofia"
   fs_cli -x "reloadxml"
   ```

2. **Make a test call** from 2001 to 2003

3. **Check logs** for caller ID:
   ```bash
   tail -100 /var/log/freeswitch/freeswitch.log | grep -iE "caller|2001.*2003|603|CALL_REJECTED"
   ```

4. **Expected result:** No more 603 Decline, call should connect successfully


# FUSIONPBX_FIX_EXTENSION_CALLING

# Fix 403 Forbidden Error: Extension-to-Extension Calling

## 🔴 Problem

**Error:** `403 Forbidden` when trying to call between extensions
- Calling from: `2002@136.115.41.45`
- Calling to: `2001@1361154145` (note: domain format issue)
- Result: `403 Forbidden`

## 🔍 Root Causes of 403 Forbidden

A **403 Forbidden** error means the call is being **blocked/denied**, not a network issue. Common causes:

1. **ACL (Access Control List) blocking** - Extension doesn't have permission to make calls
2. **Wrong domain format** - Notice the called number: `2001@1361154145` (missing dots)
3. **Dialplan context mismatch** - Extension trying to call from wrong context
4. **Extension permissions** - Extension settings blocking outbound calls
5. **SIP profile ACL** - Internal profile ACL blocking calls

## ✅ Diagnostic Steps

### Step 1: Check Domain Format Issue

**Notice the error shows:** `2001@1361154145` (no dots)

**Should be:** `2001@136.115.41.45` (with dots)

This suggests the SIP client is using wrong domain format.

### Step 2: Check Extension 2002 Settings

```bash
# Check if extension 2002 exists and is enabled
sudo -u postgres psql fusionpbx -c "SELECT extension, enabled, description FROM v_extensions WHERE extension = '2002';"
```

**Via FusionPBX GUI:**
1. Login: `https://136.115.41.45`
2. Go to: `Accounts → Extensions → 2002`
3. Check:
   - **Enabled:** Should be ✅ Enabled
   - **Caller ID:** Should have valid caller ID
   - **Context:** Should be `default` or appropriate context

### Step 3: Check ACL Settings for Extension 2002

**Via FusionPBX GUI:**
1. Go to: `Accounts → Extensions → 2002`
2. Go to: **Advanced** tab
3. Check:
   - **Caller ID Inbound:** Should allow calls
   - **Caller ID Outbound:** Should allow calls
   - **Reject Caller ID:** Should be empty
   - **Accept Caller ID:** Should allow calls or be empty

### Step 4: Check Internal SIP Profile ACL

The `internal` SIP profile might have ACL blocking:

```bash
# Check internal profile ACL settings
fs_cli -x "sofia xmlstatus profile internal" | grep -i "apply.*acl"
```

**Via FusionPBX GUI:**
1. Go to: `Advanced → SIP Profiles → internal`
2. Check Settings:
   - `apply-inbound-acl` - Should be `domains` or allow extensions
   - `apply-register-acl` - Should be `domains`

### Step 5: Check Dialplan Context

```bash
# Check what context extension 2002 is in
fs_cli -x "user_data 2002@136.115.41.45 var" | grep context

# Check if extension 2001 is accessible from that context
fs_cli -x "xml_locate dialplan default extension 2001"
```

### Step 6: Check Extension Registration

```bash
# Check if extension 2002 is registered
fs_cli -x "sofia status profile internal reg" | grep "2002"

# Should show:
# user: 2002
# contact: sip:2002@...
# registered: true
```

## 🔧 Solutions

### Solution 1: Fix SIP Client Domain Configuration (Most Likely)

The SIP client for extension 2002 is using wrong domain format: `1361154145` instead of `136.115.41.45`

**Fix on the SIP phone/client:**
1. Check SIP account settings
2. Ensure **Domain/Realm** is set to: `136.115.41.45` (with dots)
3. Not: `1361154145` (no dots)
4. Re-register the phone

**Common SIP client settings:**
- **Domain:** `136.115.41.45`
- **Realm:** `136.115.41.45`
- **Proxy:** `136.115.41.45`
- **Username:** `2002`
- **Password:** (your extension password)

### Solution 2: Check Extension 2002 Call Permissions

**Via FusionPBX GUI:**
1. Go to: `Accounts → Extensions → 2002`
2. **Settings** tab:
   - **Outbound CID:** Should be set
   - **Caller ID Name:** Should be set
3. **Advanced** tab:
   - **Reject Caller ID:** (leave empty)
   - **Accept Caller ID:** (leave empty or allow all)
   - **Toll Allow:** Check if there are restrictions

### Solution 3: Check Internal Profile ACL

**Via FusionPBX GUI:**
1. Go to: `Advanced → SIP Profiles → internal`
2. Settings tab:
   - Find: `apply-inbound-acl`
   - Value should be: `domains` (not blocking)
   - Find: `apply-register-acl`
   - Value should be: `domains`

**Or via database:**
```bash
sudo -u postgres psql fusionpbx -c "
SELECT sip_profile_setting_name, sip_profile_setting_value 
FROM v_sip_profile_settings sps
JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
WHERE sp.sip_profile_name = 'internal'
AND sip_profile_setting_name LIKE '%acl%';
"
```

### Solution 4: Check Extension Call Forwarding/Blocking

**Via FusionPBX GUI:**
1. Go to: `Accounts → Extensions → 2002`
2. Check:
   - **Do Not Disturb:** Should be **OFF**
   - **Call Forward:** Check if enabled and blocking
   - **Follow Me:** Check if enabled

### Solution 5: Test Extension 2002 Can Make Calls

```bash
# Test if extension 2002 can originate calls
fs_cli -x "originate user/2002@136.115.41.45 &echo()"

# Or test calling extension 2001 from FreeSWITCH CLI
fs_cli -x "originate {origination_caller_id_number=2002,origination_caller_id_name=2002}user/2001@136.115.41.45 &echo()"
```

**If this works:** The issue is with the SIP client configuration
**If this fails:** The issue is with FusionPBX extension settings

### Solution 6: Check Dialplan Permissions

**Via FusionPBX GUI:**
1. Go to: `Dialplan → Destinations`
2. Check if extension 2002 has permission to dial extension 2001

**Or check via database:**
```bash
sudo -u postgres psql fusionpbx -c "
SELECT * FROM v_dialplan_details 
WHERE dialplan_detail_tag = 'action' 
AND dialplan_detail_data LIKE '%2001%';
"
```

### Solution 7: Enable Call Logging

Enable detailed logging to see why 403 is happening:

```bash
# Enable SIP debugging
fs_cli -x "sofia loglevel all 9"

# Enable console logging
fs_cli -x "console loglevel debug"

# Watch logs while attempting call
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "2002|2001|403|forbidden|deny|acl"
```

**Look for:**
- ACL deny messages
- Authentication failures
- Context/permission errors

## 🎯 Most Likely Fix

Based on the error showing `2001@1361154145` (wrong domain format), **the most likely issue is:**

1. **SIP client domain misconfiguration** - Client is using `1361154145` instead of `136.115.41.45`
2. **Fix:** Update SIP client settings to use correct domain format with dots

## 🔍 Quick Verification Checklist

Run through these in order:

- [ ] **Domain format:** SIP client uses `136.115.41.45` (with dots), not `1361154145`
- [ ] **Extension enabled:** Extension 2002 is enabled in FusionPBX
- [ ] **Extension registered:** Extension 2002 shows as registered
- [ ] **Internal profile ACL:** `apply-inbound-acl` is set to `domains` (not blocking)
- [ ] **Extension permissions:** Extension 2002 has outbound call permissions
- [ ] **Do Not Disturb:** DND is OFF for extension 2002
- [ ] **Call blocking:** No call forwarding or blocking enabled
- [ ] **Test from CLI:** Test if FreeSWITCH CLI can make the call successfully

## 📝 Expected Working Configuration

### Extension 2002 SIP Client Settings:
```
Domain/Realm: 136.115.41.45  ← Must have dots!
Username: 2002
Password: (your extension password)
Proxy: 136.115.41.45 (optional)
Transport: UDP (or WSS if using WebRTC)
Port: 5060 (or 7443 for WSS)
```

### FusionPBX Extension 2002 Settings:
```
Extension: 2002
Enabled: ✅ Yes
Context: default
Domain: 136.115.41.45
Do Not Disturb: ❌ No
Call Forward: (disabled or configured correctly)
```

### Internal SIP Profile ACL:
```
apply-inbound-acl: domains
apply-register-acl: domains
```

## 🐛 Still Getting 403?

If you still get 403 after checking everything:

1. **Enable detailed logging** (Solution 7 above)
2. **Attempt the call again**
3. **Check logs for specific deny/block reason**
4. **Look for ACL entries blocking the call**
5. **Check if there's a custom dialplan blocking calls**

Share the log output and I can help identify the specific blocking rule.


# FUSIONPBX_FIX_USER_NOT_REGISTERED

# Fix USER_NOT_REGISTERED Error - Extension 2002

## 🔍 Problem Identified

**Error:** `Cannot create outgoing channel of type [user] cause: [USER_NOT_REGISTERED]`

**Root Cause:** Extension 2002 exists in the database but is **not registered** with FreeSWITCH.

**Evidence:**
- ✅ Extension 2002 exists in database: `enabled = true`, `user_context = default`
- ❌ Extension 2002 NOT registered: `sofia status profile internal reg` shows nothing for 2002

## 🎯 Solution: Register Extension 2002

### Step 1: Verify Current Registration Status

```bash
# Check all registered extensions
fs_cli -x "sofia status profile internal reg"

# Check specifically for extension 2002 (should show nothing)
fs_cli -x "sofia status profile internal reg" | grep "2002"
```

### Step 2: Check Extension 2002 Configuration

```bash
# Verify extension exists and is enabled
sudo -u postgres psql fusionpbx -c "SELECT extension, enabled, user_context, password, auth_acl FROM v_extensions WHERE extension = '2002';"
```

### Step 3: Check SIP Profile Settings

Make sure the `internal` SIP profile is running and configured correctly:

```bash
# Check if internal profile is running
fs_cli -x "sofia status"

# Check internal profile details
fs_cli -x "sofia status profile internal"
```

### Step 4: Configure SIP Phone for Extension 2002

Your SIP phone/softphone needs to register with FusionPBX. Use these settings:

#### SIP Account Settings:
- **SIP Server / Proxy:** `136.115.41.45` (or your FusionPBX IP)
- **SIP Port:** `5060` (default)
- **Username / Extension:** `2002`
- **Password:** (Check in FusionPBX GUI or database)
- **Domain / Realm:** `136.115.41.45`
- **Transport:** `UDP` (or `TCP` if configured)
- **Register:** `Yes` / `Enabled`

#### Get Extension 2002 Password:

**Option A: FusionPBX GUI**
1. Log into FusionPBX web interface
2. Go to **Accounts** → **Extensions**
3. Find extension **2002**
4. Check the **Password** field

**Option B: Database Query**
```bash
sudo -u postgres psql fusionpbx -c "SELECT extension, password FROM v_extensions WHERE extension = '2002';"
```

**Option C: Check Extension Details**
```bash
sudo -u postgres psql fusionpbx -c "SELECT extension, password, auth_acl, effective_caller_id_name, effective_caller_id_number FROM v_extensions WHERE extension = '2002';"
```

### Step 5: Verify Registration

After configuring the SIP phone, wait a few seconds and check:

```bash
# Check if extension 2002 is now registered
fs_cli -x "sofia status profile internal reg" | grep -A 5 "2002"

# Should show something like:
# reg_user=2002@136.115.41.45
# Contact: <sip:2002@192.168.x.x:5060>
```

### Step 6: Test the Call Again

Once extension 2002 is registered, try calling from extension 2001 again.

## 🔍 Troubleshooting Registration Issues

### Issue 1: SIP Phone Not Registering

**Check 1: Firewall Rules**
```bash
# Make sure UDP port 5060 is open
sudo ufw status | grep 5060

# If not, open it
sudo ufw allow 5060/udp
```

**Check 2: ACL Settings**
```bash
# Check if internal profile has proper ACL
fs_cli -x "sofia status profile internal" | grep -i acl

# Check ACL in database
sudo -u postgres psql fusionpbx -c "SELECT * FROM v_access_control_nodes WHERE node_type = 'allow' AND node_cidr LIKE '%192.168%' OR node_cidr LIKE '%10.%';"
```

**Check 3: Registration Logs**
```bash
# Watch registration attempts in real-time
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "register|2002|auth"
```

### Issue 2: Wrong Password

If the password is incorrect, you'll see authentication errors:

```bash
# Check for auth failures
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "401|403|unauthorized|2002"
```

**Fix:** Update the password in FusionPBX GUI or reset it.

### Issue 3: Wrong Domain/Context

Make sure extension 2002 is using the correct domain:

```bash
# Check extension domain and context
sudo -u postgres psql fusionpbx -c "SELECT extension, domain_name, user_context FROM v_extensions WHERE extension = '2002';"

# Should match your SIP profile domain
fs_cli -x "sofia status profile internal" | grep "Domain"
```

### Issue 4: SIP Profile Not Accepting Registrations

Check if the internal profile has `apply-register-acl` set correctly:

```bash
# Check internal profile ACL settings
fs_cli -x "sofia xmlstatus profile internal" | grep -i "apply.*acl"
```

In FusionPBX:
1. Go to **Advanced** → **SIP Profiles**
2. Click on **internal**
3. Check **Apply Register ACL** - should be set to allow your network
4. Check **Apply Inbound ACL** - should allow registrations

## 📋 Quick Registration Test

Test if extension 2002 can register by manually checking registration:

```bash
# Force a registration check
fs_cli -x "sofia status profile internal reg 2002@136.115.41.45"

# Check all registrations
fs_cli -x "sofia status profile internal reg"
```

## 🎯 Expected Result

After extension 2002 registers successfully:

1. **Registration Check:**
   ```bash
   fs_cli -x "sofia status profile internal reg" | grep "2002"
   ```
   Should show:
   ```
   reg_user=2002@136.115.41.45
   ```

2. **Call Test:**
   - Call from extension 2001 to 2002 should work
   - No more `USER_NOT_REGISTERED` errors

## 🔧 Common SIP Phone Configuration Examples

### Grandstream Phones:
- **Account:** 2002
- **SIP Server:** 136.115.41.45
- **SIP User ID:** 2002
- **Authenticate ID:** 2002
- **Authenticate Password:** [password from FusionPBX]
- **Name:** Extension 2002

### Softphones (X-Lite, Zoiper, etc.):
- **Display Name:** 2002
- **User Name:** 2002
- **Password:** [password from FusionPBX]
- **Domain:** 136.115.41.45
- **Server / Proxy:** 136.115.41.45

### WebRTC Clients:
- **SIP URI:** `2002@136.115.41.45`
- **Password:** [password from FusionPBX]
- **Server:** `wss://136.115.41.45:7443` (for secure WebSocket)

## ✅ Verification Checklist

- [ ] Extension 2002 exists in database and is enabled
- [ ] Extension 2002 password is correct
- [ ] SIP phone is configured with correct settings
- [ ] SIP phone shows "Registered" status
- [ ] `fs_cli -x "sofia status profile internal reg"` shows 2002
- [ ] Firewall allows UDP port 5060
- [ ] Internal SIP profile ACL allows registration
- [ ] Call from 2001 to 2002 works without errors

## 🎯 Next Steps

1. **Configure SIP phone** for extension 2002 with correct credentials
2. **Verify registration** using `fs_cli` command
3. **Test call** from extension 2001 to 2002
4. If still not working, check the troubleshooting section above


# FUSIONPBX_GET_CALL_DROP_LOGS

# Get FusionPBX Logs for Call Drops When Answering

## 🔍 Problem
- ✅ Call dials and rings (registration working)
- ❌ Call drops immediately when answered

## 📋 Quick Commands to Get Logs

### Method 1: Real-Time Monitoring (Recommended)

Enable maximum logging and watch in real-time, then make the call:

```bash
# Enable maximum logging
fs_cli -x "sofia loglevel all 9"
fs_cli -x "console loglevel debug"

# Watch logs in real-time - make the call now!
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "2001|2003|answer|bridge|media|rtp|codec|hangup|486|603|decline|reject|failed"
```

### Method 2: Capture Full Call Flow

Get logs for the specific call after it happens:

```bash
# Get recent logs with extensions 2001 and 2003
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "2001|2003" | tail -100

# Get logs with answer/bridge/hangup events
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "answer|bridge|hangup|2001|2003" | tail -100
```

### Method 3: Get Call-Specific Logs by Call UUID

1. First, get the call UUID from recent logs:
```bash
# Find the most recent call UUID involving 2001 and 2003
tail -200 /var/log/freeswitch/freeswitch.log | grep -E "New Channel.*2001|New Channel.*2003" | tail -1
```

2. Then get all logs for that call:
```bash
# Replace CALL_UUID with the actual UUID from step 1
grep "CALL_UUID" /var/log/freeswitch/freeswitch.log | tail -200
```

### Method 4: Get Logs with Context (Before/After Answer)

Get logs showing what happens right before and after answering:

```bash
# Get logs with 5 lines before and after matches
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "2001|2003" -A 5 -B 5 | tail -150

# Focus on answer/bridge events
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "answer|bridge|hangup" -A 10 -B 10 | grep -iE "2001|2003" | tail -100
```

## 🎯 Specific Log Searches

### 1. Look for Answer Events

```bash
# Look for answer/bridge events
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "ANSWER|CHANNEL_ANSWER|bridge.*2003" | tail -30
```

### 2. Look for Media/RTP Issues

```bash
# Look for RTP and media negotiation issues
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "rtp|media|codec|sdp|ice" | grep -iE "2001|2003" | tail -50
```

### 3. Look for Hangup/Call End Reasons

```bash
# Look for hangup causes
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "hangup|HANGUP|terminated|NORMAL|CALL_REJECTED|486|603" | grep -iE "2001|2003" | tail -30
```

### 4. Look for SIP Response Codes

```bash
# Look for SIP error codes
tail -500 /var/log/freeswitch/freeswitch.log | grep -E "SIP/2.0 [4-6][0-9][0-9]|^[0-9]{3} " | grep -iE "2001|2003" | tail -30
```

### 5. Look for Bridge Failures

```bash
# Look for bridge or media bridge failures
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "bridge.*fail|media.*fail|unable.*bridge" | grep -iE "2001|2003" | tail -30
```

## 📊 Complete Diagnostic Command

Run this to capture everything in real-time:

```bash
# Step 1: Clear previous logs (optional - be careful!)
# tail -0 /var/log/freeswitch/freeswitch.log > /dev/null

# Step 2: Enable maximum logging
fs_cli -x "sofia loglevel all 9"
fs_cli -x "console loglevel debug"

# Step 3: Start monitoring in real-time
tail -f /var/log/freeswitch/freeswitch.log | tee /tmp/call_log_$(date +%Y%m%d_%H%M%S).txt | grep -iE "2001|2003|answer|bridge|media|rtp|codec|hangup|486|603|decline|reject|failed|error|SIP/2.0"
```

**Then:**
1. Make the call from 2001 to 2003
2. Let it ring
3. Answer on 2003
4. Watch the logs as it drops
5. Stop with `Ctrl+C`
6. The full log will be saved to `/tmp/call_log_*.txt`

## 🔍 Most Important Log Sections to Check

After getting the logs, look for these specific patterns:

### 1. Answer Event
```
CHANNEL_ANSWER|CHANNEL_EXECUTE.*answer|answered
```

### 2. Media Negotiation
```
SDP|codec|RTP|media-bypass|bypass-media
```

### 3. RTP Setup
```
Starting RTP|RTP|RTCP|UDP port|media.*start
```

### 4. Hangup Cause
```
HANGUP|hangup_cause|NORMAL_CLEARING|CALL_REJECTED|486|603
```

### 5. Bridge Status
```
Bridge|bridge.*2003|unable.*bridge|bridge.*fail
```

## 📋 Extract Logs by Time Range

If you know approximately when the call happened:

```bash
# Get logs from last 10 minutes
tail -n +$(($(wc -l < /var/log/freeswitch/freeswitch.log) - 5000)) /var/log/freeswitch/freeswitch.log | grep -iE "2001|2003" | tail -100

# Or use journalctl if using systemd (alternative log location)
journalctl -u freeswitch -n 500 --no-pager | grep -iE "2001|2003"
```

## 🎯 Quick One-Liner for Immediate Log Capture

Run this command, then make the call:

```bash
fs_cli -x "sofia loglevel all 9" && fs_cli -x "console loglevel debug" && echo "Logging enabled. Make your call now..." && tail -f /var/log/freeswitch/freeswitch.log | grep --line-buffered -iE "2001|2003|answer|bridge|hangup|486|603|rtp|media|codec"
```

## 📝 Save Logs to File

To save logs to a file for later analysis:

```bash
# Save to file with timestamp
LOG_FILE="/tmp/fusionpbx_call_drop_$(date +%Y%m%d_%H%M%S).log"

# Enable logging and save
fs_cli -x "sofia loglevel all 9"
fs_cli -x "console loglevel debug"

# Start capturing
tail -f /var/log/freeswitch/freeswitch.log | tee "$LOG_FILE" | grep -iE "2001|2003"
```

After the call, check the file:
```bash
cat "$LOG_FILE" | grep -iE "answer|bridge|hangup|486|603|rtp|media"
```

## 🔍 Common Issues to Look For

Based on the symptoms (drops when answered), check for:

1. **Codec Mismatch:**
   ```bash
   tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "codec|no.*codec|codec.*fail" | grep -iE "2001|2003"
   ```

2. **RTP Port Issues:**
   ```bash
   tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "RTP|rtp.*port|UDP.*port" | grep -iE "2001|2003"
   ```

3. **Media Bypass Issues:**
   ```bash
   tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "bypass.*media|media.*bypass" | grep -iE "2001|2003"
   ```

4. **SIP Reject (486/603):**
   ```bash
   tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "486|603|Busy|Decline" | grep -iE "2001|2003"
   ```

## ✅ Next Steps

1. **Run the real-time monitoring command** above
2. **Make the call** from 2001 to 2003
3. **Answer on 2003** and watch the logs
4. **Share the logs** showing what happens when you answer
5. Look specifically for:
   - Answer events
   - Media negotiation
   - RTP setup
   - Hangup causes

This will help identify why the call drops when answered!


# FUSIONPBX_GET_LOGS_FOR_403

# Get Logs for 403 Forbidden Error

## 🎯 Quick Commands to Get Logs

### Method 1: Watch Logs in Real-Time (Recommended)

**Before making the call:**
```bash
# Enable detailed SIP logging
fs_cli -x "sofia loglevel all 9"

# Enable console/debug logging
fs_cli -x "console loglevel debug"

# Watch logs in real-time (run this, then make the call)
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "2002|2001|403|forbidden|deny|acl|reject"
```

**Then make the call from extension 2002 to 2001, and watch the output.**

### Method 2: Save Logs to File

```bash
# Enable logging
fs_cli -x "sofia loglevel all 9"
fs_cli -x "console loglevel debug"

# Save logs to file (run this, then make the call)
tail -f /var/log/freeswitch/freeswitch.log > /tmp/403_error.log 2>&1

# After the call fails, stop with Ctrl+C, then view:
cat /tmp/403_error.log | grep -iE "2002|2001|403|forbidden|deny|acl|reject"
```

### Method 3: Get Last 100 Lines of Log

```bash
# Get recent log entries
tail -100 /var/log/freeswitch/freeswitch.log | grep -iE "2002|2001|403|forbidden|deny"
```

### Method 4: Search Logs for Specific Timeframe

```bash
# Get logs from last 5 minutes
tail -500 /var/log/freeswitch/freeswitch.log | grep -iE "2002|2001|403|forbidden"

# Or search all logs for today
grep -iE "2002.*2001|403|forbidden" /var/log/freeswitch/freeswitch.log | tail -50
```

## 🔍 Detailed Logging Commands

### Enable Maximum Debugging

```bash
# Connect to FreeSWITCH CLI
fs_cli

# Then run these commands in fs_cli:
sofia loglevel all 9
console loglevel debug
loglevel debug

# Exit fs_cli
/exit
```

### Watch All SIP Messages

```bash
# Watch all SIP messages (very verbose)
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "sofia|sip|invite|2002|2001"
```

### Watch for ACL/Authorization Messages

```bash
# Focus on ACL and authorization messages
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "acl|deny|allow|403|forbidden|authorization|auth"
```

## 📊 What to Look For in Logs

When you get the logs, look for these patterns:

### Good Signs (Should See):
```
[INFO] sofia.c: Received SIP INVITE from 2002@...
[DEBUG] sofia.c: ACL check for IP ...: ALLOW
[INFO] mod_dialplan_xml.c: Processing 2002 -> 2001 in context ...
```

### Bad Signs (403 Forbidden Causes):
```
[WARNING] sofia.c: IP ... Denied by acl "..."
[ERROR] sofia.c: 403 Forbidden
[NOTICE] sofia.c: Rejecting INVITE from ... - ACL deny
[WARNING] sofia.c: Authentication failed for 2002@...
[ERROR] switch_ivr_originate.c: Permission denied
```

## 🎯 Complete Logging Script

Save this as a script to capture everything:

```bash
#!/bin/bash
# Save as: capture_403_logs.sh

echo "=== Starting Log Capture ==="
echo "Make a call from 2002 to 2001 now..."
echo "Press Ctrl+C when call fails to stop logging"
echo ""

# Enable logging
fs_cli -x "sofia loglevel all 9" > /dev/null 2>&1
fs_cli -x "console loglevel debug" > /dev/null 2>&1

# Capture logs
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/tmp/403_error_${TIMESTAMP}.log"

echo "Logging to: $LOG_FILE"
echo ""

tail -f /var/log/freeswitch/freeswitch.log | tee "$LOG_FILE" | grep -iE "2002|2001|403|forbidden|deny|acl|reject|sofia|invite|auth"
```

**Usage:**
```bash
chmod +x capture_403_logs.sh
./capture_403_logs.sh
# Make the call, wait for error, then Ctrl+C
# Check the log file:
cat /tmp/403_error_*.log
```

## 📋 One-Liner Commands (Copy & Paste)

### Get logs for last call attempt:
```bash
tail -200 /var/log/freeswitch/freeswitch.log | grep -A 5 -B 5 -iE "2002.*2001|403|forbidden"
```

### Get all 403 errors from today:
```bash
grep -i "403\|forbidden" /var/log/freeswitch/freeswitch.log | tail -20
```

### Get ACL deny messages:
```bash
grep -i "deny\|acl" /var/log/freeswitch/freeswitch.log | grep -iE "2002|2001" | tail -20
```

### Get full call flow for debugging:
```bash
fs_cli -x "sofia loglevel all 9" && tail -f /var/log/freeswitch/freeswitch.log | grep -iE "2002|2001"
```

## 🔍 Alternative: Check FreeSWITCH Console Directly

```bash
# Connect to FreeSWITCH console
fs_cli

# Enable verbose logging
sofia loglevel all 9
console loglevel debug

# Watch console output directly
# Then make the call and watch the output in real-time
```

## 📝 After Getting Logs

Once you have the logs, share them and look for:

1. **ACL deny messages** - Shows which ACL is blocking
2. **Authentication failures** - Shows auth issues
3. **Context/permission errors** - Shows dialplan issues
4. **Domain mismatch errors** - Shows domain format issues

**Common log patterns that cause 403:**
- `Denied by acl "..."` - ACL blocking
- `403 Forbidden` - Explicit rejection
- `Authentication failed` - Auth issue
- `Permission denied` - Extension permissions
- `Invalid domain` - Domain format issue

## 🎯 Recommended Command

**Run this before making the call:**
```bash
fs_cli -x "sofia loglevel all 9" && fs_cli -x "console loglevel debug" && tail -f /var/log/freeswitch/freeswitch.log | grep -iE "2002|2001|403|forbidden|deny|acl|reject|auth"
```

Then make the call from 2002 to 2001 and watch the output!


# FUSIONPBX_LOGGING_GUIDE

# FusionPBX/FreeSWITCH Logging Guide

## Finding Logs for Failed Dialing

### Main Log Locations

**FreeSWITCH Main Log:**
```bash
# Main log file
/var/log/freeswitch/freeswitch.log

# Rotated logs (daily)
/var/log/freeswitch/freeswitch.log.2024-01-15

# CDR (Call Detail Records) - shows all call attempts
/var/log/freeswitch/cdr-csv/Master.csv
```

### Quick Log Commands

```bash
# SSH into FusionPBX server
ssh root@136.115.41.45

# View recent log entries (last 100 lines)
tail -100 /var/log/freeswitch/freeswitch.log

# Follow log in real-time (press Ctrl+C to stop)
tail -f /var/log/freeswitch/freeswitch.log

# Search for extension 2001 or 2002
grep -i "2001\|2002" /var/log/freeswitch/freeswitch.log | tail -50

# Search for errors related to extensions
grep -i "error\|fail\|reject" /var/log/freeswitch/freeswitch.log | grep -i "2001\|2002" | tail -50

# Check CDR for call attempts
tail -50 /var/log/freeswitch/cdr-csv/Master.csv | grep -i "2001\|2002"
```

### Enable Detailed Logging via fs_cli

```bash
# Connect to FreeSWITCH CLI
fs_cli

# Enable debug logging (level 9 = most verbose)
fs_cli> console loglevel 9

# Enable SIP debug logging
fs_cli> sofia loglevel all 9

# Enable dialplan debug
fs_cli> dialplan_loglevel 9

# Watch logs in real-time
fs_cli> /log level 9

# Exit fs_cli
fs_cli> /exit
```

### Check Specific Extension Issues

```bash
# Check if extension 2001 exists in directory
fs_cli -x "user_exists id 2001 domain-name default"

# Check extension details
fs_cli -x "xml_locate directory domain default 2001"

# Check dialplan for extension
fs_cli -x "dialplan_lookup context=public number=2001"

# Check what happens when dialing extension
fs_cli -x "originate user/2001@default &echo"
```

### Search for Twilio Transfer Failures

```bash
# Search for Twilio-related logs
grep -i "twilio\|136.115.41.45\|sip:2001" /var/log/freeswitch/freeswitch.log | tail -50

# Search for SIP INVITE failures
grep -i "invite\|487\|404\|408\|503" /var/log/freeswitch/freeswitch.log | grep -i "2001\|2002" | tail -50

# Search for authentication failures
grep -i "auth\|401\|403" /var/log/freeswitch/freeswitch.log | tail -50
```

### Check SIP Profile Logs

```bash
# Check external profile status
fs_cli -x "sofia status profile external"

# Check SIP traces (if enabled)
ls -la /var/log/freeswitch/sip-traces/

# Enable SIP trace capture
fs_cli -x "sofia global siptrace on"
```

### Common Error Messages to Look For

**Extension Not Found (404):**
```
NOT_FOUND [sofia_contact(2001@default)]
```
**Solution:** Extension doesn't exist or wrong domain

**User Not Registered:**
```
USER_NOT_REGISTERED [2001@default]
```
**Solution:** Extension exists but phone isn't registered

**Invalid Gateway:**
```
INVALID_GATEWAY
```
**Solution:** SIP profile configuration issue

**Call Rejected:**
```
CALL_REJECTED
```
**Solution:** ACL or firewall blocking

**Timeout:**
```
TIMEOUT
```
**Solution:** Network or routing issue

### Real-Time Monitoring During Transfer

```bash
# Terminal 1: Follow main log
tail -f /var/log/freeswitch/freeswitch.log

# Terminal 2: Follow SIP log
fs_cli -x "/log level 7"
fs_cli -x "sofia loglevel all 7"

# Terminal 3: Watch for calls
watch -n 1 'fs_cli -x "show channels"'
```

### Check Extension Registration Status

```bash
# Check if extension 2001 is registered
fs_cli -x "sofia status profile internal reg" | grep -i 2001

# Check all registrations
fs_cli -x "sofia status profile internal reg"

# Check if extension is active
fs_cli -x "user_data 2001@default var presence_id"
```

### Check Dialplan Context

```bash
# List all dialplan contexts
fs_cli -x "dialplan_reload"
fs_cli -x "xml_locate dialplan"

# Test dialplan for extension 2001
fs_cli -x "dialplan_lookup context=public number=2001"
fs_cli -x "dialplan_lookup context=from-external number=2001"
fs_cli -x "dialplan_lookup context=default number=2001"
```

### FusionPBX Web GUI Logs

1. **Login to FusionPBX:**
   ```
   https://136.115.41.45
   ```

2. **View Logs:**
   - `Status → System Logs → FreeSWITCH Log`
   - `Status → SIP Status → Logs`
   - `Status → System Status → Log Viewer`

3. **CDR (Call Detail Records):**
   - `Reports → CDR → Search`
   - Filter by extension: `2001` or `2002`
   - Check call status and duration

### Enable Verbose Logging in FusionPBX GUI

1. **Go to:** `Advanced → System → Settings`
2. **Find:** `Log Level` or `Debug Level`
3. **Set to:** `DEBUG` or `9`
4. **Save**
5. **Reload FreeSWITCH:** `Status → SIP Status → Reload`

### Export Logs for Analysis

```bash
# Export last 1000 lines of log with errors
grep -i "error\|fail\|2001\|2002" /var/log/freeswitch/freeswitch.log | tail -1000 > /tmp/dialing_errors.log

# Export all SIP INVITE attempts
grep -i "invite.*2001\|invite.*2002" /var/log/freeswitch/freeswitch.log > /tmp/sip_invites.log

# Export CDR for last 24 hours
tail -100 /var/log/freeswitch/cdr-csv/Master.csv > /tmp/cdr_export.csv
```

### Most Useful Command for Your Issue

Run this single command to see recent failures:

```bash
# SSH into FusionPBX
ssh root@136.115.41.45

# One command to rule them all
tail -200 /var/log/freeswitch/freeswitch.log | grep -iE "2001|2002|error|fail|invite" | tail -50
```

This will show the last 50 relevant log entries about extensions 2001/2002, errors, failures, and INVITE attempts.


# FUSIONPBX_QUICK_SETUP

# FusionPBX Quick Setup for Twilio Transfer

## The One Thing You're Missing

Based on your error logs and screenshots, you have:
- ✅ Access Control List `Twilio-SIP` created correctly
- ❌ **SIP Profile not configured to USE the ACL**

## Quick Fix

### Via FusionPBX GUI (Easiest)

1. Login: `https://136.115.41.45`
2. Go to: `Advanced → SIP Profiles → external`
3. Find the row labeled: `apply-inbound-acl`
4. Change its **Value** to: `Twilio-SIP`
5. Make sure **Enabled** is checked ✅
6. Click **Save** at the bottom
7. Go to: `Status → SIP Status`
8. Find "external" profile
9. Click **Reload XML**
10. Click **Restart**

That's it! The SIP profile now knows to use your `Twilio-SIP` ACL.

### Via Database (If GUI Doesn't Work)

```bash
ssh root@136.115.41.45

# PostgreSQL
sudo -u postgres psql fusionpbx

UPDATE v_sip_profile_settings sps
SET sip_profile_setting_value = 'Twilio-SIP'
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

UPDATE v_sip_profile_settings sps
SET sip_profile_setting_enabled = true
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

\q

fs_cli -x "reload"
```

---

## What's Happening?

1. You created the **Access Control List** → ✅ Twilio IPs are whitelisted
2. But the **SIP Profile** doesn't know to **apply** that ACL → ❌ Still rejecting calls
3. You need to tell the SIP profile: "Use the Twilio-SIP ACL" → Missing step!

**Think of it like this:**
- ACL = A list of allowed guests
- SIP Profile = The bouncer at the door
- You created the guest list ✅
- But forgot to tell the bouncer to check it ❌

---

## Verify It Worked

```bash
ssh root@136.115.41.45
fs_cli -x "sofia xmlstatus profile external" | grep -i "apply-inbound-acl"
```

Should show:
```
<apply-inbound-acl>Twilio-SIP</apply-inbound-acl>
```

---

## Then Test

Make a test transfer call. Watch logs:

```bash
ssh root@136.115.41.45
fs_cli -x "console loglevel 9"
```

You should see SIP INVITE from Twilio IP being accepted, not rejected.



# FUSIONPBX_TROUBLESHOOT_EXTENSIONS

# FusionPBX Extension Troubleshooting Guide

## Your Current Situation

✅ **Extension 2001 IS registered** (shows Contact: `sip:2001@198.27.217.12:55965`)  
❌ **But `user_exists` returns false** - likely a domain mismatch issue

## Correct Commands for Your Setup

### Check Extension Registration (CORRECT)

```bash
# Check ALL registered extensions on internal profile
fs_cli -x "sofia status profile internal reg"

# Check specific extension registration
fs_cli -x "sofia status profile internal reg" | grep -i "2001\|2002"

# Your extension is registered to domain: 136.115.41.45 (your IP)
# So check with that domain:
fs_cli -x "user_exists id 2001 domain-name 136.115.41.45"
```

### Check Extension in Directory (Multiple Methods)

```bash
# Method 1: Check with IP as domain
fs_cli -x "user_exists id 2001 domain-name 136.115.41.45"

# Method 2: Check with 'default' domain (if configured)
fs_cli -x "user_exists id 2001 domain-name default"

# Method 3: Check all domains and find where 2001 exists
fs_cli -x "user_data 2001@136.115.41.45 var"

# Method 4: List all users in directory
fs_cli -x "xml_locate directory"
```

### Check Dialplan (CORRECT Syntax)

```bash
# FreeSWITCH doesn't use "dialplan_lookup context=..." syntax
# Instead, use these commands:

# Reload dialplan first
fs_cli -x "reloadxml"

# Check what dialplan contexts exist
fs_cli -x "xml_locate dialplan"

# Test dialing extension 2001 from external context
fs_cli -x "originate {origination_caller_id_number=Twilio,origination_caller_id_name=Twilio,context=public,domain_name=136.115.41.45}user/2001@136.115.41.45 &echo"

# Or simpler test
fs_cli -x "originate user/2001@136.115.41.45 &echo"
```

### Find CDR Logs (Correct Locations)

```bash
# CDR location might be different - check these:
ls -la /var/log/freeswitch/cdr-csv/
ls -la /var/log/freeswitch/cdr-csv/*.csv

# Or check FusionPBX database for CDR
sudo -u postgres psql fusionpbx -c "SELECT * FROM v_xml_cdr ORDER BY start_stamp DESC LIMIT 10;"

# Or via FusionPBX GUI:
# Reports → CDR → Search (filter by extension 2001)
```

### Check Extension Details from Database

```bash
# Check if extension exists in FusionPBX database
sudo -u postgres psql fusionpbx -c "SELECT extension, enabled, description FROM v_extensions WHERE extension IN ('2001', '2002');"

# Check extension user details
sudo -u postgres psql fusionpbx -c "SELECT extension, user_uuid, domain_uuid FROM v_extensions WHERE extension IN ('2001', '2002');"

# Check what domain the extensions belong to
sudo -u postgres psql fusionpbx -c "SELECT e.extension, d.domain_name FROM v_extensions e JOIN v_domains d ON e.domain_uuid = d.domain_uuid WHERE e.extension IN ('2001', '2002');"
```

### Check Extension Registration Details

```bash
# Get detailed registration info for 2001
fs_cli -x "sofia status profile internal reg" | grep -A 10 "2001"

# Check user data
fs_cli -x "user_data 2001@136.115.41.45 var presence_id"
fs_cli -x "user_data 2001@136.115.41.45 var contact"

# Check if extension can receive calls
fs_cli -x "user_callcenter 2001@136.115.41.45 status"
```

## Why Dialing Might Fail

### 1. Domain Mismatch

Your extension is registered as `2001@136.115.41.45`, but your transfer code might be using:
- `sip:2001@136.115.41.45` ✅ Correct
- `sip:2001@default` ❌ Wrong domain

**Check your transfer code:**
```bash
# Check what SIP URI your code is sending
grep -r "sip:2001" convonet/
grep -r "2001@" convonet/
```

### 2. Context Mismatch

Twilio calls come in on `external` profile, which uses context `public` or `from-external`.  
Extension 2001 might be in context `default` or `from-internal`.

**Check contexts:**
```bash
# Check what context external profile uses
fs_cli -x "sofia xmlstatus profile external" | grep context

# Check extension's context in database
sudo -u postgres psql fusionpbx -c "SELECT extension, user_context FROM v_extensions WHERE extension = '2001';"

# Check dialplan for external → extension routing
fs_cli -x "reloadxml"
fs_cli -x "xml_locate dialplan public"
```

### 3. Extension Not Reachable from External Profile

**Test if extension can be dialed from external context:**

```bash
# This simulates a call from external profile
fs_cli -x "originate {origination_caller_id_number=Twilio,context=public,domain_name=136.115.41.45}user/2001@136.115.41.45 &echo"
```

### 4. Check Main Log for Actual Errors

```bash
# Watch logs in real-time while attempting transfer
tail -f /var/log/freeswitch/freeswitch.log

# Or search for recent errors
tail -200 /var/log/freeswitch/freeswitch.log | grep -iE "2001|2002|error|fail|NOT_FOUND|USER_NOT_REGISTERED"
```

## Quick Diagnostic Script

Run this to check everything at once:

```bash
#!/bin/bash
echo "=== Extension 2001 Diagnostic ==="
echo ""
echo "1. Check registration:"
fs_cli -x "sofia status profile internal reg" | grep -i "2001"
echo ""
echo "2. Check database:"
sudo -u postgres psql fusionpbx -c "SELECT extension, enabled, user_context, domain_uuid FROM v_extensions WHERE extension = '2001';"
echo ""
echo "3. Check domain:"
sudo -u postgres psql fusionpbx -c "SELECT e.extension, d.domain_name FROM v_extensions e JOIN v_domains d ON e.domain_uuid = d.domain_uuid WHERE e.extension = '2001';"
echo ""
echo "4. Check external profile context:"
fs_cli -x "sofia xmlstatus profile external" | grep -i context
echo ""
echo "5. Recent log errors:"
tail -50 /var/log/freeswitch/freeswitch.log | grep -iE "2001|error|NOT_FOUND" | tail -10
```

## Most Likely Issue

Based on your output, extension 2001 **IS registered** and working. The failure is likely:

1. **Wrong SIP URI format** in your transfer code
2. **Context routing issue** - external calls can't reach extension
3. **Domain mismatch** - using wrong domain in SIP URI

**Next Steps:**
1. Check what SIP URI your code sends: `grep -r "sip:2001" convonet/`
2. Check extension's context: `sudo -u postgres psql fusionpbx -c "SELECT extension, user_context FROM v_extensions WHERE extension = '2001';"`
3. Check dialplan routing from `public` context to extension


# FUSIONPBX_TWILIO_CONFIG_GUIDE

# FusionPBX Configuration for Twilio Call Transfer

## Overview

This guide configures FusionPBX at **136.115.41.45** to accept SIP transfers from Twilio voice calls.

**Flow:**
```
Twilio Voice Call → AI Agent → Transfer to FusionPBX Extension 2001
```

## Required Configuration Steps

### Step 1: Create Access Control List (ACL) ✅ DONE

You've already created the `Twilio-SIP` access list in FusionPBX:

**Access Control Configuration:**
- **Name**: `Twilio-SIP`
- **Default**: `allow`
- **IP Ranges (CIDR)**:
  ```
  54.172.60.0/23
  54.244.51.0/24
  177.71.206.192/26
  54.252.254.64/26
  54.169.127.128/26
  ```
- **Description**: `Twilio-SIP`

This is **correctly configured**. ✅

---

### Step 2: Configure SIP Profile to Apply the ACL

**This is the critical missing step!** You need to apply the `Twilio-SIP` ACL to your SIP profile.

#### Option A: Via FusionPBX Web GUI (Recommended)

1. **Login to FusionPBX:**
   ```
   https://136.115.41.45
   ```

2. **Navigate to SIP Profiles:**
   ```
   Advanced → SIP Profiles → external
   ```

3. **Find the `external` SIP Profile Settings**

4. **Locate "Settings" Section:**
   Look for a setting called `apply-inbound-acl` in the Settings table.

5. **Update the Setting:**
   - Find the row: `apply-inbound-acl`
   - Change its **Value** from whatever it currently is to: `Twilio-SIP`
   - Make sure **Enabled** is set to `True`
   - Keep **Description** empty or add "Allow Twilio SIP traffic"

6. **Also Check These Settings:**
   - `apply-nat-acl`: Should be `nat.auto` or empty (Enabled: True)
   - `local-network-acl`: Should be `localnet.auto` (Enabled: True)
   - `ext-sip-ip`: Should be your public IP `136.115.41.45` (Enabled: True)
   - `ext-rtp-ip`: Should be your public IP `136.115.41.45` (Enabled: True)

7. **Save and Apply:**
   - Click "Save" button at the bottom
   - Go to: `Status → SIP Status`
   - Find the "external" profile
   - Click "Reload XML" button
   - Click "Restart" button

#### Option B: Via Database (If GUI Doesn't Work)

If the FusionPBX GUI doesn't allow you to modify the setting, update it via database:

**For PostgreSQL:**
```bash
# SSH into FusionPBX
ssh root@136.115.41.45

# Connect to PostgreSQL
sudo -u postgres psql fusionpbx

# Check current apply-inbound-acl setting
SELECT 
    sps.sip_profile_setting_name,
    sps.sip_profile_setting_value,
    sps.sip_profile_setting_enabled
FROM v_sip_profile_settings sps
JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
WHERE sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

# Update to use Twilio-SIP ACL
UPDATE v_sip_profile_settings sps
SET sip_profile_setting_value = 'Twilio-SIP'
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

# Make sure it's enabled
UPDATE v_sip_profile_settings sps
SET sip_profile_setting_enabled = true
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

# Verify the change
SELECT 
    sps.sip_profile_setting_name,
    sps.sip_profile_setting_value,
    sps.sip_profile_setting_enabled
FROM v_sip_profile_settings sps
JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
WHERE sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

# Exit PostgreSQL
\q

# Reload FreeSWITCH
fs_cli -x "reload"
fs_cli -x "reload mod_sofia"
```

**For MySQL/MariaDB:**
```bash
# Connect to MySQL
mysql -u root -p fusionpbx

# Update apply-inbound-acl setting
UPDATE v_sip_profile_settings sps
JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
SET sps.sip_profile_setting_value = 'Twilio-SIP',
    sps.sip_profile_setting_enabled = true
WHERE sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

# Verify
SELECT 
    sps.sip_profile_setting_name,
    sps.sip_profile_setting_value,
    sps.sip_profile_setting_enabled
FROM v_sip_profile_settings sps
JOIN v_sip_profiles sp ON sps.sip_profile_uuid = sp.sip_profile_uuid
WHERE sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

# Exit MySQL
EXIT;
```

---

### Step 3: Open Firewall Ports

#### On the Server/VPS Level

**Open UDP Port 5060 for SIP:**
```bash
# Using ufw
sudo ufw allow 5060/udp

# Using iptables
sudo iptables -A INPUT -p udp --dport 5060 -j ACCEPT
sudo iptables -A INPUT -p udp --dport 10000:20000 -j ACCEPT

# Save iptables rules (on Debian/Ubuntu)
sudo iptables-save > /etc/iptables/rules.v4
```

**Open RTP Ports 10000-20000:**
```bash
sudo ufw allow 10000:20000/udp
```

#### If Using Cloud Provider (Google Cloud, AWS, Azure, etc.)

Create firewall rules to allow SIP traffic:

**Google Cloud:**
```bash
gcloud compute firewall-rules create allow-twilio-sip \
    --direction=INGRESS \
    --action=ALLOW \
    --rules=udp:5060 \
    --source-ranges=54.172.60.0/23,54.244.51.0/24,177.71.206.192/26,54.252.254.64/26,54.169.127.128/26 \
    --target-tags=freepbx

gcloud compute firewall-rules create allow-twilio-rtp \
    --direction=INGRESS \
    --action=ALLOW \
    --rules=udp:10000-20000 \
    --source-ranges=54.172.60.0/23,54.244.51.0/24,177.71.206.192/26,54.252.254.64/26,54.169.127.128/26 \
    --target-tags=freepbx
```

**AWS:**
```bash
# Create Security Group rules for SIP
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxx \
    --protocol udp \
    --port 5060 \
    --source-group sg-twilio \
    --cidr 54.172.60.0/23,54.244.51.0/24,177.71.206.192/26,54.252.254.64/26,54.169.127.128/26
```

---

### Step 4: Verify Extension 2001 Exists

**Via FusionPBX Web GUI:**
1. Login to `https://136.115.41.45`
2. Go to: `Accounts → Extensions`
3. Search for extension `2001`
4. Verify:
   - Extension is **active**
   - Has a valid **device/endpoint** assigned
   - Is assigned to a valid **dial plan context**

**Or check via SSH:**
```bash
ssh root@136.115.41.45

# Check FreeSWITCH endpoints
fs_cli -x "sofia status profile external reg"

# Or check via Asterisk (if using)
asterisk -rx "pjsip list endpoints" | grep 2001
```

---

### Step 5: Test Configuration

#### Test 1: Verify SIP Port is Open

From your local machine:
```bash
nc -zuv 136.115.41.45 5060
```

**Expected:** `Connection to 136.115.41.45 5060 port [udp/sip] succeeded!`

#### Test 2: Check FreeSWITCH SIP Profile

```bash
ssh root@136.115.41.45
fs_cli -x "sofia xmlstatus profile external"
```

Look for:
- `<ext-sip-ip>136.115.41.45</ext-sip-ip>` ✅
- `<apply-inbound-acl>Twilio-SIP</apply-inbound-acl>` ✅

#### Test 3: Monitor FreeSWITCH Logs in Real-Time

```bash
# SSH into FusionPBX
ssh root@136.115.41.45

# Watch FreeSWITCH logs
tail -f /var/log/freeswitch/freeswitch.log | grep -i twilio

# Or use FreeSWITCH CLI
fs_cli -x "console loglevel 7"
```

#### Test 4: Make Test Transfer from Twilio

1. Make a test call to your Twilio number
2. Say "transfer me to agent" or similar
3. Watch the logs in real-time:

```bash
# On FusionPBX server
fs_cli -x "console loglevel 9"
```

**Look for:**
- SIP INVITE from Twilio IP (54.172.x.x or 54.244.x.x)
- ACK from FusionPBX
- Extension 2001 receiving the call
- Call being bridged successfully

---

### Step 6: Monitor Transfer Logs

**Watch FreeSWITCH CLI during transfer:**
```bash
ssh root@136.115.41.45
fs_cli
```

In the FreeSWITCH CLI, you should see:
```
[SIP]
[INVITE] from 54.172.x.x:5060
[200 OK] sending to 54.172.x.x:5060
[ACK] received
Extension 2001 is ringing
Call answered
RTP media established
```

---

### Troubleshooting

#### Issue: "Transfer failed" - SIP INVITE Rejected

**Symptoms:** Logs show `status=failed` in transfer callback

**Causes & Solutions:**

1. **Twilio IP not whitelisted**
   - Verify `Twilio-SIP` ACL exists in `Advanced → Firewall → Access Lists`
   - Verify `apply-inbound-acl` setting in SIP profile = `Twilio-SIP`

2. **Firewall blocking SIP**
   - Check UDP 5060 is open: `nc -zuv 136.115.41.45 5060`
   - Check cloud provider firewall rules
   - Check fail2ban isn't blocking: `sudo fail2ban-client status sshd`

3. **Extension 2001 doesn't exist**
   - Verify extension exists in `Accounts → Extensions`
   - Check extension is active and has valid device
   - Test extension from internal phone first

4. **FreeSWITCH not reloaded**
   - Go to `Status → SIP Status`
   - Click "Reload XML"
   - Click "Restart" for external profile

#### Issue: "403 Forbidden" or "401 Unauthorized"

**Cause:** SIP authentication required

**Solution:**
1. Set SIP authentication in your app's `.env`:
   ```
   FREEPBX_SIP_USERNAME=twilio
   FREEPBX_SIP_PASSWORD=your_secure_password
   ```
2. Create a SIP user in FusionPBX for Twilio
3. Or configure the extension to allow anonymous calls

#### Issue: "No audio" or "One-way audio"

**Cause:** RTP/NAT issues

**Solution:**
1. Verify RTP ports 10000-20000 are open in firewall
2. Check `ext-sip-ip` and `ext-rtp-ip` settings in SIP profile
3. Enable `rtp-symmetric` in SIP profile
4. Check NAT settings in cloud provider

#### Issue: "Extension not found" or "408 Request Timeout"

**Cause:** Extension 2001 doesn't exist, isn't registered, or wrong context

**Solution:**
1. Verify extension exists: `Accounts → Extensions → 2001`
2. Check extension device is online: `Status → Registrations`
3. Verify dial plan context is correct
4. Test from internal phone first

---

### Summary Checklist

- [x] ✅ **Step 1**: Access Control List `Twilio-SIP` created with 5 Twilio IP ranges
- [ ] ⚠️ **Step 2**: SIP Profile `external` → `apply-inbound-acl` set to `Twilio-SIP` ← **CRITICAL MISSING STEP**
- [ ] **Step 3**: UDP port 5060 open in server firewall
- [ ] **Step 4**: UDP ports 10000-20000 open for RTP
- [ ] **Step 5**: UDP ports open in cloud provider firewall (if applicable)
- [ ] **Step 6**: Extension 2001 exists and is active
- [ ] **Step 7**: FreeSWITCH reloaded after configuration changes
- [ ] **Step 8**: Test transfer successful

**Current Status:**
- FusionPBX IP: `136.115.41.45`
- Extension: `2001`
- SIP URI: `sip:2001@136.115.41.45;transport=udp`
- Access List: `Twilio-SIP` ✅ Created
- Missing: SIP Profile ACL configuration ⚠️

**Next Step:** Configure the `apply-inbound-acl` setting in your SIP profile (Step 2).


# FUSIONPBX_TWILIO_INVITE_FIX

# Fix Twilio SIP INVITE to FusionPBX Extensions

## ✅ Good News: Your Extension Works!

Your test call was **successful**:
- Extension 2001 exists and is registered ✅
- Extension can receive calls ✅  
- Dialplan routing works ✅
- RTP/media path works ✅

## 🔴 Problem: Twilio SIP INVITE Not Reaching FusionPBX

Since the internal call works but Twilio transfers fail, the issue is that **Twilio's SIP INVITE requests are either:**
1. Not reaching FusionPBX (firewall/network)
2. Being rejected by FusionPBX (ACL/authentication)
3. Using wrong SIP profile or context

## Diagnostic Steps

### Step 1: Monitor Logs During Twilio Transfer

```bash
# Watch logs in real-time while attempting a Twilio transfer
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "twilio|invite|2001|external"
```

**What to look for:**
- SIP INVITE from Twilio IP addresses (54.172.x.x, 54.244.x.x, etc.)
- "ACL" or "deny" messages
- "NOT_FOUND" or "USER_NOT_REGISTERED" errors
- Any errors related to `external` profile

### Step 2: Check if Twilio INVITE Reaches FusionPBX

```bash
# Enable SIP debugging
fs_cli -x "sofia loglevel all 9"

# Watch for SIP messages from Twilio IPs
tail -f /var/log/freeswitch/freeswitch.log | grep -E "54\.172\.|54\.244\.|177\.71\.|54\.252\.|54\.169\."
```

**If you see INVITE from Twilio IPs:** The issue is ACL or dialplan routing  
**If you DON'T see any INVITE:** The issue is firewall/network (Twilio can't reach FusionPBX)

### Step 3: Verify ACL Configuration

```bash
# Check if ACL is applied to external profile
fs_cli -x "sofia xmlstatus profile external" | grep -i "apply-inbound-acl"

# Should show:
# <apply-inbound-acl>Twilio-SIP</apply-inbound-acl>
```

**If it shows something else or is missing:**
- Go to FusionPBX GUI: `Advanced → SIP Profiles → external → Settings`
- Find `apply-inbound-acl` and set to `Twilio-SIP`
- Reload: `Status → SIP Status → external → Reload XML → Restart`

### Step 4: Test Direct SIP INVITE from External IP

```bash
# This simulates what Twilio does - sends INVITE to external profile
fs_cli -x "originate {origination_caller_id_number=Twilio,origination_caller_id_name=Twilio,context=public,domain_name=136.115.41.45}sofia/external/sip:2001@136.115.41.45 &echo"
```

**Note:** This uses `sofia/external/` instead of `user/` to simulate external SIP call.

## Most Likely Issues & Fixes

### Issue 1: ACL Not Applied to External Profile ❌

**Symptom:** No INVITE messages in logs, or ACL deny messages

**Fix:**
```bash
# Via Database (PostgreSQL)
sudo -u postgres psql fusionpbx

UPDATE v_sip_profile_settings sps
SET sip_profile_setting_value = 'Twilio-SIP',
    sip_profile_setting_enabled = true
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';

# If setting doesn't exist, INSERT it
INSERT INTO v_sip_profile_settings (
    sip_profile_setting_uuid,
    sip_profile_uuid,
    sip_profile_setting_name,
    sip_profile_setting_value,
    sip_profile_setting_enabled
) VALUES (
    gen_random_uuid(),
    (SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'external'),
    'apply-inbound-acl',
    'Twilio-SIP',
    true
);

\q

# Reload FreeSWITCH
fs_cli -x "reload"
fs_cli -x "sofia profile external restart"

# Verify
fs_cli -x "sofia xmlstatus profile external" | grep apply-inbound-acl
```

### Issue 2: Context Mismatch

**Problem:** External profile uses `public` context, but dialplan doesn't route `public` → extension 2001

**Check dialplan:**
```bash
# Check what dialplan exists for public context
fs_cli -x "xml_locate dialplan public extension 2001"

# Or check via FusionPBX GUI:
# Dialplan → Inbound Routes → Check routes for public context
```

**Fix:** Ensure there's a dialplan route in `public` context that routes to extension 2001:

```xml
<!-- In public context, add extension 2001 -->
<extension name="extension_2001">
  <condition field="destination_number" expression="^2001$">
    <action application="transfer" data="2001 XML default"/>
  </condition>
</extension>
```

### Issue 3: Firewall Blocking Twilio IPs

**Check firewall:**
```bash
# Check if firewall is blocking UDP 5060
sudo iptables -L -n | grep 5060

# Temporarily disable firewall for testing (NOT for production!)
sudo systemctl stop ufw
# OR
sudo iptables -F
```

**Permanent fix:** Configure firewall to allow Twilio IPs:
```bash
# Allow Twilio IP ranges
sudo ufw allow from 54.172.60.0/23 to any port 5060 proto udp
sudo ufw allow from 54.244.51.0/24 to any port 5060 proto udp
sudo ufw allow from 177.71.206.192/26 to any port 5060 proto udp
sudo ufw allow from 54.252.254.64/26 to any port 5060 proto udp
sudo ufw allow from 54.169.127.128/26 to any port 5060 proto udp
```

### Issue 4: External Profile Not Listening on Public IP

**Check:**
```bash
# Check what IP the external profile is bound to
fs_cli -x "sofia status profile external"

# Should show it's listening on 136.115.41.45:5060 (or 0.0.0.0:5060)
```

**If it's only listening on private IP (10.128.x.x):**
```bash
# Check external profile settings
fs_cli -x "sofia xmlstatus profile external" | grep -E "sip-ip|ext-sip-ip"

# Should show:
# <sip-ip>10.128.0.8</sip-ip> (binds to private)
# <ext-sip-ip>136.115.41.45</ext-sip-ip> (advertises public)
```

## Quick Test: Enable Verbose Logging and Try Transfer

```bash
# Terminal 1: Watch logs
tail -f /var/log/freeswitch/freeswitch.log

# Terminal 2: Enable verbose logging
fs_cli -x "console loglevel 9"
fs_cli -x "sofia loglevel all 9"

# Terminal 3: Now attempt a Twilio transfer
# (Make a call to your Twilio number and request transfer)

# Watch Terminal 1 for:
# - SIP INVITE from Twilio IP
# - ACL allow/deny messages
# - Dialplan routing
# - Extension lookup
```

## Expected Log Flow for Successful Transfer

When working correctly, you should see:

```
[INFO] sofia.c: Received SIP INVITE from 54.172.x.x:5060
[DEBUG] sofia.c: ACL check for 54.172.x.x: ALLOW (Twilio-SIP)
[INFO] sofia.c: Routing INVITE to extension 2001
[DEBUG] switch_core_state_machine.c: Dialing user/2001@136.115.41.45
[NOTICE] sofia.c: Channel [sofia/internal/2001@...] has been answered
[INFO] switch_channel.c: Callstate Change RINGING -> ACTIVE
```

## Most Likely Fix Based on Your Setup

Given that:
- ✅ Extension works internally
- ✅ External profile context is `public`
- ❌ Twilio transfers fail

**The most likely issue is:** `apply-inbound-acl` is not set to `Twilio-SIP` on the external profile.

**Run this to fix:**
```bash
sudo -u postgres psql fusionpbx -c "
UPDATE v_sip_profile_settings sps
SET sip_profile_setting_value = 'Twilio-SIP',
    sip_profile_setting_enabled = true
FROM v_sip_profiles sp
WHERE sps.sip_profile_uuid = sp.sip_profile_uuid
AND sp.sip_profile_name = 'external'
AND sps.sip_profile_setting_name = 'apply-inbound-acl';
"

fs_cli -x "reload"
fs_cli -x "sofia profile external restart"
```

Then test a Twilio transfer again!


# FUSIONPBX_WSS_PROFILE_SUCCESS

# FusionPBX WSS Profile - Successfully Configured! ✅

## Status

The WebRTC WebSocket Secure (wss) SIP profile is now **RUNNING** on your FusionPBX server!

**Profile Details:**
- **WSS Port:** `7443` (WebSocket Secure)
- **TLS Port:** `5061` (SIP over TLS)
- **Domain:** `136.115.41.45`
- **Status:** RUNNING ✅

## What Fixed It

The key fix was adding **TLS certificate configuration parameters** to the `wss.xml` file:

```xml
<param name="tls-cert-dir" value="$${base_dir}/conf/tls"/>
<param name="tls-cert-file" value="$${base_dir}/conf/tls/wss.pem"/>
<param name="tls-key-file" value="$${base_dir}/conf/tls/wss.pem"/>
```

Without these TLS certificate paths, FreeSWITCH couldn't load the WSS profile properly.

## Verification

### Check Profile Status

```bash
# Check if wss profile is running
fs_cli -x "sofia status profile wss"

# Check all profiles
fs_cli -x "sofia status"
```

**Expected output:**
```
wss profile on port 7443 - RUNNING (WSS)
wss profile on port 5061 - RUNNING (TLS)
```

### Check Profile Details

```bash
# Get detailed wss profile information
fs_cli -x "sofia xmlstatus profile wss" | head -30

# Check TLS certificate status
fs_cli -x "sofia xmlstatus profile wss" | grep -i "tls\|cert"
```

### Test Port Accessibility

```bash
# Check if ports are listening
sudo netstat -tlnp | grep -E "7443|5061"

# Or using ss
sudo ss -tlnp | grep -E "7443|5061"
```

**Expected output:**
```
tcp  0  0  0.0.0.0:7443  0.0.0.0:*  LISTEN  freeswitch
tcp  0  0  0.0.0.0:5061  0.0.0.0:*  LISTEN  freeswitch
```

## Next Steps: Configure WebRTC Extensions

Now that the WSS profile is running, you need to configure extensions to use WebRTC:

### Step 1: Verify Extension Exists and is Enabled

**Important:** Extensions don't need to be explicitly assigned to the `wss` profile. WebRTC clients connect to the WSS profile directly using their extension credentials. The extension just needs to exist and be enabled.

For extensions that will use WebRTC (like extension 2001, 2002, etc.):

1. **Login to FusionPBX:** `https://136.115.41.45`
2. **Navigate to:** `Accounts → Extensions`
3. **Click on the extension** (e.g., 2001)
4. **Verify the extension is enabled and configured:**
   - Extension number is set (e.g., `2001`)
   - Password is set (needed for SIP authentication)
   - User is assigned to the extension
   - **Save** if you made any changes

**Note:** Extensions can register to **any** SIP profile (internal, external, or wss) as long as:
- The extension credentials are correct
- The extension exists in the directory
- The client connects to the correct profile/port

WebRTC clients automatically use the `wss` profile when connecting via `wss://domain:7443`.

### Step 2: Update WebRTC Client Configuration

Update your WebRTC client code to use the WSS profile:

**Example Configuration:**
```javascript
const sipConfig = {
    domain: '136.115.41.45',
    wss_port: 7443,        // WSS port
    transport: 'wss',      // Use WSS
    // ... other settings
};
```

**URL Format:**
```
wss://136.115.41.45:7443
```

### Step 3: Configure Firewall

Ensure ports are open in your firewall:

```bash
# Open WSS port
sudo ufw allow 7443/tcp

# Open TLS port (if needed)
sudo ufw allow 5061/tcp

# Verify
sudo ufw status | grep -E "7443|5061"
```

### Step 4: Test WebRTC Connection

Test with a WebRTC client:

1. **Use a WebRTC SIP client** (like SIP.js, JsSIP, or your custom client)
2. **Connect to:** `wss://136.115.41.45:7443`
3. **Register with extension:** e.g., `2001@136.115.41.45`
4. **Make a test call** to another extension

### Step 5: Test Direct Transfer from WebRTC to FusionPBX

Now you can test direct transfer from your WebRTC voice assistant to FusionPBX extensions:

**In your WebRTC code:**
```javascript
// Transfer to FusionPBX extension
socketio.emit('transfer_to_extension', {
    extension: '2001',
    domain: '136.115.41.45',
    transport: 'wss',
    wss_port: 7443
});
```

## Troubleshooting

### If Profile Stops Running

```bash
# Restart the profile
fs_cli -x "sofia profile wss restart"

# Check status
fs_cli -x "sofia status profile wss"

# Check logs
tail -50 /var/log/freeswitch/freeswitch.log | grep -i wss
```

### If WebRTC Client Can't Connect

1. **Check firewall:** Ensure port 7443 is open
2. **Check TLS certificate:** Verify `wss.pem` exists and is valid
3. **Check logs:** Look for connection errors in FreeSWITCH logs
4. **Verify domain:** Ensure client uses correct domain (`136.115.41.45`)

### Check WebRTC Registration

```bash
# Check if WebRTC clients are registered
fs_cli -x "sofia status profile wss reg"

# Should show registered endpoints if any WebRTC clients are connected
```

## Database Configuration Summary

Your wss profile has:
- ✅ **Profile exists:** `v_sip_profiles` table
- ✅ **18 settings configured:** `v_sip_profile_settings` table
- ✅ **Profile enabled:** `sip_profile_enabled = true`
- ✅ **XML file exists:** `/etc/freeswitch/sip_profiles/wss.xml`
- ✅ **TLS certificates configured:** `/etc/freeswitch/tls/wss.pem`

## Important Notes

1. **TLS Certificate:** The `wss.pem` certificate is self-signed. For production, consider using a proper SSL certificate from a CA.

2. **Profile Persistence:** The XML file is manually created. If FusionPBX regenerates profiles from the database, you may need to ensure the database settings are complete.

3. **Both Ports Running:** It's normal to see the wss profile on both port 7443 (WSS) and 5061 (TLS). Both are functional.

## Success Checklist

- ✅ WSS profile running on port 7443
- ✅ TLS profile running on port 5061
- ✅ TLS certificates configured
- ✅ Database settings complete (18 settings)
- ✅ Profile enabled in database
- ✅ XML file exists and is valid
- ✅ Firewall ports configured
- ⏭️ WebRTC client configuration (next step)
- ⏭️ Extension WebRTC setup (next step)
- ⏭️ Test WebRTC connections (next step)

---

**Congratulations! Your FusionPBX WebRTC profile is now operational!** 🎉

You can now configure WebRTC clients to connect directly to FusionPBX and transfer calls from your WebRTC voice assistant to FusionPBX extensions.


# FUSIONPBX_WSS_PROFILE_TROUBLESHOOTING

# FusionPBX WSS Profile Troubleshooting Guide

## Error: "No Such Profile 'wss'"

If you see `[WARNING] sofia.c:6383 No Such Profile 'wss'` even though:
- The profile exists in `v_sip_profiles` table
- The file `/etc/freeswitch/sip_profiles/wss.xml` exists

**The problem:** FreeSWITCH is not loading the profile because:
1. FreeSWITCH reads profiles from a different directory than `/etc/freeswitch/sip_profiles/`
2. The profile settings are missing from the database (`v_sip_profile_settings` table)
3. FreeSWITCH generates profile XML from the database, not from standalone files

**Solution:** Configure the profile via FusionPBX database, not just the file.

### Step 1: Find Where FreeSWITCH Actually Loads Profiles

```bash
# Get FreeSWITCH base directory
fs_cli -x "global_getvar base_dir"

# Check where profiles are actually loaded from
fs_cli -x "global_getvar conf_dir"

# List what profiles FreeSWITCH actually sees
fs_cli -x "sofia status"

# Check internal profile location for reference
ls -la /usr/local/freeswitch/conf/sip_profiles/internal.xml 2>/dev/null
ls -la /opt/freeswitch/conf/sip_profiles/internal.xml 2>/dev/null
ls -la $(fs_cli -x "global_getvar conf_dir" | tail -1)/sip_profiles/ 2>/dev/null
```

### Step 2: Check if Profile Settings Exist in Database

The profile may exist in `v_sip_profiles` but have no settings:

```bash
# Get the profile UUID
PROFILE_UUID=$(sudo -u postgres psql fusionpbx -t -c "SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'wss';" | xargs)
echo "Profile UUID: $PROFILE_UUID"

# Check if any settings exist
sudo -u postgres psql fusionpbx -c "SELECT COUNT(*) as setting_count FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID';"

# List all settings (should show multiple rows)
sudo -u postgres psql fusionpbx -c "SELECT sip_profile_setting_name, sip_profile_setting_value FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' ORDER BY sip_profile_setting_name;"
```

### Step 3: Add Missing Profile Settings to Database

If no settings exist, you need to add them. FusionPBX generates the XML from the database:

```bash
# Get profile UUID
PROFILE_UUID=$(sudo -u postgres psql fusionpbx -t -c "SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'wss';" | xargs)

# Insert all required settings at once
sudo -u postgres psql fusionpbx << EOF
-- Core settings
INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
VALUES 
  (gen_random_uuid(), '$PROFILE_UUID', 'name', 'wss', 'true')
  ON CONFLICT DO NOTHING;

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'sip-ip', '0.0.0.0', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'sip-ip');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'sip-port', '7443', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'sip-port');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'tls', 'true', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'tls');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'tls-bind-params', 'transport=wss', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'tls-bind-params');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'ext-sip-ip', '136.115.41.45', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'ext-sip-ip');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'ext-rtp-ip', '136.115.41.45', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'ext-rtp-ip');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'domain', '136.115.41.45', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'domain');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'codec-prefs', 'G722,PCMU,PCMA', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'codec-prefs');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'rtp-ip', '0.0.0.0', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'rtp-ip');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'rtp-min-port', '16384', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'rtp-min-port');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'rtp-max-port', '32768', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'rtp-max-port');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'local-network-acl', 'localnet.auto', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'local-network-acl');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'apply-nat-acl', 'nat.auto', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'apply-nat-acl');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'apply-inbound-acl', 'domains', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'apply-inbound-acl');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'apply-register-acl', 'domains', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'apply-register-acl');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'bypass-media', 'false', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'bypass-media');

INSERT INTO v_sip_profile_settings (sip_profile_setting_uuid, sip_profile_uuid, sip_profile_setting_name, sip_profile_setting_value, sip_profile_setting_enabled)
SELECT gen_random_uuid(), '$PROFILE_UUID', 'media-bypass', 'false', 'true'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_name = 'media-bypass');
EOF

echo "✅ Profile settings added to database"
```

### Step 4: Regenerate XML from Database

After adding settings, force FusionPBX to regenerate the XML:

```bash
# Reload XML (this should regenerate profiles from database)
fs_cli -x "reloadxml"

# Wait a moment
sleep 2

# Check if profile is now visible
fs_cli -x "sofia status" | grep -i wss

# Try to start
fs_cli -x "sofia profile wss start"
fs_cli -x "sofia status profile wss"
```

### Step 5: Verify Profile Location

Check where the profile XML was actually generated:

```bash
# Find where FreeSWITCH actually loads profiles from
CONF_DIR=$(fs_cli -x "global_getvar conf_dir" | tail -1)
echo "FreeSWITCH conf directory: $CONF_DIR"

# Check if wss.xml was generated there
ls -la "$CONF_DIR/sip_profiles/wss.xml"

# If it exists, check its contents
cat "$CONF_DIR/sip_profiles/wss.xml"
```

---

## Still Failing After Adding Database Settings?

If you've added all settings to the database but still get "Invalid Profile!" or "Failure starting wss", follow these diagnostic steps:

### Diagnostic Step 1: Check Where FreeSWITCH Actually Loads Profiles

```bash
# Get FreeSWITCH base and config directories
fs_cli -x "global_getvar base_dir"
fs_cli -x "global_getvar conf_dir"

# Check common locations
ls -la /etc/freeswitch/sip_profiles/wss.xml 2>/dev/null
ls -la /usr/local/freeswitch/conf/sip_profiles/wss.xml 2>/dev/null
ls -la /opt/freeswitch/conf/sip_profiles/wss.xml 2>/dev/null
ls -la $(fs_cli -x "global_getvar conf_dir" | tail -1)/sip_profiles/wss.xml 2>/dev/null
```

### Diagnostic Step 2: Check if FusionPBX Generated the XML

FusionPBX may need explicit triggering to generate the XML from the database:

```bash
# Check if FusionPBX has a PHP script to regenerate XML
find /var/www/fusionpbx -name "*.php" | xargs grep -l "sip_profiles\|sofia.*xml" | head -5

# Or check if there's a FusionPBX CLI command
fwconsole reload 2>/dev/null || echo "fwconsole not available"

# Check if there's a specific reload command
fs_cli -x "reload mod_sofia"
```

### Diagnostic Step 3: Check the Generated XML File

If the XML file exists, check if it's valid:

```bash
# Find the XML file (try all locations)
XML_FILE=$(find /etc/freeswitch /usr/local/freeswitch/conf /opt/freeswitch/conf 2>/dev/null | grep "sip_profiles/wss.xml" | head -1)

if [ -n "$XML_FILE" ]; then
    echo "Found XML file at: $XML_FILE"
    cat "$XML_FILE"
    
    # Check if it's valid XML
    xmllint --noout "$XML_FILE" 2>&1 || echo "⚠️ XML validation failed"
else
    echo "❌ XML file not found - FusionPBX may not have generated it"
fi
```

### Diagnostic Step 4: Get Detailed Error from Logs

```bash
# Enable maximum logging
fs_cli -x "console loglevel debug"
fs_cli -x "sofia loglevel all 9"

# Try to start the profile
fs_cli -x "sofia profile wss start"

# Immediately check logs for detailed error
tail -100 /var/log/freeswitch/freeswitch.log | grep -A 10 -B 10 -iE "wss|error|fail|invalid" | tail -30

# Check specifically for XML parsing errors
tail -200 /var/log/freeswitch/freeswitch.log | grep -iE "xml|parse|syntax" | tail -20
```

### Diagnostic Step 4A: Verify FreeSWITCH Sees the Profile During reloadxml

Even if the XML file exists, FreeSWITCH might not be loading it. Check if it's being parsed:

```bash
# Watch the log file in real-time while reloading
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "wss|profile|sip_profiles" &
TAIL_PID=$!

# Reload XML
fs_cli -x "reloadxml"

# Wait a moment
sleep 3

# Kill the tail process
kill $TAIL_PID 2>/dev/null

# Check what profiles FreeSWITCH actually sees
fs_cli -x "sofia status" | head -20
```

### Diagnostic Step 4B: Check sofia.conf.xml Configuration

FusionPBX may use `sofia.conf.xml` to control which profiles are loaded. Check if wss needs to be explicitly included:

```bash
# Find sofia.conf.xml
SOFIA_CONF=$(find /etc/freeswitch -name "sofia.conf.xml" 2>/dev/null | head -1)

if [ -n "$SOFIA_CONF" ]; then
    echo "Found sofia.conf.xml at: $SOFIA_CONF"
    echo "--- Contents ---"
    cat "$SOFIA_CONF"
    
    # Check if profiles are explicitly listed
    echo ""
    echo "--- Profile references ---"
    grep -iE "profile|external|internal|wss" "$SOFIA_CONF"
else
    echo "Could not find sofia.conf.xml in /etc/freeswitch"
    
    # Check autoload_configs directory
    ls -la /etc/freeswitch/autoload_configs/ | grep sofia
fi
```

### Diagnostic Step 4C: Check How FusionPBX Generates Profile XML

FusionPBX might use a PHP script to generate profiles. Check if it's generating them correctly:

```bash
# Find FusionPBX XML generation scripts
find /var/www/fusionpbx -name "*.php" 2>/dev/null | xargs grep -l "sip_profiles\|sofia.*profile" 2>/dev/null | head -5

# Check if there's a specific include mechanism
grep -r "wss\|external\|internal" /etc/freeswitch/autoload_configs/*.xml 2>/dev/null | head -10
```

### Diagnostic Step 4D: Verify XML is Actually Being Read

Check if FreeSWITCH is attempting to read the file:

```bash
# Use strace to see if FreeSWITCH opens the file (if available)
if command -v strace >/dev/null 2>&1; then
    FS_PID=$(pgrep freeswitch | head -1)
    if [ -n "$FS_PID" ]; then
        echo "Watching FreeSWITCH process $FS_PID for file operations..."
        timeout 5 strace -p $FS_PID -e open,openat 2>&1 | grep -i "wss.xml\|sip_profiles" || echo "No file operations detected"
    fi
else
    echo "strace not available"
fi

# Alternative: Check file access times
echo "File access time before reload:"
stat /etc/freeswitch/sip_profiles/wss.xml | grep Access

# Reload
fs_cli -x "reloadxml"

sleep 2

echo "File access time after reload:"
stat /etc/freeswitch/sip_profiles/wss.xml | grep Access
```

---

### Diagnostic Step 5: Check if Profile is Listed in sofia.conf.xml

FreeSWITCH might need the profile to be explicitly listed in `sofia.conf.xml`:

```bash
# Find sofia.conf.xml
SOFIA_CONF=$(find /etc/freeswitch /usr/local/freeswitch/conf /opt/freeswitch/conf 2>/dev/null | grep "autoload_configs/sofia.conf.xml" | head -1)

if [ -n "$SOFIA_CONF" ]; then
    echo "Found sofia.conf.xml at: $SOFIA_CONF"
    cat "$SOFIA_CONF" | grep -A 5 -B 5 "wss\|external\|internal"
else
    echo "Could not find sofia.conf.xml"
fi
```

### Diagnostic Step 6: Manually Generate XML from Database

If FusionPBX isn't generating the XML automatically, you can manually create it:

```bash
# Get all settings from database
PROFILE_UUID=$(sudo -u postgres psql fusionpbx -t -c "SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'wss';" | xargs)

# Generate XML file from database settings
sudo tee /etc/freeswitch/sip_profiles/wss.xml > /dev/null << 'XML_EOF'
<profile name="wss">
  <settings>
XML_EOF

# Add each setting from database
sudo -u postgres psql fusionpbx -t -c "SELECT '<param name=\"' || sip_profile_setting_name || '\" value=\"' || sip_profile_setting_value || '\"/>' FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_enabled = 'true' ORDER BY sip_profile_setting_name;" | sed 's/^/    /' >> /etc/freeswitch/sip_profiles/wss.xml

# Close the XML
sudo tee -a /etc/freeswitch/sip_profiles/wss.xml > /dev/null << 'XML_EOF'
  </settings>
</profile>
XML_EOF

# Fix permissions
FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
FS_USER=${FS_USER:-www-data}
sudo chown $FS_USER:$FS_USER /etc/freeswitch/sip_profiles/wss.xml
sudo chmod 644 /etc/freeswitch/sip_profiles/wss.xml

# Verify XML
cat /etc/freeswitch/sip_profiles/wss.xml
xmllint --noout /etc/freeswitch/sip_profiles/wss.xml && echo "✅ XML is valid"

# Reload and try again
fs_cli -x "reloadxml"
sleep 2
fs_cli -x "sofia profile wss start"
fs_cli -x "sofia status profile wss"
```

### Diagnostic Step 7: Check Profile is Enabled in Database

```bash
# Verify profile is enabled
sudo -u postgres psql fusionpbx -c "SELECT sip_profile_name, sip_profile_enabled FROM v_sip_profiles WHERE sip_profile_name = 'wss';"

# If not enabled, enable it
sudo -u postgres psql fusionpbx -c "UPDATE v_sip_profiles SET sip_profile_enabled = 'true' WHERE sip_profile_name = 'wss';"
```

### Diagnostic Step 8: Try via FusionPBX GUI

Sometimes the GUI trigger is needed for FusionPBX to recognize the profile:

1. **Login to FusionPBX:** `https://136.115.41.45`
2. **Navigate to:** `Advanced → SIP Profiles`
3. **Look for "wss" profile** - if it's there, click on it
4. **If it's NOT there**, the profile may not be fully recognized by FusionPBX
5. **Try clicking "Add" or "+"** to create a new profile named "wss"
6. **Or use the GUI to edit settings** - this might trigger XML regeneration
7. **Go to:** `Status → SIP Status`
8. **Find "wss" profile and click "Reload XML" and "Restart"**

---

# Troubleshooting: wss Profile Fails to Start

## Your Current Issue

- ✅ `wss.xml` file exists at `/etc/freeswitch/sip_profiles/wss.xml`
- ❌ Profile fails to start: "Failure starting wss"
- ❌ `chown freeswitch:freeswitch` fails (user doesn't exist)
- ❌ File not found in standard FreeSWITCH locations

## Diagnostic Steps

### Step 1: Find the Correct FreeSWITCH User

```bash
# Check what user FreeSWITCH runs as
ps aux | grep freeswitch | grep -v grep

# Check systemd service file
systemctl status freeswitch
cat /etc/systemd/system/freeswitch.service | grep User

# OR check init script
cat /etc/init.d/freeswitch | grep USER

# Common FreeSWITCH users:
# - www-data (Debian/Ubuntu with FusionPBX)
# - freeswitch (if installed from source)
# - daemon (some installations)
```

### Step 2: Find the Correct FreeSWITCH Configuration Directory

```bash
# Check where FreeSWITCH is actually installed
which freeswitch
whereis freeswitch

# Check FreeSWITCH CLI for config path
fs_cli -x "global_getvar base_dir"
fs_cli -x "global_getvar conf_dir"

# Check running process for config location
ps aux | grep freeswitch | grep -o '\-conf [^ ]*'

# Common locations:
# - /usr/local/freeswitch/
# - /opt/freeswitch/
# - /var/lib/freeswitch/
# - /etc/freeswitch/ (FusionPBX default)
```

### Step 3: Check FreeSWITCH Logs for Error Details

```bash
# Check recent errors
tail -100 /var/log/freeswitch/freeswitch.log | grep -i wss
tail -100 /var/log/freeswitch/freeswitch.log | grep -i error
tail -100 /var/log/freeswitch/freeswitch.log | grep -i 7443

# Check for TLS certificate errors
tail -100 /var/log/freeswitch/freeswitch.log | grep -i tls
tail -100 /var/log/freeswitch/freeswitch.log | grep -i certificate

# Enable debug logging and try again
fs_cli -x "console loglevel debug"
fs_cli -x "sofia loglevel all 9"
fs_cli -x "sofia profile wss start"
tail -50 /var/log/freeswitch/freeswitch.log
```

### Step 4: Check if wss Profile is in FusionPBX Database

```bash
# Complete the database query (if it was interrupted)
sudo -u postgres psql fusionpbx -c "SELECT * FROM v_sip_profiles WHERE sip_profile_name = 'wss';"

# If it doesn't exist, create it:
sudo -u postgres psql fusionpbx << EOF
INSERT INTO v_sip_profiles (sip_profile_uuid, sip_profile_name, sip_profile_enabled, sip_profile_description)
SELECT gen_random_uuid(), 'wss', 'true', 'WebRTC WebSocket Secure Profile'
WHERE NOT EXISTS (SELECT 1 FROM v_sip_profiles WHERE sip_profile_name = 'wss');
EOF
```

### Step 5: Verify File Location and Permissions

Since FusionPBX uses `/etc/freeswitch/` as the config directory, that's likely correct. But we need to fix permissions:

```bash
# Find the correct user (most likely www-data for FusionPBX)
FS_USER=$(ps aux | grep freeswitch | grep -v grep | awk '{print $1}' | head -1)
echo "FreeSWITCH runs as user: $FS_USER"

# Fix ownership
sudo chown $FS_USER:$FS_USER /etc/freeswitch/sip_profiles/wss.xml
sudo chmod 644 /etc/freeswitch/sip_profiles/wss.xml

# Verify
ls -la /etc/freeswitch/sip_profiles/wss.xml
```

### Step 6: Check TLS Certificate Configuration

The wss profile requires a TLS certificate. Check if it's configured:

```bash
# Check if TLS certificate exists
ls -la /etc/freeswitch/tls/*.pem
ls -la /etc/freeswitch/tls/wss.*

# Check FreeSWITCH TLS directory
find /etc/freeswitch -name "*.pem" -o -name "*.crt" -o -name "*.key" 2>/dev/null

# Check what certificate FreeSWITCH is using
fs_cli -x "sofia xmlstatus profile internal" | grep -i cert
```

### Step 7: Check Port 7443 Availability

```bash
# Check if port 7443 is already in use
sudo lsof -i :7443
sudo netstat -tlnp | grep 7443
sudo ss -tlnp | grep 7443

# If something else is using it, identify and stop it
```

## Solution Steps

### Fix 1: Correct File Permissions (Most Likely Issue)

```bash
# Determine the correct user
FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
FS_GROUP=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)

# If that doesn't work, try common ones:
# For FusionPBX on Debian/Ubuntu, it's usually www-data
FS_USER="www-data"
FS_GROUP="www-data"

# Fix ownership
sudo chown $FS_USER:$FS_GROUP /etc/freeswitch/sip_profiles/wss.xml
sudo chmod 644 /etc/freeswitch/sip_profiles/wss.xml

# Verify
ls -la /etc/freeswitch/sip_profiles/wss.xml
```

### Fix 2: Add TLS Certificate Configuration

The wss profile needs TLS certificate settings. Add them to the wss.xml file:

```bash
# Backup the current file
sudo cp /etc/freeswitch/sip_profiles/wss.xml /etc/freeswitch/sip_profiles/wss.xml.backup

# Check if certificate exists
if [ -f /etc/freeswitch/tls/wss.pem ]; then
    CERT_FILE="/etc/freeswitch/tls/wss.pem"
elif [ -f /etc/freeswitch/tls/cert.pem ]; then
    CERT_FILE="/etc/freeswitch/tls/cert.pem"
elif [ -f /etc/freeswitch/tls/tls.pem ]; then
    CERT_FILE="/etc/freeswitch/tls/tls.pem"
else
    echo "Certificate not found. Need to create one."
    CERT_FILE="/etc/freeswitch/tls/wss.pem"
fi

echo "Using certificate: $CERT_FILE"

# Generate certificate if it doesn't exist
if [ ! -f "$CERT_FILE" ]; then
    sudo mkdir -p /etc/freeswitch/tls
    cd /etc/freeswitch/tls
    sudo openssl req -x509 -newkey rsa:4096 -keyout wss.pem -out wss.pem -days 365 -nodes -subj "/CN=136.115.41.45"
    sudo chown $FS_USER:$FS_GROUP wss.pem
    sudo chmod 600 wss.pem
fi

# Update wss.xml to include TLS certificate settings
sudo tee /etc/freeswitch/sip_profiles/wss.xml > /dev/null << 'EOF'
<profile name="wss">
  <settings>
    <param name="name" value="wss"/>
    <param name="sip-ip" value="0.0.0.0"/>
    <param name="sip-port" value="7443"/>
    <param name="tls" value="true"/>
    <param name="tls-bind-params" value="transport=wss"/>
    <param name="tls-cert-dir" value="$${base_dir}/conf/tls"/>
    <param name="tls-cert-file" value="$${base_dir}/conf/tls/wss.pem"/>
    <param name="tls-key-file" value="$${base_dir}/conf/tls/wss.pem"/>
    <param name="tls-ca-file" value="$${base_dir}/conf/tls/cafile.pem"/>
    <param name="ext-sip-ip" value="136.115.41.45"/>
    <param name="ext-rtp-ip" value="136.115.41.45"/>
    <param name="domain" value="136.115.41.45"/>
    <param name="codec-prefs" value="G722,PCMU,PCMA"/>
    <param name="rtp-ip" value="0.0.0.0"/>
    <param name="rtp-min-port" value="16384"/>
    <param name="rtp-max-port" value="32768"/>
    <param name="local-network-acl" value="localnet.auto"/>
    <param name="apply-nat-acl" value="nat.auto"/>
    <param name="apply-inbound-acl" value="domains"/>
    <param name="apply-register-acl" value="domains"/>
    <param name="bypass-media" value="false"/>
    <param name="media-bypass" value="false"/>
  </settings>
</profile>
EOF

# Fix permissions again
sudo chown $FS_USER:$FS_GROUP /etc/freeswitch/sip_profiles/wss.xml
```

### Fix 3: Ensure Profile Exists in Database

```bash
# Check if profile exists in database
sudo -u postgres psql fusionpbx -c "SELECT sip_profile_name, sip_profile_enabled FROM v_sip_profiles WHERE sip_profile_name = 'wss';"

# If it doesn't exist, create it
sudo -u postgres psql fusionpbx << 'SQL'
INSERT INTO v_sip_profiles (sip_profile_uuid, sip_profile_name, sip_profile_enabled, sip_profile_description)
SELECT gen_random_uuid(), 'wss', 'true', 'WebRTC Profile' WHERE NOT EXISTS (SELECT 1 FROM v_sip_profiles WHERE sip_profile_name = 'wss');
SQL

# Verify it was created
sudo -u postgres psql fusionpbx -c "SELECT sip_profile_name, sip_profile_enabled FROM v_sip_profiles WHERE sip_profile_name = 'wss';"
```

### Fix 4: Reload and Start Profile

```bash
# Reload XML configuration
fs_cli -x "reloadxml"

# Try starting the profile
fs_cli -x "sofia profile wss start"

# Check status
fs_cli -x "sofia status profile wss"

# Check for errors in logs
tail -50 /var/log/freeswitch/freeswitch.log | grep -i wss
```

## Quick Diagnostic Script

Run this complete diagnostic script:

```bash
#!/bin/bash
echo "=== FreeSWITCH wss Profile Diagnostic ==="
echo ""

echo "1. FreeSWITCH Process Information:"
ps aux | grep '[f]reeswitch' | head -3
echo ""

echo "2. FreeSWITCH User:"
FS_USER=$(ps aux | grep '[f]reeswitch' | grep -v grep | awk '{print $1}' | head -1)
echo "   User: $FS_USER"
echo ""

echo "3. Configuration Directory:"
fs_cli -x "global_getvar base_dir" 2>/dev/null || echo "   Cannot determine (fs_cli may not be accessible)"
fs_cli -x "global_getvar conf_dir" 2>/dev/null || echo "   Cannot determine"
echo ""

echo "4. File Existence:"
ls -la /etc/freeswitch/sip_profiles/wss.xml 2>/dev/null && echo "   ✅ wss.xml exists" || echo "   ❌ wss.xml not found"
echo ""

echo "5. File Permissions:"
ls -la /etc/freeswitch/sip_profiles/wss.xml | awk '{print "   Owner: "$3":"$4" Permissions: "$1}'
echo ""

echo "6. TLS Certificate Check:"
if [ -f /etc/freeswitch/tls/wss.pem ]; then
    echo "   ✅ wss.pem exists"
    ls -la /etc/freeswitch/tls/wss.pem | awk '{print "   Permissions: "$1" Owner: "$3":"$4}'
else
    echo "   ❌ wss.pem not found"
    echo "   Checking for other certificates:"
    ls -la /etc/freeswitch/tls/*.pem 2>/dev/null || echo "   No .pem files found"
fi
echo ""

echo "7. Port 7443 Status:"
if lsof -i :7443 2>/dev/null | grep -q LISTEN; then
    echo "   ⚠️  Port 7443 is already in use:"
    lsof -i :7443
else
    echo "   ✅ Port 7443 is available"
fi
echo ""

echo "8. Profile Status:"
fs_cli -x "sofia status" 2>/dev/null | grep wss || echo "   wss profile not listed"
echo ""

echo "9. Recent Log Errors:"
tail -30 /var/log/freeswitch/freeswitch.log 2>/dev/null | grep -iE "wss|7443|error|failure" | tail -5 || echo "   No recent errors found"
echo ""

echo "10. Database Status:"
sudo -u postgres psql fusionpbx -t -c "SELECT sip_profile_name, sip_profile_enabled FROM v_sip_profiles WHERE sip_profile_name = 'wss';" 2>/dev/null || echo "   Cannot check database"
echo ""

echo "=== Diagnostic Complete ==="
```

Save this as `diagnose_wss.sh`, make it executable, and run it:
```bash
chmod +x diagnose_wss.sh
sudo ./diagnose_wss.sh
```

## Most Common Issues and Quick Fixes

### Issue 1: Wrong File Ownership

```bash
# Quick fix - set to www-data (common for FusionPBX)
sudo chown www-data:www-data /etc/freeswitch/sip_profiles/wss.xml
sudo chmod 644 /etc/freeswitch/sip_profiles/wss.xml
```

### Issue 2: Missing TLS Certificate

```bash
# Generate certificate
sudo mkdir -p /etc/freeswitch/tls
cd /etc/freeswitch/tls
FS_USER=$(ps aux | grep '[f]reeswitch' | grep -v grep | awk '{print $1}' | head -1)
FS_USER=${FS_USER:-www-data}
sudo openssl req -x509 -newkey rsa:4096 -keyout wss.pem -out wss.pem -days 365 -nodes -subj "/CN=136.115.41.45"
sudo chown $FS_USER:$FS_USER wss.pem
sudo chmod 600 wss.pem
```

### Issue 3: Profile Not in Database

```bash
# Add to database
sudo -u postgres psql fusionpbx -c "INSERT INTO v_sip_profiles (sip_profile_uuid, sip_profile_name, sip_profile_enabled, sip_profile_description) SELECT gen_random_uuid(), 'wss', 'true', 'WebRTC Profile' WHERE NOT EXISTS (SELECT 1 FROM v_sip_profiles WHERE sip_profile_name = 'wss');"
fs_cli -x "reloadxml"
```

### Issue 4: Port Conflict

```bash
# Find what's using port 7443
sudo lsof -i :7443
# Kill if needed (replace PID with actual process ID)
# sudo kill -9 <PID>
```

## Expected Resolution Steps

1. **Identify the correct FreeSWITCH user** (likely `www-data`)
2. **Fix file permissions** with the correct user
3. **Generate TLS certificate** if missing
4. **Add TLS certificate settings** to wss.xml
5. **Ensure profile exists in database**
6. **Reload and start the profile**

Run the diagnostic script first to identify the exact issue, then apply the appropriate fix.

---

## Profile Exists in Database But Still Fails to Start

If the wss profile exists in `v_sip_profiles` table but still fails to start, follow these steps:

### Step 1: Check the Actual Error from Logs

```bash
# Enable debug logging and try to start
fs_cli -x "console loglevel debug"
fs_cli -x "sofia loglevel all 9"
fs_cli -x "sofia profile wss start"

# Immediately check logs for the error
tail -100 /var/log/freeswitch/freeswitch.log | grep -iE "wss|7443|error|failure|certificate|tls" | tail -20
```

### Step 2: Fix File Permissions

```bash
# Find the correct FreeSWITCH user
FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
echo "FreeSWITCH user: $FS_USER"

# If empty or root, use www-data (common for FusionPBX)
if [ -z "$FS_USER" ] || [ "$FS_USER" = "root" ]; then
    FS_USER="www-data"
fi

# Fix ownership
sudo chown $FS_USER:$FS_USER /etc/freeswitch/sip_profiles/wss.xml
sudo chmod 644 /etc/freeswitch/sip_profiles/wss.xml

# Verify
ls -la /etc/freeswitch/sip_profiles/wss.xml
```

### Step 3: Check and Generate TLS Certificate

```bash
# Check if TLS certificate exists
ls -la /etc/freeswitch/tls/*.pem 2>/dev/null

# Check what certificates FreeSWITCH uses
fs_cli -x "sofia xmlstatus profile internal" | grep -i cert

# Generate wss.pem if it doesn't exist
if [ ! -f /etc/freeswitch/tls/wss.pem ]; then
    sudo mkdir -p /etc/freeswitch/tls
    cd /etc/freeswitch/tls
    
    FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
    FS_USER=${FS_USER:-www-data}
    
    sudo openssl req -x509 -newkey rsa:4096 -keyout wss.pem -out wss.pem -days 365 -nodes -subj "/CN=136.115.41.45"
    sudo chown $FS_USER:$FS_USER wss.pem
    sudo chmod 600 wss.pem
    
    echo "✅ Certificate created: /etc/freeswitch/tls/wss.pem"
else
    echo "✅ Certificate exists: /etc/freeswitch/tls/wss.pem"
fi
```

### Step 4: Update wss.xml with TLS Certificate Paths

The wss.xml file may need explicit TLS certificate paths. Update it:

```bash
# Backup current file
sudo cp /etc/freeswitch/sip_profiles/wss.xml /etc/freeswitch/sip_profiles/wss.xml.backup

# Find FreeSWITCH base directory
FS_BASE=$(fs_cli -x "global_getvar base_dir" 2>/dev/null)
FS_BASE=${FS_BASE:-/usr/local/freeswitch}

echo "FreeSWITCH base directory: $FS_BASE"

# Update wss.xml with complete configuration including TLS paths
sudo tee /etc/freeswitch/sip_profiles/wss.xml > /dev/null << 'EOF'
<profile name="wss">
  <settings>
    <param name="name" value="wss"/>
    <param name="sip-ip" value="0.0.0.0"/>
    <param name="sip-port" value="7443"/>
    <param name="tls" value="true"/>
    <param name="tls-bind-params" value="transport=wss"/>
    <param name="ext-sip-ip" value="136.115.41.45"/>
    <param name="ext-rtp-ip" value="136.115.41.45"/>
    <param name="domain" value="136.115.41.45"/>
    <param name="codec-prefs" value="G722,PCMU,PCMA"/>
    <param name="rtp-ip" value="0.0.0.0"/>
    <param name="rtp-min-port" value="16384"/>
    <param name="rtp-max-port" value="32768"/>
    <param name="local-network-acl" value="localnet.auto"/>
    <param name="apply-nat-acl" value="nat.auto"/>
    <param name="apply-inbound-acl" value="domains"/>
    <param name="apply-register-acl" value="domains"/>
    <param name="bypass-media" value="false"/>
    <param name="media-bypass" value="false"/>
  </settings>
</profile>
EOF

# Fix permissions again
FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
FS_USER=${FS_USER:-www-data}
sudo chown $FS_USER:$FS_USER /etc/freeswitch/sip_profiles/wss.xml
sudo chmod 644 /etc/freeswitch/sip_profiles/wss.xml
```

### Step 5: Reload XML and Start Profile

```bash
# Reload XML configuration
fs_cli -x "reloadxml"

# Wait a moment
sleep 2

# Try to start the profile
fs_cli -x "sofia profile wss start"

# Check status
fs_cli -x "sofia status profile wss"
```

### Step 6: If Still Failing, Check Detailed Error

```bash
# Get detailed error from logs
tail -200 /var/log/freeswitch/freeswitch.log | grep -A 5 -B 5 -iE "wss|7443" | tail -30

# Try with maximum logging
fs_cli -x "console loglevel debug"
fs_cli -x "sofia loglevel all 9"
fs_cli -x "reloadxml"
fs_cli -x "sofia profile wss start"
sleep 1
tail -50 /var/log/freeswitch/freeswitch.log | grep -iE "wss|error|fail"
```

### Step 7: Check Port Availability

```bash
# Check if port 7443 is available
sudo lsof -i :7443
sudo netstat -tlnp | grep 7443

# If something is using it, you'll need to stop it first
```

### Step 8: Alternative - Check if Profile is Enabled in Settings

Sometimes FusionPBX needs the profile settings to be configured even if the profile exists:

```bash
# Check if there are any settings for the wss profile
sudo -u postgres psql fusionpbx -c "SELECT sip_profile_setting_name, sip_profile_setting_value FROM v_sip_profile_settings WHERE sip_profile_uuid = (SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'wss');"
```

If no settings exist, you may need to add them via FusionPBX GUI or add them manually to the database.

---

## Complete Fix Script (Run All at Once)

If you want to run everything at once, use this script:

```bash
#!/bin/bash
echo "=== Fixing wss Profile ==="

# Step 1: Find FreeSWITCH user
FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
FS_USER=${FS_USER:-www-data}
echo "Using user: $FS_USER"

# Step 2: Fix file permissions
echo "Fixing file permissions..."
sudo chown $FS_USER:$FS_USER /etc/freeswitch/sip_profiles/wss.xml
sudo chmod 644 /etc/freeswitch/sip_profiles/wss.xml

# Step 3: Ensure TLS certificate exists
echo "Checking TLS certificate..."
if [ ! -f /etc/freeswitch/tls/wss.pem ]; then
    sudo mkdir -p /etc/freeswitch/tls
    cd /etc/freeswitch/tls
    sudo openssl req -x509 -newkey rsa:4096 -keyout wss.pem -out wss.pem -days 365 -nodes -subj "/CN=136.115.41.45"
    sudo chown $FS_USER:$FS_USER wss.pem
    sudo chmod 600 wss.pem
    echo "✅ Certificate created"
else
    echo "✅ Certificate exists"
fi

# Step 4: Reload and start
echo "Reloading XML..."
fs_cli -x "reloadxml"
sleep 2

echo "Starting wss profile..."
fs_cli -x "sofia profile wss start"
sleep 2

# Step 5: Check status
echo ""
echo "=== Status Check ==="
fs_cli -x "sofia status profile wss"

# Step 6: Check for errors
echo ""
echo "=== Recent Errors ==="
tail -30 /var/log/freeswitch/freeswitch.log | grep -iE "wss|7443|error" | tail -5

echo ""
echo "=== Fix Complete ==="
```

Save as `fix_wss.sh`, make executable, and run:
```bash
chmod +x fix_wss.sh
sudo ./fix_wss.sh
```

---

### Most Likely Fix: Ensure Database Settings Trigger XML Generation

Since FusionPBX generates profiles from the database, ensure all required settings exist and trigger regeneration:

```bash
# Verify all settings are in database
PROFILE_UUID=$(sudo -u postgres psql fusionpbx -t -c "SELECT sip_profile_uuid FROM v_sip_profiles WHERE sip_profile_name = 'wss';" | xargs)
sudo -u postgres psql fusionpbx -c "SELECT sip_profile_setting_name, sip_profile_setting_value FROM v_sip_profile_settings WHERE sip_profile_uuid = '$PROFILE_UUID' AND sip_profile_setting_enabled = 'true' ORDER BY sip_profile_setting_name;"

# Check if profile is enabled
sudo -u postgres psql fusionpbX -c "SELECT sip_profile_name, sip_profile_enabled FROM v_sip_profiles WHERE sip_profile_name = 'wss';"

# If profile is disabled, enable it
sudo -u postgres psql fusionpbx -c "UPDATE v_sip_profiles SET sip_profile_enabled = 'true' WHERE sip_profile_name = 'wss';"

# Then trigger regeneration via GUI or find the PHP script
```

### 🔧 DIRECT FIX: XML File Exists But Not Loading

If `wss.xml` exists in `/etc/freeswitch/sip_profiles/` but FreeSWITCH still can't see it, the XML might be failing to parse silently. Common issues:

#### Issue 1: Missing TLS Certificate Configuration

WSS profiles require TLS certificates. Add TLS certificate paths to your XML:

```bash
# Check if TLS certificates exist
ls -la /etc/freeswitch/tls/*.pem

# Get FreeSWITCH base directory for certificate paths
BASE_DIR=$(fs_cli -x "global_getvar base_dir" | tail -1)
echo "Base dir: $BASE_DIR"

# Update wss.xml with TLS certificate configuration
sudo tee /etc/freeswitch/sip_profiles/wss.xml > /dev/null << EOF
<profile name="wss">
  <settings>
    <param name="name" value="wss"/>
    <param name="sip-ip" value="0.0.0.0"/>
    <param name="sip-port" value="7443"/>
    <param name="tls" value="true"/>
    <param name="tls-bind-params" value="transport=wss"/>
    <param name="tls-cert-dir" value="\$\${base_dir}/conf/tls"/>
    <param name="tls-cert-file" value="\$\${base_dir}/conf/tls/wss.pem"/>
    <param name="tls-key-file" value="\$\${base_dir}/conf/tls/wss.pem"/>
    <param name="ext-sip-ip" value="136.115.41.45"/>
    <param name="ext-rtp-ip" value="136.115.41.45"/>
    <param name="domain" value="136.115.41.45"/>
    <param name="codec-prefs" value="G722,PCMU,PCMA"/>
    <param name="rtp-ip" value="0.0.0.0"/>
    <param name="rtp-min-port" value="16384"/>
    <param name="rtp-max-port" value="32768"/>
    <param name="local-network-acl" value="localnet.auto"/>
    <param name="apply-nat-acl" value="nat.auto"/>
    <param name="apply-inbound-acl" value="domains"/>
    <param name="apply-register-acl" value="domains"/>
    <param name="bypass-media" value="false"/>
    <param name="media-bypass" value="false"/>
  </settings>
</profile>
EOF

# Fix permissions
FS_USER=$(ps aux | grep '[f]reeswitch' | awk '{print $1}' | head -1)
FS_USER=${FS_USER:-www-data}
sudo chown $FS_USER:$FS_USER /etc/freeswitch/sip_profiles/wss.xml
sudo chmod 644 /etc/freeswitch/sip_profiles/wss.xml

# Reload and try
fs_cli -x "reloadxml"
sleep 2
fs_cli -x "sofia profile wss start"
fs_cli -x "sofia status profile wss"
```

#### Issue 2: Check for XML Parsing Errors

Enable XML debug logging to see if there are parsing errors:

```bash
# Enable XML debug
fs_cli -x "console loglevel debug"
fs_cli -x "loglevel 7"

# Reload XML and watch for errors
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "wss|xml|parse|error|syntax" &
TAIL_PID=$!

fs_cli -x "reloadxml"
sleep 3
kill $TAIL_PID

# Check for specific XML parsing errors
tail -100 /var/log/freeswitch/freeswitch.log | grep -A 5 -B 5 -iE "wss|xml.*error|parse.*error" | tail -20
```

#### Issue 3: Verify XML is Being Included

Check if the XML file is actually being read during reloadxml:

```bash
# Check file permissions
ls -la /etc/freeswitch/sip_profiles/wss.xml

# Verify the include pattern matches
echo "Checking if wss.xml matches include pattern..."
ls -1 /etc/freeswitch/sip_profiles/*.xml | grep -v "\.noload"

# Check if wss.xml is listed
ls -1 /etc/freeswitch/sip_profiles/*.xml | grep wss

# Test XML syntax manually (if xmllint is available)
which xmllint && xmllint --noout /etc/freeswitch/sip_profiles/wss.xml || echo "xmllint not available - checking manually..."

# Check for common XML issues
grep -n "<param\|</param\|<profile\|</profile\|<settings\|</settings" /etc/freeswitch/sip_profiles/wss.xml
```

#### Issue 4: Profile Not Appearing in sofia status After reloadxml

If `wss` doesn't appear in `sofia status` after `reloadxml`, the XML file isn't being parsed. This could mean:

1. **FusionPBX is overwriting the file** - FusionPBX regenerates profiles from the database and may overwrite manual XML files
2. **XML syntax error** - A syntax error prevents the file from being parsed, but no error is shown
3. **Include pattern issue** - The file doesn't match the include pattern

**Fix: Check if FusionPBX is regenerating the file:**

```bash
# Monitor if the file gets overwritten during reloadxml
md5sum /etc/freeswitch/sip_profiles/wss.xml
BEFORE_MD5=$(md5sum /etc/freeswitch/sip_profiles/wss.xml | awk '{print $1}')

fs_cli -x "reloadxml"
sleep 2

AFTER_MD5=$(md5sum /etc/freeswitch/sip_profiles/wss.xml | awk '{print $1}')

if [ "$BEFORE_MD5" != "$AFTER_MD5" ]; then
    echo "⚠️ WARNING: File was modified during reloadxml!"
    echo "FusionPBX is overwriting your manual XML file"
    echo "You need to configure via FusionPBX GUI or database instead"
else
    echo "✅ File was not modified"
fi
```

**Fix: Check if there's an XML parsing error that's silent:**

```bash
# Enable maximum XML logging
fs_cli -x "console loglevel debug"
fs_cli -x "loglevel 7"

# Watch for XML parsing errors
tail -f /var/log/freeswitch/freeswitch.log | grep -iE "wss|xml|parse|error|sip_profiles" &
TAIL_PID=$!

fs_cli -x "reloadxml"
sleep 3
kill $TAIL_PID

# Check specifically for wss-related errors
tail -200 /var/log/freeswitch/freeswitch.log | grep -A 10 -B 10 -iE "wss|sip_profiles.*wss" | tail -30
```

**Fix: Try using FusionPBX GUI to create the profile**

Since FusionPBX generates profiles dynamically, the most reliable way is through the GUI:

1. **Login to FusionPBX:** `https://136.115.41.45`
2. **Navigate to:** `Advanced → SIP Profiles`
3. **Click "Add" or "+"** to create a new profile
4. **Set Profile Name:** `wss`
5. **Configure all settings via GUI**
6. **Save**
7. **Go to:** `Status → SIP Status`
8. **Click "Reload XML"** at the top
9. **Find "wss" profile and click "Restart"**

**Fix: Check if profile needs to be in a specific database state**

FusionPBX might require specific database entries beyond just the profile and settings:

```bash
# Check what tables are involved
sudo -u postgres psql fusionpbx -c "\dt" | grep -i "sip\|profile"

# Check if there are any constraints or triggers
sudo -u postgres psql fusionpbx -c "SELECT tablename, indexname FROM pg_indexes WHERE tablename LIKE '%sip%profile%';"

# Check if internal/external profiles have something wss doesn't
sudo -u postgres psql fusionpbx -c "SELECT * FROM v_sip_profiles WHERE sip_profile_name IN ('internal', 'external', 'wss') ORDER BY sip_profile_name;"

# Compare settings count
sudo -u postgres psql fusionpbx -c "
SELECT 
    sp.sip_profile_name,
    COUNT(sps.sip_profile_setting_uuid) as setting_count
FROM v_sip_profiles sp
LEFT JOIN v_sip_profile_settings sps ON sp.sip_profile_uuid = sps.sip_profile_uuid
WHERE sp.sip_profile_name IN ('internal', 'external', 'wss')
GROUP BY sp.sip_profile_name
ORDER BY sp.sip_profile_name;"
```

---
