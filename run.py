import uvicorn

if __name__ == "__main__":
    """Run the FastAPI application using Uvicorn server.

    Starts the development server with auto-reload enabled.
    """
    uvicorn.run(
        "app.main:app",
        host = "127.0.0.1",
        port = 8000,
        reload = True,
        log_config = None
    )