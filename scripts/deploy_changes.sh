#!/bin/bash

# Script to package and deploy local changes to GitHub
# Ensures compatibility between local development and production environments

set -e  # Exit on any error

# Configuration
REPO_URL="git@github.com:jeqbrown/service-manager.git"
MAIN_BRANCH="main"
BACKUP_BRANCH="backup-$(date +%Y%m%d-%H%M%S)"
LOCAL_ENV_FILE=".env"
EXAMPLE_ENV_FILE=".env.example"

# Check if we're in the project root (where manage.py is)
if [ ! -f "manage.py" ]; then
    echo "Error: This script must be run from the project root directory."
    exit 1
fi

# Ensure git is installed
if ! command -v git &> /dev/null; then
    echo "Error: git is not installed. Please install git first."
    exit 1
fi

# Check git status
if [ -n "$(git status --porcelain)" ]; then
    echo "Local changes detected. Proceeding with deployment process..."
else
    echo "No local changes detected. Nothing to deploy."
    exit 0
fi

# Create backup of current .env file if it exists
if [ -f "$LOCAL_ENV_FILE" ]; then
    echo "Backing up local .env file..."
    cp "$LOCAL_ENV_FILE" "${LOCAL_ENV_FILE}.backup"
fi

# Ensure .env.example is up to date but doesn't contain sensitive information
echo "Updating .env.example file..."
if [ -f "$LOCAL_ENV_FILE" ]; then
    # Extract keys from .env but use placeholder values
    grep -v "^#" "$LOCAL_ENV_FILE" | sed 's/=.*/=your_value_here/' > "$EXAMPLE_ENV_FILE"
    echo "Updated $EXAMPLE_ENV_FILE with current environment variables (values replaced with placeholders)."
else
    echo "Warning: No $LOCAL_ENV_FILE found. $EXAMPLE_ENV_FILE may be outdated."
fi

# Check for any development-specific settings that shouldn't be pushed
echo "Checking for development-specific settings..."

# Ensure DEBUG is set to False in settings.py for production
if grep -q "DEBUG = True" service_manager/settings.py; then
    echo "Warning: DEBUG is set to True in settings.py."
    read -p "Would you like to set DEBUG to False for production? (y/n): " answer
    if [[ "$answer" == "y" ]]; then
        sed -i 's/DEBUG = True/DEBUG = os.getenv("DEBUG", "False") == "True"/' service_manager/settings.py
        echo "DEBUG setting updated to use environment variable."
    fi
fi

# Offer to create a script to update the droplet without a full reinstall
read -p "Would you like to create or update the update_droplet.sh script for easy droplet updates? (y/n): " create_update_script
if [[ "$create_update_script" == "y" ]]; then
    cat > scripts/update_droplet.sh << 'EOL'
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
EOL
    chmod +x scripts/update_droplet.sh
    echo "Created scripts/update_droplet.sh for easy droplet updates."
    
    # Ask if the update script should be included in the commit
    read -p "Would you like to include the update_droplet.sh script in your commit? (y/n): " include_update_script
    if [[ "$include_update_script" == "y" ]]; then
        echo "The update_droplet.sh script will be included in your commit."
    else
        echo "The update_droplet.sh script will be excluded from your commit."
        # Add to gitignore temporarily to exclude from this commit
        echo "scripts/update_droplet.sh" >> .gitignore_temp
    fi
fi

# Create a new branch for the changes
echo "Creating backup branch: $BACKUP_BRANCH"
git checkout -b "$BACKUP_BRANCH"

# Add all changes
git add .

# Exclude .env files from being committed
git reset -- "$LOCAL_ENV_FILE" "${LOCAL_ENV_FILE}.*"
git reset -- "*.pyc" "__pycache__/" "db.sqlite3"

# Exclude update_droplet.sh if user chose not to include it
if [[ -f ".gitignore_temp" ]]; then
    git reset -- scripts/update_droplet.sh
    rm .gitignore_temp
fi

# Force add .env.example if it was modified
git add -f "$EXAMPLE_ENV_FILE"

# Commit changes
echo "Committing changes..."
read -p "Enter commit message: " commit_message
git commit -m "$commit_message"

# Push backup branch to remote
echo "Pushing backup branch to remote..."
git push -u origin "$BACKUP_BRANCH"

# Switch back to main branch
echo "Switching to main branch..."
git checkout "$MAIN_BRANCH"
git pull origin "$MAIN_BRANCH"

# Merge changes from backup branch
echo "Merging changes from backup branch..."
git merge "$BACKUP_BRANCH"

# Push to main
echo "Pushing changes to main branch..."
git push origin "$MAIN_BRANCH"

# Clean up backup branch after successful merge
echo "Cleaning up backup branch..."
git branch -d "$BACKUP_BRANCH"
git push origin --delete "$BACKUP_BRANCH"

# Restore local .env file if it was backed up
if [ -f "${LOCAL_ENV_FILE}.backup" ]; then
    echo "Restoring local .env file..."
    mv "${LOCAL_ENV_FILE}.backup" "$LOCAL_ENV_FILE"
fi

# Server deployment section
echo "Would you like to deploy changes to your server? (y/n): "
read deploy_to_server
if [[ "$deploy_to_server" == "y" ]]; then
    read -p "Enter your server IP or hostname: " server_ip
    read -p "Enter the SSH username (default: root): " ssh_user
    ssh_user=${ssh_user:-root}
    
    # Transfer scripts to server
    echo "Transferring scripts to ${ssh_user}@${server_ip}..."
    scp scripts/setup_droplet.sh ${ssh_user}@${server_ip}:/root/
    scp scripts/update_droplet.sh ${ssh_user}@${server_ip}:/root/
    
    echo "Making scripts executable on the server..."
    ssh ${ssh_user}@${server_ip} "chmod +x /root/setup_droplet.sh /root/update_droplet.sh"
    
    # Ask which deployment method to use
    echo "How would you like to deploy to the server?"
    echo "1) Run update_droplet.sh (quick update, preserves data)"
    echo "2) Run setup_droplet.sh (full reinstall, may reset data)"
    echo "3) Don't run any scripts (manual deployment later)"
    read -p "Enter your choice (1-3): " deployment_choice
    
    case $deployment_choice in
        1)
            echo "Running update script on server..."
            ssh ${ssh_user}@${server_ip} "cd /root && ./update_droplet.sh"
            echo "Update completed successfully!"
            ;;
        2)
            echo "WARNING: Running setup script will perform a full reinstall."
            read -p "Are you sure you want to continue? (y/n): " confirm_setup
            if [[ "$confirm_setup" == "y" ]]; then
                echo "Running setup script on server..."
                ssh ${ssh_user}@${server_ip} "cd /root && ./setup_droplet.sh"
                echo "Setup completed successfully!"
            else
                echo "Setup cancelled."
            fi
            ;;
        3)
            echo "Scripts transferred to server but not executed."
            echo "You can run them manually by SSH'ing into the server and running:"
            echo "  cd /root && ./update_droplet.sh"
            echo "  or"
            echo "  cd /root && ./setup_droplet.sh"
            ;;
        *)
            echo "Invalid choice. Scripts transferred but not executed."
            ;;
    esac
    
    echo "Scripts transferred successfully to /root/ directory on your server."
else
    echo "Changes pushed to GitHub but not deployed to server."
fi

echo "Deployment process complete!"
echo ""
echo "Summary of actions:"
echo "- Changes committed and pushed to GitHub"
echo "- Backup branch created and cleaned up"
if [[ "$deploy_to_server" == "y" ]]; then
    echo "- Scripts transferred to server"
    case $deployment_choice in
        1) echo "- Update script executed on server" ;;
        2) 
            if [[ "$confirm_setup" == "y" ]]; then
                echo "- Setup script executed on server"
            else
                echo "- Setup script transferred but not executed"
            fi
            ;;
        3) echo "- No scripts executed on server" ;;
    esac
fi
