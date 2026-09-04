# RedLink Production Deployment Guide

## 1. Production Architecture
- **Reverse Proxy:** Nginx with SSL/TLS (Let's Encrypt)
- **Application Server:** Gunicorn WSGI (4-8 workers)
- **Static Assets:** WhiteNoise or Nginx static alias
- **Database:** PostgreSQL 14+

## 2. Gunicorn Configuration
Run Gunicorn on a Unix domain socket:
`ash
gunicorn lifeflow_project.wsgi:application \
    --workers 4 \
    --bind 127.0.0.1:8000 \
    --timeout 60 \
    --access-logfile /var/log/lifeflow/access.log \
    --error-logfile /var/log/lifeflow/error.log
`

## 3. Systemd Service Unit (/etc/systemd/system/lifeflow.service)
`ini
[Unit]
Description=RedLink Hemovigilance Application Server
After=network.target

[Service]
User=lifeflow
Group=www-data
WorkingDirectory=/var/www/lifeflow
ExecStart=/var/www/lifeflow/venv/bin/gunicorn lifeflow_project.wsgi:application --workers 4 --bind unix:/run/lifeflow.sock
Restart=always

[Install]
WantedBy=multi-user.target
`

## 4. Docker Deployment
Use the included docker-compose.yml:
`ash
docker-compose up -d --build
`
