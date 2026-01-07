# How to Run Mortgage Database Migration on Render.com

## Option 1: Using Python Script (Recommended)

This is the easiest method and works directly with your existing setup.

### Steps:

1. **Set your DB_URI environment variable** (if not already set):
   ```bash
   export DB_URI="postgresql://hjone:lCyOYIKUZROfH12TzjkWVCC813f83BWw@dpg-d0nkb5jipnbc7393afi0-a/posts_8uci"
   ```

2. **Run the migration script**:
   ```bash
   cd /Users/hj/Web\ Development\ Projects/2.\ Convonet-Anthropic
   python migrations/run_mortgage_migration.py
   ```

   Or if you're in the project root:
   ```bash
   python migrations/run_mortgage_migration.py
   ```

3. **Verify the migration**:
   The script will automatically verify that tables were created.

---

## Option 2: Using psql Command Line

If you have `psql` installed locally, you can connect directly to Render's database.

### Steps:

1. **Install psql** (if not installed):
   - **macOS**: `brew install postgresql`
   - **Linux**: `sudo apt-get install postgresql-client`
   - **Windows**: Download from [PostgreSQL website](https://www.postgresql.org/download/)

2. **Connect to Render database**:
   ```bash
   psql "postgresql://hjone:lCyOYIKUZROfH12TzjkWVCC813f83BWw@dpg-d0nkb5jipnbc7393afi0-a/posts_8uci"
   ```

3. **Run the SQL file**:
   ```sql
   \i migrations/create_mortgage_tables.sql
   ```

   Or copy-paste the SQL content directly into the psql prompt.

4. **Verify tables**:
   ```sql
   \dt mortgage*
   ```

   Should show:
   - mortgage_applications
   - mortgage_documents
   - mortgage_debts
   - mortgage_application_notes

---

## Option 3: Using Render Database Console

Render.com provides a web-based database console.

### Steps:

1. **Go to Render Dashboard**:
   - Navigate to your PostgreSQL database service
   - Click on "Connect" or "Console"

2. **Open the SQL Editor**:
   - Look for "SQL Editor" or "Query" tab

3. **Copy and paste the SQL**:
   - Open `migrations/create_mortgage_tables.sql`
   - Copy the entire content
   - Paste into the SQL editor

4. **Execute**:
   - Click "Run" or "Execute"
   - Check for any errors

5. **Verify**:
   ```sql
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public' 
   AND table_name LIKE 'mortgage%';
   ```

---

## Option 4: Using Python Flask CLI (If Integrated)

If you want to add this as a Flask command:

1. **Add to your Flask app** (`app.py` or `convonet/app.py`):
   ```python
   @app.cli.command()
   def migrate_mortgage():
       """Run mortgage database migration"""
       from migrations.run_mortgage_migration import run_migration
       run_migration()
   ```

2. **Run the command**:
   ```bash
   flask migrate-mortgage
   ```

---

## Option 5: One-Line psql Command

If you have psql installed, you can run it in one command:

```bash
psql "postgresql://hjone:lCyOYIKUZROfH12TzjkWVCC813f83BWw@dpg-d0nkb5jipnbc7393afi0-a/posts_8uci" -f migrations/create_mortgage_tables.sql
```

---

## Troubleshooting

### Error: "relation already exists"
If tables already exist, the migration will fail. You can:

1. **Drop existing tables first** (⚠️ **WARNING: This deletes all data!**):
   ```sql
   DROP TABLE IF EXISTS mortgage_application_notes CASCADE;
   DROP TABLE IF EXISTS mortgage_debts CASCADE;
   DROP TABLE IF EXISTS mortgage_documents CASCADE;
   DROP TABLE IF EXISTS mortgage_applications CASCADE;
   DROP TYPE IF EXISTS document_status CASCADE;
   DROP TYPE IF EXISTS document_type CASCADE;
   DROP TYPE IF EXISTS application_status CASCADE;
   ```

2. **Or modify the SQL file** to use `CREATE TABLE IF NOT EXISTS` (less safe)

### Error: "permission denied"
Make sure your database user has CREATE TABLE permissions. Render.com databases usually have full permissions for the owner.

### Error: "connection refused"
- Check your network connection
- Verify the DB_URI is correct
- Check if Render database is running (not paused)
- Render databases may have connection limits

### Error: "database does not exist"
Verify the database name in your connection string. For your URI:
- Database name: `posts_8uci`
- Host: `dpg-d0nkb5jipnbc7393afi0-a`

---

## Verification Queries

After running the migration, verify with these SQL queries:

### Check tables exist:
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'mortgage%'
ORDER BY table_name;
```

Expected output:
```
mortgage_application_notes
mortgage_applications
mortgage_debts
mortgage_documents
```

### Check enum types:
```sql
SELECT typname 
FROM pg_type 
WHERE typname LIKE '%status%' OR typname LIKE '%document_type%';
```

Expected output:
```
application_status
document_status
document_type
```

### Check indexes:
```sql
SELECT indexname 
FROM pg_indexes 
WHERE tablename LIKE 'mortgage%';
```

### Check table structure:
```sql
\d mortgage_applications
\d mortgage_documents
\d mortgage_debts
\d mortgage_application_notes
```

---

## Recommended Approach

**For your setup, I recommend Option 1 (Python script)** because:
- ✅ Works with your existing Python environment
- ✅ Handles errors gracefully
- ✅ Automatically verifies the migration
- ✅ No need to install additional tools
- ✅ Can be run from your local machine or Render shell

Just run:
```bash
python migrations/run_mortgage_migration.py
```

Make sure your `.env` file or environment has `DB_URI` set, or export it:
```bash
export DB_URI="postgresql://hjone:lCyOYIKUZROfH12TzjkWVCC813f83BWw@dpg-d0nkb5jipnbc7393afi0-a/posts_8uci"
python migrations/run_mortgage_migration.py
```
