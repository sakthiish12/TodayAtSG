# Singapore Events Map Website (TodayAtSG)

## 🎯 Project Overview

A web application for discovering events happening in Singapore, focusing on concerts, festivals, DJ events, and kids events. The platform serves locals and event organizers with an interactive map interface, user reviews, and comprehensive event discovery features.

## 👥 Target Audience
- **Primary**: Singapore locals looking for events
- **Secondary**: Event organizers wanting to promote their events

## 🛠️ Technical Stack

### Frontend
- **Framework**: Vue.js
- **Hosting**: Vercel
- **Maps**: Google Maps API
- **Views**: List view and Map view (both with integrated maps)

### Backend
- **Language**: Python (FastAPI/Django)
- **Database**: Neon PostgreSQL or Supabase
- **Hosting**: Vercel (serverless functions)

### External Integrations
- Google Maps API for location services
- Web scraping for event data collection

## ✨ Core Features

### Event Discovery
- **Interactive Map**: Display events with clustering for nearby locations
- **Location Priority**: "Near me" events shown first with geolocation
- **Filtering**: By categories, tags, date, age restrictions
- **Event Details**: Date, time, age restrictions, location, external ticket links

### Event Categories
- Concerts
- Festivals  
- DJ Events
- Kids Events
- (Expandable for future categories)

### User Features
- **Reviews**: 1-5 star rating system for events
- **Review Policy**: One review per user per event, published live
- **Event Submission**: Paid feature for adding new events
- **Moderation**: User-submitted events require approval

### Data Sources
- **Eventbrite** API/scraping
- **Venue websites**: Marina Bay Sands, Suntec City
- **Singapore websites**: Community Centers (CCs)
- **VisitSingapore** happenings (starting point for testing)
- **Daily Updates**: Automated scraping every morning

## 💰 Business Model
- **Free**: General users browsing and reviewing events
- **Paid**: Event organizers submitting new events
- **Future**: Premium features and advertising (not in scope for v1)

## 🚀 Launch Strategy
- **Testing Phase**: Start with VisitSingapore happenings data
- **Full Launch**: All event types and data sources
- **Geographic Focus**: All Singapore regions from day one

---

## 📋 Detailed Task Breakdown

### 1. Project Setup & Planning
- [ ] Initialize Vue.js project with Vite
- [ ] Set up Python backend project structure
- [ ] Configure development environment
- [ ] Set up version control and collaboration workflows
- [ ] Create project documentation structure
- [ ] Define coding standards and linting rules

### 2. Database Design & Setup
- [ ] Design event schema (id, title, description, date, time, location, age_restrictions, external_url, category, tags)
- [ ] Design user schema (id, email, password_hash, created_at, is_event_organizer)
- [ ] Design review schema (id, user_id, event_id, rating, comment, created_at)
- [ ] Design category/tag schema
- [ ] Set up Neon PostgreSQL or Supabase instance
- [ ] Create database migrations
- [ ] Set up database connection and ORM
- [ ] Create seed data for testing

### 3. Backend Foundation (Python API)
- [ ] Set up FastAPI or Django project
- [ ] Configure CORS for Vue.js frontend
- [ ] Implement database models
- [ ] Create API endpoints for events (GET, POST, PUT, DELETE)
- [ ] Create API endpoints for reviews
- [ ] Create API endpoints for categories and filtering
- [ ] Implement error handling and logging
- [ ] Add API documentation (Swagger/OpenAPI)
- [ ] Set up environment configuration

### 4. Frontend Foundation (Vue.js)
- [ ] Set up Vue 3 with Composition API
- [ ] Configure Vue Router for navigation
- [ ] Set up state management (Pinia)
- [ ] Create responsive layout components
- [ ] Implement component library/design system
- [ ] Set up API service layer
- [ ] Configure build and deployment settings
- [ ] Add error handling and loading states

### 5. Google Maps Integration
- [ ] Set up Google Maps API credentials
- [ ] Integrate Google Maps in Vue.js
- [ ] Implement event markers on map
- [ ] Add clustering for nearby events
- [ ] Implement "near me" geolocation feature
- [ ] Create map and list view toggle
- [ ] Add search functionality for locations
- [ ] Optimize map performance for mobile

### 6. Data Collection & Web Scraping System
- [ ] Set up web scraping infrastructure
- [ ] Create Eventbrite API integration
- [ ] Build scrapers for Marina Bay Sands events
- [ ] Build scrapers for Suntec City events
- [ ] Build scrapers for Singapore Community Centers
- [ ] Build scraper for VisitSingapore happenings
- [ ] Implement daily automated scraping schedule
- [ ] Create data validation and cleaning system
- [ ] Set up duplicate detection and prevention
- [ ] Add monitoring and error reporting for scrapers

### 7. User Authentication & Management
- [ ] Implement user registration and login
- [ ] Set up JWT token authentication
- [ ] Create password reset functionality
- [ ] Implement email verification
- [ ] Add user profile management
- [ ] Set up role-based access (general users vs event organizers)
- [ ] Implement session management
- [ ] Add security measures (rate limiting, etc.)

### 8. Event Management System
- [ ] Create event listing with filtering
- [ ] Implement event search functionality
- [ ] Build event detail pages
- [ ] Create event submission form (paid feature)
- [ ] Implement event categorization and tagging
- [ ] Add event moderation workflow
- [ ] Create event approval/rejection system
- [ ] Implement event editing and updates
- [ ] Add event analytics and metrics

### 9. Reviews & Rating System
- [ ] Create review submission form
- [ ] Implement 1-5 star rating display
- [ ] Add review validation (one per user per event)
- [ ] Create review listing and pagination
- [ ] Implement review aggregation and average ratings
- [ ] Add review reporting system
- [ ] Create review moderation tools
- [ ] Implement review sorting and filtering

### 10. Payment Integration (Event Submissions)
- [ ] Research and choose payment provider (Stripe/PayPal)
- [ ] Set up payment processing for event submissions
- [ ] Create payment confirmation workflow
- [ ] Implement receipt generation
- [ ] Add payment history for users
- [ ] Set up refund handling
- [ ] Add payment security measures
- [ ] Create pricing tiers for different submission types

### 11. Admin Panel & Content Management
- [ ] Create admin dashboard
- [ ] Build event moderation interface
- [ ] Implement user management tools
- [ ] Add content moderation features
- [ ] Create analytics and reporting
- [ ] Build system configuration panel
- [ ] Add bulk operations for events
- [ ] Implement audit logging

### 12. Testing & Quality Assurance
- [ ] Set up unit testing framework
- [ ] Write API endpoint tests
- [ ] Create frontend component tests
- [ ] Implement integration tests
- [ ] Set up end-to-end testing
- [ ] Performance testing and optimization
- [ ] Security testing and vulnerability assessment
- [ ] Mobile responsiveness testing
- [ ] Cross-browser compatibility testing

### 13. Deployment & DevOps (Vercel)
- [ ] Set up Vercel deployment pipeline
- [ ] Configure environment variables
- [ ] Set up database connection in production
- [ ] Configure domain and SSL
- [ ] Set up monitoring and logging
- [ ] Implement backup strategies
- [ ] Create deployment documentation
- [ ] Set up staging environment
- [ ] Configure CI/CD pipeline

### 14. Post-Launch Features & Optimization
- [ ] User feedback collection system
- [ ] Performance monitoring and optimization
- [ ] SEO optimization
- [ ] Social media integration
- [ ] Email notifications for events
- [ ] Advanced filtering options
- [ ] Event recommendation system
- [ ] Mobile app considerations
- [ ] Analytics and user behavior tracking

---

## 🗂️ Database Schema (Preliminary)

```sql
-- Events Table
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    date DATE NOT NULL,
    time TIME NOT NULL,
    location VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    age_restrictions VARCHAR(50),
    external_url VARCHAR(500),
    category_id INT REFERENCES categories(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_approved BOOLEAN DEFAULT FALSE,
    source VARCHAR(100) -- 'user_submission', 'scraped', etc.
);

-- Categories Table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

-- Tags Table
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

-- Event Tags Junction Table
CREATE TABLE event_tags (
    event_id INT REFERENCES events(id),
    tag_id INT REFERENCES tags(id),
    PRIMARY KEY (event_id, tag_id)
);

-- Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_event_organizer BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reviews Table
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    event_id INT REFERENCES events(id),
    rating INT CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, event_id)
);
```

## 🔗 API Endpoints (Preliminary)

```
GET /api/events - List events with filtering
GET /api/events/{id} - Get event details
POST /api/events - Submit new event (paid, authenticated)
PUT /api/events/{id} - Update event (authenticated)
DELETE /api/events/{id} - Delete event (authenticated)

GET /api/categories - List categories
GET /api/tags - List tags

POST /api/auth/register - User registration
POST /api/auth/login - User login
POST /api/auth/logout - User logout

GET /api/reviews/event/{event_id} - Get reviews for event
POST /api/reviews - Submit review (authenticated)

GET /api/admin/events - Admin event management
PUT /api/admin/events/{id}/approve - Approve event
```

## 🏁 Getting Started

1. **Clone the repository**
2. **Set up the backend**: Install Python dependencies and configure database
3. **Set up the frontend**: Install Node.js dependencies
4. **Configure environment variables**: API keys, database connections
5. **Run development servers**: Backend and frontend
6. **Test with VisitSingapore data**: Start with initial data source

## 📋 Current Project TODOs

### High-Level Task Status
- [ ] **Project Setup & Planning** - Initialize Vue.js + Python projects, configure dev environment, set up version control
- [ ] **Database Design & Setup** - Design schemas for events, users, reviews, categories. Set up Neon/Supabase instance
- [ ] **Backend Foundation** - Set up FastAPI/Django, implement API endpoints, database models, error handling
- [ ] **Frontend Foundation** - Set up Vue 3 with Composition API, routing, state management, responsive components
- [ ] **Google Maps Integration** - Integrate maps, implement markers, clustering, geolocation 'near me' feature
- [ ] **Data Collection System** - Build web scrapers for VisitSingapore, Eventbrite, venue sites, daily automation
- [ ] **User Authentication** - Implement registration, login, JWT auth, password reset, email verification
- [ ] **Event Management** - Event listings, search, filtering, detail pages, submission form (paid), moderation
- [ ] **Reviews System** - 1-5 star ratings, one review per user per event, review aggregation and display
- [ ] **Payment Integration** - Set up Stripe/PayPal for paid event submissions, payment workflow
- [ ] **Admin Panel** - Dashboard, event moderation, user management, analytics, bulk operations
- [ ] **Testing & QA** - Unit tests, integration tests, mobile responsiveness, security testing
- [ ] **Deployment (Vercel)** - Set up CI/CD pipeline, environment config, monitoring, staging environment
- [ ] **Post-Launch Optimization** - Performance monitoring, SEO, user feedback, advanced features

---

## 📝 Notes

- Start development with VisitSingapore happenings as the initial data source for testing
- Focus on mobile-responsive design from the beginning
- Implement proper error handling and loading states throughout
- Consider rate limiting for API endpoints
- Plan for scalability as the event database grows
- Regular backup strategies for user data and events 