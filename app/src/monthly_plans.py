from fastapi import APIRouter, Depends, HTTPException
import logging
import asyncpg
from config.get_db_connection import get_db_connection
from pydantic import BaseModel
import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter()


class UpdateReadingLinkRequest(BaseModel):
    year: int
    month: str
    new_link: str


class MonthRequest(BaseModel):
    year: int
    month: str


class AddMonthGoalRequest(BaseModel):
    year: int
    month: str
    task: str
    completed: bool = False


class ToggleGoalStateRequest(BaseModel):
    year: int
    month: str
    task: str
    done: bool


class DeleteMonthGoalRequest(BaseModel):
    year: int
    month: str
    task: str


class UpdateMonthGoalRequest(BaseModel):
    year: int
    month: str
    old_task: str
    new_task: str


class AddMonthDiaryTaskRequest(BaseModel):
    year: int
    month: str
    task: str
    date: datetime.date
    completed: bool = False


class DeleteMonthDiaryTaskRequest(BaseModel):
    year: int
    month: str
    task: str
    date: datetime.date


class ToggleDiaryTaskRequest(BaseModel):
    year: int
    month: str
    task: str
    date: datetime.date
    done: bool


class UpdateMonthDiaryTaskRequest(BaseModel):
    year: int
    month: str
    date: datetime.date
    old_task: str
    new_task: str


@router.get("/get_months_ui_data")
async def get_months_states(
        request: MonthRequest,
        db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Retrieve UI display data for a specific month in a given year.

    This endpoint fetches visual and informational elements needed to display a month's
    UI components, including icons, banners, and reading links. The data is typically used
    to render the month view in the calendar interface.

    Args:
        request (MonthRequest): A Pydantic model containing:
            - year (int): The target year (e.g., 2023)
            - month (str): The target month name (e.g., "January", "February")
        db (asyncpg.Connection): Database connection dependency

    Returns:
        Dict[str, str]: A dictionary containing UI display elements:
            - icon_path (str): Path/URL to the month's icon image
            - banner (str): Path/URL to the month's banner image
            - reading_link (str): URL to associated reading material
            - month_icon_path (str): Path/URL to an alternative month icon

    Raises:
        HTTPException 404:
            - If the specified year is not found
            - If no UI data exists for the specified month
        HTTPException 500: If there's an unexpected server error
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", request.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        query = """
        SELECT icon_path, banner, reading_link, month_icon_path 
        FROM months 
        WHERE year_id = $1 AND month_name = $2
        """
        row = await db.fetchrow(query, year_id, request.month)

        if not row:
            raise HTTPException(status_code=404, detail="No data found for given month and year")

        return {
            "icon_path": row["icon_path"],
            "banner": row["banner"],
            "reading_link": row["reading_link"],
            "month_icon_path": row["month_icon_path"]
        }

    except Exception as e:
        logger.error(f"Error fetching month data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/update_reading_link")
async def update_reading_link(
        request: UpdateReadingLinkRequest,
        db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Update the reading link for a specific month in a given year.

    This endpoint modifies the associated reading material URL for a particular month.
    The updated link will be used wherever month-related reading materials are referenced
    in the application UI.

    Args:
        request (UpdateReadingLinkRequest): A Pydantic model containing:
            - year (int): The target year (e.g., 2023)
            - month (str): The target month name (full English name, e.g., "January")
            - new_link (str): The new URL for reading materials
        db (asyncpg.Connection): Database connection dependency

    Returns:
        Dict[str, str]: A dictionary with operation status:
            - message (str): Success confirmation message

    Raises:
        HTTPException 404:
            - If the specified year is not found
            - If the specified month is not found for the given year
        HTTPException 500: If there's an unexpected server error during update
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", request.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        month_row = await db.fetchrow(
            "SELECT id FROM months WHERE year_id = $1 AND month_name = $2",
            year_id, request.month
        )

        if not month_row:
            raise HTTPException(status_code=404, detail="Month not found")

        await db.execute(
            "UPDATE months SET reading_link = $1 WHERE year_id = $2 AND month_name = $3",
            request.new_link, year_id, request.month
        )

        return {"message": "Reading link updated successfully"}

    except Exception as e:
        logger.error(f"Error updating reading link: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/add_month_goal")
async def add_month_goal(
        request: AddMonthGoalRequest,
        db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Add a new monthly goal/task to the specified month and year.

    This endpoint creates a new goal entry in the monthly plans, which can represent tasks,
    objectives, or milestones for a particular month. The goal can be marked as completed or pending.

    Args:
       request (AddMonthGoalRequest): A Pydantic model containing:
           - year (int): The target year (e.g., 2023)
           - month (str): The target month name (full English name, e.g., "January")
           - task (str): The goal/task description
           - completed (bool): Initial completion status (default: False)
       db (asyncpg.Connection): Database connection dependency

    Returns:
       Dict[str, str]: A dictionary with operation status:
           - message (str): Success confirmation message

    Raises:
       HTTPException 404: If the specified year is not found
       HTTPException 500: If there's an unexpected server error during insertion
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", request.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        await db.execute(
            "INSERT INTO monthly_plans (year_id, month, task, completed) VALUES ($1, $2, $3, $4)",
            year_id, request.month, request.task, request.completed
        )

        return {"message": "Goal added successfully"}

    except Exception as e:
        logger.error(f"Error adding goal: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/get_month_goals")
async def get_month_goals(
        request: MonthRequest, db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Retrieve all goals/tasks for a specific month and year.

    This endpoint fetches the list of monthly goals along with their completion status,
    typically used to display and track monthly objectives in the application UI.

    Args:
        request (MonthRequest): A Pydantic model containing:
            - year (int): The target year (e.g., 2023)
            - month (str): The target month name (full English name, e.g., "January")
        db (asyncpg.Connection): Database connection dependency

    Returns:
        Dict[str, List[Dict[str, Union[str, bool]]]: A dictionary containing:
            - goals (List): Array of goal objects with:
                - task (str): The goal description
                - done (bool): Completion status

    Raises:
        HTTPException 404: If the specified year is not found
        HTTPException 500: If there's an unexpected server error
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", request.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        query = """
        SELECT task, completed FROM monthly_plans
        WHERE year_id = $1 AND month = $2 ORDER BY id
        """
        rows = await db.fetch(query, year_id, request.month)

        if not rows:
            return {"goals": []}

        goals = [{"task": row["task"], "done": row["completed"]} for row in rows]

        return {"goals": goals}

    except Exception as e:
        logger.error(f"Error fetching month goals: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/toggle_month_goal_state")
async def toggle_month_goal_state(
        request: ToggleGoalStateRequest,
        db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Toggle or set the completion state of a specific monthly goal.

    This endpoint updates the completion status of an existing monthly goal/task,
    allowing users to mark goals as complete or incomplete. The change takes effect
    immediately in the application UI.

    Args:
        request (ToggleGoalStateRequest): A Pydantic model containing:
            - year (int): The target year (e.g., 2023)
            - month (str): The target month name (full English name, e.g., "January")
            - task (str): The exact goal description to modify
            - done (bool): The new completion state (true = complete, false = incomplete)
        db (asyncpg.Connection): Database connection dependency

    Returns:
        Dict[str, str]: A dictionary with operation status:
            - message (str): Success confirmation message

    Raises:
        HTTPException 404:
            - If the specified year is not found
            - If the specified goal is not found
        HTTPException 500: If there's an unexpected server error
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", request.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        goal_row = await db.fetchrow(
            "SELECT id FROM monthly_plans WHERE year_id = $1 AND month = $2 AND task = $3",
            year_id, request.month, request.task
        )

        if not goal_row:
            raise HTTPException(status_code=404, detail="Goal not found")

        await db.execute(
            "UPDATE monthly_plans SET completed = $1 WHERE year_id = $2 AND month = $3 AND task = $4",
            request.done, year_id, request.month, request.task
        )

        return {"message": "Goal state updated successfully"}

    except Exception as e:
        logger.error(f"Error updating goal state: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/delete_month_goal")
async def delete_month_goal(
        request: DeleteMonthGoalRequest,
        db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Permanently delete a specific monthly goal/task.

    This endpoint removes a goal entry from the monthly plans database for the specified
    year and month. The deletion is irreversible and will immediately remove the goal
    from all application views.

    Args:
        request (DeleteMonthGoalRequest): A Pydantic model containing:
            - year (int): The target year (e.g., 2023)
            - month (str): The target month name (full English name, e.g., "January")
            - task (str): The exact description of the goal to delete
        db (asyncpg.Connection): Database connection dependency

    Returns:
        Dict[str, str]: A dictionary with operation status:
            - message (str): Success confirmation message

    Raises:
        HTTPException 404:
            - If the specified year is not found
            - If the specified goal is not found for the given month/year
        HTTPException 500: If there's an unexpected server error
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", request.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        goal_row = await db.fetchrow(
            "SELECT id FROM monthly_plans WHERE year_id = $1 AND month = $2 AND task = $3",
            year_id, request.month, request.task
        )

        if not goal_row:
            raise HTTPException(status_code=404, detail="Goal not found")

        await db.execute(
            "DELETE FROM monthly_plans WHERE year_id = $1 AND month = $2 AND task = $3",
            year_id, request.month, request.task
        )

        return {"message": "Goal deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting goal: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/update_month_goal")
async def update_month_goal(
        request: UpdateMonthGoalRequest,
        db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Update the task description of an existing monthly goal.

    This endpoint modifies the text of a specific goal while maintaining its completion status.
    The update affects all application views where the goal appears.

    Args:
        request (UpdateMonthGoalRequest): A Pydantic model containing:
            - year (int): The target year (e.g., 2023)
            - month (str): The target month name (full English name, e.g., "January")
            - old_task (str): The exact current goal description to be modified
            - new_task (str): The new goal description text
        db (asyncpg.Connection): Database connection dependency

    Returns:
        Dict[str, str]: A dictionary with operation status:
            - message (str): Success confirmation message

    Raises:
        HTTPException 404:
            - If the specified year is not found
            - If the specified goal is not found
        HTTPException 500: If there's an unexpected server error
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", request.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        goal_row = await db.fetchrow(
            "SELECT id FROM monthly_plans WHERE year_id = $1 AND month = $2 AND task = $3",
            year_id, request.month, request.old_task
        )

        if not goal_row:
            raise HTTPException(status_code=404, detail="Goal not found")

        await db.execute(
            "UPDATE monthly_plans SET task = $1 WHERE year_id = $2 AND month = $3 AND task = $4",
            request.new_task, year_id, request.month, request.old_task
        )

        return {"message": "Goal updated successfully"}

    except Exception as e:
        logger.error(f"Error updating goal: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/add_month_diary_task")
async def add_month_diary_task(
        request: AddMonthDiaryTaskRequest,
        db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Add a new diary task for a specific date within a month and year.

    This endpoint creates a dated task entry in the monthly diary, which can represent
    daily activities, reminders, or events. Each task is associated with a specific
    calendar date and can be marked as completed or pending.

    Args:
        request (AddMonthDiaryTaskRequest): A Pydantic model containing:
            - year (int): The target year (e.g., 2023)
            - month (str): The target month name (full English name, e.g., "January")
            - date (date): The specific date for the task (YYYY-MM-DD format)
            - task (str): The task description/contents
            - completed (bool): Initial completion status (default: False)
        db (asyncpg.Connection): Database connection dependency

    Returns:
        Dict[str, str]: A dictionary with operation status:
            - message (str): Success confirmation message

    Raises:
        HTTPException 404: If the specified year is not found
        HTTPException 500: If there's an unexpected server error
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", request.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        await db.execute(
            """
            INSERT INTO monthly_diary (year_id, month, date, task, completed) 
            VALUES ($1, $2, $3, $4, $5)
            """,
            year_id, request.month, request.date, request.task, request.completed
        )

        return {"message": "Diary task added successfully"}

    except Exception as e:
        logger.error(f"Error adding diary task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/get_month_diary_tasks")
async def get_month_diary_tasks(
        request: MonthRequest,
        db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Retrieve all diary tasks for a specific month and year, sorted by date.

    This endpoint fetches dated task entries from the monthly diary, returning them in
    chronological order. Each task includes its completion status and is formatted for
    easy display in calendar views or diary interfaces.

    Args:
        request (MonthRequest): A Pydantic model containing:
            - year (int): The target year (e.g., 2023)
            - month (str): The target month name (full English name, e.g., "January")
        db (asyncpg.Connection): Database connection dependency

    Returns:
        Dict[str, List[Dict[str, Union[str, bool]]]: A dictionary containing:
            - tasks (List): Array of task objects sorted by date, each with:
                - date (str): ISO formatted date (YYYY-MM-DD)
                - task (str): The task description
                - completed (bool): Completion status

    Raises:
        HTTPException 404: If the specified year is not found
        HTTPException 500: If there's an unexpected server error
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", request.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        query = """
        SELECT date, task, completed FROM monthly_diary
        WHERE year_id = $1 AND month = $2
        ORDER BY date, id
        """
        rows = await db.fetch(query, year_id, request.month)

        if not rows:
            return {"tasks": []}

        tasks = [
            {"date": row["date"].isoformat(), "task": row["task"], "completed": row["completed"]}
            for row in rows
        ]

        return {"tasks": tasks}

    except Exception as e:
        logger.error(f"Error fetching monthly diary tasks: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/delete_month_diary_task")
async def delete_month_diary_task(
        request: DeleteMonthDiaryTaskRequest,
        db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Permanently delete a specific diary task entry by date and description.

    This endpoint removes a dated task entry from the monthly diary database. The deletion
    is precise, requiring matching year, month, exact task description, and specific date.
    The operation is irreversible and will immediately remove the task from all views.

    Args:
        request (DeleteMonthDiaryTaskRequest): A Pydantic model containing:
            - year (int): The target year (e.g., 2023)
            - month (str): The target month name (full English name, e.g., "January")
            - date (date): The specific date of the task (YYYY-MM-DD format)
            - task (str): The exact description of the task to delete
        db (asyncpg.Connection): Database connection dependency

    Returns:
        Dict[str, str]: A dictionary with operation status:
            - message (str): Success confirmation message

    Raises:
        HTTPException 404:
            - If the specified year is not found
            - If no matching diary task is found for all specified parameters
        HTTPException 500: If there's an unexpected server error
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", request.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        diary_row = await db.fetchrow(
            "SELECT id FROM monthly_diary WHERE year_id = $1 AND month = $2 AND task = $3 AND date = $4",
            year_id, request.month, request.task, request.date
        )

        if not diary_row:
            raise HTTPException(status_code=404, detail="Diary task not found")

        await db.execute(
            "DELETE FROM monthly_diary WHERE year_id = $1 AND month = $2 AND task = $3 AND date = $4",
            year_id, request.month, request.task, request.date
        )

        return {"message": "Diary task deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting diary task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/toggle_month_diary_task")
async def toggle_month_diary_task(
        request: ToggleDiaryTaskRequest,
        db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Toggle or set the completion status of a specific dated diary task.

    This endpoint updates the completion status of a diary task entry, allowing users to
    mark dated tasks as complete or incomplete. The change affects all views where the
    task appears and is immediately reflected in the UI.

    Args:
        request (ToggleDiaryTaskRequest): A Pydantic model containing:
            - year (int): The target year (e.g., 2023)
            - month (str): The target month name (full English name, e.g., "January")
            - date (date): The specific date of the task (YYYY-MM-DD format)
            - task (str): The exact description of the task to update
            - done (bool): The new completion status (true = complete, false = incomplete)
        db (asyncpg.Connection): Database connection dependency

    Returns:
        Dict[str, str]: A dictionary with operation status:
            - message (str): Success confirmation message

    Raises:
        HTTPException 404:
            - If the specified year is not found
            - If no matching diary task is found for all specified parameters
        HTTPException 500: If there's an unexpected server error
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", request.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        task_row = await db.fetchrow(
            "SELECT id FROM monthly_diary WHERE year_id = $1 AND month = $2 AND task = $3 AND date = $4",
            year_id, request.month, request.task, request.date
        )

        if not task_row:
            raise HTTPException(status_code=404, detail="Task not found")

        await db.execute(
            "UPDATE monthly_diary SET completed = $1 WHERE year_id = $2 AND month = $3 AND task = $4 AND date = $5",
            request.done, year_id, request.month, request.task, request.date
        )

        return {"message": "Diary task status updated successfully"}

    except Exception as e:
        logger.error(f"Error updating diary task status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/update_month_diary_task")
async def update_month_diary_task(
        request: UpdateMonthDiaryTaskRequest,
        db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Update the description of an existing dated diary task.

    This endpoint modifies the task description while maintaining its date and completion status.
    The update affects all application views where the task appears.

    Args:
        request (UpdateMonthDiaryTaskRequest): A Pydantic model containing:
            - year (int): The target year (e.g., 2023)
            - month (str): The target month name (full English name, e.g., "January")
            - date (date): The specific date of the task (YYYY-MM-DD format)
            - old_task (str): The exact current task description to be modified
            - new_task (str): The new task description text
        db (asyncpg.Connection): Database connection dependency

    Returns:
        Dict[str, str]: A dictionary with operation status:
            - message (str): Success confirmation message

    Raises:
        HTTPException 404:
            - If the specified year is not found
            - If no matching diary task is found for all specified parameters
        HTTPException 500: If there's an unexpected server error
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", request.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        diary_row = await db.fetchrow(
            """
            SELECT id FROM monthly_diary
            WHERE year_id = $1 AND month = $2 AND date = $3 AND task = $4
            """,
            year_id, request.month, request.date, request.old_task
        )

        if not diary_row:
            raise HTTPException(status_code=404, detail="Task not found")

        await db.execute(
            """
            UPDATE monthly_diary
            SET task = $1
            WHERE year_id = $2 AND month = $3 AND date = $4 AND task = $5
            """,
            request.new_task, year_id, request.month, request.date, request.old_task
        )

        return {"message": "Diary task updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
