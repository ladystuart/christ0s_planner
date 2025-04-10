from datetime import datetime
from tkcalendar import Calendar
from config.imports import *
from config.settings import HABIT_TRACKER
from config.tooltip import ToolTip
from config.utils import add_source_label_third_level as add_source_label_habit_tracker, add_icon_image
from datetime import date as setcalendardate


async def get_tasks_from_server(year):
    """
    Fetches habit tracker tasks for a given year from the server.

    Args:
        year (int): The year for which habit tracker tasks are requested.

    Returns:
        dict: The JSON response containing habit tracker tasks if the request is successful.

    Raises:
        Exception: If the request fails or returns a non-200 status code.
    """
    params = {"year": year}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{SERVER_URL}/get_habit_tracker",
                                   params=params, ssl=SSL_ENABLED) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Error: {response.status}")
        except Exception as e:
            print(f"Error sending request: {e}")


async def send_new_start_date_to_server(year, selected_date):
    """
    Sends an updated start date for a given year to the server.

    Args:
        year (int): The year for which the start date is being updated.
        selected_date (datetime): The new start date to be set.

    Returns:
        None

    Raises:
        Exception: If the request fails due to a network issue or a server error.
    """
    selected_date = selected_date.date()

    payload = {
        "year": int(year),
        "date": selected_date.isoformat()
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{SERVER_URL}/update_start_date",
                                    json=payload, ssl=SSL_ENABLED) as response:
                response_text = await response.text()
                if response.status != 200:
                    print(f"Error: Failed to update: {response_text}")
        except Exception as e:
            print(f"Error sending update request: {e}")


async def send_task_update_to_server(year, day, task, status):
    """
    Sends an update for a specific habit tracker task to the server.

    Args:
        year (int): The year associated with the habit tracker entry.
        day (str): The specific day for which the task is being updated (format: "YYYY-MM-DD").
        task (str): The name or description of the task.
        status (bool): The completion status of the task (True for completed, False for not completed).

    Returns:
        None

    Raises:
        Exception: If the request fails due to a network issue or a server error.
    """
    data = {
        "year": int(year),
        "day": day,
        "task": task,
        "completed": status
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{SERVER_URL}/update_habit_tracker_task_state",
                                    json=data, ssl=SSL_ENABLED) as response:
                if response.status != 200:
                    print(f"Error sending data: {response.status}")
        except Exception as e:
            print(f"Server connection error: {e}")


async def refresh_server_data(year):
    """
    Sends a request to the server to refresh the habit tracker states for a given year.

    Args:
        year (int): The year for which habit tracker data should be refreshed.

    Returns:
        None

    Raises:
        Exception: If the request fails due to a network issue or a server error.
    """
    params = {"year": int(year)}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{SERVER_URL}/refresh_habit_tracker_states",
                                    json=params, ssl=SSL_ENABLED) as response:
                if response.status != 200:
                    raise Exception(f"Error: {response.status}")
        except Exception as e:
            print(f"Error sending request: {e}")


async def edit_server_habit_tracker(year, start_date, day, tasks):
    """
    Sends a request to update the habit tracker data on the server.

    Args:
        year (int): The year for which the habit tracker should be updated.
        start_date (datetime.date): The starting date of the habit tracking period.
        day (str): The specific day of the week to update.
        tasks (list): A list of tasks associated with the specified day.

    Returns:
        dict or None: The server's response as a dictionary if the request is successful, otherwise None.

    Raises:
        aiohttp.ClientError: If there is an issue with the request.
    """
    task_data = {
        "year": int(year),
        "start_date": start_date.isoformat(),
        "day": day,
        "tasks": tasks
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{SERVER_URL}/edit_habit_tracker",
                                    json=task_data, ssl=SSL_ENABLED) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            print(f"Error during request: {e}")
        return None


class HabitTracker(tk.Frame):
    """
    The HabitTracker class represents the frame for the habit tracking page.
    This frame displays habit tracking information, allows navigation to other pages
    such as "Yearly Plans", and manages UI components related to habit tracking.
    """
    def __init__(self, parent, main_window, year):
        """
        Initializes the HabitTracker frame by setting up the background, loading the habit tracker data,
        and configuring the navigation elements and other interface components.

        :param parent: The parent widget where this frame will be placed (usually the main window).
        :param main_window: The main window of the application, used to handle scrollbars and other global actions.
        :param year: The specific year to display in the habit tracker, affecting data and UI elements.
        """
        super().__init__(parent)
        self.configure(bg=INTERFACE['bg_color'])
        self.main_window = main_window
        self.main_window.disable_buttons()
        self.year = year
        self.parent = parent
        self.main_window.check_scrollbar()

        self.habit_tracker = asyncio.run(get_tasks_from_server(self.year))

        self.first_clickable_label, self.second_clickable_label = (add_source_label_habit_tracker
                                                                   (self,
                                                                    icon_path_1=ICONS_PATHS['yearly_plans'],
                                                                    clickable_text="Yearly plans /",
                                                                    click_command_1=self.navigate_to_yearly_plans,
                                                                    icon_path_2=ICONS_PATHS['year'],
                                                                    year_name=f"{self.year} /",
                                                                    icon_path_3=ICONS_PATHS['habit_tracker'],
                                                                    text=PAGES_NAMES['habit_tracker'],
                                                                    click_command_2=lambda:
                                                                    self.navigate_to_year(self.year)))

        self.first_clickable_label["state"] = "disabled"
        self.second_clickable_label["state"] = "disabled"

        self.icon_image_original = asyncio.run(add_icon_image(ICONS_PATHS['habit_tracker']))

        self.add_icon_and_label(self, PAGES_NAMES['habit_tracker'])

        add_separator(parent=self, color=INTERFACE['separator'])

        self.add_quote_and_image()

        self.main_window.enable_buttons()
        self.first_clickable_label["state"] = "normal"
        self.second_clickable_label["state"] = "normal"

    def edit_date(self):
        """
        Opens a new window allowing the user to select a new date for the 'Week Starting Date'.
        The user can pick a date from a calendar widget, and upon saving, the new date is processed.

        :return: None
        """
        self.date_window = tk.Toplevel(self)
        self.date_window.withdraw()
        self.date_window.title("Edit Week Starting Date")

        # Center window
        center_window_on_parent(self.main_window, self.date_window, 400, 300)
        self.date_window.iconbitmap(APP['icon_path'])

        # Add calendar
        calendar = Calendar(self.date_window, selectmode='day', date_pattern='yyyy-mm-dd')
        # Get today's date
        today = setcalendardate.today()

        # Set the calendar to today's date
        calendar.selection_set(today)
        calendar.pack(padx=20, pady=20)

        # Save button
        save_button = tk.Button(self.date_window, text="Save Date", font=HABIT_TRACKER['toplevel_windows_font'],
                                command=lambda: self.save_new_date(calendar.get_date()))
        save_button.pack(pady=10)
        save_button.config(cursor="hand2")

        self.date_window.deiconify()

    def save_new_date(self, selected_date):
        """
        Saves the newly selected date as the 'Week Starting' date and updates the corresponding data
        on server. It also updates the 'habit_tracker' section, if necessary, to reflect the new week starting date.

        :param selected_date: The date selected by the user, passed as a string in the format 'yyyy-mm-dd'.
        :return: None
        """
        try:
            old_key = list(self.habit_tracker.keys())[0]

            selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
            new_key = f"Week starting {selected_date_obj.strftime('%Y-%m-%d')}"

            self.habit_tracker[new_key] = self.habit_tracker.pop(old_key)

            asyncio.run(send_new_start_date_to_server(self.year, selected_date_obj))

            self.date_window.destroy()

            # Widget refresh
            self.refresh_habit_tracker()

            messagebox.showinfo("Success", f"Date updated to {new_key}")

        except Exception as e:
            messagebox.showerror("Error", f"Error while saving new date: {e}")

    def refresh_habit_tracker(self):
        """
        Refreshes the habit tracker interface by clearing the current contents of the left frame
        and re-adding the habit tracker demo and the associated buttons.

        :return: None
        """
        if hasattr(self, 'tracker_frame'):
            for widget in self.left_frame.winfo_children():
                widget.destroy()

            self.add_habit_tracker(self.left_frame)

            # Create buttons
            self.create_habit_tracker_buttons(self.left_frame)

    def create_habit_tracker_buttons(self, parent_frame):
        """
        Creates and adds buttons to the provided parent frame. These buttons include:
        - Edit Date button: Allows the user to edit the start date for the habit tracker.
        - Edit Habit Tracker button: Allows the user to edit the habit tracker itself.
        - Refresh Habit Tracker button: Refreshes the habit tracker to update the data or view.

        :param parent_frame: The Tkinter frame (or container) where the buttons will be placed.
        :return: None
        """
        # Delete button
        date_edit = tk.Button(parent_frame, text="Edit Date", font=HABIT_TRACKER['buttons_font'], width=20,
                              command=self.edit_date)
        date_edit.pack(pady=5, anchor="center")
        date_edit.config(cursor="hand2")

        # Tracker edit button
        button_edit = tk.Button(parent_frame, text="Edit Habit Tracker", font=HABIT_TRACKER['buttons_font'], width=20,
                                command=self.edit_habit_tracker)
        button_edit.pack(pady=5, anchor="center")
        button_edit.config(cursor="hand2")

        # Habit tracker refresh button
        button_refresh = tk.Button(parent_frame, text="Refresh Habit Tracker", font=HABIT_TRACKER['buttons_font'],
                                   width=20,
                                   command=self.refresh_tasks)
        button_refresh.pack(pady=5, anchor="center")
        button_refresh.config(cursor="hand2")

    def edit_habit_tracker(self):
        """
        Opens a window to edit the habit tracker for the current week. The user can modify the tasks for each day
        of the week. Tasks can be added as a comma-separated list, and changes will be saved to the server.

        :return: None
        """
        self.edit_window = tk.Toplevel(self)
        self.edit_window.withdraw()
        self.edit_window.title("Edit Habit Tracker")

        center_window_on_parent(self.main_window, self.edit_window, 500, 310)
        self.edit_window.iconbitmap(APP['icon_path'])

        edit_frame = tk.Frame(self.edit_window, bg=INTERFACE['bg_color'])
        edit_frame.pack(padx=10, pady=5)

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # Get key
        start_date_key = self.get_start_date()

        def save_changes(day, task_entry):
            """
            Saves the tasks for a specific day into the habit tracker and updates the server data.

            :param day: The day of the week (e.g., "Monday")
            :param task_entry: The Entry widget where the user inputted the tasks for the day
            :return: None
            """
            task_text = task_entry.get()  # Get input text

            if task_text:
                tasks_to_server = [task.strip() for task in task_text.split(',') if task.strip()]

                if len(tasks_to_server) != len(set(tasks_to_server)):
                    messagebox.showerror("Error", "Duplicate tasks are not allowed!")
                    self.edit_window.lift()
                    return

                existing_tasks = {task["task"]: task["completed"] for task in
                                  self.habit_tracker.get(start_date_key, {}).get(day, [])}

                tasks = []
                for task in task_text.split(','):
                    task = task.strip()
                    if task:
                        tasks.append({"task": task, "completed": existing_tasks.get(task, False)})

                self.habit_tracker.setdefault(start_date_key, {})[day] = tasks
            else:
                self.habit_tracker.setdefault(start_date_key, {})[day] = []
                tasks_to_server = []

            parts = start_date_key.split()
            parts = parts[-1]
            date_obj = datetime.strptime(parts, "%Y-%m-%d").date()
            asyncio.run(edit_server_habit_tracker(self.year, date_obj, day, tasks_to_server))

            # Update tracker
            self.update_habit_tracker_frame()

        # Show tasks
        for row, day in enumerate(days):
            day_label = tk.Label(edit_frame, text=day, font=HABIT_TRACKER['toplevel_windows_title_font'],
                                 bg=INTERFACE['bg_color'], fg=HABIT_TRACKER['toplevel_windows_font_color'])
            day_label.grid(row=row, column=0, padx=5, pady=5)

            current_tasks = self.habit_tracker.get(start_date_key, {}).get(day, [])

            task_text = ", ".join([task["task"] for task in current_tasks])

            task_entry = tk.Entry(edit_frame, font=("Arial", 12), bg=HABIT_TRACKER['entry_bg_color'],
                                  fg=HABIT_TRACKER['toplevel_windows_font_color'], width=30)
            task_entry.insert(0, task_text)
            task_entry.grid(row=row, column=1, padx=5, pady=5)
            ToolTip(task_entry, "Enter items separated by commas")

            # Capturing the value of 'day' for the lambda
            task_entry.bind("<Return>", lambda event, day=day, task_entry=task_entry: save_changes(day, task_entry))

            # Save button
            save_button = tk.Button(edit_frame, text="Save", font=HABIT_TRACKER['toplevel_windows_font'],
                                    command=lambda day=day, task_entry=task_entry: save_changes(day, task_entry))
            save_button.grid(row=row, column=2, padx=5, pady=5)
            save_button.config(cursor="hand2")

        self.edit_window.deiconify()

    def add_quote_and_image(self):
        """
        This method sets up the layout for displaying the habit tracker, an image, and a motivational quote.
        It arranges components in a split layout with a tracker on the left and the image with a quote on the right.

        :return: None
        """
        main_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        main_frame.pack(pady=5)

        # Left frame w tracker
        self.left_frame = tk.Frame(main_frame, bg=HABIT_TRACKER['left_frame_bg'])
        self.left_frame.pack(side=tk.LEFT, padx=2, pady=5, fill=tk.BOTH, expand=True)

        self.add_habit_tracker(self.left_frame)

        # Add buttons
        self.create_habit_tracker_buttons(self.left_frame)

        # Right frame w image and quote
        right_frame = tk.Frame(main_frame, bg=INTERFACE['bg_color'])
        right_frame.pack(side=tk.RIGHT, padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Add image
        add_image_to_grid(right_frame, HABIT_TRACKER['image_link'], row=0, column=0, height=500,
                          width=350,
                          rowspan=1, columnspan=1)
        right_frame.grid_anchor("e")

        # Quote frame
        quote_frame = tk.Frame(right_frame, bg=INTERFACE['bg_color'])
        quote_frame.grid(row=1, column=0, sticky="e", pady=(10, 0), padx=10)

        # Vertical line
        line = tk.Canvas(quote_frame, width=2, bg=INTERFACE['separator'], height=100)
        line.grid(row=0, column=0, padx=(0, 10), sticky="e", columnspan=1)

        # Quote text
        quote_text = HABIT_TRACKER['quote_text']
        label_quote = tk.Label(quote_frame, text=quote_text, font=HABIT_TRACKER['quote_font'],
                               bg=INTERFACE['bg_color'], wraplength=HABIT_TRACKER['quote_wraplength'])
        label_quote.grid(row=0, column=1, sticky="e", padx=10)

    def refresh_tasks(self):
        """
        This method resets the completion status of all tasks in the habit tracker by setting each task's 'completed' field to False.
        It then saves the updated tasks to the JSON file and updates the habit tracker interface.

        :return: None
        """
        try:
            for week_key in self.habit_tracker:
                for day_key in self.habit_tracker[week_key]:
                    for task in self.habit_tracker[week_key][day_key]:
                        task['completed'] = False

            asyncio.run(refresh_server_data(self.year))

            self.update_habit_tracker_frame()

        except Exception as e:
            print(f"Error refreshing habit tracker: {e}")

    def update_habit_tracker_frame(self):
        """
        This method is responsible for refreshing the habit tracker frame by clearing all existing widgets,
        re-adding the habit tracker demo (display), and updating the interface with buttons and other components.

        :return: None
        """
        if hasattr(self, 'tracker_frame'):
            for widget in self.left_frame.winfo_children():
                widget.destroy()

            self.add_habit_tracker(self.left_frame)

            # Add buttons
            self.create_habit_tracker_buttons(self.left_frame)

            # Lift the edit_window if it exists and is valid
            if hasattr(self, 'edit_window') and isinstance(self.edit_window, tk.Toplevel):
                self.edit_window.lift()  # Bring the edit window to the front

    def get_start_date(self):
        """
        This method retrieves the first start date (key) from the habit tracker JSON data.
        It looks for keys that start with "Week starting" and returns the first such key found.

        :return: The first key starting with 'Week starting' if found, otherwise None.
        """
        if self.habit_tracker:
            date_keys = [key for key in self.habit_tracker.keys() if key.startswith("Week starting")]

            if date_keys:
                return date_keys[0]
            else:
                print("No keys 'Week starting'.")
                return None
        else:
            print("No data")
            return None

    def add_habit_tracker(self, parent_frame):
        """
        This method is used to create and display a demo habit tracker UI within the specified parent frame.
        It retrieves habit tracking data from a JSON file, constructs a layout of the habit tracker for each day of the week,
        and displays checkboxes for each task within the week. Each task can be marked as completed via checkboxes.

        :param parent_frame: The parent frame where the habit tracker UI will be displayed.
        :return: None
        """
        if not self.habit_tracker:
            return

        # Get week date
        start_date = self.get_start_date()
        if not start_date:
            return

        self.tracker_frame = tk.Frame(parent_frame, bg=HABIT_TRACKER['habit_tracker_frame_bg'], relief=tk.GROOVE, bd=2)
        self.tracker_frame.pack(padx=10, pady=5)

        week_label = tk.Label(self.tracker_frame,
                              text=f"{start_date}",
                              font=HABIT_TRACKER['week_starting_label_font'],
                              bg=HABIT_TRACKER['week_starting_label_bg'],
                              fg=HABIT_TRACKER['week_starting_font_color'],
                              bd=2,
                              relief=HABIT_TRACKER['week_starting_label_relief'])
        week_label.grid(row=0, column=0, columnspan=4, pady=10, padx=5)

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # Get start date
        habit_data = self.habit_tracker.get(start_date, {})

        row = 1
        self.checkboxes_state = {}  # Checkbox dict

        for i in range(0, len(days), 2):
            day1 = days[i]
            day2 = days[i + 1] if i + 1 < len(days) else None

            day1_frame = tk.Frame(self.tracker_frame, bg=HABIT_TRACKER['day_frame_bg'])
            day1_frame.grid(row=row, column=0, padx=5, pady=5, sticky="nsew")

            day1_label = tk.Label(day1_frame, text=f"{day1}", font=HABIT_TRACKER['day_label_title_font'],
                                  bg=HABIT_TRACKER['day_label_bg'], fg=HABIT_TRACKER['day_label_font_color'])
            day1_label.pack(pady=5, anchor="w")

            if day1 in habit_data:

                sorted_tasks = sorted(habit_data[day1], key=lambda x: x["task"].lower())  # Sorting tasks

                for task_info in sorted_tasks:
                    task = task_info["task"]
                    completed = task_info["completed"]
                    checkbox_var = tk.BooleanVar(value=completed)
                    checkbox = tk.Checkbutton(day1_frame, text=task, font=HABIT_TRACKER['checkbox_font'],
                                              bg=HABIT_TRACKER['day_label_bg'],
                                              fg=HABIT_TRACKER['day_label_font_color'],
                                              variable=checkbox_var,
                                              command=lambda task=task, day=day1, checkbox_var=checkbox_var:
                                              self.update_task_state(task, day, checkbox_var))
                    checkbox.pack(anchor="w")
                    checkbox.config(cursor="hand2")

                    self.checkboxes_state[(day1, task)] = checkbox_var

            if day2:
                day2_frame = tk.Frame(self.tracker_frame, bg=HABIT_TRACKER['day_frame_bg'])
                day2_frame.grid(row=row, column=1, padx=5, pady=5, sticky="nsew")

                day2_label = tk.Label(day2_frame, text=f"{day2}", font=HABIT_TRACKER['day_label_title_font'],
                                      bg=HABIT_TRACKER['day_label_bg'], fg=HABIT_TRACKER['day_label_font_color'])
                day2_label.pack(pady=5, anchor="w")

                if day2 in habit_data:
                    sorted_tasks = sorted(habit_data[day2], key=lambda x: x["task"].lower())
                    for task_info in sorted_tasks:
                        task = task_info["task"]
                        completed = task_info["completed"]
                        checkbox_var = tk.BooleanVar(value=completed)
                        checkbox = tk.Checkbutton(day2_frame, text=task,
                                                  font=HABIT_TRACKER['checkbox_font'],
                                                  bg=HABIT_TRACKER['day_label_bg'],
                                                  fg=HABIT_TRACKER['day_label_font_color'],
                                                  variable=checkbox_var,
                                                  command=lambda task=task, day=day2, checkbox_var=checkbox_var:
                                                  self.update_task_state(task, day, checkbox_var))
                        checkbox.pack(anchor="w")
                        checkbox.config(cursor="hand2")

                        self.checkboxes_state[(day2, task)] = checkbox_var

            row += 1

    def update_task_state(self, task, day, checkbox_var):
        """
        This method updates the completion status of a task for a given day based on the state of the checkbox.

        :param task: The task description (e.g., "Exercise", "Read a book").
        :param day: The day of the week (e.g., "Monday", "Tuesday").
        :param checkbox_var: The Boolean variable that tracks the state of the checkbox (checked or unchecked).
        :return: None
        """
        start_date = self.get_start_date()

        habit_data = self.habit_tracker.get(start_date, {})

        if day in habit_data:
            for task_info in habit_data[day]:
                if task_info["task"] == task:
                    task_info["completed"] = checkbox_var.get()
                    asyncio.run(send_task_update_to_server(
                        self.year, day, task, task_info["completed"]
                    ))

            self.habit_tracker[start_date] = habit_data

    def add_icon_and_label(self, parent, text):
        """
        This method creates a frame containing an icon and a label with the provided text.

        :param parent: The parent widget where this frame will be added.
        :param text: The text to display alongside the icon.
        :return: None
        """
        label_frame = tk.Frame(parent, bg=INTERFACE['bg_color'])
        label_frame.pack(anchor="w", pady=10, padx=10, fill="x")

        # Add title icon
        try:
            icon_image = self.icon_image_original.resize((30, 30), Image.Resampling.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_image)
            icon_label = tk.Label(label_frame, image=icon_photo, bg=INTERFACE['bg_color'])
            icon_label.image = icon_photo
            icon_label.pack(anchor="w")
        except Exception as e:
            print(f"Icon load error: {e}")

        # Add text
        text_label = tk.Label(label_frame, text=text, font=HABIT_TRACKER['page_title_font'],
                              bg=INTERFACE['bg_color'], anchor="w")
        text_label.pack(anchor="w", pady=(5, 0))

    def navigate_to_yearly_plans(self):
        """
        Return to Yearly plans.

        :return: None
        """
        self.main_window.bind_events()
        self.main_window.show_tab_content("yearly_plans")

    def navigate_to_year(self, year):
        """
        This method navigates the user interface to a specified year's view.

        :param year: The year to navigate to.
        :return: None
        """
        self.main_window.bind_events()
        clear_canvas(self.parent)

        from src.year import Year
        year_frame = Year(self.parent, main_window=self.main_window, year=year)
        year_frame.pack(fill=tk.BOTH, expand=True)

        reset_canvas_view(self.main_window)
