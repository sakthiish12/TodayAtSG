# Environment Variables Reference

This document provides a complete reference for all environment variables needed for TodayAtSG deployment.

## 🎯 Quick Setup

### 1. Frontend Variables (Vercel Dashboard)
```bash
VITE_API_BASE_URL=https://your-domain.vercel.app/api
VITE_GOOGLE_MAPS_API_KEY=your_google_maps_api_key
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_key
```

### 2. Backend Variables (Vercel Dashboard)
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
SECRET_KEY=your_32_character_secret_key
GOOGLE_MAPS_API_KEY=your_google_maps_server_key
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
```

## 📋 Complete Variable List

### Critical Variables (Required)

| Variable | Environment | Description | Example |
|----------|-------------|-------------|---------|
| `DATABASE_URL` | Backend | PostgreSQL connection string | `postgresql+asyncpg://user:pass@host:5432/db` |
| `SECRET_KEY` | Backend | JWT signing key (32+ chars) | `your_super_secure_random_string_here` |
| `VITE_API_BASE_URL` | Frontend | API endpoint URL | `https://todayatsg.vercel.app/api` |
| `VITE_GOOGLE_MAPS_API_KEY` | Frontend | Google Maps JavaScript API key | `AIzaSyC4YoJ...` |
| `GOOGLE_MAPS_API_KEY` | Backend | Google Maps server API key | `AIzaSyC4YoJ...` |

### Payment Integration

| Variable | Environment | Description | Example |
|----------|-------------|-------------|---------|
| `VITE_STRIPE_PUBLISHABLE_KEY` | Frontend | Stripe publishable key | `pk_live_51H...` |
| `STRIPE_SECRET_KEY` | Backend | Stripe secret key | `sk_live_51H...` |
| `STRIPE_WEBHOOK_SECRET` | Backend | Stripe webhook secret | `whsec_1N...` |

### Application Configuration

| Variable | Environment | Description | Default |
|----------|-------------|-------------|---------|
| `APP_NAME` | Backend | Application name | `TodayAtSG API` |
| `APP_VERSION` | Backend | Application version | `1.0.0` |
| `ENVIRONMENT` | Backend | Environment type | `production` |
| `DEBUG` | Backend | Debug mode | `false` |
| `LOG_LEVEL` | Backend | Logging level | `INFO` |

### Database Alternatives

| Variable | Environment | Description | Priority |
|----------|-------------|-------------|----------|
| `DATABASE_URL` | Backend | Primary database URL | 1st |
| `NEON_DATABASE_URL` | Backend | Neon database URL | 2nd |
| `SUPABASE_DATABASE_URL` | Backend | Supabase database URL | 3rd |
| `POSTGRES_URL` | Backend | Generic PostgreSQL URL | 4th |

### CORS Configuration

| Variable | Environment | Description | Default |
|----------|-------------|-------------|---------|
| `ALLOWED_ORIGINS` | Backend | Comma-separated origins | Auto-configured |
| `ALLOWED_METHODS` | Backend | HTTP methods allowed | `GET,POST,PUT,DELETE,OPTIONS,PATCH,HEAD` |
| `ALLOWED_HEADERS` | Backend | Headers allowed | `*` |

### External APIs

| Variable | Environment | Description | Required |
|----------|-------------|-------------|----------|
| `EVENTBRITE_API_KEY` | Backend | Eventbrite API key | Optional |
| `SENTRY_DSN` | Backend | Sentry error tracking | Optional |

### Email Configuration (Optional)

| Variable | Environment | Description | Example |
|----------|-------------|-------------|---------|
| `SMTP_HOST` | Backend | SMTP server host | `smtp.gmail.com` |
| `SMTP_PORT` | Backend | SMTP server port | `587` |
| `SMTP_USER` | Backend | SMTP username | `your_email@gmail.com` |
| `SMTP_PASSWORD` | Backend | SMTP password | `your_app_password` |
| `FROM_EMAIL` | Backend | From email address | `noreply@todayatsg.com` |

### Frontend Feature Flags

| Variable | Environment | Description | Default |
|----------|-------------|-------------|---------|
| `VITE_DEBUG` | Frontend | Enable debug mode | `false` |
| `VITE_ENABLE_DEVTOOLS` | Frontend | Enable Vue devtools | `false` |
| `VITE_ENABLE_ANALYTICS` | Frontend | Enable analytics | `true` |

### Geolocation Settings

| Variable | Environment | Description | Default |
|----------|-------------|-------------|---------|
| `VITE_DEFAULT_SEARCH_RADIUS` | Frontend | Default search radius (km) | `10` |
| `VITE_MAX_SEARCH_RADIUS` | Frontend | Maximum search radius (km) | `100` |
| `VITE_SINGAPORE_CENTER_LAT` | Frontend | Singapore center latitude | `1.3521` |
| `VITE_SINGAPORE_CENTER_LNG` | Frontend | Singapore center longitude | `103.8198` |

## 🔧 Vercel-Specific Variables

These are automatically set by Vercel:

| Variable | Description | Example |
|----------|-------------|---------|
| `VERCEL_ENV` | Deployment environment | `production` |
| `VERCEL_URL` | Deployment URL | `todayatsg-abc123.vercel.app` |
| `VERCEL_REGION` | Deployment region | `sin1` |
| `VERCEL_GIT_COMMIT_REF` | Git branch name | `main` |

## 🚨 Security Best Practices

### Secret Key Generation
```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### API Key Security
- Use different keys for development/production
- Never commit API keys to version control
- Rotate keys regularly
- Use environment-specific restrictions

### Database Security
- Use SSL connections (included in connection strings)
- Use read-only replicas for read operations when possible
- Set up connection pooling limits

## 📝 Environment-Specific Configuration

### Production
```bash
# Use production API keys
# Enable error monitoring
# Disable debug modes
# Use secure connection strings
DEBUG=false
ENVIRONMENT=production
VITE_DEBUG=false
VITE_ENABLE_DEVTOOLS=false
```

### Development
```bash
# Use test API keys
# Enable debug modes
# Use local database when possible
DEBUG=true
ENVIRONMENT=development
VITE_DEBUG=true
VITE_ENABLE_DEVTOOLS=true
```

### Preview (Vercel)
```bash
# Use staging API keys
# Enable limited debugging
# Test production-like environment
DEBUG=false
ENVIRONMENT=preview
VITE_DEBUG=false
```

## ✅ Validation Checklist

Before deploying, verify:

- [ ] All critical variables are set
- [ ] Database connection string is correct format
- [ ] API keys are for the correct environment
- [ ] CORS origins include your domain
- [ ] Secret key is sufficiently random and long
- [ ] Frontend API base URL matches your deployment
- [ ] Payment keys match (publishable with secret)
- [ ] Google Maps keys have correct restrictions

## 🔍 Testing Environment Variables

### Test Database Connection
```python
import asyncpg
import asyncio

async def test_db():
    conn = await asyncpg.connect("your_database_url")
    result = await conn.fetchval("SELECT 1")
    await conn.close()
    print(f"Database test: {'✅ Success' if result == 1 else '❌ Failed'}")

asyncio.run(test_db())
```

### Test API Keys
```bash
# Test Google Maps API
curl "https://maps.googleapis.com/maps/api/geocode/json?address=Singapore&key=YOUR_API_KEY"

# Test Stripe API
curl https://api.stripe.com/v1/payment_intents \
  -u sk_test_YOUR_SECRET_KEY: \
  -d amount=2000 \
  -d currency=sgd
```

---

**Last Updated**: $(date)
**Environment**: Production Ready 🚀