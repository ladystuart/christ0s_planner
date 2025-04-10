### Enter your ip address here!
SERVER_URL = "https://YOUR-IP:8443"

SSL_ENABLED = False
VERIFY_ENABLED = False

# App settings
APP = {
    'title': "Christ0$",  # Title
    'geometry': "950x550",  # Geometry
    'icon_path': "./app_icon.ico",  # Path to app icon
    'welcome_text': "Welcome back!",
    'welcome_text_font': ("Arial", 24)
}

# Side panel settings
SIDE_PANEL = {
    'bg_color': "#2F343F",  # Color
    'width': 150,  # Width
    'font': ("Arial", 9),  # Font
    'connection_status_font': ("Arial", 13, "bold"),
    'connection_failed_color': "red",
    'connection_successful_color': "green",
}

# Interface data
INTERFACE = {
    'bg_color': "#F0F0F0",  # Color
    'button_bg_color': "#F0F0F0",  # Side panel buttons color
    'separator': '#000000',  # Separator
    'source_label_font': ("Arial", 12),  # Source label font
    'page_title_font': ("Arial", 20, "bold"),  # Title font
    'headers_font': ("Arial", 15, "bold"),  # Headers font
    'text_color': "black",
    'icon_dimensions': 30,
    'source_icon_dimensions': 20,
    'text_label_font': ("Arial", 12)
}

BANNER_PATHS = {
    'useful_links': "useful_links/banner.png",
    'lists_for_life': "lists_for_life/banner.png",
    'reading': "lists_for_life/reading/banner.png",
    'wishlist': "lists_for_life/wishlist/banner.png",
    'goals': "lists_for_life/goals/banner.png",
    'courses': "lists_for_life/courses/banner.png",
    'yearly_plans': "yearly_plans/banner.png",
    'calendar': "yearly_plans/year/calendar_banner.png",
    'yearly_plans_inner': "yearly_plans/year/yearly_plans_banner.png",
    'gratitude_diary': "yearly_plans/year/gratitude_diary_banner.png",
    'review': "yearly_plans/year/review_banner.png",
    'months': "yearly_plans/year/months_banner.png",
    'work': "work/banner.png",
    'work_place': "work/banner.png"
}

PAGES_NAMES = {
    'useful_links': "Useful links",
    'lists_for_life': "#Lists_for_life",
    'reading': "Reading",
    'wishlist': "Wishlist",
    'goals': "Goals",
    'courses': "Courses",
    'yearly_plans': "Yearly plans",
    'calendar': "Calendar",
    'yearly_plans_inner': "Yearly plans",
    'habit_tracker': "Habit tracker",
    'gratitude_diary': "Gratitude diary",
    'best_in_months': "Best in months",
    'months': "Months",
    'review': "Review",
    'work': "Work"
}

ICONS_PATHS = {
    'useful_links': "useful_links/icon.png",
    'lists_for_life': "lists_for_life/icon.png",
    'reading': "lists_for_life/reading/reading.png",
    'wishlist': "lists_for_life/wishlist/wishlist.png",
    'goals': "lists_for_life/goals/goals.png",
    'courses': "lists_for_life/courses/courses.png",
    'yearly_plans': "yearly_plans/icon.png",
    'year': "yearly_plans/year/year_icon.png",
    'calendar': "yearly_plans/year/calendar_icon.png",
    'yearly_plans_inner': "yearly_plans/year/yearly_plans_icon.png",
    'habit_tracker': "yearly_plans/year/habit_tracker_icon.png",
    'gratitude_diary': "yearly_plans/year/gratitude_diary_icon.png",
    'best_in_months': "yearly_plans/year/best_in_months_icon.png",
    'months': "yearly_plans/year/months_icon.png",
    'review': "yearly_plans/year/review_icon.png",
    'work': "work/icon.png",
    'work_place': "work/work_button_icon.png"
}

TOOLTIP = {
    'font': ("Arial", 9),
    'bg_color': "lightyellow",
    'relief': "solid"
}

# JSON data path
DATA_PATHS = {
    'tabs': "./data/tabs.json",
    'useful_links': "./data/useful_links.json",
    'lists_for_life': "./data/lists_for_life.json"
}

USEFUL_LINKS = {
    'title_icon_dimensions': 32,
    'table_head_bg_color': "#87CEEB",
    'table_font_bold': ("Arial", 11, "bold"),
    'table_font': ("Arial", 11),
    'table_bg_first': "#F0F0F0",
    'table_bg_second': "#D3D3D3",
    'description_font_bold': ("Arial", 13, "bold"),
    'description_label': ("Arial", 13),
    'link_font': ("Arial", 13),
    'link_color': 'blue'
}

LISTS_FOR_LIFE = {
    'button_font': ("Arial", 12, "bold")
}

READING = {
    'image_link': "lists_for_life/reading/book.png",
    'quote_wraplength': 400,
    'book_banner_path': "lists_for_life/reading/banners",
    'book_icon_path': "lists_for_life/reading/icons",
    'base_folder': "lists_for_life/reading/covers",
    'add_button_color': "#90EE90",
    'not_started_label_color': "#E3E2E0",
    'in_progress_label_color': "#D3E5EF",
    'done_label_color': "#DBEDDB",
    'load_more_button_color': "#ADD8E6",
    'add_window_lines_color': "#D3D3D3",
    'default_label_color': "#D3D3D3",
    'button_font': ("Arial", 12),
    'filter_font': ("Arial", 12),
    'columns_titles_font': ("Arial", 14, "bold"),
    'toplevel_windows_font': ("Arial", 12),
    'books_info_title_font': ("Arial", 14, "bold"),
    'books_info_font': ("Arial", 12),
    'quote_font': ("Arial", 12, "italic"),
    'book_title_wraplength': 500,
    'quote_text': "\"Of all things, I liked books best.\"\n― Nikola Tesla",
    'delete_button_color': "#FFA07A",
    'cover_width': 100,
    'cover_height': 150
}

WISHLIST = {
    'add_button_color': "#90EE90",
    'add_button_font': ("Arial", 12),
    'dist_folder_path': "lists_for_life/wishlist",
    'toplevel_windows_font': ("Arial", 12),
    'browse_button_font': ("Arial", 12),
    'save_button_font': ("Arial", 12),
    'wishlist_item_font': ("Arial", 12),
    'delete_button_color': "#FFA07A",
    'delete_edit_button_font': ("Arial", 12),
    'image_height': 50,
    'image_width': 50,
}

GOALS = {
    'toplevel_windows_font': ("Arial", 12),
    'save_button_font': ("Arial", 12),
    'goal_entry_font': ("Arial", 12),
    'add_button_font': ("Arial", 12),
    'add_button_color': "#90EE90",
    'quote_text': "You're familiar with the phrase\n \"Man's reach exceeds his grasp\"?\nIt's a lie. \""
                  "Man's grasp exceeds his nerve\". \n— Nikola Tesla",
    'image_link': "lists_for_life/goals/stairs.png",
    'quote_wraplength': 400,
    'quote_font': ("Arial", 12, "italic"),
    'goals_font': ("Arial", 12),
    'delete_edit_button_font': ("Arial", 11),
    'delete_button_color': "#FFA07A"
}

COURSES = {
    'toplevel_windows_font': ("Arial", 12),
    'save_button_font': ("Arial", 12),
    'course_entry_font': ("Arial", 12),
    'add_button_font': ("Arial", 12),
    'quote_text': "\"Somewhere, something incredible is waiting to be known.\" \n― Carl Sagan",
    'image_link': "lists_for_life/courses/forest.png",
    'quote_wraplength': 500,
    'quote_font': ("Arial", 12, "italic"),
    'courses_font': ("Arial", 12),
    'delete_edit_button_font': ("Arial", 11),
    'delete_button_color': "#FFA07A",
    'add_button_color': "#90EE90",
}

YEARLY_PLANS = {
    'menu_font': ("Arial", 9),
    'save_button_font': ("Arial", 12),
    'cancel_button_font': ("Arial", 12),
    'toplevel_windows_font': ("Arial", 12),
    'year_buttons_font': ("Arial", 12),
    'pin_label_bg': "#E0E0D8",
    'pin_icon_path': "yearly_plans/pin_icon.png",
    'smile_icon_path': "yearly_plans/cool_face_icon.png",
    'pin_frame_font': ("Arial", 12),
    'pin_frame_text_color': "#333333",
    'add_button_color': "#90EE90",
    'add_button_font': ("Arial", 12),
    'image_link': "yearly_plans/library.png",
    'quote_text': "\"Maybe next year for my Nobel Prize?\"\n― Steven Magee",
    'quote_font': ("Arial", 12, "italic"),
    'quote_wraplength': 400
}

YEAR = {
    'image_link': "yearly_plans/year/rose.png",
    'quote_text': "\"You have the freedom to be yourself, your true self, here and now, "
                  "and nothing can stand in your way."
                  "\"\n― Richard Bach, Jonathan Livingston Seagull",
    'quote_font': ("Arial", 12, "italic"),
    'quote_wraplength': 300,
    'buttons_font': ("Arial", 12),
    'title_text_font': ("Arial", 20, "bold")
}

CALENDAR = {
    'buttons_font': ("Arial", 12),
    'add_button_bg': "#90EE90",
    'delete_button_color': "#FFA07A",
    'toplevel_windows_font': ("Arial", 12),
    'calendar_selected_task_bg': "#FFCCCC",
    'calendar_selected_task_text': "black"
}

YEARLY_PLANS_INNER = {
    'toplevel_windows_font': ("Arial", 12),
    'buttons_font': ("Arial", 12),
    'add_button_color': "#90EE90",
    'tasks_font': ("Arial", 12),
    'entry_font': ("Arial", 12),
    'delete_button_color': "#FFA07A",
}

HABIT_TRACKER = {
    'toplevel_windows_font': ("Arial", 12),
    'buttons_font': ("Arial", 12),
    'toplevel_windows_title_font': ("Arial", 14, "bold"),
    'toplevel_windows_font_color': "#333333",
    'entry_bg_color': "#FFFFFF",
    'left_frame_bg': "#E0E0D8",
    'image_link': "yearly_plans/year/plane.png",
    'quote_text': "\"Heaven is not a place, and it's not a time. Heaven is being perfect.\"\n"
                  "― Richard Bach, Jonathan Livingston Seagull",
    'quote_font': ("Arial", 12, "italic"),
    'quote_wraplength': 300,
    'habit_tracker_frame_bg': "#F5F5F0",
    'week_starting_label_font': ("Arial", 15, "bold"),
    'week_starting_label_bg': "#F5F5F0",
    'week_starting_font_color': "#333333",
    'week_starting_label_relief': "ridge",
    'day_frame_bg': "#F5F5F0",
    'day_label_title_font': ("Arial", 14, "bold"),
    'day_label_bg': "#F5F5F0",
    'day_label_font_color': "#333333",
    'checkbox_font': ("Arial", 12),
    'page_title_font': ("Arial", 20, "bold")
}

GRATITUDE_DIARY = {
    'toplevel_windows_font': ("Arial", 12),
    'buttons_font': ("Arial", 12),
    'add_button_color': "#90EE90",
    'tasks_font': ("Arial", 12),
    'entry_font': ("Arial", 12),
    'months_label_font': ("Arial", 14, "bold")
}

BEST_IN_MONTHS = {
    'months_font': ("Arial", 14, "bold"),
    'buttons_font': ("Arial", 12),
    'image_width': 150,
    'image_height': 100,
    'page_title_font': ("Arial", 20, "bold"),
    'upload_button_color': "#90EE90",
    'delete_button_color': "#FFA07A",
    'base_folder': "yearly_plans/year",
}

REVIEW = {
    '1. How would you describe this year with a single word?': "#DFFFD6",
    '2. What is your biggest challenge this year?': "#D6F4FF",
    '3. One thing you are most proud of this year:': "#FFD6E5",
    '4. How did you take care of yourself this year?': "#FFD6D6",
    '5. How have you changed over the year': "#FFE6CC",
    '6. New things you learned:': "#FFFFCC",
    '7. What made this year special?': "#EBD6C5",
    '8. What are you most grateful for?': "#E6D6FF",
    '9. Top 3 priorities for the next year:': "#E0E0E0",
    '10. Did you do your best?': "#F2F2F2",
    'question_label_text_color': "black",
    'question_label_text_font': ("Arial", 12, "bold"),
    'entry_text_font': ("Arial", 12),
    'button_text_font': ("Arial", 12),
    'button_color': "#90EE90",
}

MONTHS = {
    'not_started_icon_path': "yearly_plans/year/not_started_icon.png",
    'in_progress_icon': "yearly_plans/year/in_progress_icon.png",
    'done_icon': "yearly_plans/year/done_icon.png",
    'buttons_font': ("Arial", 12),
    'image_link': "yearly_plans/year/lion.png",
    'quote_text': "\"The wisest men follow their own direction.\"\n― Euripides",
    'quote_font': ("Arial", 12, "italic"),
    'quote_wraplength': 350,
}

MONTHLY_PLANS = {
    'selected_date_color': "#FFCCCC",
    'toplevel_windows_font': ("Arial", 12),
    'popup_window_font': ("Arial", 12),
    'entry_bg_color': "#FFFFFF",
    'window_font': ("Arial", 12),
    'add_button_color': "#90EE90",
    'buttons_font': ("Arial", 12),
    'title_icon_dimensions': 32,
    'diary_title': "Diary",
    'diary_icon_path': "yearly_plans/year/diary_icon.png",
    'reading_title': "Reading",
    'reading_icon_path': "yearly_plans/year/book_icon.png",
    'calendar_title': "Calendar",
    'calendar_icon_path': "yearly_plans/year/calendar_icon.png",
    'calendar_font': ("Arial", 8),
    'calendar_selected_color': "#FFCCCC",
    'calendar_selected_text_color': "black",
    'goals_title': "Goals",
    'goals_icon_path': "yearly_plans/year/goals_icon.png",
    'error_label_font': ("Arial", 10),
    'reading_label_bg': "#90EE90",
    'reading_highlightbackground': "#90EE90",
    'reading_relief': "solid",
    'reading_highlightcolor': "#90EE90",
    'reading_label_font': ("Arial", 12)
}

WORK = {
    'buttons_font': ("Arial", 12),
    'add_button_color': "#90EE90",
    'add_button_relief': "raised",
    'toplevel_windows_font': ("Arial", 12),
    'buttons_relief': "raised"
}

WORK_PLACE = {
    'text_font': ("Arial", 12),
    'text_bg_color': "#FFFFFF",
    'buttons_font': ("Arial", 12),
    'add_button_color': "#90EE90",
    'save_button_color': "#90EE90",
    'delete_button_color': "#FFA07A"
}
