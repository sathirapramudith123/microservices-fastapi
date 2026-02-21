import time
from fastapi import Request
import logging

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