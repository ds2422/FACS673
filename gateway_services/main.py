from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from dotenv import load_dotenv
from fastapi import FastAPI

# Load environment variables
load_dotenv()

app = FastAPI(title="API Gateway Service")

# Allow CORS for all origins (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Microservice base URLs
SERVICES = {
    "auth": os.getenv("AUTH_SERVICE_URL"),
    "file": os.getenv("FILE_SERVICE_URL"),
    "summarizer": os.getenv("URL_SUMMARIZER_URL"),
    "comparison": os.getenv("COMPARISON_SERVICE_URL"),
    "backend": os.getenv("SUMMARIZATION_BACKEND_URL"),
}


# Helper function to forward requests
async def forward_request(service_name: str, path: str, request: Request):
    base_url = SERVICES.get(service_name)
    if not base_url:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")

    url = f"{base_url}/{path}"
    async with httpx.AsyncClient() as client:
        method = request.method.lower()
        data = await request.body()
        headers = dict(request.headers)

        response = await client.request(method, url, content=data, headers=headers)
        return response





# Proxy routes for each microservice
@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def auth_proxy(path: str, request: Request):
    return await forward_request("auth", path, request)


@app.api_route("/file/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def file_proxy(path: str, request: Request):
    return await forward_request("file", path, request)


@app.api_route("/summarizer/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def summarizer_proxy(path: str, request: Request):
    return await forward_request("summarizer", path, request)


@app.api_route("/comparison/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def comparison_proxy(path: str, request: Request):
    return await forward_request("comparison", path, request)


@app.api_route("/backend/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def backend_proxy(path: str, request: Request):
    return await forward_request("backend", path, request)


@app.get("/health")
async def health_check():
    return {"status": "Gateway is running"}
@app.get("/")
def root():
    return {"message": "Gateway Service is running", "available_routes": ["/auth", "/file", "/summarizer"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)
