#!/bin/bash
# Automated deployment script for Shark Tank Intelligence Platform
# Run this script on your VPS: bash auto_deploy.sh

set -e  # Exit on error

echo "=========================================="
echo "Shark Tank Intelligence - Auto Deployment"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/var/www/shark-tank"
REPO_URL="https://github.com/thesnehadas/eatmeshark.git"
SERVICE_NAME="shark-tank"
DOMAIN="thesnehadas.com"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Updating system and installing dependencies...${NC}"
apt update
apt install -y python3 python3-pip python3.12-venv git nginx

echo -e "${YELLOW}Step 2: Setting up application directory...${NC}"
mkdir -p $APP_DIR
cd $APP_DIR

# Clone or update repository
if [ -d ".git" ]; then
    echo "Repository exists, pulling latest changes..."
    git pull origin main || git pull origin master
else
    echo "Cloning repository..."
    git clone $REPO_URL .
fi

echo -e "${YELLOW}Step 3: Creating Python virtual environment...${NC}"
# Remove existing venv if it exists and failed
if [ -d "venv" ] && [ ! -f "venv/bin/python3" ]; then
    echo "Removing broken virtual environment..."
    rm -rf venv
fi

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

echo -e "${YELLOW}Step 4: Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${YELLOW}Step 5: Setting permissions...${NC}"
chown -R www-data:www-data $APP_DIR
chmod -R 755 $APP_DIR

echo -e "${YELLOW}Step 6: Creating systemd service...${NC}"
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Shark Tank Intelligence Platform
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
Environment="BASE_PATH=/eatmeshark"
ExecStart=$APP_DIR/venv/bin/gunicorn --config $APP_DIR/gunicorn_config.py api:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${YELLOW}Step 7: Configuring Nginx...${NC}"
cat > /etc/nginx/sites-available/$SERVICE_NAME << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    # Serve the app at /eatmeshark
    location /eatmeshark/ {
        proxy_pass http://127.0.0.1:5000/eatmeshark/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Script-Name /eatmeshark;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Redirect /eatmeshark to /eatmeshark/
    location = /eatmeshark {
        return 301 /eatmeshark/;
    }

    # Static files
    location /eatmeshark/static/ {
        alias $APP_DIR/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/$SERVICE_NAME /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
echo -e "${YELLOW}Step 8: Testing Nginx configuration...${NC}"
if nginx -t; then
    echo -e "${GREEN}Nginx configuration is valid${NC}"
    systemctl reload nginx
else
    echo -e "${RED}Nginx configuration has errors!${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 9: Starting services...${NC}"
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl restart $SERVICE_NAME

# Wait a moment for service to start
sleep 3

echo -e "${YELLOW}Step 10: Checking service status...${NC}"
if systemctl is-active --quiet $SERVICE_NAME; then
    echo -e "${GREEN}Service is running!${NC}"
else
    echo -e "${RED}Service failed to start. Checking logs...${NC}"
    journalctl -u $SERVICE_NAME -n 20 --no-pager
    exit 1
fi

echo ""
echo -e "${GREEN}=========================================="
echo -e "Deployment Complete! 🎉"
echo -e "==========================================${NC}"
echo ""
echo "Your application is now available at:"
echo -e "  ${GREEN}http://$DOMAIN${NC}"
echo ""
echo "Useful commands:"
echo "  systemctl status $SERVICE_NAME    # Check status"
echo "  systemctl restart $SERVICE_NAME    # Restart service"
echo "  journalctl -u $SERVICE_NAME -f    # View logs"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Set up SSL: certbot --nginx -d $DOMAIN -d www.$DOMAIN"
echo "  2. Configure firewall: ufw allow 80/tcp && ufw allow 443/tcp"
echo ""

