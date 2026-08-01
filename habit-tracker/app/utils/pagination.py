from typing import Tuple

def paginate(page: int = 1, limit: int = 10) -> Tuple[int, int]:
    
    page = min(max(1, page), 10)
    
    limit = min(max(1, limit), 50)
    
    skip: int = (page - 1) * limit
        
    return skip, limit
