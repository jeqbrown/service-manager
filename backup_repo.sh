#!/bin/bash

# Create backup directory with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="../backups/service_manager_$TIMESTAMP"
BUNDLE_NAME="service_manager_$TIMESTAMP.bundle"

# Create backup directory
mkdir -p "../backups"

# Create Git bundle
git bundle create "../backups/$BUNDLE_NAME" --all

# Create full backup
mkdir -p "$BACKUP_DIR"
cp -r ./ "$BACKUP_DIR"

# Create compressed archive
tar -czf "$BACKUP_DIR.tar.gz" -C "$BACKUP_DIR" .

# Clean up temporary directory
rm -rf "$BACKUP_DIR"

echo "Backup completed:"
echo "1. Git bundle: ../backups/$BUNDLE_NAME"
echo "2. Full backup: $BACKUP_DIR.tar.gz"