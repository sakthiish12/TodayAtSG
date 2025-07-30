# TodayAtSG Vercel Deployment Guide

This guide provides step-by-step instructions for deploying the TodayAtSG Singapore Events Map Website to Vercel with Vue.js frontend and FastAPI serverless backend.

## 🏗️ Architecture Overview

- **Frontend**: Vue.js 3 with Vite build system
- **Backend**: FastAPI serverless functions
- **Database**: PostgreSQL (Neon or Supabase)
- **Hosting**: Vercel with CDN
- **Maps**: Google Maps API integration
- **Payments**: Stripe integration
- **Authentication**: JWT-based auth system

## 📋 Prerequisites

Before deploying, ensure you have:

1. **Accounts Setup**:
   - Vercel account (connected to GitHub)
   - Database provider (Neon or Supabase)
   - Google Cloud Platform (for Maps API)
   - Stripe account (for payments)

2. **API Keys Required**:
   - Google Maps API key
   - Stripe publishable and secret keys
   - Database connection string
   - JWT secret key (generate secure random string)

3. **Development Environment**:
   - Node.js 20+ installed
   - Python 3.11+ installed
   - Git repository ready

## 🚀 Deployment Steps

### Step 1: Prepare the Project

1. **Run the deployment preparation script**:
   ```bash
   ./deploy.sh production
   ```

2. **Verify build output**:
   - Check that `frontend/dist/` contains the built files
   - Ensure `api/` directory has all Python serverless functions
   - Confirm `vercel.json` configuration is present

### Step 2: Environment Variables Configuration

#### Frontend Environment Variables (VITE_ prefix)

Set these in Vercel dashboard under Project Settings → Environment Variables:

```bash
# API Configuration
VITE_API_BASE_URL=https://your-domain.vercel.app/api
VITE_APP_NAME=TodayAtSG
VITE_APP_VERSION=1.0.0

# Google Maps
VITE_GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# Stripe (Publishable Key)
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key

# App Configuration
VITE_DEFAULT_SEARCH_RADIUS=10
VITE_MAX_SEARCH_RADIUS=100
VITE_SINGAPORE_CENTER_LAT=1.3521
VITE_SINGAPORE_CENTER_LNG=103.8198

# Feature Flags
VITE_DEBUG=false
VITE_ENABLE_DEVTOOLS=false
VITE_ENABLE_ANALYTICS=true
```

#### Backend Environment Variables

```bash
# Application
APP_NAME=TodayAtSG API
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=INFO

# Database (Choose one)
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
# OR for Neon
NEON_DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
# OR for Supabase
SUPABASE_DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db

# Security
SECRET_KEY=your_super_secure_secret_key_32_chars_min
ALGORITHM=HS256

# CORS (automatically configured for Vercel)
ALLOWED_ORIGINS=https://your-domain.com,https://your-domain.vercel.app
ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS,PATCH,HEAD
ALLOWED_HEADERS=*

# External APIs
GOOGLE_MAPS_API_KEY=your_google_maps_server_key
EVENTBRITE_API_KEY=your_eventbrite_key

# Stripe
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=noreply@todayatsg.com

# Redis (Optional - for caching)
REDIS_URL=redis://username:password@host:port/0

# Monitoring
SENTRY_DSN=your_sentry_dsn_here
```

### Step 3: Database Setup

1. **Create Database** (choose one):
   
   **Option A: Neon (Recommended)**
   ```bash
   # Visit https://neon.tech
   # Create a new project
   # Copy the connection string
   ```
   
   **Option B: Supabase**
   ```bash
   # Visit https://supabase.com
   # Create a new project
   # Go to Settings → Database
   # Copy the connection string
   ```

2. **Run Database Migrations**:
   ```bash
   # Set up your local environment first
   cd backend
   pip install -r requirements.txt
   
   # Set DATABASE_URL in your .env file
   echo "DATABASE_URL=your_connection_string" > .env
   
   # Run migrations
   alembic upgrade head
   ```

### Step 4: Deploy to Vercel

#### Method 1: GitHub Integration (Recommended)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Configure for Vercel deployment"
   git push origin main
   ```

2. **Connect to Vercel**:
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will auto-detect the configuration from `vercel.json`

3. **Configure Environment Variables**:
   - In Vercel dashboard, go to Project Settings → Environment Variables
   - Add all the environment variables listed above
   - Make sure to set the environment (Production, Preview, Development)

#### Method 2: Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login and Deploy**:
   ```bash
   vercel login
   vercel --prod
   ```

### Step 5: Custom Domain Setup (Optional)

1. **Add Custom Domain**:
   - In Vercel dashboard, go to Project Settings → Domains
   - Add your custom domain (e.g., `todayatsg.com`)
   - Configure DNS records as instructed

2. **Update Environment Variables**:
   - Update `VITE_API_BASE_URL` to use your custom domain
   - Update `ALLOWED_ORIGINS` to include your custom domain

## 🔧 Configuration Files

### Key Files Created:

1. **`/vercel.json`** - Main Vercel configuration
2. **`/api/index.py`** - Main API entry point
3. **`/api/requirements.txt`** - Python dependencies for serverless
4. **`/api/serverless_db.py`** - Database connection handling
5. **`/api/cors_config.py`** - CORS configuration
6. **`/frontend/vite.config.ts`** - Frontend build configuration
7. **`/package.json`** - Root package configuration

### Routing Configuration:

- **Frontend**: All routes except `/api/*` go to Vue.js SPA
- **API**: `/api/*` routes go to Python serverless functions
- **Health Check**: `/health` → `/api/health`
- **API Docs**: `/docs` → `/api/docs` (disabled in production)

## 🔍 Troubleshooting

### Common Issues:

1. **Build Failures**:
   ```bash
   # Check Node.js version
   node --version  # Should be 20+
   
   # Clear cache and rebuild
   cd frontend
   npm run clean
   npm install
   npm run build:vercel
   ```

2. **Database Connection Issues**:
   ```bash
   # Test connection string format
   # Should be: postgresql+asyncpg://user:pass@host:port/db
   # NOT: postgres:// (convert to postgresql+asyncpg://)
   ```

3. **CORS Errors**:
   - Verify `ALLOWED_ORIGINS` includes your domain
   - Check that Vercel URL is included in CORS settings
   - Ensure environment variables are set correctly

4. **API Function Timeouts**:
   - Functions have 30s timeout (300s for scraping)
   - Use connection pooling for database efficiency
   - Consider breaking large operations into smaller functions

### Debugging:

1. **Check Function Logs**:
   - Go to Vercel Dashboard → Functions
   - Click on any function to see logs and metrics

2. **Test API Endpoints**:
   ```bash
   # Health check
   curl https://your-domain.vercel.app/api/health
   
   # Test CORS
   curl -H "Origin: https://your-frontend-domain.com" \
        -H "Access-Control-Request-Method: GET" \
        -X OPTIONS https://your-domain.vercel.app/api/events
   ```

## 📊 Performance Optimization

### Database:
- Use connection pooling (configured in `serverless_db.py`)
- Enable connection reuse with `NullPool` for serverless
- Index geolocation queries for map performance

### Frontend:
- Code splitting configured in Vite
- Lazy loading for maps and heavy components
- CDN caching for static assets

### API:
- Function-level caching headers
- Optimized for cold starts
- Regional deployment (Singapore)

## 🔒 Security Considerations

1. **Environment Variables**:
   - Never commit API keys to repository
   - Use different keys for development/production
   - Rotate keys regularly

2. **CORS Configuration**:
   - Restrictive origins in production
   - Specific headers allowed
   - Credentials properly configured

3. **Rate Limiting**:
   - Configured per endpoint
   - Authentication rate limiting
   - IP-based restrictions

## 📈 Monitoring & Analytics

1. **Vercel Analytics**:
   - Automatically enabled for performance monitoring
   - View in Vercel Dashboard → Analytics

2. **Sentry Integration**:
   - Error tracking and performance monitoring
   - Set `SENTRY_DSN` environment variable

3. **Database Monitoring**:
   - Use your database provider's monitoring tools
   - Set up alerts for connection issues

## 🚦 Going Live Checklist

- [ ] All environment variables set in Vercel
- [ ] Database migrations run successfully
- [ ] Custom domain configured (if applicable)
- [ ] SSL certificate active
- [ ] CORS configured for your domain
- [ ] API endpoints responding correctly
- [ ] Google Maps integration working
- [ ] Stripe payment integration tested
- [ ] Error monitoring configured
- [ ] Performance monitoring enabled
- [ ] Backup strategy in place

## 📞 Support

For deployment issues:
1. Check the [troubleshooting section](#troubleshooting)
2. Review Vercel function logs
3. Test API endpoints individually
4. Verify environment variable configuration

---

**Deployment Status**: Ready for Production 🚀

Last Updated: $(date)