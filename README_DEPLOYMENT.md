# 🚀 Deployment Guide - Quick Start

## Deploy from GitHub (Recommended)

### 1. Push to GitHub
```bash
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/shark-tank-intelligence.git
git push -u origin main
```

### 2. Initial VPS Setup (One-Time)
```bash
ssh root@62.72.57.117
cd /var/www
git clone https://github.com/YOUR_USERNAME/shark-tank-intelligence.git shark-tank
cd shark-tank
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Deploy Updates
```bash
# On VPS
cd /var/www/shark-tank
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
systemctl restart shark-tank
```

**Full guide:** See `DEPLOY_FROM_GITHUB.md`

---

## Manual Deployment

See `DEPLOYMENT.md` for detailed manual deployment steps.

---

## Quick Deploy Script

See `QUICK_DEPLOY.md` for the fastest deployment method.

