# RedLink Hosting & Production Deployment Guide

This guide covers the most popular and practical ways to host and deploy **RedLink**:

1. **[Option 1: Free / Instant Cloud Hosting (Render or Railway)](#option-1-free--instant-cloud-hosting-recommended)** — *Easiest (No server management needed)*
2. **[Option 2: Docker & Docker Compose](#option-2-docker--docker-compose-production-ready)** — *Portable & standard for any cloud VPS*
3. **[Option 3: Traditional Linux VPS (Ubuntu + Nginx + Gunicorn + PostgreSQL)](#option-3-traditional-linux-vps-ubuntu--nginx--gunicorn)** — *Enterprise / Bare-metal*
4. **[Option 4: Local Network / Hospital LAN Access](#option-4-local-network--hospital-lan-hosting)** — *College lab or on-premise clinic*

---

## Option 1: Free / Instant Cloud Hosting (Recommended)

You can deploy RedLink directly from your GitHub repository ([phanindra267/Hemovigilance](https://github.com/phanindra267/Hemovigilance.git)) in less than 5 minutes.

### Deploying on Render (Free Tier Available)

1. **Sign Up / Log In:**
   - Go to [render.com](https://render.com/) and sign in with your GitHub account.

2. **Create a New Web Service:**
   - Click **New +** $\rightarrow$ **Web Service**.
   - Connect your GitHub repository: `phanindra267/Hemovigilance`.

3. **Configure the Service:**
   - **Name:** `redlink-blood-bank` (or your preferred name)
   - **Region:** Choose the region closest to you (e.g., Singapore, Frankfurt, Oregon)
   - **Branch:** `main`
   - **Root Directory:** *(leave blank)*
   - **Runtime:** `Python 3`
   - **Build Command:**
     ```bash
     bash build.sh
     ```
   - **Start Command:**
     ```bash
     gunicorn lifeflow_project.wsgi:application --workers 2 --bind 0.0.0.0:$PORT
     ```
   - **Plan:** Free

4. **Add Environment Variables:**
   Under **Environment Variables**, add:
   | Key | Value | Description |
   |---|---|---|
   | `DEBUG` | `False` | Disables debug mode for production |
   | `SECRET_KEY` | *(generate any long random string)* | Security key |
   | `ALLOWED_HOSTS` | `.onrender.com,localhost,127.0.0.1` | Permits Render domains |

5. **Deploy:**
   - Click **Create Web Service**.
   - Render will run `build.sh` (installing dependencies, collecting static files, applying migrations, and seeding demo data).
   - Your site will be live at `https://redlink-blood-bank.onrender.com`!

---

## Option 2: Docker & Docker Compose (Production Ready)

RedLink comes preconfigured with a `Dockerfile`, `docker-compose.yml`, and `nginx.conf`. This is the ideal option for hosting on **DigitalOcean Droplets**, **AWS EC2**, **Linode**, or **Hetzner**.

### Steps:

1. **SSH into your server:**
   ```bash
   ssh root@your-server-ip
   ```

2. **Clone the repository:**
   ```bash
   git clone https://github.com/phanindra267/Hemovigilance.git
   cd Hemovigilance
   ```

3. **Configure Environment:**
   ```bash
   cp .env.example .env
   nano .env
   ```
   Set:
   ```env
   DEBUG=False
   SECRET_KEY=your-secure-random-production-key
   ALLOWED_HOSTS=yourdomain.com,your-server-ip
   DB_ENGINE=postgresql
   DB_NAME=lifeflow_db
   DB_USER=lifeflow_user
   DB_PASSWORD=your_secure_db_password
   DB_HOST=db
   DB_PORT=5432
   ```

4. **Build and Launch Containers:**
   ```bash
   docker compose up -d --build
   ```

5. **Run Database Migrations & Seed Demo Data:**
   ```bash
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py seed_demo_data
   ```

Your application is now running behind Nginx on port 80 with PostgreSQL!

---

## Option 3: Traditional Linux VPS (Ubuntu + Nginx + Gunicorn)

### 1. Install System Packages
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv python3-dev libpq-dev postgresql postgresql-contrib nginx curl
```

### 2. Configure PostgreSQL
```bash
sudo -u postgres psql
```
```sql
CREATE DATABASE redlink_db;
CREATE USER redlink_user WITH PASSWORD 'StrongPassword123';
ALTER ROLE redlink_user SET client_encoding TO 'utf8';
ALTER ROLE redlink_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE redlink_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE redlink_db TO redlink_user;
\q
```

### 3. Clone and Set Up Environment
```bash
sudo mkdir -p /var/www/redlink
sudo chown $USER:$USER /var/www/redlink
git clone https://github.com/phanindra267/Hemovigilance.git /var/www/redlink
cd /var/www/redlink

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with your PostgreSQL credentials and domain
```

### 4. Migrate and Collect Static
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py seed_demo_data
```

### 5. Create Systemd Service for Gunicorn (`/etc/systemd/system/redlink.service`)
```ini
[Unit]
Description=RedLink Gunicorn Application Server
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/redlink
ExecStart=/var/www/redlink/venv/bin/gunicorn lifeflow_project.wsgi:application \
    --workers 4 \
    --bind unix:/run/redlink.sock
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl start redlink
sudo systemctl enable redlink
```

### 6. Configure Nginx (`/etc/nginx/sites-available/redlink`)
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 25M;

    location /static/ {
        alias /var/www/redlink/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /var/www/redlink/media/;
        expires 30d;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/redlink.sock;
    }
}
```

Enable site & restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/redlink /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. Install Free SSL with Let's Encrypt (HTTPS)
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## Option 4: Local Network / Hospital LAN Hosting

If you want to run RedLink on your local computer or laptop and allow **other devices on your Wi-Fi/LAN** (tablets, phones, other computers in the clinic/lab) to access it:

### 1. Find Your Local IP Address
- **On Windows:**
  Open PowerShell and type:
  ```powershell
  ipconfig
  ```
  Look for `IPv4 Address` (e.g., `192.168.1.45` or `10.0.0.12`).

### 2. Update `ALLOWED_HOSTS` in `.env`
Open `.env` and add your IP:
```env
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.45,0.0.0.0
```

### 3. Run the Server Bound to `0.0.0.0`
```powershell
python manage.py runserver 0.0.0.0:8000
```

### 4. Access from Any Device on the Network
On any phone, tablet, or PC connected to the same Wi-Fi:
```
http://192.168.1.45:8000
```
*(Replace `192.168.1.45` with your actual IPv4 address).*
