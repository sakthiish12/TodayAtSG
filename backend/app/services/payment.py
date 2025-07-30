"""
Payment service for handling event submission payments via Stripe.
"""

import stripe
import structlog
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta

from app.core.config import settings
from app.models.user import User
from app.models.event import Event

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

logger = structlog.get_logger("payment")


class PaymentError(Exception):
    """Custom exception for payment-related errors."""
    pass


class PaymentService:
    """Service for handling payments via Stripe."""
    
    def __init__(self):
        self.logger = structlog.get_logger("payment_service")
    
    async def create_payment_intent(
        self,
        amount: Decimal,
        currency: str = "sgd",
        user: Optional[User] = None,
        event_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe Payment Intent for event submission.
        
        Args:
            amount: Payment amount in the smallest currency unit (cents)
            currency: Currency code (default: SGD)
            user: User making the payment
            event_data: Event data for metadata
            metadata: Additional metadata for the payment
            
        Returns:
            Dict containing payment intent data
        """
        try:
            # Convert amount to cents (Stripe uses smallest currency unit)
            amount_cents = int(amount * 100)
            
            # Prepare metadata
            payment_metadata = {
                "service": "event_submission",
                "environment": settings.ENVIRONMENT,
            }
            
            if user:
                payment_metadata.update({
                    "user_id": str(user.id),
                    "user_email": user.email,
                })
            
            if event_data:
                payment_metadata.update({
                    "event_title": event_data.get("title", "")[:500],  # Stripe limits metadata values
                    "event_category": event_data.get("category", ""),
                    "event_date": str(event_data.get("date", "")),
                })
            
            if metadata:
                payment_metadata.update(metadata)
            
            # Create payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency.lower(),
                metadata=payment_metadata,
                automatic_payment_methods={"enabled": True},
                description=f"TodayAtSG Event Submission - {event_data.get('title', 'Unknown Event') if event_data else 'Event'}",
            )
            
            self.logger.info(
                "Payment intent created",
                payment_intent_id=payment_intent.id,
                amount=amount,
                currency=currency,
                user_id=user.id if user else None,
            )
            
            return {
                "id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "amount": amount,
                "currency": currency,
                "status": payment_intent.status,
                "metadata": payment_intent.metadata,
            }
            
        except stripe.error.StripeError as e:
            self.logger.error(
                "Stripe error creating payment intent",
                error=str(e),
                amount=amount,
                currency=currency,
                user_id=user.id if user else None,
            )
            raise PaymentError(f"Payment processing error: {str(e)}")
        
        except Exception as e:
            self.logger.error(
                "Unexpected error creating payment intent",
                error=str(e),
                amount=amount,
                currency=currency,
                user_id=user.id if user else None,
                exc_info=True,
            )
            raise PaymentError(f"Unexpected payment error: {str(e)}")
    
    async def confirm_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Confirm and retrieve payment intent details.
        
        Args:
            payment_intent_id: Stripe Payment Intent ID
            
        Returns:
            Dict containing payment confirmation data
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            self.logger.info(
                "Payment intent retrieved",
                payment_intent_id=payment_intent_id,
                status=payment_intent.status,
                amount=payment_intent.amount,
            )
            
            return {
                "id": payment_intent.id,
                "status": payment_intent.status,
                "amount": payment_intent.amount / 100,  # Convert back from cents
                "currency": payment_intent.currency,
                "metadata": payment_intent.metadata,
                "created": datetime.fromtimestamp(payment_intent.created),
                "payment_method": payment_intent.payment_method,
            }
            
        except stripe.error.StripeError as e:
            self.logger.error(
                "Stripe error retrieving payment intent",
                payment_intent_id=payment_intent_id,
                error=str(e),
            )
            raise PaymentError(f"Payment confirmation error: {str(e)}")
        
        except Exception as e:
            self.logger.error(
                "Unexpected error retrieving payment intent",
                payment_intent_id=payment_intent_id,
                error=str(e),
                exc_info=True,
            )
            raise PaymentError(f"Unexpected payment confirmation error: {str(e)}")
    
    async def refund_payment(
        self,
        payment_intent_id: str,
        amount: Optional[Decimal] = None,
        reason: str = "requested_by_customer"
    ) -> Dict[str, Any]:
        """
        Refund a payment.
        
        Args:
            payment_intent_id: Stripe Payment Intent ID
            amount: Amount to refund (optional, defaults to full refund)
            reason: Reason for refund
            
        Returns:
            Dict containing refund data
        """
        try:
            # Get the payment intent first
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if payment_intent.status != "succeeded":
                raise PaymentError("Cannot refund a payment that hasn't succeeded")
            
            # Create refund
            refund_data = {
                "payment_intent": payment_intent_id,
                "reason": reason,
            }
            
            if amount:
                refund_data["amount"] = int(amount * 100)  # Convert to cents
            
            refund = stripe.Refund.create(**refund_data)
            
            self.logger.info(
                "Payment refunded",
                payment_intent_id=payment_intent_id,
                refund_id=refund.id,
                amount=refund.amount / 100,
                reason=reason,
            )
            
            return {
                "id": refund.id,
                "payment_intent_id": payment_intent_id,
                "amount": refund.amount / 100,
                "currency": refund.currency,
                "status": refund.status,
                "reason": refund.reason,
            }
            
        except stripe.error.StripeError as e:
            self.logger.error(
                "Stripe error creating refund",
                payment_intent_id=payment_intent_id,
                error=str(e),
            )
            raise PaymentError(f"Refund error: {str(e)}")
        
        except Exception as e:
            self.logger.error(
                "Unexpected error creating refund",
                payment_intent_id=payment_intent_id,
                error=str(e),
                exc_info=True,
            )
            raise PaymentError(f"Unexpected refund error: {str(e)}")
    
    async def handle_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """
        Handle Stripe webhook events.
        
        Args:
            payload: Raw webhook payload
            signature: Stripe signature header
            
        Returns:
            Dict containing webhook event data
        """
        try:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload, signature, settings.STRIPE_WEBHOOK_SECRET
            )
            
            self.logger.info(
                "Webhook event received",
                event_type=event["type"],
                event_id=event["id"],
            )
            
            # Handle different event types
            if event["type"] == "payment_intent.succeeded":
                await self._handle_payment_succeeded(event["data"]["object"])
            elif event["type"] == "payment_intent.payment_failed":
                await self._handle_payment_failed(event["data"]["object"])
            elif event["type"] == "refund.created":
                await self._handle_refund_created(event["data"]["object"])
            
            return {
                "event_type": event["type"],
                "event_id": event["id"],
                "processed": True,
            }
            
        except stripe.error.SignatureVerificationError as e:
            self.logger.error("Invalid webhook signature", error=str(e))
            raise PaymentError("Invalid webhook signature")
        
        except Exception as e:
            self.logger.error(
                "Error processing webhook",
                error=str(e),
                exc_info=True,
            )
            raise PaymentError(f"Webhook processing error: {str(e)}")
    
    async def _handle_payment_succeeded(self, payment_intent: Dict[str, Any]) -> None:
        """Handle successful payment webhook."""
        self.logger.info(
            "Payment succeeded",
            payment_intent_id=payment_intent["id"],
            amount=payment_intent["amount"] / 100,
            metadata=payment_intent.get("metadata", {}),
        )
        
        # TODO: Update event submission status in database
        # TODO: Send confirmation email to user
        # TODO: Notify admins of new paid submission
    
    async def _handle_payment_failed(self, payment_intent: Dict[str, Any]) -> None:
        """Handle failed payment webhook."""
        self.logger.warning(
            "Payment failed",
            payment_intent_id=payment_intent["id"],
            amount=payment_intent["amount"] / 100,
            metadata=payment_intent.get("metadata", {}),
            last_payment_error=payment_intent.get("last_payment_error"),
        )
        
        # TODO: Update event submission status in database
        # TODO: Send failure notification to user
    
    async def _handle_refund_created(self, refund: Dict[str, Any]) -> None:
        """Handle refund created webhook."""
        self.logger.info(
            "Refund created",
            refund_id=refund["id"],
            payment_intent_id=refund["payment_intent"],
            amount=refund["amount"] / 100,
            reason=refund["reason"],
        )
        
        # TODO: Update event submission status in database
        # TODO: Send refund confirmation to user
    
    def get_publishable_key(self) -> str:
        """Get Stripe publishable key for frontend."""
        return settings.STRIPE_PUBLISHABLE_KEY or ""


# Create global payment service instance
payment_service = PaymentService()