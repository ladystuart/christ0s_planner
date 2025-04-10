from fastapi import APIRouter, Depends, HTTPException
import logging
import asyncpg
from config.get_db_connection import get_db_connection
from pydantic import BaseModel
import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter()


class GratitudeEntry(BaseModel):
    year: int
    date: datetime.date
    entry: str


class GratitudeEntryDelete(BaseModel):
    year: int
    date: datetime.date


@router.post("/task_add_gratitude_diary")
async def add_gratitude_entry(entry_data: GratitudeEntry, db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Adds a new entry to the gratitude diary for the specified year.

    Args:
        entry_data (GratitudeEntry): An object containing:
            - year (int): The year for which the gratitude entry is being added.
            - date (str): The date of the entry.
            - entry (str): The content of the gratitude entry.
        db (asyncpg.Connection): A database connection object, injected via Depends.

    Returns:
        dict: A message indicating the success of the entry addition.

    Raises:
        HTTPException:
            - 404 if the specified year is not found in the database.
            - 500 if an internal server error occurs while adding the entry.
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", entry_data.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        await db.execute(
            "INSERT INTO gratitude_diary (year_id, entry_date, content) VALUES ($1, $2, $3)",
            year_id, entry_data.date, entry_data.entry
        )
        return {"message": "Gratitude entry added successfully"}

    except Exception as e:
        logger.error(f"Error adding gratitude entry: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/get_gratitude_diary_entries")
async def get_gratitude_entries(year: int, db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Retrieves all gratitude diary entries for the specified year.

    Args:
        year (int): The year for which gratitude entries are being fetched.
        db (asyncpg.Connection): A database connection object, injected via Depends.

    Returns:
        list: A list of dictionaries where each dictionary contains:
            - date (str): The date of the gratitude entry in "YYYY-MM-DD" format.
            - entry (str): The content of the gratitude entry.

    Raises:
        HTTPException:
            - 404 if the specified year is not found in the database.
            - 500 if an internal server error occurs while fetching the entries.
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        entries = await db.fetch(
            "SELECT entry_date, content FROM gratitude_diary WHERE year_id = $1 ORDER BY entry_date",
            year_id
        )

        gratitude_entries = [
            {"date": entry['entry_date'].strftime("%Y-%m-%d"), "entry": entry['content']}
            for entry in entries
        ]

        return gratitude_entries

    except Exception as e:
        logger.error(f"Error fetching gratitude entries: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/gratitude_diary_edit")
async def edit_gratitude_entries(entry_data: GratitudeEntry, db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Edits an existing gratitude diary entry for a given year and date, or creates a new one if none exists.

    Args:
        entry_data (GratitudeEntry): The data for the gratitude entry, including the year, date, and content.
        db (asyncpg.Connection): A database connection object, injected via Depends.

    Returns:
        dict: A message indicating whether the entry was updated or created successfully.

    Raises:
        HTTPException:
            - 404 if the specified year is not found in the database.
            - 500 if an internal server error occurs while updating or inserting the entry.
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", entry_data.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        existing_entry = await db.fetchrow(
            "SELECT id FROM gratitude_diary WHERE year_id = $1 AND entry_date = $2",
            year_id, entry_data.date
        )

        if existing_entry:
            await db.execute(
                "UPDATE gratitude_diary SET content = $1 WHERE id = $2",
                entry_data.entry, existing_entry["id"]
            )
        else:
            await db.execute(
                "INSERT INTO gratitude_diary (year_id, entry_date, content) VALUES ($1, $2, $3)",
                year_id, entry_data.date, entry_data.entry
            )

        return {"message": "Gratitude diary entry updated successfully"}

    except Exception as e:
        logger.error(f"Error updating gratitude diary entry: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/gratitude_diary_delete")
async def delete_gratitude_entry(entry_data: GratitudeEntryDelete, db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Deletes a gratitude diary entry for a given year and date.

    Args:
        entry_data (GratitudeEntryDelete): The data for the gratitude entry to be deleted, including the year and date.
        db (asyncpg.Connection): A database connection object, injected via Depends.

    Returns:
        dict: A message indicating whether the entry was deleted successfully.

    Raises:
        HTTPException:
            - 404 if the specified year or entry does not exist.
            - 500 if an internal server error occurs while deleting the entry.
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", entry_data.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        result = await db.execute(
            "DELETE FROM gratitude_diary WHERE year_id = $1 AND entry_date = $2",
            year_id, entry_data.date
        )

        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Entry not found")

        return {"message": "Entry deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting gratitude diary entry: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
