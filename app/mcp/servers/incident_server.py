import sys
from pathlib import Path

# Ensure the repository root is on sys.path so `app` imports work when
# this file is executed as a script (e.g. `python app/mcp/servers/incident_server.py`).
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mcp.server import MCPServer

from app.services.access_service import (
    approve_access_request as approve_access_request_service,
    create_access_request as create_access_request_service,
    get_access_request as get_access_request_service,
)
from app.services.incident_service import (
    create_incident as create_incident_service,
    get_incident as get_incident_service,
    search_incidents as search_incidents_service,
)

mcp = MCPServer("IT Operations Server")


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


@mcp.tool()
def create_access_request(
    user_id: int,
    resource: str,
    requested_role: str,
    risk: str,
) -> dict:
    """Create a pending request for access to an IT resource."""
    try:
        return create_access_request_service(
            user_id=user_id,
            resource=resource,
            requested_role=requested_role,
            risk=risk,
        )
    except ValueError as error:
        return {"error": str(error)}


@mcp.tool()
def get_access_request(request_id: int) -> dict:
    """Retrieve an access request by ID."""
    request = get_access_request_service(request_id)
    if request is None:
        return {"error": f"Access request {request_id} was not found."}
    return request


@mcp.tool()
def approve_access_request(request_id: int, approved_by: str) -> dict:
    """Approve a pending access request with an explicit approver identity."""
    try:
        return approve_access_request_service(request_id, approved_by)
    except ValueError as error:
        return {"error": str(error)}


def main():
    mcp.run()


if __name__ == "__main__":
    main()  