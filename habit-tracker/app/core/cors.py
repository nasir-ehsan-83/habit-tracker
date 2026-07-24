from typing import Dict, Any

cors: Dict[str, Any] = {
    "allow_origins" : [
        "http://localhost:8000",    # for react dev
        "http://127.0.0.1:5500",    # for liveserver
        "https://www.google.com"    # for google
    ],
    "allow_credentials" : True,
    "allow_methods" : ["GET", "POST", "DELETE", "PATCH", "PUT"],
    "allow_headers" : ["*"]
}