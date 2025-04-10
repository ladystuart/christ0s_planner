from config.imports import *
from config.settings import MONTHLY_PLANS
from config.utils import add_icon_image, load_icon_image
from datetime import datetime
from tkcalendar import Calendar as TkCalendar
import calendar as cal
from config.tooltip import ToolTip


def add_popup(widget, popup_text):
    """
    Adds a popup tooltip that displays when the user hovers over the given widget.
    The popup shows the provided text and disappears when the mouse leaves the widget.

    :param widget: The Tkinter widget to which the popup will be attached.
    :param popup_text: The text to display in the popup when the user hovers over the widget.
    :return: None
    """
    popup_window = None

    def show_popup(event):
        """
        Creates and displays the popup window near the mouse cursor.

        :param event: The mouse event that triggered the function (provides mouse position).
        :return: None
        """
        nonlocal popup_window
        if popup_window:
            return

        popup_window = tk.Toplevel(widget)
        popup_window.title("Popup")
        popup_window.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
        popup_window.resizable(False, False)

        popup_window.wm_iconbitmap(APP['icon_path'])

        label = tk.Label(
            popup_window,
            text=popup_text,
            bg=INTERFACE['bg_color'],
            font=MONTHLY_PLANS['popup_window_font'],
            wraplength=300
        )
        label.pack(padx=10, pady=10)

    def hide_popup(event):
        """
        Closes the popup window when the user moves the mouse away from the widget.

        :param event: The mouse event that triggered the function.
        :return: None
        """
        nonlocal popup_window
        if popup_window:
            popup_window.destroy()
            popup_window = None

    def bind_popup_recursive(widget):
        """
        Binds the show and hide events for the popup to the widget and all of its child widgets.

        :param widget: The widget to bind the events to.
        :return: None
        """
        widget.bind("<Enter>", show_popup)
        widget.bind("<Leave>", hide_popup)
        for child in widget.winfo_children():
            bind_popup_recursive(child)

    bind_popup_recursive(widget)


def add_line_under_title(parent_frame, row, column, width):
    """
    Adds a horizontal line under a title in the specified grid position.

    This function creates a thin horizontal line (using a `tk.Canvas` widget) and places
    it in the specified position in the given parent frame's grid. The line is drawn
    with a specified width, and is typically used as a separator under a title or section.

    :param parent_frame: The frame (container) where the line will be added.
                          This is the parent widget in which the line is placed.
    :param row: The row in the grid where the line will be placed.
    :param column: The column in the grid where the line will be placed.
    :param width: The width of the line in pixels. It defines how long the line will be.
    :return: None
    """
    line = tk.Canvas(parent_frame, height=1, width=width, bg=INTERFACE['separator'], bd=0, highlightthickness=0)
    line.grid(row=row, column=column, pady=5)


def create_icon_label(frame, icon_path, icon_size=(20, 20), bg_color=INTERFACE['bg_color']):
    """
    Creates a label with an icon and adds it to a given frame.

    This function loads an icon from the specified path, resizes it according to the given size,
    and creates a label with the icon that is placed in the provided frame. The label is
    positioned to the left of any other widgets in the frame (if any). If there is an error
    loading the image, it will be caught and logged.

    :param frame: The frame where the icon label will be placed. This is the parent widget
                  that holds the icon label.
    :param icon_path: The path to the image file of the icon. This file is expected to be
                      in a format supported by PIL (e.g., PNG, JPG).
    :param icon_size: The size of the icon as a tuple (width, height). The default is (20, 20).
                      The icon will be resized to fit these dimensions.
    :param bg_color: The background color of the label. It defaults to the value defined in
                     `INTERFACE['bg_color']`.

    :return: None. This function creates and adds a label to the frame but does not return
             any value.
    """
    try:
        icon_photo = asyncio.run(load_icon_image(SERVER_URL, icon_path, VERIFY_ENABLED))

        icon_label = tk.Label(frame, image=icon_photo, bg=bg_color)
        icon_label.image = icon_photo
        icon_label.pack(side="left")

    except requests.exceptions.RequestException as e:
        print(f"Error loading icon from URL: {e}")
    except Exception as e:
        print(f"Error processing the icon: {e}")


def create_text_label(frame, text, font=MONTHLY_PLANS['window_font'], bg_color=INTERFACE['bg_color']):
    """
    Creates a label with the specified text and adds it to a given frame.

    This function creates a label widget with the provided text, font, and background color.
    The label is then placed in the given frame and aligned to the left side with some padding.

    :param frame: The parent frame (or container) where the label will be placed. This is the
                  widget that holds the text label.
    :param text: The text to be displayed in the label. This is the content of the label.
    :param font: The font style of the label text. The default is the font specified in
                 `MONTHLY_PLANS['window_font']`.
    :param bg_color: The background color of the label. The default is taken from
                     `INTERFACE['bg_color']`.

    :return: None. This function creates and adds a label to the frame but does not return
             any value.
    """
    source_label = tk.Label(frame, text=text, font=font, bg=bg_color)
    source_label.pack(side="left", padx=(5, 0))


def create_clickable_text(frame, text, font=MONTHLY_PLANS['window_font'], bg_color=INTERFACE['bg_color'],
                          command=None):
    """
    Creates a clickable text label in a given frame.

    This function creates a label with the specified text, font, and background color,
    and makes the label behave like a button (clickable). When clicked, it triggers
    the provided command function.

    :param frame: The parent frame (or container) where the clickable label will be placed.
                  This is the widget that holds the label.
    :param text: The text to be displayed in the clickable label.
    :param font: The font style of the label text. Default is `MONTHLY_PLANS['window_font']`.
    :param bg_color: The background color of the label. Default is `INTERFACE['bg_color']`.
    :param command: A function to be executed when the label is clicked. The function is
                    triggered on a left-click event. If not provided, the label will not
                    have any action.

    :return: None. This function creates a clickable label and adds it to the frame.
    """
    clickable_label = tk.Label(frame, text=text, font=font, fg="black", cursor="hand2", bg=bg_color)
    clickable_label.pack(side="left", padx=(5, 0))

    if command:
        clickable_label.bind("<Button-1>", lambda e: command())

    return clickable_label


async def get_months_ui_data_from_server(year, month):
    """
    Fetches all UI-related data for the specified year and month from the server.

    Args:
        year (int): The year for which data is requested.
        month (str): The month for which data is requested (e.g., "January", "Feb").

    Returns:
        dict: A dictionary containing the month's UI data if the request is successful,
              or an empty dictionary if there was an error.
    """
    params = {"year": int(year), "month": month}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{SERVER_URL}/get_months_ui_data",
                                   json=params, ssl=SSL_ENABLED) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    print(f"Error getting data: {response.status}")
                    return {}
        except Exception as e:
            print(f"Exception error: {e}")
            return {}


async def update_reading_link_on_server(year, month, new_link):
    """
    Sends a request to the server to update the reading link for a specific year and month.

    Args:
        year (int): The year associated with the reading link.
        month (str): The month associated with the reading link.
        new_link (str): The updated URL/link to be stored on the server.

    Returns:
        None. Shows a message box with the result. Logs the error if the request fails.
    """
    data = {"year": year, "month": month, "new_link": new_link}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{SERVER_URL}/update_reading_link",
                                    json=data, ssl=SSL_ENABLED) as response:
                if response.status == 200:
                    messagebox.showinfo("Success", "Reading link updated successfully!")
                else:
                    error_message = await response.text()
                    messagebox.showerror("Error", f"Failed to update reading link.")
                    print("Error:", error_message)
    except Exception as e:
        print(f"Exception error: {e}")
        return {}


async def add_month_goal_to_server(year, month, goal_data):
    """
    Sends a monthly goal to the server to be saved.

    Args:
        year (int): The year the goal is associated with.
        month (str): The month the goal is associated with.
        goal_data (dict): A dictionary containing the goal details.
            Expected keys:
                - "task" (str): The text of the goal/task.
                - "done" (bool): Completion status of the goal.

    Returns:
        None. Logs an error message if the request fails.
    """
    data = {"year": year, "month": month, "task": goal_data["task"], "completed": goal_data["done"]}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{SERVER_URL}/add_month_goal",
                                    json=data, ssl=SSL_ENABLED) as response:
                if response.status != 200:
                    error_message = await response.text()
                    print("Error:", error_message)
    except Exception as e:
        print(f"Exception error: {e}")


async def get_month_goals_from_server(year, month):
    """
    Fetches the list of monthly goals from the server for the given year and month.

    Args:
        year (int): The year for which the goals should be retrieved.
        month (str): The month for which the goals should be retrieved.

    Returns:
        list: A list of goals for the specified year and month.
              Returns an empty list if an error occurs or no goals are found.
    """
    data = {"year": year, "month": month}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SERVER_URL}/get_month_goals",
                                   json=data, ssl=SSL_ENABLED) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("goals", [])
                else:
                    print(f"Error: {response.status} - {await response.text()}")
                    return []
    except Exception as e:
        print(f"Exception while fetching goals: {e}")
        return []


async def toggle_server_goal_state(year, month, goal):
    """
    Toggles the completion status of a specific goal on the server for the given year and month.

    Args:
        year (int): The year associated with the goal.
        month (str): The month associated with the goal.
        goal (dict): A dictionary containing the goal data, including:
                     - "task" (str): The goal description.
                     - "done" (bool): The updated completion state of the goal.

    Returns:
        None
    """
    data = {
        "year": year,
        "month": month,
        "task": goal["task"],
        "done": goal["done"]
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{SERVER_URL}/toggle_month_goal_state",
                                    json=data, ssl=SSL_ENABLED) as response:
                if response.status != 200:
                    error_message = await response.text()
                    print(f"Error updating goal state: {error_message}")
    except Exception as e:
        print(f"Exception while updating goal state: {e}")


async def delete_month_goal_from_server(year, month, goal):
    """
    Deletes a specific goal from the server for the given year and month.

    Args:
        year (int): The year associated with the goal.
        month (str): The month associated with the goal.
        goal (dict): A dictionary containing the goal data, with:
                     - "task" (str): The description of the goal to be deleted.

    Returns:
        None
    """
    payload = {"year": year, "month": month, "task": goal["task"]}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{SERVER_URL}/delete_month_goal",
                                    json=payload, ssl=SSL_ENABLED) as response:
                if response.status != 200:
                    error_msg = await response.text()
                    print(f"Error deleting goal: {error_msg}")
    except Exception as e:
        print(f"Exception while deleting goal: {e}")


async def update_month_goal_on_server(year, month, new_task, old_task):
    """
    Updates an existing monthly goal on the server by replacing the old task with a new one.

    Args:
        year (int): The year the goal is associated with.
        month (str): The month the goal is associated with.
        new_task (str): The updated task content.
        old_task (str): The original task content to be replaced.

    Returns:
        None
    """
    payload = {
        "year": year,
        "month": month,
        "old_task": old_task,
        "new_task": new_task
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{SERVER_URL}/update_month_goal",
                                    json=payload, ssl=SSL_ENABLED) as response:
                if response.status != 200:
                    error_message = await response.text()
                    print(f"Error updating goal: {response.status} - {error_message}")
    except Exception as e:
        print(f"Exception during goal update: {e}")


async def add_months_diary_task_to_server(year, month, task, day_date):
    """
    Sends a new diary task for a specific date within a month to the server.

    Args:
        year (int): The year associated with the task.
        month (str): The month associated with the task (e.g., "January").
        task (str): The content of the task to be added.
        day_date (str): The date for the task in "DD.MM.YY" format.

    Returns:
        dict | None: The response JSON from the server if successful, otherwise None.
    """
    task_date = datetime.strptime(day_date, "%d.%m.%y").date()
    data = {
        "year": year,
        "month": month,
        "task": task,
        "date": task_date.isoformat(),
        "completed": False
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{SERVER_URL}/add_month_diary_task",
                                    json=data, ssl=SSL_ENABLED) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_message = await response.text()
                    print(f"Error updating goal: {response.status} - {error_message}")
    except Exception as e:
        print(f"Exception during diary task add: {e}")


async def get_month_diary_tasks_from_server(year, month):
    """
    Fetches diary tasks for a specific month and year from the server.

    Args:
        year (int): The year for which to retrieve tasks.
        month (str): The name of the month (e.g., "January").

    Returns:
        list: A list of diary tasks if the request is successful, otherwise an empty list.
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{SERVER_URL}/get_month_diary_tasks",
                                    json={"year": year, "month": month}, ssl=SSL_ENABLED) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("tasks", [])
                else:
                    error_message = await response.text()
                    print(f"Error fetching tasks: {response.status} - {error_message}")
                    return []
        except Exception as e:
            print(f"Exception during task fetch: {e}")
            return []


async def delete_diary_task_from_server(year, month, task, date):
    """
    Sends a request to delete a diary task for a given date.

    Args:
        year (int): The year of the task.
        month (str): The name of the month.
        task (str): The task description to delete.
        date (str): The ISO-formatted date (e.g., "2025-04-04") associated with the task.

    Returns:
        list: An empty list if an exception occurs. Otherwise, returns None.
    """
    payload = {
        "year": year,
        "month": month,
        "task": task,
        "date": date
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{SERVER_URL}/delete_month_diary_task",
                                    json=payload, ssl=SSL_ENABLED) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"Error deleting task: {response.status} - {error_text}")
    except Exception as e:
        print(f"Exception during diary task delete: {e}")
        return []


async def toggle_diary_task_status_on_server(year, month, task, date, done):
    """
    Toggles the completion status of a diary task for a given date.

    Args:
        year (int): The year of the task.
        month (str): The month name (e.g., 'January', 'February').
        task (str): The task description to toggle.
        date (str): The ISO-formatted date (e.g., "2025-04-04") associated with the task.
        done (bool): The completion status of the task. True if completed, False otherwise.

    Returns:
        None: If successful, it updates the task status but does not return anything.
    """
    payload = {
        "year": year,
        "month": month,
        "task": task,
        "date": date,
        "done": done
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{SERVER_URL}/toggle_month_diary_task",
                                    json=payload, ssl=SSL_ENABLED) as response:
                if response.status != 200:
                    print(f"Error updating task: {response.status}")
    except Exception as e:
        print("Exception while toggling task:", e)


async def update_month_diary_task_on_server(year, month, date, old_task, new_task):
    """
    Updates a diary task for a given month and date.

    Args:
        year (int): The year of the task.
        month (str): The month of the task (e.g., 'January', 'February').
        date (str): The ISO-formatted date (e.g., "2025-04-04") associated with the task.
        old_task (str): The current task description that will be replaced.
        new_task (str): The new task description that will replace the old task.

    Returns:
        None: If successful, it updates the task on the server but does not return anything.
    """
    payload = {
        "year": year,
        "month": month,
        "old_task": old_task,
        "new_task": new_task,
        "date": date
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{SERVER_URL}/update_month_diary_task",
                                    json=payload, ssl=SSL_ENABLED) as response:
                if response.status != 200:
                    print(f"Error updating task: {response.status}")
    except Exception as e:
        print("Exception while updating task:", e)


async def get_popup_color_from_server(year, month):
    """
    Fetches the popup color for a given year and month from the server.

    Args:
        year (int): The year for which the popup color is requested.
        month (str): The month for which the popup color is requested.

    Returns:
        dict: A dictionary containing the popup color data if the request is successful.
        list: An empty list in case of failure or exception.
    """
    payload = {
        "year": year,
        "month": month
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SERVER_URL}/get_popup_colour",
                                   json=payload, ssl=SSL_ENABLED) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    print(f"Error fetching popup color: {response.status}")
                    return []
    except Exception as e:
        print(f"Exception while fetching popup color: {e}")
        return []


async def get_popup_data_from_server(year, month):
    """
    Fetches the popup data for a given year and month from the server.

    Args:
        year (int): The year for which the popup data is requested.
        month (str): The month for which the popup data is requested.

    Returns:
        dict: A dictionary containing the popup data if the request is successful.
        list: An empty list in case of failure or exception.
    """
    payload = {
        "year": year,
        "month": month
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SERVER_URL}/get_popup_data",
                                   json=payload, ssl=SSL_ENABLED) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    print(f"Error fetching popup data: {response.status}")
                    return []
    except Exception as e:
        print(f"Exception while fetching popup data: {e}")
        return []


async def add_popup_color_to_server(year, month, formatted_date, selected_color):
    """
    Adds the selected popup color for a specific date to the server.

    Args:
        year (int): The year to which the popup color belongs.
        month (str): The month to which the popup color belongs.
        formatted_date (str): The formatted date (e.g., "DD.MM.YYYY") for which the color is applied.
        selected_color (str): The selected color code to be associated with the date.

    Returns:
        dict: A dictionary with the status and message indicating the result of the operation.
    """
    payload = {
        "year": year,
        "month": month,
        "date": formatted_date,
        "colour_code": selected_color
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{SERVER_URL}/add_month_popup_colour", json=payload,
                                    ssl=SSL_ENABLED) as response:
                if response.status != 200:
                    print(f"Error adding popup color: {response.status}")
                    return {"status": "error", "message": "Failed to add popup color"}
    except Exception as e:
        print(f"Exception while adding popup color: {e}")
        return {"status": "error", "message": f"Exception occurred: {e}"}


async def add_popup_data_to_server(year, month, formatted_date, popup_text):
    """
    Adds popup message data for a specific date to the server.

    Args:
        year (int): The year to which the popup data belongs.
        month (str): The month to which the popup data belongs.
        formatted_date (str): The formatted date (e.g., "DD.MM.YYYY") for which the popup message is set.
        popup_text (str): The text message to be associated with the date for the popup.

    Returns:
        dict: A dictionary with the status and message indicating the result of the operation.
    """
    payload = {
        "year": year,
        "month": month,
        "date": formatted_date,
        "popup_message": popup_text
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{SERVER_URL}/add_month_popup_data", json=payload,
                                    ssl=SSL_ENABLED) as response:
                if response.status != 200:
                    print(f"Error adding popup data: {response.status}")
                    return {"status": "error", "message": "Failed to add popup data"}
    except Exception as e:
        print(f"Exception while adding popup data: {e}")
        return {"status": "error", "message": f"Exception occurred: {e}"}


async def delete_popup_colour_from_server(year, month, date):
    """
    Deletes a popup color for a specific date from the server.

    Args:
        year (int): The year to which the popup color belongs.
        month (str): The month to which the popup color belongs.
        date (str): The formatted date (e.g., "DD.MM.YYYY") for which the popup color is set.

    Returns:
        dict: A dictionary with the status and message indicating the result of the operation.
    """
    payload = {
        "year": year,
        "month": month,
        "date": date
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{SERVER_URL}/delete_month_popup_colour", json=payload,
                                      ssl=SSL_ENABLED) as response:
                if response.status != 200:
                    print(f"Error deleting popup color: {response.status}")
                    return {"status": "error", "message": "Failed to delete popup color"}
    except Exception as e:
        print(f"Exception while deleting popup color: {e}")
        return {"status": "error", "message": f"Exception occurred: {e}"}


async def delete_popup_data_from_server(year, month, date):
    """
    Deletes popup data (message) for a specific date from the server.

    Args:
        year (int): The year to which the popup data belongs.
        month (str): The month to which the popup data belongs.
        date (str): The formatted date (e.g., "DD.MM.YYYY") for which the popup data is set.

    Returns:
        dict: A dictionary with the status and message indicating the result of the operation.
    """
    payload = {
        "year": year,
        "month": month,
        "date": date
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{SERVER_URL}/delete_month_popup_data", json=payload,
                                      ssl=SSL_ENABLED) as response:
                if response.status != 200:
                    print(f"Error deleting popup data: {response.status}")
                    return {"status": "error", "message": "Failed to delete popup data"}
    except Exception as e:
        print(f"Exception while deleting popup data: {e}")
        return {"status": "error", "message": f"Exception occurred: {e}"}


def get_tooltip_input(parent, main_window):
    """
    Creates a popup window that prompts the user to enter a task for a selected day.
    This method displays a small window with an input field, where the user can type
    a task description. Upon clicking "OK", the input is retrieved and returned.

    :param parent: The parent widget that will be used to center the popup window.
    :param main_window: The main window, used to determine the position of the popup
                         window relative to it.
    :return: A string representing the task entered by the user. If no task is entered,
             an empty string is returned.
    """
    popup = tk.Toplevel(parent)
    popup.withdraw()
    popup.title("Enter task")
    center_window_on_parent(main_window, popup, 400, 150)
    popup.iconbitmap(APP['icon_path'])

    font_style = MONTHLY_PLANS['toplevel_windows_font']

    label = tk.Label(popup, text="Add task for selected day:", font=font_style)
    label.pack(padx=20, pady=10)

    input_field = tk.Entry(popup, font=font_style)
    input_field.pack(padx=20, pady=10)
    input_field.bind("<Return>", lambda event: on_ok())

    result = {"value": None}

    def on_ok():
        """
        This function retrieves the value entered in the input field and
        closes the popup window.

        :return: None
        """

        popup_input = input_field.get()

        if not popup_input:
            messagebox.showerror("Empty Input", "Field cannot be empty! Please enter your description.")
            popup.lift()
            return

        result["value"] = popup_input
        popup.destroy()

    # OK button
    button = tk.Button(popup, text="OK", command=on_ok, font=font_style)
    button.pack(pady=10)
    button.config(cursor="hand2")

    popup.deiconify()
    parent.wait_window(popup)

    return result["value"] if result["value"] else ""


class MonthlyPlans(tk.Frame):
    """
    This class represents the Monthly Plans interface, which displays
    various information related to the selected month including banners,
    icons, task lists, and other relevant details. It is a part of the
    larger application, and this frame can be integrated into the main window.

    Attributes:
        parent (tk.Widget): The parent widget (typically the main window)
            in which this frame is embedded.
        main_window (tk.Tk): The main application window, used for general
            application control.
        year (int): The current year displayed in the monthly plans.
        month (int): The current month displayed in the monthly plans.
        tasks (dict): A dictionary containing tasks loaded from server.
        month_data (dict): A dictionary containing UI data loaded from server.
        month_goals (dict): A dictionary containing month goals loaded from server.
        popup_color (dict): A dictionary containing popup colors loaded from server.
        popup_data (dict): A dictionary containing popup data loaded from server.
        header_frames (list): A list to store header-related UI components.
        banner_label (tk.Label): Label for displaying the banner image.
        banner_image_original (Image): The original image object for the banner.
        icon_image_original (Image): The original image object for the month icon.
    """
    def __init__(self, parent, main_window, year, month):
        """
        Initializes the MonthlyPlans frame.

        :param parent: The parent widget in which this frame will be placed.
        :param main_window: The main application window.
        :param year: The year to be displayed for the selected month.
        :param month: The month to be displayed in the frame.
        """
        super().__init__(parent)
        self.configure(bg=INTERFACE['bg_color'])
        self.main_window = main_window
        self.main_window.disable_buttons()
        self.year = year
        self.month = month
        self.parent = parent

        self.main_window.check_scrollbar()

        self.tasks = asyncio.run(get_month_diary_tasks_from_server(self.year, self.month))

        self.month_data = asyncio.run(get_months_ui_data_from_server(self.year, self.month))

        icon_path = None
        banner_path = None
        reading_path = None
        month_icon_path = None

        if self.month_data:
            icon_path = self.month_data["icon_path"]
            banner_path = self.month_data["banner"]
            reading_path = self.month_data["reading_link"]
            month_icon_path = self.month_data["month_icon_path"]

        self.month_goals = asyncio.run(get_month_goals_from_server(self.year, self.month))

        self.popup_color = asyncio.run(get_popup_color_from_server(self.year, self.month))
        self.popup_data = asyncio.run(get_popup_data_from_server(self.year, self.month))

        self.header_frames = []

        self.first_clickable_label, self.second_clickable_label, self.third_clickable_label = (
            self.add_source_label(icon_path, self.month))

        self.first_clickable_label["state"] = "disabled"
        self.second_clickable_label["state"] = "disabled"
        self.third_clickable_label["state"] = "disabled"

        # Banner add
        self.banner_label, self.banner_image_original = add_banner(
            self,
            banner_path=banner_path,
            bg_color=INTERFACE['bg_color']
        )

        # resize_banner
        if self.banner_label and self.banner_image_original:
            self.bind("<Configure>", lambda event: resize_banner(
                self,
                self.banner_label,
                self.banner_image_original
            ))

        self.icon_image_original = asyncio.run(add_icon_image(icon_path))

        add_icon_and_label(self, text=self.month,
                           icon_path=icon_path,
                           bg_color=INTERFACE['bg_color'])
        add_separator(parent=self, color=INTERFACE['separator'])

        self.add_head_data(reading_path)

        add_separator(parent=self, color=INTERFACE['separator'])

        self.add_diary()
        add_separator(parent=self, color=INTERFACE['separator'])

        self.add_month(month_icon_path)

        self.main_window.enable_buttons()
        self.first_clickable_label["state"] = "normal"
        self.second_clickable_label["state"] = "normal"
        self.third_clickable_label["state"] = "normal"

    def initialize_frame_colors(self, date, frame):
        """
        Initializes the color and popup content for a specific date's frame based on
        the stored data in `self.tasks`. This method checks if the date has a color
        assigned to it and changes the background color of the provided frame. It
        also checks if there is a popup message associated with the date and adds
        it to the frame if available.

        :param date: A string representing the date in the format "day.month.year".
                     Example: "25.12.2024" for December 25th, 2024.
        :param frame: The Tkinter frame widget whose color and tooltip need to be set.
        :return: None
        """
        formatted_date = datetime.strptime(date, "%d.%m.%y").date().isoformat()

        color = None
        for item in self.popup_color:
            if item['date'] == formatted_date:
                color = item['colour_code']
                break

        popup_text = None
        for item in self.popup_data:
            if item['date'] == formatted_date:
                popup_text = item['popup_message']
                break

        if color:
            def change_color_recursive(widget, color):
                """
                A recursive helper function to change the background color of the widget
                and its children.

                :param widget: The widget whose background color is to be changed.
                :param color: The color to set as the background.
                :return: None
                """
                try:
                    widget.config(bg=color)
                except tk.TclError:
                    pass
                for child in widget.winfo_children():
                    change_color_recursive(child, color)

            change_color_recursive(frame, color)

        if popup_text:
            add_popup(frame, popup_text)

    def on_left_click(self, event, frame, date):
        """
        Handles the event when the user left-clicks on a specific date's frame in the calendar.
        It toggles the background color of the frame, adds or removes task information for
        the selected date, and updates the calendar server data.

        :param event: The event that triggered the function (not used in this method directly).
        :param frame: The Tkinter frame representing the selected date in the calendar.
        :param date: The string representing the selected date in the format "day.month.year".
        :return: None
        """
        current_bg = frame.cget("bg")
        default_bg = INTERFACE['bg_color']
        # New color
        selected_color = MONTHLY_PLANS['selected_date_color']

        def unbind_popup_recursive(widget):
            """
            Unbinds the popup tooltip events (hover in/out) from the widget and its children.

            :param widget: The widget from which to unbind the events.
            :return: None
            """
            widget.unbind("<Enter>")
            widget.unbind("<Leave>")
            for child in widget.winfo_children():
                unbind_popup_recursive(child)

        formatted_date = datetime.strptime(date, "%d.%m.%y").date().isoformat()

        if current_bg == selected_color:
            self.change_frame_background(frame, default_bg)

            # Delete entries from both arrays
            self.popup_color = [item for item in self.popup_color if item['date'] != formatted_date]
            self.popup_data = [item for item in self.popup_data if item['date'] != formatted_date]
            asyncio.run(delete_popup_colour_from_server(self.year, self.month, formatted_date))
            asyncio.run(delete_popup_data_from_server(self.year, self.month, formatted_date))

            unbind_popup_recursive(frame)

            frame.bind("<Enter>", lambda event: frame.config(cursor="hand2"))
            frame.bind("<Leave>", lambda event: frame.config(cursor=""))

        else:
            popup_text = get_tooltip_input(self.main_window, self.main_window,)

            if popup_text:
                self.change_frame_background(frame, selected_color)

                self.popup_color.append({'date': formatted_date, 'colour_code': selected_color})
                self.popup_data.append({'date': formatted_date, 'popup_message': popup_text})

                asyncio.run(add_popup_color_to_server(self.year, self.month, formatted_date, selected_color))
                asyncio.run(add_popup_data_to_server(self.year, self.month, formatted_date, popup_text))

                add_popup(frame, popup_text)

                frame.bind("<Enter>", lambda event: frame.config(cursor="hand2"))
                frame.bind("<Leave>", lambda event: frame.config(cursor=""))

        self.fill_calendar(self.popup_color, self.popup_data)

    def change_frame_background(self, widget, bg_color):
        """
        Recursively changes the background color of the given widget and all of its child widgets.

        This method is useful for updating the background color of a container widget (such as a frame)
        and ensuring that all its child widgets inherit the new color.

        :param widget: The Tkinter widget whose background color is to be changed. This can be any widget,
                       such as a frame, button, label, etc.
        :param bg_color: The background color to set for the widget and its children.
        :return: None
        """
        widget.config(bg=bg_color)
        for child in widget.winfo_children():
            self.change_frame_background(child, bg_color)

    def add_month(self, month_icon_path):
        """
        Adds a calendar view for a specific month, displaying each day of the month along with associated tasks and other elements.
        The function generates a series of UI elements, including frames, labels, input fields, and buttons to interact with each day.

        :param month_icon_path: Path to the icon associated with the month (for example, a picture or logo).
        :return: None
        """
        year = self.year

        month = {name: num for num, name in enumerate(cal.month_name) if name}[self.month]

        _, num_days = cal.monthrange(year, month)

        weekdays = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

        for day in range(1, num_days + 1):
            month_frame_title = tk.Frame(self, bg=INTERFACE['bg_color'])
            month_frame_title.pack(pady=5)

            day_date = f"{day:02d}.{month:02d}.{str(year)[2:]}"

            title_frame_month = tk.Frame(month_frame_title, bg=INTERFACE['bg_color'])
            title_frame_month.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
            title_label(title_frame_month, day_date, month_icon_path,
                        MONTHLY_PLANS['title_icon_dimensions'],
                        MONTHLY_PLANS['title_icon_dimensions'])

            self.initialize_frame_colors(day_date, title_frame_month)

            def bind_event_to_children(widget, event, handler):
                """
                Binds a specific event handler to the widget and all of its child widgets.

                :param widget: The parent widget to bind the event to.
                :param event: The event type (e.g., <Button-1> for left click).
                :param handler: The event handler function to be called when the event occurs.
                :return: None
                """
                widget.bind(event, handler)
                for child in widget.winfo_children():
                    bind_event_to_children(child, event, handler)

            def bind_cursor_change_recursive(widget, enter_cursor, leave_cursor):
                """
                Changes the cursor style when the mouse enters or leaves a widget.

                :param widget: The widget to bind cursor change events to.
                :param enter_cursor: The cursor style to apply when the mouse enters the widget.
                :param leave_cursor: The cursor style to apply when the mouse leaves the widget.
                :return: None
                """
                widget.bind("<Enter>", lambda event: widget.config(cursor=enter_cursor))
                widget.bind("<Leave>", lambda event: widget.config(cursor=leave_cursor))

            bind_event_to_children(title_frame_month,
                                   "<Button-1>",
                                   lambda event,
                                          title_frame_month=title_frame_month,
                                          day_date=day_date: self.on_left_click(event, title_frame_month, day_date))

            bind_cursor_change_recursive(title_frame_month, "hand2", "")

            add_separator(parent=self, color=INTERFACE['separator'])

            month_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
            month_frame.pack(pady=5, fill="x")

            left_frame = tk.Frame(month_frame, bg=INTERFACE['bg_color'])
            left_frame.grid(column=0, row=0, padx=5, pady=5, sticky="w")

            month_frame.grid_columnconfigure(0, weight=1)
            month_frame.grid_columnconfigure(1, weight=1)

            input_frame = tk.Frame(left_frame, bg=INTERFACE['bg_color'])
            input_frame.grid(row=0, column=0, sticky="w", pady=5)

            task_input = tk.Entry(input_frame, bg=MONTHLY_PLANS['entry_bg_color'], font=MONTHLY_PLANS['window_font'])
            task_input.grid(row=0, column=0, padx=5, pady=5)

            tasks_frame = tk.Frame(left_frame, bg=INTERFACE['bg_color'])
            tasks_frame.grid(row=1, column=0, sticky="w", pady=5)

            add_task_button = tk.Button(
                input_frame,
                text="Add task",
                command=lambda task_input=task_input, tasks_frame=tasks_frame,
                               day_date=day_date: self.add_task_to_frame(tasks_frame, task_input, day_date),
                bg=MONTHLY_PLANS['add_button_color'],
                font=MONTHLY_PLANS['buttons_font']
            )
            add_task_button.grid(row=0, column=1, padx=5)
            add_task_button.config(cursor="hand2")
            task_input.bind("<Return>", lambda event, task_input=task_input, tasks_frame=tasks_frame,
                                               day_date=day_date: self.add_task_to_frame(tasks_frame, task_input,
                                                                                         day_date))

            right_frame = tk.Frame(month_frame, bg=INTERFACE['bg_color'])
            right_frame.grid(column=1, row=0, padx=5, pady=5, sticky="nw")

            weekday_index = cal.weekday(year, month, day)
            weekday_name = weekdays[weekday_index]

            label = tk.Label(right_frame, text=weekday_name, bg=INTERFACE['bg_color'],
                             font=MONTHLY_PLANS['window_font'])
            label.pack(anchor="nw")

            self.load_existing_tasks_for_day(tasks_frame, day_date)

            add_separator(parent=self, color=INTERFACE['separator'])

    def load_existing_tasks_for_day(self, tasks_frame, day_date):
        """
        Loads and displays any existing tasks for a specific day.
        Now works with a list of tasks instead of a nested dictionary.

        :param tasks_frame: The frame where tasks will be displayed.
        :param day_date: The date in format DD.MM.YY (e.g., "01.01.25").
        :return: None
        """
        try:
            day_obj = datetime.strptime(day_date, "%d.%m.%y")
            formatted_date = day_obj.strftime("%Y-%m-%d")

            day_tasks = [task for task in self.tasks if task["date"] == formatted_date]

            if not day_tasks:
                return

            for idx, task in enumerate(day_tasks):
                task_text = task["task"]
                task_done = task["completed"]

                task_var = tk.BooleanVar(value=task_done)
                task_checkbox = tk.Checkbutton(
                    tasks_frame,
                    text=task_text,
                    variable=task_var,
                    bg=INTERFACE['bg_color'],
                    font=MONTHLY_PLANS['window_font'],
                    anchor="w",
                    command=lambda task_text=task_text, task_var=task_var,
                                   day_date=day_date: self.update_task_status(
                        task_text, task_var.get(), day_date)
                )
                task_checkbox.config(wraplength=300)
                task_checkbox.grid(row=len(tasks_frame.winfo_children()), column=0, sticky="w", padx=5, pady=2)
                task_checkbox.config(cursor="hand2")

                menu = self.create_diary_context_menu(task_text, task_checkbox, day_date, tasks_frame)
                task_checkbox.bind("<Button-3>", lambda event, m=menu: m.post(event.x_root, event.y_root))

                ToolTip(task_checkbox, "Right click to edit/delete")

        except ValueError:
            print(f"Invalid date format: {day_date}")

    def create_diary_context_menu(self, task_text, task_checkbox, day_date, tasks_frame):
        """
        Creates a context menu for a diary task with options to edit or delete the task.

        :param task_text: The text of the task to be displayed.
        :param task_checkbox: The checkbox widget associated with the task.
        :param day_date: The date for which the task is scheduled.
        :param tasks_frame: The frame containing all the tasks.
        :return: A Tkinter Menu widget with options to edit or delete the task.
        """
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Edit",
                         command=lambda: self.edit_diary_task(task_text, day_date, tasks_frame, task_checkbox))
        menu.add_command(label="Delete", command=lambda: self.delete_diary_task(task_text, day_date, tasks_frame))
        return menu

    def edit_diary_task(self, diary_task, day_date, tasks_frame, checkbox):
        """
        Opens a new window that allows the user to edit an existing diary task.

        :param diary_task: The current text of the task to be edited.
        :param day_date: The date for which the task is scheduled.
        :param tasks_frame: The frame containing the tasks for the day.
        :param checkbox: The checkbox widget associated with the task (not used in this function but might be relevant for future edits).
        :return: None
        """
        edit_window = tk.Toplevel(self)
        edit_window.withdraw()
        center_window_on_parent(self.main_window, edit_window, 300, 200)
        edit_window.title("Edit Task")
        edit_window.iconbitmap(APP['icon_path'])

        tk.Label(edit_window, text="Edit your task:", font=MONTHLY_PLANS['toplevel_windows_font']).pack(pady=10)
        task_entry = tk.Entry(edit_window, width=30, font=MONTHLY_PLANS['toplevel_windows_font'])
        task_entry.pack(pady=5)
        task_entry.insert(0, diary_task)
        task_entry.bind("<Return>", lambda event: save_changes())

        def save_changes():
            """
            Saves the changes made to the diary task and updates the task list.

            :return: None
            """
            new_task_text = task_entry.get().strip()
            formatted_date = datetime.strptime(day_date, "%d.%m.%y").date().isoformat()

            if not new_task_text:
                messagebox.showerror("Error", "Task can't be empty!")
                edit_window.lift()
                return

            # Check if task wasn't changed
            if new_task_text == diary_task:
                messagebox.showinfo("Info", "Task title wasn't changed.")
                edit_window.lift()
                return

            # Check if task already exists for this date
            for existing_task in self.tasks:
                if existing_task['date'] == formatted_date and existing_task['task'] == new_task_text:
                    messagebox.showerror("Error", "This task already exists for this date!")
                    edit_window.lift()
                    return

            old_task_text = None

            for task in self.tasks:
                if task['date'] == formatted_date and task['task'] == diary_task:
                    old_task_text = task['task']
                    task['task'] = new_task_text
                    break

            asyncio.run(update_month_diary_task_on_server(self.year, self.month,
                                                          formatted_date, old_task_text, new_task_text))

            for widget in tasks_frame.winfo_children():
                widget.destroy()

            self.load_existing_tasks_for_day(tasks_frame, day_date)

            edit_window.destroy()

        # Buttons
        save_button = tk.Button(edit_window, text="Save", command=save_changes,
                                font=MONTHLY_PLANS['toplevel_windows_font'])
        save_button.pack(pady=10)
        save_button.config(cursor="hand2")

        cancel_button = tk.Button(edit_window, text="Cancel", command=edit_window.destroy,
                                  font=MONTHLY_PLANS['toplevel_windows_font'])
        cancel_button.pack(pady=10)
        cancel_button.config(cursor="hand2")

        edit_window.deiconify()

    def delete_diary_task(self, diary_task, day_date, tasks_frame):
        """
        Deletes a specific task from the diary for a given day and updates the UI.

        :param diary_task: The text of the task to be deleted.
        :param day_date: The date for which the task is scheduled.
        :param tasks_frame: The frame that holds the UI components for the tasks of the day.
        :return: None
        """
        formatted_date = datetime.strptime(day_date, "%d.%m.%y").date().isoformat()

        self.tasks = [
            task for task in self.tasks
            if not (task["date"] == formatted_date and task["task"] == diary_task)
        ]

        asyncio.run(delete_diary_task_from_server(self.year, self.month, diary_task, formatted_date))

        for widget in tasks_frame.winfo_children():
            widget.destroy()

        self.load_existing_tasks_for_day(tasks_frame, day_date)

    def update_task_status(self, task_text, task_done, day_date):
        """
        Updates the completion status of a task for a given day in the diary.

        :param task_text: The text of the task whose status needs to be updated.
        :param task_done: A boolean value indicating whether the task is marked as done (True) or not (False).
        :param day_date: The date on which the task is scheduled.
        :return: None
        """
        if "." in day_date:
            try:
                day_date = datetime.strptime(day_date, "%d.%m.%y").date().isoformat()
            except ValueError:
                print("Date format error:", day_date)
                return

        for task in self.tasks:
            if task["date"] == day_date and task["task"] == task_text:
                task["completed"] = task_done
                asyncio.run(toggle_diary_task_status_on_server(self.year, self.month, task_text, day_date, task_done))
                break

    def add_task_to_frame(self, tasks_frame, task_input, day_date):
        """
        Adds a new task to the task list for a specific day and updates the UI.

        :param tasks_frame: The frame where the tasks for the day are displayed.
        :param task_input: The input field (Entry widget) containing the new task text.
        :param day_date: The date on which the new task is scheduled.
        :return: None
        """
        task = task_input.get()

        if not task:
            messagebox.showwarning("Empty field", "Please enter your task!")
            return

        date_obj = datetime.strptime(day_date, "%d.%m.%y")
        formatted_date = date_obj.strftime("%Y-%m-%d")

        for existing_task in self.tasks:
            if existing_task["date"] == formatted_date and existing_task["task"] == task:
                messagebox.showwarning("Warning", f"Task '{task}' already exists for {day_date}")
                return

        new_task = {
            "date": formatted_date,
            "task": task,
            "completed": False
        }
        self.tasks.append(new_task)

        asyncio.run(add_months_diary_task_to_server(self.year, self.month, task, day_date))

        task_input.delete(0, tk.END)

        for widget in tasks_frame.winfo_children():
            widget.destroy()

        self.load_existing_tasks_for_day(tasks_frame, day_date)

    def add_diary(self):
        """
        Creates and displays a diary section in the user interface, including a title frame
        and a label with the title and an icon.

        :return: None
        """
        title_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        title_frame.pack(pady=5)

        title_label(title_frame, MONTHLY_PLANS['diary_title'],
                    MONTHLY_PLANS['diary_icon_path'],
                    MONTHLY_PLANS['title_icon_dimensions'],
                    MONTHLY_PLANS['title_icon_dimensions'])

    def add_head_data(self, reading_path):
        """
        Creates and displays the main header section of the interface, including frames for
        displaying reading data, a calendar, and goals. Also adds relevant titles, icons,
        and links for each section.

        :param reading_path: The path to the reading link to be displayed.
        :return: None
        """
        self.data_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        self.data_frame.pack(pady=5)

        left_frame = tk.Frame(self.data_frame, bg=INTERFACE['bg_color'])
        left_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nw")

        title_label(left_frame,
                    MONTHLY_PLANS['reading_title'],
                    MONTHLY_PLANS['reading_icon_path'],
                    MONTHLY_PLANS['title_icon_dimensions'],
                    MONTHLY_PLANS['title_icon_dimensions'])
        add_line_under_title(self.data_frame, row=1, column=0, width=180)

        self.add_reading_link(self.data_frame, reading_path)

        center_frame = tk.Frame(self.data_frame, bg=INTERFACE['bg_color'])
        center_frame.grid(row=0, column=1, padx=10, pady=5, sticky="n")

        title_label(center_frame,
                    MONTHLY_PLANS['calendar_title'],
                    MONTHLY_PLANS['calendar_icon_path'],
                    MONTHLY_PLANS['title_icon_dimensions'],
                    MONTHLY_PLANS['title_icon_dimensions'])
        add_line_under_title(self.data_frame, row=1, column=1, width=200)

        self.my_calendar = TkCalendar(self.data_frame, selectmode='day', date_pattern='dd-mm-yyyy',
                                      font=MONTHLY_PLANS['calendar_font'],
                                      width=160, height=100)
        self.my_calendar.grid(row=2, column=1, pady=10, sticky="n")

        month_mapping = {
            "January": 1,
            "February": 2,
            "March": 3,
            "April": 4,
            "May": 5,
            "June": 6,
            "July": 7,
            "August": 8,
            "September": 9,
            "October": 10,
            "November": 11,
            "December": 12
        }

        month_number = month_mapping.get(self.month)

        start_date = datetime(self.year, month_number, 1)

        self.my_calendar.selection_set(start_date)

        self.my_calendar.tag_config("popup_highlight",
                                    background=MONTHLY_PLANS['calendar_selected_color'],
                                    foreground=MONTHLY_PLANS['calendar_selected_text_color'])

        self.fill_calendar(self.popup_color, self.popup_data)

        right_frame = tk.Frame(self.data_frame, bg=INTERFACE['bg_color'])
        right_frame.grid(row=0, column=2, padx=10, pady=5, sticky="nw")

        title_label(right_frame,
                    MONTHLY_PLANS['goals_title'],
                    MONTHLY_PLANS['goals_icon_path'],
                    MONTHLY_PLANS['title_icon_dimensions'],
                    MONTHLY_PLANS['title_icon_dimensions'])

        add_line_under_title(self.data_frame, row=1, column=2, width=150)
        self.add_goal()

    def fill_calendar(self, popup_color, popup_data):
        """
        This method fills the calendar with events that have associated popup messages and color codes
        for specific dates. It first clears any existing events and then processes the provided data to
        create new events in the calendar for the specified month.

        Args:
            popup_color (list): A list of dictionaries containing color codes for specific dates. Each dictionary
                                 should have 'date' (str) and 'colour_code' (str) keys.
            popup_data (list): A list of dictionaries containing popup messages for specific dates. Each dictionary
                               should have 'date' (str) and 'popup_message' (str) keys.

        Returns:
            None: This method does not return anything. It modifies the calendar by adding new events.
        """
        for event_id in self.my_calendar.get_calevents():
            self.my_calendar.calevent_remove(event_id)

        # Create mappings for faster lookup
        popup_dict = {}
        color_dict = {}

        # Process all date formats
        for item in popup_data + popup_color:
            date_str = item['date']
            try:
                # Try ISO format first (2025-01-05)
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                try:
                    # Try day-month-year format (05.01.25)
                    date_obj = datetime.strptime(date_str, "%d.%m.%y")
                except ValueError:
                    print(f"Skipping invalid date format: {date_str}")
                    continue

            # Standardize the date string for consistent lookups
            std_date = date_obj.strftime("%Y-%m-%d")

            if 'popup_message' in item:
                popup_dict[std_date] = item['popup_message']
            if 'colour_code' in item:
                color_dict[std_date] = item['colour_code']

        # Process all unique dates
        all_dates = set(popup_dict.keys()).union(set(color_dict.keys()))

        for date_str in all_dates:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")

                # Only process dates for the specified month
                if date_obj.strftime("%B") == self.month:
                    # Get popup text if exists
                    popup_text = popup_dict.get(date_str, "")

                    # Create event (even if no popup text, just for color highlighting)
                    self.my_calendar.calevent_create(date_obj, popup_text, "popup_highlight")

            except ValueError:
                print(f"Wrong date format: {date_str}")

    def add_goal(self):
        """
        Creates and displays the goals section in the UI, including a button to add new goals.

        This function creates a frame for displaying goals, adds a button that allows the user to
        add a new goal, and then displays any existing goals in the interface.

        :return: None
        """
        goals_frame = tk.Frame(self.data_frame, bg=INTERFACE['bg_color'])
        goals_frame.grid(row=2, column=2, padx=10, pady=5, sticky="nsew")

        add_goal_button = tk.Button(goals_frame, text="Add goal", command=self.add_new_goal,
                                    font=MONTHLY_PLANS['buttons_font'],
                                    bg=MONTHLY_PLANS['add_button_color'])
        add_goal_button.grid(row=0, column=0, pady=10)
        add_goal_button.config(cursor="hand2")

        self.goals_frame = goals_frame

        self.display_goals()

    def create_context_menu(self, goal, checkbox):
        """
        Creates a context menu for a goal, allowing the user to edit or delete the goal.

        This function creates a right-click context menu with two options:
        1. Edit: Opens an edit dialog for the goal.
        2. Delete: Deletes the goal from the list.

        :param goal: The goal text or object for which the context menu is being created.
        :param checkbox: The checkbox widget associated with the goal. It may be used for editing the goal's completion status.
        :return: A tk.Menu object representing the context menu.
        """
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Edit", command=lambda: self.edit_goal(goal, checkbox))
        menu.add_command(label="Delete", command=lambda: self.delete_goal(goal))
        return menu

    def edit_goal(self, goal, checkbox):
        """
        Opens a dialog window that allows the user to edit an existing goal.

        This function creates a top-level window with a text entry field to allow the user
        to modify the task associated with the provided goal. After the user submits the edit,
        the goal is updated, and the change is reflected in the associated checkbox text.

        :param goal: The goal object that contains the task information to be edited.
        :param checkbox: The checkbox widget associated with the goal. The goal's text is also updated in this checkbox.
        :return: None
        """
        edit_window = tk.Toplevel(self)
        edit_window.withdraw()
        center_window_on_parent(self.main_window, edit_window, 400, 100)
        edit_window.title("Edit Goal")
        edit_window.iconbitmap(APP['icon_path'])

        goal_entry = tk.Entry(edit_window, font=MONTHLY_PLANS['toplevel_windows_font'], width=30)
        goal_entry.insert(0, goal["task"])
        goal_entry.pack(pady=10)
        goal_entry.bind("<Return>", lambda event: submit_edit())

        def submit_edit():
            """
            Submits the edited goal, updating the goal's text and the checkbox label.

            :return: None
            """
            new_task = goal_entry.get().strip()

            if not new_task:
                messagebox.showwarning("Error", "Goal title is blank.")
                edit_window.lift()
                return

            if new_task == goal["task"]:
                messagebox.showwarning("Warning", "The goal title hasn't been changed!")
                edit_window.lift()
                return

            if any(g["task"] == new_task for g in self.month_goals):
                messagebox.showwarning("Warning", "Goal with this title already exists.")
                edit_window.lift()
                return

            old_task = None

            for g in self.month_goals:
                if g["task"] == goal["task"]:
                    old_task = g["task"]
                    g["task"] = new_task
                    break

            checkbox.config(text=new_task)
            asyncio.run(update_month_goal_on_server(self.year, self.month, new_task, old_task))
            edit_window.destroy()

        submit_button = tk.Button(edit_window, text="Save", command=submit_edit,
                                  font=MONTHLY_PLANS['toplevel_windows_font'])
        submit_button.pack(pady=5)
        submit_button.config(cursor="hand2")

        error_label = tk.Label(edit_window, text="", fg="red", font=MONTHLY_PLANS['error_label_font'])
        error_label.pack()

        edit_window.deiconify()

    def delete_goal(self, goal):
        """
        Deletes a goal from the task list and updates the UI.

        This function removes the specified goal from the list of goals stored in the server.
        After removing the goal, the UI is updated to reflect the changes, and the updated tasks
        are saved back to the server.

        :param goal: The goal object to be deleted. It represents a specific task in the task list.
        :return: None
        """
        self.month_goals = [g for g in self.month_goals if g["task"] != goal["task"]]

        self.display_goals()

        asyncio.run(delete_month_goal_from_server(self.year, self.month, goal))

    def add_new_goal(self):
        """
        Opens a dialog window to allow the user to enter and add a new goal.

        This function creates a top-level window where the user can enter a new goal.
        If the input is valid (not empty), the new goal is added to the task list for the current month,
        the UI is updated to display the new goal, and the updated tasks are saved to the server.

        :return: None
        """
        input_window = tk.Toplevel(self)
        input_window.title("Enter New Goal")
        input_window.withdraw()
        input_window.iconbitmap(APP['icon_path'])
        center_window_on_parent(self.main_window, input_window, 400, 100)

        goal_entry = tk.Entry(input_window, font=MONTHLY_PLANS['toplevel_windows_font'], width=30)
        goal_entry.pack(pady=10)
        goal_entry.bind("<Return>", lambda event: submit_goal())

        def submit_goal():
            """
            Submits the new goal if valid and adds it to the task list.

            :return: None
            """
            new_goal = goal_entry.get().strip()

            if not new_goal:
                messagebox.showerror("Blank Input", "Please enter a goal.")
                input_window.lift()
                return

            if any(goal["task"] == new_goal for goal in self.month_goals):
                messagebox.showerror("Duplicate Goal", "This goal already exists.")
                input_window.lift()
                return

            if new_goal:
                goal_data = {"task": new_goal, "done": False}

                self.month_goals.append(goal_data)

                self.display_goals()

                asyncio.run(add_month_goal_to_server(self.year, self.month, goal_data))

                input_window.destroy()
            else:
                error_label.config(text="Please enter a valid goal.")

        submit_button = tk.Button(input_window, text="Add Goal", command=submit_goal,
                                  font=MONTHLY_PLANS['toplevel_windows_font'])
        submit_button.pack(pady=5)
        submit_button.config(cursor="hand2")

        error_label = tk.Label(input_window, text="", fg="red", font=MONTHLY_PLANS['error_label_font'])
        error_label.pack()
        input_window.deiconify()

    def display_goals(self):
        """
        This method is responsible for displaying the list of goals for the current month in the GUI.
        It removes any existing checkboxes in the goals frame, checks if there are goals to display,
        and then creates checkboxes for each goal with an option to toggle the completion state.

        It also sets up a context menu for editing or deleting goals when the user right-clicks on a goal checkbox.


        Returns: None

        """
        for widget in self.goals_frame.winfo_children():
            if isinstance(widget, tk.Checkbutton):
                widget.destroy()

        if isinstance(self.month_goals, list) and len(self.month_goals) > 0:
            for i, goal in enumerate(self.month_goals):
                goal_var = tk.BooleanVar(value=goal["done"])
                checkbox = tk.Checkbutton(
                    self.goals_frame,
                    text=goal["task"],
                    variable=goal_var,
                    font=MONTHLY_PLANS['window_font'],
                    wraplength=200,
                    command=lambda g=goal, var=goal_var: self.toggle_goal_state(g, var),
                )
                checkbox.grid(row=i + 1, column=0, sticky="nw", padx=5)

                checkbox.config(cursor="hand2")

                menu = self.create_context_menu(goal, checkbox)
                checkbox.bind("<Button-3>", lambda event, m=menu: m.post(event.x_root, event.y_root))

                ToolTip(checkbox, text="Right click to edit/delete")

    def toggle_goal_state(self, goal, goal_var):
        """
        Toggles the completion state of a goal and updates the task data.

        This function updates the "done" status of the specified goal based on the state of the provided checkbox.
        When a user clicks a checkbox (marking a goal as done or undone), the goal's "done" field is updated accordingly.
        After updating the goal's state, the task data is saved to server.

        :param goal: The goal object whose state is being toggled. This is typically a dictionary containing the goal's data, including the "done" field.
        :param goal_var: The Boolean variable associated with the checkbox that represents the goal's completion state. It stores the current checked/unchecked status.
        :return: None
        """
        goal["done"] = goal_var.get()

        for g in self.month_goals:
            if g["task"] == goal["task"]:
                g["done"] = goal["done"]
                break

        asyncio.run(toggle_server_goal_state(self.year, self.month, goal))

    def add_reading_link(self, parent_frame, link):
        """
        Adds a clickable label to the specified parent frame that opens a reading link in the web browser.

        This function creates a label that displays a clickable "Click to view reading progress" text.
        When the label is clicked, it opens the provided link in the web browser.
        The label also supports right-clicking to open an edit window where the link can be modified.

        If the label already exists, it will be destroyed and recreated with the updated link,
        which can be loaded from the month data from server if no link is provided.

        :param parent_frame: The parent frame (a `tk.Frame`) where the clickable label will be added.
        :param link: The URL (string) to open when the label is clicked. If no link is provided, the link will be loaded from the month data.
        :return: None
        """
        if hasattr(self, 'reading_link_label'):
            self.reading_link_label.destroy()
            self.month_data["reading_link"] = link

        self.reading_link_label = tk.Label(parent_frame, text="Click to view\nreading progress", fg="black",
                                           cursor="hand2",
                                           bg=MONTHLY_PLANS['reading_label_bg'],
                                           height=10, width=20,
                                           relief=MONTHLY_PLANS['reading_relief'],
                                           highlightbackground=MONTHLY_PLANS['reading_highlightbackground'],

                                           highlightcolor=MONTHLY_PLANS['reading_highlightcolor'],

                                           font=MONTHLY_PLANS['reading_label_font'],
                                           )
        self.reading_link_label.grid(row=2, column=0, pady=5, sticky="n")
        self.reading_link_label.config(cursor="hand2")
        ToolTip(self.reading_link_label, "Right click to edit link")

        self.reading_link_label.bind("<Button-1>", lambda e: webbrowser.open(link))
        self.reading_link_label.bind("<Button-3>", lambda e: self.open_edit_window(e, link))

    def open_edit_window(self, event, current_link):
        """
        Opens a window to allow the user to edit the current reading link.

        This function creates a new window where the user can modify the reading link.
        The current reading link is pre-populated in a text entry field. Once the user
        enters a new link and clicks "Save", the link is updated both in the data
        and in the displayed label.

        :param event: The event object that triggered this function. This is used to associate
                      the original label (the clickable link) with the newly entered link.
        :param current_link: The current reading link to pre-populate the entry field.
                             This is the link that will be displayed initially in the edit window.
        :return: None
        """
        edit_window = tk.Toplevel(self)
        edit_window.withdraw()
        edit_window.title("Edit Reading Link")
        center_window_on_parent(self.main_window, edit_window, 400, 150)

        edit_window.iconbitmap(APP['icon_path'])

        font_style = MONTHLY_PLANS['toplevel_windows_font']

        label = tk.Label(edit_window, text="Enter new reading link:", font=font_style)
        label.pack(pady=10)

        entry = tk.Entry(edit_window, width=40, font=font_style)
        entry.insert(0, current_link)
        entry.pack(pady=5)
        entry.bind("<Return>", lambda event: save_link())

        def save_link():
            """
            Saves the new reading link, updates the label and the task data.

            This function is called when the user clicks the "Save" button or presses
            Enter. It updates the reading link in the data and the UI, and saves the
            changes to the server.

            :return: None
            """
            new_link = entry.get()

            if not new_link:
                messagebox.showerror("Error", f"Link can't be blank!")
                edit_window.lift()
                return

            if new_link == self.month_data["reading_link"]:
                messagebox.showerror("Error", f"Link hasn't been changed!")
                edit_window.lift()
                return

            if new_link:
                asyncio.run(update_reading_link_on_server(self.year, self.month, new_link))
                self.reading_link_label.unbind("<Button-1>")
                self.reading_link_label.config(text="Click to view\nreading progress",
                                               fg="black", cursor="hand2")
                event.widget.bind("<Button-1>", lambda e: webbrowser.open(new_link))
                self.add_reading_link(self.data_frame, new_link)
                self.month_data["reading_link"] = new_link

            edit_window.destroy()

        save_button = tk.Button(edit_window, text="Save", command=save_link, font=font_style)
        save_button.pack(pady=10)
        save_button.config(cursor="hand2")

        edit_window.deiconify()

    def add_source_label(self, path, text):
        """
        Adds a source label with navigation links to the current UI frame.

        This function creates a header frame containing a series of clickable elements
        (icons and text) that form a navigation path. Each element links to a different
        view or section of the application, such as Yearly Plans, Year, and Months. The
        source label is added at the top of the current window or panel.

        :param path: The path to the icon representing the current source or section.
                     This icon is displayed at the end of the navigation path.
        :param text: The text to be displayed as the label for the current section.
                     This text describes the content or source of the current section.

        :return: None. This function updates the UI by adding the header frame with
                 clickable navigation elements.
        """
        header_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        header_frame.pack(anchor="nw", pady=(5, 2), padx=10)

        create_icon_label(header_frame, ICONS_PATHS['yearly_plans'])

        first_clickable_label = create_clickable_text(header_frame, "Yearly plans /",
                                                      command=self.navigate_to_yearly_plans)

        create_icon_label(header_frame, ICONS_PATHS['year'])

        second_clickable_label = create_clickable_text(header_frame, f"{self.year} /",
                                                       command=lambda: self.navigate_to_year(self.year))

        create_icon_label(header_frame, ICONS_PATHS['months'])

        third_clickable_label = create_clickable_text(header_frame, "Months /",
                                                      command=lambda: self.navigate_to_months())

        create_icon_label(header_frame, path)

        create_text_label(header_frame, text)

        return first_clickable_label, second_clickable_label, third_clickable_label

    def navigate_to_months(self):
        """
        Go to months page.

        :return: None
        """
        self.main_window.bind_events()
        clear_canvas(self.parent)

        from src.months import Months
        months_frame = Months(self.parent, main_window=self.main_window, year=self.year)
        months_frame.pack(fill=tk.BOTH, expand=True)

        reset_canvas_view(self.main_window)

    def navigate_to_yearly_plans(self):
        """
        Return to Yearly plans.

        :return: None
        """
        self.main_window.bind_events()
        self.main_window.show_tab_content("yearly_plans")

    def navigate_to_year(self, year):
        """
        Navigates to the Year view by loading the corresponding year data and displaying it in the main window.

        This method is triggered when the user selects a specific year from the navigation path. It clears
        the current content, loads the year data from server, and then displays the Year view for the
        specified year.

        :param year: The year to navigate to. This parameter is used to load the year-specific data from server.
        :return: None. This method updates the UI by displaying the Year view for the selected year.
        """
        self.main_window.bind_events()
        clear_canvas(self.parent)

        from src.year import Year
        year_frame = Year(self.parent, main_window=self.main_window, year=year)
        year_frame.pack(fill=tk.BOTH, expand=True)

        reset_canvas_view(self.main_window)
