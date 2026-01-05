#!/bin/bash
# Quick fix for Nginx configuration

APP_DIR="/var/www/shark-tank"
SERVICE_NAME="shark-tank"
DOMAIN="thesnehadas.com"

echo "Updating Nginx configuration..."

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

    # Handle /eatmeshark without trailing slash
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

# Test and reload
nginx -t && systemctl reload nginx

echo "Nginx configuration updated!"
echo "Test at: http://$DOMAIN/eatmeshark/"

