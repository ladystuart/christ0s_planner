import asyncpg
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from pydantic import BaseModel
from pathlib import Path
import shutil
import logging
from config.get_db_connection import get_db_connection

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

IMAGE_UPLOAD_FOLDER = Path(__file__).resolve().parent.parent.parent / "uploads" / "assets" / "yearly_plans" / "year"
IMAGE_UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

router = APIRouter()


class BestInMonthsData(BaseModel):
    year: int
    month: str
    image_path: str


class YearRequest(BaseModel):
    year: int


class ImageDeleteRequest(BaseModel):
    file_name: str


class BestInMonthsDeleteRequest(BaseModel):
    year: int
    month: str


@router.post("/upload_best_in_month_image/{year}")
async def upload_best_in_month_image(year: int, file: UploadFile = File(...)):
    """
    Uploads an image for the 'best in month' for a given year and stores it in the server.

    This endpoint handles the upload of an image for a specified year. It ensures that a folder for that year exists on
    the server and saves the uploaded image to that folder. A unique file name is used to prevent overwriting existing files.
    The image is stored in the specified directory, and the function returns a success message along with the path to the uploaded image.

    Args:
        year (int): The year for which the 'best in month' image is being uploaded.
        file (UploadFile): The image file being uploaded.

    Returns:
        dict: A success message with the path to the uploaded image.

    Raises:
        HTTPException: If an error occurs during the file upload process, a 500 status code is returned with the error message.
    """
    try:
        # Ensure the directory for the year exists
        year_folder = IMAGE_UPLOAD_FOLDER / str(year)
        year_folder.mkdir(parents=True, exist_ok=True)

        # Create a unique file name or use the original file name
        file_location = year_folder / file.filename

        # Save the file to the server
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Return a success response
        return {"message": "Image uploaded successfully", "image_path": str(file_location)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")


@router.post("/add_best_in_months_data")
async def add_best_in_months_data(data: BestInMonthsData, db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Adds data for the 'best in month' image to the database.

    This endpoint inserts information about the 'best in month' image for a specified year and month into the database.
    If the year does not exist in the database, it is first created. The function then inserts the month and image path
    for the 'best in month' into the corresponding table.

    Args:
        data (BestInMonthsData): The data containing the year, month, and image path for the 'best in month'.
        db (asyncpg.Connection): The database connection used to execute queries.

    Returns:
        dict: A success message indicating that the data was added successfully.

    Raises:
        HTTPException: If an error occurs during the database operation, a 500 status code is returned with the error message.
    """
    try:
        year_id_query = "SELECT id FROM years WHERE year = $1"
        year_id = await db.fetchval(year_id_query, data.year)

        if not year_id:
            year_id = await db.fetchval("INSERT INTO years (year) VALUES ($1) RETURNING id", data.year)

        insert_query = """
            INSERT INTO best_in_months (year_id, month, image_path)
            VALUES ($1, $2, $3)
        """
        await db.execute(insert_query, year_id, data.month, data.image_path)

        return {"message": "Data added successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add data: {str(e)}")


@router.get("/get_best_in_months_data")
async def get_best_in_months_data(request: YearRequest, db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Retrieves the 'best in month' data for a specified year from the database.

    This endpoint fetches the 'best in month' images for each month of a specified year.
    The function first checks if the specified year exists in the database. If the year is found, it retrieves the
    corresponding months and image paths, returning them in order of the months.

    Args:
        request (YearRequest): The request containing the year for which to fetch the 'best in month' data.
        db (asyncpg.Connection): The database connection used to execute queries.

    Returns:
        list: A list of dictionaries, each containing a 'month' and the corresponding 'image_path'.

    Raises:
        HTTPException:
            - If the year is not found in the database, a 404 status code is returned with the error message.
            - If an internal server error occurs during the database operation, a 500 status code is returned.
    """
    try:
        year = request.year

        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        rows = await db.fetch(
            "SELECT month, image_path FROM best_in_months WHERE year_id = $1 ORDER BY month",
            year_id
        )

        return [{"month": row["month"], "image_path": row["image_path"]} for row in rows]

    except Exception as e:
        logger.error(f"Error fetching best in months data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/delete_best_in_month_image/{year}")
async def delete_best_in_month_image(year: int, request: ImageDeleteRequest):
    """
    Deletes a 'best in month' image for a specified year.

    This endpoint allows the deletion of a specific image associated with a year.
    The function checks if the folder for the given year exists, and then verifies whether the
    image file to be deleted exists within that folder. If the image is found, it is deleted;
    otherwise, appropriate error messages are returned.

    Args:
        year (int): The year associated with the image to be deleted.
        request (ImageDeleteRequest): The request containing the file name of the image to delete.

    Returns:
        dict: A success message indicating the image was deleted.

    Raises:
        HTTPException:
            - If the folder for the specified year does not exist, a 404 status code is returned with the error message "folder not found".
            - If the image file does not exist, a 404 status code is returned with the error message "image not found".
            - If an internal error occurs during the file deletion process, a 500 status code is returned with the error message.
    """
    try:
        year_folder = IMAGE_UPLOAD_FOLDER / str(year)

        if not year_folder.exists():
            raise HTTPException(status_code=404, detail="folder not found")

        image_path = year_folder / request.file_name

        if not image_path.exists():
            raise HTTPException(status_code=404, detail="image not found")

        image_path.unlink()

        return {"message": f"image '{request.file_name}' deleted successfully"}

    except Exception as e:
        logger.error(f"image delete error: {e}")
        raise HTTPException(status_code=500, detail=f"internal server error: {str(e)}")


@router.post("/delete_best_in_months_task")
async def delete_best_in_months_task(data: BestInMonthsDeleteRequest,
                                     db: asyncpg.Connection = Depends(get_db_connection)):
    """
    Deletes a 'best in month' entry from the database for a specified year and month.

    This endpoint allows for the deletion of a specific entry in the `best_in_months` table
    based on the given year and month. The function checks if the year exists in the database
    and then proceeds to delete the entry for the given month. If the entry is not found, an
    appropriate error is returned.

    Args:
        data (BestInMonthsDeleteRequest): The request body containing the year and month
                                           for the entry to be deleted.
        db (asyncpg.Connection): A database connection dependency to interact with the database.

    Returns:
        dict: A success message indicating the entry was deleted successfully.

    Raises:
        HTTPException:
            - If the year is not found in the database, a 404 status code with the message "Year not found" is raised.
            - If no entry exists for the specified year and month, a 404 status code with the message "Entry not found" is raised.
            - If an internal error occurs during the deletion process, a 500 status code with a generic error message is raised.
    """
    try:
        year_row = await db.fetchrow("SELECT id FROM years WHERE year = $1", data.year)
        if not year_row:
            raise HTTPException(status_code=404, detail="Year not found")

        year_id = year_row["id"]

        delete_query = "DELETE FROM best_in_months WHERE year_id = $1 AND month = $2"
        result = await db.execute(delete_query, year_id, data.month)

        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Entry not found")

        return {"message": f"Entry for {data.month} {data.year} deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting best in months task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
