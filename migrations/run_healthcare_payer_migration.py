"""
Run Healthcare Payer Database Migration
Executes the SQL migration script against the PostgreSQL database
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def run_migration():
    """Run the healthcare payer tables migration"""
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
            "create_healthcare_payer_tables.sql"
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
        in_do_block = False
        
        for line in sql_content.split('\n'):
            # Skip comment-only lines (but not inside DO blocks)
            if line.strip().startswith('--') and not in_do_block:
                continue
            
            # Track DO blocks (PL/pgSQL)
            if line.strip().upper().startswith('DO $$'):
                in_do_block = True
            
            if in_do_block:
                current_statement.append(line)
                if line.strip().upper().endswith('$$;'):
                    in_do_block = False
                    statement = '\n'.join(current_statement)
                    if statement.strip():
                        statements.append(statement)
                    current_statement = []
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
            for i, statement in enumerate(statements, 1):
                # Skip empty statements
                if not statement.strip() or statement.strip() == ';':
                    continue
                
                # Show truncated statement for logging
                stmt_preview = statement.strip()[:80].replace('\n', ' ')
                print(f"   [{i}/{len(statements)}] {stmt_preview}...")
                
                try:
                    conn.execute(text(statement))
                    conn.commit()
                except Exception as e:
                    error_msg = str(e)
                    if "already exists" in error_msg.lower():
                        print(f"   ⚠️  Skipped (already exists)")
                        conn.rollback()
                    elif "does not exist" in error_msg.lower() and "drop" in statement.lower():
                        print(f"   ⚠️  Skipped (doesn't exist)")
                        conn.rollback()
                    elif "duplicate key" in error_msg.lower():
                        print(f"   ⚠️  Skipped (duplicate data)")
                        conn.rollback()
                    else:
                        print(f"   ❌ Error: {error_msg[:100]}")
                        conn.rollback()
                        # Continue with other statements
            
            print("✅ Migration completed!")
            print("\n📊 Verifying tables...")
            
            # Verify tables were created
            verification_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN (
                    'healthcare_plans',
                    'healthcare_members',
                    'plan_benefits',
                    'healthcare_claims',
                    'claim_line_items',
                    'prior_authorizations',
                    'member_accumulations',
                    'healthcare_providers',
                    'care_programs',
                    'member_care_programs'
                )
                ORDER BY table_name;
            """)
            
            result = conn.execute(verification_query)
            tables = [row[0] for row in result]
            
            if tables:
                print(f"✅ Found {len(tables)} healthcare tables:")
                for table in tables:
                    print(f"   - {table}")
                    
                # Count sample data
                count_queries = [
                    ("healthcare_plans", "SELECT COUNT(*) FROM healthcare_plans"),
                    ("healthcare_providers", "SELECT COUNT(*) FROM healthcare_providers"),
                    ("care_programs", "SELECT COUNT(*) FROM care_programs"),
                    ("plan_benefits", "SELECT COUNT(*) FROM plan_benefits")
                ]
                
                print("\n📊 Sample data counts:")
                for table_name, query in count_queries:
                    try:
                        result = conn.execute(text(query))
                        count = result.scalar()
                        print(f"   - {table_name}: {count} rows")
                    except:
                        pass
            else:
                print("⚠️  No healthcare tables found (check for errors above)")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Healthcare Payer Database Migration")
    print("=" * 60)
    print()
    run_migration()
    print()
    print("=" * 60)
