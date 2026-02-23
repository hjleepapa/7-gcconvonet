# FusionPBX: Create "public" Context - Step by Step

## Confirmed Issue
- ✅ SIP profile `internal` uses `Context: public`
- ❌ "public" context doesn't exist in Dialplan Manager dropdown
- **Solution:** Create the "public" context first

## Step-by-Step: Create "public" Context

### Method 1: Via Dialplan Manager (If Available)

1. **Login to FusionPBX:** `https://136.115.41.45`
2. **Navigate:** Advanced → Dialplan Manager
3. **Look for:**
   - A "Contexts" tab or button
   - Or "Add Context" button
   - Or a dropdown/selector for contexts with a "+" or "Add" option
4. **Create new context:**
   - **Name:** `public`
   - **Description:** `Public context for external calls`
   - **Save**

### Method 2: Via Advanced Menu

1. **Login to FusionPBX:** `https://136.115.41.45`
2. **Navigate:** Advanced → (look for)
   - Dialplan → Contexts
   - Or Settings → Dialplan → Contexts
   - Or Advanced → Contexts
3. **Click:** "+" or "Add" button
4. **Fill in:**
   - **Name:** `public`
   - **Description:** `Public context for external calls`
   - **Save**

### Method 3: Via Database (If UI Not Available)

If you can't find the UI option, create it directly in the database:

```bash
# Connect to FusionPBX database
psql -U fusionpbx -d fusionpbx

# Create public context
INSERT INTO v_dialplans (dialplan_uuid, dialplan_name, dialplan_context, dialplan_enabled, domain_uuid)
SELECT 
    uuid_generate_v4(),
    'public',
    'public',
    'true',
    (SELECT domain_uuid FROM v_domains LIMIT 1)
WHERE NOT EXISTS (
    SELECT 1 FROM v_dialplans WHERE dialplan_context = 'public'
);

# Exit psql
\q
```

Then reload XML:
```bash
fs_cli -x "reloadxml"
```

### Method 4: Direct XML File Edit (Last Resort)

If none of the above work, create the context XML file directly:

```bash
# Find dialplan directory
find /etc/freeswitch -name "dialplan" -type d 2>/dev/null

# Or check FusionPBX structure
ls -la /var/www/fusionpbx/app/dialplan/

# Create public.xml file
cat > /etc/freeswitch/dialplan/public.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<include>
  <context name="public">
    <!-- Dialplan entries will go here -->
  </context>
</include>
EOF

# Set permissions
chown freeswitch:freeswitch /etc/freeswitch/dialplan/public.xml
chmod 644 /etc/freeswitch/dialplan/public.xml

# Reload XML
fs_cli -x "reloadxml"
```

## After Creating "public" Context

1. **Verify it appears in dropdown:**
   - Go to Dialplan Manager → Add
   - Check if "public" now appears in Context dropdown

2. **Create dialplan entry:**
   - **Context:** Select `public`
   - **Name:** `Twilio-to-Extension-2001`
   - **Enabled:** `True`
   - **Continue**
   - **Condition 1:** `destination_number` = `^2001$`
   - **Action 1:** `transfer` = `2001 XML internal`
   - **Save**

3. **Reload XML:**
   ```bash
   fs_cli -x "reloadxml"
   ```

## Quick Test

After creating context and dialplan:

```bash
# Reload XML
fs_cli -x "reloadxml"

# Check if context exists now
fs_cli -x "show dialplan" | grep public

# Test a call transfer
```

## Troubleshooting

If "public" still doesn't appear after creating:

1. **Check if it was created:**
   ```bash
   # Check database
   psql -U fusionpbx -d fusionpbx -c "SELECT * FROM v_dialplans WHERE dialplan_context = 'public';"
   
   # Check XML files
   ls -la /etc/freeswitch/dialplan/ | grep public
   ```

2. **Reload XML:**
   ```bash
   fs_cli -x "reloadxml"
   ```

3. **Refresh browser** and check dropdown again

