#!/bin/bash
# StateOfForms Deployment Script
# Builds locally and deploys to DigitalOcean droplet

set -e

DROPLET_USER="root"
DROPLET_HOST="165.245.134.64"
DROPLET_PATH="/var/www/stateofforms"
SSH_KEY="~/.ssh/stateofforms_droplet"

echo "🏗️  Building StateOfForms..."
cd "$(dirname "$0")/.."

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Build the site
echo "🔨 Building Astro site..."
npm run build

# Check if build was successful
if [ ! -d "dist" ]; then
    echo "❌ Build failed - dist directory not found"
    exit 1
fi

echo "📤 Deploying to droplet..."

# Create backup on droplet
ssh -i $SSH_KEY $DROPLET_USER@$DROPLET_HOST "
    if [ -d $DROPLET_PATH ]; then
        echo '💾 Creating backup...'
        mv $DROPLET_PATH ${DROPLET_PATH}.backup.$(date +%Y%m%d_%H%M%S) || true
    fi
    mkdir -p $DROPLET_PATH
"

# Upload files
echo "📁 Uploading files..."
rsync -avz --delete -e "ssh -i $SSH_KEY" \
    ./dist/ \
    $DROPLET_USER@$DROPLET_HOST:$DROPLET_PATH/

# Set permissions
ssh -i $SSH_KEY $DROPLET_USER@$DROPLET_HOST "
    chown -R www-data:www-data $DROPLET_PATH
    chmod -R 755 $DROPLET_PATH
    echo '🔄 Reloading Nginx...'
    nginx -t && systemctl reload nginx
"

echo ""
echo "✅ Deployment complete!"
echo "🌐 Visit: https://stateofforms.com"
echo ""
