from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import time
from jose import jwt
from jose.exceptions import JWTError

class RateLimiter:
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.access_records = {}

    async def check_rate_limit(self, client_ip: str):
        current_time = time.time()
        
        if client_ip not in self.access_records:
            self.access_records[client_ip] = {
                "count": 1,
                "start_time": current_time
            }
            return True
        
        record = self.access_records[client_ip]
        
        if current_time - record["start_time"] > self.time_window:
            record["count"] = 1
            record["start_time"] = current_time
            return True
        
        if record["count"] >= self.max_requests:
            return False
        
        record["count"] += 1
        return True

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        credentials = await super().__call__(request)
        if not credentials:
            return None
            
        if credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=403,
                detail="Invalid authentication scheme"
            )
            
        try:
            payload = jwt.decode(
                credentials.credentials,
                "your-secret-key",
                algorithms=["HS256"]
            )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=403,
                detail="Invalid or expired token"
            )

class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limiter: RateLimiter):
        super().__init__(app)
        self.rate_limiter = rate_limiter

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        
        if not await self.rate_limiter.check_rate_limit(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Too many requests"
            )
        
        # Check for API key in headers for certain endpoints
        if request.url.path.startswith("/api/"):
            api_key = request.headers.get("X-API-KEY")
            if not api_key or api_key != "your-api-key":
                raise HTTPException(
                    status_code=401,
                    detail="Invalid API key"
                )
        
        response = await call_next(request)
        return response
