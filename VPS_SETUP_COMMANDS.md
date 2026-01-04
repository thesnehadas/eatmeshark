# VPS Setup Commands - Quick Reference

## Fix Virtual Environment Issue

If you get the error about `ensurepip` not being available, run:

```bash
apt update
apt install python3.12-venv python3-pip -y
```

Then recreate the virtual environment:
```bash
cd /var/www/shark-tank
rm -rf venv  # Remove failed venv if it exists
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Complete Setup Sequence

```bash
# 1. Update system and install dependencies
apt update
apt install python3 python3-pip python3.12-venv git nginx -y

# 2. Clone repository
cd /var/www
git clone https://github.com/thesnehadas/eatmeshark.git shark-tank
cd shark-tank

# 3. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# 5. Set permissions
chown -R www-data:www-data /var/www/shark-tank
chmod -R 755 /var/www/shark-tank
```

## Create Systemd Service

```bash
nano /etc/systemd/system/shark-tank.service
```

Paste:
```ini
[Unit]
Description=Shark Tank Intelligence Platform
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/shark-tank
Environment="PATH=/var/www/shark-tank/venv/bin"
ExecStart=/var/www/shark-tank/venv/bin/gunicorn --config /var/www/shark-tank/gunicorn_config.py api:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
systemctl daemon-reload
systemctl enable shark-tank
systemctl start shark-tank
systemctl status shark-tank
```

## Configure Nginx

```bash
nano /etc/nginx/sites-available/shark-tank
```

Paste:
```nginx
server {
    listen 80;
    server_name thesnehadas.com www.thesnehadas.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/shark-tank/static;
        expires 30d;
    }
}
```

Enable:
```bash
ln -s /etc/nginx/sites-available/shark-tank /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx
```

## SSL Setup (Optional)

```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d thesnehadas.com -d www.thesnehadas.com
```

