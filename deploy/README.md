# StateOfForms Deployment Guide

## Initial Setup (One Time)

### 1. Run Setup Script on Droplet

SSH into your droplet and run the setup script:

```bash
# From your local machine
ssh stateofforms

# On the droplet
cd /root
```

Upload the setup script:

```bash
# From your local machine in the stateofforms directory
scp deploy/setup-droplet.sh stateofforms:/root/
ssh stateofforms "chmod +x /root/setup-droplet.sh && /root/setup-droplet.sh"
```

This will install:
- Nginx web server
- Node.js
- Certbot (for SSL)
- Configure firewall
- Set up Nginx configuration

### 2. Setup SSL Certificate

After DNS has propagated (wait 5-60 minutes after updating GoDaddy), run:

```bash
ssh stateofforms
certbot --nginx -d stateofforms.com -d www.stateofforms.com
```

Follow the prompts:
- Enter your email
- Agree to terms
- Choose to redirect HTTP to HTTPS (recommended)

Certbot will automatically renew certificates before they expire.

### 3. Update QueryForge CORS Settings

Before deploying, make sure QueryForge allows requests from your domain.

On your QueryForge server, update the CORS settings to include:
```python
CORS_ALLOWED_ORIGINS = [
    "https://stateofforms.com",
    "https://www.stateofforms.com",
    "http://localhost:4321",  # Keep for local dev
]
```

Push these changes to QueryForge production.

## Deploying Updates

### Quick Deploy

From your local stateofforms directory:

```bash
cd ~/Documents/stateofforms
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

This will:
1. Build the Astro site locally
2. Create a backup on the droplet
3. Upload the new files
4. Reload Nginx

### Manual Deploy

```bash
# Build locally
npm run build

# Upload to droplet
rsync -avz --delete -e "ssh -i ~/.ssh/stateofforms_droplet" \
    ./dist/ \
    root@165.245.134.64:/var/www/stateofforms/

# Set permissions
ssh stateofforms "chown -R www-data:www-data /var/www/stateofforms && systemctl reload nginx"
```

## Droplet Information

- **IP:** 165.245.134.64
- **Domain:** stateofforms.com
- **Web Root:** /var/www/stateofforms
- **SSH Alias:** `ssh stateofforms`
- **Nginx Config:** /etc/nginx/sites-available/stateofforms

## Useful Commands

```bash
# Check Nginx status
ssh stateofforms "systemctl status nginx"

# View Nginx error logs
ssh stateofforms "tail -f /var/log/nginx/error.log"

# View Nginx access logs
ssh stateofforms "tail -f /var/log/nginx/access.log"

# Test Nginx configuration
ssh stateofforms "nginx -t"

# Reload Nginx
ssh stateofforms "systemctl reload nginx"

# Check SSL certificate status
ssh stateofforms "certbot certificates"

# Test SSL renewal (dry run)
ssh stateofforms "certbot renew --dry-run"
```

## Troubleshooting

### Site not loading
1. Check Nginx is running: `ssh stateofforms "systemctl status nginx"`
2. Check files exist: `ssh stateofforms "ls -la /var/www/stateofforms"`
3. Check logs: `ssh stateofforms "tail /var/log/nginx/error.log"`

### SSL certificate issues
1. Verify DNS is pointing to droplet: `dig stateofforms.com`
2. Check certificate status: `ssh stateofforms "certbot certificates"`
3. Try manual renewal: `ssh stateofforms "certbot renew"`

### API calls failing
1. Check browser console for CORS errors
2. Verify QueryForge CORS settings include stateofforms.com
3. Test API directly: `curl https://queryforge.ai/api/stock/AAPL?limit=1`

## CI/CD with GitHub Actions

The GitHub Actions workflow in `.github/workflows/deploy.yml` can be updated to deploy to your droplet instead of GitHub Pages.

See `.github/workflows/deploy-droplet.yml.example` for reference.
