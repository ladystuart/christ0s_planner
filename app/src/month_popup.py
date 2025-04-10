from fastapi import APIRouter, Depends, HTTPException
import logging
import asyncpg
from config.get_db_connection import get_db_connection
from pydantic import BaseModel
import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter()


class MonthRequest(BaseModel):
    year: int
    month: str


class PopupColorRequest(BaseModel):
    year: int
    month: str
    date: datetime.date
    colour_code: str


class PopupDataRequest(BaseModel):
    year: int
    month: str
    date: datetime.date
    popup_message: str


class PopupColorDelete(BaseModel):
    year: int
    month: str
    date: datetime.date


class PopupDataDelete(BaseModel):
    year: int
    month: str
    date: datetime.date


@router.get("/get_popup_colour")
async def get_popup_color(request: MonthRequest, db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Retrieve color codes and dates for popup tasks for a specific month and year.

    This endpoint fetches all task color information (color codes and associated dates)
    from the database for the specified month and year. The data is returned as a list
    of dictionaries containing color codes and dates.

    Args:
        request (MonthRequest): A Pydantic model containing:
            - year (int): The year to query (e.g., 2023)
            - month (int): The month to query (1-12)
        db (asyncpg.Connection): Database connection dependency

    Returns:
        List[Dict[str, Any]]: A list of dictionaries where each dictionary contains:
            - colour_code (str): The color code associated with a task
            - date (date): The date of the task

    Raises:
        HTTPException 404: If the specified year is not found in the database
        HTTPException 500: If there's an unexpected server error during processing
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", request.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        query = """
        SELECT colour_code, date
        FROM task_colours
        WHERE year_id = $1 AND month = $2
        """
        rows = await db.fetch(query, year_id, request.month)

        if not rows:
            return []

        result = [{"colour_code": row["colour_code"], "date": row["date"]} for row in rows]

        return result

    except Exception as e:
        logger.error(f"Error fetching popup color: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/get_popup_data")
async def get_popup_data(request: MonthRequest, db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Retrieve popup messages and their associated dates for a specific month and year.

    This endpoint fetches all popup messages and their corresponding dates from the database
    for the specified month and year. The data is returned as a list of dictionaries
    containing the popup messages and dates.

    Args:
        request (MonthRequest): A Pydantic model containing:
            - year (int): The year to query (e.g., 2023)
            - month (int): The month to query (1-12)
        db (asyncpg.Connection): Database connection dependency

    Returns:
        List[Dict[str, Any]]: A list of dictionaries where each dictionary contains:
            - popup_message (str): The message content to be displayed in the popup
            - date (date): The date associated with the popup message

    Raises:
        HTTPException 404: If the specified year is not found in the database
        HTTPException 500: If there's an unexpected server error during processing
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", request.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        query = """
        SELECT popup_message, date
        FROM task_popups
        WHERE year_id = $1 AND month = $2
        """
        rows = await db.fetch(query, year_id, request.month)

        if not rows:
            return []

        result = [{"popup_message": row["popup_message"], "date": row["date"]} for row in rows]

        return result

    except Exception as e:
        logger.error(f"Error fetching popup data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/add_month_popup_colour")
async def add_popup_color(
        request: PopupColorRequest,
        db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Add a new popup color entry for a specific date in a given month and year.

    This endpoint inserts a new color code associated with a specific date into the database.
    The color will be used to display visual indicators (like colored markers) in the calendar UI.

    Args:
        request (PopupColorRequest): A Pydantic model containing:
            - year (int): The target year (e.g., 2023)
            - month (int): The target month (1-12)
            - date (date): The specific date for the color marker (YYYY-MM-DD format)
            - colour_code (str): The hexadecimal color code (e.g., "#FF5733")
        db (asyncpg.Connection): Database connection dependency

    Returns:
        Dict[str, str]: A dictionary with operation status:
            - status (str): "success" if operation completed
            - message (str): Human-readable result message

    Raises:
        HTTPException 404: If the specified year is not found in the database
        HTTPException 500: If there's an unexpected server error during insertion
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", request.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        query = """
        INSERT INTO task_colours (year_id, month, date, colour_code)
        VALUES ($1, $2, $3, $4)
        """
        await db.execute(query, year_id, request.month, request.date, request.colour_code)

        return {"status": "success", "message": "Popup color added successfully"}

    except Exception as e:
        logger.error(f"Error adding popup color: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/add_month_popup_data")
async def add_popup_data(
        request: PopupDataRequest,
        db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Add a new popup message entry for a specific date in a given month and year.

    This endpoint inserts a new popup message that will be displayed when interacting with
    the specified date in the calendar UI. The message typically contains event details,
    reminders, or other date-specific information.

    Args:
        request (PopupDataRequest): A Pydantic model containing:
            - year (int): The target year (e.g., 2023)
            - month (int): The target month (1-12)
            - date (date): The specific date for the popup (YYYY-MM-DD format)
            - popup_message (str): The content to be displayed in the popup
        db (asyncpg.Connection): Database connection dependency

    Returns:
        Dict[str, str]: A dictionary with operation status:
            - status (str): "success" if operation completed
            - message (str): Human-readable result message

    Raises:
        HTTPException 404: If the specified year is not found in the database
        HTTPException 500: If there's an unexpected server error during insertion
        HTTPException 400: If the input data validation fails
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", request.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        query = """
        INSERT INTO task_popups (year_id, month, date, popup_message)
        VALUES ($1, $2, $3, $4)
        """
        await db.execute(query, year_id, request.month, request.date, request.popup_message)

        return {"status": "success", "message": "Popup data added successfully"}

    except Exception as e:
        logger.error(f"Error adding popup data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/delete_month_popup_colour")
async def delete_popup_colour(
        request: PopupColorDelete,
        db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Delete a popup color entry for a specific date in a given month and year.

    This endpoint removes a color marker associated with a specific date from the database.
    After deletion, the color indicator will no longer appear on the calendar UI for the specified date.

    Args:
        request (PopupColorDelete): A Pydantic model containing:
            - year (int): The target year (e.g., 2023)
            - month (int): The target month (1-12)
            - date (date): The specific date to remove the color from (YYYY-MM-DD format)
        db (asyncpg.Connection): Database connection dependency

    Returns:
        Dict[str, str]: A dictionary with operation status:
            - status (str): "success" if deletion completed
            - message (str): Human-readable result message

    Raises:
        HTTPException 404:
            - If the specified year is not found in the database
            - If no color entry exists for the specified date
        HTTPException 500: If there's an unexpected server error during deletion
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", request.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        query = """
        DELETE FROM task_colours
        WHERE year_id = $1 AND month = $2 AND date = $3
        """
        result = await db.execute(query, year_id, request.month, request.date)

        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Popup color not found for the given date")

        return {"status": "success", "message": "Popup color deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting popup color: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/delete_month_popup_data")
async def delete_popup_data(
        request: PopupDataDelete,
        db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Delete a popup message entry for a specific date in a given month and year.

    This endpoint removes a popup message associated with a specific date from the database.
    After successful deletion, the popup will no longer appear when users interact with
    the specified date in the calendar interface.

    Args:
        request (PopupDataDelete): A Pydantic model containing:
            - year (int): The target year (e.g., 2023)
            - month (int): The target month (1-12)
            - date (date): The specific date to remove the popup from (YYYY-MM-DD format)
        db (asyncpg.Connection): Database connection dependency

    Returns:
        Dict[str, str]: A dictionary with operation status:
            - status (str): "success" if deletion completed successfully
            - message (str): Human-readable result message

    Raises:
        HTTPException 404:
            - If the specified year is not found in the database
            - If no popup message exists for the specified date
        HTTPException 500: If there's an unexpected server error during deletion
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", request.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        query = """
        DELETE FROM task_popups
        WHERE year_id = $1 AND month = $2 AND date = $3
        """
        result = await db.execute(query, year_id, request.month, request.date)

        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Popup data not found for the given date")

        return {"status": "success", "message": "Popup data deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting popup data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
