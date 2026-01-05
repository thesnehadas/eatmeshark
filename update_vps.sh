#!/bin/bash
# Quick update script - run this on VPS after code changes

cd /var/www/shark-tank
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
systemctl restart shark-tank
echo "Update complete! Check status with: systemctl status shark-tank"

