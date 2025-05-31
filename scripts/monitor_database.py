#!/usr/bin/env python3
"""
Database Monitoring Script for IFAM FastAPI Backend

This script monitors database metrics and performance:
- Database size and growth
- Table sizes and row counts
- Index usage statistics
- Query performance metrics
- Connection pool status

Usage:
    python monitor_database.py [--output-format FORMAT]

Options:
    --output-format    Output format: text, json, or csv (default: text)
"""

import os
import sys
import argparse
import json
import csv
import logging
import datetime
from pathlib import Path
import sqlite3
import pymysql
from tabulate import tabulate

# Add the parent directory to sys.path to import app modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('database_monitoring.log')
    ]
)
logger = logging.getLogger('database_monitoring')

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Monitor the application database')
    parser.add_argument('--output-format', choices=['text', 'json', 'csv'], default='text',
                        help='Output format (default: text)')
    return parser.parse_args()

def get_sqlite_metrics(db_path):
    """Get metrics for a SQLite database."""
    metrics = {
        'database_name': os.path.basename(db_path),
        'database_path': db_path,
        'timestamp': datetime.datetime.now().isoformat(),
        'database_type': 'SQLite',
        'tables': [],
        'indexes': [],
        'database_stats': {}
    }
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get database size
        cursor.execute("PRAGMA page_count;")
        page_count = cursor.fetchone()[0]
        cursor.execute("PRAGMA page_size;")
        page_size = cursor.fetchone()[0]
        db_size_bytes = page_count * page_size
        metrics['database_stats']['size_bytes'] = db_size_bytes
        metrics['database_stats']['size_mb'] = db_size_bytes / (1024 * 1024)
        
        # Get database version
        cursor.execute("SELECT sqlite_version();")
        metrics['database_stats']['version'] = cursor.fetchone()[0]
        
        # Get database encoding
        cursor.execute("PRAGMA encoding;")
        metrics['database_stats']['encoding'] = cursor.fetchone()[0]
        
        # Get table list and stats
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            table_info = {'name': table, 'columns': [], 'row_count': 0}
            
            # Get column info
            cursor.execute(f"PRAGMA table_info(`{table}`);")
            columns = cursor.fetchall()
            for col in columns:
                column_info = {
                    'name': col['name'],
                    'type': col['type'],
                    'notnull': bool(col['notnull']),
                    'pk': bool(col['pk'])
                }
                table_info['columns'].append(column_info)
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM `{table}`;")
            table_info['row_count'] = cursor.fetchone()[0]
            
            metrics['tables'].append(table_info)
        
        # Get index information
        cursor.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index';")
        indexes = cursor.fetchall()
        
        for idx in indexes:
            index_info = {
                'name': idx['name'],
                'table': idx['tbl_name']
            }
            
            # Get index details
            cursor.execute(f"PRAGMA index_info(`{idx['name']}`);")
            index_columns = cursor.fetchall()
            index_info['columns'] = [col['name'] for col in index_columns]
            
            metrics['indexes'].append(index_info)
        
        conn.close()
        return metrics
    
    except Exception as e:
        logger.error(f"Error getting SQLite metrics: {e}")
        return None

def get_mysql_metrics(connection_string):
    """Get metrics for a MySQL database."""
    metrics = {
        'timestamp': datetime.datetime.now().isoformat(),
        'database_type': 'MySQL',
        'tables': [],
        'indexes': [],
        'database_stats': {}
    }
    
    try:
        # Parse MySQL connection string
        # Format: mysql+pymysql://user:password@host:port/dbname
        conn_parts = connection_string.replace('mysql+pymysql://', '').split('@')
        user_pass = conn_parts[0].split(':')
        host_db = conn_parts[1].split('/')
        
        user = user_pass[0]
        password = user_pass[1] if len(user_pass) > 1 else ''
        
        host_port = host_db[0].split(':')
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 3306
        
        database = host_db[1]
        metrics['database_name'] = database
        
        # Connect to MySQL
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        try:
            with connection.cursor() as cursor:
                # Get database version
                cursor.execute("SELECT VERSION();")
                metrics['database_stats']['version'] = cursor.fetchone()['VERSION()']
                
                # Get database size
                cursor.execute("""
                    SELECT 
                        SUM(data_length + index_length) as size_bytes,
                        SUM(data_length + index_length) / 1024 / 1024 as size_mb
                    FROM 
                        information_schema.tables 
                    WHERE 
                        table_schema = %s;
                """, (database,))
                size_info = cursor.fetchone()
                metrics['database_stats']['size_bytes'] = size_info['size_bytes']
                metrics['database_stats']['size_mb'] = size_info['size_mb']
                
                # Get table information
                cursor.execute("""
                    SELECT 
                        table_name,
                        engine,
                        table_rows,
                        data_length,
                        index_length,
                        create_time,
                        update_time
                    FROM 
                        information_schema.tables 
                    WHERE 
                        table_schema = %s;
                """, (database,))
                tables = cursor.fetchall()
                
                for table in tables:
                    table_info = {
                        'name': table['table_name'],
                        'engine': table['engine'],
                        'row_count': table['table_rows'],
                        'data_size_bytes': table['data_length'],
                        'index_size_bytes': table['index_length'],
                        'total_size_bytes': table['data_length'] + table['index_length'],
                        'created_at': table['create_time'].isoformat() if table['create_time'] else None,
                        'updated_at': table['update_time'].isoformat() if table['update_time'] else None,
                        'columns': []
                    }
                    
                    # Get column information
                    cursor.execute("""
                        SELECT 
                            column_name,
                            column_type,
                            is_nullable,
                            column_key,
                            column_default,
                            extra
                        FROM 
                            information_schema.columns 
                        WHERE 
                            table_schema = %s AND table_name = %s;
                    """, (database, table['table_name']))
                    columns = cursor.fetchall()
                    
                    for col in columns:
                        column_info = {
                            'name': col['column_name'],
                            'type': col['column_type'],
                            'nullable': col['is_nullable'] == 'YES',
                            'key': col['column_key'],
                            'default': col['column_default'],
                            'extra': col['extra']
                        }
                        table_info['columns'].append(column_info)
                    
                    metrics['tables'].append(table_info)
                
                # Get index information
                cursor.execute("""
                    SELECT 
                        table_name,
                        index_name,
                        non_unique,
                        column_name,
                        seq_in_index
                    FROM 
                        information_schema.statistics 
                    WHERE 
                        table_schema = %s 
                    ORDER BY 
                        table_name, index_name, seq_in_index;
                """, (database,))
                index_rows = cursor.fetchall()
                
                # Process index information
                current_index = None
                for row in index_rows:
                    if current_index is None or current_index['name'] != row['index_name'] or current_index['table'] != row['table_name']:
                        if current_index is not None:
                            metrics['indexes'].append(current_index)
                        
                        current_index = {
                            'name': row['index_name'],
                            'table': row['table_name'],
                            'unique': not bool(row['non_unique']),
                            'columns': []
                        }
                    
                    current_index['columns'].append(row['column_name'])
                
                if current_index is not None:
                    metrics['indexes'].append(current_index)
                
                # Get connection pool information
                cursor.execute("SHOW STATUS LIKE 'Threads_%';")
                thread_info = cursor.fetchall()
                
                metrics['database_stats']['connection_pool'] = {
                    row['Variable_name']: row['Value'] for row in thread_info
                }
                
                # Get query cache information
                cursor.execute("SHOW VARIABLES LIKE 'query_cache%';")
                query_cache_vars = cursor.fetchall()
                
                metrics['database_stats']['query_cache'] = {
                    row['Variable_name']: row['Value'] for row in query_cache_vars
                }
                
                return metrics
                
        finally:
            connection.close()
            
    except Exception as e:
        logger.error(f"Error getting MySQL metrics: {e}")
        return None

def output_metrics_text(metrics):
    """Output metrics in text format."""
    if not metrics:
        print("No metrics available")
        return
    
    print(f"Database Monitoring Report - {metrics['timestamp']}")
    print(f"Database Type: {metrics['database_type']}")
    print(f"Database Name: {metrics['database_name']}")
    
    print("\nDatabase Statistics:")
    for key, value in metrics['database_stats'].items():
        if isinstance(value, dict):
            print(f"  {key.replace('_', ' ').title()}:")
            for subkey, subvalue in value.items():
                print(f"    {subkey}: {subvalue}")
        else:
            print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print("\nTables:")
    table_data = []
    for table in metrics['tables']:
        row_count = table.get('row_count', 0)
        size_mb = table.get('total_size_bytes', 0) / (1024 * 1024) if 'total_size_bytes' in table else 'N/A'
        size_mb = f"{size_mb:.2f} MB" if isinstance(size_mb, float) else size_mb
        table_data.append([
            table['name'],
            row_count,
            size_mb,
            len(table['columns'])
        ])
    
    print(tabulate(
        table_data,
        headers=["Table Name", "Row Count", "Size", "Column Count"],
        tablefmt="grid"
    ))
    
    print("\nIndexes:")
    index_data = []
    for index in metrics['indexes']:
        index_data.append([
            index['name'],
            index['table'],
            "Yes" if index.get('unique', False) else "No",
            ", ".join(index['columns'])
        ])
    
    print(tabulate(
        index_data,
        headers=["Index Name", "Table", "Unique", "Columns"],
        tablefmt="grid"
    ))

def output_metrics_json(metrics):
    """Output metrics in JSON format."""
    if not metrics:
        print(json.dumps({"error": "No metrics available"}))
        return
    
    print(json.dumps(metrics, indent=2))

def output_metrics_csv(metrics):
    """Output metrics in CSV format."""
    if not metrics:
        print("No metrics available")
        return
    
    # Output database stats
    print("Database Statistics:")
    writer = csv.writer(sys.stdout)
    writer.writerow(["Metric", "Value"])
    for key, value in metrics['database_stats'].items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                writer.writerow([f"{key}.{subkey}", subvalue])
        else:
            writer.writerow([key, value])
    
    # Output tables
    print("\nTables:")
    writer = csv.writer(sys.stdout)
    writer.writerow(["Table Name", "Row Count", "Size (bytes)", "Column Count"])
    for table in metrics['tables']:
        row_count = table.get('row_count', 0)
        size = table.get('total_size_bytes', 'N/A')
        writer.writerow([
            table['name'],
            row_count,
            size,
            len(table['columns'])
        ])
    
    # Output indexes
    print("\nIndexes:")
    writer = csv.writer(sys.stdout)
    writer.writerow(["Index Name", "Table", "Unique", "Columns"])
    for index in metrics['indexes']:
        writer.writerow([
            index['name'],
            index['table'],
            "Yes" if index.get('unique', False) else "No",
            ", ".join(index['columns'])
        ])

def main():
    """Main function to run the monitoring process."""
    args = parse_args()
    output_format = args.output_format
    
    try:
        if CONFIG.DB_TYPE == 'sqlite':
            # Extract SQLite database path from connection string
            # Format: sqlite:///path/to/db.sqlite
            db_path = CONFIG.DB_CONNECTION_STRING.replace('sqlite:///', '')
            if not os.path.isabs(db_path):
                # If path is relative, make it absolute from the project root
                db_path = os.path.join(Path(__file__).resolve().parent.parent, db_path)
            
            if os.path.exists(db_path):
                metrics = get_sqlite_metrics(db_path)
            else:
                logger.error(f"SQLite database file not found: {db_path}")
                sys.exit(1)
                
        elif CONFIG.DB_TYPE == 'mysql':
            metrics = get_mysql_metrics(CONFIG.DB_CONNECTION_STRING)
            
        else:
            logger.error(f"Unsupported database type: {CONFIG.DB_TYPE}")
            sys.exit(1)
        
        if metrics:
            if output_format == 'json':
                output_metrics_json(metrics)
            elif output_format == 'csv':
                output_metrics_csv(metrics)
            else:
                output_metrics_text(metrics)
        else:
            logger.error("Failed to get database metrics")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Monitoring failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
