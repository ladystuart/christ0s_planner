from config.imports import *
from config.settings import YEARLY_PLANS_INNER
from config.utils import add_source_label_third_level as add_source_label_yearly_plans_inner, load_tasks_from_json


class YearlyPlansInner(tk.Frame):
    """
    A class for displaying and interacting with yearly plans.

    This class is used to show the plans for a specific year, allowing users to
    view, add, and modify tasks associated with that year. It loads task data from
    a JSON file and displays it in a user-friendly interface. The class also includes
    navigation elements to go back to the main yearly plans or navigate to a specific year.

    Attributes:
        main_window (tk.Tk): The main application window.
        year (int): The year for which the plans are being displayed.
        parent (tk.Widget): The parent widget for this frame.
        json_file (str): The path to the JSON file containing task data.
        tasks (dict): A dictionary containing the task data loaded from the JSON file.
        yearly_plans (list): A list of yearly plans loaded from the task data.
    """

    def __init__(self, parent, main_window, json_file, year):
        """
        Initialize the YearlyPlansInner frame.

        :param parent: The parent widget that contains this frame (typically a window or another frame).
        :param main_window: The main window of the application, used for global actions (e.g., scrollbar handling).
        :param json_file: Path to the JSON file that contains task data.
        :param year: The specific year for which the plans are displayed.
        """
        super().__init__(parent)
        self.configure(bg=INTERFACE['bg_color'])
        self.main_window = main_window
        self.year = year
        self.parent = parent
        self.json_file = json_file  # Path to JSON
        self.task_vars = []

        self.tasks = load_tasks_from_json(json_file)
        self.yearly_plans = self.tasks.get("yearly_plans", [])

        add_source_label_yearly_plans_inner(self,
                                            icon_path_1=ICONS_PATHS['yearly_plans'],
                                            clickable_text="Yearly plans /",
                                            click_command_1=self.navigate_to_yearly_plans,
                                            icon_path_2=ICONS_PATHS['year'],
                                            year_name=f"{self.year} /",
                                            icon_path_3=ICONS_PATHS['yearly_plans_inner'],
                                            text=PAGES_NAMES['yearly_plans_inner'],
                                            click_command_2=lambda: self.navigate_to_year(self.year))

        # Banner add
        self.banner_label, self.banner_image_original = add_banner(
            self,
            banner_path=BANNER_PATHS['yearly_plans_inner'],
            bg_color=INTERFACE['bg_color']
        )

        # resize_banner
        if self.banner_label and self.banner_image_original:
            self.bind("<Configure>", lambda event: resize_banner(
                self,
                self.banner_label,
                self.banner_image_original
            ))

        self.icon_image_original = Image.open(ICONS_PATHS['yearly_plans_inner'])

        add_icon_and_label(self, text=PAGES_NAMES['yearly_plans_inner'],
                           icon_path=ICONS_PATHS['yearly_plans_inner'],
                           bg_color=INTERFACE['bg_color'])
        add_separator(parent=self, color=INTERFACE['separator'])

        self.add_task_input()
        self.display_tasks()

        self.after(10, self.main_window.check_scrollbar)

    def edit_task(self, task, frame):
        """
        Opens a new window for editing a task.

        This method creates a new top-level window that allows the user to edit the content
        of an existing task. It pre-fills the input field with the current task text, and
        provides an option to save the changes. The window also includes a Save button,
        and pressing the Enter key will save the changes as well.

        :param task: The task to be edited. This is the initial content of the text field.
        :param frame: The parent frame where the task is located. It will be updated after saving the changes.
        :return: None
        """
        edit_window = tk.Toplevel(self)
        edit_window.withdraw()
        edit_window.title("Edit task")

        center_window_on_parent(self.main_window, edit_window, 400, 100)

        try:
            icon_image = Image.open(APP['icon_path'])
            icon_photo = ImageTk.PhotoImage(icon_image)
            edit_window.iconphoto(False, icon_photo)
        except Exception as e:
            print(f"Error icon load: {e}")

        task_entry = tk.Entry(edit_window, font=YEARLY_PLANS_INNER['toplevel_windows_font'], width=40)
        task_entry.insert(0, task)
        task_entry.pack(pady=10)
        task_entry.bind("<Return>", lambda event: self.save_task_changes(task, task_entry.get(), edit_window, frame))

        # Save button
        save_button = tk.Button(edit_window, text="Save", font=YEARLY_PLANS_INNER['toplevel_windows_font'],
                                command=lambda: self.save_task_changes(task, task_entry.get(), edit_window, frame))
        save_button.pack(pady=5)
        save_button.config(cursor="hand2")

        edit_window.deiconify()

    def save_task_changes(self, old_task, new_task_text, edit_window, frame):
        """
        Saves changes to a task and updates the relevant UI elements.

        This method finds the task in the internal list (`self.tasks["yearly_plans"]`)
        that matches the `old_task`, updates its text with the `new_task_text`,
        and then saves the changes to the JSON file. It also updates the text of
        any associated UI elements (such as checkbuttons) in the given frame to reflect
        the updated task text. Finally, it closes the edit window.

        :param old_task: The current text of the task that is being edited.
        :param new_task_text: The new text to update the task with.
        :param edit_window: The window where the task is being edited. It will be closed after saving the changes.
        :param frame: The frame containing the task's UI elements (such as checkbuttons) to be updated with the new text.
        :return: None
        """
        for task_info in self.tasks["yearly_plans"]:
            if task_info["task"] == old_task:
                task_info["task"] = new_task_text
                break

        # Save to JSON
        self.save_tasks_to_json()

        for widget in frame.winfo_children():
            if isinstance(widget, tk.Checkbutton):
                widget.config(text=new_task_text)

        edit_window.destroy()

    def add_task_input(self):
        """
        Creates the input field and button for adding a new task.

        This method sets up an entry field where the user can type a new task and a button
        to add the task to the list. The "Enter" key is bound to trigger the addition of
        the task, as well as clicking the "Add Task" button. The button's appearance is also
        configured with a custom font and background color.

        :return: None
        """
        self.task_entry = tk.Entry(self, width=40, font=YEARLY_PLANS_INNER['entry_font'])
        self.task_entry.pack(pady=10)
        self.task_entry.bind("<Return>", lambda event: self.add_task())

        self.add_task_button = tk.Button(self, text="Add Task", command=self.add_task,
                                         font=YEARLY_PLANS_INNER['buttons_font'],
                                         bg=YEARLY_PLANS_INNER['add_button_color'])
        self.add_task_button.pack(pady=5)
        self.add_task_button.config(cursor="hand2")

    def display_tasks(self):
        """
        Displays the tasks on the user interface.

        This method iterates through the list of tasks in `self.tasks["yearly_plans"]`,
        and for each task, it creates a corresponding widget to display the task
        and its completion status. After displaying each task, the method ensures that
        the scrollbar (if any) is correctly updated in the main window.

        :return: None
        """

        for task_info in self.tasks.get("yearly_plans", []):
            task = task_info["task"]
            done = task_info["done"]

            # Create widget for each task
            self.create_task_widget(task, done)

            self.main_window.check_scrollbar()

    def create_task_widget(self, task, done):
        """
        Creates a widget for displaying a task with options to edit, delete, and toggle its completion status.

        This method creates a frame for each task that includes a checkbox to mark the task as done or undone,
        a button to delete the task, and a button to edit the task. It uses the provided task text and its
        completion status to set up the UI. The checkbox state is bound to a Boolean variable to track whether
        the task is completed or not.

        :param task: The text description of the task to be displayed.
        :param done: The current completion status of the task (True if completed, False if not).
        :return: None
        """
        frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        frame.pack(fill=tk.X, padx=10, pady=5)

        var = tk.BooleanVar(value=done)

        # Task checkbox
        check_button = tk.Checkbutton(frame, text=task, variable=var, bg=INTERFACE['bg_color'],
                                      font=YEARLY_PLANS_INNER['tasks_font'],
                                      command=lambda: self.update_task_status(task, var))
        check_button.pack(side=tk.LEFT)
        check_button.config(cursor="hand2")

        # Delete button
        delete_button = tk.Button(frame, text="Delete", bg=YEARLY_PLANS_INNER['delete_button_color'],
                                  font=YEARLY_PLANS_INNER['buttons_font'],
                                  command=lambda: self.remove_task(task, frame))
        delete_button.pack(side=tk.RIGHT, padx=5)
        delete_button.config(cursor="hand2")

        # Edit button
        edit_button = tk.Button(frame, text="Edit", font=YEARLY_PLANS_INNER['buttons_font'],
                                command=lambda: self.edit_task(task, frame))
        edit_button.pack(side=tk.RIGHT, padx=5)
        edit_button.config(cursor="hand2")

        # Add variable True/False
        self.task_vars.append((task, var))

    def update_task_status(self, task, var):
        """
        Updates the completion status of a task.

        This method is called when a user interacts with the checkbox to mark a task as completed or undone.
        It updates the `done` status of the task in the internal task list and saves the updated tasks to the JSON file.

        :param task: The text description of the task whose completion status needs to be updated.
        :param var: The Boolean variable (tk.BooleanVar) that holds the new completion status (True or False).
        :return: None
        """
        for task_info in self.tasks["yearly_plans"]:
            if task_info["task"] == task:
                task_info["done"] = var.get()
                break
        self.save_tasks_to_json()

    def remove_task(self, task, frame):
        """
        Removes a task from the task list and deletes its corresponding widget.

        This method is called when the user clicks the "Delete" button for a task.
        It removes the task from the internal list of tasks, deletes the associated widget from the UI,
        and updates the task list in the JSON file.

        :param task: The text description of the task to be removed.
        :param frame: The frame (widget) containing the task UI element that should be removed.
        :return: None
        """
        self.tasks["yearly_plans"] = [task_info for task_info in self.tasks["yearly_plans"] if
                                      task_info["task"] != task]
        self.save_tasks_to_json()
        frame.destroy()  # Delete task widget

        # Check scroll
        self.main_window.check_scrollbar()

    def add_task(self):
        """
        Adds a new task to the task list and updates the UI.

        This method is called when the user enters a task in the input field and presses the "Add Task" button
        or the "Enter" key. The new task is validated (it cannot be empty), added to the task list, and saved
        to the JSON file. The UI is updated by clearing the input field and displaying the newly added task.
        If the input is empty, an error message is shown.

        :return: None
        """
        new_task = self.task_entry.get().strip()
        if new_task:
            # Add new task to list
            self.tasks["yearly_plans"].append({"task": new_task, "done": False})
            self.save_tasks_to_json()

            # Clear entry field
            self.task_entry.delete(0, tk.END)

            self.create_task_widget(new_task, False)
            # Check scroll
            self.main_window.check_scrollbar()
        else:
            messagebox.showinfo("Error", "Task cannot be empty.")

    def save_tasks_to_json(self):
        """
        Save to JSON.

        :return: None
        """
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=4)

    def navigate_to_yearly_plans(self):
        """
        Return to Yearly plans

        :return: None
        """
        self.main_window.bind_events()
        self.main_window.show_tab_content("yearly_plans")

    def navigate_to_year(self, year):
        """
        Navigate to the specified year and display the corresponding year view.

        This method is responsible for transitioning to a new year view. It clears the current screen (or canvas),
        binds events for the new context, and then loads and displays the year-specific content
        by creating a new instance of the `Year` class with the provided year.

        :param year: The year to navigate to. This is typically the year for which the user wants to view or manage tasks.
        :return: None
        """
        self.main_window.bind_events()
        clear_canvas(self.parent)

        from src.year import Year
        year_frame = Year(self.parent, json_file=f"data/years/{year}.json", main_window=self.main_window, year=year)
        year_frame.pack(fill=tk.BOTH, expand=True)

        reset_canvas_view(self.main_window)
