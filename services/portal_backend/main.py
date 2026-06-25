"""
InsuStream Portal API - Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import configurations
from configs.app.settings import app_settings

# Import routes
from routes.upload_routes import router as upload_router

# Initialize FastAPI application
app = FastAPI(
    title=app_settings.app_name,
    version=app_settings.version,
    debug=app_settings.debug
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": app_settings.app_name,
        "version": app_settings.version,
        "status": "online"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/api/health")
@app.get("/api/health/")
async def api_health():
    """API health check endpoint"""
    return {"status": "healthy", "api_version": app_settings.version}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3011, reload=True)

