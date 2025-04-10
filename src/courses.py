from config.imports import *
from config.settings import COURSES
from config.utils import add_source_label_second_level as add_source_label_lists_for_life


async def load_tasks_from_server():
    """
    Asynchronously loads tasks (courses) from the server.

    This function sends an asynchronous HTTP GET request to the server's `/get_courses` endpoint.
    If the request is successful (status code 200), it returns the response data as a JSON object.
    In case of failure (non-200 status code), it logs an error message with the failure status code.
    If there is a connection error, it catches the exception and prints an error message.
    If no tasks are loaded or an error occurs, an empty list is returned.

    Returns:
        list: A list of tasks (courses) from the server, or an empty list if an error occurs.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SERVER_URL}/get_courses", ssl=SSL_ENABLED) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Failed to load tasks: {response.status}")
    except aiohttp.ClientError as e:
        print(f"Connection error: {e}")
    return []


async def toggle_task(task, var):
    """
    Toggles the completion status of a task on the server.

    :param task: Dictionary containing task data. Should include 'id' as a unique identifier.
    :param var: `BooleanVar` linked to the `Checkbutton` representing the task's completion status.
    :return: None
    """
    new_status = var.get()
    task_text = task.get("text")

    if not task_text:
        print("Error: Task is missing!")
        return

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"{SERVER_URL}/update_course_status",
                    json={"title": task_text, "completed": new_status},
                    ssl=SSL_ENABLED
            ) as response:
                if response.status == 200:
                    task['completed'] = new_status
                else:
                    print(f"Failed to update task: {response.status}")
    except aiohttp.ClientError as e:
        print(f"Connection error: {e}")


async def add_course(task):
    """
    Save a new course to the PostgreSQL database.

    :param task: Dictionary with task text and status.
    :return: None
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{SERVER_URL}/add_new_course", json={"title": task['text']},
                                    ssl=SSL_ENABLED) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Failed to save task: {response.status}")
                    return {"error": f"Failed with status code: {response.status}"}
    except aiohttp.ClientError as e:
        print(f"Error occurred while sending request: {e}")
        return {"error": f"Connection error: {e}"}


async def remove_task(task, frame, tasks):
    """
    Removes a task from the tasks list, updates the database, and deletes its associated UI elements.

    :param task: Dictionary representing the task to be removed. The dictionary is expected to be part of `self.tasks`.
    :param frame: The UI frame associated with the task. This frame will be destroyed upon task removal.
    :param tasks: All tasks.
    :return: tasks

    Steps performed by this method:
    1. Removes the specified `task` from `self.tasks`.
    2. Calls `self.save_tasks` to persist the updated tasks list to the database.
    3. Destroys the `frame` containing the UI elements associated with the removed task.
    """
    try:
        if task in tasks:
            tasks.remove(task)

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{SERVER_URL}/delete_course", json={"title": task["text"]},
                                    ssl=SSL_ENABLED) as response:
                if response.status == 200:
                    frame.destroy()
                elif response.status == 404:
                    print("Task not found on server")
                else:
                    print(f"Failed to delete task: {response.status}")
        return tasks
    except aiohttp.ClientError as e:
        print(f"Connection error: {e}")


async def save_task_changes(task, new_text, edit_window, frame, tasks):
    """
    Asynchronously saves the changes made to a task.

    This function updates the task's text locally and on the server. It also reflects the changes in the user interface.

    Args:
        task (dict): The task whose text is being updated.
        new_text (str): The new text that will replace the old task text.
        edit_window (tk.Toplevel): The window where the task is being edited. It will be closed after saving the changes.
        frame (tk.Frame): The parent frame containing the Checkbutton associated with the task. The Checkbutton's text
                            will be updated to reflect the new task text.
        tasks (dict): All tasks.

    Returns:
        tasks

    This function performs the following:
    1. Updates the task's `text` attribute with the new text if the `new_text` is not empty or whitespace.
    2. Sends a POST request to the server to update the task title on the server side.
    3. If the task's text was successfully updated, the corresponding Checkbutton's label in the provided frame is updated with the new text.
    4. Closes the edit window after saving the changes.
    5. If there is a connection issue or the task update fails, an error message is printed.
    6. If no Checkbutton is found in the frame, a message is printed.
    """
    if not new_text.strip():
        messagebox.showerror("Error", "Course title cannot be empty!")
        edit_window.lift()
        return tasks

    if new_text == task['text']:
        messagebox.showerror("Error", "You didn't change the title!")
        edit_window.lift()
        return tasks

    if any(existing_task["text"] == new_text for existing_task in tasks):
        messagebox.showerror("Error", "Course with this title already exists!")
        edit_window.lift()
        return tasks

    if new_text.strip():
        old_text = task['text']
        task['text'] = new_text

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{SERVER_URL}/update_course_title"
                data = {"new_title": task['text'], "title": old_text}
                async with session.post(url, json=data, ssl=SSL_ENABLED) as response:
                    if response.status != 200:
                        print("Failed to update task")

        except aiohttp.ClientError as e:
            print(f"Error during the HTTP request: {e}")

        checkbutton_found = False
        for child in frame.winfo_children():
            if isinstance(child, tk.Checkbutton):
                child.config(text=new_text)
                checkbutton_found = True
                break

        if not checkbutton_found:
            print("Checkbutton not found in the frame.")

        edit_window.destroy()

    return tasks


class Courses(tk.Frame):
    """
    This class represents the "Courses" page in the application. It is a Frame widget
    that displays a list of tasks, a banner, and various UI elements related to the course section.
    """
    def __init__(self, parent, main_window):
        """
        Initializes the Courses frame with the provided parameters. This includes setting up
        the background color, loading tasks from the server, and setting up the UI elements.

        :param parent: The parent widget to which this frame is attached.
        :param main_window: The main window of the application, passed for context.
        """
        super().__init__(parent)
        self.task_load_count = 0
        self.parent = parent
        self.main_window = main_window
        self.configure(bg=INTERFACE['bg_color'])
        self.main_window.disable_buttons()

        self.tasks = asyncio.run(load_tasks_from_server())  # Load tasks from server

        self.clickable_label = add_source_label_lists_for_life(
            self,  # Parent element
            icon_path_1=ICONS_PATHS['lists_for_life'],
            clickable_text="#Lists_for_life /",
            click_command=self.navigate_to_lists_for_life,
            icon_path_2=ICONS_PATHS['courses'],
            text=PAGES_NAMES['courses']
        )
        self.clickable_label["state"] = "disable"

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

        if self.tasks:
            self.display_tasks()
        else:
            self.main_window.enable_buttons()
            self.clickable_label["state"] = "normal"

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
        task_entry.bind("<Return>",
                        lambda event: self.update_tasks_after_change(task, task_entry.get(), edit_window, frame))

        # Save button
        save_button = tk.Button(edit_window, text="Save", font=COURSES['save_button_font'],
                                command=lambda: self.update_tasks_after_change(task, task_entry.get(), edit_window,
                                                                               frame))
        save_button.pack(pady=5)
        save_button.config(cursor="hand2")

        # Show window
        edit_window.deiconify()

    def update_tasks_after_change(self, task, new_text, edit_window, frame):
        """
        Updates the list of tasks after a task's text has been changed.

        This method is called when a user edits the title of an existing task. It asynchronously
        calls the `save_task_changes` function to save the changes both locally and on the server,
        and then updates the local list of tasks (`self.tasks`) with the new task list.

        Args:
            self: The instance of the class calling this method, which contains the `self.tasks` list.
            task (dict): The task that is being updated. It contains the original text and other properties.
            new_text (str): The new text to replace the existing task's text.
            edit_window (tk.Toplevel): The window where the task is being edited. It will be closed after saving.
            frame (tk.Frame): The frame containing the UI elements associated with the task, where the Checkbutton text will be updated.

        Returns:
            None: This method updates the `self.tasks` list and reflects changes in the UI and on the server.
        """
        updated_tasks = asyncio.run(save_task_changes(task, new_text, edit_window, frame, self.tasks))
        self.tasks = updated_tasks

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
        Add new course to list and server.

        :return: None
        """
        task_text = self.task_entry.get().strip()  # Get text from entry

        if not task_text:
            messagebox.showerror("Error", "Course title cannot be empty!")
            return

        if task_text:

            if any(task["text"] == task_text for task in self.tasks):
                messagebox.showerror("Error", "Course with the same title already exists!")
                return

            new_task = {'text': task_text, 'completed': False}
            self.tasks.append(new_task)  # Add course to list
            asyncio.run(add_course(new_task))
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
                                      command=lambda: asyncio.run(toggle_task(task, var)))
        check_button.pack(side=tk.LEFT)
        check_button.config(cursor="hand2")

        # Delete button
        delete_button = tk.Button(frame, text="Delete", bg=COURSES['delete_button_color'],
                                  font=COURSES['delete_edit_button_font'],
                                  command=lambda: self.update_tasks_after_removal(task, frame))
        delete_button.pack(side=tk.RIGHT, padx=5)
        delete_button.config(cursor="hand2")

        # Edit button
        edit_button = tk.Button(frame, text="Edit",
                                font=COURSES['delete_edit_button_font'],
                                command=lambda: self.edit_task(task, frame))
        edit_button.pack(side=tk.RIGHT, padx=5)
        edit_button.config(cursor="hand2")

        # Increment task load counter
        self.task_load_count += 1

        # If all tasks are loaded, enable buttons
        if self.task_load_count == len(self.tasks):
            self.main_window.enable_buttons()
            self.clickable_label["state"] = "normal"

    def update_tasks_after_removal(self, task, frame):
        """
        Updates the list of tasks after a task has been removed.

        This method is called when a user deletes an existing task. It asynchronously
        calls the `remove_task` function to remove the task both locally and on the server,
        and then updates the local list of tasks (`self.tasks`) to reflect the removal.

        Args:
            self: The instance of the class calling this method, which contains the `self.tasks` list.
            task (dict): The task to be removed. It contains the text and other properties of the task.
            frame (tk.Frame): The frame containing the UI elements associated with the task. The frame will be destroyed after removal.

        Returns:
            None: This method updates the `self.tasks` list by removing the task and updates the UI accordingly.
        """
        updated_tasks = asyncio.run(remove_task(task, frame, self.tasks))
        self.tasks = updated_tasks  # Update self.tasks with the returned list
