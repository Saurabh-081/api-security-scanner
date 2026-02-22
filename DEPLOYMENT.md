# Deployment Guide - Render.com

This guide walks you through deploying the API Security Scanner to Render.com.

## Prerequisites

- GitHub account with this repository
- Render.com account (free tier available)
- PostgreSQL database (provided by Render)

## Deployment Steps

### 1. Connect Repository to Render

1. Go to [https://dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** and select **"Web Service"**
3. Connect your GitHub account and select this repository
4. Choose the `main` branch

### 2. Deploy Backend Service

**Service Settings:**
- **Name:** `api-security-scanner-backend`
- **Environment:** Python 3
- **Region:** Oregon (or your preferred region)
- **Plan:** Free or Starter (depending on your needs)
- **Root Directory:** `backend` (set this in Render)

**Build Command:**
```bash
pip install --upgrade pip && pip install -r requirements.txt
```

**Start Command:**
```bash
gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

**Environment Variables:**
| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection string (from database service) |
| `SECRET_KEY` | *(auto-generate)* | JWT secret key for signing tokens |
| `DEBUG` | `false` | Disable debug mode for production |
| `BACKEND_HOST` | `0.0.0.0` | Listen on all interfaces |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | 24 hours |
| `CORS_ORIGINS` | `https://your-frontend-domain.onrender.com` | Frontend domain for CORS |

### 3. Deploy PostgreSQL Database

**Service Settings:**
- **Name:** `api-security-scanner-db`
- **Database:** PostgreSQL 16
- **Region:** Same as backend (Oregon)
- **Plan:** Free tier available

**Environment Variables:**
| Variable | Value |
|----------|-------|
| `POSTGRES_USER` | `apiuser` |
| `POSTGRES_PASSWORD` | *(auto-generate)* |
| `POSTGRES_DB` | `apisecurity` |

After creation, copy the **Database URL** and use it in the backend's `DATABASE_URL` environment variable.

### 4. Deploy Frontend Service

**Service Settings:**
- **Name:** `api-security-scanner-frontend`
- **Environment:** Node
- **Region:** Oregon (same as backend)
- **Node Version:** 18
- **Root Directory:** `frontend` (set this in Render)

**Build Command:**
```bash
npm install && npm run build
```

**Publish Directory:** `dist`

**Environment Variables:**
| Variable | Value |
|----------|-------|
| `VITE_API_URL` | `https://api-security-scanner-backend.onrender.com/api` |

### 5. Update Backend CORS Configuration

After deploying the frontend, update the backend's `CORS_ORIGINS` environment variable with the frontend URL:

```
https://api-security-scanner-frontend.onrender.com
```

### 6. Database Initialization (First Deploy Only)

The database tables are created automatically when the backend starts for the first time.

### 7. SSL/HTTPS

Render automatically provides free SSL certificates for all services.

## Monitoring

1. Go to your service dashboard on Render.com
2. Check **"Logs"** for deployment and runtime logs
3. Use **"Events"** tab to view service history

## Troubleshooting

### Backend fails to start
- Check logs in Render dashboard
- Verify `DATABASE_URL` is correctly set
- Ensure Python version is 3.11+

### Frontend shows blank page
- Check browser console for errors (F12)
- Verify `VITE_API_URL` is set correctly
- Check CORS settings on backend

### Database connection errors
- Verify database is running and healthy
- Check `DATABASE_URL` format: `postgresql://user:password@host:5432/dbname`
- Ensure backend `SECRET_KEY` is set

### API requests return 502 Bad Gateway
- Check backend service logs
- Verify environment variables are set
- Restart the backend service

## Environment Variables Reference

### Backend Required Variables
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret (use strong random value)

### Backend Optional Variables
- `DEBUG` - Set to `false` in production
- `CORS_ORIGINS` - Comma-separated list of allowed origins
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time

### Frontend Required Variables
- `VITE_API_URL` - Backend API base URL (e.g., `https://api-security-scanner-backend.onrender.com/api`)

## Updating Deployment

To update any service after deployment:

1. Commit and push changes to GitHub
2. Render detects changes automatically
3. Services redeploy (manual trigger or automatic depending on settings)
4. Check **"Events"** tab for deployment status

## Performance Notes

- Free tier may have limitations (memory, disk, request timeouts)
- Consider upgrading to Starter plan for production use
- Database connections are limited on free tier

## Support

For issues with Render deployment, visit [Render Docs](https://render.com/docs) or contact Render support.

For issues with the application, check the [project README](./README.md).
