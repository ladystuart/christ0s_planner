from fastapi import APIRouter, Depends, HTTPException
import logging
import asyncpg
from typing import List
from config.get_db_connection import get_db_connection
from pydantic import BaseModel
import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter()


class WeekStartUpdate(BaseModel):
    year: int
    date: datetime.date


class TaskUpdate(BaseModel):
    year: int
    day: str
    task: str
    completed: bool


class RefreshHabitTrackerRequest(BaseModel):
    year: int


class HabitTrackerUpdate(BaseModel):
    year: int
    start_date: datetime.date
    day: str
    tasks: List[str]


@router.get("/get_habit_tracker")
async def get_habit_tracker(year: int, db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Fetches the habit tracker data for a given year, organized by week and day.

    Args:
        year (int): The year for which the habit tracker data is fetched.
        db (asyncpg.Connection): A database connection object, injected via Depends.

    Returns:
        dict: A nested dictionary where the keys are weeks, and each week contains days of the week with tasks and completion status.

    Raises:
        HTTPException:
            - 404 if the specified year does not exist.
            - 500 if an internal server error occurs while fetching the habit tracker data.
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        query = """
        SELECT week_starting, day_of_week, task, completed
        FROM habit_tracker
        WHERE year_id = $1
        ORDER BY week_starting, day_of_week;
        """
        records = await db.fetch(query, year_id)

        habit_data = defaultdict(lambda: defaultdict(list))

        for record in records:
            week_start = f"Week starting {record['week_starting']}"
            habit_data[week_start][record['day_of_week']].append({
                "task": record["task"],
                "completed": record["completed"]
            })

        return habit_data

    except Exception as e:
        logger.error(f"Error fetching habit tracker data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/update_start_date")
async def update_start_date(data: WeekStartUpdate, db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Updates the starting date of a week in the habit tracker for a given year.

    Args:
        data (WeekStartUpdate): The data containing the year and new start date.
        db (asyncpg.Connection): A database connection object, injected via Depends.

    Returns:
        dict: A message indicating whether the week start date was updated successfully.

    Raises:
        HTTPException:
            - 404 if the specified year is not found or no week starting date is found for the year.
            - 500 if an internal server error occurs while updating the start date.
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", data.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        old_week = await db.fetchrow("""
            SELECT DISTINCT week_starting FROM habit_tracker WHERE year_id = $1
        """, year_id)

        if not old_week:
            raise HTTPException(status_code=404, detail="No week starting found for this year")

        old_date = old_week["week_starting"]

        await db.execute("""
            UPDATE habit_tracker 
            SET week_starting = $1
            WHERE year_id = $2 AND week_starting = $3
        """, data.date, year_id, old_date)

        return {"message": "Week starting date updated successfully"}

    except Exception as e:
        logger.error(f"Error updating week starting date: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/update_habit_tracker_task_state")
async def update_task(data: TaskUpdate, db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Updates the completion state of a specific task in the habit tracker for a given year.

    Args:
        data (TaskUpdate): The data containing the year, day of the week, task name, and its completed state.
        db (asyncpg.Connection): A database connection object, injected via Depends.

    Returns:
        dict: A message indicating whether the task was successfully updated.

    Raises:
        HTTPException:
            - 404 if the task is not found in the database.
            - 500 if an internal server error occurs.
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", data.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        result = await db.execute("""
            UPDATE habit_tracker
            SET completed = $1
            WHERE year_id = $2 AND day_of_week = $3 AND task = $4
        """, data.completed, year_id, data.day, data.task)

        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Task not found")

        return {"message": f"Task '{data.task}' updated successfully"}

    except Exception as e:
        logger.error(f"Task update error {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/refresh_habit_tracker_states")
async def refresh_habit_tracker_states(data: RefreshHabitTrackerRequest,
                                       db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Resets all tasks in the habit tracker for a specific year by setting their completion status to FALSE.

    Args:
        data (RefreshHabitTrackerRequest): The data containing the year for which tasks will be reset.
        db (asyncpg.Connection): The database connection object, injected via Depends.

    Returns:
        dict: A success message indicating that all tasks have been reset.

    Raises:
        HTTPException:
            - 404 if the specified year is not found.
            - 500 if there is an internal server error.
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", data.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        await db.execute("""
            UPDATE habit_tracker 
            SET completed = FALSE
            WHERE year_id = $1
        """, year_id)

        return {"message": "All tasks successfully reset"}

    except Exception as e:
        logger.error(f"Error resetting habit tracker states: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/edit_habit_tracker")
async def edit_habit_tracker(data: HabitTrackerUpdate, db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Update the tasks in the habit tracker for a specific year, week, and day.

    Args:
        data (HabitTrackerUpdate): The data containing the year, week starting date, day of the week,
                                   and the list of tasks to be updated.
        db (asyncpg.Connection): The database connection object, injected via Depends.

    Returns:
        dict: A success message indicating that the habit tracker has been updated.
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", data.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        existing_tasks = await db.fetch("""
            SELECT task FROM habit_tracker
            WHERE year_id = $1 AND week_starting = $2 AND day_of_week = $3
        """, year_id, data.start_date, data.day)

        existing_task_set = {task['task'] for task in existing_tasks}

        new_task_set = set(data.tasks)

        tasks_to_add = new_task_set - existing_task_set
        tasks_to_remove = existing_task_set - new_task_set

        for task in tasks_to_add:
            await db.execute("""
                INSERT INTO habit_tracker (year_id, week_starting, day_of_week, task, completed)
                VALUES ($1, $2, $3, $4, FALSE)
            """, year_id, data.start_date, data.day, task)

        for task in tasks_to_remove:
            await db.execute("""
                DELETE FROM habit_tracker
                WHERE year_id = $1 AND week_starting = $2 AND day_of_week = $3 AND task = $4
            """, year_id, data.start_date, data.day, task)

        return {"message": "Habit tracker updated successfully"}

    except Exception as e:
        logger.error(f"Error updating habit tracker: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
