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

# Add Docker's official GPG key (with force overwrite)
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg -f

# Set up the stable repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create and switch to application directory
mkdir -p /opt/service_manager
cd /opt/service_manager

# Backup existing .env if it exists
if [ -f .env ]; then
    echo "Backing up existing .env file..."
    cp .env ../temp_env
fi

# Clean directory and clone repository
rm -rf * .[!.]* ..?*
git clone git@github.com:jeqbrown/service-manager.git .

# Restore or create new .env file
if [ -f ../temp_env ]; then
    echo "Restoring existing .env file..."
    mv ../temp_env .env
else
    # Get the Droplet's public IP
    DROPLET_IP=$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address)

    # Create new environment file with random passwords
    cat > .env << EOL
POSTGRES_DB=service_manager
POSTGRES_USER=service_manager_user
POSTGRES_PASSWORD=$(openssl rand -base64 32)
POSTGRES_HOST=db
POSTGRES_PORT=5432

DEBUG=False
SECRET_KEY=$(openssl rand -base64 32)
ALLOWED_HOSTS=${DROPLET_IP},svcflo.com

DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=$(openssl rand -base64 16)
EOL
fi

# Configure UFW to allow HTTP/HTTPS (idempotent)
ufw allow 80/tcp
ufw allow 443/tcp

# Remove any existing containers and volumes
docker-compose down -v

# Start the application
docker-compose up -d --build

echo "Setup complete! The application should now be running."




