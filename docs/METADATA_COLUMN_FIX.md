# Metadata Column Fix - SQLAlchemy Reserved Name

## Problem

SQLAlchemy's Declarative API reserves the attribute name `metadata` for internal use. When we tried to use `metadata` as a column name in our mortgage models, it caused this error:

```
sqlalchemy.exc.InvalidRequestError: Attribute name 'metadata' is reserved when using the Declarative API.
```

## Solution

Renamed the `metadata` columns to avoid the conflict:
- `MortgageApplication.metadata` → `MortgageApplication.app_metadata`
- `MortgageDocument.metadata` → `MortgageDocument.doc_metadata`

## Files Changed

1. **`convonet/models/mortgage_models.py`**
   - Renamed `metadata` to `app_metadata` in `MortgageApplication` class
   - Renamed `metadata` to `doc_metadata` in `MortgageDocument` class

2. **`migrations/create_mortgage_tables.sql`**
   - Updated column names in CREATE TABLE statements

3. **`migrations/rename_metadata_columns.sql`** (NEW)
   - Migration script to rename existing columns in deployed databases

4. **`migrations/run_rename_metadata_migration.py`** (NEW)
   - Python script to run the rename migration

## Migration Instructions

### For New Databases

If you're creating the tables for the first time, just run the normal migration:
```bash
python migrations/run_mortgage_migration.py
```

The updated `create_mortgage_tables.sql` will create tables with the correct column names.

### For Existing Databases

If you already have mortgage tables with `metadata` columns, run the rename migration:

```bash
python migrations/run_rename_metadata_migration.py
```

Or manually run the SQL:
```bash
psql -U username -d database_name -f migrations/rename_metadata_columns.sql
```

## Verification

After running the migration, verify the columns were renamed:

```sql
SELECT table_name, column_name
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name IN ('mortgage_applications', 'mortgage_documents')
AND column_name IN ('app_metadata', 'doc_metadata', 'metadata')
ORDER BY table_name, column_name;
```

You should see:
- `mortgage_applications.app_metadata` ✅
- `mortgage_documents.doc_metadata` ✅
- No `metadata` columns ❌

## Notes

- The `metadata` columns were used for storing flexible JSON data
- No code changes needed in routes or MCP tools - they don't directly access these columns
- The columns are optional (nullable=True), so existing data won't be affected
