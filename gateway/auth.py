from jose import jwt
from fastapi import Depends

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

def verify_token(token: str):
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")