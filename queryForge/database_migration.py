#!/usr/bin/env python3
"""
Database Migration Script
Migrates data from SQL Server to PostgreSQL
"""

import pyodbc
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
import logging
from datetime import datetime
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class DatabaseMigrator:
    def __init__(self):
        # SQL Server connection settings
        self.sql_server_config = {
            'driver': '{ODBC Driver 17 for SQL Server}',
            'server': 'SOFDEV',
            'username': 'sa',
            'password': 'DCPower2014',
            'trust_certificate': True
        }
        
        # PostgreSQL connection settings  
        self.postgres_config = {
            'host': 'localhost',
            'database': 'queryforge_db',
            'user': 'queryforge',
            'password': 'secretpassword',
            'port': '5432'
        }
        
        self.sql_conn = None
        self.pg_conn = None
        self.sql_engine = None
        self.pg_engine = None
    
    def connect_sql_server(self):
        """Connect to SQL Server"""
        try:
            conn_str = (
                f"DRIVER={self.sql_server_config['driver']};"
                f"SERVER={self.sql_server_config['server']};"
                f"UID={self.sql_server_config['username']};"
                f"PWD={self.sql_server_config['password']};"
                f"TrustServerCertificate=yes"
            )
            self.sql_conn = pyodbc.connect(conn_str)
            
            # Also create SQLAlchemy engine for pandas
            engine_str = (
                f"mssql+pyodbc://{self.sql_server_config['username']}:"
                f"{self.sql_server_config['password']}@"
                f"{self.sql_server_config['server']}/master?"
                f"driver=ODBC+Driver+17+for+SQL+Server&Encrypt=no"
            )
            self.sql_engine = create_engine(engine_str)
            
            logging.info("✓ Connected to SQL Server")
            return True
        except Exception as e:
            logging.error(f"✗ SQL Server connection failed: {e}")
            return False
    
    def connect_postgresql(self):
        """Connect to PostgreSQL"""
        try:
            self.pg_conn = psycopg2.connect(
                host=self.postgres_config['host'],
                database=self.postgres_config['database'],
                user=self.postgres_config['user'],
                password=self.postgres_config['password'],
                port=self.postgres_config['port']
            )
            
            # Also create SQLAlchemy engine for pandas
            engine_str = (
                f"postgresql+psycopg2://{self.postgres_config['user']}:"
                f"{self.postgres_config['password']}@"
                f"{self.postgres_config['host']}:{self.postgres_config['port']}/"
                f"{self.postgres_config['database']}"
            )
            self.pg_engine = create_engine(engine_str)
            
            logging.info("✓ Connected to PostgreSQL")
            return True
        except Exception as e:
            logging.error(f"✗ PostgreSQL connection failed: {e}")
            return False
    
    def get_sql_server_tables(self, database_name=None):
        """Get list of tables from SQL Server"""
        try:
            query = """
            SELECT 
                TABLE_SCHEMA,
                TABLE_NAME,
                TABLE_TYPE
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_SCHEMA, TABLE_NAME
            """
            
            if database_name:
                # Switch to specific database
                cursor = self.sql_conn.cursor()
                cursor.execute(f"USE [{database_name}]")
                cursor.commit()
            
            df = pd.read_sql(query, self.sql_conn)
            logging.info(f"Found {len(df)} tables in SQL Server")
            return df
        except Exception as e:
            logging.error(f"Error getting SQL Server tables: {e}")
            return None
    
    def migrate_table(self, schema_name, table_name, chunk_size=1000):
        """Migrate a single table from SQL Server to PostgreSQL"""
        try:
            full_table_name = f"[{schema_name}].[{table_name}]"
            logging.info(f"Starting migration of {full_table_name}")
            
            # Get table structure
            structure_query = f"""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                CHARACTER_MAXIMUM_LENGTH,
                NUMERIC_PRECISION,
                NUMERIC_SCALE
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = '{schema_name}' AND TABLE_NAME = '{table_name}'
            ORDER BY ORDINAL_POSITION
            """
            
            columns_df = pd.read_sql(structure_query, self.sql_conn)
            logging.info(f"Table {full_table_name} has {len(columns_df)} columns")
            
            # Get row count
            count_query = f"SELECT COUNT(*) as row_count FROM {full_table_name}"
            row_count = pd.read_sql(count_query, self.sql_conn).iloc[0]['row_count']
            logging.info(f"Table {full_table_name} has {row_count} rows")
            
            if row_count == 0:
                logging.info(f"Skipping empty table {full_table_name}")
                return True
            
            # Migrate data in chunks
            postgres_table_name = f"{schema_name}_{table_name}".lower()
            
            for offset in range(0, row_count, chunk_size):
                data_query = f"""
                SELECT * FROM {full_table_name}
                ORDER BY (SELECT NULL)
                OFFSET {offset} ROWS
                FETCH NEXT {chunk_size} ROWS ONLY
                """
                
                chunk_df = pd.read_sql(data_query, self.sql_conn)
                
                # Write to PostgreSQL
                chunk_df.to_sql(
                    postgres_table_name,
                    self.pg_engine,
                    if_exists='append' if offset > 0 else 'replace',
                    index=False,
                    method='multi'
                )
                
                logging.info(f"Migrated rows {offset + 1} to {min(offset + chunk_size, row_count)} of {full_table_name}")
            
            logging.info(f"✓ Successfully migrated {full_table_name} to {postgres_table_name}")
            return True
            
        except Exception as e:
            logging.error(f"✗ Error migrating table {schema_name}.{table_name}: {e}")
            return False
    
    def run_migration(self, database_name=None, table_filter=None):
        """Run the complete migration process"""
        logging.info("Starting database migration...")
        
        # Connect to databases
        if not self.connect_postgresql():
            return False
            
        if not self.connect_sql_server():
            return False
        
        # Get list of tables
        tables_df = self.get_sql_server_tables(database_name)
        if tables_df is None:
            return False
        
        # Filter tables if specified
        if table_filter:
            tables_df = tables_df[tables_df['TABLE_NAME'].str.contains(table_filter, case=False)]
        
        # Migrate each table
        success_count = 0
        total_tables = len(tables_df)
        
        for _, row in tables_df.iterrows():
            schema = row['TABLE_SCHEMA']
            table = row['TABLE_NAME']
            
            if self.migrate_table(schema, table):
                success_count += 1
        
        logging.info(f"Migration completed: {success_count}/{total_tables} tables migrated successfully")
        
        # Close connections
        if self.sql_conn:
            self.sql_conn.close()
        if self.pg_conn:
            self.pg_conn.close()
        
        return success_count == total_tables

def main():
    """Main function"""
    migrator = DatabaseMigrator()
    
    # Test connections first
    print("Testing database connections...")
    
    if migrator.connect_postgresql():
        print("✓ PostgreSQL connection successful")
    else:
        print("✗ PostgreSQL connection failed")
        return
    
    if migrator.connect_sql_server():
        print("✓ SQL Server connection successful")
        print("\nUse this script to migrate your data:")
        print("python database_migration.py")
        print("\nOr customize the migration:")
        print("# migrator.run_migration(database_name='YourDatabase')")
        print("# migrator.run_migration(table_filter='Customer')")
    else:
        print("✗ SQL Server connection failed")
        print("Please check the SQL Server credentials and network connectivity")

if __name__ == "__main__":
    main()