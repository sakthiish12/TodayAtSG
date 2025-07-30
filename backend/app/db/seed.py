"""
Database seeding script for TodayAtSG
Seeds the database with initial categories, tags, and sample data for Singapore events.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, date, time
from decimal import Decimal
import asyncio

from app.db.database import AsyncSessionLocal
from app.models.category import Category
from app.models.tag import Tag
from app.models.user import User
from app.models.event import Event
from app.models.review import Review
from app.core.security import get_password_hash


async def seed_categories(db: AsyncSession):
    """Seed initial categories for Singapore events."""
    
    categories_data = [
        {
            "name": "Concerts",
            "slug": "concerts",
            "description": "Live music performances, concerts, and musical events",
            "icon": "🎵",
            "color": "#FF6B6B",
            "sort_order": 1
        },
        {
            "name": "Festivals",
            "slug": "festivals",
            "description": "Cultural festivals, food festivals, and seasonal celebrations",
            "icon": "🎉",
            "color": "#4ECDC4",
            "sort_order": 2
        },
        {
            "name": "DJ Events",
            "slug": "dj-events",
            "description": "Electronic music, DJ sets, and club events",
            "icon": "🎧",
            "color": "#45B7D1",
            "sort_order": 3
        },
        {
            "name": "Kids Events",
            "slug": "kids-events",
            "description": "Family-friendly events and activities for children",
            "icon": "🧸",
            "color": "#96CEB4",
            "sort_order": 4
        },
        {
            "name": "Food & Drink",
            "slug": "food-drink",
            "description": "Food markets, wine tastings, and culinary experiences",
            "icon": "🍽️",
            "color": "#FECA57",
            "sort_order": 5
        },
        {
            "name": "Art & Culture",
            "slug": "art-culture",
            "description": "Art exhibitions, cultural shows, and museum events",
            "icon": "🎨",
            "color": "#FF9FF3",
            "sort_order": 6
        },
        {
            "name": "Sports & Fitness",
            "slug": "sports-fitness",
            "description": "Sports events, fitness classes, and outdoor activities",
            "icon": "⚽",
            "color": "#54A0FF",
            "sort_order": 7
        },
        {
            "name": "Workshops",
            "slug": "workshops",
            "description": "Educational workshops, skill-building sessions, and classes",
            "icon": "📚",
            "color": "#5F27CD",
            "sort_order": 8
        },
        {
            "name": "Nightlife",
            "slug": "nightlife",
            "description": "Bars, clubs, and nighttime entertainment",
            "icon": "🌙",
            "color": "#222f3e",
            "sort_order": 9
        },
        {
            "name": "Networking",
            "slug": "networking",
            "description": "Business networking, meetups, and professional events",
            "icon": "🤝",
            "color": "#10ac84",
            "sort_order": 10
        }
    ]
    
    for category_data in categories_data:
        # Check if category already exists
        result = await db.execute(
            select(Category).where(Category.slug == category_data["slug"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            category = Category(**category_data)
            db.add(category)
            print(f"Added category: {category_data['name']}")
    
    await db.commit()


async def seed_tags(db: AsyncSession):
    """Seed initial tags for Singapore events."""
    
    tags_data = [
        {"name": "Outdoor", "slug": "outdoor", "color": "#2ecc71"},
        {"name": "Indoor", "slug": "indoor", "color": "#3498db"},
        {"name": "Free", "slug": "free", "color": "#27ae60"},
        {"name": "Paid", "slug": "paid", "color": "#e74c3c"},
        {"name": "Family Friendly", "slug": "family-friendly", "color": "#f39c12"},
        {"name": "Adults Only", "slug": "adults-only", "color": "#8e44ad"},
        {"name": "Weekend", "slug": "weekend", "color": "#16a085"},
        {"name": "Weekday", "slug": "weekday", "color": "#2980b9"},
        {"name": "Marina Bay", "slug": "marina-bay", "color": "#d35400"},
        {"name": "Orchard", "slug": "orchard", "color": "#c0392b"},
        {"name": "Clarke Quay", "slug": "clarke-quay", "color": "#9b59b6"},
        {"name": "Sentosa", "slug": "sentosa", "color": "#1abc9c"},
        {"name": "Chinatown", "slug": "chinatown", "color": "#e67e22"},
        {"name": "Little India", "slug": "little-india", "color": "#f1c40f"},
        {"name": "Bugis", "slug": "bugis", "color": "#34495e"},
        {"name": "Raffles Place", "slug": "raffles-place", "color": "#95a5a6"},
        {"name": "Live Music", "slug": "live-music", "color": "#e91e63"},
        {"name": "Dancing", "slug": "dancing", "color": "#9c27b0"},
        {"name": "Food", "slug": "food", "color": "#ff9800"},
        {"name": "Drinks", "slug": "drinks", "color": "#607d8b"},
        {"name": "Art", "slug": "art", "color": "#673ab7"},
        {"name": "Culture", "slug": "culture", "color": "#3f51b5"},
        {"name": "Technology", "slug": "technology", "color": "#009688"},
        {"name": "Business", "slug": "business", "color": "#795548"},
        {"name": "Health", "slug": "health", "color": "#4caf50"},
        {"name": "Wellness", "slug": "wellness", "color": "#8bc34a"},
        {"name": "Education", "slug": "education", "color": "#ff5722"},
        {"name": "Entertainment", "slug": "entertainment", "color": "#ff4081"},
        {"name": "Social", "slug": "social", "color": "#40c4ff"},
        {"name": "Charity", "slug": "charity", "color": "#69f0ae"}
    ]
    
    for tag_data in tags_data:
        # Check if tag already exists
        result = await db.execute(
            select(Tag).where(Tag.slug == tag_data["slug"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            tag = Tag(**tag_data)
            db.add(tag)
            print(f"Added tag: {tag_data['name']}")
    
    await db.commit()


async def seed_admin_user(db: AsyncSession):
    """Create a default admin user."""
    
    admin_email = "admin@todayatsg.com"
    
    # Check if admin already exists
    result = await db.execute(
        select(User).where(User.email == admin_email)
    )
    existing_admin = result.scalar_one_or_none()
    
    if not existing_admin:
        admin_user = User(
            email=admin_email,
            password_hash=get_password_hash("admin123!@#"),  # Change this in production!
            first_name="System",
            last_name="Administrator",
            is_admin=True,
            is_event_organizer=True,
            is_active=True,
            is_verified=True
        )
        
        db.add(admin_user)
        await db.commit()
        print(f"Created admin user: {admin_email}")
        print("⚠️  WARNING: Change the default admin password in production!")
    else:
        print("Admin user already exists")


async def seed_sample_events(db: AsyncSession):
    """Seed sample events with Singapore locations."""
    
    # Get categories and tags for relationships
    categories_result = await db.execute(select(Category))
    categories = {cat.slug: cat for cat in categories_result.scalars().all()}
    
    tags_result = await db.execute(select(Tag))
    tags = {tag.slug: tag for tag in tags_result.scalars().all()}
    
    # Get admin user
    admin_result = await db.execute(
        select(User).where(User.email == "admin@todayatsg.com")
    )
    admin_user = admin_result.scalar_one_or_none()
    
    if not admin_user:
        print("No admin user found, skipping sample events")
        return
    
    sample_events_data = [
        # Major Festivals & Events
        {
            "title": "Singapore Night Festival 2024",
            "description": "Experience the magic of Singapore's arts and culture scene come alive after dark. The Singapore Night Festival transforms the Civic District into a vibrant outdoor gallery featuring light installations, performances, and interactive art.",
            "short_description": "Arts and culture festival in the Civic District with light installations and performances.",
            "date": date(2024, 8, 23),
            "time": time(19, 0),
            "end_date": date(2024, 8, 25),
            "end_time": time(23, 0),
            "location": "Civic District",
            "venue": "National Museum of Singapore",
            "address": "93 Stamford Rd, Singapore 178897",
            "latitude": Decimal("1.2966"),
            "longitude": Decimal("103.8486"),
            "age_restrictions": "All ages welcome",
            "price_info": "Free admission",
            "external_url": "https://www.nightfestival.gov.sg",
            "category_slug": "festivals",
            "tag_slugs": ["outdoor", "free", "art", "culture", "weekend"]
        },
        {
            "title": "Singapore Grand Prix 2024",
            "description": "The only Formula 1 night race on the calendar returns to the Marina Bay Street Circuit. Experience the thrill of high-speed racing through Singapore's iconic cityscape under the lights.",
            "short_description": "Formula 1 Singapore Grand Prix - the world's only F1 night race.",
            "date": date(2024, 9, 22),
            "time": time(20, 0),
            "end_time": time(22, 30),
            "location": "Marina Bay",
            "venue": "Marina Bay Street Circuit",
            "address": "1 Republic Blvd, Singapore 038975",
            "latitude": Decimal("1.2918"),
            "longitude": Decimal("103.8606"),
            "age_restrictions": "All ages welcome",
            "price_info": "From SGD $98",
            "external_url": "https://www.singaporegp.sg",
            "category_slug": "sports-fitness",
            "tag_slugs": ["outdoor", "paid", "marina-bay", "weekend", "entertainment"]
        },
        {
            "title": "Mid-Autumn Festival at Gardens by the Bay",
            "description": "Celebrate the Mid-Autumn Festival with stunning lantern displays, traditional performances, and family activities at Gardens by the Bay. Marvel at the giant lanterns and enjoy mooncake tastings.",
            "short_description": "Mid-Autumn Festival celebration with lantern displays and cultural performances.",
            "date": date(2024, 9, 17),
            "time": time(18, 0),
            "end_date": date(2024, 9, 17),
            "end_time": time(22, 0),
            "location": "Gardens by the Bay",
            "venue": "Supertree Grove",
            "address": "18 Marina Gardens Dr, Singapore 018953",
            "latitude": Decimal("1.2816"),
            "longitude": Decimal("103.8636"),
            "age_restrictions": "All ages welcome",
            "price_info": "Free admission",
            "external_url": "https://www.gardensbythebay.com.sg",
            "category_slug": "festivals",
            "tag_slugs": ["outdoor", "free", "family-friendly", "culture", "marina-bay"]
        },
        
        # Nightlife & Music
        {
            "title": "Zouk Singapore: Carl Cox",
            "description": "Legendary DJ Carl Cox returns to Singapore for an unforgettable night of electronic music at Zouk. Known for his energetic sets and technical prowess, Carl Cox will take you on a journey through the best of house and techno.",
            "short_description": "Carl Cox live at Zouk Singapore - legendary house and techno DJ performance.",
            "date": date(2024, 9, 15),
            "time": time(22, 0),
            "end_time": time(6, 0),
            "location": "Clarke Quay",
            "venue": "Zouk Singapore",
            "address": "3C River Valley Rd, Singapore 179022",
            "latitude": Decimal("1.2894"),
            "longitude": Decimal("103.8458"),
            "age_restrictions": "18+ only",
            "price_info": "From SGD $80",
            "external_url": "https://www.zoukclub.com.sg",
            "category_slug": "dj-events",
            "tag_slugs": ["indoor", "paid", "adults-only", "clarke-quay", "dancing", "nightlife"]
        },
        {
            "title": "Jazz at Lincoln",
            "description": "Intimate jazz sessions every Friday at Lincoln Music Lounge featuring local and international jazz musicians. Enjoy smooth cocktails and soulful music in this cozy Bugis venue.",
            "short_description": "Weekly jazz sessions at Lincoln Music Lounge in Bugis.",
            "date": date(2024, 8, 16),
            "time": time(20, 0),
            "end_time": time(23, 0),
            "location": "Bugis",
            "venue": "Lincoln Music Lounge",
            "address": "2 Stamford Rd, Singapore 178882",
            "latitude": Decimal("1.2966"),
            "longitude": Decimal("103.8520"),
            "age_restrictions": "21+ only",
            "price_info": "SGD $25 cover charge",
            "external_url": "https://www.lincolnmusiclounge.com",
            "category_slug": "concerts",
            "tag_slugs": ["indoor", "paid", "adults-only", "bugis", "live-music", "drinks"]
        },
        {
            "title": "Warehouse Party: Underground Techno",
            "description": "Experience Singapore's underground techno scene at this warehouse party featuring local DJs and special international guests. Raw industrial setting meets cutting-edge electronic music.",
            "short_description": "Underground techno warehouse party with local and international DJs.",
            "date": date(2024, 8, 31),
            "time": time(23, 0),
            "end_time": time(7, 0),
            "location": "Industrial Area",
            "venue": "Warehouse 28",
            "address": "28 Kaki Bukit Rd 3, Singapore 417837",
            "latitude": Decimal("1.3375"),
            "longitude": Decimal("103.9033"),
            "age_restrictions": "18+ only",
            "price_info": "SGD $40 early bird, SGD $60 at door",
            "external_url": "https://www.underground.sg",
            "category_slug": "dj-events",
            "tag_slugs": ["indoor", "paid", "adults-only", "dancing", "nightlife", "weekend"]
        },
        
        # Family & Kids Events
        {
            "title": "Marina Bay Sands ArtScience Museum: Future World",
            "description": "An interactive digital art exhibition where visitors can explore, play, and learn through hands-on experiences. Perfect for families, this immersive exhibition features digital installations that respond to touch and movement.",
            "short_description": "Interactive digital art exhibition perfect for families at ArtScience Museum.",
            "date": date(2024, 7, 1),
            "time": time(10, 0),
            "end_date": date(2024, 12, 31),
            "end_time": time(19, 0),
            "location": "Marina Bay",
            "venue": "ArtScience Museum",
            "address": "6 Bayfront Ave, Singapore 018974",
            "latitude": Decimal("1.2859"),
            "longitude": Decimal("103.8607"),
            "age_restrictions": "All ages welcome",
            "price_info": "Adults SGD $22, Children SGD $16",
            "external_url": "https://www.marinabaysands.com/museum.html",
            "category_slug": "kids-events",
            "tag_slugs": ["indoor", "paid", "family-friendly", "marina-bay", "art", "education"]
        },
        {
            "title": "Sentosa Beach Fun Day",
            "description": "Join us for a day of beach games, sandcastle building competitions, and water sports at Siloso Beach. Perfect family fun with activities for all ages, food vendors, and live entertainment.",
            "short_description": "Family beach day with games, competitions, and entertainment at Siloso Beach.",
            "date": date(2024, 8, 18),
            "time": time(10, 0),
            "end_time": time(17, 0),
            "location": "Sentosa",
            "venue": "Siloso Beach",
            "address": "51 Imbiah Rd, Singapore 099708",
            "latitude": Decimal("1.2494"),
            "longitude": Decimal("103.8303"),
            "age_restrictions": "All ages welcome",
            "price_info": "Free event (transport to Sentosa not included)",
            "external_url": "https://www.sentosa.com.sg",
            "category_slug": "kids-events",
            "tag_slugs": ["outdoor", "free", "family-friendly", "sentosa", "weekend"]
        },
        {
            "title": "Science Centre Singapore: Robotics Workshop",
            "description": "Kids aged 8-14 can learn basic robotics and programming in this hands-on workshop. Build and program your own robot while learning STEM concepts in a fun, interactive environment.",
            "short_description": "Hands-on robotics and programming workshop for kids at Science Centre.",
            "date": date(2024, 8, 24),
            "time": time(14, 0),
            "end_time": time(16, 0),
            "location": "Jurong East",
            "venue": "Science Centre Singapore",
            "address": "15 Science Centre Rd, Singapore 609081",
            "latitude": Decimal("1.3336"),
            "longitude": Decimal("103.7361"),
            "age_restrictions": "Ages 8-14",
            "price_info": "SGD $45 per child",
            "external_url": "https://www.science.edu.sg",
            "category_slug": "workshops",
            "tag_slugs": ["indoor", "paid", "education", "technology", "weekend"]
        },
        
        # Food & Culinary Events
        {
            "title": "Singapore Food Festival 2024",
            "description": "Celebrate Singapore's rich culinary heritage at the annual Singapore Food Festival. From hawker fare to fine dining, experience the best of local and international cuisine with special menus, cooking demonstrations, and food tours.",
            "short_description": "Annual celebration of Singapore's culinary scene with special menus and food events.",
            "date": date(2024, 7, 12),
            "time": time(11, 0),
            "end_date": date(2024, 7, 28),
            "end_time": time(22, 0),
            "location": "Islandwide",
            "venue": "Various locations",
            "address": "Multiple venues across Singapore",
            "latitude": Decimal("1.3521"),
            "longitude": Decimal("103.8198"),
            "age_restrictions": "All ages welcome",
            "price_info": "Varies by restaurant and event",
            "external_url": "https://www.singaporefoodfestival.com",
            "category_slug": "food-drink",
            "tag_slugs": ["food", "culture", "family-friendly", "weekend", "weekday"]
        },
        {
            "title": "Craft Beer Festival Singapore",
            "description": "Sample over 100 craft beers from local and international breweries at Marina Bay. Meet the brewers, enjoy food pairings, and discover new flavors in Singapore's biggest craft beer celebration.",
            "short_description": "Craft beer festival with 100+ beers from local and international breweries.",
            "date": date(2024, 9, 7),
            "time": time(17, 0),
            "end_date": date(2024, 9, 8),
            "end_time": time(23, 0),
            "location": "Marina Bay",
            "venue": "Marina Bay Event Plaza",
            "address": "10 Bayfront Ave, Singapore 018956",
            "latitude": Decimal("1.2834"),
            "longitude": Decimal("103.8607"),
            "age_restrictions": "18+ only",
            "price_info": "SGD $35 entry + tokens for drinks",
            "external_url": "https://www.craftbeerfest.sg",
            "category_slug": "food-drink",
            "tag_slugs": ["outdoor", "paid", "adults-only", "marina-bay", "drinks", "weekend"]
        },
        {
            "title": "Kids Cooking Workshop: Dim Sum Making",
            "description": "Learn to make traditional dim sum with your little ones in this hands-on cooking workshop. Children will learn about Chinese culinary traditions while creating delicious steamed dumplings and buns.",
            "short_description": "Hands-on dim sum making workshop for children and families.",
            "date": date(2024, 8, 10),
            "time": time(14, 0),
            "end_time": time(16, 30),
            "location": "Chinatown",
            "venue": "Chinatown Food Street",
            "address": "Smith St, Singapore 058934",
            "latitude": Decimal("1.2820"),
            "longitude": Decimal("103.8447"),
            "age_restrictions": "Ages 5-12 with parent/guardian",
            "price_info": "SGD $60 per child (includes one adult)",
            "external_url": "https://www.example.com/cooking-workshop",
            "category_slug": "workshops",
            "tag_slugs": ["indoor", "paid", "family-friendly", "chinatown", "food", "education"]
        },
        
        # Arts & Culture
        {
            "title": "Singapore International Jazz Festival",
            "description": "Three days of smooth jazz featuring international and local artists at Marina Bay Sands. Enjoy performances by renowned jazz musicians in an intimate setting with stunning views of the Singapore skyline.",
            "short_description": "Three-day international jazz festival at Marina Bay Sands.",
            "date": date(2024, 10, 18),
            "time": time(19, 30),
            "end_date": date(2024, 10, 20),
            "end_time": time(23, 0),
            "location": "Marina Bay",
            "venue": "Marina Bay Sands Event Plaza",
            "address": "10 Bayfront Ave, Singapore 018956",
            "latitude": Decimal("1.2834"),
            "longitude": Decimal("103.8607"),
            "age_restrictions": "All ages welcome",
            "price_info": "From SGD $120",
            "external_url": "https://www.singaporejazzfestival.com",
            "category_slug": "concerts",
            "tag_slugs": ["outdoor", "paid", "marina-bay", "live-music", "weekend"]
        },
        {
            "title": "Singapore Art Week: Gallery Hopping",
            "description": "Explore Singapore's vibrant art scene during Art Week with special exhibitions, artist talks, and gallery openings across the city. Free shuttle buses connect major art venues.",
            "short_description": "Art Week gallery hopping with exhibitions and artist talks across the city.",
            "date": date(2024, 8, 14),
            "time": time(10, 0),
            "end_date": date(2024, 8, 18),
            "end_time": time(22, 0),
            "location": "Multiple Areas",
            "venue": "Various galleries",
            "address": "Multiple locations across Singapore",
            "latitude": Decimal("1.3521"),
            "longitude": Decimal("103.8198"),
            "age_restrictions": "All ages welcome",
            "price_info": "Most events free, some premium talks SGD $20",
            "external_url": "https://www.singaporeartweek.sg",
            "category_slug": "art-culture",
            "tag_slugs": ["indoor", "free", "paid", "art", "culture", "weekday", "weekend"]
        },
        {
            "title": "National Gallery Singapore: Modern Art Exhibition",
            "description": "Discover Southeast Asian modern art at the National Gallery's latest exhibition. Featuring works by renowned regional artists, this exhibition explores themes of identity, tradition, and modernity.",
            "short_description": "Southeast Asian modern art exhibition at National Gallery Singapore.",
            "date": date(2024, 7, 15),
            "time": time(10, 0),
            "end_date": date(2024, 11, 15),
            "end_time": time(18, 0),
            "location": "Civic District",
            "venue": "National Gallery Singapore",
            "address": "1 St Andrew's Rd, Singapore 178957",
            "latitude": Decimal("1.2903"),
            "longitude": Decimal("103.8520"),
            "age_restrictions": "All ages welcome",
            "price_info": "Adults SGD $20, Students SGD $15",
            "external_url": "https://www.nationalgallery.sg",
            "category_slug": "art-culture",
            "tag_slugs": ["indoor", "paid", "art", "culture", "weekday", "weekend"]
        },
        
        # Sports & Fitness
        {
            "title": "Singapore Marathon 2024",
            "description": "Join thousands of runners in Singapore's premier marathon event. Choose from 5km, 10km, half marathon, or full marathon distances. The scenic route takes you through iconic Singapore landmarks.",
            "short_description": "Singapore's premier marathon with multiple distance options through iconic landmarks.",
            "date": date(2024, 12, 1),
            "time": time(5, 0),
            "end_time": time(12, 0),
            "location": "Multiple Areas",
            "venue": "Orchard Road (Start/Finish)",
            "address": "Orchard Rd, Singapore",
            "latitude": Decimal("1.3048"),
            "longitude": Decimal("103.8318"),
            "age_restrictions": "Varies by category, minimum age 16 for full marathon",
            "price_info": "From SGD $65 (5km) to SGD $120 (full marathon)",
            "external_url": "https://www.singaporemarathon.com",
            "category_slug": "sports-fitness",
            "tag_slugs": ["outdoor", "paid", "health", "weekend", "orchard"]
        },
        {
            "title": "Yoga by the Bay",
            "description": "Start your weekend with sunrise yoga at Marina Bay with stunning views of the city skyline. All levels welcome in this peaceful outdoor session led by certified instructors.",
            "short_description": "Sunrise yoga session at Marina Bay with city skyline views.",
            "date": date(2024, 8, 17),
            "time": time(6, 30),
            "end_time": time(7, 30),
            "location": "Marina Bay",
            "venue": "Marina Bay Waterfront",
            "address": "Marina Bay Waterfront Promenade, Singapore",
            "latitude": Decimal("1.2820"),
            "longitude": Decimal("103.8542"),
            "age_restrictions": "All ages welcome (children under 12 with adult)",
            "price_info": "SGD $15 per person",
            "external_url": "https://www.yogabythebay.sg",
            "category_slug": "sports-fitness",
            "tag_slugs": ["outdoor", "paid", "wellness", "marina-bay", "weekend"]
        },
        
        # Business & Networking
        {
            "title": "Singapore Fintech Festival",
            "description": "Asia's largest fintech festival bringing together global leaders, innovators, and startups. Network with industry experts, attend keynote sessions, and discover the latest fintech trends.",
            "short_description": "Asia's largest fintech festival with global leaders and industry networking.",
            "date": date(2024, 11, 6),
            "time": time(9, 0),
            "end_date": date(2024, 11, 8),
            "end_time": time(18, 0),
            "location": "Marina Bay",
            "venue": "Marina Bay Sands Expo",
            "address": "10 Bayfront Ave, Singapore 018956",
            "latitude": Decimal("1.2834"),
            "longitude": Decimal("103.8607"),
            "age_restrictions": "Professional event, 18+ recommended",
            "price_info": "From SGD $1,200 (3-day pass)",
            "external_url": "https://www.fintechfestival.sg",
            "category_slug": "networking",
            "tag_slugs": ["indoor", "paid", "business", "technology", "weekday", "marina-bay"]
        },
        {
            "title": "Startup Grind Singapore: Monthly Meetup",
            "description": "Monthly networking event for entrepreneurs, investors, and startup enthusiasts. Features a fireside chat with a successful founder, followed by networking drinks and startup pitches.",
            "short_description": "Monthly startup networking with founder talks and pitch sessions.",
            "date": date(2024, 8, 22),
            "time": time(18, 30),
            "end_time": time(21, 0),
            "location": "Raffles Place",
            "venue": "Google Singapore Office",
            "address": "70 Pasir Panjang Rd, Singapore 117371",
            "latitude": Decimal("1.2758"),
            "longitude": Decimal("103.7968"),
            "age_restrictions": "All ages welcome",
            "price_info": "Free for members, SGD $20 for non-members",
            "external_url": "https://www.startupgrind.com/singapore",
            "category_slug": "networking",
            "tag_slugs": ["indoor", "paid", "business", "technology", "weekday", "social"]
        }
    ]
    
    for event_data in sample_events_data:
        # Check if event already exists
        result = await db.execute(
            select(Event).where(Event.title == event_data["title"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            # Get category
            category = categories.get(event_data["category_slug"])
            if not category:
                print(f"Category {event_data['category_slug']} not found for event {event_data['title']}")
                continue
            
            # Create event without tags first
            event_dict = event_data.copy()
            del event_dict["category_slug"]
            del event_dict["tag_slugs"]
            
            event = Event(
                **event_dict,
                category_id=category.id,
                submitted_by_id=admin_user.id,
                source="admin",
                is_approved=True,
                is_active=True
            )
            
            db.add(event)
            await db.flush()  # Get the event ID
            
            # Add tags
            for tag_slug in event_data["tag_slugs"]:
                tag = tags.get(tag_slug)
                if tag:
                    event.tags.append(tag)
            
            print(f"Added sample event: {event_data['title']}")
    
    await db.commit()


async def create_sample_user_and_reviews(db: AsyncSession):
    """Create a sample user and some reviews."""
    
    sample_user_email = "user@example.com"
    
    # Check if sample user already exists
    result = await db.execute(
        select(User).where(User.email == sample_user_email)
    )
    existing_user = result.scalar_one_or_none()
    
    if not existing_user:
        sample_user = User(
            email=sample_user_email,
            password_hash=get_password_hash("password123"),
            first_name="John",
            last_name="Doe",
            is_active=True,
            is_verified=True
        )
        
        db.add(sample_user)
        await db.commit()
        await db.refresh(sample_user)
        print(f"Created sample user: {sample_user_email}")
    else:
        sample_user = existing_user
        print("Sample user already exists")
    
    # Add some sample reviews
    events_result = await db.execute(
        select(Event).where(Event.is_approved == True).limit(3)
    )
    events = events_result.scalars().all()
    
    sample_reviews = [
        {
            "rating": 5,
            "comment": "Amazing festival! The light installations were absolutely stunning and the performances were world-class. Definitely coming back next year!"
        },
        {
            "rating": 4,
            "comment": "Great night out! Carl Cox was incredible as always. The sound system at Zouk is top-notch. Only downside was the long queue to get in."
        },
        {
            "rating": 5,
            "comment": "Perfect family activity! My kids loved the interactive art installations. Educational and fun at the same time. Highly recommended for families."
        }
    ]
    
    for i, event in enumerate(events[:len(sample_reviews)]):
        # Check if review already exists
        review_result = await db.execute(
            select(Review).where(
                Review.user_id == sample_user.id,
                Review.event_id == event.id
            )
        )
        existing_review = review_result.scalar_one_or_none()
        
        if not existing_review:
            review = Review(
                user_id=sample_user.id,
                event_id=event.id,
                rating=sample_reviews[i]["rating"],
                comment=sample_reviews[i]["comment"]
            )
            
            db.add(review)
            print(f"Added sample review for event: {event.title}")
    
    await db.commit()


async def seed_database():
    """Main seeding function."""
    print("🌱 Starting database seeding...")
    
    async with AsyncSessionLocal() as db:
        try:
            print("\n📚 Seeding categories...")
            await seed_categories(db)
            
            print("\n🏷️  Seeding tags...")
            await seed_tags(db)
            
            print("\n👤 Creating admin user...")
            await seed_admin_user(db)
            
            print("\n🎉 Seeding sample events...")
            await seed_sample_events(db)
            
            print("\n⭐ Creating sample user and reviews...")
            await create_sample_user_and_reviews(db)
            
            print("\n✅ Database seeding completed successfully!")
            print("🔐 Default admin credentials:")
            print("   Email: admin@todayatsg.com")
            print("   Password: admin123!@#")
            print("   ⚠️  IMPORTANT: Change the admin password in production!")
            
        except Exception as e:
            print(f"❌ Error during seeding: {str(e)}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_database())