import logging
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    user = db.query(User).filter(User.email == "admin@shieldai.com").first()
    if not user:
        user = User(
            email="admin@shieldai.com",
            hashed_password=get_password_hash("admin123"),
            name="Admin User",
            is_superuser=True,
        )
        db.add(user)
        db.commit()
        logger.info("Admin user created")
    else:
        logger.info("Admin user already exists")

def main() -> None:
    logger.info("Initializing database")
    db = SessionLocal()
    init_db(db)
    logger.info("Database initialized")

if __name__ == "__main__":
    main()
