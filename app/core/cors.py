from typing import ( 
    Dict,
    Any
)


cors: Dict[str, Any] = {
    "allow_origins": [
        "http://localhost:8000",
        "http://127.0.0.1:5500",
    ],
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "DELETE", "PATCH", "PUT"],
    "allow_headers": ["*"]
}
"""
CORS configuration for the FastAPI application.

Controls which domains can access the API and what operations are permitted.
- allow_origins: List of allowed client origins
- allow_credentials: Enables cookies in cross-origin requests
- allow_methods: Allowed HTTP methods (GET, POST, PUT, PATCH, DELETE)
- allow_headers: Allowed HTTP headers ('*' permits all)
"""