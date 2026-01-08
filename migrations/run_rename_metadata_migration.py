"""
Run Metadata Column Rename Migration
Renames 'metadata' columns to 'app_metadata' and 'doc_metadata' to avoid SQLAlchemy reserved name conflict
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_rename_migration():
    """Run the metadata column rename migration"""
    # Get database URI from environment
    db_uri = os.getenv("DB_URI")
    
    if not db_uri:
        print("❌ DB_URI environment variable not set")
        sys.exit(1)
    
    print(f"🔧 Connecting to database...")
    print(f"   Database: {db_uri.split('@')[1] if '@' in db_uri else 'hidden'}")
    
    try:
        # Create engine
        engine = create_engine(db_uri, pool_pre_ping=True)
        
        # Read SQL file
        sql_file_path = os.path.join(
            os.path.dirname(__file__),
            "rename_metadata_columns.sql"
        )
        
        if not os.path.exists(sql_file_path):
            print(f"❌ SQL file not found: {sql_file_path}")
            sys.exit(1)
        
        print(f"📄 Reading SQL file: {sql_file_path}")
        with open(sql_file_path, 'r') as f:
            sql_content = f.read()
        
        # Split SQL into individual statements
        statements = []
        current_statement = []
        
        for line in sql_content.split('\n'):
            # Skip comment-only lines
            if line.strip().startswith('--'):
                continue
            # Skip empty lines
            if not line.strip():
                continue
            
            current_statement.append(line)
            
            # If line ends with semicolon, it's end of statement
            if line.strip().endswith(';'):
                statement = '\n'.join(current_statement)
                if statement.strip():
                    statements.append(statement)
                current_statement = []
        
        # Execute statements
        print(f"🚀 Executing {len(statements)} SQL statements...")
        
        with engine.connect() as conn:
            # Begin transaction
            trans = conn.begin()
            
            try:
                for i, statement in enumerate(statements, 1):
                    # Skip empty statements
                    if not statement.strip() or statement.strip() == ';':
                        continue
                    
                    print(f"   [{i}/{len(statements)}] Executing statement...")
                    try:
                        conn.execute(text(statement))
                        conn.commit()
                    except Exception as e:
                        # Check if column doesn't exist (already renamed or table doesn't exist)
                        error_msg = str(e)
                        if "does not exist" in error_msg.lower():
                            print(f"   ⚠️  Statement {i} skipped (column may already be renamed or table doesn't exist): {error_msg[:100]}")
                            conn.rollback()
                        else:
                            raise
                
                print("✅ Migration completed successfully!")
                print("\n📊 Verifying columns...")
                
                # Verify columns were renamed
                verification_query = text("""
                    SELECT 
                        table_name,
                        column_name
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                    AND table_name IN ('mortgage_applications', 'mortgage_documents')
                    AND column_name IN ('app_metadata', 'doc_metadata', 'metadata')
                    ORDER BY table_name, column_name;
                """)
                
                result = conn.execute(verification_query)
                columns = [(row[0], row[1]) for row in result]
                
                if columns:
                    print(f"✅ Found columns:")
                    for table, column in columns:
                        print(f"   - {table}.{column}")
                    
                    # Check if old metadata columns still exist
                    old_metadata = [c for t, c in columns if c == 'metadata']
                    if old_metadata:
                        print(f"\n⚠️  Warning: Old 'metadata' columns still exist. Please check manually.")
                    else:
                        print(f"\n✅ All 'metadata' columns have been renamed successfully!")
                else:
                    print("⚠️  No columns found (tables may not exist yet)")
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Migration failed: {e}")
                import traceback
                traceback.print_exc()
                sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Metadata Column Rename Migration")
    print("=" * 60)
    print()
    print("This will rename 'metadata' columns to 'app_metadata' and 'doc_metadata'")
    print("to avoid SQLAlchemy reserved name conflict.")
    print()
    run_rename_migration()
    print()
    print("=" * 60)
