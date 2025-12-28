# Delivery Box - EC2 Deployment Guide

## 1. EC2 Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3-pip python3-venv nginx mysql-server git

# Start MySQL
sudo systemctl start mysql
sudo systemctl enable mysql
```

## 2. MySQL Database Setup
```bash
# Secure MySQL installation
sudo mysql_secure_installation

# Create database
sudo mysql -e "CREATE DATABASE delivery_box;"
sudo mysql -e "CREATE USER 'delivery_user'@'localhost' IDENTIFIED BY 'your_secure_password';"
sudo mysql -e "GRANT ALL PRIVILEGES ON delivery_box.* TO 'delivery_user'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"

# Import schema
sudo mysql delivery_box < /home/ubuntu/delivery-box/db/schema.sql
```

## 3. Clone and Setup Application
```bash
# Clone repository
cd /home/ubuntu
git clone <your-repo-url> delivery-box
cd delivery-box

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 4. Configure Environment Variables
```bash
# Create .env file
nano .env
```

Add the following:
```env
# Database
DB_HOST=localhost
DB_USER=delivery_user
DB_PASSWORD=your_secure_password
DB_NAME=delivery_box
DB_PORT=3306

# Security
SECRET_KEY=your-very-secure-random-secret-key
JWT_SECRET=your-very-secure-jwt-secret-key

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id

# PubNub
PUBNUB_PUBLISH_KEY=your-pubnub-publish-key
PUBNUB_SUBSCRIBE_KEY=your-pubnub-subscribe-key
PUBNUB_SECRET_KEY=your-pubnub-secret-key

# Environment
FLASK_ENV=production
```

## 5. Setup Systemd Service
```bash
# Create log directory
sudo mkdir -p /var/log/delivery-box
sudo chown ubuntu:www-data /var/log/delivery-box

# Copy service file
sudo cp delivery-box.service /etc/systemd/system/

# Reload systemd and start service
sudo systemctl daemon-reload
sudo systemctl start delivery-box
sudo systemctl enable delivery-box

# Check status
sudo systemctl status delivery-box
```

## 6. Setup Nginx
```bash
# Copy nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/delivery-box

# Update nginx.conf with your domain/IP
sudo nano /etc/nginx/sites-available/delivery-box
# Change: server_name your-domain.com www.your-domain.com;
# Change: alias /home/ubuntu/delivery-box/app/static;

# Enable site
sudo ln -s /etc/nginx/sites-available/delivery-box /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

## 7. Configure Security Groups (AWS Console)
- Allow HTTP (port 80)
- Allow HTTPS (port 443)
- Allow SSH (port 22) - restrict to your IP
- Allow MySQL (port 3306) - only if external access needed

## 8. Setup SSL with Let's Encrypt (Optional but Recommended)
```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal is configured automatically
# Test renewal
sudo certbot renew --dry-run
```

## 9. Useful Commands
```bash
# View application logs
sudo journalctl -u delivery-box -f

# Restart application
sudo systemctl restart delivery-box

# Restart nginx
sudo systemctl restart nginx

# View nginx logs
sudo tail -f /var/log/nginx/delivery-box-error.log
sudo tail -f /var/log/nginx/delivery-box-access.log

# Update application
cd /home/ubuntu/delivery-box
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart delivery-box
```

## 10. Security Checklist
- [ ] Changed all default passwords
- [ ] Generated strong SECRET_KEY and JWT_SECRET
- [ ] Configured firewall/security groups
- [ ] Enabled HTTPS with SSL certificate
- [ ] Set secure=True for cookies (already done)
- [ ] Restricted database access
- [ ] Regular system updates: `sudo apt update && sudo apt upgrade`
- [ ] Monitor logs regularly
- [ ] Backup database regularly

## Troubleshooting
```bash
# Check if app is running
ps aux | grep gunicorn

# Check ports
sudo netstat -tlnp | grep -E ':(80|443|8000)'

# Test database connection
mysql -u delivery_user -p delivery_box -e "SELECT 1;"

# Check disk space
df -h

# Check memory
free -h
```
