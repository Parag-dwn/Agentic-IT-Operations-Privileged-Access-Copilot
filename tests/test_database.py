from app.database.database import SessionLocal
from app.database.models import Incident, User


def test_database_has_users():
    db = SessionLocal()

    try:
        users = db.query(User).all()
        assert len(users) >= 1
    finally:
        db.close()


def test_database_has_incidents():
    db = SessionLocal()

    try:
        incidents = db.query(Incident).all()
        assert len(incidents) >= 1
    finally:
        db.close()