from fastapi import APIRouter, HTTPException
from config.get_db_connection import get_db_connection
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter()


class NewCourse(BaseModel):
    title: str


class CourseUpdateStatus(BaseModel):
    title: str
    completed: bool


class CourseDeleteRequest(BaseModel):
    title: str


class CourseUpdateTitle(BaseModel):
    new_title: str
    title: str


@router.get("/get_courses")
async def get_courses():
    """
    Retrieves a list of courses with their completion status from the database.

    Returns:
        list: A list of dictionaries, each containing:
              - 'text': the course title,
              - 'completed': a boolean indicating whether the course is completed.

    Raises:
        HTTPException:
            - 500 if there is an error while fetching data from the database.
    """
    try:
        conn = await get_db_connection()

        rows = await conn.fetch("SELECT title, completed FROM courses ORDER BY id;")

        await conn.close()
        return [{"text": row["title"], "completed": row["completed"]} for row in rows]
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update_course_status")
async def update_course_status(task: CourseUpdateStatus):
    """
    Updates the completion status of a course in the database.

    Args:
        task (CourseUpdateStatus): An object containing:
            - title (str): The title of the course.
            - completed (bool): The updated completion status of the course.

    Returns:
        dict: A message indicating whether the course status was successfully updated.

    Raises:
        HTTPException:
            - 404 if no course with the given title is found.
            - 500 if there is an error during the update operation.
    """
    try:
        conn = await get_db_connection()
        query = "UPDATE courses SET completed = $1 WHERE title = $2;"
        result = await conn.execute(query, task.completed, task.title)

        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Task not found")

        return {"message": "Task updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()


@router.post("/delete_course")
async def delete_course(task: CourseDeleteRequest):
    """
    Deletes a course from the database based on the provided course title.

    Args:
        task (CourseDeleteRequest): An object containing:
            - title (str): The title of the course to be deleted.

    Returns:
        dict: A message indicating whether the course was successfully deleted.

    Raises:
        HTTPException:
            - 404 if the course with the given title is not found.
            - 500 if there is an error during the deletion process.
    """
    try:
        conn = await get_db_connection()
        query = "DELETE FROM courses WHERE title = $1;"
        result = await conn.execute(query, task.title)

        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Task not found")

        return {"message": "Task deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()


@router.post("/update_course_title")
async def update_course_status(task: CourseUpdateTitle):
    """
    Updates the title of a course in the database.

    Args:
        task (CourseUpdateTitle): An object containing:
            - title (str): The current title of the course.
            - new_title (str): The new title to update the course with.

    Returns:
        dict: A message indicating whether the course title was successfully updated.

    Raises:
        HTTPException:
            - 404 if no course with the given title is found.
            - 500 if there is an internal server error during the update process.
    """
    try:
        conn = await get_db_connection()

        query = "UPDATE courses SET title = $1 WHERE title = $2;"
        result = await conn.execute(query, task.new_title, task.title)

        if not result:
            raise HTTPException(status_code=404, detail="Task not found")

        await conn.close()

        return {"message": "Task updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/add_new_course")
async def add_course(task: NewCourse):
    """
    Adds a new course to the database with the given title.
    The course is marked as not completed by default.

    Args:
        task (NewCourse): An object containing:
            - title (str): The title of the new course.

    Returns:
        dict: A message indicating whether the course was successfully added.

    Raises:
        HTTPException:
            - 400 if the course could not be added.
            - 500 if an internal server error occurs.
    """
    try:
        conn = await get_db_connection()
        query = "INSERT INTO courses (title, completed) VALUES ($1, FALSE);"
        result = await conn.execute(query, task.title)

        if result:
            return {"message": "Course added successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to add course")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        await conn.close()
