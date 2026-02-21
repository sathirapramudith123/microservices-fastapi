from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
import httpx
from jose import jwt
from typing import Any
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import time
import logging



app = FastAPI(title="API Gateway", version="1.0.0")

SERVICES = {
    "student": "http://localhost:8001", #<- student service url
    "course": "http://localhost:8002"  #<- course service url
}

async def forward_request(service: str, path: str, method: str, request: Request = None, **kwargs) -> Any:
    """
    Forward request to the appropriate microservice
    """

    if service not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")

    url = f"{SERVICES[service]}{path}"

    # Forward headers (important for authentication)
    #headers = dict(request.headers) if request else {}

    async with httpx.AsyncClient() as client:

        try:
            if method == "GET":
                response = await client.get(url, **kwargs)
            elif method == "POST":
                response = await client.post(url, **kwargs)
            elif method == "PUT":
                response = await client.put(url, **kwargs)
            elif method == "DELETE":
                response = await client.delete(url, **kwargs)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")
            return JSONResponse(
                content=response.json()
                if response.text else None,
                status_code=response.status_code
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Service {service} is unavailable: {str(e)}")
        

async def forward_request(service: str, path: str, method: str, **kwargs) -> Any:
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail="Service configuration missing")

    url = f"{SERVICES[service]}{path}"

    async with httpx.AsyncClient() as client:
        try:
            # Added a timeout to prevent gateway hanging (Activity 4)
            response = await client.request(method, url, timeout=5.0, **kwargs)
            
            # If the backend service returns an error, relay it (Activity 4)
            if response.status_code >= 400:
                return JSONResponse(
                    status_code=response.status_code,
                    content={"error": "Downstream Service Error", "detail": response.text}
                )

            return JSONResponse(
                content=response.json() if response.text else None,
                status_code=response.status_code
            )
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail=f"Service {service} is offline")
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail=f"Service {service} timed out")
        

security = HTTPBearer()
SECRET_KEY = "your secret key"

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# Optional: Configure standard python logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gateway")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    method = request.method
    path = request.url.path
    client_host = request.client.host
    
    print(f"--- Incoming Request: {method} {path} from {client_host} ---")
    
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  
    
    print(f"--- Finished Request: {method} {path} | Status: {response.status_code} | Time: {process_time:.2f}ms ---")
    
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


@app.get("/")
async def read_root():
    return {
        "message": "API Gateway is running",
        "available_services": list(SERVICES.keys())
    }

#student endpoints
@app.get("/gateway/students")
async def get_all_students():
    """Get all students through gateway"""
    return await forward_request("student", "/api/students", "GET")

@app.get("/gateway/students/{student_id}")
async def get_student(student_id: int):
    """Get a student by ID through gateway"""
    return await forward_request("student", f"/api/students/{student_id}", "GET")


@app.post("/gateway/students")
async def create_student(request: Request):
    """Create a new student through gateway"""
    body = await request.json()
    return await forward_request("student", "/api/students", "POST", json=body)

@app.put("/gateway/students/{student_id}")
async def update_student(student_id: int, request: Request):
    """Update a student through gateway"""
    body = await request.json()
    return await forward_request("student", f"/api/students/{student_id}", "PUT", json=body)

@app.delete("/gateway/students/{student_id}")
async def delete_student(student_id: int):
    """Delete a student through gateway"""
    return await forward_request("student", f"/api/students/{student_id}", "DELETE")


#course endpoints
@app.get("/gateway/courses")
async def get_courses():
    return await forward_request("course", "/api/courses", "GET")

@app.post("/gateway/courses")
async def create_course(request: Request):
    body = await request.json()
    return await forward_request("course", "/api/courses", "POST", json=body)



@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)}
    )

# Apply to routes
@app.get("/gateway/students", dependencies=[Depends(verify_token)])
async def get_all_students():
    return await forward_request("student", "/api/students", "GET")