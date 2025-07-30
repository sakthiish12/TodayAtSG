"""
Serverless database configuration for Vercel deployment.
Optimized for serverless functions with connection pooling and cold start handling.
"""

import os
import logging
from typing import Optional
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
import asyncpg

logger = logging.getLogger(__name__)

class ServerlessDatabase:
    """Database manager optimized for serverless environments."""
    
    def __init__(self):
        self.engine: Optional[create_async_engine] = None
        self.session_factory: Optional[async_sessionmaker] = None
        self._initialized = False
    
    def _get_database_url(self) -> str:
        """Get database URL from environment variables."""
        # Try different environment variable names for flexibility
        db_url = (
            os.getenv("DATABASE_URL") or
            os.getenv("NEON_DATABASE_URL") or
            os.getenv("SUPABASE_DATABASE_URL") or
            os.getenv("POSTGRES_URL")
        )
        
        if not db_url:
            raise ValueError("No database URL found in environment variables")
        
        # Convert postgres:// to postgresql+asyncpg:// if needed
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif not db_url.startswith("postgresql+asyncpg://"):
            if db_url.startswith("postgresql://"):
                db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        return db_url
    
    async def initialize(self):
        """Initialize database connection with serverless optimizations."""
        if self._initialized:
            return
        
        try:
            db_url = self._get_database_url()
            
            # Create engine with serverless-optimized settings
            self.engine = create_async_engine(
                db_url,
                # Use NullPool for serverless - no persistent connections
                poolclass=NullPool,
                # Disable connection pooling entirely for serverless
                pool_pre_ping=True,
                pool_recycle=300,  # 5 minutes
                # Optimize for serverless cold starts
                connect_args={
                    "server_settings": {
                        "jit": "off",  # Disable JIT for faster cold starts
                        "application_name": "todayatsg_serverless",
                    },
                    "command_timeout": 10,
                    "server_timeout": 10,
                },
                # Echo SQL in development
                echo=os.getenv("ENVIRONMENT", "production") == "development",
            )
            
            # Create session factory
            self.session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=True,
                autocommit=False,
            )
            
            self._initialized = True
            logger.info("Database initialized for serverless environment")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    @asynccontextmanager
    async def get_session(self):
        """Get database session with proper cleanup."""
        if not self._initialized:
            await self.initialize()
        
        session = self.session_factory()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()
    
    async def health_check(self) -> bool:
        """Check database connectivity."""
        try:
            if not self._initialized:
                await self.initialize()
            
            async with self.get_session() as session:
                result = await session.execute("SELECT 1")
                return result.scalar() == 1
                
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def close(self):
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()
            self._initialized = False
            logger.info("Database connections closed")

# Create global database instance
db_manager = ServerlessDatabase()

# Dependency for FastAPI
async def get_database_session():
    """FastAPI dependency for database sessions."""
    async with db_manager.get_session() as session:
        yield session

# Health check function
async def check_database_health() -> dict:
    """Health check for database connectivity."""
    is_healthy = await db_manager.health_check()
    return {
        "database": "healthy" if is_healthy else "unhealthy",
        "connection_pool": "serverless_nullpool",
        "initialized": db_manager._initialized,
    }

# Startup and shutdown handlers
async def startup_database():
    """Initialize database on startup."""
    await db_manager.initialize()

async def shutdown_database():
    """Clean up database connections on shutdown."""
    await db_manager.close()