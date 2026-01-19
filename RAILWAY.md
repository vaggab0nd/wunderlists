# Railway Deployment Guide

## Quick Links

- **CORS/Lovable Issues**: See [LOVABLE_RAILWAY.md](LOVABLE_RAILWAY.md) for connecting Lovable to Railway API
- **Database Issues**: Continue reading this guide

## Database Connection Issues

If you're seeing "no database connection" errors on Railway, follow these troubleshooting steps:

### 1. Verify Database Service is Running

1. Go to your Railway project dashboard
2. Check if the PostgreSQL database service is running (green status)
3. If stopped, click to restart it

### 2. Check Environment Variables

Railway needs to link your app to the database:

1. Go to your **app service** (not database) in Railway
2. Click on the **Variables** tab
3. Verify these variables are present:
   - `DATABASE_URL` (should start with `postgres://` or `postgresql://`)
   - Or `DATABASE_PRIVATE_URL` (internal Railway network)

### 3. Link Database to App Service

If DATABASE_URL is missing:

1. In Railway dashboard, go to your **app service**
2. Click **Variables** tab
3. Click **+ New Variable**
4. Click **Add Reference**
5. Select your **PostgreSQL database**
6. Choose `DATABASE_URL` from the dropdown
7. Click **Add**
8. Your app will automatically redeploy

### 4. Use the Diagnostic Script

Run the diagnostic script locally (with Railway variables):

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Run diagnostics with Railway environment
railway run python railway_diagnostics.py
```

Or run it directly on Railway:

```bash
railway run python railway_diagnostics.py
```

### 5. Check Railway Logs

View real-time logs to see connection errors:

```bash
railway logs
```

Look for these log messages:
- `Database initialization attempt X/5` - Shows connection attempts
- `Database connection test successful` - Good sign!
- `Environment variables available` - Shows which DB vars are set
- Connection errors with details

### 6. Common Issues & Solutions

#### Issue: "No DATABASE_URL found"
**Solution:** Link your database to app service (see step 3)

#### Issue: "Connection timeout"
**Solutions:**
- Database service might be starting up (wait 30 seconds)
- Check if database is in the same region as your app
- Verify database service is running

#### Issue: "Authentication failed"
**Solutions:**
- Database credentials may have changed
- Remove and re-add database reference variable
- Restart both database and app services

#### Issue: "SSL connection error"
**Solution:** The app now automatically adds `sslmode=require` for Railway connections

#### Issue: "Tables not found"
**Solution:** This is normal on first deployment - tables are created automatically on startup

### 7. Health Check Endpoint

Check your app's health status:

```
https://your-app.railway.app/health
```

This returns detailed diagnostics:
```json
{
  "status": "healthy",
  "service": "wunderlists",
  "database": {
    "status": "connected",
    "details": {
      "version": ["PostgreSQL", "14.5"],
      "connection_pool": {
        "size": 5,
        "checked_in": 4,
        "checked_out": 1
      }
    }
  },
  "environment": {
    "has_database_url": true,
    "has_database_private_url": false,
    "has_pgurl": false
  }
}
```

### 8. What This Fix Does

The code now includes:

1. **Multiple environment variable checks**: Tries `DATABASE_URL`, `DATABASE_PRIVATE_URL`, and `PGURL`
2. **Automatic URL format conversion**: Converts `postgres://` to `postgresql://`
3. **SSL mode for Railway**: Automatically adds SSL requirement for Railway connections
4. **Connection retry logic**: 5 attempts with exponential backoff (2s, 4s, 8s, 16s, 32s)
5. **Connection pooling**: Optimized pool size with health monitoring
6. **Detailed logging**: Every step is logged for debugging
7. **Enhanced health checks**: `/health` endpoint shows connection status and diagnostics

### 9. Manual Database Setup (if needed)

If you need to manually provision a database:

```bash
# Using Railway CLI
railway add -d postgresql

# Then link it to your app (see step 3)
```

### 10. Still Having Issues?

If none of the above works:

1. **Check Railway Status**: Visit https://railway.app/status
2. **Database Logs**: Check database service logs in Railway dashboard
3. **Redeploy Both Services**:
   ```bash
   railway up -d  # Redeploy database
   railway up     # Redeploy app
   ```
4. **Create New Database**:
   - Sometimes starting fresh helps
   - Add new PostgreSQL service
   - Link it to your app
   - Remove old database service

### Key Files

- `backend/app/database.py` - Database connection logic with Railway support
- `backend/app/main.py` - Startup with retry logic and health checks
- `railway_diagnostics.py` - Diagnostic script to test connection
- `Dockerfile` - Uses Railway's PORT environment variable

### Environment Variables Checklist

On Railway, your app service should have:
- ✓ `DATABASE_URL` (from database reference)
- ✓ `PORT` (automatically provided by Railway)
- ✓ `OPENWEATHER_API_KEY` (if using weather features)

Optional:
- `DEBUG=false` (for production)
- `HOST=0.0.0.0` (usually not needed)
- `CORS_ORIGINS` (default is `*` to allow all origins)

## CORS & API Access Issues

If you're getting CORS errors or "Railway API is down or blocking requests" from Lovable or other frontends:

### Quick Checks

1. **Test API is running:**
   ```bash
   curl https://your-app.railway.app/api/ping
   ```
   Should return: `{"status": "ok", "message": "pong", ...}`

2. **Check CORS headers:**
   ```bash
   curl -I https://your-app.railway.app/api/ping \
     -H "Origin: https://lovable.dev"
   ```
   Should include: `Access-Control-Allow-Origin: *`

3. **View logs for errors:**
   ```bash
   railway logs --tail 50
   ```

### Solutions

- **API not responding**: Check database connection (sections above)
- **CORS errors**: See [LOVABLE_RAILWAY.md](LOVABLE_RAILWAY.md) for detailed troubleshooting
- **502/503 errors**: API failed to start, check logs for Python/database errors

The app includes automatic CORS support for:
- All origins by default (`*`)
- Explicit Lovable domain support
- Proper error handling with CORS headers
- Request logging for debugging

For complete CORS troubleshooting, see **LOVABLE_RAILWAY.md**.

---

**Last Updated**: January 2026
**Railway Version**: v2 (current)
**Related**: LOVABLE_RAILWAY.md, railway_diagnostics.py
