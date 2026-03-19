from pydantic import BaseModel, EmailStr
from datetime import datetime, UTC
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
import uuid, enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from database.db import Base
from app.schemas.scheduleSchemas import ScheduleType, DayOfWeek, SchedulerStatus

class SchedulerWebhookData(Base):
    __tablename__ = "scheduler_webhook_data"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True, index=True)
    webhook_url = Column(String(255), nullable=False)
    webhook_headers = Column(JSON, nullable=True, default=lambda: {})
    webhook_timeout_seconds=Column(Integer, nullable=False, default=90)


class SchedulerCallbackData(Base):
    __tablename__ = "scheduler_callback_data"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True, index=True)
    callback_url = Column(String(255), nullable=True)
    callback_headers = Column(JSON, nullable=True, default=lambda: {})
    callback_timeout_seconds=Column(Integer, nullable=False, default=90)


class Scheduler(Base):
    __tablename__ = "scheduler"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)
    webhook_id = Column(Integer, ForeignKey("scheduler_webhook_data.id"), nullable=False)
    callback_id = Column(Integer, ForeignKey("scheduler_callback_data.id"), nullable=True)
    webhook = relationship("SchedulerWebhookData")
    callback = relationship("SchedulerCallbackData")
    payload = Column(JSON, nullable=False)
    execution_time = Column(DateTime(timezone=True), nullable=True)
    schedule_type = Column(Enum(ScheduleType, name="schedule_type_enum"), nullable=False, default=ScheduleType.ONCE)
    # -> weekly -> [1,3,5]  (Mon Wed Fri) or monthly -> [1,15]
    repeat_on = Column(ARRAY(Integer), nullable=True)
    status = Column(Enum(SchedulerStatus, name="scheduler_status_enum"), default=True)
    max_retry = Column(Integer, default=3)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    last_executed_at = Column(DateTime(timezone=True), nullable=True)
    next_executed_at = Column(DateTime(timezone=True), nullable=True, index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate= lambda: datetime.now(UTC))

class ScheduleTaskExecutions(Base):
    __tablename__ = "schedule_task_executions"
    id = Column(Integer, primary_key=True)
    scheduler_id=Column(Integer, ForeignKey("scheduler.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(10), nullable=False)
    attempt = Column(Integer, nullable=False)
    response_code = Column(Integer, nullable=False)
    executed_at = Column(DateTime(timezone=True), nullable=False)
    response_time_ms = Column(Integer, nullable=False)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate= lambda: datetime.now(UTC))

class ScheduleCallbackExecutions(Base):
    __tablename__ = "schedule_callback_executions"
    id = Column(Integer, primary_key=True)
    scheduler_id=Column(Integer, ForeignKey("scheduler.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(100), nullable=False)
    attempt = Column(Integer, nullable=False)
    response_code = Column(Integer, nullable=False)
    executed_at = Column(DateTime(timezone=True), nullable=False)
    response_time_ms = Column(Integer, nullable=False)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate= lambda: datetime.now(UTC))

class ParentScheduler(Base):
    __tablename__ = "parent_scheduler"
    id = Column(Integer, primary_key=True)
    user_id=Column(UUID(as_uuid=True), nullable=True)
    scheduler_id=Column(Integer, ForeignKey("scheduler.id", ondelete="CASCADE"), nullable=False, index=True)
