from fastapi import APIRouter, Depends, HTTPException
import logging
import asyncpg
from config.get_db_connection import get_db_connection
from pydantic import BaseModel
import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter()


class CalendarTask(BaseModel):
    year: int
    date: datetime.date
    event: str


class TaskDeleteRequest(BaseModel):
    year: int
    date: datetime.date
    event: str


@router.get("/get_calendar_tasks")
async def get_calendar_tasks(year: int, db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Retrieves all calendar events for a specified year.

    This endpoint fetches tasks (events) from the `calendar` table that are associated
    with the provided year by joining with the `years` table. The results are ordered by date.

    Args:
        year (int): The year for which to retrieve calendar events.
        db (asyncpg.Connection): Database connection dependency.

    Returns:
        list[dict]: A list of events with their corresponding dates.

    Raises:
        HTTPException (500): If an error occurs while fetching data.
    """
    try:
        query = """
        SELECT c.date, c.event 
        FROM calendar c
        JOIN years y ON c.year_id = y.id
        WHERE y.year = $1
        ORDER BY c.date, c.id
        """
        rows = await db.fetch(query, year)
        return [{"date": str(row["date"]), "event": row["event"]} for row in rows]
    except Exception as e:
        return {"error": "internal server error"}


@router.post("/add_calendar_task")
async def add_calendar_task(task: CalendarTask, db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Adds a new calendar task (event) for a specific date and year.

    If the provided year does not already exist in the `years` table, it will be created.
    Then the task is added to the `calendar` table, linked to the corresponding year.

    Args:
        task (CalendarTask): A pydantic model containing the year, date, and event description.
        db (asyncpg.Connection): Database connection provided via dependency injection.

    Returns:
        dict: A message indicating that the task was successfully added.

    Raises:
        HTTPException (500): If an internal server error occurs.
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", task.year)

        if year_row is None:
            year_row = await db.fetchrow("INSERT INTO years (year) VALUES ($1) RETURNING id", task.year)

        year_id = year_row["id"]

        await db.execute(
            "INSERT INTO calendar (year_id, date, event) VALUES ($1, $2, $3)",
            year_id, task.date, task.event
        )

        return {"message": "Task added successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/delete_calendar_task")
async def delete_calendar_task(task: TaskDeleteRequest, db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Deletes a specific calendar task (event) for a given year, date, and event description.

    This endpoint first checks if the provided year exists in the `years` table. If not, a 404 error is returned.
    Then, it attempts to delete the specified task from the `calendar` table. If the task is not found, a 404 error is raised.

    Args:
        task (TaskDeleteRequest): A pydantic model containing the year, date, and event description of the task to delete.
        db (asyncpg.Connection): Database connection provided via dependency injection.

    Returns:
        dict: A message indicating that the task was successfully deleted.

    Raises:
        HTTPException:
            - 404 if the year or task is not found.
            - 500 if an internal server error occurs.
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", task.year)

        if year_row is None:
            raise HTTPException(status_code=404, detail="Year not found.")

        year_id = year_row["id"]

        result = await db.execute(
            """
            DELETE FROM calendar
            WHERE year_id = $1 AND date = $2 AND event = $3
            """,
            year_id, task.date, task.event
        )

        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Task not found.")

        return {"message": "Task deleted successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
