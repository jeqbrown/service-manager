#!/bin/bash

# Script to set up React frontend for Service Manager

set -e  # Exit on any error

# Configuration
FRONTEND_DIR="frontend"

# Check if we're in the project root
if [ ! -f "manage.py" ]; then
    echo "Error: This script must be run from the project root directory."
    exit 1
fi

# Create frontend directory if it doesn't exist
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "Creating frontend directory..."
    mkdir -p "$FRONTEND_DIR"
fi

# Initialize React app
echo "Initializing React app..."
npx create-react-app "$FRONTEND_DIR" --template typescript

# Navigate to frontend directory
cd "$FRONTEND_DIR"

# Install additional dependencies
echo "Installing additional dependencies..."
npm install axios react-router-dom @headlessui/react @heroicons/react

# Update package.json for proxy configuration
echo "Configuring proxy for development..."
node -e "
const fs = require('fs');
const packageJson = JSON.parse(fs.readFileSync('package.json'));
packageJson.proxy = 'http://localhost:8000';
fs.writeFileSync('package.json', JSON.stringify(packageJson, null, 2));
"

echo "React setup complete! You can now start developing your frontend."
echo "To start the development server, run: cd $FRONTEND_DIR && npm start"