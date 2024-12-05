from datetime import datetime
from tkcalendar import Calendar
from config.imports import *
from config.settings import HABIT_TRACKER
from config.utils import add_source_label_third_level as add_source_label_habit_tracker
from datetime import date as setcalendardate


def load_tasks_from_json(json_file):
    """
    Loads the habit tracker data from the given JSON file.

    :param json_file: The path to the JSON file containing tasks data.
    :return: A dictionary containing the habit tracker data, or an empty dictionary if an error occurs.
    """
    try:
        with open(json_file, "r", encoding='utf-8') as file:
            tasks = json.load(file)

            if "habit_tracker" in tasks:
                return tasks["habit_tracker"]
            else:
                print("Error: 'habit_tracker' not found in JSON")
                return {}
    except FileNotFoundError:
        print(f"{json_file} not found. Returning empty tasks.")
        return {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON in {json_file}. Returning empty tasks.")
        return {}


class HabitTracker(tk.Frame):
    """
    The HabitTracker class represents the frame for the habit tracking page.
    This frame displays habit tracking information, allows navigation to other pages
    such as "Yearly Plans", and manages UI components related to habit tracking.
    """
    def __init__(self, parent, main_window, json_file, year):
        """
        Initializes the HabitTracker frame by setting up the background, loading the habit tracker data,
        and configuring the navigation elements and other interface components.

        :param parent: The parent widget where this frame will be placed (usually the main window).
        :param main_window: The main window of the application, used to handle scrollbars and other global actions.
        :param json_file: The path to the JSON file containing habit tracker data.
        :param year: The specific year to display in the habit tracker, affecting data and UI elements.
        """
        super().__init__(parent)
        self.configure(bg=INTERFACE['bg_color'])
        self.main_window = main_window
        self.year = year
        self.parent = parent
        self.json_file = json_file
        self.main_window.check_scrollbar()

        self.habit_tracker = load_tasks_from_json(json_file)

        add_source_label_habit_tracker(self,
                                       icon_path_1=ICONS_PATHS['yearly_plans'],
                                       clickable_text="Yearly plans /",
                                       click_command_1=self.navigate_to_yearly_plans,
                                       icon_path_2=ICONS_PATHS['year'],
                                       year_name=f"{self.year} /",
                                       icon_path_3=ICONS_PATHS['habit_tracker'],
                                       text=PAGES_NAMES['habit_tracker'],
                                       click_command_2=lambda: self.navigate_to_year(self.year))

        self.icon_image_original = Image.open(ICONS_PATHS['habit_tracker'])

        self.add_icon_and_label(self, PAGES_NAMES['habit_tracker'])

        add_separator(parent=self, color=INTERFACE['separator'])

        self.add_quote_and_image()

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
        in the JSON file. It also updates the 'habit_tracker' section, if necessary, to reflect the new week starting date.

        :param selected_date: The date selected by the user, passed as a string in the format 'yyyy-mm-dd'.
        :return: None
        """
        try:
            # Reformat the date 'yyyy-mm-dd'
            selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d')

            # New key 'week starting'
            week_starting_key = f"Week starting {selected_date_obj.strftime('%Y-%m-%d')}"

            # Load from JSON
            with open(self.json_file, 'r', encoding='utf-8') as f:
                current_data = json.load(f)

            # Renew 'week_starting'
            current_data['week_starting'] = week_starting_key

            if 'habit_tracker' in current_data:
                old_key = list(current_data['habit_tracker'].keys())[0]
                current_data['habit_tracker'][week_starting_key] = current_data['habit_tracker'].pop(old_key)

            # Save to JSON
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(current_data, f, ensure_ascii=False, indent=4)

            self.date_window.destroy()

            # Widget refresh
            self.refresh_habit_tracker()

            messagebox.showinfo("Success", f"Date updated to {week_starting_key}")

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

            self.add_habit_tracker_demo(self.left_frame)

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
        of the week. Tasks can be added as a comma-separated list, and changes will be saved to the JSON file.

        :return: None
        """
        self.edit_window = tk.Toplevel(self)
        self.edit_window.withdraw()
        self.edit_window.title("Edit Habit Tracker")

        center_window_on_parent(self.main_window, self.edit_window, 500, 350)
        self.edit_window.iconbitmap(APP['icon_path'])

        edit_frame = tk.Frame(self.edit_window, bg=INTERFACE['bg_color'])
        edit_frame.pack(padx=10, pady=5)

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # Get key
        start_date_key = self.get_start_date_from_json()

        def save_changes(day, task_entry):
            """
            Saves the tasks for a specific day into the habit tracker and updates the JSON file.

            :param day: The day of the week (e.g., "Monday")
            :param task_entry: The Entry widget where the user inputted the tasks for the day
            :return: None
            """
            task_text = task_entry.get()  # Get input text
            if task_text:
                tasks = [{"task": task.strip(), "completed": False} for task in task_text.split(',')]
                self.habit_tracker[start_date_key][day] = tasks
            else:
                self.habit_tracker[start_date_key][day] = []
            self.save_tasks_to_json(self.habit_tracker)  # Save to JSON

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

        self.add_habit_tracker_demo(self.left_frame)

        # Add buttons
        self.create_habit_tracker_buttons(self.left_frame)  # Используем новую функцию для добавления кнопок

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

            self.save_tasks_to_json(self.habit_tracker)

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

            self.add_habit_tracker_demo(self.left_frame)

            # Add buttons
            self.create_habit_tracker_buttons(self.left_frame)

            # Lift the edit_window if it exists and is valid
            if hasattr(self, 'edit_window') and isinstance(self.edit_window, tk.Toplevel):
                self.edit_window.lift()  # Bring the edit window to the front

    def get_start_date_from_json(self):
        """
        This method retrieves the first start date (key) from the habit tracker JSON data.
        It looks for keys that start with "Week starting" and returns the first such key found.

        :return: The first key starting with 'Week starting' if found, otherwise None.
        """
        self.habit_tracker = load_tasks_from_json(self.json_file)

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

    def add_habit_tracker_demo(self, parent_frame):
        """
        This method is used to create and display a demo habit tracker UI within the specified parent frame.
        It retrieves habit tracking data from a JSON file, constructs a layout of the habit tracker for each day of the week,
        and displays checkboxes for each task within the week. Each task can be marked as completed via checkboxes.

        :param parent_frame: The parent frame where the habit tracker UI will be displayed.
        :return: None
        """
        if not self.habit_tracker:
            print("No data")
            return

        # Get week date
        start_date = self.get_start_date_from_json()
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
                for task_info in habit_data[day1]:
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
                    for task_info in habit_data[day2]:
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
        start_date = self.get_start_date_from_json()

        habit_data = self.habit_tracker.get(start_date, {})

        for task_info in habit_data.get(day, []):
            if task_info["task"] == task:
                task_info["completed"] = checkbox_var.get()

        self.save_tasks_to_json(self.habit_tracker)

    def save_tasks_to_json(self, tasks_data):
        """
        This method saves the updated tasks data to a JSON file, specifically updating the 'habit_tracker' field.

        :param tasks_data: The updated habit tracker data that needs to be saved to the JSON file.
        :return: None
        """
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                current_data = json.load(f)

            current_data['habit_tracker'] = tasks_data

            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(current_data, f, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f"Error saving to JSON: {e}")

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
        year_frame = Year(self.parent, json_file=f"data/years/{year}.json", main_window=self.main_window, year=year)
        year_frame.pack(fill=tk.BOTH, expand=True)

        reset_canvas_view(self.main_window)
