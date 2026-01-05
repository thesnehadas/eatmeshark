#!/bin/bash
# IMMEDIATE FIX - Run this on your VPS NOW

APP_DIR="/var/www/shark-tank"
SERVICE_NAME="shark-tank"
DOMAIN="thesnehadas.com"

echo "=========================================="
echo "FIXING NGINX CONFIGURATION"
echo "=========================================="

# Update Nginx config
cat > /etc/nginx/sites-available/$SERVICE_NAME << 'NGINX_EOF'
server {
    listen 80;
    server_name thesnehadas.com www.thesnehadas.com;

    # Redirect /eatmeshark to /eatmeshark/
    location = /eatmeshark {
        return 301 /eatmeshark/;
    }

    # Serve the app at /eatmeshark/
    location /eatmeshark/ {
        proxy_pass http://127.0.0.1:5000/eatmeshark/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Script-Name /eatmeshark;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files
    location /eatmeshark/static/ {
        alias /var/www/shark-tank/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
NGINX_EOF

# Test and reload Nginx
nginx -t && systemctl reload nginx

echo ""
echo "Nginx fixed! Now updating application..."

# Pull latest code
cd $APP_DIR
git pull origin main

# Restart service
systemctl restart $SERVICE_NAME

echo ""
echo "=========================================="
echo "FIX COMPLETE!"
echo "=========================================="
echo ""
echo "Test at: http://$DOMAIN/eatmeshark/"
echo ""
echo "Check service status:"
echo "  systemctl status $SERVICE_NAME"
echo ""
echo "Check logs if still not working:"
echo "  journalctl -u $SERVICE_NAME -n 50"
echo ""

