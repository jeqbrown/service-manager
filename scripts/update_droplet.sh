#!/bin/bash

# Script to update the DigitalOcean droplet with the latest changes
# without performing a full reinstall

set -e  # Exit on any error

# Configuration
APP_DIR="/opt/service_manager"

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "Error: This script must be run as root."
    exit 1
fi

# Navigate to application directory
cd "$APP_DIR"

# Backup current .env file
if [ -f .env ]; then
    echo "Backing up existing .env file..."
    cp .env .env.backup
fi

# Pull latest changes
echo "Pulling latest changes from GitHub..."
git pull

# Restore .env file
if [ -f .env.backup ]; then
    echo "Restoring .env file..."
    mv .env.backup .env
fi

# Restart containers with the updated code
echo "Restarting Docker containers..."
docker-compose down
docker-compose up -d

echo "Update complete! The application should now be running with the latest changes."
