#!/usr/bin/env python3
"""
Database Integration Test Suite for TodayAtSG

This script tests all major database operations including:
- Database connections and migrations
- CRUD operations for all models
- Geolocation queries and distance calculations
- Data integrity and constraint validation
- Performance of indexed queries

Run with: python test_database.py
"""

import asyncio
import sys
from pathlib import Path
from decimal import Decimal
from datetime import date, time, datetime

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import select, text, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import AsyncSessionLocal
from app.models.user import User
from app.models.category import Category
from app.models.tag import Tag
from app.models.event import Event
from app.models.review import Review
from app.utils.geolocation import (
    haversine_distance, 
    find_nearby_events, 
    is_within_singapore,
    get_nearest_singapore_location,
    GeolocationService
)


class DatabaseTestSuite:
    """Comprehensive database test suite."""
    
    def __init__(self):
        self.async_session = AsyncSessionLocal
        self.test_results = []
        
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({'name': test_name, 'passed': passed, 'message': message})
        print(f"{status}: {test_name}")
        if message and not passed:
            print(f"    Error: {message}")

    async def test_database_connections(self):
        """Test basic database connectivity."""
        print("\n🔌 Testing Database Connections...")
        
        try:
            async with self.async_session() as db:
                result = await db.execute(text("SELECT 1"))
                assert result.scalar() == 1
                self.log_test("Async database connection", True)
        except Exception as e:
            self.log_test("Async database connection", False, str(e))

    async def test_table_structure(self):
        """Test that all expected tables exist with correct structure."""
        print("\n📋 Testing Table Structure...")
        
        expected_tables = ['users', 'categories', 'tags', 'events', 'reviews', 'event_tags']
        
        try:
            async with self.async_session() as db:
                # Check table existence
                result = await db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                existing_tables = [row[0] for row in result.fetchall()]
                
                for table in expected_tables:
                    if table in existing_tables:
                        self.log_test(f"Table '{table}' exists", True)
                    else:
                        self.log_test(f"Table '{table}' exists", False, "Table missing")
                
                # Check for indexes (performance indicators)
                result = await db.execute(text("SELECT name FROM sqlite_master WHERE type='index'"))
                indexes = [row[0] for row in result.fetchall()]
                
                # Critical indexes for performance
                critical_indexes = [
                    'idx_events_location_coords',
                    'idx_events_date_approved_active',
                    'idx_events_category_date_approved'
                ]
                
                for index in critical_indexes:
                    if index in indexes:
                        self.log_test(f"Performance index '{index}' exists", True)
                    else:
                        self.log_test(f"Performance index '{index}' exists", False, "Index missing")
                        
        except Exception as e:
            self.log_test("Table structure check", False, str(e))

    async def test_crud_operations(self):
        """Test Create, Read, Update, Delete operations for all models."""
        print("\n📝 Testing CRUD Operations...")
        
        try:
            async with self.async_session() as db:
                # Test Category CRUD
                test_category = Category(
                    name="Test Category",
                    slug="test-category",
                    description="Test category for validation",
                    sort_order=999
                )
                db.add(test_category)
                await db.commit()
                await db.refresh(test_category)
                
                # Read
                result = await db.execute(select(Category).where(Category.slug == "test-category"))
                found_category = result.scalar_one_or_none()
                assert found_category is not None
                assert found_category.name == "Test Category"
                self.log_test("Category CRUD operations", True)
                
                # Test Tag CRUD
                test_tag = Tag(
                    name="Test Tag",
                    slug="test-tag",
                    color="#FF0000"
                )
                db.add(test_tag)
                await db.commit()
                await db.refresh(test_tag)
                
                result = await db.execute(select(Tag).where(Tag.slug == "test-tag"))
                found_tag = result.scalar_one_or_none()
                assert found_tag is not None
                self.log_test("Tag CRUD operations", True)
                
                # Test User CRUD
                test_user = User(
                    email="test@example.com",
                    password_hash="hashed_password",
                    first_name="Test",
                    last_name="User",
                    is_active=True,
                    is_verified=True
                )
                db.add(test_user)
                await db.commit()
                await db.refresh(test_user)
                
                result = await db.execute(select(User).where(User.email == "test@example.com"))
                found_user = result.scalar_one_or_none()
                assert found_user is not None
                self.log_test("User CRUD operations", True)
                
                # Test Event CRUD with relationships
                test_event = Event(
                    title="Test Event",
                    description="A test event for validation",
                    short_description="Test event",
                    date=date(2024, 12, 25),
                    time=time(14, 30),
                    location="Marina Bay",
                    venue="Test Venue",
                    address="123 Test Street, Singapore 123456",
                    latitude=Decimal("1.2806"),
                    longitude=Decimal("103.8598"),
                    category_id=found_category.id,
                    submitted_by_id=found_user.id,
                    is_approved=True,
                    is_active=True,
                    source="test"
                )
                db.add(test_event)
                await db.commit()
                await db.refresh(test_event)
                
                # Add tag relationship
                test_event.tags.append(found_tag)
                await db.commit()
                
                result = await db.execute(select(Event).where(Event.title == "Test Event"))
                found_event = result.scalar_one_or_none()
                assert found_event is not None
                assert found_event.category_id == found_category.id
                self.log_test("Event CRUD with relationships", True)
                
                # Test Review CRUD
                test_review = Review(
                    user_id=found_user.id,
                    event_id=found_event.id,
                    rating=5,
                    comment="Great test event!"
                )
                db.add(test_review)
                await db.commit()
                
                result = await db.execute(select(Review).where(Review.user_id == found_user.id))
                found_review = result.scalar_one_or_none()
                assert found_review is not None
                assert found_review.rating == 5
                self.log_test("Review CRUD operations", True)
                
                # Clean up test data
                await db.delete(test_review)
                await db.delete(test_event)
                await db.delete(test_user)
                await db.delete(test_tag)
                await db.delete(test_category)
                await db.commit()
                
        except Exception as e:
            self.log_test("CRUD operations", False, str(e))

    async def test_data_constraints(self):
        """Test database constraints and validation rules."""
        print("\n🔒 Testing Data Constraints...")
        
        try:
            async with self.async_session() as db:
                # Test unique constraints
                try:
                    category1 = Category(name="Unique Test", slug="unique-test", sort_order=1)
                    category2 = Category(name="Unique Test 2", slug="unique-test", sort_order=2)  # Same slug
                    
                    db.add(category1)
                    db.add(category2)
                    await db.commit()
                    
                    self.log_test("Unique constraint enforcement", False, "Duplicate slug allowed")
                except Exception:
                    self.log_test("Unique constraint enforcement", True)
                    await db.rollback()
                
                # Test check constraints (rating range)
                try:
                    # First create valid user and event
                    test_user = User(email="constraint@test.com", password_hash="hash", is_active=True)
                    test_category = Category(name="Constraint Test", slug="constraint-test", sort_order=1)
                    db.add(test_user)
                    db.add(test_category)
                    await db.commit()
                    await db.refresh(test_user)
                    await db.refresh(test_category)
                    
                    test_event = Event(
                        title="Constraint Test Event",
                        date=date(2024, 9, 1),
                        time=time(14, 0),
                        location="Test Location",
                        category_id=test_category.id,
                        is_approved=True,
                        is_active=True,
                        source="test"
                    )
                    db.add(test_event)
                    await db.commit()
                    await db.refresh(test_event)
                    
                    # Try invalid rating
                    invalid_review = Review(
                        user_id=test_user.id,
                        event_id=test_event.id,
                        rating=6,  # Invalid - should be 1-5
                        comment="Invalid rating test"
                    )
                    db.add(invalid_review)
                    await db.commit()
                    
                    self.log_test("Check constraint enforcement (rating)", False, "Invalid rating allowed")
                except Exception:
                    self.log_test("Check constraint enforcement (rating)", True)
                    await db.rollback()
                
        except Exception as e:
            self.log_test("Data constraints test", False, str(e))

    async def test_geolocation_functions(self):
        """Test geolocation utilities and queries."""
        print("\n🌍 Testing Geolocation Functions...")
        
        try:
            # Test haversine distance calculation
            # Distance between Marina Bay and Orchard Road (known distance ~3km)
            distance = haversine_distance(1.2806, 103.8598, 1.3048, 103.8318)
            expected_distance = 3.0  # Approximate
            
            if abs(distance - expected_distance) < 1.0:  # Within 1km tolerance
                self.log_test("Haversine distance calculation", True)
            else:
                self.log_test("Haversine distance calculation", False, 
                            f"Expected ~{expected_distance}km, got {distance:.2f}km")
            
            # Test Singapore bounds validation
            valid_coords = is_within_singapore(1.2806, 103.8598)  # Marina Bay
            invalid_coords = is_within_singapore(0.0, 0.0)  # Null Island
            
            if valid_coords and not invalid_coords:
                self.log_test("Singapore bounds validation", True)
            else:
                self.log_test("Singapore bounds validation", False, 
                            f"Marina Bay valid: {valid_coords}, Null Island valid: {invalid_coords}")
            
            # Test nearest location finding
            nearest = get_nearest_singapore_location(1.2806, 103.8598)  # Marina Bay coordinates
            if nearest and nearest['key'] == 'marina_bay':
                self.log_test("Nearest location detection", True)
            else:
                self.log_test("Nearest location detection", False, 
                            f"Expected marina_bay, got {nearest['key'] if nearest else None}")
            
        except Exception as e:
            self.log_test("Geolocation functions test", False, str(e))

    async def test_geolocation_queries(self):
        """Test database queries with geolocation filtering."""
        print("\n📍 Testing Geolocation Database Queries...")
        
        try:
            async with self.async_session() as db:
                # Create test data for geolocation queries
                test_category = Category(name="Geo Test", slug="geo-test", sort_order=1)
                db.add(test_category)
                await db.commit()
                await db.refresh(test_category)
                
                # Create events at known Singapore locations
                test_events = [
                    Event(
                        title="Marina Bay Event",
                        date=date(2024, 9, 1),
                        time=time(14, 0),
                        location="Marina Bay",
                        latitude=Decimal("1.2806"),
                        longitude=Decimal("103.8598"),
                        category_id=test_category.id,
                        is_approved=True,
                        is_active=True,
                        source="test"
                    ),
                    Event(
                        title="Orchard Event",
                        date=date(2024, 9, 1),
                        time=time(15, 0),
                        location="Orchard Road",
                        latitude=Decimal("1.3048"),
                        longitude=Decimal("103.8318"),
                        category_id=test_category.id,
                        is_approved=True,
                        is_active=True,
                        source="test"
                    ),
                    Event(
                        title="Jurong Event",
                        date=date(2024, 9, 1),
                        time=time(16, 0),
                        location="Jurong East",
                        latitude=Decimal("1.3329"),
                        longitude=Decimal("103.7436"),
                        category_id=test_category.id,
                        is_approved=True,
                        is_active=True,
                        source="test"
                    )
                ]
                
                for event in test_events:
                    db.add(event)
                await db.commit()
                
                # Test finding nearby events from Marina Bay (should find Marina Bay and Orchard, not Jurong)
                nearby_events = await find_nearby_events(
                    db=db,
                    center_lat=1.2806,  # Marina Bay
                    center_lng=103.8598,
                    radius_km=5.0  # 5km radius
                )
                
                nearby_titles = [event['title'] for event in nearby_events]
                
                # Should find Marina Bay Event (0km) and Orchard Event (~3km), but not Jurong Event (~25km)
                if "Marina Bay Event" in nearby_titles and "Orchard Event" in nearby_titles:
                    if "Jurong Event" not in nearby_titles:
                        self.log_test("Geolocation radius filtering", True)
                    else:
                        self.log_test("Geolocation radius filtering", False, "Jurong event found within 5km of Marina Bay")
                else:
                    self.log_test("Geolocation radius filtering", False, 
                                f"Expected nearby events not found. Found: {nearby_titles}")
                
                # Test distance calculation accuracy
                marina_event = next((e for e in nearby_events if e['title'] == "Marina Bay Event"), None)
                if marina_event and marina_event['distance_km'] < 0.1:  # Should be very close
                    self.log_test("Distance calculation accuracy", True)
                else:
                    self.log_test("Distance calculation accuracy", False, 
                                f"Marina Bay event distance: {marina_event['distance_km'] if marina_event else 'Not found'}")
                
                # Clean up test data
                for event in test_events:
                    await db.delete(event)
                await db.delete(test_category)
                await db.commit()
                
        except Exception as e:
            self.log_test("Geolocation database queries", False, str(e))

    async def test_query_performance(self):
        """Test query performance with indexes."""
        print("\n⚡ Testing Query Performance...")
        
        try:
            async with self.async_session() as db:
                # Test index usage by running common queries and measuring execution
                import time
                
                # Test geolocation query performance
                start_time = time.time()
                result = await db.execute(
                    select(Event).where(
                        Event.latitude.between(1.2, 1.4),
                        Event.longitude.between(103.6, 104.0),
                        Event.is_approved == True,
                        Event.is_active == True
                    ).limit(50)
                )
                events = result.scalars().all()
                geo_query_time = time.time() - start_time
                
                if geo_query_time < 1.0:  # Should complete within 1 second
                    self.log_test("Geolocation query performance", True, f"{geo_query_time:.3f}s")
                else:
                    self.log_test("Geolocation query performance", False, f"Slow query: {geo_query_time:.3f}s")
                
                # Test category-based query performance
                start_time = time.time()
                result = await db.execute(
                    select(Event).where(
                        Event.category_id == 1,
                        Event.is_approved == True,
                        Event.date >= date(2024, 1, 1)
                    ).limit(20)
                )
                events = result.scalars().all()
                category_query_time = time.time() - start_time
                
                if category_query_time < 0.5:  # Should be very fast with indexes
                    self.log_test("Category query performance", True, f"{category_query_time:.3f}s")
                else:
                    self.log_test("Category query performance", False, f"Slow query: {category_query_time:.3f}s")
                
        except Exception as e:
            self.log_test("Query performance test", False, str(e))

    async def test_data_integrity(self):
        """Test referential integrity and cascading operations."""
        print("\n🔗 Testing Data Integrity...")
        
        try:
            async with self.async_session() as db:
                # Create test data with relationships
                test_user = User(email="integrity@test.com", password_hash="hash", is_active=True)
                test_category = Category(name="Integrity Test", slug="integrity-test", sort_order=1)
                
                db.add(test_user)
                db.add(test_category)
                await db.commit()
                await db.refresh(test_user)
                await db.refresh(test_category)
                
                test_event = Event(
                    title="Integrity Test Event",
                    date=date(2024, 9, 1),
                    time=time(14, 0),
                    location="Test Location",
                    category_id=test_category.id,
                    submitted_by_id=test_user.id,
                    is_approved=True,
                    is_active=True,
                    source="test"
                )
                db.add(test_event)
                await db.commit()
                await db.refresh(test_event)
                
                test_review = Review(
                    user_id=test_user.id,
                    event_id=test_event.id,
                    rating=4,
                    comment="Integrity test review"
                )
                db.add(test_review)
                await db.commit()
                
                # Test cascading delete (delete user should cascade to reviews)
                await db.delete(test_user)
                await db.commit()
                
                # Check if review was cascaded
                result = await db.execute(select(Review).where(Review.id == test_review.id))
                remaining_review = result.scalar_one_or_none()
                
                if remaining_review is None:
                    self.log_test("Cascading delete (user -> reviews)", True)
                else:
                    self.log_test("Cascading delete (user -> reviews)", False, "Review not deleted")
                
                # Clean up remaining test data
                await db.delete(test_event)
                await db.delete(test_category)
                await db.commit()
                
        except Exception as e:
            self.log_test("Data integrity test", False, str(e))

    async def run_all_tests(self):
        """Run the complete test suite."""
        print("🧪 Starting TodayAtSG Database Test Suite")
        print("=" * 60)
        
        # Run all test categories
        await self.test_database_connections()
        await self.test_table_structure()
        await self.test_crud_operations()
        await self.test_data_constraints()
        await self.test_geolocation_functions()
        await self.test_geolocation_queries()
        await self.test_query_performance()
        await self.test_data_integrity()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Test Results Summary")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  - {result['name']}: {result['message']}")
        
        print(f"\n{'✅ All tests passed!' if failed_tests == 0 else '❌ Some tests failed. Check the issues above.'}")
        
        return failed_tests == 0


async def main():
    """Run the database test suite."""
    test_suite = DatabaseTestSuite()
    success = await test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())