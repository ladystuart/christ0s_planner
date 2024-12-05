from config.imports import *
from config.settings import GOALS
from config.utils import add_source_label_second_level as add_source_label_lists_for_life


class Goals(tk.Frame):
    """
    The Goals class is responsible for creating the interface of the 'Goals' tab.
    It includes a goals page with functionality for users to delete, add, and edit items.
    """
    def __init__(self, parent, json_file, main_window):
        """
        Initializes the "Goals" page for the "Lists for Life" application.

        :param parent: The parent widget where this frame will be placed.
        :param json_file: Path to the JSON file used to store and load goal data.
        :param main_window: Reference to the main application window, used for navigation and interaction.

        This constructor performs the following steps:
        1. Calls the superclass initializer and configures the background color.
        2. Stores the parent, JSON file path, and main application window reference.
        3. Loads the goal data from the JSON file and initializes `self.tasks`.
        4. Adds a source label at the top of the page using `add_source_label_lists_for_life`. This includes:
           - Displaying icons and clickable text to navigate back to the "Lists for Life" page.
           - Adding the current page name and relevant icons.
        5. Adds a banner image using the `add_banner` function and binds a resize handler to dynamically adjust the banner size.
        6. Displays the page's main icon and label using `add_icon_and_label`.
        7. Adds a visual separator line below the header.
        8. Displays an inspirational quote with an image using `self.add_quote_and_image`.
        9. Creates an input field for adding new goals using `self.create_task_input`.
        10. Displays the current list of goals by calling `self.display_goals`.
        """
        super().__init__(parent)
        self.parent = parent
        self.main_window = main_window
        self.configure(bg=INTERFACE['bg_color'])

        self.json_file = json_file  # Store the json_file path
        self.tasks = self.load_tasks()  # Initialize self.tasks by loading from JSON

        add_source_label_lists_for_life(
            self,  # Parent element
            icon_path_1=ICONS_PATHS['lists_for_life'],
            clickable_text="#Lists_for_life /",
            click_command=self.navigate_to_lists_for_life,
            icon_path_2=ICONS_PATHS['goals'],
            text=PAGES_NAMES['goals']
        )

        # Banner add
        self.banner_label, self.banner_image_original = add_banner(
            self,
            banner_path=BANNER_PATHS['goals'],  # Path to banner
            bg_color=INTERFACE['bg_color']  # Bg color
        )

        # resize_banner function
        if self.banner_label and self.banner_image_original:
            self.bind("<Configure>", lambda event: resize_banner(
                self,
                self.banner_label,
                self.banner_image_original
            ))

        add_icon_and_label(self, text=PAGES_NAMES['goals'], icon_path=ICONS_PATHS['goals'],
                           bg_color=INTERFACE['bg_color'])
        add_separator(parent=self, color=INTERFACE['separator'])

        self.add_quote_and_image()

        self.create_task_input()  # New task entry
        self.display_goals()  # Show goals

    def edit_task(self, task, frame):
        """
        Opens a new window for editing the text of an existing goal.

        :param task: Dictionary representing the goal to be edited. It must contain at least a 'text' key with the current goal text.
        :param frame: The parent frame where the task is displayed. Used to update the UI after changes.
        :return: None

        This method performs the following steps:
        1. Creates a top-level window for editing the goal's text.
        2. Sets the title of the window to "Edit goal" and centers it relative to the parent.
        3. Attempts to load and set the application icon for the edit window.
        4. Adds an entry field pre-filled with the current goal text, allowing the user to make changes.
           - Binds the `<Return>` key to save the changes when pressed.
        5. Adds a "Save" button, which also saves the changes and closes the window.
        6. Updates the task in the parent frame and in the underlying data structure by calling `self.save_task_changes`.
        """
        edit_window = tk.Toplevel(self)
        edit_window.withdraw()
        edit_window.title("Edit goal")

        center_window_on_parent(self.main_window, edit_window, 400, 100)

        try:
            icon_image = Image.open(APP['icon_path'])
            icon_photo = ImageTk.PhotoImage(icon_image)
            edit_window.iconphoto(False, icon_photo)
        except Exception as e:
            print(f"Error icon load: {e}")

        # Edit task entry
        task_entry = tk.Entry(edit_window, font=GOALS['toplevel_windows_font'], width=40)
        task_entry.insert(0, task['text'])  # Current title
        task_entry.pack(pady=10)
        task_entry.bind("<Return>", lambda event: self.save_task_changes(task, task_entry.get(), edit_window, frame))

        # Save button
        save_button = tk.Button(edit_window, text="Save", font=GOALS['save_button_font'],
                                command=lambda: self.save_task_changes(task, task_entry.get(), edit_window, frame))
        save_button.pack(pady=5)
        save_button.config(cursor="hand2")

        edit_window.deiconify()

    def save_task_changes(self, task, new_text, edit_window, frame):
        """
        Saves the changes made to a task and updates the user interface accordingly.

        :param task: Dictionary representing the task being edited. The dictionary must include at least a 'text' key for the task description.
        :param new_text: The updated text entered by the user for the task.
        :param edit_window: The top-level edit window to be closed after saving changes.
        :param frame: The frame containing the task's associated widgets (e.g., Checkbutton) to be updated with the new text.
        :return: None

        Steps performed by this method:
        1. Checks if the new text is not empty or whitespace. If it is valid:
           - Updates the 'text' field of the `task` dictionary with the `new_text`.
           - Calls `self.save_tasks` to persist the updated tasks list to the JSON file.
        2. Searches the `frame` for a `Checkbutton` widget associated with the task:
           - Updates the `text` property of the `Checkbutton` to reflect the new task text.
           - Logs a message if the `Checkbutton` was not found in the frame.
        3. Closes the edit window (`edit_window`) after successfully saving the changes.
        """
        if new_text.strip():
            task['text'] = new_text
            self.save_tasks()  # Save to JSON

            # Refresh checkbox text
            checkbutton_found = False
            for child in frame.winfo_children():
                if isinstance(child, tk.Checkbutton):
                    child.config(text=new_text)
                    checkbutton_found = True
                    break

            if not checkbutton_found:
                print("Checkbutton not found in the frame.")

            edit_window.destroy()

    def remove_task(self, task, frame):
        """
        Removes a task from the tasks list, updates the JSON file, and deletes its associated UI elements.

        :param task: Dictionary representing the task to be removed. The dictionary is expected to be part of `self.tasks`.
        :param frame: The UI frame associated with the task. This frame will be destroyed upon task removal.
        :return: None

        Steps performed by this method:
        1. Removes the specified `task` from `self.tasks`.
        2. Calls `self.save_tasks` to persist the updated tasks list to the JSON file.
        3. Destroys the `frame` containing the UI elements associated with the removed task.
        """
        self.tasks.remove(task)  # Delete goal
        self.save_tasks()
        frame.destroy()

    def create_task_input(self):
        """
        Creates entry and button for adding new goal.

        :return: None
        """
        input_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        input_frame.pack(pady=10)

        self.task_entry = tk.Entry(input_frame, font=GOALS['goal_entry_font'], width=40)
        self.task_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.task_entry.bind("<Return>", lambda event: self.add_task())

        add_button = tk.Button(input_frame, text="Add goal", font=GOALS['add_button_font'],
                               bg=GOALS['add_button_color'],
                               command=self.add_task)
        add_button.pack(side=tk.LEFT)
        add_button.config(cursor="hand2")

    def add_task(self):
        """
        Add new goal to JSON

        :return: None
        """
        task_text = self.task_entry.get().strip()  # Get text from entry

        if task_text:
            new_task = {'text': task_text, 'completed': False}  # Create new goal
            self.tasks.append(new_task)
            self.save_tasks()  # Save to JSON
            self.task_entry.delete(0, tk.END)
            self.create_task_widget(new_task)  # Show new goal

    def add_quote_and_image(self):
        """
        Adds a quote and an accompanying image to the interface.

        :return: None

        This method performs the following:
        1. Creates an `image_frame` to hold the quote and image.
        2. Creates a `quote_frame` within `image_frame` to organize the quote text and a decorative vertical line.
        3. Adds a vertical line to the `quote_frame` for aesthetic separation.
        4. Displays a quote using `label_quote`, with text properties configured via the `GOALS` dictionary.
        5. Adds an image to the `image_frame` next to the quote using `add_image_to_grid`.

        Layout:
        - The quote is positioned to the left of the image.
        - The image is added to the right in a grid configuration.
        """
        # Image frame
        image_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        image_frame.pack(pady=5)

        # Quote frame
        quote_frame = tk.Frame(image_frame, bg=INTERFACE['bg_color'])
        quote_frame.grid(row=0, column=0, padx=(0, 10), pady=5)

        # Vertical line
        line = tk.Canvas(quote_frame, width=2, bg=INTERFACE['separator'], height=100)
        line.pack(side=tk.LEFT, padx=(0, 10))

        # Quote text
        quote_text = GOALS['quote_text']
        label_quote = tk.Label(quote_frame, text=quote_text, font=GOALS['quote_font'], bg=INTERFACE['bg_color'],
                               wraplength=GOALS['quote_wraplength'])
        label_quote.pack(side=tk.LEFT, fill=tk.BOTH)

        add_image_to_grid(image_frame, GOALS['image_link'], row=0, column=1, height=200,
                          width=300, rowspan=1)

    def navigate_to_lists_for_life(self):
        """
        Returning to page #Lists_for_life.

        :return: None
        """
        self.main_window.show_tab_content("lists_for_life")

    def load_tasks(self):
        """
        Get goals from JSON.

        :return: data['tasks']
        """
        if os.path.exists(self.json_file):
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data['tasks']  # Предполагается, что в JSON есть ключ 'tasks'
        return []

    def save_tasks(self):
        """
        Save goals to JSON.

        :return: None
        """
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump({"tasks": self.tasks}, f, ensure_ascii=False, indent=4)

    def display_goals(self):
        """
        Show goals.

        :return: None
        """
        for task in self.tasks:
            self.create_task_widget(task)

    def create_task_widget(self, task):
        """
        Creates a widget for displaying a single task with options to edit, delete, and toggle its completion status.

        :param task: Dictionary containing the task data. Keys include:
                      - "text": The text of the task.
                      - "completed": A boolean indicating the task's completion status.
        :return: None

        This method performs the following actions:
        1. Creates a `frame` to hold the task's components.
        2. Adds a `Checkbutton` to toggle the task's completion, bound to a `BooleanVar` reflecting the `completed` state.
        3. Adds an "Edit" button to modify the task text, invoking the `edit_task` method.
        4. Adds a "Delete" button to remove the task, invoking the `remove_task` method.

        Layout:
        - The task text (as a `Checkbutton`) is aligned to the left.
        - The "Edit" and "Delete" buttons are positioned on the right.

        Each component uses styles and colors defined in the `GOALS` and `INTERFACE` dictionaries.
        """
        frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        frame.pack(fill=tk.X, padx=10, pady=5)

        var = tk.BooleanVar(value=task['completed'])  # Checkbox

        check_button = tk.Checkbutton(frame, text=task['text'], variable=var, bg=INTERFACE['bg_color'],
                                      font=GOALS['goals_font'],
                                      command=lambda: self.toggle_task(task, var))
        check_button.pack(side=tk.LEFT)
        check_button.config(cursor="hand2")

        # Delete button
        delete_button = tk.Button(frame, text="Delete", bg=GOALS['delete_button_color'],
                                  command=lambda: self.remove_task(task, frame),
                                  font=GOALS['delete_edit_button_font'])
        delete_button.pack(side=tk.RIGHT, padx=5)
        delete_button.config(cursor="hand2")

        # Edit button
        edit_button = tk.Button(frame, text="Edit", command=lambda: self.edit_task(task, frame),
                                font=GOALS['delete_edit_button_font'])
        edit_button.pack(side=tk.RIGHT, padx=5)
        edit_button.config(cursor="hand2")

    def toggle_task(self, task, var):
        """
        Toggles the completion status of a task.

        :param task: Dictionary containing task data. Keys include:
                      - "completed": A boolean indicating the task's completion status.
        :param var: `BooleanVar` linked to the `Checkbutton` representing the task's completion status.
        :return: None

        This method performs the following actions:
        1. Updates the `completed` status of the task in the `task` dictionary based on the state of `var`.
        2. Saves the updated tasks list to the JSON file.

        Note: The commented line `frame.destroy()` can be used to remove the task widget from the interface if necessary
        (e.g., for filtering completed tasks).
        """
        task['completed'] = var.get()
        self.save_tasks()  # Save to JSON
