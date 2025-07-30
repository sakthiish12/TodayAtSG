from fastapi import APIRouter

from app.api.endpoints import events, auth, categories, tags, reviews, users, admin, payment, scraping

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(events.router, prefix="/events", tags=["Events"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(tags.router, prefix="/tags", tags=["Tags"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(payment.router, prefix="/payment", tags=["Payment"])
api_router.include_router(scraping.router, prefix="/admin/scraping", tags=["Admin", "Scraping"])