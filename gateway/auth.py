from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt

security = HTTPBearer()
SECRET_KEY = "your secret key"

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# Apply to routes
@app.get("/gateway/students", dependencies=[Depends(verify_token)])
async def get_all_students():
    return await forward_request("student", "/api/students", "GET")