#!/bin/bash
# Manual deployment script to run on VPS
# This pulls from GitHub and restarts the service

set -e

APP_DIR="/var/www/shark-tank"
BRANCH="main"  # or "master" depending on your default branch

echo "=========================================="
echo "Deploying from GitHub"
echo "=========================================="

cd $APP_DIR

echo "Pulling latest code from GitHub..."
git pull origin $BRANCH

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing/updating dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Setting permissions..."
chown -R www-data:www-data $APP_DIR
chmod -R 755 $APP_DIR

echo "Restarting service..."
systemctl restart shark-tank

echo "Checking service status..."
sleep 2
systemctl status shark-tank --no-pager

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="

