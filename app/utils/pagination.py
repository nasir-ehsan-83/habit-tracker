from typing import Tuple

def paginate(page_in: int = 1, limit_in: int = 10) -> Tuple[int, int]:
    """Calculate pagination skip and limit values.

    Args:
        page: Page number (1-10). Defaults to 1.
        limit: Items per page (1-50). Defaults to 10.

    Returns:
        Tuple[int, int]: (skip, limit) values for database queries.
            - skip: Number of items to skip
            - limit: Number of items to return

    Example:
        skip, limit = paginate(2, 15)  # Returns: (15, 15)
    """
    page: int = min(max(1, page_in), 10)
    
    limit: int = min(max(1, limit_in), 50)
    
    skip: int = (page - 1) * limit
        
    return skip, limit