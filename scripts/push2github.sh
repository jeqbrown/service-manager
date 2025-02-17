#!/bin/bash

# Ensure script exits on any error
set -e

# Create timestamp for branch name
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BRANCH_NAME="update_$TIMESTAMP"

# Ensure we're in the git repository root
if [ ! -d ".git" ]; then
    echo "Error: Must run from git repository root"
    exit 1
fi

# Create backup before making any changes
./backup_repo.sh

# Create and checkout new branch
echo "Creating new branch: $BRANCH_NAME"
git checkout -b "$BRANCH_NAME"

# Add all changes
echo "Adding changes..."
git add .

# Prompt for commit message
echo "Enter commit message:"
read -r COMMIT_MESSAGE

# Commit changes
echo "Committing changes..."
git commit -m "$COMMIT_MESSAGE"

# Push new branch to remote
echo "Pushing to GitHub..."
git push origin "$BRANCH_NAME"

echo "Complete! New branch '$BRANCH_NAME' has been pushed to GitHub."
echo "To merge these changes, create a pull request from '$BRANCH_NAME' to 'main'"