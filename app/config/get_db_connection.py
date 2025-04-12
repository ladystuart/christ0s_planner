import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"


async def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database.

    This function uses the asyncpg library to connect to a PostgreSQL database
    using a connection string composed of environment variables (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME).
    It returns a connection object that can be used to interact with the database asynchronously.

    Returns:
        asyncpg.Connection: A connection object to interact with the PostgreSQL database.
    """
    return await asyncpg.connect(DATABASE_URL)


async def create_tables():
    """
    Creates the necessary tables in the PostgreSQL database if they do not already exist.

    This function connects to the database and creates a series of tables to structure the data for the application.
    These tables include information related to years, calendar events, yearly plans, habit tracking, gratitude diaries,
    reviews, monthly plans, and more. The tables are designed to handle various aspects of data related to the user's
    yearly activities, such as tracking goals, courses, books, work tasks, and blog content.

    Each table is created with appropriate relationships (foreign keys) to ensure data integrity across the different
    data categories.

    Tables created include:
        - years: Stores the years for reference.
        - calendar: Stores events related to a specific year.
        - yearly_plans: Stores tasks for each year and their completion status.
        - habit_tracker: Stores weekly habits with completion status.
        - gratitude_diary: Stores daily gratitude entries.
        - review: Stores review questions and answers for each year.
        - best_in_months: Stores images for the best moments of each month.
        - monthly_plans: Stores tasks for each month.
        - monthly_diary: Stores tasks and completion status for each day of the month.
        - task_colours: Stores color codes for tasks on specific days.
        - task_popups: Stores popup messages for tasks on specific days.
        - months: Stores month-related information such as name, icon, and reading link.
        - reading: Stores information about books being read.
        - authors: Stores author names.
        - reading_authors: Stores relationships between books and authors.
        - wishlist: Stores books or items on the user's wishlist.
        - goals: Stores the user's goals with completion status.
        - courses: Stores courses with completion status.
        - work: Stores work-related tasks.
        - work_place: Stores work notes related to specific tasks.

    Returns:
        None: This function does not return a value. It performs database table creation asynchronously.
    """
    conn = await get_db_connection()

    await conn.execute('''
    CREATE TABLE IF NOT EXISTS years (
       id SERIAL PRIMARY KEY,
       year INTEGER NOT NULL UNIQUE
    );
    ''')

    await conn.execute('''
    CREATE TABLE IF NOT EXISTS calendar (
       id SERIAL PRIMARY KEY,
       year_id INTEGER REFERENCES years(id) ON DELETE CASCADE,
       date DATE NOT NULL,
       event VARCHAR(255)
    );
    ''')

    await conn.execute('''
    CREATE TABLE IF NOT EXISTS yearly_plans (
       id SERIAL PRIMARY KEY,
       year_id INTEGER REFERENCES years(id) ON DELETE CASCADE,
       task VARCHAR(255) NOT NULL,
       completed BOOLEAN NOT NULL DEFAULT FALSE
    );
    ''')

    await conn.execute('''
    CREATE TABLE IF NOT EXISTS habit_tracker (
       id SERIAL PRIMARY KEY,
       year_id INTEGER REFERENCES years(id) ON DELETE CASCADE,
       week_starting DATE,
       day_of_week VARCHAR(9),
       task VARCHAR(255),
       completed BOOLEAN DEFAULT FALSE
    );
    ''')

    await conn.execute('''
    CREATE TABLE IF NOT EXISTS gratitude_diary (
       id SERIAL PRIMARY KEY,
       year_id INTEGER REFERENCES years(id) ON DELETE CASCADE,
       entry_date DATE,
       content TEXT
    );
    ''')

    await conn.execute('''
    CREATE TABLE IF NOT EXISTS review (
       id SERIAL PRIMARY KEY,
       year_id INTEGER REFERENCES years(id) ON DELETE CASCADE,
       question VARCHAR(255),
       answer TEXT
    );
    ''')

    await conn.execute('''
    CREATE TABLE IF NOT EXISTS best_in_months (
       id SERIAL PRIMARY KEY,
       year_id INTEGER REFERENCES years(id) ON DELETE CASCADE,
       month VARCHAR(20), 
       image_path TEXT
    );
    ''')

    await conn.execute('''
    CREATE TABLE IF NOT EXISTS monthly_plans (
       id SERIAL PRIMARY KEY,
       year_id INTEGER REFERENCES years(id) ON DELETE CASCADE,
       month VARCHAR(20),     
       task TEXT,        
       completed BOOLEAN DEFAULT FALSE
    );
    ''')

    await conn.execute('''
    CREATE TABLE IF NOT EXISTS monthly_diary (
       id SERIAL PRIMARY KEY,
       year_id INTEGER REFERENCES years(id) ON DELETE CASCADE,
       month VARCHAR(20),       
       date DATE NOT NULL,       
       task TEXT,            
       completed BOOLEAN DEFAULT FALSE
    );
    ''')

    await conn.execute('''
    CREATE TABLE IF NOT EXISTS task_colours (
       id SERIAL PRIMARY KEY,
       year_id INTEGER REFERENCES years(id) ON DELETE CASCADE,
       month VARCHAR(20),
       date DATE NOT NULL,  
       colour_code VARCHAR(7)
    );
    ''')

    await conn.execute('''
    CREATE TABLE IF NOT EXISTS task_popups (
       id SERIAL PRIMARY KEY,
       year_id INTEGER REFERENCES years(id) ON DELETE CASCADE,
       month VARCHAR(20),    
       date DATE NOT NULL,      
       popup_message TEXT
    );
    ''')

    await conn.execute('''
    CREATE TABLE IF NOT EXISTS months (
       id SERIAL PRIMARY KEY,
       year_id INTEGER REFERENCES years(id) ON DELETE CASCADE,
       month_name VARCHAR(20) NOT NULL,
       icon_path VARCHAR(255),
       banner VARCHAR(255),
       reading_link VARCHAR(255),
       month_icon_path VARCHAR(255)
    );
    ''')

    await conn.execute(''' 
    CREATE TABLE IF NOT EXISTS reading (
       id SERIAL PRIMARY KEY,
       title VARCHAR(255) NOT NULL,
       language VARCHAR(100),
       status VARCHAR(50),
       link VARCHAR(255),
       series VARCHAR(255),
       banner_path VARCHAR(255),
       icon_path VARCHAR(255),
       cover_path VARCHAR(255)
    );
    ''')

    await conn.execute(''' 
    CREATE TABLE IF NOT EXISTS authors (
       id SERIAL PRIMARY KEY,
       name VARCHAR(255) NOT NULL
    );
    ''')

    await conn.execute(''' 
    CREATE TABLE IF NOT EXISTS reading_authors (
       reading_id INTEGER REFERENCES reading(id) ON DELETE CASCADE,
       author_id INTEGER REFERENCES authors(id) ON DELETE CASCADE,
       PRIMARY KEY (reading_id, author_id)
    );
    ''')

    await conn.execute(''' 
    CREATE TABLE IF NOT EXISTS wishlist (
       id SERIAL PRIMARY KEY,
       title TEXT NOT NULL,
       image_path TEXT NOT NULL
    );
    ''')

    await conn.execute(''' 
    CREATE TABLE IF NOT EXISTS goals (
       id SERIAL PRIMARY KEY,
       title VARCHAR(255) NOT NULL,
       completed BOOLEAN NOT NULL DEFAULT FALSE
    );
    ''')

    await conn.execute(''' 
    CREATE TABLE IF NOT EXISTS courses (
       id SERIAL PRIMARY KEY,
       title VARCHAR(225) NOT NULL,
       completed BOOLEAN NOT NULL DEFAULT FALSE
    );
    ''')

    await conn.execute(''' 
    CREATE TABLE IF NOT EXISTS work (
       id SERIAL PRIMARY KEY, 
       work_name VARCHAR(255) NOT NULL 
    );
    ''')

    await conn.execute(''' 
    CREATE TABLE IF NOT EXISTS work_place (
       id SERIAL PRIMARY KEY,
       work_id INTEGER REFERENCES work(id) ON DELETE CASCADE,  
       note_text TEXT,  
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
    );
    ''')

    await conn.close()
