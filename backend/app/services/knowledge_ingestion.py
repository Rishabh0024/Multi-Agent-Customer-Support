import json
from typing import List, Dict, Any
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import KnowledgeDoc
from app.vector_store.qdrant_client import qdrant_store
from app.core.logging import logger

SAMPLE_KNOWLEDGE_DOCS = [
    {
        "title": "30-Day Return and Refund Policy",
        "category": "Returns & Refunds",
        "content": """Customers may return eligible items within 30 days of delivery for a full refund or exchange.
To qualify for a return:
1. Items must be in original condition, unwashed, and with all tags/packaging intact.
2. Electronics must include all cables, chargers, and manuals in the original box.
3. Software, downloadable items, and personalized customized products are non-refundable.

How to initiate a return:
- Go to 'My Orders' -> Select item -> Click 'Request Return'.
- A prepaid shipping label will be generated for domestic returns.
- Refunds are processed to the original payment method within 5-7 business days after inspection at our fulfillment warehouse."""
    },
    {
        "title": "Shipping Methods, Costs, and Delivery Times",
        "category": "Shipping & Logistics",
        "content": """We offer three delivery tiers across all supported regions:
1. Standard Ground Shipping: 3-5 business days. Free for orders above $50, otherwise flat $4.99.
2. Expedited Express Shipping: 2 business days. Flat $12.99.
3. Overnight Priority Shipping: Next-day delivery when ordered before 2:00 PM EST. Flat $24.99.

Tracking your package:
Once your package ships, an automated tracking email containing your FedEx/UPS tracking code is sent. You can also view live real-time carrier status on your account order details page."""
    },
    {
        "title": "1-Year Limited Hardware Warranty",
        "category": "Warranty & Repairs",
        "content": """All hardware devices manufactured by our brand carry a 1-year limited warranty covering manufacturer defects in materials and craftsmanship under normal usage.

What is covered:
- Motherboard defects, power button failure, battery health degrading below 80% within 12 months.

What is NOT covered:
- Accidental water damage, screen drops, cosmetic scratches, unauthorized modifications or third-party repairs.

To submit a warranty repair claim:
Contact support with your proof of purchase (invoice number). If approved, our team will issue an RMA (Return Merchandise Authorization) number and prepaid shipping box."""
    },
    {
        "title": "Order Cancellation Policy",
        "category": "Orders & Billing",
        "content": """Orders can be cancelled free of charge within 1 hour of placement before they enter the warehouse packing stage.
- To cancel: Navigate to 'Account' > 'Recent Orders' and click 'Cancel Order'.
- If the 1-hour window has passed and the order has already been dispatched, the order cannot be intercepted. You may refuse delivery or request a free 30-day return once delivered."""
    },
    {
        "title": "Billing Invoices and Accepted Payment Methods",
        "category": "Orders & Billing",
        "content": """We accept all major credit/debit cards (Visa, MasterCard, American Express), PayPal, Apple Pay, Google Pay, and Klarna Pay-in-4.
- Invoices: Official tax invoices with GST/VAT IDs can be downloaded as PDF from your Account Billing page immediately after purchase.
- Currency: All transactions are billed in USD or your local detected currency with zero international foreign transaction fees from our end."""
    },
    {
        "title": "Account Security and Password Recovery",
        "category": "Account & Security",
        "content": """If you forgot your password or suspect unauthorized account activity:
1. Click 'Forgot Password' on the login screen and enter your registered email address.
2. You will receive a secure password reset link valid for 15 minutes.
3. Two-Factor Authentication (2FA) is strongly recommended and can be enabled under Account Settings > Security via Google Authenticator or SMS codes."""
    }
]

async def seed_knowledge_base(db: AsyncSession):
    """Seeds both PostgreSQL and Qdrant with enterprise support documentation and restores any missing docs."""
    try:
        # Check existing docs in DB
        result = await db.execute(select(KnowledgeDoc))
        existing_docs = result.scalars().all()
        existing_titles = {d.title for d in existing_docs}

        missing_docs = [item for item in SAMPLE_KNOWLEDGE_DOCS if item["title"] not in existing_titles]

        if missing_docs:
            logger.info(f"Found {len(missing_docs)} missing knowledge documents. Seeding into PostgreSQL & Qdrant...")
            for item in missing_docs:
                # Add to Qdrant vector store
                doc_id = await qdrant_store.add_document(
                    title=item["title"],
                    content=item["content"],
                    category=item["category"]
                )

                # Add to PostgreSQL
                db_doc = KnowledgeDoc(
                    title=item["title"],
                    category=item["category"],
                    content=item["content"],
                    embedding_id=doc_id,
                    metadata_info={"source": "seed_data"}
                )
                db.add(db_doc)

            await db.commit()
            logger.info(f"Successfully seeded/restored {len(missing_docs)} documents into PostgreSQL and Qdrant.")
        else:
            logger.info(f"Knowledge base is healthy. All {len(existing_docs)} default documents present.")
    except Exception as e:
        logger.error(f"Error seeding knowledge base: {e}")
