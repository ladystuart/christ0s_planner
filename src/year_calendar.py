from config.imports import *
from tkcalendar import Calendar as TkCalendar
from datetime import datetime
import datetime as mycalendardatestart
from config.settings import CALENDAR
from config.utils import add_source_label_third_level as add_source_label_calendar, load_icon_image


async def load_calendar_tasks(year):
    """
    Fetches the calendar tasks for a specific year from the server.

    Args:
        year (str): The year for which the calendar tasks are to be fetched.

    Returns:
        dict: A JSON response containing the calendar tasks for the specified year.
              The response format is assumed to be a dictionary containing the tasks.

    Raises:
        HTTPError: If the request to the server fails or the response status code is not 200.
    """
    params = {"year": year}

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{SERVER_URL}/get_calendar_tasks", params=params, ssl=SSL_ENABLED) as response:
            response.raise_for_status()
            return await response.json()


async def add_task_to_server(selected_date: str, task: str):
    """
    Adds a new task to the server's calendar.

    Args:
        selected_date (str): The date for which the task is being added, in either 'MM/DD/YY' or 'YYYY-MM-DD' format.
        task (str): The description of the task to be added.

    Returns:
        dict: A JSON response from the server confirming the addition of the task.

    Raises:
        ValueError: If the date format is incorrect.
        HTTPError: If the request to the server fails or the response status code is not 200.
    """
    try:
        if "/" in selected_date:
            date_obj = mycalendardatestart.datetime.strptime(selected_date, "%m/%d/%y").date()
        else:
            date_obj = mycalendardatestart.datetime.strptime(selected_date, "%Y-%m-%d").date()

    except ValueError:
        print("Error: date format error. Expected 'YYYY-MM-DD'")
        return

    url = f"{SERVER_URL}/add_calendar_task"
    data = {
        "year": date_obj.year,
        "date": date_obj.isoformat(),
        "event": task
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, ssl=SSL_ENABLED) as response:
            response.raise_for_status()
            return await response.json()


async def delete_task_from_server(formatted_date, task_to_delete, year):
    """
    Deletes the task from the server by sending a DELETE request to /delete_calendar_task.

    :return: None
    """
    task_date = mycalendardatestart.datetime.strptime(formatted_date, "%Y-%m-%d").date()

    # Prepare data to send
    task_data = {
        "year": year,
        "date": task_date.isoformat(),
        "event": task_to_delete,
    }

    # Send the DELETE request to the server
    async with aiohttp.ClientSession() as session:
        async with session.delete(f"{SERVER_URL}/delete_calendar_task",
                                  json=task_data, ssl=SSL_ENABLED) as response:
            response.raise_for_status()
            return await response.json()


class Calendar(tk.Frame):
    """
    A calendar widget for managing tasks for a specific year. It includes functionalities
    such as viewing, adding, and deleting tasks for any given year, as well as displaying
    a calendar interface with a banner and navigation options.

    Attributes:
    - main_window (tk.Tk): The main application window.
    - year (int): The year that the calendar represents.
    - parent (tk.Widget): The parent widget (usually a window or frame).
    - tasks (list): A list of tasks loaded from server.
    """
    def __init__(self, parent, main_window, year):
        """
        Initializes the Calendar widget.

        :param parent: The parent widget that will contain this calendar frame.
        :param main_window: The main window of the application.
        :param year: The year that this calendar represents.
        """
        super().__init__(parent)
        self.configure(bg=INTERFACE['bg_color'])
        self.main_window = main_window
        self.main_window.disable_buttons()
        self.year = year
        self.parent = parent
        self.main_window.check_scrollbar()

        self.tasks = asyncio.run(load_calendar_tasks(self.year))

        self.first_clickable_label, self.second_clickable_label = (add_source_label_calendar
                                                                   (self,
                                                                    icon_path_1=ICONS_PATHS['yearly_plans'],
                                                                    clickable_text="Yearly plans /",
                                                                    click_command_1=self.navigate_to_yearly_plans,
                                                                    icon_path_2=ICONS_PATHS['year'],
                                                                    year_name=f"{self.year} /",
                                                                    icon_path_3=ICONS_PATHS['calendar'],
                                                                    text=PAGES_NAMES['calendar'],
                                                                    click_command_2=lambda:
                                                                    self.navigate_to_year(self.year)))

        self.first_clickable_label["state"] = "disabled"
        self.second_clickable_label["state"] = "disabled"

        # Banner add
        self.banner_label, self.banner_image_original = add_banner(
            self,
            banner_path=BANNER_PATHS['calendar'],
            bg_color=INTERFACE['bg_color']
        )

        # resize_banner
        if self.banner_label and self.banner_image_original:
            self.bind("<Configure>", lambda event: resize_banner(
                self,
                self.banner_label,
                self.banner_image_original
            ))

        self.icon_photo = asyncio.run(load_icon_image(SERVER_URL, ICONS_PATHS['calendar'], VERIFY_ENABLED))

        add_icon_and_label(self, text=PAGES_NAMES['calendar'], icon_path=ICONS_PATHS['calendar'],
                           bg_color=INTERFACE['bg_color'])
        add_separator(parent=self, color=INTERFACE['separator'])

        # Add calendar
        self.add_calendar_widget()

        self.add_task_button = tk.Button(self, text="Add Task", command=self.add_task,
                                         font=CALENDAR['buttons_font'], bg=CALENDAR['add_button_bg'])
        self.add_task_button.pack(side="left", padx=10, pady=10)
        self.add_task_button.config(cursor="hand2")

        # View tasks button
        self.view_tasks_button = tk.Button(self, text="View Tasks", command=self.view_tasks,
                                           font=CALENDAR['buttons_font'])
        self.view_tasks_button.pack(side="left", padx=10, pady=10)
        self.view_tasks_button.config(cursor="hand2")

        # Delete button
        self.delete_task_button = tk.Button(self, text="Delete Task", command=self.delete_task,
                                            font=CALENDAR['buttons_font'], bg=CALENDAR['delete_button_color'])
        self.delete_task_button.pack(side="left", padx=10, pady=10)
        self.delete_task_button.config(cursor="hand2")

        self.mark_existing_task_dates()

        self.main_window.enable_buttons()
        self.first_clickable_label["state"] = "normal"
        self.second_clickable_label["state"] = "normal"

    def mark_existing_task_dates(self):
        """
        Iterates over the existing tasks and marks the corresponding dates on the calendar.

        For each task, it retrieves the date and event details, formats the date from 'YYYY-MM-DD'
        to 'MM/DD/YYYY' format, and adds a marker on the calendar to indicate the task.

        Returns:
            None
        """
        for task in self.tasks:
            date = task["date"]
            event = task["event"]

            date_obj = datetime.strptime(date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%m/%d/%Y")

            self.add_task_marker(formatted_date, event)

    def delete_task(self):
        """
        Deletes a task from the calendar on the selected date. If no tasks are present
        for the selected date, a message box will inform the user. If a task exists,
        the user is prompted to select which task to delete. After deletion, if no tasks
        remain for that date, the date is removed from the calendar.

        :return: None
        """
        selected_date = self.my_calendar.get_date()

        selected_date_obj = datetime.strptime(selected_date, "%m/%d/%y").date()

        formatted_date = selected_date_obj.strftime("%Y-%m-%d")

        tasks_on_date = [task for task in self.tasks if task["date"] == formatted_date]

        if tasks_on_date:
            # Toplevel window
            task_to_delete = self.show_task_selection_dialog(tasks_on_date)

            if task_to_delete:
                # Delete the task from the list
                self.tasks = [task for task in self.tasks if
                              not (task["date"] == formatted_date and task["event"] == task_to_delete)]

                # If no tasks are left for the selected date, remove it from the calendar
                tasks_on_date = [task for task in self.tasks if task["date"] == formatted_date]
                if not tasks_on_date:
                    self.my_calendar.calevent_remove(date=selected_date_obj)
                asyncio.run(delete_task_from_server(formatted_date, task_to_delete, self.year))
        else:
            messagebox.showinfo("Warning", f"No tasks found for {selected_date}")

    def show_task_selection_dialog(self, tasks):
        """
        Displays a dialog to the user for selecting a task to delete. The dialog shows a list of tasks
        that the user can select from. Once a task is selected and the 'Delete' button is clicked,
        the selected task is returned.

        :param tasks: A list of tasks (strings) for the selected date that the user can choose from.
        :return: The selected task (string), or None if no task was selected.
        """
        dialog = tk.Toplevel(self)
        dialog.withdraw()
        dialog.title("Select Task to Delete")

        # Parameters
        base_height = 100  # Mon height
        task_height = 20
        max_visible_tasks = 6
        visible_tasks = min(len(tasks), max_visible_tasks)

        window_height = base_height + visible_tasks * task_height
        window_width = 400

        center_window_on_parent(self.main_window, dialog, window_width, window_height)
        dialog.iconbitmap(APP['icon_path'])

        # Create task list
        listbox = tk.Listbox(dialog, height=visible_tasks, selectmode=tk.SINGLE, font=CALENDAR['toplevel_windows_font'])
        for task in tasks:
            listbox.insert(tk.END, task['event'])  # Insert only the event
        listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        selected_task = None

        def on_select():
            """
            If task selected.

            :return: None
            """
            nonlocal selected_task
            selected_task = listbox.get(tk.ACTIVE)
            dialog.destroy()

        # Delete confirm button
        select_button = tk.Button(dialog, text="Delete", command=on_select, font=CALENDAR['toplevel_windows_font'])
        select_button.pack(pady=5)
        select_button.config(cursor="hand2")

        dialog.deiconify()

        dialog.wait_window()

        return selected_task

    def view_tasks(self):
        """
        Displays a dialog showing all tasks for the selected date on the calendar.
        If there are no tasks for the selected date, a message is displayed saying so.

        :return: None
        """
        selected_date = self.my_calendar.get_date()

        formatted_date = datetime.strptime(selected_date, "%m/%d/%y").strftime("%Y-%m-%d")

        tasks = [task["event"] for task in self.tasks if task.get("date") == formatted_date]

        tasks_window = tk.Toplevel(self)
        tasks_window.withdraw()

        # Calculate window
        base_height = 30  # Min height
        task_height = 30
        window_height = base_height + len(tasks) * task_height
        window_width = 400

        center_window_on_parent(self.main_window, tasks_window, window_width, window_height)

        tasks_window.title(f"Tasks for {formatted_date}")
        # Add icon
        tasks_window.iconbitmap(APP['icon_path'])

        if not tasks:
            label = tk.Label(tasks_window, text="No tasks for this date.", font=CALENDAR['toplevel_windows_font'])
            label.pack(padx=20, pady=20)
        else:
            # Show all tasks
            for task in tasks:
                label = tk.Label(tasks_window, text=task, font=CALENDAR['toplevel_windows_font'])
                label.pack(padx=20, pady=5)

        tasks_window.deiconify()

    def add_calendar_widget(self):
        """
        Adds the calendar widget to the user interface and highlights the days that have tasks.

        :return: None
        """
        # Get the current date
        today = mycalendardatestart.date.today()

        current_month = today.month
        current_day = today.day

        # Add calendar
        self.my_calendar = TkCalendar(self, selectmode="day", year=self.year, month=current_month, day=current_day)
        self.my_calendar.pack(fill="both", expand=True, padx=10, pady=10)

        # Highlight tasks
        self.highlight_task_days()

    def highlight_task_days(self):
        """
        Highlights the days on the calendar that have tasks associated with them.

        It iterates over all the dates in the `self.tasks["calendar"]` dictionary,
        and for each date with tasks, it highlights the corresponding day on the calendar.

        :return: None
        """
        if "calendar" in self.tasks:
            self.my_calendar.tag_config("popup_highlight", background=CALENDAR['calendar_selected_task_bg'],
                                        foreground=CALENDAR['calendar_selected_task_text'])

            for date_str, tasks in self.tasks["calendar"].items():
                if tasks:
                    if len(date_str.split('/')[2]) == 2:
                        date_str = date_str[:-2] + "20" + date_str[-2:]
                    try:
                        date_obj = datetime.strptime(date_str, "%m/%d/%Y").date()
                        self.my_calendar.calevent_create(
                            date_obj, "Task", tags=(f"task_{date_str}", "popup_highlight")
                        )
                    except ValueError as e:
                        print(f"Error parsing date {date_str}: {e}")

    def add_task(self):
        """
        Opens a custom input window to add a new task for the selected date on the calendar.

        The user can enter a task, which is associated with a specific date selected from the calendar.
        The task is then added to the calendar and saved to the task list.

        :return: None
        """
        selected_date = self.my_calendar.get_date()

        # Convert the selected date to the desired format (DD.MM.YY)
        formatted_date = datetime.strptime(selected_date, "%m/%d/%y").strftime("%d.%m.%y")

        # Create a custom input window for the task
        task_window = tk.Toplevel(self)
        task_window.withdraw()
        task_window.title(f"Enter task for {formatted_date}")
        center_window_on_parent(self.main_window, task_window, 400, 200)

        # Set the window icon
        icon_image = Image.open(APP['icon_path'])  # Replace with the path to your icon
        icon_photo = ImageTk.PhotoImage(icon_image)
        task_window.iconphoto(True, icon_photo)

        # Label for the header
        label = tk.Label(task_window, text=f"Enter task for {formatted_date}:", font=CALENDAR['toplevel_windows_font'])
        label.pack(padx=20, pady=10)

        # Task entry field
        task_entry = tk.Entry(task_window, font=CALENDAR['toplevel_windows_font'], width=30)
        task_entry.pack(padx=20, pady=10)

        # Bind the Enter key to confirm
        task_entry.bind("<Return>", lambda event: self.on_confirm(task_entry, selected_date, task_window))

        # Confirm button
        confirm_button = tk.Button(task_window, text="Add Task",
                                   command=lambda: self.on_confirm(task_entry, selected_date, task_window),
                                   font=CALENDAR['toplevel_windows_font'])
        confirm_button.pack(pady=10)
        confirm_button.config(cursor="hand2")

        # Cancel button
        cancel_button = tk.Button(task_window, text="Cancel", command=task_window.destroy,
                                  font=CALENDAR['toplevel_windows_font'])
        cancel_button.pack(pady=10)
        cancel_button.config(cursor="hand2")

        task_window.deiconify()

    def on_confirm(self, task_entry, selected_date, task_window):
        """
        Handles the confirmation of a task addition. It retrieves the task from the input field,
        adds it to the task list for the selected date, updates the task in the JSON file, and closes the window.

        :param task_entry: The Entry widget containing the task description entered by the user.
        :param selected_date: The date for which the task is being added.
        :param task_window: The window where the task is being entered.
        :return: None
        """
        task = task_entry.get()
        if task:
            # Convert selected_date to 'YYYY-MM-DD' format
            selected_date_obj = datetime.strptime(selected_date, "%m/%d/%y").strftime("%Y-%m-%d")

            # Check if the task already exists for the selected date
            existing_tasks = [t['event'] for t in self.tasks if t['date'] == selected_date_obj]

            if task in existing_tasks:
                # Show a messagebox warning that the task already exists
                messagebox.showwarning("Error", "This task already exists for the selected date.")
                task_window.lift()
            else:
                # Add the task since it doesn't exist
                self.add_task_marker(selected_date, task)
                asyncio.run(add_task_to_server(selected_date, task))

                new_task = {
                    "date": selected_date_obj,
                    "event": task
                }
                self.tasks.append(new_task)  # Adding the new task

                task_window.destroy()

    def add_task_marker(self, date, task):
        """
        Adds a marker (event) for a specific task on the calendar for the given date. This method creates a visual marker
        on the calendar that corresponds to the task on the specified date.

        :param date: The date for the task in the format "mm/dd/yyyy".
        :param task: The task description that will be displayed as an event on the calendar.
        :return: None
        """
        if len(date.split('/')[2]) == 2:
            date = date[:-2] + "20" + date[-2:]

        date_obj = datetime.strptime(date, "%m/%d/%Y").date()

        # Create calendar event
        event_id = self.my_calendar.calevent_create(date_obj, task, "task")

        self.my_calendar.tag_config("popup_highlight", background=CALENDAR['calendar_selected_task_bg'],
                                    foreground=CALENDAR['calendar_selected_task_text'])
        self.my_calendar.calevent_create(date_obj, task, tags=("task", "popup_highlight"))

    def navigate_to_yearly_plans(self):
        """
        Return to Yearly plans.

        :return: None
        """
        self.main_window.bind_events()
        self.main_window.show_tab_content("yearly_plans")

    def navigate_to_year(self, year):
        """
        Navigate back to the year view by switching to the Year frame.
        This will clear the current canvas and load the year view,
        displaying the selected year's information from the respective JSON file.

        :param year: The year to navigate to (e.g., "2024").
        :return: None
        """
        self.main_window.bind_events()
        clear_canvas(self.parent)

        from src.year import Year
        year_frame = Year(self.parent, main_window=self.main_window, year=year)
        year_frame.pack(fill=tk.BOTH, expand=True)

        reset_canvas_view(self.main_window)
