from fastapi import APIRouter, Depends, HTTPException
import logging
import asyncpg
from typing import List
from config.get_db_connection import get_db_connection
from pydantic import BaseModel

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter()


class Review(BaseModel):
    question: str
    answer: str


class ReviewUpdate(BaseModel):
    year: int
    reviews: List[dict]


@router.get("/get_review", response_model=List[Review])
async def get_review(year: int, db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Retrieve all review questions and answers for a specific year.

    This endpoint fetches the complete set of review questions and their corresponding
    answers for the specified year. The data is typically used for annual reflections,
    retrospectives, or year-in-review features.

    Args:
        year (int): The target year to fetch review data for (e.g., 2023)
        db (asyncpg.Connection): Database connection dependency

    Returns:
        List[Review]: A list of Review objects containing:
            - question (str): The review question prompt
            - answer (str): The recorded answer to the question

    Raises:
        HTTPException 404:
            - If the specified year is not found
            - If no review data exists for the specified year
        HTTPException 500: If there's an unexpected server error
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        query = """
        SELECT question, answer
        FROM review
        WHERE year_id = $1
        """
        records = await db.fetch(query, year_id)

        if not records:
            raise HTTPException(status_code=404, detail="No review data found for the year")

        return [Review(question=record['question'], answer=record['answer']) for record in records]

    except Exception as e:
        logger.error(f"Error fetching review data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/update_review")
async def update_review(data: ReviewUpdate, db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Update or create review questions and answers for a specific year.

    This endpoint performs an upsert operation (update or insert) for annual review data.
    It can handle both new questions and updates to existing ones in a single request.

    Args:
        data (ReviewUpdate): A Pydantic model containing:
            - year (int): The target year for review data (e.g., 2023)
            - reviews (List[Dict]): List of review items, each containing:
                - question (str): The review question text
                - answer (str): The answer to store for this question
        db (asyncpg.Connection): Database connection dependency

    Returns:
        Dict[str, str]: A dictionary with operation status:
            - message (str): Success confirmation message

    Raises:
        HTTPException 404: If the specified year is not found
        HTTPException 400: If required fields are missing
        HTTPException 500: If there's a database error during update
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", data.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        for review in data.reviews:
            question = review["question"]
            answer = review["answer"]

            existing_record = await db.fetchrow(
                "SELECT id FROM review WHERE year_id = $1 AND question = $2", year_id, question
            )

            if existing_record:
                await db.execute(
                    "UPDATE review SET answer = $1 WHERE year_id = $2 AND question = $3",
                    answer, year_id, question
                )
            else:
                await db.execute(
                    "INSERT INTO review (year_id, question, answer) VALUES ($1, $2, $3)",
                    year_id, question, answer
                )

        return {"message": "Review data updated successfully"}

    except Exception as e:
        logger.error(f"Error updating review data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
