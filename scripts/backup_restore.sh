
#!/bin/bash

# Development Server Backup and Restore Script
# Supports: Projects, Databases, Configurations

BACKUP_DIR="/app/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

function backup() {
    echo "Starting backup process..."
    mkdir -p "$BACKUP_DIR/$TIMESTAMP"
    
    # Backup projects
    echo "Backing up projects..."
    tar -czf "$BACKUP_DIR/$TIMESTAMP/projects.tar.gz" -C /app projects
    
    # Backup database (PostgreSQL)
    echo "Backing up database..."
    PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > "$BACKUP_DIR/$TIMESTAMP/db_backup.sql"
    
    # Backup configurations
    echo "Backing up configurations..."
    tar -czf "$BACKUP_DIR/$TIMESTAMP/configs.tar.gz" -C /app configs
    
    echo "Backup completed. Files saved to: $BACKUP_DIR/$TIMESTAMP"
}

function restore() {
    if [ -z "$1" ]; then
        echo "Usage: $0 restore <backup_directory>"
        exit 1
    fi
    
    BACKUP_PATH="$1"
    echo "Starting restore from $BACKUP_PATH..."
    
    # Restore projects
    echo "Restoring projects..."
    rm -rf /app/projects/*
    tar -xzf "$BACKUP_PATH/projects.tar.gz" -C /app
    
    # Restore database
    echo "Restoring database..."
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$BACKUP_PATH/db_backup.sql"
    
    # Restore configurations
    echo "Restoring configurations..."
    rm -rf /app/configs/*
    tar -xzf "$BACKUP_PATH/configs.tar.gz" -C /app
    
    echo "Restore completed from $BACKUP_PATH"
}

case "$1" in
    backup)
        backup
        ;;
    restore)
        restore "$2"
        ;;
    *)
        echo "Usage: $0 {backup|restore <backup_directory>}"
        exit 1
esac
