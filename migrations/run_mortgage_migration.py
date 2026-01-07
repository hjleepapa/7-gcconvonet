"""
Run Mortgage Database Migration
Executes the SQL migration script against the Render.com PostgreSQL database
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Run the mortgage tables migration"""
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
            "create_mortgage_tables.sql"
        )
        
        if not os.path.exists(sql_file_path):
            print(f"❌ SQL file not found: {sql_file_path}")
            sys.exit(1)
        
        print(f"📄 Reading SQL file: {sql_file_path}")
        with open(sql_file_path, 'r') as f:
            sql_content = f.read()
        
        # Split SQL into individual statements (handle multiple statements)
        # Remove comments and split by semicolon
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
                        # Some statements might fail if objects already exist
                        error_msg = str(e)
                        if "already exists" in error_msg.lower() or "does not exist" in error_msg.lower():
                            print(f"   ⚠️  Statement {i} skipped (object already exists or doesn't exist): {error_msg[:100]}")
                            conn.rollback()
                        else:
                            raise
                
                print("✅ Migration completed successfully!")
                print("\n📊 Verifying tables...")
                
                # Verify tables were created
                verification_query = text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name LIKE 'mortgage%'
                    ORDER BY table_name;
                """)
                
                result = conn.execute(verification_query)
                tables = [row[0] for row in result]
                
                if tables:
                    print(f"✅ Found {len(tables)} mortgage tables:")
                    for table in tables:
                        print(f"   - {table}")
                else:
                    print("⚠️  No mortgage tables found (may need to check manually)")
                
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
    print("Mortgage Database Migration")
    print("=" * 60)
    print()
    run_migration()
    print()
    print("=" * 60)
