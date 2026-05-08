# schema_loader.py — TiDB Schema Deployment Tool
# Version: v0.1.0
# Author: Haiwen Yin (胖头鱼 🐟 / yhw)
# License: Apache 2.0

"""
TiDB Schema Loader - Automated DDL deployment tool for memory system tables.
Supports dry-run mode, schema validation, and idempotent deployments.
"""

import os
import sys
import pymysql
from typing import Optional


class SchemaLoader:
    """Deploy and manage TiDB memory system schema."""
    
    def __init__(self, host='127.0.0.1', port=4000, user='root@memcluster', 
                 password='', database='memory_system'):
        self.host = os.environ.get('TIDB_HOST', host)
        self.port = int(os.environ.get('TIDB_PORT', port))
        self.user = os.environ.get('TIDB_USER', user)
        self.password = os.environ.get('TIDB_PASS', password)
        self.database = os.environ.get('TIDB_DATABASE', database)
        
    def connect(self):
        """Establish connection to TiDB tenant database."""
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    
    def check_schema_exists(self) -> bool:
        """Check if memory system schema already exists in the database."""
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                # Check for primary table existence
                cursor.execute("""
                    SELECT COUNT(*) as cnt 
                    FROM information_schema.TABLES 
                    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'memory_nodes'
                """, (self.database,))
                
                result = cursor.fetchone()
                return result['cnt'] > 0 if result else False
        finally:
            conn.close()
    
    def apply_schema(self, sql_file_path: Optional[str] = None, dry_run: bool = False):
        """Apply schema DDL from file.
        
        Args:
            sql_file_path: Path to SQL file (defaults to init_memory_system.sql in scripts/)
            dry_run: If True, only print statements without executing
        """
        if not sql_file_path:
            # Auto-detect script location
            current_dir = os.path.dirname(os.path.abspath(__file__))
            sql_file_path = os.path.join(current_dir, 'init_memory_system.sql')
        
        # Read SQL file
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Split into individual statements (handle semicolons)
        statements = []
        current_statement = ""
        for line in sql_content.split('\n'):
            stripped = line.strip()
            if stripped.startswith('--') or not stripped:
                continue
            current_statement += line + '\n'
            if stripped.endswith(';'):
                statements.append(current_statement.rstrip())
                current_statement = ""
        
        # Remove empty statements
        statements = [s for s in statements if s.strip()]
        
        print(f"Found {len(statements)} SQL statements")
        
        if dry_run:
            print("\n=== DRY RUN MODE ===")
            for i, stmt in enumerate(statements, 1):
                preview = stmt[:80].replace('\n', ' ') + "..." if len(stmt) > 80 else stmt.replace('\n', ' ')
                print(f"Statement {i}: {preview}")
            return
        
        # Execute statements
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                for i, statement in enumerate(statements, 1):
                    # Skip comment-only statements
                    if not statement.strip():
                        continue
                    
                    try:
                        cursor.execute(statement)
                        print(f"✓ Statement {i} executed successfully")
                    except Exception as e:
                        preview = statement[:50].replace('\n', ' ') + "..." if len(statement) > 50 else statement.replace('\n', ' ')
                        print(f"✗ Statement {i} failed: {preview}")
                        print(f"  Error: {str(e)}")
            
            conn.commit()
            print("\n✓ Schema deployment completed!")
        except Exception as e:
            conn.rollback()
            print(f"\n✗ Deployment failed with error: {e}")
            raise
        finally:
            conn.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy TiDB memory system schema')
    parser.add_argument('--dry-run', action='store_true', help='Preview without executing')
    parser.add_argument('--sql-file', type=str, help='Path to SQL file')
    parser.add_argument('--check-exists', action='store_true', help='Only check if schema exists')
    
    args = parser.parse_args()
    
    loader = SchemaLoader()
    
    if args.check_exists:
        exists = loader.check_schema_exists()
        print(f"Schema exists: {exists}")
        sys.exit(0 if exists else 1)
    
    if not args.sql_file and not os.path.exists(os.path.join(os.path.dirname(__file__), 'init_memory_system.sql')):
        print("Error: Cannot find init_memory_system.sql in scripts directory")
        sys.exit(1)
    
    loader.apply_schema(sql_file_path=args.sql_file, dry_run=args.dry_run)
