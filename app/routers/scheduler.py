from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas import scheduleSchemas as schemas
from database.db import db as get_db
from database.models import Scheduler, SchedulerWebhookData, SchedulerCallbackData, ScheduleType, DayOfWeek

router = APIRouter(prefix="/scheduler", tags=["Scheduler"])

@router.post("/create", response_model=schemas.SchedulerResponse,status_code=status.HTTP_201_CREATED)
def create_scheduler(request: schemas.SchedulerCreateRequest, db: Session = Depends(get_db)):
    """Create a scheduler task"""
    # insert into db
    schedule_type: ScheduleType = request.schedule_type
    repeat_on: list[int] | None = request.repeat_on
    
    if schedule_type == ScheduleType.WEEKLY and (not repeat_on or any(day not in range(1,8) for day in repeat_on)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="For weekly schedule, repeat_on must be a list of integers between 1 and 7 representing days of the week (1 for Monday, 7 for Sunday).")
    if schedule_type == ScheduleType.MONTHLY and (not repeat_on or any(day not in range(1,32) for day in repeat_on)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="For monthly schedule, repeat_on must be a list of integers between 1 and 31 representing days of the month.")

    try:
        webhook_data = SchedulerWebhookData(
            name=request.webhook.name,
            webhook_url=request.webhook.webhook_url,
            webhook_headers=request.webhook.webhook_headers,
            webhook_timeout_seconds=request.webhook.webhook_timeout_seconds,
        )
        db.add(webhook_data)
        db.flush()

        callback_data = None
        if request.callback:
            callback_data = SchedulerCallbackData(
                name=request.callback.name,
                callback_url=request.callback.callback_url,
                callback_headers=request.callback.callback_headers,
                callback_timeout_seconds=request.callback.callback_timeout_seconds,
            )
            db.add(callback_data)
            db.flush()

        scheduler = Scheduler(
            name=request.name,
            webhook_id=webhook_data.id,
            callback_id=callback_data.id if callback_data else None,
            payload=request.payload,
            execution_time=request.execution_time,
            schedule_type=request.schedule_type,
            repeat_on=request.repeat_on,
            active=request.active,
            max_retry=request.max_retry,
        )
        db.add(scheduler)
        db.commit()
        db.refresh(scheduler)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create scheduler: {str(e)}"
        )
    return {
        "id": scheduler.id,
        "message": "Scheduler created successfully"
    }
@router.post("/update", response_model=schemas.SchedulerResponse, status_code=status.HTTP_200_OK)
def update_scheduler(request: schemas.SchedulerUpdateRequest, db: Session = Depends(get_db)):
    scheduler = db.query(Scheduler).filter(Scheduler.id == request.id).first()
    try:
        if not scheduler:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheduler not found")
        if request.webhook:
                webhook_data = db.query(SchedulerWebhookData).filter(
                    SchedulerWebhookData.id == scheduler.webhook_id
                ).first()
                if not webhook_data:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")
                for field, value in request.webhook.model_dump(exclude_unset=True).items():
                    setattr(webhook_data, field, value)
                    
        if request.callback:
                if scheduler.callback_id:
                    callback_data = db.query(SchedulerCallbackData).filter(
                        SchedulerCallbackData.id == scheduler.callback_id
                    ).first()
                    if not callback_data:
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Callback not found")
                    for field, value in request.callback.model_dump(exclude_unset=True).items():
                        setattr(callback_data, field, value)
                else:
                    callback_data = SchedulerCallbackData(**request.callback.model_dump())
                    db.add(callback_data)
                    db.flush()
                    scheduler.callback_id = callback_data.id
        update_data = request.model_dump(exclude_unset=True, exclude={"webhook", "callback"})
        for field, value in update_data.items():
            setattr(scheduler, field, value)
        db.commit()
        db.refresh(scheduler)  
                  
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update scheduler: {str(e)}"
        )

    return {
        "id": scheduler.id,
        "message": "Scheduler updated successfully"
    }