#!/bin/bash

# Remove any existing Docker installations
apt-get remove -y docker docker-engine docker.io containerd runc

# Update and install prerequisites
apt-get update
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up the stable repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/docker/daemon.json > /dev/null

# Install Docker Engine
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create and switch to application directory
mkdir -p /opt/service_manager
cd /opt/service_manager

# Clean up any existing files
rm -rf *

# Generate SSH key for GitHub
ssh-keygen -t ed25519 -C "your-email@example.com" -f ~/.ssh/github_deploy_key -N ""

# Display the public key
echo "Add this public key to your GitHub repository's deploy keys:"
cat ~/.ssh/github_deploy_key.pub
echo -e "\nPress Enter after you've added the key to GitHub..."
read

# Configure SSH for GitHub
mkdir -p ~/.ssh
cat > ~/.ssh/config << EOL
Host github.com
    IdentityFile ~/.ssh/github_deploy_key
    StrictHostKeyChecking no
EOL

# Clone repository using SSH
git clone git@github.com:jeqbrown/service-manager.git .

# Get the Droplet's public IP
DROPLET_IP=$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address)

# Create environment file
cat > .env << EOL
POSTGRES_DB=service_manager
POSTGRES_USER=service_manager_user
POSTGRES_PASSWORD=$(openssl rand -base64 32)
POSTGRES_HOST=db
POSTGRES_PORT=5432

DEBUG=False
SECRET_KEY=$(openssl rand -base64 32)
ALLOWED_HOSTS=${DROPLET_IP}

DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=$(openssl rand -base64 16)
EOL

# Configure UFW to allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Start the application
docker-compose -f docker-compose.yml up -d
