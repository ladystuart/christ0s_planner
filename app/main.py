from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import logging

from config.get_db_connection import create_tables
from src.courses import router as courses_router
from src.goals import router as goals_router
from src.wishlist import router as wishlist_router
from src.reading import router as reading_router
from src.yearly_plans import router as yearly_plans_router
from src.year_calendar import router as year_calendar_router
from src.yearly_plans_inner import router as yearly_plans_inner_router
from src.best_in_months import router as best_in_months_router
from src.gratitude_diary import router as gratitude_diary_router
from src.months import router as months_router
from src.review import router as review_router
from src.habit_tracker import router as habit_tracker_router
from src.work import router as work_router
from src.monthly_plans import router as monthly_plans_router
from src.month_popup import router as month_popup_router

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(goals_router)
app.include_router(courses_router)
app.include_router(wishlist_router)
app.include_router(reading_router)
app.include_router(yearly_plans_router)
app.include_router(year_calendar_router)
app.include_router(yearly_plans_inner_router)
app.include_router(best_in_months_router)
app.include_router(gratitude_diary_router)
app.include_router(months_router)
app.include_router(habit_tracker_router)
app.include_router(review_router)
app.include_router(work_router)
app.include_router(monthly_plans_router)
app.include_router(month_popup_router)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BANNERS_DIR = os.path.join(BASE_DIR, "../uploads/assets/lists_for_life/reading/banners")
ICONS_DIR = os.path.join(BASE_DIR, "../uploads/assets/lists_for_life/reading/icons")

ASSETS_FOLDER = "server/uploads/assets"

os.makedirs(ASSETS_FOLDER, exist_ok=True)

app.mount("/assets", StaticFiles(directory=ASSETS_FOLDER), name="assets")


async def get_image_names(directory):
    """
    Fetches the names of all files in the specified directory (excluding extensions) and returns them in sorted order.

    Args:
        directory (str): The path to the directory from which to fetch file names.

    Returns:
        list: A sorted list of file names (without extensions) found in the specified directory.

    Raises:
        HTTPException: If the directory does not exist, or if an error occurs while reading the directory.
    """
    if not os.path.exists(directory):
        logger.error(f"Directory not found: {directory}")
        raise HTTPException(status_code=404, detail=f"Directory not found: {directory}")

    try:
        files = [
            os.path.splitext(f)[0]
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        ]
        return sorted(files)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/banners")
async def get_banners():
    """
    Retrieves the names of all image files in the banners directory and returns them as a sorted list.

    Returns:
        dict: A dictionary containing the list of banner image names under the key "banners".
    """
    banners = await get_image_names(BANNERS_DIR)
    return {"banners": banners}


@app.get("/icons")
async def get_icons():
    """
    Retrieves the names of all image files in the icons directory and returns them as a sorted list.

    Returns:
        dict: A dictionary containing the list of icon image names under the key "icons".
    """
    icons = await get_image_names(ICONS_DIR)
    return {"icons": icons}


@app.get("/check_server_connection")
def home():
    """
    Returns a simple message indicating that the server is running.

    Returns:
        dict: A dictionary with a message confirming the server is running.
    """
    return {"message": "Server is running"}


@app.on_event("startup")
async def startup_event():
    """
    This function is executed when the FastAPI application starts up. It creates the necessary database tables
    if they do not already exist and logs the available routes in the application.

    Returns:
        None
    """
    await create_tables()
    logger.debug("Database tables are created if they did not exist.")

    logger.debug("Available routes:")
    for route in app.routes:
        logger.debug(route.path)


@app.exception_handler(404)
async def custom_404_handler(_, __):
    """
    Custom exception handler for 404 errors. This handler is triggered when a route is not found.
    It returns a JSON response with an error message.

    Args:
        _: The request object (not used here).
        __: The exception object (not used here).

    Returns:
        JSONResponse: A response with a 404 status code and a JSON error message.
    """
    return JSONResponse(status_code=404, content={"error": "Resource not found"})
