# TodayAtSG Backend API

A comprehensive FastAPI backend for the Singapore Events Map Website, providing robust event management, user authentication, payment processing, and web scraping capabilities.

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Redis (optional, for background tasks)

### Installation

1. **Clone and Navigate**
   ```bash
   cd backend
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb todayatsg
   
   # Run deployment script (creates tables and seeds data)
   python deploy.py
   ```

6. **Start Development Server**
   ```bash
   python run_dev.py
   # Or: uvicorn app.main:app --reload
   ```

7. **Access API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/api/docs
   - Admin Panel: http://localhost:8000/api/admin

## 📋 Features

### 🔐 Authentication & Authorization
- JWT-based authentication with refresh tokens
- Role-based access control (Users, Event Organizers, Admins)
- Password strength validation and secure hashing
- Email verification and password reset
- Rate limiting for auth endpoints

### 🎉 Event Management
- **Comprehensive CRUD operations** for events
- **Advanced search and filtering** with geolocation support
- **Event categorization** with Singapore-specific categories
- **Tag system** for flexible event classification
- **Event approval workflow** for user submissions
- **Featured events** and analytics tracking
- **"Near me" functionality** with distance calculations

### ⭐ Reviews & Ratings
- **5-star rating system** with comment support
- **One review per user per event** constraint
- **Review aggregation** and statistics
- **Review moderation** with reporting system
- **Review verification** for confirmed attendees

### 💳 Payment Integration
- **Stripe integration** for event submission payments
- **Webhook handling** for payment confirmation
- **Payment intent creation** and confirmation
- **Refund support** with admin controls
- **Free event quotas** for organizers

### 🕷️ Web Scraping
- **Multi-source scraping** (VisitSingapore, Eventbrite, Marina Bay Sands)
- **Configurable scrapers** with retry logic
- **Daily automated scraping** with background tasks
- **Duplicate detection** and data validation
- **Admin scraping management** interface

### 🛡️ Security & Performance
- **Comprehensive middleware** stack
- **Rate limiting** with IP-based tracking
- **Security headers** and CORS configuration
- **Request/response logging** with structured logs
- **Error handling** with detailed logging
- **Input validation** with Pydantic schemas

### 📊 Admin Features
- **Event moderation** with approval/rejection workflow
- **User management** with role assignment
- **Review moderation** with hide/delete options
- **Analytics dashboard** with key metrics
- **Scraping management** with job monitoring
- **System health checks** and monitoring

## 🏗️ Architecture

### Directory Structure
```
backend/
├── app/
│   ├── api/
│   │   ├── endpoints/        # API route handlers
│   │   └── dependencies/     # Shared dependencies
│   ├── core/
│   │   ├── config.py        # Settings and configuration
│   │   ├── security.py      # Authentication utilities
│   │   └── middleware.py    # Custom middleware
│   ├── db/
│   │   ├── database.py      # Database connection
│   │   ├── base.py          # Base model imports
│   │   └── seed.py          # Database seeding
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic services
│   └── utils/               # Utility functions
├── alembic/                 # Database migrations
├── tests/                   # Test suites
└── deploy.py               # Deployment script
```

### Technology Stack

- **FastAPI** - Modern, fast web framework
- **SQLAlchemy 2.0** - Async ORM with PostgreSQL
- **Alembic** - Database migrations
- **Pydantic** - Data validation and serialization
- **Stripe** - Payment processing
- **Redis** - Caching and background tasks
- **httpx** - Async HTTP client for scraping
- **BeautifulSoup** - HTML parsing
- **Structlog** - Structured logging
- **pytest** - Testing framework

## 🌐 API Documentation

### Main Endpoints

#### Authentication (`/api/auth`)
```
POST   /register           # User registration
POST   /login              # User login
POST   /refresh            # Token refresh
GET    /me                 # Current user info
PUT    /me                 # Update user info
POST   /change-password    # Change password
POST   /forgot-password    # Request password reset
POST   /reset-password     # Reset password
POST   /logout             # User logout
```

#### Events (`/api/events`)
```
GET    /                   # List events (with filtering)
POST   /search             # Advanced event search
GET    /{id}               # Get single event
POST   /submit             # Submit event (authenticated)
POST   /                   # Create event (organizers/admins)
PUT    /{id}               # Update event
DELETE /{id}               # Delete event
GET    /nearby             # Get nearby events
GET    /featured           # Get featured events
POST   /{id}/click         # Track event click
```

#### Categories (`/api/categories`)
```
GET    /                   # List categories
GET    /popular            # Popular categories
GET    /{id}               # Get single category
POST   /                   # Create category (admin)
PUT    /{id}               # Update category (admin)
DELETE /{id}               # Delete category (admin)
```

#### Tags (`/api/tags`)
```
GET    /                   # List tags
GET    /popular            # Popular tags
GET    /suggest            # Tag suggestions
GET    /{id}               # Get single tag
POST   /                   # Create tag (admin)
PUT    /{id}               # Update tag (admin)
DELETE /{id}               # Delete tag (admin)
```

#### Reviews (`/api/reviews`)
```
GET    /event/{id}         # Get event reviews
GET    /event/{id}/stats   # Get review statistics
POST   /                   # Create review
PUT    /{id}               # Update review
DELETE /{id}               # Delete review
POST   /{id}/report        # Report review
GET    /user/my-reviews    # Get user's reviews
```

#### Payment (`/api/payment`)
```
POST   /create-intent      # Create payment intent
POST   /confirm            # Confirm payment
POST   /webhook            # Stripe webhook
GET    /config             # Payment configuration
```

#### Admin (`/api/admin`)
```
GET    /events/pending     # Pending events
POST   /events/{id}/approve # Approve/reject event
GET    /events/all         # All events (admin view)
POST   /events/{id}/feature # Feature/unfeature event
GET    /users              # List users
POST   /users/{id}/toggle-active # Activate/deactivate user
POST   /users/{id}/make-organizer # Grant organizer privileges
GET    /reviews/reported   # Reported reviews
POST   /reviews/{id}/moderate # Moderate review
GET    /stats/dashboard    # Admin dashboard stats
```

#### Scraping (`/api/admin/scraping`)
```
POST   /run                # Start scraping job (async)
POST   /run-sync           # Run scraping job (sync)
GET    /sources            # Available scraping sources
POST   /test/{source}      # Test specific source
GET    /stats              # Scraping statistics
```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Application
DEBUG=true
ENVIRONMENT=development
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
DATABASE_URL_SYNC=postgresql://user:pass@localhost/db

# External APIs
GOOGLE_MAPS_API_KEY=your-google-maps-key
STRIPE_SECRET_KEY=sk_test_your-stripe-key
STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-key

# Email (for notifications)
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Redis (optional)
REDIS_URL=redis://localhost:6379/0
```

### Database Setup

1. **Create Database**
   ```bash
   createdb todayatsg
   ```

2. **Run Migrations**
   ```bash
   alembic upgrade head
   ```

3. **Seed Data**
   ```bash
   python -c "from app.db.seed import seed_database; import asyncio; asyncio.run(seed_database())"
   ```

Or use the deployment script:
```bash
python deploy.py
```

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

### Test Categories

- **Authentication tests** - Registration, login, permissions
- **Event tests** - CRUD operations, search, filtering
- **Review tests** - Rating system, moderation
- **Admin tests** - Management interfaces
- **API tests** - Endpoint validation, error handling

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   # Set production environment variables
   export ENVIRONMENT=production
   export DEBUG=false
   export DATABASE_URL=your-production-db-url
   # ... other production settings
   ```

2. **Database Migration**
   ```bash
   alembic upgrade head
   ```

3. **Run Deployment Script**
   ```bash
   python deploy.py
   ```

4. **Start Production Server**
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Vercel Deployment

The backend is configured for Vercel serverless deployment:

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Deploy**
   ```bash
   vercel
   ```

3. **Configure Environment Variables** in Vercel dashboard

### Docker Deployment

```bash
# Build image
docker build -t todayatsg-backend .

# Run container
docker run -p 8000:8000 --env-file .env todayatsg-backend
```

## 📚 Development

### Code Style

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

```bash
# Format code
black app tests

# Sort imports
isort app tests

# Lint code
flake8 app tests

# Type check
mypy app
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Adding New Features

1. **Create model** in `app/models/`
2. **Create schema** in `app/schemas/`
3. **Create endpoints** in `app/api/endpoints/`
4. **Add tests** in `tests/`
5. **Update documentation**

## 🏥 Health Checks

The API includes comprehensive health monitoring:

- **Basic health check**: `GET /health`
- **Database connectivity**: Automatic checks
- **External service status**: API key validation
- **System resources**: File permissions, disk space

## 📊 Monitoring & Logging

### Structured Logging

All logs are structured using `structlog`:

```python
logger.info(
    "Event created",
    event_id=event.id,
    user_id=user.id,
    category=event.category.name
)
```

### Monitoring Integration

- **Sentry** for error tracking (optional)
- **Request tracking** with unique request IDs
- **Performance monitoring** with request timing
- **Rate limiting** with configurable thresholds

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Write tests** for new functionality
4. **Ensure tests pass**: `pytest`
5. **Format code**: `black app tests`
6. **Commit changes**: `git commit -m 'Add amazing feature'`
7. **Push to branch**: `git push origin feature/amazing-feature`
8. **Open Pull Request**

## 📄 License

This project is part of the TodayAtSG platform. All rights reserved.

## 📞 Support

For questions or support:
- **GitHub Issues**: For bug reports and feature requests
- **Email**: admin@todayatsg.com
- **Documentation**: Check the `/api/docs` endpoint when running

---

**Built with ❤️ for the Singapore events community**