# TodayAtSG Deployment Guide

## 🚀 Quick Deployment to Vercel

Your TodayAtSG Singapore Events Platform is ready for deployment! Here's how to get it live:

### 1. GitHub Repository
✅ **Repository Created**: https://github.com/sakthiish12/TodayAtSG
✅ **Code Pushed**: All 204 files committed and pushed

### 2. Vercel Deployment Setup

#### Option A: Deploy via Vercel Dashboard (Recommended)
1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "New Project" 
3. Import from Git: Select `sakthiish12/TodayAtSG`
4. Configure:
   - **Framework Preset**: Vue.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build:vercel`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

#### Option B: Deploy via CLI
```bash
cd /Users/sakthiish/Documents/Projects/TodayAtSG
vercel --prod
```

### 3. Environment Variables Setup

Add these environment variables in Vercel Dashboard (Settings → Environment Variables):

#### Frontend Environment Variables:
```
VITE_API_BASE_URL=https://your-app.vercel.app/api
VITE_GOOGLE_MAPS_API_KEY=your_google_maps_api_key
VITE_APP_ENV=production
VITE_STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
```

#### Backend Environment Variables:
```
DATABASE_URL=your_postgresql_connection_string
SECRET_KEY=your_jwt_secret_key_here
STRIPE_SECRET_KEY=your_stripe_secret_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
EMAIL_FROM=noreply@todayatsg.com
EMAIL_USERNAME=your_email_username
EMAIL_PASSWORD=your_email_password
```

### 4. Database Setup Options

#### Option A: Neon (Recommended)
1. Go to [neon.tech](https://neon.tech)
2. Create new project: "TodayAtSG"
3. Copy connection string to `DATABASE_URL`

#### Option B: Supabase
1. Go to [supabase.com](https://supabase.com)
2. Create new project: "TodayAtSG"
3. Copy connection string to `DATABASE_URL`

### 5. API Keys Required

#### Google Maps API Key:
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Enable Maps JavaScript API, Places API, Geocoding API
3. Create API key and add to both `VITE_GOOGLE_MAPS_API_KEY` and `GOOGLE_MAPS_API_KEY`

#### Stripe API Keys:
1. Go to [Stripe Dashboard](https://dashboard.stripe.com)
2. Get publishable key → `VITE_STRIPE_PUBLISHABLE_KEY`
3. Get secret key → `STRIPE_SECRET_KEY`

### 6. Post-Deployment Setup

After successful deployment:

1. **Initialize Database**:
   ```bash
   # Run database migrations
   curl -X POST https://your-app.vercel.app/api/admin/migrate
   
   # Seed with Singapore data
   curl -X POST https://your-app.vercel.app/api/admin/seed
   ```

2. **Test Key Features**:
   - Visit your deployed site
   - Test map loading with Singapore events
   - Try user registration/login
   - Test event search and filtering
   - Verify review system works

3. **Start Data Collection**:
   ```bash
   # Trigger initial scraping
   curl -X POST https://your-app.vercel.app/api/scraping/run-all
   ```

### 7. Custom Domain (Optional)

1. In Vercel Dashboard: Settings → Domains
2. Add domain: `todayatsg.com`
3. Configure DNS with your domain provider

### 8. Expected Deployment Result

Once deployed, your TodayAtSG platform will have:

🗺️ **Interactive Singapore Events Map**
🎯 **Event Discovery & Filtering** 
👤 **User Authentication & Reviews**
🕷️ **Automated Daily Data Collection**
💳 **Payment Integration for Event Submissions**
📱 **Mobile-Responsive Design**

### 9. Monitoring & Analytics

Your deployment includes:
- Error tracking ready for Sentry integration
- Performance monitoring
- API request logging
- Database query optimization

## 🎉 You're Ready to Launch!

Your Singapore Events Platform is production-ready with:
- **204 files** of comprehensive codebase
- **Vue.js + FastAPI + PostgreSQL** tech stack
- **Google Maps integration** for event discovery
- **Complete user management** system
- **Automated event data collection**
- **Scalable serverless architecture**

Visit your deployed app and start discovering Singapore events! 🇸🇬