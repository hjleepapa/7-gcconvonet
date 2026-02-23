# FusionPBX Database Connection - Alternative Methods

## Problem
PostgreSQL peer authentication failed. This is a common issue when trying to connect as a non-postgres user.

## Solution Options

### Option 1: Connect as postgres user (Easiest)

```bash
# Switch to postgres user
sudo -u postgres psql -d fusionpbx

# Or directly
sudo -u postgres psql fusionpbx
```

### Option 2: Use psql with password

```bash
# Try with password prompt
psql -U fusionpbx -d fusionpbx -h localhost

# Or if you know the password
PGPASSWORD=your_password psql -U fusionpbx -d fusionpbx -h localhost
```

### Option 3: Find FusionPBX database credentials

Check FusionPBX config file for database credentials:

```bash
# Find FusionPBX config
find /etc -name "*config.php" 2>/dev/null | grep -i fusion
find /var/www/fusionpbx -name "*config.php" 2>/dev/null

# Or check common locations
cat /var/www/fusionpbx/resources/config.php | grep -i db
cat /etc/fusionpbx/config.php | grep -i db
```

### Option 4: Use FreeSWITCH CLI to create context (Alternative)

Instead of database, we can try creating the context via FreeSWITCH XML directly:

```bash
# Find dialplan directory
find /etc/freeswitch -name "dialplan" -type d 2>/dev/null

# Check if public.xml exists
ls -la /etc/freeswitch/dialplan/public.xml 2>/dev/null

# If it doesn't exist, create it
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

## Recommended: Try postgres user first

```bash
# Connect as postgres user
sudo -u postgres psql fusionpbx

# Then run the INSERT command
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

# Exit
\q
```

## Alternative: Create Context via Web UI

If database access is difficult, try finding the context creation in FusionPBX web UI:

1. **Login:** `https://136.115.41.45`
2. **Look for:**
   - Advanced → Dialplan → Contexts
   - Advanced → Settings → Contexts
   - Or search for "Context" in the menu

## Quick Test: Direct XML Method

The easiest might be to create the XML file directly:

```bash
# Create public context XML file
sudo mkdir -p /etc/freeswitch/dialplan
sudo tee /etc/freeswitch/dialplan/public.xml > /dev/null << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<include>
  <context name="public">
  </context>
</include>
EOF

# Set ownership
sudo chown freeswitch:freeswitch /etc/freeswitch/dialplan/public.xml
sudo chmod 644 /etc/freeswitch/dialplan/public.xml

# Reload
fs_cli -x "reloadxml"
```

Then check if "public" appears in the dropdown.

