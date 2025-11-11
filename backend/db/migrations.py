"""
Database migrations - Auto-create tables and seed data
Runs on application startup
"""
from sqlalchemy import text
from db.database import engine
from db.models import Base, CompanyPolicy, ComplianceScore
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)


async def run_migrations():
    """Create all tables and seed initial data"""
    try:
        logger.info("🔄 Running database migrations...")
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ Database tables created")
        
        # Seed initial data
        await seed_initial_data()
        
        logger.info("✅ Database migrations completed")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise


async def seed_initial_data():
    """Seed database with sample company policies and initial compliance score"""
    from db.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        try:
            # Check if data already exists
            result = await session.execute(text("SELECT COUNT(*) FROM company_policies"))
            count = result.scalar()
            
            if count > 0:
                logger.info("📊 Sample data already exists, skipping seed")
                return
            
            logger.info("🌱 Seeding initial data...")
            
            # Sample Company Policy 1: KYC Requirements
            policy1 = CompanyPolicy(
                id=str(uuid.uuid4()),
                policy_name="KYC and Customer Due Diligence",
                policy_version="v2.1",
                section_number="3.2",
                section_title="Customer Identification Process",
                content="""
                All customers must provide valid government-issued identification.
                For individual accounts, acceptable documents include:
                - Aadhaar Card
                - PAN Card
                - Passport
                - Voter ID
                
                Additional proof of address required within 6 months.
                Video KYC permitted for accounts below ₹50,000.
                Physical verification mandatory for high-value accounts (>₹10 lakhs).
                Re-KYC required every 10 years for regular accounts.
                """,
                last_updated=datetime.utcnow(),
                is_active=True
            )
            
            # Sample Company Policy 2: AML Monitoring
            policy2 = CompanyPolicy(
                id=str(uuid.uuid4()),
                policy_name="Anti-Money Laundering Framework",
                policy_version="v1.8",
                section_number="5.1",
                section_title="Transaction Monitoring Thresholds",
                content="""
                Automated monitoring for suspicious transaction patterns:
                - Cash deposits >₹10 lakhs in a single day
                - Multiple cash deposits totaling >₹20 lakhs in a month
                - International wire transfers >$10,000 USD
                - Structuring patterns (multiple transactions just below threshold)
                
                Alert generation for manual review within 24 hours.
                Escalation to Compliance Officer for amounts >₹50 lakhs.
                Suspicious Transaction Reports (STR) filed within 7 days.
                Customer risk scoring updated quarterly.
                """,
                last_updated=datetime.utcnow(),
                is_active=True
            )
            
            # Sample Company Policy 3: Digital Lending
            policy3 = CompanyPolicy(
                id=str(uuid.uuid4()),
                policy_name="Digital Lending Operations",
                policy_version="v1.2",
                section_number="2.4",
                section_title="Interest Rate Disclosure",
                content="""
                All digital lending products must clearly disclose:
                - Annual Percentage Rate (APR) inclusive of all charges
                - Processing fees (maximum 2% of loan amount)
                - Late payment charges (not exceeding ₹500 or 3% per month)
                - Prepayment charges clearly stated (currently waived)
                
                Loan agreements sent via registered email and SMS.
                Cooling-off period of 3 days for loans >₹1 lakh.
                Disbursement only to customer's verified bank account.
                Recovery practices comply with RBI Fair Practices Code.
                """,
                last_updated=datetime.utcnow(),
                is_active=True
            )
            
            session.add_all([policy1, policy2, policy3])
            
            # Initial Compliance Score
            initial_score = ComplianceScore(
                id=str(uuid.uuid4()),
                score=82.0,
                total_circulars=0,
                pending_reviews=0,
                critical_issues=0,
                high_issues=0,
                score_breakdown={
                    "kyc_aml": 85,
                    "digital_lending": 78,
                    "payments": 83,
                    "cyber_security": 80,
                    "data_privacy": 82
                },
                calculated_at=datetime.utcnow(),
                notes="Initial baseline score before circular processing"
            )
            
            session.add(initial_score)
            
            await session.commit()
            logger.info("✅ Sample policies and initial score seeded")
            
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ Seed data failed: {e}")
            raise


async def drop_all_tables():
    """Drop all tables (use with caution!)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.warning("⚠️ All tables dropped")
