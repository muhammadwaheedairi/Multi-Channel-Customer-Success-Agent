from fastapi import APIRouter, Request
from database.queries import get_customer_by_email
from core.exceptions import FTEException

router = APIRouter(prefix="/customers", tags=["customers"])

@router.get("/lookup")
async def lookup_customer(
    request: Request,
    email: str = None,
    phone: str = None
):
    """
    Look up customer by email OR phone across all channels.
    PDF requirement: cross-channel customer identification.
    """
    if not email and not phone:
        raise FTEException("Provide email or phone", status_code=400)

    pool = request.app.state.pool

    if email:
        customer = await get_customer_by_email(pool, email)
        if customer:
            return {
                "id": str(customer["id"]),
                "email": customer["email"],
                "name": customer["name"],
                "phone": customer["phone"],
                "created_at": str(customer["created_at"])
            }

    if phone:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """SELECT c.* FROM customers c
                   JOIN customer_identifiers ci ON ci.customer_id = c.id
                   WHERE ci.identifier_type = 'whatsapp'
                   AND ci.identifier_value = $1""",
                phone
            )
            if row:
                return {
                    "id": str(row["id"]),
                    "email": row["email"],
                    "name": row["name"],
                    "phone": row["phone"],
                    "created_at": str(row["created_at"])
                }

    raise FTEException("Customer not found", status_code=404)
