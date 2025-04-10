from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from config.get_db_connection import get_db_connection

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter()


class WorkPlace(BaseModel):
    work_name: str


class UpdateWorkPlace(BaseModel):
    new_work_name: str
    old_work_name: str


class WorkNote(BaseModel):
    work_name: str
    note_text: str


class EditWorkNote(BaseModel):
    work_name: str
    new_text: str
    old_text: str


@router.post("/add_work_place")
async def add_work_place(workplace: WorkPlace):
    """
    Adds a new workplace to the database.

    This endpoint inserts a new workplace entry into the `work` table and
    returns the created record. If the insertion fails, it raises an HTTP 400 error.
    On unexpected errors, it raises an HTTP 500 error.

    Args:
        workplace (WorkPlace): A pydantic model containing the name of the workplace to be added.

    Returns:
        dict: A dictionary with the ID and name of the newly created workplace.

    Raises:
        HTTPException: If the insertion fails or an internal error occurs.
    """
    connection = None
    try:
        connection = await get_db_connection()

        query = """
        INSERT INTO work (work_name)
        VALUES ($1)
        RETURNING id, work_name;
        """
        result = await connection.fetchrow(query, workplace.work_name)

        if not result:
            raise HTTPException(status_code=400, detail="Failed to add work place")

    except Exception as e:
        logger.error(f"Error adding work place: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    finally:
        if connection:
            await connection.close()


@router.get("/get_work_place")
async def get_work_places():
    """
    Retrieves all workplace names from the database.

    This endpoint fetches all records from the `work` table and returns a list of
    workplace names as buttons. If there are no workplaces, it returns an empty list.

    Returns:
        dict: A dictionary containing a list of workplace names under the key "buttons".

    Raises:
        HTTPException: If an internal server error occurs during the database operation.
    """
    connection = None
    try:
        connection = await get_db_connection()

        query = "SELECT work_name FROM work ORDER BY id"
        result = await connection.fetch(query)

        work_places = [row["work_name"] for row in result]

        if not work_places:
            return {"buttons": []}

        return {"buttons": work_places}

    except Exception as e:
        logger.error(f"Error fetching work places: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    finally:
        if connection:
            await connection.close()


@router.post("/delete_work_place")
async def delete_work_place(workplace: WorkPlace):
    """
    Deletes a workplace from the database.

    This endpoint deletes a workplace from the `work` table based on the provided
    workplace name. If the workplace does not exist, it raises a 404 error.

    Args:
        workplace (WorkPlace): A pydantic model containing the name of the workplace to be deleted.

    Returns:
        dict: A success message indicating the workplace was deleted.

    Raises:
        HTTPException: If the workplace is not found or an internal server error occurs.
    """
    connection = None
    try:
        connection = await get_db_connection()

        query = "DELETE FROM work WHERE work_name = $1 RETURNING work_name;"
        result = await connection.fetchrow(query, workplace.work_name)

        if not result:
            raise HTTPException(status_code=404, detail=f"Work place '{workplace.work_name}' not found")

        return {"message": f"Work place '{workplace.work_name}' deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting work place: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    finally:
        if connection:
            await connection.close()


@router.post("/update_work_place_title")
async def update_work_place_title(workplace: UpdateWorkPlace):
    """
    Updates the name of an existing workplace in the database.

    This endpoint updates the `work_name` of a workplace in the `work` table,
    based on the provided old and new names. If the workplace with the old name
    does not exist, it raises a 404 error.

    Args:
        workplace (UpdateWorkPlace): A pydantic model containing the old and new workplace names.

    Returns:
        dict: A success message indicating the workplace was updated.

    Raises:
        HTTPException: If the workplace is not found or an internal server error occurs.
    """
    connection = None
    try:
        connection = await get_db_connection()

        query = """
        UPDATE work
        SET work_name = $1
        WHERE work_name = $2
        RETURNING id, work_name;
        """
        result = await connection.fetchrow(query, workplace.new_work_name, workplace.old_work_name)

        if not result:
            raise HTTPException(status_code=404, detail=f"Work place '{workplace.old_work_name}' not found")

        return {"message": f"Work place '{workplace.old_work_name}' updated successfully"}

    except Exception as e:
        logger.error(f"Error updating work place title: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    finally:
        if connection:
            await connection.close()


@router.post("/add_work_note")
async def add_work_note(work_note: WorkNote):
    """
    Adds a note to a specific workplace in the database.

    This endpoint first verifies that the given workplace exists by name,
    then inserts a note associated with that workplace into the `work_place` table.
    If the workplace is not found or the insertion fails, appropriate HTTP errors are raised.

    Args:
        work_note (WorkNote): A pydantic model containing the name of the workplace and the note text.

    Returns:
        dict: A message indicating success and the ID of the newly created note.

    Raises:
        HTTPException: If the workplace is not found, the note could not be added,
                       or an internal server error occurs.
    """
    connection = None
    try:
        connection = await get_db_connection()

        query = "SELECT id FROM work WHERE work_name = $1"
        work_record = await connection.fetchrow(query, work_note.work_name)

        if not work_record:
            raise HTTPException(status_code=404, detail=f"Work place '{work_note.work_name}' not found")

        work_id = work_record["id"]

        query = """
        INSERT INTO work_place (work_id, note_text)
        VALUES ($1, $2)
        RETURNING id;
        """
        result = await connection.fetchrow(query, work_id, work_note.note_text)

        if not result:
            raise HTTPException(status_code=400, detail="Failed to add note")

        return {"message": "Note added successfully", "note_id": result["id"]}

    except Exception as e:
        logger.error(f"Error adding note: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    finally:
        if connection:
            await connection.close()


@router.get("/get_work_place_notes")
async def get_work_place_notes(work_name: str):
    """
    Retrieves all notes associated with a specific workplace.

    This endpoint looks up the workplace by its name, then fetches all related notes
    from the `work_place` table, ordered by creation time in descending order.

    Args:
        work_name (str): The name of the workplace for which to retrieve notes.

    Returns:
        dict: A dictionary containing a list of notes with their text and creation timestamp.

    Raises:
        HTTPException:
            - 404 if the specified workplace is not found.
            - 500 if an internal server error occurs.
    """
    connection = None
    try:
        connection = await get_db_connection()

        query = "SELECT id FROM work WHERE work_name = $1"
        work_record = await connection.fetchrow(query, work_name)

        if not work_record:
            raise HTTPException(status_code=404, detail=f"Work place '{work_name}' not found")

        work_id = work_record["id"]

        query = "SELECT note_text, created_at FROM work_place WHERE work_id = $1 ORDER BY created_at DESC"
        notes = await connection.fetch(query, work_id)

        return {"notes": [{"text": note["note_text"], "created_at": note["created_at"]} for note in notes]}

    except Exception as e:
        logger.error(f"Error fetching notes: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    finally:
        if connection:
            await connection.close()


@router.post("/delete_work_place_note")
async def delete_work_place_note(work_note: WorkNote):
    """
    Deletes a specific note associated with a workplace.

    This endpoint first verifies the existence of the specified workplace by name.
    If the workplace exists, it attempts to delete a note matching the provided text
    from the `work_place` table. If the note is not found, a 404 error is returned.

    Args:
        work_note (WorkNote): A pydantic model containing the workplace name and note text to be deleted.

    Returns:
        dict: A message confirming that the note was successfully deleted.

    Raises:
        HTTPException:
            - 404 if the workplace or note is not found.
            - 500 if an internal server error occurs.
    """
    connection = None
    try:
        connection = await get_db_connection()

        query = "SELECT id FROM work WHERE work_name = $1"
        work_record = await connection.fetchrow(query, work_note.work_name)

        if not work_record:
            raise HTTPException(status_code=404, detail=f"Work place '{work_note.work_name}' not found.")

        work_id = work_record["id"]

        query = "DELETE FROM work_place WHERE work_id = $1 AND note_text = $2 RETURNING id"
        result = await connection.fetchrow(query, work_id, work_note.note_text)

        if not result:
            raise HTTPException(status_code=404, detail="Note not found.")

        return {"message": "Work note deleted."}

    except Exception as e:
        logger.error(f"Note deletion error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")

    finally:
        if connection:
            await connection.close()


@router.post("/edit_work_place_note")
async def edit_work_place_note(note: EditWorkNote):
    """
    Updates the text of an existing note for a specific workplace.

    This endpoint locates a note by its current text and associated workplace name,
    then updates its content to the new text provided. If the note or workplace does not exist,
    or the update fails, a 404 error is returned.

    Args:
        note (EditWorkNote): A pydantic model containing the workplace name,
                             the old note text, and the new note text.

    Returns:
        dict: A message confirming that the note was successfully updated.

    Raises:
        HTTPException:
            - 404 if the note or workplace is not found, or the update failed.
            - 500 if an internal server error occurs.
    """
    connection = None
    try:
        connection = await get_db_connection()

        query = """
        UPDATE work_place
        SET note_text = $1
        WHERE note_text = $2
        AND work_id = (SELECT id FROM work WHERE work_name = $3)
        RETURNING id;
        """
        result = await connection.fetchrow(query, note.new_text, note.old_text, note.work_name)

        if not result:
            raise HTTPException(status_code=404, detail="Note not found or update failed.")

        return {"message": "Note updated successfully"}

    except Exception as e:
        logger.error(f"Error updating note: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    finally:
        if connection:
            await connection.close()
