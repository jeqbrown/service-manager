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

# Handle existing installation
if [ -f .env ]; then
    echo "Existing installation detected. Preserving .env file..."
    mv .env ../temp_env
fi

# Clean up directory while preserving deploy key
if [ -f ~/.ssh/github_deploy_key ]; then
    echo "Existing GitHub deploy key found. Skipping key generation..."
else
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

    # Create new environment file
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
ufw enable

# Install Certbot for SSL certificates
apt-get install -y certbot python3-certbot-nginx

# Check if domain is pointing to this server
DOMAIN="svcflo.com"
SERVER_IP=$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address)
DOMAIN_IP=$(dig +short $DOMAIN)

echo "Server IP: $SERVER_IP"
echo "Domain IP: $DOMAIN_IP"

# Create a temporary Nginx config for domain validation
apt-get install -y nginx
cat > /etc/nginx/sites-available/default << EOL
server {
    listen 80;
    server_name $DOMAIN;
    location / {
        return 200 'Domain validation successful';
    }
}
EOL

# Reload Nginx to apply the temporary config
systemctl restart nginx

if [ "$SERVER_IP" = "$DOMAIN_IP" ]; then
    echo "Domain is correctly pointing to this server. Proceeding with SSL setup."
    
    # Stop nginx to free up port 80 for certbot
    systemctl stop nginx
    
    # Get SSL certificate
    certbot certonly --standalone -d $DOMAIN --non-interactive --agree-tos --email admin@example.com
    
    # Create directory for certificates in Docker volume
    mkdir -p /opt/service_manager/certs
    
    # Copy certificates to Docker volume
    cp -L /etc/letsencrypt/live/$DOMAIN/fullchain.pem /opt/service_manager/certs/
    cp -L /etc/letsencrypt/live/$DOMAIN/privkey.pem /opt/service_manager/certs/
    
    # Set proper permissions
    chmod 755 /opt/service_manager/certs
    chmod 644 /opt/service_manager/certs/*.pem
else
    echo "Warning: Domain $DOMAIN does not point to this server's IP ($SERVER_IP)."
    echo "SSL certificate will not be obtained. Please update DNS records and run the script again."
fi

# Stop any running containers
docker-compose down 2>/dev/null || true

# Modify docker-compose.yml to include SSL certificates
cat > docker-compose.override.yml << EOL
version: '3.8'

services:
  nginx:
    volumes:
      - /opt/service_manager/certs:/etc/letsencrypt/live/svcflo.com:ro
EOL

# Start the application
docker-compose -f docker-compose.yml up -d

echo "Setup complete! The application should now be running."
echo "If SSL certificates were obtained, the site should be accessible at https://$DOMAIN"
echo "Otherwise, it should be accessible at http://$DOMAIN or http://$SERVER_IP"

# Set up auto-renewal for SSL certificates
(crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet && cp -L /etc/letsencrypt/live/$DOMAIN/fullchain.pem /opt/service_manager/certs/ && cp -L /etc/letsencrypt/live/$DOMAIN/privkey.pem /opt/service_manager/certs/ && docker-compose -f /opt/service_manager/docker-compose.yml restart nginx") | crontab -




