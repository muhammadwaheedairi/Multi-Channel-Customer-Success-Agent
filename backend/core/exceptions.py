from fastapi import Request
from fastapi.responses import JSONResponse

class FTEException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

async def fte_exception_handler(request: Request, exc: FTEException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message}
    )

async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )
