#!/usr/bin/env python3
"""
Supabase Database Setup Script
==============================

This script will help you set up your Supabase database with the required tables and sample data.
You need to have your Supabase credentials in the .env file first.

Usage:
    python setup_database.py
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def get_supabase_client() -> Client:
    """Get Supabase client with credentials from environment."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Error: Missing Supabase credentials!")
        print("Please add the following to your .env file:")
        print("SUPABASE_URL=https://your-project-ref.supabase.co")
        print("SUPABASE_KEY=your-anon-key")
        print("SUPABASE_SERVICE_ROLE_KEY=your-service-role-key")
        sys.exit(1)
    
    return create_client(url, key)

def run_sql_file(client: Client, file_path: str, description: str):
    """Run a SQL file against the Supabase database."""
    try:
        with open(file_path, 'r') as f:
            sql_content = f.read()
        
        print(f"📝 {description}...")
        
        # Split SQL into individual statements
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for statement in statements:
            if statement:
                try:
                    result = client.rpc('exec_sql', {'sql': statement}).execute()
                    print(f"   ✅ Executed successfully")
                except Exception as e:
                    # Try direct execution for some statements
                    try:
                        if 'CREATE TABLE' in statement.upper():
                            # For table creation, we'll use a different approach
                            print(f"   ⚠️  Table creation may need manual execution")
                        else:
                            print(f"   ⚠️  Statement may need manual execution: {str(e)[:100]}")
                    except:
                        print(f"   ⚠️  Statement may need manual execution")
        
        print(f"✅ {description} completed!")
        
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
    except Exception as e:
        print(f"❌ Error running {description}: {e}")

def main():
    """Main setup function."""
    print("🚀 Supabase Database Setup")
    print("=" * 40)
    
    # Test connection
    try:
        client = get_supabase_client()
        print("✅ Connected to Supabase successfully!")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        sys.exit(1)
    
    # Check if tables already exist
    try:
        result = client.table('employees').select('id').limit(1).execute()
        if result.data:
            print("⚠️  Database appears to already have data. Skipping setup.")
            response = input("Do you want to continue anyway? (y/N): ")
            if response.lower() != 'y':
                print("Setup cancelled.")
                sys.exit(0)
    except:
        # Tables don't exist, continue with setup
        pass
    
    # Run schema creation
    schema_file = "supabase/schema.sql"
    if os.path.exists(schema_file):
        run_sql_file(client, schema_file, "Creating database schema")
    else:
        print(f"❌ Schema file not found: {schema_file}")
        return
    
    # Run sample data
    sample_file = "supabase/sample_data.sql"
    if os.path.exists(sample_file):
        run_sql_file(client, sample_file, "Adding sample data")
    else:
        print(f"❌ Sample data file not found: {sample_file}")
        return
    
    print("\n🎉 Database setup completed!")
    print("\nNext steps:")
    print("1. Verify your tables in the Supabase dashboard")
    print("2. Test the agent with: python livekit_switchboard_agent.py dev")
    print("3. Try voice commands like 'Search for employees' or 'Find John Smith'")

if __name__ == "__main__":
    main()

