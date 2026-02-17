#!/bin/bash
# StateOfForms Droplet Initial Setup Script
# Run this once on a fresh Ubuntu droplet

set -e

echo "🚀 Starting StateOfForms Droplet Setup..."

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install essential packages
echo "📦 Installing essential packages..."
apt install -y nginx certbot python3-certbot-nginx git curl ufw

# Install Node.js 20.x
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Verify installations
echo "✅ Verifying installations..."
nginx -v
node -v
npm -v

# Configure firewall
echo "🔒 Configuring firewall..."
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

# Create web directory
echo "📁 Creating web directory..."
mkdir -p /var/www/stateofforms
chown -R www-data:www-data /var/www/stateofforms

# Copy nginx configuration
echo "🌐 Setting up Nginx..."
cat > /etc/nginx/sites-available/stateofforms << 'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name stateofforms.com www.stateofforms.com;

    root /var/www/stateofforms;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript application/json image/svg+xml;

    # Cache static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Main location
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/stateofforms /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx config
nginx -t

# Restart nginx
systemctl restart nginx
systemctl enable nginx

echo ""
echo "✅ Droplet setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Deploy your site: ./deploy.sh"
echo "  2. Setup SSL: certbot --nginx -d stateofforms.com -d www.stateofforms.com"
echo ""
echo "🌐 Your droplet is ready at: http://165.245.134.64"
