#!/usr/bin/env python3
"""
Database Backup Script for IFAM FastAPI Backend

This script creates backups of the database used by the IFAM FastAPI application.
It supports both SQLite and MySQL databases as configured in the application.

Usage:
    python backup_database.py [--output-dir /path/to/backup/dir]

Options:
    --output-dir    Directory where backups will be stored (default: ./backups)
"""

import os
import sys
import argparse
import shutil
import subprocess
import datetime
import logging
from pathlib import Path

# Add the parent directory to sys.path to import app modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('database_backup.log')
    ]
)
logger = logging.getLogger('database_backup')

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Backup the application database')
    parser.add_argument('--output-dir', default='./backups', 
                        help='Directory where backups will be stored')
    return parser.parse_args()

def ensure_backup_dir(backup_dir):
    """Ensure the backup directory exists."""
    os.makedirs(backup_dir, exist_ok=True)
    logger.info(f"Using backup directory: {backup_dir}")

def backup_sqlite(db_path, backup_dir):
    """Backup a SQLite database."""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"sqlite_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        # Simple file copy for SQLite
        shutil.copy2(db_path, backup_path)
        logger.info(f"SQLite database backed up to {backup_path}")
        
        # Create a compressed version
        compressed_path = f"{backup_path}.gz"
        subprocess.run(['gzip', '-c', backup_path], stdout=open(compressed_path, 'wb'), check=True)
        logger.info(f"Compressed backup created at {compressed_path}")
        
        # Remove the uncompressed backup to save space
        os.remove(backup_path)
        
        return compressed_path
    except Exception as e:
        logger.error(f"Failed to backup SQLite database: {e}")
        raise

def backup_mysql(connection_string, backup_dir):
    """Backup a MySQL database."""
    # Parse MySQL connection string
    # Format: mysql+pymysql://user:password@host:port/dbname
    try:
        # Extract MySQL connection details
        conn_parts = connection_string.replace('mysql+pymysql://', '').split('@')
        user_pass = conn_parts[0].split(':')
        host_db = conn_parts[1].split('/')
        
        user = user_pass[0]
        password = user_pass[1] if len(user_pass) > 1 else ''
        
        host_port = host_db[0].split(':')
        host = host_port[0]
        port = host_port[1] if len(host_port) > 1 else '3306'
        
        database = host_db[1]
        
        # Create backup filename
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"mysql_backup_{database}_{timestamp}.sql"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Use mysqldump to create backup
        cmd = [
            'mysqldump',
            f'--user={user}',
            f'--host={host}',
            f'--port={port}',
            '--single-transaction',
            '--routines',
            '--triggers',
            '--events',
            database
        ]
        
        if password:
            # Use environment variable for password to avoid it showing in process list
            env = os.environ.copy()
            env['MYSQL_PWD'] = password
            with open(backup_path, 'w') as f:
                subprocess.run(cmd, stdout=f, env=env, check=True)
        else:
            with open(backup_path, 'w') as f:
                subprocess.run(cmd, stdout=f, check=True)
        
        logger.info(f"MySQL database backed up to {backup_path}")
        
        # Compress the backup
        compressed_path = f"{backup_path}.gz"
        subprocess.run(['gzip', '-f', backup_path], check=True)
        logger.info(f"Compressed backup created at {compressed_path}")
        
        return compressed_path
    except Exception as e:
        logger.error(f"Failed to backup MySQL database: {e}")
        raise

def cleanup_old_backups(backup_dir, keep_days=30):
    """Remove backups older than specified days."""
    try:
        now = datetime.datetime.now()
        cutoff = now - datetime.timedelta(days=keep_days)
        
        for item in os.listdir(backup_dir):
            item_path = os.path.join(backup_dir, item)
            if os.path.isfile(item_path) and (item.startswith('sqlite_backup_') or item.startswith('mysql_backup_')):
                # Get file modification time
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(item_path))
                if mtime < cutoff:
                    os.remove(item_path)
                    logger.info(f"Removed old backup: {item_path}")
    except Exception as e:
        logger.error(f"Error during cleanup of old backups: {e}")

def main():
    """Main function to run the backup process."""
    args = parse_args()
    backup_dir = os.path.abspath(args.output_dir)
    ensure_backup_dir(backup_dir)
    
    try:
        if CONFIG.DB_TYPE == 'sqlite':
            # Extract SQLite database path from connection string
            # Format: sqlite:///path/to/db.sqlite
            db_path = CONFIG.DB_CONNECTION_STRING.replace('sqlite:///', '')
            if not os.path.isabs(db_path):
                # If path is relative, make it absolute from the project root
                db_path = os.path.join(Path(__file__).resolve().parent.parent, db_path)
            
            if os.path.exists(db_path):
                backup_path = backup_sqlite(db_path, backup_dir)
                logger.info(f"SQLite backup completed successfully: {backup_path}")
            else:
                logger.error(f"SQLite database file not found: {db_path}")
                sys.exit(1)
                
        elif CONFIG.DB_TYPE == 'mysql':
            backup_path = backup_mysql(CONFIG.DB_CONNECTION_STRING, backup_dir)
            logger.info(f"MySQL backup completed successfully: {backup_path}")
            
        else:
            logger.error(f"Unsupported database type: {CONFIG.DB_TYPE}")
            sys.exit(1)
            
        # Cleanup old backups
        cleanup_old_backups(backup_dir)
        
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
