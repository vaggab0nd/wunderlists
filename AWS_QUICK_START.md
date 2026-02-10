# AWS Quick Start Guide

This is a streamlined guide to get Wunderlists running on AWS in under 30 minutes.

## Prerequisites Checklist

- [ ] AWS Account with admin access
- [ ] GitHub repository set up (vaggab0nd/wunderlists)
- [ ] Code pushed to `main` branch
- [ ] OpenWeather API key (optional, for weather features)

## Step-by-Step Deployment

### 1. Create Database (5-10 minutes)

**AWS RDS Console:**
1. Go to: https://console.aws.amazon.com/rds
2. Click **Create database**
3. Select: **PostgreSQL**
4. Template: **Free tier** (for testing)
5. Settings:
   - **DB instance identifier**: `wunderlists-db`
   - **Master username**: `wunderlists_admin`
   - **Master password**: [Create strong password - save this!]
6. Connectivity:
   - **Public access**: Yes
   - **VPC security group**: Create new `wunderlists-db-sg`
7. Additional config:
   - **Initial database name**: `wunderlists_db`
8. Click **Create database**

**Wait 5-10 minutes** for database to be available.

**Get connection string:**
- Go to RDS → Databases → wunderlists-db
- Copy **Endpoint**: `wunderlists-db.xxxxx.us-east-1.rds.amazonaws.com`
- Build DATABASE_URL:
  ```
  postgresql://wunderlists_admin:YOUR_PASSWORD@wunderlists-db.xxxxx.us-east-1.rds.amazonaws.com:5432/wunderlists_db
  ```

### 2. Deploy Backend (10-15 minutes)

**AWS App Runner Console:**
1. Go to: https://console.aws.amazon.com/apprunner
2. Click **Create service**
3. Source:
   - **Repository type**: Source code repository
   - **Connect to GitHub** (authorize if first time)
   - **Repository**: `vaggab0nd/wunderlists`
   - **Branch**: `main`
   - **Deployment trigger**: Automatic
4. Build settings:
   - **Configuration source**: Use a configuration file
   - **Configuration file**: `apprunner.yaml`
5. Service settings:
   - **Service name**: `wunderlists-api`
   - **CPU**: 1 vCPU
   - **Memory**: 2 GB
   - **Port**: 8000
   - **Environment variables** (click "Add environment variable"):
     ```
     DATABASE_URL = postgresql://wunderlists_admin:PASSWORD@wunderlists-db.xxxxx.rds.amazonaws.com:5432/wunderlists_db
     DEBUG = False
     ```
6. Health check:
   - **Path**: `/health`
7. Click **Create & deploy**

**Wait 5-10 minutes** for deployment.

**Get backend URL:**
- Copy **Default domain**: `https://xxxxxxxxxx.us-east-1.awsapprunner.com`
- Test: Open `https://your-url.awsapprunner.com/health` in browser
- Should see: `{"status":"healthy"}`

### 3. Deploy Frontend (5-10 minutes)

**AWS Amplify Console:**
1. Go to: https://console.aws.amazon.com/amplify
2. Click **New app** → **Host web app**
3. Source:
   - Select **GitHub**
   - **Authorize** AWS Amplify
   - **Repository**: `vaggab0nd/wunderlists`
   - **Branch**: `main`
4. App settings:
   - **App name**: `wunderlists-frontend`
   - Build settings: Amplify will detect `amplify.yml`
5. **Environment variables**:
   ```
   VITE_RAILWAY_API_URL = https://your-apprunner-url.awsapprunner.com/api
   ```
   (Use the App Runner URL from step 2, add `/api` at the end)
6. Click **Save and deploy**

**Wait 5-10 minutes** for build and deployment.

**Get frontend URL:**
- Copy the URL: `https://main.xxxxxxxx.amplifyapp.com`
- Open in browser and test!

### 4. Update CORS (2 minutes)

Go back to **App Runner** and add the Amplify URL to environment variables:

1. App Runner Console → Services → wunderlists-api → Configuration
2. Edit → Environment variables → Add:
   ```
   ALLOWED_ORIGINS = https://main.xxxxxxxx.amplifyapp.com
   ```
3. Click **Deploy** to apply changes

### 5. Test Your Application! ✅

Open your Amplify URL: `https://main.xxxxxxxx.amplifyapp.com`

Test:
- [ ] Dashboard loads
- [ ] Can create a task
- [ ] Can view tasks
- [ ] Can create a note
- [ ] Weather widgets display (if API key set)
- [ ] Backend status shows "Connected"

## Costs

**Free Tier (First 12 months):**
- RDS: 750 hours/month free (db.t3.micro)
- App Runner: Generous free tier included
- Amplify: 1000 build minutes/month free

**After Free Tier:**
- ~$40-65/month for development environment
- ~$150-265/month for production with scaling

## Troubleshooting

**Frontend can't connect to backend:**
1. Check `VITE_RAILWAY_API_URL` includes `/api` at the end
2. Verify backend is running: Test health endpoint
3. Check CORS: Add Amplify URL to `ALLOWED_ORIGINS`

**Database connection fails:**
1. Check DATABASE_URL format
2. Verify RDS security group allows connections (0.0.0.0/0)
3. Ensure RDS is "Available" status

**Build fails:**
1. Check CloudWatch Logs (App Runner) or Build logs (Amplify)
2. Verify environment variables are set correctly
3. Check configuration files: `apprunner.yaml`, `amplify.yml`

## Next Steps

1. **Custom Domain**: Add your own domain in Amplify
2. **Monitoring**: Set up CloudWatch alarms
3. **Backups**: Configure RDS automated backups
4. **Security**: Move secrets to AWS Secrets Manager
5. **CI/CD**: Set up staging environment with `develop` branch

## Detailed Guide

For comprehensive documentation, security best practices, and advanced configurations, see:
- **[AWS_DEPLOYMENT.md](./AWS_DEPLOYMENT.md)** - Complete deployment guide

---

**Need help?** Check the detailed deployment guide or AWS documentation:
- App Runner: https://docs.aws.amazon.com/apprunner
- Amplify: https://docs.aws.amazon.com/amplify
- RDS: https://docs.aws.amazon.com/rds
