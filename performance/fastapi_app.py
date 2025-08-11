from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import uvicorn

app = FastAPI(title="FastAPI Benchmark")

@app.get("/")
async def home():
    return PlainTextResponse("Hello, FastAPI!")

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=5000, 
        workers=1, 
        access_log=False,
        loop="uvloop",  # Use uvloop for better performance
        http="httptools",  # Use httptools for better performance
        limit_concurrency=1000,  # Higher concurrency limit
        limit_max_requests=0,  # No request limit
        timeout_keep_alive=30,  # Keep-alive timeout
    ) 