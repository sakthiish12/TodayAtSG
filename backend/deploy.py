#!/usr/bin/env python3
"""
Deployment script for TodayAtSG FastAPI backend.
Handles database migrations and data seeding.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.core.config import settings
from app.db.database import AsyncSessionLocal, engine
from app.db.base import Base
from app.db.seed import seed_database


async def create_tables():
    """Create database tables."""
    print("🏗️  Creating database tables...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created successfully!")


async def run_migrations():
    """Run Alembic migrations."""
    print("🔄 Running database migrations...")
    
    try:
        import subprocess
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Database migrations completed successfully!")
            if result.stdout:
                print(result.stdout)
        else:
            print("❌ Database migrations failed!")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("⚠️  Alembic not found. Skipping migrations.")
        print("   Run 'pip install alembic' to enable migrations.")
        
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False
    
    return True


async def seed_data():
    """Seed the database with initial data."""
    print("🌱 Seeding database with initial data...")
    
    try:
        await seed_database()
        print("✅ Database seeding completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Database seeding failed: {e}")
        return False


async def health_check():
    """Perform basic health checks."""
    print("🔍 Performing health checks...")
    
    checks_passed = 0
    total_checks = 4
    
    # Check database connection
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
        print("✅ Database connection: OK")
        checks_passed += 1
    except Exception as e:
        print(f"❌ Database connection: FAILED - {e}")
    
    # Check required environment variables
    required_vars = ["DATABASE_URL", "SECRET_KEY"]
    env_vars_ok = all(getattr(settings, var, None) for var in required_vars)
    
    if env_vars_ok:
        print("✅ Environment variables: OK")
        checks_passed += 1
    else:
        print("❌ Environment variables: MISSING required variables")
    
    # Check external API keys (warn if missing)
    api_keys = {
        "Google Maps": settings.GOOGLE_MAPS_API_KEY,
        "Stripe": settings.STRIPE_SECRET_KEY,
    }
    
    missing_keys = [name for name, key in api_keys.items() if not key]
    if not missing_keys:
        print("✅ External API keys: OK")
        checks_passed += 1
    else:
        print(f"⚠️  External API keys: Missing {', '.join(missing_keys)}")
        print("   The application will work but some features may be limited.")
        checks_passed += 0.5
    
    # Check file permissions
    try:
        upload_dir = Path(settings.upload_path)
        upload_dir.mkdir(parents=True, exist_ok=True)
        test_file = upload_dir / "test_write.tmp"
        test_file.write_text("test")
        test_file.unlink()
        print("✅ File permissions: OK")
        checks_passed += 1
    except Exception as e:
        print(f"❌ File permissions: FAILED - {e}")
    
    print(f"\n📊 Health check results: {checks_passed}/{total_checks} checks passed")
    return checks_passed >= total_checks * 0.75  # 75% pass rate


async def main():
    """Main deployment function."""
    print("🚀 Starting TodayAtSG Backend Deployment")
    print("=" * 50)
    
    # Show current environment
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug mode: {settings.DEBUG}")
    print(f"Database: {settings.DATABASE_URL[:50]}...")
    print("")
    
    deployment_steps = [
        ("Health Check", health_check),
        ("Database Migration", run_migrations),
        ("Database Seeding", seed_data),
        ("Final Health Check", health_check),
    ]
    
    success_count = 0
    
    for step_name, step_func in deployment_steps:
        print(f"Step: {step_name}")
        print("-" * 30)
        
        try:
            success = await step_func()
            if success:
                success_count += 1
                print(f"✅ {step_name} completed successfully!\n")
            else:
                print(f"❌ {step_name} failed!\n")
                
                # Ask if should continue
                if settings.ENVIRONMENT == "production":
                    print("🛑 Stopping deployment due to failure in production environment.")
                    break
                else:
                    continue_deployment = input("Continue deployment? (y/N): ").lower().strip()
                    if continue_deployment != 'y':
                        print("🛑 Deployment stopped by user.")
                        break
                    print("")
                        
        except KeyboardInterrupt:
            print("\n🛑 Deployment interrupted by user.")
            break
        except Exception as e:
            print(f"❌ Unexpected error in {step_name}: {e}")
            if settings.ENVIRONMENT == "production":
                break
    
    # Final status
    print("=" * 50)
    if success_count == len(deployment_steps):
        print("🎉 Deployment completed successfully!")
        print(f"🌐 API will be available at: http://localhost:8000")
        print(f"📚 API documentation: http://localhost:8000/api/docs")
        print(f"🔧 Admin panel: http://localhost:8000/api/admin")
        
        if settings.DEBUG:
            print("\n🔐 Default admin credentials:")
            print("   Email: admin@todayatsg.com")
            print("   Password: admin123!@#")
            print("   ⚠️  IMPORTANT: Change these credentials in production!")
        
        return 0
    else:
        print(f"⚠️  Deployment completed with issues ({success_count}/{len(deployment_steps)} steps successful)")
        print("Please review the errors above and fix any issues.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)