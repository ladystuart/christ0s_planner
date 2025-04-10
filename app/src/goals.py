from fastapi import APIRouter, HTTPException
from config.get_db_connection import get_db_connection
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter()


class NewGoal(BaseModel):
    title: str


class GoalUpdateStatus(BaseModel):
    title: str
    completed: bool


class GoalDeleteRequest(BaseModel):
    title: str


class GoalUpdateTitle(BaseModel):
    new_title: str
    title: str


@router.get("/get_goals")
async def get_goals():
    """
    Retrieves a list of goals from the database.

    Returns:
        List[dict]: A list of goals, where each goal is represented as a dictionary with:
            - text (str): The title of the goal.
            - completed (bool): The completion status of the goal.

    Raises:
        HTTPException:
            - 500 if there is an error while retrieving the goals from the database.
    """
    try:
        conn = await get_db_connection()

        rows = await conn.fetch("SELECT title, completed FROM goals ORDER BY id;")

        await conn.close()
        return [{"text": row["title"], "completed": row["completed"]} for row in rows]
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update_goal_status")
async def update_goal_status(task: GoalUpdateStatus):
    """
    Updates the completion status of a goal in the database.

    Args:
        task (GoalUpdateStatus): An object containing:
            - title (str): The title of the goal to be updated.
            - completed (bool): The new completion status of the goal.

    Returns:
        dict: A message indicating whether the goal was successfully updated.

    Raises:
        HTTPException:
            - 404 if the goal with the given title is not found.
            - 500 if there is an internal server error during the update.
    """
    try:
        conn = await get_db_connection()
        query = "UPDATE goals SET completed = $1 WHERE title = $2;"
        result = await conn.execute(query, task.completed, task.title)

        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Task not found")

        return {"message": "Task updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()


@router.post("/delete_goal")
async def delete_goal(task: GoalDeleteRequest):
    """
    Deletes a goal from the database based on the given title.

    Args:
        task (GoalDeleteRequest): An object containing:
            - title (str): The title of the goal to delete.

    Returns:
        dict: A message indicating whether the goal was successfully deleted.

    Raises:
        HTTPException:
            - 404 if the goal with the specified title is not found.
            - 500 if an internal server error occurs during deletion.
    """
    try:
        conn = await get_db_connection()
        query = "DELETE FROM goals WHERE title = $1;"
        result = await conn.execute(query, task.title)

        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Task not found")

        return {"message": "Task deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()


@router.post("/update_goal_title")
async def update_goal_status(task: GoalUpdateTitle):
    """
    Updates the title of an existing goal in the database.

    Args:
        task (GoalUpdateTitle): An object containing:
            - title (str): The current title of the goal.
            - new_title (str): The new title to update the goal with.

    Returns:
        dict: A message indicating whether the goal's title was successfully updated.

    Raises:
        HTTPException:
            - 404 if the goal with the specified title is not found.
            - 500 if an internal server error occurs during the update.
    """
    try:
        conn = await get_db_connection()

        query = "UPDATE goals SET title = $1 WHERE title = $2;"
        result = await conn.execute(query, task.new_title, task.title)

        if not result:
            raise HTTPException(status_code=404, detail="Task not found")

        await conn.close()

        return {"message": "Task updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/add_new_goal")
async def update_goal(task: NewGoal):
    """
    Adds a new goal to the database with the given title and sets its completed status to False by default.

    Args:
        task (NewGoal): An object containing:
            - title (str): The title of the new goal to add.

    Returns:
        dict: A message indicating whether the goal was successfully added.

    Raises:
        HTTPException:
            - 400 if the goal could not be added.
            - 500 if an internal server error occurs during insertion.
    """
    try:
        conn = await get_db_connection()
        query = "INSERT INTO goals (title, completed) VALUES ($1, FALSE);"
        result = await conn.execute(query, task.title)

        if result:
            return {"message": "Goal added successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to add goal")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        await conn.close()
