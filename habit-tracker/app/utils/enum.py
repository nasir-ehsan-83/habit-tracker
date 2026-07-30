from enum import Enum

class UserRole(str, Enum):
    user    = "user"
    admin   = "admin"

class UserStatus(str, Enum):
    active  = "active"
    deleted = "deleted"
    block   = "block"

class HabitStatus(str, Enum):
    pending     = "pending"
    completed   = "completed"
    skipped     = "skipped"
    deleted     = "deleted"
    archived    = "archived"
