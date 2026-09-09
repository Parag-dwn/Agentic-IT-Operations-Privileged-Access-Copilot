from app.database.database import SessionLocal
from app.database.models import AccessRequest, User


ALLOWED_RISKS = {"low", "medium", "high"}


def _serialize_request(request: AccessRequest) -> dict:
	return {
		"id": request.id,
		"user_id": request.user_id,
		"resource": request.resource,
		"requested_role": request.requested_role,
		"risk": request.risk,
		"status": request.status,
		"approved_by": request.approved_by,
	}


def create_access_request(
	user_id: int,
	resource: str,
	requested_role: str,
	risk: str,
) -> dict:
	if risk not in ALLOWED_RISKS:
		raise ValueError(
			f"Invalid risk '{risk}'. Allowed values: "
			f"{sorted(ALLOWED_RISKS)}"
		)

	if not resource.strip() or not requested_role.strip():
		raise ValueError("Resource and requested role are required")

	db = SessionLocal()

	try:
		user = db.get(User, user_id)
		if user is None:
			raise ValueError(f"User {user_id} was not found")
		if not user.is_active:
			raise ValueError(f"User {user_id} is inactive")

		request = AccessRequest(
			user_id=user_id,
			resource=resource.strip(),
			requested_role=requested_role.strip(),
			risk=risk,
			status="pending",
		)
		db.add(request)
		db.commit()
		db.refresh(request)
		return _serialize_request(request)
	finally:
		db.close()


def get_access_request(request_id: int) -> dict | None:
	db = SessionLocal()

	try:
		request = db.get(AccessRequest, request_id)
		return None if request is None else _serialize_request(request)
	finally:
		db.close()


def approve_access_request(request_id: int, approved_by: str) -> dict:
	if not approved_by.strip():
		raise ValueError("An approver is required")

	db = SessionLocal()

	try:
		request = db.get(AccessRequest, request_id)
		if request is None:
			raise ValueError(f"Access request {request_id} was not found")
		if request.status != "pending":
			raise ValueError(
				f"Access request {request_id} is already {request.status}"
			)

		request.status = "approved"
		request.approved_by = approved_by.strip()
		db.commit()
		db.refresh(request)
		return _serialize_request(request)
	finally:
		db.close()
