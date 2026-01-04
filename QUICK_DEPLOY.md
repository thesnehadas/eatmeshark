# Quick Deployment Guide for thesnehadas.com

## 🚀 Fastest Way to Deploy

### Step 1: Upload Files to VPS

**Option A: Using PowerShell Script (Windows)**
```powershell
# Run from your project directory
.\upload_to_vps.ps1
```

**Option B: Manual Upload via SCP**
```powershell
# From your project directory
scp -r * root@62.72.57.117:/var/www/shark-tank/
```

**Option C: Using SFTP Client**
- Use FileZilla, WinSCP, or similar
- Connect to: `62.72.57.117`
- Upload all files to: `/var/www/shark-tank/`

### Step 2: SSH into Your VPS

```bash
ssh root@62.72.57.117
```

### Step 3: Run Deployment Script

```bash
cd /var/www/shark-tank
chmod +x deploy.sh
bash deploy.sh
```

### Step 4: Set Up SSL (Optional but Recommended)

```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d thesnehadas.com -d www.thesnehadas.com
```

### Step 5: Verify

Visit: **http://thesnehadas.com** (or https:// after SSL)

---

## 📋 Manual Steps (If Script Fails)

### 1. Install Dependencies
```bash
apt update
apt install python3 python3-pip python3-venv nginx -y
```

### 2. Set Up Python Environment
```bash
cd /var/www/shark-tank
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Create Systemd Service
```bash
nano /etc/systemd/system/shark-tank.service
```
Paste the service file content from `DEPLOYMENT.md`

### 4. Configure Nginx
```bash
nano /etc/nginx/sites-available/shark-tank
```
Paste the nginx config from `DEPLOYMENT.md`

### 5. Start Services
```bash
systemctl daemon-reload
systemctl enable shark-tank
systemctl start shark-tank
systemctl reload nginx
```

---

## 🔧 Troubleshooting

**Service won't start?**
```bash
journalctl -u shark-tank -n 50
```

**Nginx errors?**
```bash
nginx -t
tail -f /var/log/nginx/error.log
```

**Can't access the site?**
- Check firewall: `ufw allow 80/tcp && ufw allow 443/tcp`
- Check service: `systemctl status shark-tank`
- Check port: `netstat -tlnp | grep 5000`

---

## 📝 Important Files to Upload

Make sure these are uploaded:
- ✅ `api.py` - Flask application
- ✅ `requirements.txt` - Dependencies
- ✅ `gunicorn_config.py` - Gunicorn config
- ✅ `src/` - Source code directory
- ✅ `templates/` - HTML templates
- ✅ `static/` - CSS/JS files
- ✅ `models/` - Trained ML models (IMPORTANT!)

---

## 🎯 After Deployment

Your app will be live at:
- **http://thesnehadas.com**
- **https://thesnehadas.com** (after SSL setup)

API endpoints:
- `http://thesnehadas.com/api/health`
- `http://thesnehadas.com/api/countries`

