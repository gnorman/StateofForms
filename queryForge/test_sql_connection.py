#!/usr/bin/env python3
"""
SQL Server Connection Test
Run this script and enter your actual password when prompted
"""

import pyodbc
import getpass

def test_sql_connection():
    print("SQL Server Connection Test")
    print("=" * 40)
    
    # Get password securely
    password = getpass.getpass("Enter the actual sa password: ")
    
    # Different server name variations to try
    server_variations = [
        "SOFDEV",
        "192.168.1.55\\SOFDEV", 
        "192.168.1.55",
        "192.168.1.55,1433"
    ]
    
    connection_templates = [
        "DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={};UID=sa;PWD={};Encrypt=no",
        "DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={};UID=sa;PWD={};TrustServerCertificate=yes;Encrypt=no",
        "DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={};UID=sa;PWD={};Trusted_Connection=no;Encrypt=no"
    ]
    
    for server in server_variations:
        print(f"\nTesting server: {server}")
        
        for i, template in enumerate(connection_templates, 1):
            try:
                conn_str = template.format(server, password)
                print(f"  Attempt {i}: ", end="")
                
                conn = pyodbc.connect(conn_str, timeout=10)
                cursor = conn.cursor()
                cursor.execute("SELECT @@SERVERNAME, SYSTEM_USER, DB_NAME()")
                result = cursor.fetchone()
                
                print("✓ SUCCESS!")
                print(f"    Server: {result[0]}")
                print(f"    User: {result[1]}")
                print(f"    Database: {result[2]}")
                
                # Test a simple query
                cursor.execute("SELECT COUNT(*) FROM sys.databases")
                db_count = cursor.fetchone()[0]
                print(f"    Databases: {db_count}")
                
                conn.close()
                
                print(f"\n🎉 Working connection string:")
                print(f"    DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};UID=sa;PWD=***;Encrypt=no")
                return True
                
            except Exception as e:
                error_msg = str(e)
                if "timeout" in error_msg.lower():
                    print("✗ Timeout")
                elif "login failed" in error_msg.lower():
                    print("✗ Login failed")
                else:
                    print(f"✗ Error: {error_msg[:50]}...")
    
    print("\n❌ All connection attempts failed")
    print("\nTroubleshooting suggestions:")
    print("1. Verify the password contains the exact special characters")
    print("2. Check if SQL Server instance name is different") 
    print("3. Confirm Mixed Mode Authentication is enabled")
    print("4. Try connecting from Management Studio and check connection properties")
    
    return False

if __name__ == "__main__":
    test_sql_connection()