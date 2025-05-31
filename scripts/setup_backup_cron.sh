#!/bin/bash
# Setup cron job for database backups
# This script sets up a daily cron job to backup the database

# Get the absolute path to the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_SCRIPT="$PROJECT_DIR/scripts/backup_database.py"
BACKUP_DIR="$PROJECT_DIR/backups"

# Make the backup script executable
chmod +x "$BACKUP_SCRIPT"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create a temporary file for the crontab
TEMP_CRON=$(mktemp)

# Export current crontab
crontab -l > "$TEMP_CRON" 2>/dev/null || echo "# New crontab" > "$TEMP_CRON"

# Check if the backup job already exists
if ! grep -q "$BACKUP_SCRIPT" "$TEMP_CRON"; then
    # Add the backup job to run daily at 2:00 AM
    echo "# IFAM FastAPI Database Backup - Daily at 2:00 AM" >> "$TEMP_CRON"
    echo "0 2 * * * cd $PROJECT_DIR && $BACKUP_SCRIPT --output-dir $BACKUP_DIR >> $PROJECT_DIR/logs/backup.log 2>&1" >> "$TEMP_CRON"
    
    # Install the new crontab
    crontab "$TEMP_CRON"
    echo "Cron job installed successfully."
else
    echo "Backup cron job already exists."
fi

# Clean up the temporary file
rm "$TEMP_CRON"

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_DIR/logs"

echo "Backup system setup complete."
echo "Backups will be stored in: $BACKUP_DIR"
echo "Logs will be stored in: $PROJECT_DIR/logs/backup.log"
echo ""
echo "To run a backup manually, execute:"
echo "python $BACKUP_SCRIPT --output-dir $BACKUP_DIR"
