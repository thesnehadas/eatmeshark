#!/bin/bash
# Deployment script for Shark Tank Intelligence Platform

echo "=========================================="
echo "Shark Tank Intelligence - Deployment Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root${NC}"
    exit 1
fi

APP_DIR="/var/www/shark-tank"
SERVICE_NAME="shark-tank"

echo -e "${YELLOW}Step 1: Creating application directory...${NC}"
mkdir -p $APP_DIR
cd $APP_DIR

echo -e "${YELLOW}Step 2: Setting up Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

echo -e "${YELLOW}Step 3: Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

echo -e "${YELLOW}Step 4: Setting permissions...${NC}"
chown -R www-data:www-data $APP_DIR
chmod -R 755 $APP_DIR

echo -e "${YELLOW}Step 5: Creating systemd service...${NC}"
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Shark Tank Intelligence Platform
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --config $APP_DIR/gunicorn_config.py api:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo -e "${YELLOW}Step 6: Configuring Nginx...${NC}"
cat > /etc/nginx/sites-available/$SERVICE_NAME << EOF
server {
    listen 80;
    server_name thesnehadas.com www.thesnehadas.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias $APP_DIR/static;
        expires 30d;
    }
}
EOF

ln -sf /etc/nginx/sites-available/$SERVICE_NAME /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

echo -e "${YELLOW}Step 7: Testing Nginx configuration...${NC}"
nginx -t

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Nginx configuration is valid${NC}"
    systemctl reload nginx
else
    echo -e "${RED}Nginx configuration has errors!${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 8: Starting service...${NC}"
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME

echo -e "${YELLOW}Step 9: Checking service status...${NC}"
sleep 2
systemctl status $SERVICE_NAME --no-pager

echo -e "${GREEN}=========================================="
echo -e "Deployment Complete!"
echo -e "==========================================${NC}"
echo ""
echo "Your application should be available at:"
echo "  http://thesnehadas.com"
echo ""
echo "Useful commands:"
echo "  systemctl status $SERVICE_NAME    # Check status"
echo "  systemctl restart $SERVICE_NAME   # Restart service"
echo "  journalctl -u $SERVICE_NAME -f    # View logs"
echo ""
echo "Next steps:"
echo "  1. Set up SSL: certbot --nginx -d thesnehadas.com"
echo "  2. Configure firewall: ufw allow 80/tcp && ufw allow 443/tcp"

