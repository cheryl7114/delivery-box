cd /var/www/delivery-box
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
sudo systemctl restart delivery-box
