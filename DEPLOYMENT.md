# Deployment Guide for Hostinger VPS

This guide will help you deploy the Shark Tank Intelligence Platform to your Hostinger VPS at `thesnehadas.com`.

## Prerequisites

- SSH access to your Hostinger VPS
- Domain `thesnehadas.com` pointing to your VPS IP: `62.72.57.117`
- Python 3.8+ installed on the VPS

## Step 1: Connect to Your VPS

```bash
ssh root@62.72.57.117
# Or use your Hostinger VPS credentials
```

## Step 2: Install Required Software

```bash
# Update system
apt update && apt upgrade -y

# Install Python and pip (if not already installed)
apt install python3 python3-pip python3-venv -y

# Install Nginx (web server/reverse proxy)
apt install nginx -y

# Install Git (to clone or upload your code)
apt install git -y
```

## Step 3: Upload Your Application

### Option A: Using Git (Recommended)
```bash
# Create application directory
mkdir -p /var/www/shark-tank
cd /var/www/shark-tank

# Clone your repository (if using Git)
# git clone <your-repo-url> .

# Or upload files via SFTP/SCP from your local machine
```

### Option B: Using SCP from Local Machine
From your local machine (Windows PowerShell):
```powershell
# Navigate to your project directory
cd C:\Users\ASUS\Downloads\shark-tank-deal-predictor

# Upload files to VPS
scp -r * root@62.72.57.117:/var/www/shark-tank/
```

## Step 4: Set Up Python Environment

```bash
cd /var/www/shark-tank

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn  # Production WSGI server
```

## Step 5: Configure Gunicorn

Create a Gunicorn configuration file:

```bash
nano /var/www/shark-tank/gunicorn_config.py
```

Add this content:
```python
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
timeout = 120
keepalive = 5
user = "www-data"
group = "www-data"
```

## Step 6: Create Systemd Service

Create a systemd service file to run the application:

```bash
nano /etc/systemd/system/shark-tank.service
```

Add this content:
```ini
[Unit]
Description=Shark Tank Intelligence Platform
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/shark-tank
Environment="PATH=/var/www/shark-tank/venv/bin"
ExecStart=/var/www/shark-tank/venv/bin/gunicorn --config gunicorn_config.py api:app
Restart=always

[Install]
WantedBy=multi-user.target
```

## Step 7: Configure Nginx

Create Nginx configuration:

```bash
nano /etc/nginx/sites-available/shark-tank
```

Add this content:
```nginx
server {
    listen 80;
    server_name thesnehadas.com www.thesnehadas.com;

    # Redirect HTTP to HTTPS (after SSL setup)
    # return 301 https://$server_name$request_uri;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files
    location /static {
        alias /var/www/shark-tank/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable the site:
```bash
ln -s /etc/nginx/sites-available/shark-tank /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default  # Remove default site if exists
nginx -t  # Test configuration
systemctl reload nginx
```

## Step 8: Set Up SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get SSL certificate
certbot --nginx -d thesnehadas.com -d www.thesnehadas.com

# Auto-renewal is set up automatically
```

## Step 9: Set Permissions

```bash
# Set ownership
chown -R www-data:www-data /var/www/shark-tank

# Set permissions
chmod -R 755 /var/www/shark-tank
```

## Step 10: Start the Service

```bash
# Start and enable the service
systemctl daemon-reload
systemctl start shark-tank
systemctl enable shark-tank

# Check status
systemctl status shark-tank

# View logs
journalctl -u shark-tank -f
```

## Step 11: Configure Firewall

```bash
# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp  # SSH
ufw enable
```

## Step 12: Verify Deployment

1. Open your browser and visit: `http://thesnehadas.com` (or `https://thesnehadas.com` after SSL)
2. Test the API: `http://thesnehadas.com/api/health`
3. Check if predictions work

## Troubleshooting

### Check Application Logs
```bash
journalctl -u shark-tank -n 50
```

### Check Nginx Logs
```bash
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

### Restart Services
```bash
systemctl restart shark-tank
systemctl restart nginx
```

### Check if Port 5000 is Listening
```bash
netstat -tlnp | grep 5000
```

## Updating the Application

When you make changes:

```bash
cd /var/www/shark-tank
source venv/bin/activate
git pull  # If using Git
# Or upload new files via SCP

# Install new dependencies if needed
pip install -r requirements.txt

# Restart the service
systemctl restart shark-tank
```

## Important Notes

1. **Models**: Make sure all trained models are uploaded to `/var/www/shark-tank/models/`
2. **Data**: Upload datasets if needed (though they're only needed for training)
3. **Environment Variables**: Create a `.env` file if you need environment variables
4. **Backup**: Regularly backup your models and configuration

## Quick Commands Reference

```bash
# Start service
systemctl start shark-tank

# Stop service
systemctl stop shark-tank

# Restart service
systemctl restart shark-tank

# View logs
journalctl -u shark-tank -f

# Check status
systemctl status shark-tank
```

