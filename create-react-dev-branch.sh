#!/bin/bash

# Script to create a development branch for React restructuring

set -e  # Exit on any error

# Configuration
MAIN_BRANCH="main"
DEV_BRANCH="react-restructure"

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

# Switch to main branch if not already on it
if [ "$CURRENT_BRANCH" != "$MAIN_BRANCH" ]; then
    echo "Switching to $MAIN_BRANCH branch..."
    git checkout $MAIN_BRANCH
fi

# Pull latest changes from main
echo "Pulling latest changes from $MAIN_BRANCH..."
git pull origin $MAIN_BRANCH

# Create new development branch
echo "Creating new development branch: $DEV_BRANCH..."
git checkout -b $DEV_BRANCH

# Push the new branch to remote
echo "Pushing $DEV_BRANCH to remote..."
git push -u origin $DEV_BRANCH

echo "Development branch $DEV_BRANCH created successfully!"
echo "You are now on branch: $DEV_BRANCH"