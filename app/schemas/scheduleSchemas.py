
from datetime import datetime
import enum

from pydantic import BaseModel

class ScheduleType(str, enum.Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class DayOfWeek(int, enum.Enum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7
    
class SchedulerResponse(BaseModel):
    id: int
    message: str | None
    
class CallBackRequest(BaseModel):
    name: str | None
    callback_url: str
    callback_headers: dict
    callback_timeout_seconds: int = 90

class WebHookRequest(BaseModel):
    name: str | None
    webhook_url: str
    webhook_headers: dict
    webhook_timeout_seconds: int = 90
    
class SchedulerCreateRequest(BaseModel):
    name: str | None
    webhook: WebHookRequest
    callback: CallBackRequest | None
    payload: dict
    execution_time: datetime
    schedule_type: ScheduleType
    repeat_on: list[int] | None
    active: bool = True
    max_retry: int = 3

class SchedulerUpdateRequest(BaseModel):
    id: int
    name: str | None
    webhook: WebHookRequest | None
    callback: CallBackRequest | None
    payload: dict | None
    execution_time: datetime | None
    schedule_type: ScheduleType | None
    repeat_on: list[int] | None
    active: bool | None
    max_retry: int | None
    