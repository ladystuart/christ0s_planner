import os
from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import List
from pathlib import Path
import shutil
import logging
from config.get_db_connection import get_db_connection

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

BOOK_UPLOAD_FOLDER = Path(
    __file__).resolve().parent.parent.parent / "uploads" / "assets" / "lists_for_life" / "reading" / "covers"
BOOK_UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

BOOK_DELETE_FOLDER = Path(__file__).resolve().parent.parent.parent / "uploads" / "assets"
BOOK_DELETE_FOLDER.mkdir(parents=True, exist_ok=True)

router = APIRouter()


class BookCreate(BaseModel):
    title: str
    authors: List[str]
    language: str
    status: str
    link: str
    series: str
    banner_path: str
    icon_path: str
    cover_path: str


class Book(BaseModel):
    title: str
    authors: List[str]
    language: str
    status: str
    link: str
    series: str
    banner_path: str
    icon_path: str
    cover_path: str

    class Config:
        from_attributes = True


class DeleteBook(BaseModel):
    title: str


class DeleteBookImage(BaseModel):
    cover_path: str


class BookUpdate(BaseModel):
    old_title: str
    title: str
    authors: List[str]
    language: str
    status: str
    link: str
    series: str
    banner_path: str
    icon_path: str
    cover_path: str


@router.get("/get_books", response_model=List[Book])
async def get_books():
    """
    Retrieve all books with their complete details from the reading list.

    This endpoint fetches the entire collection of books including their metadata,
    author information, and associated media paths. The data is formatted according
    to the Book model and includes all available book information in a single query.

    Returns:
        List[Book]: A list of Book objects containing:
            - title (str): The book's title
            - authors (List[str]): List of author names
            - language (str): Publication language
            - status (str): Reading status (e.g., "read", "unread", "in-progress")
            - link (str): URL to the book or related resource
            - series (str): Series name if applicable (empty string if none)
            - banner_path (str): Path/URL to the banner image
            - icon_path (str): Path/URL to the icon image
            - cover_path (str): Path/URL to the cover image

    Raises:
        HTTPException 500: If there's an unexpected server error
    """
    try:
        db = await get_db_connection()

        query = """
        SELECT r.id, r.title, r.language, r.status, r.link, r.series, r.banner_path, r.icon_path, r.cover_path,
               array_agg(a.name) AS authors
        FROM reading r
        LEFT JOIN reading_authors ra ON r.id = ra.reading_id
        LEFT JOIN authors a ON ra.author_id = a.id
        GROUP BY r.id;
        """

        result = await db.fetch(query)

        books = []
        for row in result:
            book = Book(
                title=row["title"],
                authors=row["authors"],
                language=row["language"],
                status=row["status"],
                link=row["link"],
                series=row["series"] or "",
                banner_path=row["banner_path"] or "",
                icon_path=row["icon_path"] or "",
                cover_path=row["cover_path"]
            )
            books.append(book)

        await db.close()
        return books

    except Exception as e:
        logger.error(f"Error fetching books: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/upload_book_image")
async def upload_image(file: UploadFile = File(...)):
    """
    Upload a book-related image file to the server.

    This endpoint accepts image uploads for book covers, banners, or icons,
    saving them to the designated book upload folder on the server.
    The uploaded file must have a unique filename within the destination folder.

    Args:
        file (UploadFile): The image file to upload, with metadata including:
            - filename: Original name of the file
            - content_type: MIME type of the file
            - file: Actual file content

    Returns:
        Dict[str, str]: A dictionary containing:
            - file_path (str): Server path where the file was saved

    Raises:
        HTTPException 400: If a file with the same name already exists
        HTTPException 413: If the file exceeds size limits
        HTTPException 415: If the file is not an allowed image type
        HTTPException 500: If there's an upload error
    """
    file_path = BOOK_UPLOAD_FOLDER / file.filename

    if file_path.exists():
        raise HTTPException(status_code=400, detail="File already exists")

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"file_path": str(file_path)}


@router.post("/add_book")
async def add_book(book: BookCreate):
    """
    Add a new book to the reading list with associated authors.

    This endpoint creates a new book entry and handles author relationships,
    creating new author records if they don't already exist. The book and author
    data will be available across all reading list views after creation.

    Args:
        book (BookCreate): A Pydantic model containing:
            - title (str): The book's title (required)
            - authors (List[str]): List of author names (minimum 1 required)
            - language (str): Publication language (e.g., "English")
            - status (str): Reading status ("unread", "in-progress", "read")
            - link (str): URL to book or related resource (optional)
            - series (str): Series name if applicable (optional)
            - banner_path (str): Path to banner image (optional)
            - icon_path (str): Path to icon image (optional)
            - cover_path (str): Path to cover image (optional)

    Returns:
        Dict[str, Union[str, int]]: A dictionary containing:
            - message (str): Success confirmation
            - book_id (int): The database ID of the created book

    Raises:
        HTTPException 400: If required fields are missing or invalid
        HTTPException 500: If there's a database error
    """
    try:
        db = await get_db_connection()

        author_ids = []
        for author_name in book.authors:
            author = await db.fetchrow("SELECT id FROM authors WHERE name = $1", author_name)
            if not author:
                result = await db.fetchrow("INSERT INTO authors(name) VALUES($1) RETURNING id", author_name)
                author_ids.append(result["id"])
            else:
                author_ids.append(author["id"])

        result = await db.fetchrow("""
            INSERT INTO reading(title, language, status, link, series, banner_path, icon_path, cover_path)
            VALUES($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
        """, book.title, book.language, book.status, book.link, book.series, book.banner_path, book.icon_path,
                                   book.cover_path)

        new_book_id = result["id"]

        for author_id in author_ids:
            await db.execute("INSERT INTO reading_authors(reading_id, author_id) VALUES($1, $2)", new_book_id,
                             author_id)

        await db.close()

        return {"message": "Book added successfully", "book_id": new_book_id}

    except Exception as e:
        logger.error(f"Error adding book: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/delete_book")
async def delete_book(book: DeleteBook):
    """
    Permanently delete a book and its author associations from the reading list.

    This endpoint removes a book entry and all its relationships from the database.
    The deletion is irreversible and will immediately remove the book from all views.

    Args:
        book (DeleteBook): A Pydantic model containing:
            - title (str): The exact title of the book to delete (case-sensitive)

    Returns:
        Dict[str, str]: A dictionary with operation status:
            - message (str): Success confirmation message

    Raises:
        HTTPException 404: If no book with the specified title exists
        HTTPException 500: If there's a database error during deletion
    """
    try:
        db = await get_db_connection()

        await db.execute("DELETE FROM reading WHERE title = $1", book.title)

        await db.execute("DELETE FROM reading_authors WHERE reading_id = (SELECT id FROM reading WHERE title = $1)",
                         book.title)

        await db.close()
        return {"message": "Book deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting book: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/delete_book_image")
async def delete_book_image(book: DeleteBookImage):
    """
    Delete a book's cover image from the server storage.

    This endpoint permanently removes a book cover image file from the server's
    designated book images folder. The operation only affects the image file and
    not the book record in the database.

    Args:
        book (DeleteBookImage): A Pydantic model containing:
            - cover_path (str): The relative path to the image file to delete
                              (e.g., "covers/book123.jpg")

    Returns:
        Dict[str, str]: A dictionary with operation status:
            - message (str): Success confirmation message

    Raises:
        HTTPException 404: If the specified image file does not exist
        HTTPException 403: If the file path attempts directory traversal
        HTTPException 500: If there's a filesystem error during deletion
    """
    try:
        cover_file_path = BOOK_DELETE_FOLDER / book.cover_path
        if cover_file_path.exists():
            os.remove(cover_file_path)
            return {"message": "Image deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Image not found")
    except Exception as e:
        logger.error(f"Error deleting image: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/update_books_info")
async def update_book_info(book: BookUpdate):
    """
    Update all information for an existing book in the reading list.

    This endpoint performs a comprehensive update of a book's metadata including:
    - Basic information (title, language, status)
    - Related links and series information
    - Image paths (cover, banner, icon)
    - Author associations (replaces existing authors)

    Args:
        book (BookUpdate): A Pydantic model containing:
            - old_title (str): Current title of the book to update (required)
            - title (str): New title (optional)
            - authors (List[str]): New list of authors (replaces existing)
            - language (str): Updated language
            - status (str): New reading status
            - link (str): Updated book link/URL
            - series (str): Updated series information
            - banner_path (str): New banner image path
            - icon_path (str): New icon image path
            - cover_path (str): New cover image path

    Returns:
        Dict[str, str]: A dictionary with operation status:
            - message (str): Success confirmation message

    Raises:
        HTTPException 404: If no book with the specified old_title exists
        HTTPException 400: If required fields are missing
        HTTPException 500: If there's a database error during update
    """
    try:
        db = await get_db_connection()

        existing_book = await db.fetchrow("SELECT id FROM reading WHERE title = $1", book.old_title)
        if not existing_book:
            raise HTTPException(status_code=404, detail="Book not found")

        book_id = existing_book["id"]

        await db.execute("""
            UPDATE reading
            SET title = $1, language = $2, status = $3, link = $4, series = $5, 
                banner_path = $6, icon_path = $7, cover_path = $8
            WHERE id = $9
        """, book.title, book.language, book.status, book.link, book.series,
                         book.banner_path, book.icon_path, book.cover_path, book_id)

        await db.execute("DELETE FROM reading_authors WHERE reading_id = $1", book_id)

        author_ids = []
        for author_name in book.authors:
            author = await db.fetchrow("SELECT id FROM authors WHERE name = $1", author_name)
            if not author:
                result = await db.fetchrow("INSERT INTO authors(name) VALUES($1) RETURNING id", author_name)
                author_ids.append(result["id"])
            else:
                author_ids.append(author["id"])

        for author_id in author_ids:
            await db.execute("INSERT INTO reading_authors(reading_id, author_id) VALUES($1, $2)", book_id, author_id)

        await db.close()

        return {"message": "Book updated successfully"}

    except Exception as e:
        logger.error(f"Error updating book: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
