# Agentic IT Operations and Privileged Access Copilot

## Current Status

This repository is an early-stage prototype. The working runtime capability is a PostgreSQL-backed Model Context Protocol (MCP) server for searching, retrieving, and creating IT incidents, plus a small access-request workflow with explicit approval.

The repository also contains a database schema for users, entitlements, access requests, and audit logs. Access-request creation, retrieval, and approval are implemented at the service and MCP layers. Policy retrieval, agent orchestration, guardrails, and audit logging are not implemented yet.

The original product goal is a secure AI copilot that can help IT and security teams investigate incidents, evaluate privileged-access requests against enterprise policy, interact with IT systems through controlled tools, and require human approval before sensitive actions. At the current implementation level, it should be treated as an incident-management integration prototype rather than a production privileged-access system.

## What It Is Useful For Today

The implemented system is useful as a small foundation for:

- Exposing incident-management operations as MCP tools to an MCP-compatible client.
- Searching incident titles and descriptions with a keyword.
- Retrieving one incident by numeric ID.
- Creating a new incident with a validated P1-P4 priority when called through MCP.
- Creating a pending access request for an active user.
- Retrieving an access request by ID.
- Approving a pending access request with an explicit approver identity.
- Prototyping the database contract that a future operations or access copilot could use.
- Demonstrating how an AI client could call an internal IT operation through a typed tool boundary instead of embedding database logic in the client.

It is not currently suitable for granting production privileges, making access decisions, enforcing policy, or operating as an unattended IT automation agent.

## Implemented Architecture

```text
MCP client
	|
	v
Incident MCP server
app/mcp/servers/incident_server.py
	|
	v
Incident service
app/services/incident_service.py
	|
	v
SQLAlchemy engine and session
app/database/database.py
	|
	v
PostgreSQL 16
```

The MCP server is created as `IT Operations Server` and exposes six tools:

| Tool | Inputs | Behavior |
| --- | --- | --- |
| `search_incidents` | `query: str` | Searches `Incident.title` and `Incident.description` using case-insensitive SQL `ILIKE`. Returns matching incident dictionaries. |
| `get_incident` | `incident_id: int` | Retrieves one incident. Returns an error dictionary when the ID does not exist. |
| `create_incident` | `title: str`, `description: str`, `priority: str` | Accepts only `P1`, `P2`, `P3`, or `P4`, then creates an incident with status `open`. |
| `create_access_request` | `user_id: int`, `resource: str`, `requested_role: str`, `risk: str` | Creates a `pending` request for an active user. Risk must be `low`, `medium`, or `high`. |
| `get_access_request` | `request_id: int` | Retrieves one access request by ID. |
| `approve_access_request` | `request_id: int`, `approved_by: str` | Transitions a pending request to `approved` and records the supplied approver value. |

The server can be started from the repository root with:

```bash
python app/mcp/servers/incident_server.py
```

The exact transport used by `mcp.run()` is determined by the installed MCP library. No client configuration or deployed application service is included in this repository.

## Repository Layout

| Path | Responsibility | Current state |
| --- | --- | --- |
| `app/database/models.py` | SQLAlchemy schema | Implemented for users, entitlements, incidents, access requests, and audit logs. |
| `app/database/database.py` | Database URL loading, engine, and sessions | Implemented; requires `DATABASE_URL` at import time. |
| `app/database/init_db.py` | Create database tables | Implemented with `Base.metadata.create_all()`. |
| `app/database/seed.py` | Insert sample users, entitlements, and incidents | Implemented, but not idempotent. |
| `app/services/incident_service.py` | Incident search, retrieval, and creation | Implemented. |
| `app/services/access_service.py` | Access-request validation and state transitions | Implemented for create, retrieve, and approve. |
| `app/mcp/servers/incident_server.py` | MCP incident tools | Implemented. |
| `app/agents/` | Intended AI agents | Package placeholder only. |
| `app/graph/` | Intended LangGraph orchestration | Package placeholder only. |
| `app/guardrails/` | Intended AI and tool safety controls | Package placeholder only. |
| `app/rag/` | Intended policy retrieval and embeddings | Package placeholder only. |
| `app/api/` | Intended HTTP API | Package placeholder only. |
| `data/policies/` | Intended enterprise policy documents | Empty. |
| `frontend/` | Intended user interface | Empty. |
| `tests/` | Database, MCP, and access workflow tests | Five tests; they require an already seeded database. |
| `docker-compose.yml` | Local PostgreSQL dependency | Starts PostgreSQL only; it does not start the Python application. |

## Database Model

The SQLAlchemy models define these entities:

- `User`: username, name, department, email, and active status.
- `Entitlement`: a user’s resource and role assignment, such as read-only access to `finance-db`.
- `Incident`: title, description, priority, status, and creation timestamp.
- `AccessRequest`: requested resource and role, risk, approval status, approver, and timestamp.
- `AuditLog`: user, agent, tool, serialized arguments, decision, and timestamp.

`Incident` and `AccessRequest` are used by the current services and MCP server. `AuditLog` remains a schema foundation, not an active workflow. Foreign keys are present, but ORM relationships, database check constraints, authentication, authorization, and tenant isolation are not defined.

## Sample Data

The seed script creates:

- `rahul.sharma` in Finance with read-only access to `finance-db`.
- `priya.verma` in IT with operator access to `it-support`.
- `admin.user` in Security with security-admin access to `production-db`.
- A P1 VPN authentication incident in `investigating` status.
- A P2 Finance application incident in `monitoring` status.

Run the seed script only once against a fresh database. It inserts fixed usernames and email addresses, so running it repeatedly will normally fail on unique constraints.

## Local Setup

### Prerequisites

- Python 3 with the dependencies in `requirements.txt`.
- Docker and Docker Compose, or another reachable PostgreSQL 16-compatible database.
- A database URL available through the environment or a local `.env` file.

### Start PostgreSQL

```bash
cp .env.example .env
docker compose up -d
```

The included Compose file starts PostgreSQL with:

```text
Host: localhost
Port: 5432
Database: agentic_it_ops
User: postgres
Password: postgres
```

These credentials are for local development only and must not be used in a production deployment.

### Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Create and seed the schema

```bash
python -m app.database.init_db
python -m app.database.seed
```

The database module loads `DATABASE_URL` using `python-dotenv`. Importing database-backed modules without that variable configured raises an error.

### Run the tests

```bash
pytest
```

The tests assume PostgreSQL is reachable and that the schema and seed data already exist. They do not create an isolated test database or clean up records.

### Start the incident MCP server

```bash
python app/mcp/servers/incident_server.py
```

An MCP-compatible client can then connect using the transport supported by the installed MCP package and call the six incident and access-request tools described above.

## Configuration

`.env.example` contains these settings:

| Variable | Current use |
| --- | --- |
| `DATABASE_URL` | Used to create the SQLAlchemy engine. Required. |
| `APP_ENV` | Declared, but not currently read by application code. |
| `LLM_PROVIDER` | Declared, but no LLM client is initialized. |
| `GEMINI_API_KEY` | Declared, but not currently read. |
| `LOG_LEVEL` | Declared, but no application logging configuration is present. |

The dependency list includes LangChain, LangGraph, ChromaDB, NeMo Guardrails, FastAPI, Streamlit, and LLM clients. Their presence indicates planned integrations; it does not mean those features are active.

## Security and Production Limitations

The current implementation must not be connected directly to production systems or trusted with privileged actions. Important gaps include:

- No authentication or caller identity propagation.
- No authorization checks for incident access or mutation.
- No policy-based access-request evaluation or role/entitlement conflict check.
- Approval currently records a caller-supplied string; it does not authenticate or authorize the approver.
- No policy ingestion, policy retrieval, or citation mechanism.
- No AI agent or LLM invocation.
- No guardrail enforcement for prompts, tool calls, or sensitive data.
- No audit record written when MCP tools are called or incidents are changed.
- No external IT-system integrations; MCP currently wraps the local database only.
- No incident update, assignment, escalation, or deletion operation.
- No pagination or result limit for incident search.
- No database migrations; schema creation uses `create_all()`.
- No authorization, policy validation, or audit enforcement at the service layer.
- No production secret management, TLS configuration, rate limiting, or monitoring.
- No application container, HTTP API, or frontend implementation.

## Intended Future Product

The schema and package structure suggest a future workflow like this:

1. An authenticated IT or security user submits an incident investigation or privileged-access request.
2. An orchestrator routes the request to specialized agents.
3. A policy-retrieval component searches approved enterprise documents in `data/policies/` or a vector store.
4. Agents inspect incidents and entitlements through controlled MCP tools.
5. Guardrails validate the request, retrieved context, proposed tool arguments, and sensitive output.
6. High-risk actions pause for explicit human approval.
7. Approved actions execute through authorized integrations and produce an immutable audit record.

That workflow is a roadmap, not a behavior currently supplied by this repository.

## Recommended Next Implementation Steps

1. Add a real application entry point and document the MCP client transport.
2. Add service-layer validation, pagination, authorization, and consistent error handling.
3. Add policy-based risk evaluation, entitlement checks, rejection/expiration state transitions, and approval authorization around the current access-request workflow.
4. Write audit records for every tool invocation and privileged decision.
5. Add policy documents, ingestion, retrieval, source citations, and tests for policy conflicts.
6. Implement agent and graph orchestration only after the tool and approval contracts are stable.
7. Add authentication, secrets management, migrations, isolated test fixtures, and integration tests before any production use.

## Bottom Line

Today, this project is best understood as a foundation for an IT operations copilot: a local PostgreSQL schema plus an MCP server for incidents and basic access requests. Its immediate value is demonstrating controlled tool boundaries and reserving the data structures needed for future privileged-access automation. The secure policy-aware multi-agent copilot described by the project name and original summary remains to be built.
