"""
Routes Package - HTTP endpoints
"""
from routes.upload_routes import router as upload_router, UploadController


__all__ = [
    'upload_router',
    'UploadController',
]
