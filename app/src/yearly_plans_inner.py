from fastapi import APIRouter, Depends, HTTPException
import logging
import asyncpg
from config.get_db_connection import get_db_connection
from pydantic import BaseModel

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter()


class TaskCreate(BaseModel):
    year: int
    task: str
    completed: bool


class TaskUpdateStatus(BaseModel):
    year: int
    task: str
    completed: bool


class TaskDelete(BaseModel):
    year: int
    task: str


class TaskUpdate(BaseModel):
    year: int
    old_task: str
    task: str
    completed: bool


@router.post("/add_task_yearly_plans_inner")
async def add_task(task_data: TaskCreate, db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Adds a new task to the yearly plans for a specific year.

    This endpoint performs the following actions:
    1. Validates if the specified year exists in the `years` table.
    2. Inserts a new task into the `yearly_plans` table with the provided `task` and its `completed` status.

    Args:
        task_data (TaskCreate): A request object containing the `year`, `task`, and `completed` status.
        db (asyncpg.Connection): Database connection provided via dependency injection.

    Returns:
        dict: A message indicating the successful addition of the task.

    Raises:
        HTTPException (404): If the specified `year` is not found in the `years` table.
        HTTPException (500): If an internal server error occurs while adding the task.
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", task_data.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        await db.execute(
            "INSERT INTO yearly_plans (year_id, task, completed) VALUES ($1, $2, $3)",
            year_id, task_data.task, task_data.completed
        )
        return {"message": "Task added successfully"}
    except Exception as e:
        logger.error(f"Error adding task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/get_tasks_yearly_plans_inner")
async def get_tasks(year: int, db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Retrieves the list of tasks for a specific year from the yearly plans.

    This endpoint performs the following actions:
    1. Validates if the specified year exists in the `years` table.
    2. Fetches the tasks from the `yearly_plans` table that correspond to the specified year.
    3. Returns a list of tasks with their completion status.

    Args:
        year (int): The year for which tasks need to be retrieved.
        db (asyncpg.Connection): Database connection provided via dependency injection.

    Returns:
        dict: A dictionary containing a list of tasks for the specified year, including the task description and completion status (`done`).

    Raises:
        HTTPException (404): If the specified `year` is not found in the `years` table.
        HTTPException (500): If an internal server error occurs while fetching the tasks.
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        rows = await db.fetch(
            "SELECT id, task, completed FROM yearly_plans WHERE year_id = $1 ORDER BY id",
            year_id
        )

        tasks = [{"task": row["task"], "done": row["completed"]} for row in rows]

        return {"tasks": tasks}

    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/yearly_plans_inner_update_task_status")
async def update_task_status(task_data: TaskUpdateStatus, db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Updates the completion status of a specific task for a given year in the yearly plans.

    This endpoint performs the following actions:
    1. Validates if the specified year exists in the `years` table.
    2. Updates the completion status (`completed`) of a specific task for that year in the `yearly_plans` table.
    3. Returns a success message if the update is successful, or an error message if the task is not found.

    Args:
        task_data (TaskUpdateStatus): The data containing the year, task, and the new completion status.
        db (asyncpg.Connection): Database connection provided via dependency injection.

    Returns:
        dict: A dictionary with a success message indicating that the task's completion status has been updated.

    Raises:
        HTTPException (404): If the specified `year` or `task` is not found in the respective tables.
        HTTPException (500): If an internal server error occurs while updating the task status.
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", task_data.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        result = await db.execute(
            """
            UPDATE yearly_plans 
            SET completed = $1 
            WHERE year_id = $2 AND task = $3
            """,
            task_data.completed, year_id, task_data.task
        )

        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Task not found.")

        return {"message": "Task status updated successfully."}

    except Exception as e:
        logger.error(f"Error updating task status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/yearly_plans_inner_delete_task")
async def delete_task(task_data: TaskDelete, db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Deletes a specific task for a given year from the yearly plans.

    This endpoint performs the following actions:
    1. Validates if the specified year exists in the `years` table.
    2. Deletes the task from the `yearly_plans` table for the given year.
    3. Returns a success message if the task is deleted, or an error message if the task is not found.

    Args:
        task_data (TaskDelete): The data containing the year and the task to delete.
        db (asyncpg.Connection): Database connection provided via dependency injection.

    Returns:
        dict: A dictionary with a success message indicating that the task has been deleted.

    Raises:
        HTTPException (404): If the specified `year` or `task` is not found in the respective tables.
        HTTPException (500): If an internal server error occurs while deleting the task.
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", task_data.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        result = await db.execute(
            "DELETE FROM yearly_plans WHERE year_id = $1 AND task = $2",
            year_id, task_data.task
        )

        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Task not found.")

        return {"message": "Task deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/yearly_plans_inner_edit_task")
async def edit_task_on_server(task_data: TaskUpdate, db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Edits a specific task for a given year in the yearly plans.

    This endpoint performs the following actions:
    1. Validates if the specified year exists in the `years` table.
    2. Updates the task in the `yearly_plans` table for the given year, changing its name and completion status.
    3. Returns a success message if the task is successfully updated, or an error message if the task is not found.

    Args:
     task_data (TaskUpdate): The data containing the year, old task name, new task name, and completion status.
     db (asyncpg.Connection): Database connection provided via dependency injection.

    Returns:
     dict: A dictionary with a success message indicating that the task has been updated.

    Raises:
     HTTPException (404): If the specified `year` or `old_task` is not found in the respective tables.
     HTTPException (500): If an internal server error occurs while updating the task.
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", task_data.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        result = await db.execute(
            """
            UPDATE yearly_plans 
            SET task = $1, completed = $2
            WHERE year_id = $3 AND task = $4
            """,
            task_data.task, task_data.completed, year_id, task_data.old_task
        )

        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Task not found.")

        return {"message": "Task updated successfully."}

    except Exception as e:
        logger.error(f"Error updating task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
