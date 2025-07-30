# TodayAtSG - AI Development Team Configuration

## Project Overview
Singapore Events Map Website - A web application for discovering events in Singapore with Vue.js frontend, Python backend, and Google Maps integration.

**Detected Technology Stack:**
- Frontend: Vue.js 3 with Composition API
- Backend: Python (FastAPI/Django) 
- Database: PostgreSQL (Neon/Supabase)
- Maps: Google Maps API
- Hosting: Vercel
- Features: Web scraping, user authentication, reviews, payment integration

## AI Development Team Configuration
*Optimized configuration based on awesome-claude-agents repository*

### Core Development Team

#### **Vue.js Frontend Architecture** → `@vue-component-architect`
*Location: `awesome-claude-agents/agents/specialized/vue/vue-component-architect.md`*

**Specializations:**
- Vue 3 Composition API expert with deep Google Maps integration experience
- Interactive map components with event clustering and geolocation features
- Real-time filtering and search with Pinia state management
- Mobile-first responsive design for Singapore's mobile-heavy audience
- Event card components with rating systems and social features

**Use Cases:**
- "Create an interactive Singapore events map with clustering"
- "Build Vue components for event discovery with advanced filtering"
- "Implement real-time geolocation-based 'events near me' feature"
- "Design responsive event cards with reviews and ratings"
- "Create Vue.js dashboard for event organizers"

#### **Python Backend & Web Scraping** → `@backend-developer`
*Location: `awesome-claude-agents/agents/universal/backend-developer.md`*

**Specializations:**
- Multi-framework Python expertise (FastAPI/Django) for Singapore's diverse data sources
- Advanced web scraping systems for Eventbrite, Marina Bay Sands, Suntec City
- Background task processing for daily automated data collection
- Business logic for event validation, categorization, and deduplication
- Payment integration expertise for event submission monetization

**Use Cases:**
- "Build comprehensive web scraping system for Singapore event sources"
- "Implement daily automation for VisitSingapore, Community Centers data"
- "Create event validation and anti-spam systems"
- "Set up payment processing for event organizer submissions"
- "Build data pipeline for cleaning and categorizing scraped events"

#### **RESTful API Architecture** → `@api-architect`
*Location: `awesome-claude-agents/agents/universal/api-architect.md`*

**Specializations:**
- Technology-agnostic API design with Singapore-specific data patterns
- Geolocation-based filtering and search endpoint optimization
- Event discovery APIs with sophisticated filtering (category, date, age, location)
- Authentication systems for dual user types (general users vs event organizers)
- Rate limiting and API monetization for event submission features

**Use Cases:**
- "Design optimal API endpoints for Singapore event discovery"
- "Create geolocation-aware event search with radius filtering"
- "Implement review system APIs with anti-gaming measures"
- "Design event submission workflow with payment integration"
- "Build APIs for real-time event updates and notifications"

#### **Django API Specialist** → `@django-api-developer`
*Location: `awesome-claude-agents/agents/specialized/django/django-api-developer.md`*

**Advanced Alternative for Python/Django Stack:**
- Django REST Framework expertise with complex filtering and pagination
- Advanced Django model relationships for events, venues, categories, reviews
- Custom authentication for event organizers vs general users
- GraphQL implementation for efficient mobile data fetching
- API versioning and documentation for third-party integrations

**Use Cases:**
- "Implement Django REST APIs with advanced event filtering"
- "Create Django models for Singapore's venue and event hierarchies"
- "Build GraphQL endpoints for mobile app efficiency"
- "Set up Django admin for event moderation workflows"

### Specialized Support Team

#### **Modern CSS & UI Design** → `@tailwind-css-expert`
*Location: `awesome-claude-agents/agents/universal/tailwind-css-expert.md`*

**Specializations:**
- Singapore-optimized mobile-first design (80%+ mobile usage)
- Interactive map overlays and event card styling
- Cultural design patterns for Southeast Asian audiences
- Dark/light mode for different usage contexts (outdoor events, nightlife)
- Performance-optimized CSS for fast loading on Singapore's mobile networks

**Use Cases:**
- "Design mobile-optimized event discovery interface"
- "Create Singapore-themed color schemes and cultural UI patterns"
- "Style interactive map components with event clustering"
- "Build responsive event submission forms for organizers"

#### **Performance & Database Optimization** → `@performance-optimizer`
*Location: `awesome-claude-agents/agents/core/performance-optimizer.md`*

**Specializations:**
- Geographic query optimization for Singapore's compact geography
- Event search performance with multiple filter combinations
- Database indexing strategies for high-volume event data
- Caching strategies for frequently accessed Singapore venues
- Mobile performance optimization for resource-constrained devices

**Use Cases:**
- "Optimize geolocation queries for Singapore's 724 km² area"
- "Implement efficient caching for popular venues like Marina Bay Sands"
- "Optimize real-time event discovery with multiple concurrent filters"
- "Performance-tune daily web scraping processes"

#### **Code Quality & Security** → `@code-reviewer`
*Location: `awesome-claude-agents/agents/core/code-reviewer.md`*

**Specializations:**
- Security review for payment processing and user data
- Web scraping compliance and rate limiting best practices
- Data validation for untrusted scraped content
- API security for public-facing event discovery features
- Cross-browser compatibility for Singapore's diverse device ecosystem

**Use Cases:**
- "Review payment integration security for event submissions"
- "Audit web scraping systems for compliance and ethics"
- "Security review of user-generated content (reviews, event submissions)"
- "Code review for optimal mobile performance"

#### **Architecture Analysis** → `@code-archaeologist`
*Location: `awesome-claude-agents/agents/core/code-archaeologist.md`*

**Specializations:**
- Deep project structure analysis and architectural documentation
- Technology stack optimization recommendations
- Legacy pattern identification and modernization paths
- Integration assessment for Singapore's external data sources
- Codebase health evaluation and technical debt analysis

**Use Cases:**
- "Analyze current project structure and recommend optimizations"
- "Map integration patterns for Singapore government APIs"
- "Evaluate technical debt and create modernization roadmap"
- "Document architecture for new team member onboarding"

### Quick Team Usage Guide

#### **Full-Stack Feature Development**
1. **Planning**: `@code-archaeologist` → Analyze requirements and current architecture
2. **API Design**: `@api-architect` → Design endpoints and data structures  
3. **Backend Logic**: `@backend-developer` → Implement business logic and integrations
4. **Frontend Components**: `@vue-component-architect` → Build Vue.js user interface
5. **Styling**: `@tailwind-css-expert` → Responsive design and mobile optimization
6. **Optimization**: `@performance-optimizer` → Performance tuning and scaling
7. **Quality Assurance**: `@code-reviewer` → Security and code quality review

#### **Common Development Scenarios**

**New Event Source Integration:**
```
1. @backend-developer: "Integrate new event source: [venue/website]"  
2. @performance-optimizer: "Optimize data processing for [X] events per day"
3. @code-reviewer: "Review scraping compliance and error handling"
```

**Interactive Map Feature:**
```
1. @vue-component-architect: "Build interactive map with event clustering"
2. @api-architect: "Design efficient geolocation-based event APIs"
3. @tailwind-css-expert: "Style map overlays and mobile interactions"
```

**Event Discovery Enhancement:**
```
1. @api-architect: "Design advanced filtering API (category, date, age, location)"
2. @vue-component-architect: "Create sophisticated search and filter UI"
3. @performance-optimizer: "Optimize complex filtering queries"
```

**User-Generated Content:**
```
1. @api-architect: "Design event submission and review systems"
2. @backend-developer: "Implement content moderation and payment processing"
3. @code-reviewer: "Security audit for user input and payment handling"
```

### Singapore-Specific Optimizations

Each agent is configured to understand:
- **Geographic Context**: Singapore's unique urban density and venue distribution
- **Cultural Patterns**: Local event preferences, timing, and user behaviors  
- **Technical Environment**: High mobile usage, fast internet, diverse device ecosystem
- **Data Sources**: Local APIs (VisitSingapore, Community Centers, major venues)
- **Regulatory Context**: Payment processing, data privacy, content moderation requirements

Your AI development team is now optimized for building TodayAtSG with deep Singapore market knowledge and cutting-edge technical expertise!

---
*Team configuration optimized by team-configurator on 2025-07-28*
*Based on awesome-claude-agents repository analysis*