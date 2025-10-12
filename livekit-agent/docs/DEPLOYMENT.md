# Deployment Guide

## Overview

This guide covers deploying the Switchboard Assistant to production environments. The application consists of multiple services that can be deployed independently or together.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Twilio    │────▶│ LiveKit SIP  │────▶│   Agent     │
│   SIP       │     │   Trunk      │     │  Service    │
└─────────────┘     └──────────────┘     └─────────────┘
                           │                       │
                    ┌──────┴──────┐        ┌──────┴──────┐
                    │             │        │             │
              ┌─────▼────┐  ┌────▼─────┐  ┌▼────────────┐
              │ Supabase │  │ Backend  │  │  Frontend   │
              │Database  │  │  API     │  │   Web UI    │
              └──────────┘  └──────────┘  └─────────────┘
```

## Prerequisites

### Required Services
- LiveKit Cloud account or self-hosted LiveKit server
- Twilio account with SIP trunking enabled
- Supabase project
- Domain name (for production)
- SSL certificate (for HTTPS)

### Required Credentials
- LiveKit API keys
- Twilio account SID and auth token
- Supabase URL and service role key
- OpenAI and Deepgram API keys

## Deployment Options

### Option 1: Docker Compose (Recommended)

#### 1. Prepare Environment

Create production environment file:
```bash
cp env.example .env.production
```

Fill in production credentials:
```bash
# LiveKit
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your_production_api_key
LIVEKIT_API_SECRET=your_production_api_secret

# Twilio
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_SIP_TRUNK_ID=your_sip_trunk_id

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# AI Services
OPENAI_API_KEY=your_openai_key
DEEPGRAM_API_KEY=your_deepgram_key

# Production settings
DEBUG=false
LOG_LEVEL=INFO
```

#### 2. Create Docker Compose Configuration

Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  agent:
    build: .
    environment:
      - ENV_FILE=.env.production
    env_file:
      - .env.production
    restart: unless-stopped
    depends_on:
      - backend
    networks:
      - switchboard-network

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - ENV_FILE=.env.production
    env_file:
      - .env.production
    restart: unless-stopped
    networks:
      - switchboard-network

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
      - NEXT_PUBLIC_SUPABASE_URL=${SUPABASE_URL}
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
    restart: unless-stopped
    depends_on:
      - backend
    networks:
      - switchboard-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    restart: unless-stopped
    depends_on:
      - frontend
      - backend
    networks:
      - switchboard-network

networks:
  switchboard-network:
    driver: bridge
```

#### 3. Deploy with Docker Compose

```bash
# Build and start services
docker-compose -f docker-compose.prod.yml up -d

# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Option 2: LiveKit Cloud Deployment

#### 1. Deploy Agent to LiveKit Cloud

```bash
# Install LiveKit CLI
curl -sSL https://get.livekit.io/ | bash

# Authenticate
lk cloud auth

# Deploy agent
lk agent deploy --name switchboard-agent
```

#### 2. Configure SIP Integration

In LiveKit Cloud dashboard:
1. Go to SIP settings
2. Add Twilio SIP trunk
3. Configure inbound routing rules
4. Set up outbound calling

### Option 3: Manual Server Deployment

#### 1. Server Requirements

- Ubuntu 20.04+ or similar Linux distribution
- 4GB RAM minimum, 8GB recommended
- 50GB storage
- Public IP address
- Domain name with DNS configured

#### 2. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Nginx
sudo apt install nginx
```

#### 3. Deploy Services

```bash
# Clone repository
git clone https://github.com/your-org/switchboard-assistant.git
cd switchboard-assistant

# Set up Python environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up frontend
cd frontend
npm install
npm run build

# Set up backend
cd ../backend
pip install -r requirements.txt

# Start services with systemd
sudo cp deploy/switchboard-agent.service /etc/systemd/system/
sudo cp deploy/switchboard-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable switchboard-agent switchboard-backend
sudo systemctl start switchboard-agent switchboard-backend
```

## Configuration

### Nginx Configuration

Create `/etc/nginx/sites-available/switchboard`:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support for real-time features
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/switchboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL Certificate

Using Let's Encrypt:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Systemd Services

Create `/etc/systemd/system/switchboard-agent.service`:
```ini
[Unit]
Description=Switchboard Agent
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/switchboard-assistant
Environment=PATH=/opt/switchboard-assistant/venv/bin
ExecStart=/opt/switchboard-assistant/venv/bin/python livekit_basic_agent.py start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Database Setup

### Supabase Production Setup

1. Create production Supabase project
2. Run database migrations:
```bash
cd supabase
supabase db push
```

3. Set up Row Level Security policies
4. Configure real-time subscriptions
5. Set up database backups

### Sample Data

Insert initial data:
```sql
-- Insert departments
INSERT INTO departments (name, description, routing_priority) VALUES
('Management', 'Executive and management team', 1),
('Sales', 'Sales and business development', 2),
('Support', 'Customer support and technical assistance', 3);

-- Insert sample employees
INSERT INTO employees (name, phone, email, department_id, status) VALUES
('John Smith', '+1234567890', 'john@company.com', 
 (SELECT id FROM departments WHERE name = 'Management'), 'available'),
('Jane Doe', '+1234567891', 'jane@company.com', 
 (SELECT id FROM departments WHERE name = 'Sales'), 'available');

-- Insert company info
INSERT INTO company_info (company_name, greeting_message) VALUES
('Your Company', 'Thank you for calling. How may I direct your call?');
```

## Monitoring and Logging

### Application Monitoring

Set up monitoring with:
- **Prometheus + Grafana** for metrics
- **Sentry** for error tracking
- **LogDNA** or **ELK Stack** for log aggregation

### Health Checks

Create health check endpoints:
```python
# backend/health.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@router.get("/health/db")
async def db_health():
    # Check database connection
    pass

@router.get("/health/external")
async def external_health():
    # Check external service availability
    pass
```

### Logging Configuration

```python
# logging_config.py
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/var/log/switchboard/agent.log')
    ]
)
```

## Backup and Recovery

### Database Backups

Set up automated Supabase backups:
```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
pg_dump $DATABASE_URL > /backups/switchboard_$DATE.sql
```

### Application Backups

```bash
# Backup application data
tar -czf /backups/switchboard_app_$(date +%Y%m%d).tar.gz \
    /opt/switchboard-assistant \
    --exclude=venv \
    --exclude=node_modules
```

## Security Considerations

### Environment Security
- Use strong, unique passwords
- Rotate API keys regularly
- Enable 2FA on all service accounts
- Use environment variable files with restricted permissions

### Network Security
- Configure firewall rules
- Use HTTPS everywhere
- Implement rate limiting
- Set up DDoS protection

### Application Security
- Keep dependencies updated
- Use security headers
- Implement input validation
- Regular security audits

## Troubleshooting

### Common Issues

1. **Agent Not Starting**
   - Check environment variables
   - Verify API keys
   - Check log files

2. **SIP Calls Not Working**
   - Verify Twilio configuration
   - Check LiveKit SIP settings
   - Test with Twilio console

3. **Database Connection Issues**
   - Check Supabase credentials
   - Verify network connectivity
   - Check RLS policies

### Debug Commands

```bash
# Check service status
sudo systemctl status switchboard-agent
sudo systemctl status switchboard-backend

# View logs
sudo journalctl -u switchboard-agent -f
sudo journalctl -u switchboard-backend -f

# Test database connection
python -c "from db.supabase_client import client; print(client.table('employees').select('*').execute())"

# Test SIP configuration
curl -X POST https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/Calls.json \
  -u $TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN \
  -d "To=+1234567890" \
  -d "From=$TWILIO_PHONE_NUMBER" \
  -d "Url=https://your-domain.com/twiml"
```

## Scaling

### Horizontal Scaling

- Use load balancer for multiple agent instances
- Implement database connection pooling
- Use Redis for session management
- Set up auto-scaling groups

### Performance Optimization

- Enable gzip compression
- Use CDN for static assets
- Implement caching strategies
- Optimize database queries

## Maintenance

### Regular Tasks

- Update dependencies monthly
- Review and rotate API keys
- Monitor disk space and performance
- Review security logs
- Test backup and recovery procedures

### Updates

```bash
# Update application
git pull origin main
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

## Support

For deployment issues:
1. Check logs first
2. Review this documentation
3. Check service status pages
4. Contact support team

## Resources

- [LiveKit Cloud Documentation](https://docs.livekit.io/cloud/)
- [Twilio SIP Trunking Guide](https://www.twilio.com/docs/sip-trunking)
- [Supabase Production Guide](https://supabase.com/docs/guides/platform/going-into-prod)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Configuration Guide](https://nginx.org/en/docs/)


