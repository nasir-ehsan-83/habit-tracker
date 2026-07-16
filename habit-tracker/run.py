import uvicorn
from app.config.logging_handler import logger 

if __name__ == "__main__":
    # با تنظیم log_config=None، یوویکورن از تنظیمات شما استفاده می‌کند
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True, log_config=None)
