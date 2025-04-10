from fastapi import APIRouter, Depends, HTTPException
import logging
import asyncpg
from pathlib import Path
from pydantic import BaseModel
import shutil
import traceback
from datetime import datetime
from config.get_db_connection import get_db_connection
from config.months_data import months_data
from config.habit_tracker_data import TASKS
from config.review_data import REVIEW_QUESTIONS

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

YEAR_UPLOAD_FOLDER = Path(__file__).resolve().parent.parent.parent / "uploads" / "assets" / "yearly_plans" / "year"

router = APIRouter()


class YearRequest(BaseModel):
    year: int


class YearUpdateRequest(BaseModel):
    old_year: int
    new_year: int


@router.get("/get_years")
async def get_years(db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Retrieves a list of all years stored in the `years` table, ordered by year in descending order.

    This endpoint fetches the `id` and `year` columns from the `years` table and returns them as a list of dictionaries.

    Args:
        db (asyncpg.Connection): Database connection provided via dependency injection.

    Returns:
        list[dict]: A list of dictionaries, each containing the `id` and `year` of a year in the database.

    Raises:
        HTTPException (500): If an internal server error occurs.
    """
    try:
        rows = await db.fetch("SELECT id, year FROM years ORDER BY year DESC")
        return [{"id": row["id"], "year": row["year"]} for row in rows]
    except Exception as e:
        return {"error": "internal server error"}


@router.post("/add_year", status_code=200)
async def add_year(year_data: dict, db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Adds a new year entry into the `years` table and initializes related records in other tables.

    This endpoint performs the following actions:
    1. Verifies if the provided year is a valid integer.
    2. Checks if the year already exists in the `years` table.
    3. Inserts the new year into the `years` table.
    4. Initializes related entries in the `review`, `months`, and `habit_tracker` tables for the new year.

    Args:
        year_data (dict): A dictionary containing the `year` key with the year to be added.
        db (asyncpg.Connection): Database connection provided via dependency injection.

    Returns:
        int: The ID of the newly added year in the `years` table.

    Raises:
        HTTPException (400): If the year is invalid or already exists in the database.
        HTTPException (500): If a database error occurs during the process.
    """
    year = year_data.get("year")
    if not isinstance(year, int):
        raise HTTPException(status_code=400, detail="Invalid year format")

    try:
        existing_year = await db.fetchrow("SELECT id FROM years WHERE year = $1", year)
        if existing_year:
            raise HTTPException(status_code=400, detail="Year already exists")

        new_year = await db.fetchval("INSERT INTO years (year) VALUES ($1) RETURNING id", year)

        await db.executemany(
            "INSERT INTO review (year_id, question, answer) VALUES ($1, $2, '')",
            [(new_year, question) for question in REVIEW_QUESTIONS]
        )

        for month_name, data in months_data.items():
            await db.execute("""
                INSERT INTO months (year_id, month_name, icon_path, banner, reading_link, month_icon_path)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, new_year, month_name, data["icon_path"], data["banner"], data["reading_link"], data["month_icon_path"])

        week_starting = datetime.strptime(f"{year}-01-01", "%Y-%m-%d").date()

        for day_of_week, task in TASKS:
            await db.execute("""
                INSERT INTO habit_tracker (year_id, week_starting, day_of_week, task, completed)
                VALUES ($1, $2, $3, $4, FALSE)
            """, new_year, week_starting, day_of_week, task)

        return new_year
    except Exception as e:
        logger.error(f"Database error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Database error")


@router.delete("/delete_year")
async def delete_year(request: YearRequest, db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Deletes a year entry from the database and removes related files from the server.

    This endpoint performs the following actions:
    1. Verifies if the year exists in the `years` table.
    2. Deletes the year from the `years` table.
    3. Attempts to remove the corresponding folder from the file system, if it exists.

    Args:
        request (YearRequest): A request object containing the `year` to be deleted.
        db (asyncpg.Connection): Database connection provided via dependency injection.

    Returns:
        dict: A message indicating the success of the deletion.

    Raises:
        HTTPException (404): If the year does not exist in the `years` table.
        HTTPException (500): If an internal server error occurs during the deletion process.
    """
    year = request.year

    try:
        existing_year = await db.fetchrow("SELECT id FROM years WHERE year = $1", year)
        if not existing_year:
            raise HTTPException(status_code=404, detail="Year not found")

        await db.execute("DELETE FROM years WHERE year = $1", year)

        year_folder = YEAR_UPLOAD_FOLDER / str(year)

        if year_folder.exists() and year_folder.is_dir():
            shutil.rmtree(year_folder)
        else:
            logger.warning(f"Year {year} folder not found.")

        return {"message": f"Year {year} and related data deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting year {year}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/edit_year")
async def edit_year(request: YearUpdateRequest, db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Updates the year in the database and renames the corresponding folder on the server.

    This endpoint performs the following actions:
    1. Updates the year in the `years` table.
    2. Adjusts the `week_starting` dates in the `habit_tracker` table to reflect the new year.
    3. Renames the folder corresponding to the year in the file system, if it exists.

    Args:
        request (YearUpdateRequest): A request object containing the `old_year` and `new_year` values.
        db (asyncpg.Connection): Database connection provided via dependency injection.

    Returns:
        dict: A message indicating the success of the update.

    Raises:
        HTTPException (404): If the `old_year` does not exist in the `years` table.
        HTTPException (409): If the `new_year` already exists in the `years` table.
        HTTPException (500): If an internal server error occurs during the update process.
    """
    try:
        result = await db.execute(
            "UPDATE years SET year = $1 WHERE year = $2",
            request.new_year,
            request.old_year
        )

        new_year_id = await db.fetchval("SELECT id FROM years WHERE year = $1", request.new_year)

        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Old year not found")

        await db.execute("""
            UPDATE habit_tracker
            SET week_starting = 
                DATE_TRUNC('year', week_starting) + INTERVAL '1 year' * ($1 - EXTRACT(YEAR FROM week_starting)::int)
            WHERE year_id = $2
        """, request.new_year, new_year_id)

        old_folder = YEAR_UPLOAD_FOLDER / str(request.old_year)
        new_folder = YEAR_UPLOAD_FOLDER / str(request.new_year)

        if old_folder.exists() and old_folder.is_dir():
            shutil.move(str(old_folder), str(new_folder))
        else:
            logger.warning(f"Folder for year {request.old_year} not found")

        return {"message": f"Year {request.old_year} updated to {request.new_year}"}

    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=409, detail="New year already exists")

    except Exception as e:
        logger.error(f"Error updating year {request.old_year} to {request.new_year}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
