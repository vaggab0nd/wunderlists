# AWS Deployment Guide - Wunderlists

This guide covers deploying the Wunderlists monorepo to AWS using App Runner (backend), Amplify (frontend), and RDS (database).

## Architecture Overview

```
┌─────────────────┐      ┌──────────────────┐
│  AWS Amplify    │      │  AWS App Runner  │
│  (Frontend)     │─────▶│  (FastAPI)       │
│  React/Vite     │      │  Port 8000       │
└─────────────────┘      └──────────┬───────┘
                                    │
                                    ▼
                         ┌──────────────────┐
                         │  Amazon RDS      │
                         │  PostgreSQL      │
                         └──────────────────┘
```

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI installed and configured (`aws configure`)
- GitHub repository for CI/CD integration
- Domain name (optional, for custom domains)

## Part 1: Database Setup (Amazon RDS)

### 1.1 Create RDS PostgreSQL Instance

**Console Steps:**
1. Go to RDS Console → Create database
2. Choose **PostgreSQL** engine
3. Template: **Free tier** (for testing) or **Production** (for prod)
4. Settings:
   - DB instance identifier: `wunderlists-db`
   - Master username: `wunderlists_admin`
   - Master password: [Generate strong password]
   - DB instance class: `db.t3.micro` (free tier) or `db.t3.small` (production)
   - Storage: 20 GB (General Purpose SSD)
   - Enable storage autoscaling: Yes (up to 100 GB)
5. Connectivity:
   - VPC: Default VPC (or create new)
   - Public access: **Yes** (for App Runner to connect)
   - VPC security group: Create new → `wunderlists-db-sg`
6. Additional configuration:
   - Initial database name: `wunderlists_db`
   - Backup retention: 7 days
   - Enable deletion protection: Yes (for production)

**Using AWS CLI:**
```bash
aws rds create-db-instance \
  --db-instance-identifier wunderlists-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.3 \
  --master-username wunderlists_admin \
  --master-user-password YOUR_SECURE_PASSWORD \
  --allocated-storage 20 \
  --db-name wunderlists_db \
  --backup-retention-period 7 \
  --vpc-security-group-ids sg-xxxxxxxxx \
  --publicly-accessible
```

### 1.2 Configure Security Group

Allow inbound traffic from App Runner:
1. Go to RDS → Databases → wunderlists-db → VPC security groups
2. Edit inbound rules:
   - Type: PostgreSQL
   - Protocol: TCP
   - Port: 5432
   - Source: `0.0.0.0/0` (for App Runner) or specific CIDR blocks
   - Description: App Runner access

**Note:** For better security, use VPC endpoints or restrict to specific IP ranges.

### 1.3 Get Connection Details

After RDS is created (takes ~5-10 minutes):
1. Go to RDS → Databases → wunderlists-db
2. Copy the **Endpoint** (e.g., `wunderlists-db.xxxxx.us-east-1.rds.amazonaws.com`)
3. Note the **Port** (default: 5432)

**Build DATABASE_URL:**
```
postgresql://wunderlists_admin:YOUR_PASSWORD@wunderlists-db.xxxxx.us-east-1.rds.amazonaws.com:5432/wunderlists_db
```

## Part 2: Backend Setup (AWS App Runner)

### 2.1 Prepare Backend for Deployment

Ensure your backend is ready:

**File: `backend/app/main.py`** - Add health check endpoint if not present:
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

**File: `apprunner.yaml`** (create in project root):
```yaml
version: 1.0
runtime: python3
build:
  commands:
    pre-build:
      - pip install --upgrade pip
    build:
      - pip install -r requirements.txt
    post-build:
      - cd backend && alembic upgrade head
run:
  runtime-version: 3.11
  command: uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
  network:
    port: 8000
  env:
    - name: HOST
      value: "0.0.0.0"
    - name: PORT
      value: "8000"
```

### 2.2 Create App Runner Service

**Console Steps:**
1. Go to App Runner Console → Create service
2. Source:
   - Repository type: **Source code repository**
   - Connect to GitHub (one-time setup)
   - Repository: `vaggab0nd/wunderlists`
   - Branch: `main`
   - Deployment trigger: **Automatic** (CI/CD)
3. Build settings:
   - Configuration source: **Use a configuration file**
   - Configuration file: `apprunner.yaml`
4. Service settings:
   - Service name: `wunderlists-api`
   - Virtual CPU: 1 vCPU
   - Memory: 2 GB
   - Environment variables (add these):
     ```
     DATABASE_URL=postgresql://wunderlists_admin:PASSWORD@wunderlists-db.xxxxx.rds.amazonaws.com:5432/wunderlists_db
     OPENWEATHER_API_KEY=your_api_key_here
     DEBUG=False
     ALLOWED_ORIGINS=https://main.xxxxxxxx.amplifyapp.com,https://yourdomain.com
     ```
   - Port: 8000
5. Security:
   - Instance role: Create new or use existing
6. Health check:
   - Path: `/health`
   - Interval: 10 seconds
   - Timeout: 5 seconds
   - Healthy threshold: 1
   - Unhealthy threshold: 5
7. Auto scaling:
   - Min instances: 1
   - Max instances: 3
   - Concurrency: 100

**Using AWS CLI:**
```bash
aws apprunner create-service \
  --service-name wunderlists-api \
  --source-configuration '{
    "CodeRepository": {
      "RepositoryUrl": "https://github.com/vaggab0nd/wunderlists",
      "SourceCodeVersion": {
        "Type": "BRANCH",
        "Value": "main"
      },
      "CodeConfiguration": {
        "ConfigurationSource": "REPOSITORY",
        "CodeConfigurationValues": {
          "Runtime": "PYTHON_3",
          "BuildCommand": "pip install -r requirements.txt",
          "StartCommand": "uvicorn backend.app.main:app --host 0.0.0.0 --port 8000",
          "Port": "8000",
          "RuntimeEnvironmentVariables": {
            "DATABASE_URL": "postgresql://...",
            "DEBUG": "False"
          }
        }
      }
    },
    "AutoDeploymentsEnabled": true
  }' \
  --instance-configuration '{
    "Cpu": "1 vCPU",
    "Memory": "2 GB"
  }'
```

### 2.3 Configure CORS

Update `backend/app/main.py` to allow Amplify domain:
```python
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",
    "https://main.xxxxxxxx.amplifyapp.com",  # Replace with your Amplify URL
    "https://yourdomain.com",  # Your custom domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2.4 Note Your Backend URL

After deployment completes (~5-10 minutes):
1. Go to App Runner → Services → wunderlists-api
2. Copy the **Default domain** URL
3. Example: `https://xxxxxxxxxx.us-east-1.awsapprunner.com`
4. Test: `curl https://your-url.awsapprunner.com/health`

## Part 3: Frontend Setup (AWS Amplify)

### 3.1 Prepare Frontend Build Configuration

**File: `amplify.yml`** (create in project root):
```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - cd frontend
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: frontend/dist
    files:
      - '**/*'
  cache:
    paths:
      - frontend/node_modules/**/*
```

### 3.2 Create Amplify App

**Console Steps:**
1. Go to AWS Amplify Console → New app → Host web app
2. Source:
   - Select **GitHub**
   - Authorize AWS Amplify (one-time)
   - Repository: `vaggab0nd/wunderlists`
   - Branch: `main`
3. App settings:
   - App name: `wunderlists-frontend`
   - Environment: `production`
4. Build settings:
   - Build and test settings: Use `amplify.yml` detected in repo
   - Edit if needed to ensure it points to `frontend/` directory
5. Environment variables:
   - Add: `VITE_RAILWAY_API_URL` = `https://your-apprunner-url.awsapprunner.com/api`
6. Review and save

**Using AWS CLI:**
```bash
aws amplify create-app --name wunderlists-frontend --repository https://github.com/vaggab0nd/wunderlists

aws amplify create-branch --app-id YOUR_APP_ID --branch-name main

aws amplify start-deployment --app-id YOUR_APP_ID --branch-name main
```

### 3.3 Configure Environment Variables

In Amplify Console:
1. Go to App settings → Environment variables
2. Add:
   ```
   VITE_RAILWAY_API_URL=https://your-apprunner-url.awsapprunner.com/api
   ```
3. Redeploy to apply changes

### 3.4 Custom Domain (Optional)

1. Go to App settings → Domain management
2. Add domain → Custom domain
3. Enter your domain (e.g., `wunderlists.yourdomain.com`)
4. Follow DNS configuration instructions
5. Wait for SSL certificate provisioning (~15 minutes)

## Part 4: Environment Variables Summary

### Backend (App Runner)

```bash
# Required
DATABASE_URL=postgresql://wunderlists_admin:PASSWORD@wunderlists-db.xxxxx.rds.amazonaws.com:5432/wunderlists_db
DEBUG=False
HOST=0.0.0.0
PORT=8000

# Optional
OPENWEATHER_API_KEY=your_api_key_here
ALLOWED_ORIGINS=https://main.xxxxxxxx.amplifyapp.com,https://yourdomain.com
```

### Frontend (Amplify)

```bash
# Required
VITE_RAILWAY_API_URL=https://your-apprunner-url.awsapprunner.com/api

# Optional (not used, but in template)
VITE_SUPABASE_PROJECT_ID=not-used
VITE_SUPABASE_PUBLISHABLE_KEY=not-used
VITE_SUPABASE_URL=not-used
```

## Part 5: Database Migrations

### Initial Setup

Connect to RDS and run migrations:

**Option 1: From Local Machine**
```bash
# Update DATABASE_URL in .env to point to RDS
export DATABASE_URL="postgresql://wunderlists_admin:PASSWORD@wunderlists-db.xxxxx.rds.amazonaws.com:5432/wunderlists_db"

# Run migrations
alembic upgrade head
```

**Option 2: From App Runner**
Add to `apprunner.yaml` post-build:
```yaml
post-build:
  - cd backend && alembic upgrade head
```

This runs migrations automatically on each deployment.

### Future Migrations

1. Create migration locally:
   ```bash
   alembic revision --autogenerate -m "description"
   ```
2. Commit and push to GitHub
3. App Runner will auto-deploy and run migrations

## Part 6: Security Best Practices

### 6.1 RDS Security

- [ ] Use **VPC peering** or **PrivateLink** for App Runner → RDS connection
- [ ] Restrict RDS security group to App Runner's IP range
- [ ] Enable **SSL/TLS** for database connections
- [ ] Use **Secrets Manager** for database credentials
- [ ] Enable **automated backups** (retention: 7-30 days)
- [ ] Enable **deletion protection** for production

### 6.2 App Runner Security

- [ ] Use **IAM roles** for AWS service access (not access keys)
- [ ] Store secrets in **AWS Secrets Manager** or **Parameter Store**
- [ ] Enable **VPC connector** for private resource access
- [ ] Use **environment-specific** branches (main, staging, dev)
- [ ] Enable **request logging** to CloudWatch

### 6.3 Amplify Security

- [ ] Enable **branch-based deployments** (main = prod, develop = staging)
- [ ] Use **custom headers** for security (CSP, HSTS, X-Frame-Options)
- [ ] Enable **password protection** for staging branches
- [ ] Use **custom domains** with SSL/TLS
- [ ] Enable **web application firewall** (WAF) if needed

### 6.4 Environment Variables Management

**Use AWS Secrets Manager:**
```bash
# Store database URL
aws secretsmanager create-secret \
  --name wunderlists/database-url \
  --secret-string "postgresql://..."

# Store API keys
aws secretsmanager create-secret \
  --name wunderlists/openweather-key \
  --secret-string "your_api_key"
```

**Reference in App Runner:**
```yaml
env:
  - name: DATABASE_URL
    value: "{{resolve:secretsmanager:wunderlists/database-url}}"
```

## Part 7: Cost Optimization

### Expected Monthly Costs (US East)

**Development/Staging:**
- RDS PostgreSQL (db.t3.micro): ~$15-20/month
- App Runner (1 vCPU, 2GB): ~$25-40/month (depending on usage)
- Amplify Hosting: ~$0-5/month (generous free tier)
- **Total: ~$40-65/month**

**Production:**
- RDS PostgreSQL (db.t3.small, Multi-AZ): ~$60-80/month
- App Runner (2 vCPU, 4GB, autoscaling): ~$80-150/month
- Amplify Hosting: ~$5-15/month
- CloudFront (optional): ~$5-20/month
- **Total: ~$150-265/month**

### Cost Savings Tips

1. **Use RDS free tier** (750 hours/month for 12 months)
2. **Enable RDS autoscaling** only when needed
3. **Use Amplify free tier** (1000 build minutes, 15GB storage/month)
4. **Set up App Runner autoscaling** min=1, max=3
5. **Use Reserved Instances** for RDS if long-term (save 30-60%)
6. **Enable CloudWatch alarms** for cost monitoring

## Part 8: Monitoring & Logging

### CloudWatch Setup

**App Runner Logs:**
1. Go to App Runner → Services → wunderlists-api → Logs
2. View application logs and system logs
3. Set up log retention (default: 7 days)

**RDS Monitoring:**
1. Go to RDS → Databases → wunderlists-db → Monitoring
2. View CPU, memory, storage, connections
3. Enable Enhanced Monitoring for detailed metrics

**Amplify Logs:**
1. Go to Amplify → App → Build history
2. View build logs for each deployment

### CloudWatch Alarms

**Create alarms for:**
- RDS CPU > 80%
- RDS storage < 20%
- RDS connection count > 80% of max
- App Runner 5xx errors > 10/minute
- App Runner latency > 2 seconds

**Example alarm (AWS CLI):**
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name wunderlists-api-high-cpu \
  --alarm-description "App Runner CPU > 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/AppRunner \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

## Part 9: CI/CD Pipeline

### Automatic Deployments

**Backend (App Runner):**
- Trigger: Push to `main` branch
- Process: Build → Deploy → Health check
- Rollback: Automatic on health check failure

**Frontend (Amplify):**
- Trigger: Push to `main` branch
- Process: Build → Deploy → Cache invalidation
- Rollback: Manual via Amplify Console

### Branch Strategy

```
main (production)
  ├── develop (staging)
  └── feature/* (feature branches)
```

**Configure in Amplify:**
1. Connect `main` branch → Production environment
2. Connect `develop` branch → Staging environment
3. Enable pull request previews

## Part 10: Deployment Checklist

### Pre-Deployment

- [ ] Database migrations tested locally
- [ ] Environment variables documented
- [ ] CORS origins configured correctly
- [ ] Health check endpoint working
- [ ] Frontend build succeeds locally (`npm run build`)
- [ ] Backend tests passing (if any)
- [ ] API documentation updated

### Initial Deployment

- [ ] RDS instance created and accessible
- [ ] App Runner service deployed successfully
- [ ] Amplify app deployed successfully
- [ ] Database migrations applied
- [ ] Frontend connects to backend API
- [ ] Test core features (create task, view tasks, etc.)
- [ ] SSL certificates provisioned

### Post-Deployment

- [ ] CloudWatch alarms configured
- [ ] Backup strategy verified
- [ ] Cost monitoring enabled
- [ ] Custom domain configured (if applicable)
- [ ] Documentation updated with URLs
- [ ] Secrets stored in Secrets Manager
- [ ] Team access configured (IAM roles)

## Part 11: Troubleshooting

### Common Issues

**1. Frontend can't connect to backend**
- Check `VITE_RAILWAY_API_URL` is correct
- Verify CORS origins in backend include Amplify URL
- Check App Runner service is running
- Test backend health: `curl https://your-api.awsapprunner.com/health`

**2. Database connection errors**
- Verify DATABASE_URL format is correct
- Check RDS security group allows App Runner connections
- Ensure RDS instance is publicly accessible (or use VPC)
- Test connection: `psql $DATABASE_URL`

**3. App Runner deployment fails**
- Check CloudWatch logs for build errors
- Verify `apprunner.yaml` syntax
- Ensure all required environment variables are set
- Check Python version compatibility

**4. Amplify build fails**
- Check build logs in Amplify console
- Verify `amplify.yml` configuration
- Ensure environment variables are set
- Check Node.js version compatibility

**5. Migrations fail**
- Check DATABASE_URL is correct
- Ensure database is accessible
- Run migrations manually first: `alembic upgrade head`
- Check Alembic configuration

### Getting Help

**AWS Support:**
- AWS Support Center: https://console.aws.amazon.com/support
- App Runner Docs: https://docs.aws.amazon.com/apprunner
- Amplify Docs: https://docs.aws.amazon.com/amplify

**Application Logs:**
- App Runner: CloudWatch Logs
- Amplify: Build logs in console
- RDS: Database logs in CloudWatch

## Part 12: Backup & Disaster Recovery

### RDS Backups

**Automated backups:**
- Retention: 7-35 days
- Backup window: Set during low-traffic hours
- Stored in S3 (automatic)

**Manual snapshots:**
```bash
aws rds create-db-snapshot \
  --db-instance-identifier wunderlists-db \
  --db-snapshot-identifier wunderlists-db-snapshot-$(date +%Y%m%d)
```

**Restore from snapshot:**
```bash
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier wunderlists-db-restored \
  --db-snapshot-identifier wunderlists-db-snapshot-20260210
```

### App Runner Rollback

1. Go to App Runner → Services → wunderlists-api → Deployments
2. Select previous deployment
3. Click "Redeploy"

### Amplify Rollback

1. Go to Amplify → App → Build history
2. Select successful build
3. Click "Redeploy this version"

## Summary

Your AWS architecture:
- **Frontend**: Amplify (auto-deploys from GitHub)
- **Backend**: App Runner (auto-deploys from GitHub)
- **Database**: RDS PostgreSQL (automated backups)
- **Monitoring**: CloudWatch (logs, metrics, alarms)
- **Security**: IAM roles, Secrets Manager, VPC

**Estimated setup time:** 1-2 hours
**Estimated monthly cost:** $40-65 (dev) / $150-265 (production)

---

**Next Steps:**
1. Create RDS instance (10 minutes)
2. Deploy backend to App Runner (15 minutes)
3. Deploy frontend to Amplify (10 minutes)
4. Test end-to-end (15 minutes)
5. Configure monitoring and alarms (15 minutes)

Good luck with your deployment! 🚀
