from app.database.database import SessionLocal
from app.database.models import Incident


def search_incidents(query: str):
    db = SessionLocal()

    try:
        incidents = (
            db.query(Incident)
            .filter(
                Incident.title.ilike(f"%{query}%")
                | Incident.description.ilike(f"%{query}%")
            )
            .all()
        )

        return [
            {
                "id": incident.id,
                "title": incident.title,
                "description": incident.description,
                "priority": incident.priority,
                "status": incident.status,
            }
            for incident in incidents
        ]

    finally:
        db.close()


def get_incident(incident_id: int):
    db = SessionLocal()

    try:
        # Use session.get when available (SQLAlchemy 1.4+/2.0)
        incident = db.get(Incident, incident_id)

        if incident is None:
            return None

        return {
            "id": incident.id,
            "title": incident.title,
            "description": incident.description,
            "priority": incident.priority,
            "status": incident.status,
        }

    finally:
        db.close()
        
        
def create_incident(
    title: str,
    description: str,
    priority: str,
):
    db = SessionLocal()

    try:
        incident = Incident(
            title=title,
            description=description,
            priority=priority,
            status="open",
        )

        db.add(incident)
        db.commit()
        db.refresh(incident)

        return {
            "id": incident.id,
            "title": incident.title,
            "description": incident.description,
            "priority": incident.priority,
            "status": incident.status,
        }

    finally:
        db.close()