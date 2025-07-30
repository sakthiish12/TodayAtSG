#!/usr/bin/env python3
"""
Simple test to check if the FastAPI app can import and start
"""
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_basic_import():
    """Test basic imports work"""
    try:
        from app.main import app
        print("✅ FastAPI app imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import FastAPI app: {e}")
        return False

def test_basic_routes():
    """Test basic route structure"""
    try:
        from app.main import app
        routes = [route.path for route in app.routes]
        print(f"✅ Found {len(routes)} routes: {routes[:5]}...")
        return True
    except Exception as e:
        print(f"❌ Failed to check routes: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing TodayAtSG Backend...")
    
    # Test basic imports
    if not test_basic_import():
        sys.exit(1)
    
    # Test basic routes
    if not test_basic_routes():
        sys.exit(1)
    
    print("🎉 Basic backend tests passed!")