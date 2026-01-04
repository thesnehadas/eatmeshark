#!/bin/bash
# Quick setup script to initialize GitHub repository

echo "=========================================="
echo "GitHub Repository Setup"
echo "=========================================="

# Check if git is initialized
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
fi

# Add all files
echo "Adding files to git..."
git add .

# Check if there are changes
if git diff --staged --quiet; then
    echo "No changes to commit."
else
    echo "Creating initial commit..."
    git commit -m "Initial commit - Shark Tank Intelligence Platform"
fi

echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. Create a new repository on GitHub:"
echo "   https://github.com/new"
echo ""
echo "2. Add the remote and push:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/shark-tank-intelligence.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Follow DEPLOY_FROM_GITHUB.md for deployment instructions"
echo ""

