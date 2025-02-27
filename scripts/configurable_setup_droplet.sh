#!/bin/bash

# Configurable setup script for deploying Django applications to a DigitalOcean droplet
# This script can be used for different projects by changing the configuration variables

# Configuration variables
REPO_URL=${REPO_URL:-"git@github.com:jeqbrown/service-manager.git"}
DOMAIN=${DOMAIN:-"svcflo.com"}
APP_DIR=${APP_DIR:-"/opt/service_manager"}
DB_NAME=${DB_NAME:-"service_manager"}
DB_USER=${DB_USER:-"service_manager_user"}
ADMIN_EMAIL=${ADMIN_EMAIL:-"admin@example.com"}
DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME:-"admin"}

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
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create and switch to application directory
mkdir -p ${APP_DIR}
cd ${APP_DIR}

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
    ssh-keygen -t ed25519 -C "${ADMIN_EMAIL}" -f ~/.ssh/github_deploy_key -N ""

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
git clone ${REPO_URL} .

# Restore or create new .env file
if [ -f ../temp_env ]; then
    echo "Restoring existing .env file..."
    mv ../temp_env .env
else
    # Get the Droplet's public IP
    DROPLET_IP=$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address)

    # Create new environment file
    cat > .env << EOL
POSTGRES_DB=${DB_NAME}
POSTGRES_USER=${DB_USER}
POSTGRES_PASSWORD=$(openssl rand -base64 32)
POSTGRES_HOST=db
POSTGRES_PORT=5432

DEBUG=False
SECRET_KEY=$(openssl rand -base64 32)
ALLOWED_HOSTS=${DROPLET_IP},${DOMAIN}

DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME}
DJANGO_SUPERUSER_EMAIL=${ADMIN_EMAIL}
DJANGO_SUPERUSER_PASSWORD=$(openssl rand -base64 16)
EOL
fi

# Configure UFW to allow HTTP/HTTPS (idempotent)
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Install Certbot for SSL certificates
apt-get install -y certbot python3-certbot-nginx

# Check if domain is pointing to this server
SERVER_IP=$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address)
DOMAIN_IP=$(dig +short ${DOMAIN})

echo "Server IP: $SERVER_IP"
echo "Domain IP: $DOMAIN_IP"

# Stop any running containers to free up ports
docker-compose down 2>/dev/null || true

# Create a temporary Nginx config for domain validation
apt-get install -y nginx
systemctl stop nginx

# Create nginx config file
cat > /etc/nginx/sites-available/default << EOL
server {
    listen 80;
    server_name ${DOMAIN};
    location / {
        return 200 'Domain validation successful';
    }
}
EOL

# Check if domain is pointing to this server
if [ "$SERVER_IP" = "$DOMAIN_IP" ]; then
    echo "Domain is correctly pointing to this server. Proceeding with SSL setup."
    
    # Get SSL certificate
    certbot certonly --standalone -d ${DOMAIN} --non-interactive --agree-tos --email ${ADMIN_EMAIL}
    
    # Create directory for certificates in Docker volume
    mkdir -p ${APP_DIR}/certs
    
    # Copy certificates to Docker volume
    cp -L /etc/letsencrypt/live/${DOMAIN}/fullchain.pem ${APP_DIR}/certs/
    cp -L /etc/letsencrypt/live/${DOMAIN}/privkey.pem ${APP_DIR}/certs/
    
    # Set proper permissions
    chmod 755 ${APP_DIR}/certs
    chmod 644 ${APP_DIR}/certs/*.pem
    
    # Create nginx.conf for production with SSL
    cat > ${APP_DIR}/nginx.conf << EOL
server {
    listen 80;
    server_name ${DOMAIN};
    return 301 https://${DOMAIN}\$request_uri;
}

server {
    listen 443 ssl;
    server_name ${DOMAIN};

    ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;

    location /static/ {
        alias /usr/share/nginx/static/;
    }

    location /media/ {
        alias /usr/share/nginx/media/;
    }

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL

    # Create docker-compose override for SSL
    cat > ${APP_DIR}/docker-compose.override.yml << EOL
version: '3.8'

services:
  nginx:
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ${APP_DIR}/certs:/etc/letsencrypt/live/${DOMAIN}:ro
    ports:
      - "80:80"
      - "443:443"
EOL

else
    echo "Warning: Domain ${DOMAIN} does not point to this server's IP ($SERVER_IP)."
    echo "SSL certificate will not be obtained. Please update DNS records and run the script again."
    
    # Create nginx.conf for HTTP only
    cat > ${APP_DIR}/nginx.conf << EOL
server {
    listen 80;
    server_name ${DOMAIN} $SERVER_IP;

    location /static/ {
        alias /usr/share/nginx/static/;
    }

    location /media/ {
        alias /usr/share/nginx/media/;
    }

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOL

    # Create docker-compose override for HTTP only
    cat > ${APP_DIR}/docker-compose.override.yml << EOL
version: '3.8'

services:
  nginx:
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    ports:
      - "80:80"
EOL
fi

# Start the application
docker-compose up -d

echo "Setup complete! The application should now be running."
echo "If SSL certificates were obtained, the site should be accessible at https://${DOMAIN}"
echo "Otherwise, it should be accessible at http://${DOMAIN} or http://$SERVER_IP"

# Set up auto-renewal for SSL certificates
(crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet && cp -L /etc/letsencrypt/live/${DOMAIN}/fullchain.pem ${APP_DIR}/certs/ && cp -L /etc/letsencrypt/live/${DOMAIN}/privkey.pem ${APP_DIR}/certs/ && docker-compose -f ${APP_DIR}/docker-compose.yml restart nginx") | crontab -

# Create a simple update script for future updates
cat > ${APP_DIR}/update.sh << EOL
#!/bin/bash

# Script to update the application with the latest changes
# without performing a full reinstall

set -e  # Exit on any error

# Configuration
APP_DIR="${APP_DIR}"

# Check if running as root
if [ "\$(id -u)" -ne 0 ]; then
    echo "Error: This script must be run as root."
    exit 1
fi

# Navigate to application directory
cd "\$APP_DIR"

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

chmod +x ${APP_DIR}/update.sh

echo ""
echo "Usage instructions for future deployments:"
echo "----------------------------------------"
echo "To deploy to a different project or domain, run this script with environment variables:"
echo ""
echo "REPO_URL=\"git@github.com:username/project.git\" \\"
echo "DOMAIN=\"example.com\" \\"
echo "APP_DIR=\"/opt/my-app\" \\"
echo "DB_NAME=\"mydb\" \\"
echo "DB_USER=\"myuser\" \\"
echo "ADMIN_EMAIL=\"admin@example.com\" \\"
echo "./configurable_setup_droplet.sh"
echo ""
echo "To update an existing deployment, run the update.sh script in your app directory:"
echo "cd ${APP_DIR} && ./update.sh"