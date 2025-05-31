#!/usr/bin/env python3
"""
Database Optimization Script for IFAM FastAPI Backend

This script performs optimization tasks on the database to maintain performance:
- For SQLite: VACUUM, ANALYZE, and integrity check
- For MySQL: Optimize tables, analyze tables, and check for fragmentation

Usage:
    python optimize_database.py [--full]

Options:
    --full    Perform a full optimization (more intensive, may take longer)
"""

import os
import sys
import argparse
import logging
import subprocess
import datetime
from pathlib import Path
import sqlite3
import pymysql

# Add the parent directory to sys.path to import app modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('database_optimization.log')
    ]
)
logger = logging.getLogger('database_optimization')

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Optimize the application database')
    parser.add_argument('--full', action='store_true', 
                        help='Perform a full optimization (more intensive)')
    return parser.parse_args()

def optimize_sqlite(db_path, full_optimization=False):
    """Optimize a SQLite database."""
    logger.info(f"Optimizing SQLite database at: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check database integrity
        logger.info("Checking database integrity...")
        cursor.execute("PRAGMA integrity_check;")
        integrity_result = cursor.fetchone()[0]
        if integrity_result == "ok":
            logger.info("Integrity check passed")
        else:
            logger.error(f"Integrity check failed: {integrity_result}")
            return False
        
        # Run VACUUM to rebuild the database file
        if full_optimization:
            logger.info("Running VACUUM (this may take a while)...")
            cursor.execute("VACUUM;")
        
        # Run ANALYZE to update statistics
        logger.info("Running ANALYZE to update statistics...")
        cursor.execute("ANALYZE;")
        
        # Optimize indexes
        logger.info("Optimizing indexes...")
        cursor.execute("PRAGMA optimize;")
        
        # Get database size before and after
        cursor.execute("PRAGMA page_count;")
        page_count = cursor.fetchone()[0]
        cursor.execute("PRAGMA page_size;")
        page_size = cursor.fetchone()[0]
        db_size_mb = (page_count * page_size) / (1024 * 1024)
        
        logger.info(f"Database size: {db_size_mb:.2f} MB")
        logger.info("SQLite optimization completed successfully")
        
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error optimizing SQLite database: {e}")
        return False

def optimize_mysql(connection_string, full_optimization=False):
    """Optimize a MySQL database."""
    logger.info("Optimizing MySQL database")
    
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
        
        # Connect to MySQL
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        
        try:
            with connection.cursor() as cursor:
                # Get list of tables
                cursor.execute("SHOW TABLES;")
                tables = [table[0] for table in cursor.fetchall()]
                
                if not tables:
                    logger.warning("No tables found in database")
                    return True
                
                # Check and optimize each table
                for table in tables:
                    logger.info(f"Checking table: {table}")
                    
                    # Check table
                    cursor.execute(f"CHECK TABLE `{table}`;")
                    check_result = cursor.fetchall()
                    for result in check_result:
                        if result[3] != "OK":
                            logger.warning(f"Table {table} check result: {result[3]}")
                    
                    # Analyze table to update statistics
                    logger.info(f"Analyzing table: {table}")
                    cursor.execute(f"ANALYZE TABLE `{table}`;")
                    
                    if full_optimization:
                        # Optimize table (reorganizes the physical storage)
                        logger.info(f"Optimizing table: {table}")
                        cursor.execute(f"OPTIMIZE TABLE `{table}`;")
                
                # Get database size
                cursor.execute("""
                    SELECT 
                        SUM(data_length + index_length) / 1024 / 1024 AS size_mb 
                    FROM 
                        information_schema.tables 
                    WHERE 
                        table_schema = %s;
                """, (database,))
                db_size = cursor.fetchone()[0]
                logger.info(f"Database size: {db_size:.2f} MB")
                
                logger.info("MySQL optimization completed successfully")
                return True
                
        finally:
            connection.close()
            
    except Exception as e:
        logger.error(f"Error optimizing MySQL database: {e}")
        return False

def main():
    """Main function to run the optimization process."""
    args = parse_args()
    full_optimization = args.full
    
    if full_optimization:
        logger.info("Performing FULL database optimization (this may take longer)")
    else:
        logger.info("Performing standard database optimization")
    
    try:
        if CONFIG.DB_TYPE == 'sqlite':
            # Extract SQLite database path from connection string
            # Format: sqlite:///path/to/db.sqlite
            db_path = CONFIG.DB_CONNECTION_STRING.replace('sqlite:///', '')
            if not os.path.isabs(db_path):
                # If path is relative, make it absolute from the project root
                db_path = os.path.join(Path(__file__).resolve().parent.parent, db_path)
            
            if os.path.exists(db_path):
                success = optimize_sqlite(db_path, full_optimization)
                if success:
                    logger.info("SQLite optimization completed successfully")
                else:
                    logger.error("SQLite optimization failed")
                    sys.exit(1)
            else:
                logger.error(f"SQLite database file not found: {db_path}")
                sys.exit(1)
                
        elif CONFIG.DB_TYPE == 'mysql':
            success = optimize_mysql(CONFIG.DB_CONNECTION_STRING, full_optimization)
            if success:
                logger.info("MySQL optimization completed successfully")
            else:
                logger.error("MySQL optimization failed")
                sys.exit(1)
            
        else:
            logger.error(f"Unsupported database type: {CONFIG.DB_TYPE}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
