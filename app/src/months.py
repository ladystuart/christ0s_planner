from fastapi import APIRouter, Depends, HTTPException
import logging
import asyncpg
from config.get_db_connection import get_db_connection
from pydantic import BaseModel

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter()


class MonthIconUpdate(BaseModel):
    month_name: str
    year: int
    icon_path: str


@router.get("/get_months_states")
async def get_months_states(year: int, db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Retrieve all months with their associated icons for a given year.

    This endpoint returns the list of months and their corresponding icon paths
    for the specified year, typically used to display the calendar navigation
    or year overview interface.

    Args:
        year (int): The target year to fetch months for (e.g., 2023)
        db (asyncpg.Connection): Database connection dependency

    Returns:
        List[Dict[str, str]]: A list of month objects, each containing:
            - month_name (str): Full month name (e.g., "January")
            - icon_path (str): Path/URL to the month's icon image

    Raises:
        HTTPException 404: If the specified year is not found
        HTTPException 500: If there's an unexpected server error
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]
        rows = await db.fetch("SELECT month_name, icon_path FROM months WHERE year_id = $1", year_id)

        months_data = [
            {"month_name": row["month_name"], "icon_path": row["icon_path"]}
            for row in rows
        ]

        return months_data
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/update_months_icon_status")
async def update_month_icon(
        data: MonthIconUpdate,
        db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Update the icon path for a specific month in a given year.

    This endpoint modifies the visual icon associated with a calendar month,
    which is typically displayed in month selection interfaces and overviews.

    Args:
        data (MonthIconUpdate): A Pydantic model containing:
            - year (int): The target year (e.g., 2023)
            - month_name (str): The full month name to update (e.g., "January")
            - icon_path (str): The new path/URL for the month's icon image
        db (asyncpg.Connection): Database connection dependency

    Returns:
        Dict[str, str]: A dictionary with operation status:
            - message (str): Success confirmation message

    Raises:
        HTTPException 404:
            - If the specified year is not found
            - If the specified month is not found for the given year
        HTTPException 500: If there's an unexpected server error
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", data.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]
        result = await db.execute(
            """
            UPDATE months 
            SET icon_path = $1 
            WHERE year_id = $2 AND month_name = $3
            """,
            data.icon_path, year_id, data.month_name
        )

        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Month not found")

        return {"message": "Icon updated successfully"}
    except Exception as e:
        logger.error(f"Error updating icon: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
