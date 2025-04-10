from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Request
from config.get_db_connection import get_db_connection
from fastapi.responses import FileResponse
from pydantic import BaseModel
import shutil
import os
import logging
from pathlib import Path
from pathlib import Path
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_FOLDER = Path(__file__).resolve().parent.parent.parent / "uploads" / "assets" / "lists_for_life" / "wishlist"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


class NewWishlistItem(BaseModel):
    title: str
    image_path: str


class UpdateWishlistItem(BaseModel):
    new_title: str
    old_title: str
    old_image_path: str
    new_image_path: str


@router.post("/upload_image")
async def upload_image(file: UploadFile = File(...)):
    """
    Upload an image file to the server's designated storage location.

    This endpoint accepts image file uploads and saves them to the server's upload directory.
    It prevents duplicate filenames and validates basic file properties.

    Args:
        file (UploadFile): The image file to upload, containing:
            - filename: Original name of the file
            - content_type: MIME type of the file
            - file: File content stream

    Returns:
        Dict[str, str]: A dictionary containing:
            - filename (str): The name of the successfully uploaded file

    Raises:
        HTTPException 400: If file already exists or is not an image
        HTTPException 413: If file exceeds size limits
        HTTPException 500: If upload fails due to server error
    """
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    if os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="File already exists")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file.filename}


@router.post("/add_wishlist_item")
async def add_wishlist_item(item: NewWishlistItem, db=Depends(get_db_connection)):
    """
    Add a new item to the wishlist with title and image path.

    This endpoint creates a new wishlist entry in the database, storing the item's
    title and normalized image path. The image path is converted to POSIX format
    for consistency across platforms.

    Args:
        item (NewWishlistItem): A Pydantic model containing:
            - title (str): The name/description of the wishlist item (required)
            - image_path (str): Path/URL to the item's image (required)
        db (asyncpg.Connection): Database connection dependency

    Returns:
        Dict[str, Union[str, int]]: A dictionary containing:
            - id (int): The database ID of the newly created item
            - message (str): Success confirmation message

    Raises:
        HTTPException 400: If required fields are missing or invalid
        HTTPException 500: If there's a database error during insertion
    """
    try:
        normalized_path = Path(item.image_path).as_posix()

        item_id = await db.fetchval(
            "INSERT INTO wishlist (title, image_path) VALUES ($1, $2) RETURNING id;",
            item.title,
            normalized_path
        )
        return {"id": item_id, "message": "Wishlist item added successfully"}
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        await db.close()


@router.get("/get_image/{image_filename}")
async def get_image(image_filename: str):
    """
    Retrieve an image file from the server's upload directory.

    This endpoint serves image files that were previously uploaded to the server.
    It performs security checks to prevent directory traversal attacks and
    validates the existence of the requested file.

    Args:
        image_filename (str): The name of the image file to retrieve (must be a
                            simple filename without path components)

    Returns:
        FileResponse: The requested image file with proper content-type headers

    Raises:
        HTTPException 400: If filename contains suspicious characters/paths
        HTTPException 404: If the image file doesn't exist
        HTTPException 415: If the file is not a supported image type
    """
    file_path = os.path.join(UPLOAD_FOLDER, image_filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(file_path)


@router.get("/get_wishlist_items")
async def get_wishlist_items(db=Depends(get_db_connection)):
    """
    Retrieve all items from the wishlist.

    This endpoint fetches the complete list of wishlist items including their titles
    and associated image paths. The data is returned as an array of items sorted
    by their creation order.

    Args:
        db (asyncpg.Connection): Database connection dependency

    Returns:
        List[Dict[str, str]]: A list of wishlist items, each containing:
            - title (str): The name/description of the wishlist item
            - image_path (str): Path/URL to the item's image

    Raises:
        HTTPException 500: If there's a database error during retrieval
    """
    try:
        query = "SELECT title, image_path FROM wishlist ORDER BY id;"

        rows = await db.fetch(query)

        wishlist_items = [{'title': row['title'], 'image_path': row['image_path']} for row in rows]

        return wishlist_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching wishlist items: {str(e)}")
    finally:
        await db.close()


@router.post("/remove_wishlist_item")
async def remove_wishlist_item(request: Request, db=Depends(get_db_connection)):
    """
    Remove a wishlist item and its associated image.

    This endpoint deletes a wishlist item from the database and optionally removes
    its associated image file from the server storage. The operation requires
    either the item title or image path for identification.

    Args:
        request (Request): The incoming request containing JSON payload with:
            - title (str): The title of the wishlist item to remove (optional)
            - image_path (str): The image path of the item to remove (optional)
        db (asyncpg.Connection): Database connection dependency

    Returns:
        Dict[str, str]: A dictionary with operation status:
            - message (str): Success confirmation message

    Raises:
        HTTPException 400: If neither title nor image_path is provided
        HTTPException 404: If specified item/image doesn't exist
        HTTPException 500: If there's a server error during deletion
    """
    try:
        task_data = await request.json()
        title = task_data.get("title")
        image_path = task_data.get("image_path")

        absolute_image_path = UPLOAD_FOLDER / Path(image_path).name

        if image_path and os.path.exists(absolute_image_path):
            os.remove(absolute_image_path)

        if title:
            await db.execute("DELETE FROM wishlist WHERE title = $1;", title)

        return {"message": "Task and image deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing task: {str(e)}")


@router.post("/update_wishlist_item")
async def update_wishlist_item(
        item: UpdateWishlistItem,
        db=Depends(get_db_connection)
):
    """
    Update an existing wishlist item's title and image path.

    This endpoint modifies a wishlist item's details, including optionally replacing
    its associated image file. The old image is automatically cleaned up if replaced.

    Args:
       item (UpdateWishlistItem): A Pydantic model containing:
           - old_title (str): Current title of the item to update (required)
           - new_title (str): New title for the item (required)
           - old_image_path (str): Current image path (required)
           - new_image_path (str): New image path (required)
       db (asyncpg.Connection): Database connection dependency

    Returns:
       Dict[str, str]: A dictionary with operation status:
           - message (str): Success confirmation message

    Raises:
       HTTPException 400: If required fields are missing
       HTTPException 404: If item to update doesn't exist
       HTTPException 500: If there's an error during update
    """
    default_image_path = item.new_image_path
    old_image_path = os.path.join(UPLOAD_FOLDER, os.path.basename(item.old_image_path))
    new_image_path = os.path.join(UPLOAD_FOLDER, os.path.basename(item.new_image_path))

    try:
        if old_image_path and os.path.exists(old_image_path) and old_image_path != new_image_path:
            try:
                os.remove(old_image_path)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error removing old image: {str(e)}")

        await db.execute("UPDATE wishlist SET title = $1, image_path = $2 WHERE title = $3", item.new_title,
                         default_image_path, item.old_title)

        return {"message": "Task updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")
