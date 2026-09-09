from app.database.database import SessionLocal
from app.database.models import (
    AccessRequest,
    AuditLog,
    Entitlement,
    Incident,
    User,
)


def seed_database():
    db = SessionLocal()

    try:
        users = [
            User(
                username="rahul.sharma",
                full_name="Rahul Sharma",
                department="Finance",
                email="rahul.sharma@example.com",
            ),
            User(
                username="priya.verma",
                full_name="Priya Verma",
                department="IT",
                email="priya.verma@example.com",
            ),
            User(
                username="admin.user",
                full_name="Admin User",
                department="Security",
                email="admin.user@example.com",
            ),
        ]

        db.add_all(users)
        db.flush()

        entitlements = [
            Entitlement(
                user_id=users[0].id,
                resource="finance-db",
                role="read-only",
            ),
            Entitlement(
                user_id=users[1].id,
                resource="it-support",
                role="operator",
            ),
            Entitlement(
                user_id=users[2].id,
                resource="production-db",
                role="security-admin",
            ),
        ]

        incidents = [
            Incident(
                title="VPN Authentication Failure",
                description=(
                    "Users are experiencing intermittent VPN "
                    "authentication failures."
                ),
                priority="P1",
                status="investigating",
            ),
            Incident(
                title="Finance Application Slow",
                description=(
                    "Finance application response times are "
                    "higher than normal."
                ),
                priority="P2",
                status="monitoring",
            ),
        ]

        db.add_all(entitlements)
        db.add_all(incidents)

        db.commit()

        print("Database seeded successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()