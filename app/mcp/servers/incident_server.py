import sys
from pathlib import Path

# Ensure the repository root is on sys.path so `app` imports work when
# this file is executed as a script (e.g. `python app/mcp/servers/incident_server.py`).
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mcp.server import MCPServer

from app.services.incident_service import (
    create_incident as create_incident_service,
    get_incident as get_incident_service,
    search_incidents as search_incidents_service,
)

mcp = MCPServer("Incident Management Server")


@mcp.tool()
def search_incidents(query: str) -> list[dict]:
    """
    Search IT incidents by title or description.

    Args:
        query: Search keyword such as VPN, database, network, etc.
    """
    return search_incidents_service(query)


@mcp.tool()
def get_incident(incident_id: int) -> dict:
    """
    Retrieve a specific IT incident.

    Args:
        incident_id: Numeric incident ID.
    """
    incident = get_incident_service(incident_id)

    if incident is None:
        return {
            "error": f"Incident {incident_id} was not found."
        }

    return incident

@mcp.tool()
def create_incident(
    title: str,
    description: str,
    priority: str,
) -> dict:
    """
    Create a new IT incident.

    Args:
        title: Short incident title.
        description: Detailed description.
        priority: Incident priority: P1, P2, P3 or P4.
    """

    allowed_priorities = {"P1", "P2", "P3", "P4"}

    if priority not in allowed_priorities:
        return {
            "error": (
                f"Invalid priority '{priority}'. "
                f"Allowed values: {sorted(allowed_priorities)}"
            )
        }

    return create_incident_service(
        title=title,
        description=description,
        priority=priority,
    )        
        
def main():
    mcp.run()


if __name__ == "__main__":
    main()  