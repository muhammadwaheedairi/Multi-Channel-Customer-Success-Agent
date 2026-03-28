from fastapi import APIRouter, Request
from database.queries import get_customer_by_email
from core.exceptions import FTEException

router = APIRouter(prefix="/customers", tags=["customers"])

@router.get("/lookup")
async def lookup_customer(email: str, request: Request):
    pool = request.app.state.pool
    customer = await get_customer_by_email(pool, email)
    if not customer:
        raise FTEException("Customer not found", status_code=404)
    return {
        "id": str(customer["id"]),
        "email": customer["email"],
        "name": customer["name"],
        "phone": customer["phone"],
        "created_at": str(customer["created_at"])
    }
