from enum import Enum



class UserRole(str, Enum):
    """User roles for access control."""

    user        = "user"
    admin       = "admin"



class UserStatus(str, Enum):
    """User account status."""

    active      = "active"
    deleted     = "deleted"
    block       = "block"



class HabitStatus(str, Enum):
    """Habit completion status."""

    pending     = "pending"
    completed   = "completed"
    skipped     = "skipped"
    deleted     = "deleted"
    archived    = "archived"



class HabitCategory(str, Enum):
    """Habit categories for organization."""

    sport       = "sport"
    study       = "study"
    health      = "health"
    finance     = "finance"
    work        = "work"
    routine     = "routine"
    social      = "social"




class Timeframe(str, Enum):
    """Time periods for analytics and filtering."""

    DAY         = "day"
    WEEK        = "week"
    MONTH       = "month"
    YEAR        = "year"
    ALL         = "all"