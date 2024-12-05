from config.imports import *
from config.settings import COURSES
from config.utils import add_source_label_second_level as add_source_label_lists_for_life


class Courses(tk.Frame):
    """
    This class represents the "Courses" page in the application. It is a Frame widget
    that displays a list of tasks, a banner, and various UI elements related to the course section.
    """
    def __init__(self, parent, json_file, main_window):
        """
        Initializes the Courses frame with the provided parameters. This includes setting up
        the background color, loading tasks from the specified JSON file, and setting up the UI elements.

        :param parent: The parent widget to which this frame is attached.
        :param json_file: Path to the JSON file from which the tasks will be loaded.
        :param main_window: The main window of the application, passed for context.
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
            icon_path_2=ICONS_PATHS['courses'],
            text=PAGES_NAMES['courses']
        )

        # Banner add
        self.banner_label, self.banner_image_original = add_banner(
            self,
            banner_path=BANNER_PATHS['courses'],  # Path to banner
            bg_color=INTERFACE['bg_color']  # Bg color
        )

        # resize_banner function
        if self.banner_label and self.banner_image_original:
            self.bind("<Configure>", lambda event: resize_banner(
                self,
                self.banner_label,
                self.banner_image_original
            ))

        add_icon_and_label(self, text=PAGES_NAMES['courses'], icon_path=ICONS_PATHS['courses'],
                           bg_color=INTERFACE['bg_color'])
        add_separator(parent=self, color=INTERFACE['separator'])

        self.add_quote_and_image()

        self.create_task_input()  # Add new course field
        self.display_tasks()  # Show courses

    def edit_task(self, task, frame):
        """
        Opens a new window to edit a task.

        :param task: Dictionary containing task information (e.g., {'text': 'Task title'})
        :param frame: The frame from which the task is being edited
        :return: None
        """
        edit_window = tk.Toplevel(self)  # Create new window

        # Hide window before centering
        edit_window.withdraw()
        center_window_on_parent(self.main_window, edit_window, 400, 100)

        edit_window.title("Edit course")

        try:
            icon_image = Image.open(APP['icon_path'])
            icon_photo = ImageTk.PhotoImage(icon_image)
            edit_window.iconphoto(False, icon_photo)
        except Exception as e:
            print(f"Edit window load error: {e}")

        # Course title entry
        task_entry = tk.Entry(edit_window, font=COURSES['toplevel_windows_font'], width=40)
        task_entry.insert(0, task['text'])
        task_entry.pack(pady=10)
        task_entry.bind("<Return>", lambda event: self.save_task_changes(task, task_entry.get(), edit_window, frame))

        # Save button
        save_button = tk.Button(edit_window, text="Save", font=COURSES['save_button_font'],
                                command=lambda: self.save_task_changes(task, task_entry.get(), edit_window, frame))
        save_button.pack(pady=5)
        save_button.config(cursor="hand2")
        # Show window
        edit_window.deiconify()

    def save_task_changes(self, task, new_text, edit_window, frame):
        """
        Saves the changes made to a task (updates task title, saves to JSON, and updates the checkbox text).

        :param task: The task being edited (dictionary with task details).
        :param new_text: The new task title entered by the user.
        :param edit_window: The window where the task is being edited.
        :param frame: The frame containing the Checkbutton corresponding to the task.
        :return: None
        """
        if new_text.strip():
            task['text'] = new_text
            self.save_tasks()  # Save to JSON

            checkbutton_found = False
            for child in frame.winfo_children():
                if isinstance(child, tk.Checkbutton):
                    child.config(text=new_text)  # Update checkbox text
                    checkbutton_found = True
                    break

            if not checkbutton_found:
                print("Checkbutton not found in the frame.")

            edit_window.destroy()

    def remove_task(self, task, frame):
        """
        Removes a task from the interface and the underlying data list, then saves the changes to the JSON file.

        :param task: The task to be removed (dictionary representing the task).
        :param frame: The frame or widget containing the task that will be removed from the UI.
        :return: None
        """
        self.tasks.remove(task)  # Delete course from list
        self.save_tasks()  # Save to JSON
        frame.destroy()  # Delete widget

    def create_task_input(self):
        """
        Creates the input interface (entry field and button) for adding a new task.

        :return: None
        """
        input_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        input_frame.pack(pady=10)

        self.task_entry = tk.Entry(input_frame, font=COURSES['course_entry_font'], width=40)
        self.task_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.task_entry.bind("<Return>", lambda event: self.add_task())

        add_button = tk.Button(input_frame, text="Add course", font=COURSES['add_button_font'],
                               bg=COURSES['add_button_color'],
                               command=self.add_task)
        add_button.pack(side=tk.LEFT)
        add_button.config(cursor="hand2")

    def add_task(self):
        """
        Add new course to list and JSON

        :return: None
        """
        task_text = self.task_entry.get().strip()  # Get text from entry

        if task_text:
            new_task = {'text': task_text, 'completed': False}
            self.tasks.append(new_task)  # Add course to list
            self.save_tasks()  # Save to JSON
            self.task_entry.delete(0, tk.END)
            self.create_task_widget(new_task)

    def add_quote_and_image(self):
        """
        Adds a quote with a separator line and an image to the UI.

        :return: None
        """
        # Image frame
        image_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        image_frame.pack(pady=5)

        # Quote and line frame
        quote_frame = tk.Frame(image_frame, bg=INTERFACE['bg_color'])
        quote_frame.grid(row=1, column=0, padx=(0, 10), pady=5)

        # Vertical line
        line = tk.Canvas(quote_frame, width=2, bg=INTERFACE['separator'], height=100)
        line.pack(side=tk.LEFT, padx=(0, 10))

        # Quote text
        quote_text = COURSES['quote_text']
        label_quote = tk.Label(quote_frame, text=quote_text, font=COURSES['quote_font'], bg=INTERFACE['bg_color'],
                               wraplength=COURSES['quote_wraplength'])
        label_quote.pack(side=tk.LEFT, fill=tk.BOTH)

        add_image_to_grid(image_frame, COURSES['image_link'], row=0, column=0, height=350, width=650, rowspan=1)

    def navigate_to_lists_for_life(self):
        """
        Returning to page #Lists_for_life.

        :return: None
        """
        self.main_window.show_tab_content("lists_for_life")

    def load_tasks(self):
        """
        Get courses from JSON

        :return: data['tasks']
        """
        if os.path.exists(self.json_file):
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data['tasks']  # Предполагается, что в JSON есть ключ 'tasks'
        return []

    def save_tasks(self):
        """
        Save tasks to JSON

        :return: None
        """
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump({"tasks": self.tasks}, f, ensure_ascii=False, indent=4)

    def display_tasks(self):
        """
        Show courses

        :return: None
        """
        for task in self.tasks:
            self.create_task_widget(task)

    def create_task_widget(self, task):
        """
        Creates a task widget with a checkbox, edit button, and delete button.

        :param task: Dictionary containing task details (text, completed status, etc.)
        :return: None
        """
        frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        frame.pack(fill=tk.X, padx=10, pady=5)

        var = tk.BooleanVar(value=task['completed'])

        check_button = tk.Checkbutton(frame, text=task['text'], variable=var, bg=INTERFACE['bg_color'],
                                      font=COURSES['courses_font'],
                                      command=lambda: self.toggle_task(task, var))
        check_button.pack(side=tk.LEFT)
        check_button.config(cursor="hand2")

        # Delete button
        delete_button = tk.Button(frame, text="Delete", bg=COURSES['delete_button_color'],
                                  font=COURSES['delete_edit_button_font'],
                                  command=lambda: self.remove_task(task, frame))
        delete_button.pack(side=tk.RIGHT, padx=5)
        delete_button.config(cursor="hand2")

        # Edit button
        edit_button = tk.Button(frame, text="Edit",
                                font=COURSES['delete_edit_button_font'],
                                command=lambda: self.edit_task(task, frame))
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
