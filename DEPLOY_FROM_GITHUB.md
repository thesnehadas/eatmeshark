# Deploy from GitHub to Hostinger VPS

This guide shows you how to deploy directly from GitHub, making updates much easier!

## 🚀 Setup (One-Time)

### Step 1: Push Your Code to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Shark Tank Intelligence Platform"

# Add your GitHub repository
git remote add origin https://github.com/YOUR_USERNAME/shark-tank-intelligence.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 2: Initial Setup on VPS

SSH into your VPS:
```bash
ssh root@62.72.57.117
```

Run these commands:
```bash
# Install Git (if not installed)
apt update && apt install git -y

# Create application directory
mkdir -p /var/www/shark-tank
cd /var/www/shark-tank

# Clone your repository
git clone https://github.com/YOUR_USERNAME/shark-tank-intelligence.git .

# Set up Python environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Set permissions
chown -R www-data:www-data /var/www/shark-tank
chmod -R 755 /var/www/shark-tank
```

### Step 3: Set Up Systemd Service

Create the service file:
```bash
nano /etc/systemd/system/shark-tank.service
```

Paste this:
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

Enable and start:
```bash
systemctl daemon-reload
systemctl enable shark-tank
systemctl start shark-tank
```

### Step 4: Configure Nginx

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

Enable and reload:
```bash
ln -s /etc/nginx/sites-available/shark-tank /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx
```

---

## 🔄 Deploying Updates (Two Methods)

### Method 1: Manual Deployment (Simple)

**On your VPS:**
```bash
cd /var/www/shark-tank
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
systemctl restart shark-tank
```

Or use the provided script:
```bash
chmod +x .github/workflows/deploy-manual.sh
.github/workflows/deploy-manual.sh
```

### Method 2: Automated with GitHub Actions (Advanced)

#### Setup GitHub Secrets

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Add these secrets:
   - `VPS_HOST`: `62.72.57.117`
   - `VPS_USER`: `root`
   - `VPS_SSH_KEY`: Your private SSH key (see below)
   - `VPS_PORT`: `22` (optional)

#### Generate SSH Key for GitHub Actions

**On your local machine:**
```bash
# Generate a new SSH key (or use existing)
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions

# Copy public key to VPS
ssh-copy-id -i ~/.ssh/github_actions.pub root@62.72.57.117

# Display private key (copy this to GitHub secret)
cat ~/.ssh/github_actions
```

**On Windows PowerShell:**
```powershell
# Generate key
ssh-keygen -t ed25519 -C "github-actions" -f $env:USERPROFILE\.ssh\github_actions

# Copy public key to VPS (you'll need to do this manually or use ssh-copy-id if available)
# Then display private key
Get-Content $env:USERPROFILE\.ssh\github_actions
```

#### How It Works

1. Push code to GitHub:
   ```bash
   git add .
   git commit -m "Update application"
   git push origin main
   ```

2. GitHub Actions automatically:
   - Connects to your VPS
   - Pulls latest code
   - Updates dependencies
   - Restarts the service

---

## 📝 Quick Reference

### Daily Workflow

```bash
# 1. Make changes locally
# 2. Commit and push
git add .
git commit -m "Your update message"
git push origin main

# 3. Deploy (choose one method):

# Method A: Manual (SSH into VPS)
ssh root@62.72.57.117
cd /var/www/shark-tank && git pull && systemctl restart shark-tank

# Method B: Automated (if GitHub Actions is set up)
# Just push - deployment happens automatically!
```

### Useful Commands

```bash
# Check service status
systemctl status shark-tank

# View logs
journalctl -u shark-tank -f

# Restart service
systemctl restart shark-tank

# Check if updates are available
cd /var/www/shark-tank
git fetch
git status
```

---

## 🔒 Security Best Practices

1. **Use SSH Keys**: Don't use passwords, use SSH keys
2. **Restrict SSH Access**: Only allow your IP if possible
3. **Use Non-Root User**: Create a dedicated user for deployment
4. **Enable Firewall**: `ufw enable` and only allow necessary ports
5. **Set Up SSL**: Use Let's Encrypt for HTTPS

---

## 🐛 Troubleshooting

**Git pull fails?**
```bash
# Check if you have uncommitted changes
git status

# Stash changes if needed
git stash
git pull
git stash pop
```

**Service won't restart?**
```bash
# Check logs
journalctl -u shark-tank -n 50

# Check if port is in use
netstat -tlnp | grep 5000
```

**Dependencies not updating?**
```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

---

## ✅ Benefits of GitHub Deployment

- ✅ **Version Control**: Track all changes
- ✅ **Easy Rollback**: `git revert` if something breaks
- ✅ **Collaboration**: Multiple people can contribute
- ✅ **Automation**: GitHub Actions can auto-deploy
- ✅ **Backup**: Code is safely stored on GitHub
- ✅ **History**: See what changed and when

---

## 🎯 Next Steps

1. Push your code to GitHub
2. Set up the VPS (one-time)
3. Use `git push` to deploy updates!

That's it! Much easier than manual file uploads. 🚀

