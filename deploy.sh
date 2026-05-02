#!/bin/bash
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Screener·US — Firebase Deploy Script"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Load nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Step 1: Check firebase CLI
if ! command -v firebase &> /dev/null; then
  echo "Installing Firebase CLI..."
  npm install -g firebase-tools
fi

echo ""
echo "Step 1: Login to Firebase (browser will open)..."
firebase login

echo ""
echo "Step 2: Deploying frontend to Firebase Hosting..."
cd "$(dirname "$0")"
firebase deploy --only hosting --project stock-market-research-platform

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Frontend deployed!"
echo ""
echo "  Your site is live at:"
echo "  https://stock-market-research-platform.web.app"
echo ""
echo "  ⚠️  NEXT STEP — Deploy the backend:"
echo "  1. Go to https://railway.app and sign up (free)"
echo "  2. Click 'New Project' → 'Deploy from GitHub repo'"
echo "     OR drag-drop the /backend folder"
echo "  3. Railway auto-detects the Dockerfile and deploys"
echo "  4. Copy your Railway URL (e.g. https://xxx.railway.app)"
echo "  5. Edit frontend/index.html — find this line:"
echo "     const API = window.BACKEND_URL || 'http://localhost:8000';"
echo "     Change it to:"
echo "     const API = 'https://YOUR-RAILWAY-URL.railway.app';"
echo "  6. Run this script again to redeploy the frontend"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
