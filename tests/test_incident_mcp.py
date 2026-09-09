import pytest

from mcp import Client

from app.mcp.servers.incident_server import mcp


@pytest.mark.anyio
async def test_search_incidents():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "search_incidents",
            {"query": "VPN"},
        )

        assert result.structured_content is not None