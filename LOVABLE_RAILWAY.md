# Connecting Lovable to Railway API

## Quick Fix Checklist

If Lovable is reporting "Railway API is down or blocking requests (possibly CORS)", follow these steps:

### 1. Verify Railway API is Running

Test your Railway API directly:
```bash
# Replace YOUR-APP-URL with your actual Railway URL
curl https://your-app.railway.app/api/ping
```

Expected response:
```json
{
  "status": "ok",
  "message": "pong",
  "timestamp": 1234567890.123,
  "service": "wunderlists"
}
```

### 2. Check Railway Deployment Status

1. Go to Railway dashboard
2. Open your project
3. Check the **app service** (not database) status
4. Look for any deployment errors in the logs
5. Ensure it shows "Active" with a green indicator

### 3. Get Your Railway API URL

In Railway dashboard:
1. Click on your **app service**
2. Go to the **Settings** tab
3. Find the **Domains** section
4. Copy your public Railway domain (e.g., `your-app.railway.app`)

### 4. Configure Lovable with Railway URL

In your Lovable project:

1. Open your project settings or environment configuration
2. Set the API base URL to your Railway domain:
   ```
   API_URL=https://your-app.railway.app
   ```

3. Make sure to include `https://` and NO trailing slash

### 5. Test the Connection

From Lovable, try these test endpoints:

**Ping Test:**
```javascript
fetch('https://your-app.railway.app/api/ping')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

**Health Check:**
```javascript
fetch('https://your-app.railway.app/api/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

## Common Issues & Solutions

### Issue 1: "net::ERR_CONNECTION_REFUSED"

**Cause**: Railway API is not running or not deployed

**Solutions:**
- Check Railway deployment logs for errors
- Look for "502 Bad Gateway" or "503 Service Unavailable"
- Verify DATABASE_URL is set (see RAILWAY.md)
- Redeploy your app: `railway up`

### Issue 2: "CORS policy: No 'Access-Control-Allow-Origin' header"

**Cause**: CORS is not properly configured or API returned an error before CORS headers were added

**Solutions:**

1. **Check if API is responding at all:**
   ```bash
   curl -I https://your-app.railway.app/api/ping
   ```
   Should return `200 OK` with CORS headers

2. **Check Railway logs for errors:**
   ```bash
   railway logs
   ```
   Look for application startup errors

3. **Verify CORS configuration:**
   The latest code includes automatic Lovable domain support. Check logs for:
   ```
   CORS configured with origins: All origins (*)
   ```

4. **If needed, explicitly set CORS origins** in Railway:
   - Go to app service → Variables
   - Add `CORS_ORIGINS` variable
   - Set value to: `https://lovable.dev,https://*.lovable.dev,https://lovable.app,https://*.lovable.app`

### Issue 3: "preflight request doesn't pass access control check"

**Cause**: OPTIONS requests are blocked or not handled

**Solutions:**

1. The app now handles all HTTP methods including OPTIONS
2. Check that Railway API is fully started (check logs)
3. Clear browser cache and try again

### Issue 4: "Failed to fetch" or "Network error"

**Cause**: Railway API is down, starting up, or has crashed

**Solutions:**

1. **Check Railway logs:**
   ```bash
   railway logs --tail 50
   ```

2. **Look for these in logs:**
   - `Database connection test successful` ✓ Good
   - `Database initialization attempt X failed` ✗ Database issue
   - `Application startup failed` ✗ Critical error

3. **Restart the service:**
   ```bash
   railway up
   ```

### Issue 5: Database errors in Railway logs

**Cause**: DATABASE_URL not configured

**Solution**: See RAILWAY.md section 2-3 for database linking instructions

## Debugging Steps

### Step 1: Test Railway API Directly

```bash
# Ping test (should always work)
curl https://your-app.railway.app/api/ping

# Health check (includes database status)
curl https://your-app.railway.app/api/health

# Test specific endpoint
curl https://your-app.railway.app/api/tasks/
```

### Step 2: Check CORS Headers

```bash
# Check CORS headers on preflight
curl -X OPTIONS https://your-app.railway.app/api/tasks/ \
  -H "Origin: https://lovable.dev" \
  -H "Access-Control-Request-Method: GET" \
  -i
```

Should include:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
Access-Control-Allow-Headers: *
```

### Step 3: Check Railway Logs

```bash
railway logs --tail 100
```

Look for:
- ✓ `Wunderlists API Started Successfully`
- ✓ `CORS Origins: All origins (*)`
- ✓ `Database connection test successful`
- ✓ `Incoming request: GET /api/ping from origin: https://lovable.dev`

### Step 4: Test from Browser Console

In Lovable, open browser DevTools console and run:

```javascript
// Test basic connectivity
fetch('https://your-app.railway.app/api/ping')
  .then(response => {
    console.log('Status:', response.status)
    console.log('Headers:', [...response.headers.entries()])
    return response.json()
  })
  .then(data => console.log('Data:', data))
  .catch(error => console.error('Error:', error))
```

## What the Latest Code Does

The updated code includes:

1. **Comprehensive CORS Support**
   - Allows all origins by default (wildcard `*`)
   - Explicitly includes Lovable domains
   - Handles all HTTP methods (GET, POST, PUT, DELETE, OPTIONS, PATCH)
   - Exposes all headers
   - Caches preflight requests for 1 hour

2. **Request Logging**
   - Logs every incoming request with origin
   - Shows request duration and status
   - Helps debug connection issues

3. **Exception Handlers**
   - Ensures CORS headers are sent even on errors
   - Returns proper JSON error responses
   - Logs all errors for debugging

4. **Health Endpoints**
   - `/api/ping` - Simple connectivity test
   - `/api/health` - Detailed diagnostics including database status

5. **Startup Logging**
   - Shows CORS configuration on startup
   - Displays Railway environment info
   - Confirms successful startup

## Environment Variables

In Railway, your app service should have:

| Variable | Required | Example | Purpose |
|----------|----------|---------|---------|
| `DATABASE_URL` | Yes | `postgres://...` | Database connection (from database reference) |
| `PORT` | Auto | `8000` | Provided by Railway automatically |
| `CORS_ORIGINS` | No | `*` | Default allows all, or set specific origins |
| `OPENWEATHER_API_KEY` | Optional | `abc123...` | For weather features |
| `DEBUG` | No | `false` | Enable debug mode |

## Railway CLI Quick Reference

```bash
# Link to your project
railway link

# View logs
railway logs

# Tail logs (live)
railway logs --tail

# Redeploy
railway up

# Run command in Railway environment
railway run python railway_diagnostics.py

# Open Railway dashboard
railway open
```

## Testing Checklist

- [ ] Railway API is deployed and Active
- [ ] `/api/ping` returns `{"status": "ok"}`
- [ ] `/api/health` shows `"status": "healthy"`
- [ ] Database status is `"connected"` in health check
- [ ] CORS headers are present in response
- [ ] Railway logs show successful startup
- [ ] No errors in Railway logs
- [ ] Lovable can fetch from API

## Still Not Working?

### Check Railway Platform Status
Visit https://railway.app/status to see if there are any platform issues

### Railway Logs Show No Activity
Your app might not be starting at all:
1. Check `railway logs` for startup errors
2. Look for Python/dependency errors
3. Verify `Dockerfile` and `requirements.txt`
4. Try redeploying: `railway up`

### API Returns 502/503
Railway can't reach your app:
1. Verify `Dockerfile` uses Railway's `$PORT` variable
2. Check app is binding to `0.0.0.0` not `localhost`
3. Look for crashes in Railway logs

### Database Connection Issues
See RAILWAY.md for comprehensive database troubleshooting

### Need More Help?
1. Share Railway logs: `railway logs --tail 100`
2. Share health check response: `curl https://your-app.railway.app/api/health`
3. Check browser Network tab for specific error codes

---

**Last Updated**: January 2026
**Related Files**: RAILWAY.md, backend/app/main.py, Dockerfile
