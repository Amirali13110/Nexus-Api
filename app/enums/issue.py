from enum import Enum
from enum import IntEnum


class IssuePriority(IntEnum):
    NOPRIORITY = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


class IssueStatus(str, Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class IssueSortBy(str, Enum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    TITLE = "title"
    PRIORITY = "priority"
    STATUS = "status"
    DUE_DATE = "due_date"
