"""Payment endpoints for event submission payments."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from decimal import Decimal
import structlog

from app.db.database import get_db
from app.core.security import get_current_active_user
from app.core.config import settings
from app.models.user import User
from app.services.payment import payment_service, PaymentError
from pydantic import BaseModel

router = APIRouter()
logger = structlog.get_logger("payment_api")


class PaymentIntentRequest(BaseModel):
    """Request model for creating payment intent."""
    amount: Decimal
    currency: str = "sgd"
    event_title: str
    event_category: str
    event_date: str


class PaymentIntentResponse(BaseModel):
    """Response model for payment intent creation."""
    id: str
    client_secret: str
    amount: Decimal
    currency: str
    status: str
    publishable_key: str


class PaymentConfirmationRequest(BaseModel):
    """Request model for payment confirmation."""
    payment_intent_id: str


class PaymentConfirmationResponse(BaseModel):
    """Response model for payment confirmation."""
    id: str
    status: str
    amount: Decimal
    currency: str
    success: bool


@router.post("/create-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    payment_request: PaymentIntentRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create a Stripe Payment Intent for event submission."""
    
    try:
        # Validate amount (should match event submission price)
        expected_amount = Decimal(str(settings.EVENT_SUBMISSION_PRICE_SGD))
        if payment_request.amount != expected_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid payment amount. Expected SGD {expected_amount}"
            )
        
        # Check if user can submit free events
        if current_user.can_submit_free_event():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have free event submissions available. No payment required."
            )
        
        # Prepare event data for payment metadata
        event_data = {
            "title": payment_request.event_title,
            "category": payment_request.event_category,
            "date": payment_request.event_date,
        }
        
        # Create payment intent
        payment_intent = await payment_service.create_payment_intent(
            amount=payment_request.amount,
            currency=payment_request.currency,
            user=current_user,
            event_data=event_data,
            metadata={
                "user_id": str(current_user.id),
                "purpose": "event_submission",
            }
        )
        
        logger.info(
            "Payment intent created for user",
            user_id=current_user.id,
            payment_intent_id=payment_intent["id"],
            amount=payment_request.amount,
            event_title=payment_request.event_title,
        )
        
        return PaymentIntentResponse(
            id=payment_intent["id"],
            client_secret=payment_intent["client_secret"],
            amount=payment_intent["amount"],
            currency=payment_intent["currency"],
            status=payment_intent["status"],
            publishable_key=payment_service.get_publishable_key(),
        )
        
    except PaymentError as e:
        logger.error(
            "Payment error creating intent",
            user_id=current_user.id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(
            "Unexpected error creating payment intent",
            user_id=current_user.id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment processing error"
        )


@router.post("/confirm", response_model=PaymentConfirmationResponse)
async def confirm_payment(
    confirmation_request: PaymentConfirmationRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Confirm a payment and return status."""
    
    try:
        # Retrieve payment intent from Stripe
        payment_details = await payment_service.confirm_payment(
            confirmation_request.payment_intent_id
        )
        
        is_successful = payment_details["status"] == "succeeded"
        
        logger.info(
            "Payment confirmation checked",
            user_id=current_user.id,
            payment_intent_id=confirmation_request.payment_intent_id,
            status=payment_details["status"],
            success=is_successful,
        )
        
        return PaymentConfirmationResponse(
            id=payment_details["id"],
            status=payment_details["status"],
            amount=payment_details["amount"],
            currency=payment_details["currency"],
            success=is_successful,
        )
        
    except PaymentError as e:
        logger.error(
            "Payment error confirming payment",
            user_id=current_user.id,
            payment_intent_id=confirmation_request.payment_intent_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(
            "Unexpected error confirming payment",
            user_id=current_user.id,
            payment_intent_id=confirmation_request.payment_intent_id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment confirmation error"
        )


@router.post("/webhook")
async def payment_webhook(request: Request) -> Any:
    """Handle Stripe webhook events."""
    
    try:
        # Get raw payload and signature
        payload = await request.body()
        signature = request.headers.get("Stripe-Signature", "")
        
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing Stripe signature"
            )
        
        # Process webhook
        webhook_result = await payment_service.handle_webhook(payload, signature)
        
        logger.info(
            "Webhook processed",
            event_type=webhook_result["event_type"],
            event_id=webhook_result["event_id"],
        )
        
        return {"received": True}
        
    except PaymentError as e:
        logger.error("Webhook processing error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error("Unexpected webhook error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing error"
        )


@router.get("/config")
async def get_payment_config(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get payment configuration for frontend."""
    
    return {
        "publishable_key": payment_service.get_publishable_key(),
        "currency": "sgd",
        "event_submission_price": settings.EVENT_SUBMISSION_PRICE_SGD,
        "free_events_per_month": settings.FREE_EVENTS_PER_ORGANIZER_PER_MONTH,
        "user_can_submit_free": current_user.can_submit_free_event(),
    }