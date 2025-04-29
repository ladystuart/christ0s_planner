from config.imports import *
from config.tooltip import ToolTip
from config.utils import add_source_label_second_level as add_source_label_lists_for_life
from config.settings import READING


def create_book_type_label(parent_frame, text, font, row, column, text_color, bg_color):
    """
    Creates a label with the specified text, font, and colors, and places it in the grid within the parent frame.

    :param parent_frame: The parent frame where the label will be placed.
    :param text: The text to be displayed on the label.
    :param font: The font for the label's text.
    :param row: The row number in the grid where the label will be placed.
    :param column: The column number in the grid where the label will be placed.
    :param text_color: The color of the text on the label.
    :param bg_color: The background color of the label.
    :return: None

    Actions:
    1. A label is created with the specified text, font, and colors.
    2. The label is placed in the grid within the parent frame at the specified row and column.
    3. Padding (10px on the X-axis and 5px on the Y-axis) is applied for better visual perception.
    """
    label = tk.Label(parent_frame, text=text, font=font, fg=text_color, bg=bg_color)
    label.grid(row=row, column=column, padx=10, pady=5, sticky="ew")
    return label


class Reading(tk.Frame):
    """
    The Reading class is responsible for creating the interface for the 'Reading' tab.
    It includes a book database with the ability to delete, add, and view books by the user.
    """
    def __init__(self, parent, json_file, main_window):
        """
        Initializes the window for displaying tasks, a banner, and other interface elements.

        :param parent: The parent element for the current window (e.g., main frame or window).
        :param json_file: The path to the JSON file from which task data will be loaded.
        :param main_window: The main window of the application, passed for interacting with the main interface.

        The constructor performs the following actions:
        1. Sets the background color of the current window to #F0F0F0.
        2. Initializes variables for the number of tasks displayed by categories (Not Started, In Progress, Done).
        3. Loads tasks from the specified JSON file using the `load_tasks()` method.
        4. Inserts interface elements:
           - Adds a title with icons and a clickable text that leads to the "Lists_for_life" page.
           - Adds a banner with an image, resizing it when the window size changes.
           - Adds an icon with text corresponding to the "Reading" page.
           - Adds a separator with the specified color.
        5. Inserts a quote and an image using the `add_quote_and_image()` method.
        6. Inserts the book (or task) database using the `add_books_database()` method.

        This constructor sets up and displays all necessary elements for the task reading page.
        """
        super().__init__(parent)

        self.parent = parent
        self.main_window = main_window
        self.configure(bg=INTERFACE['bg_color'])

        self.not_started_loaded = 50  # "Not Started" books number
        self.in_progress_loaded = 50  # "In Progress" books number
        self.done_loaded = 50  # "Done" books number
        self.tasks_per_page = 50  # Iteration number

        self.json_file = json_file

        self.tasks = self.load_tasks()

        add_source_label_lists_for_life(
            self,  # Parent
            icon_path_1=ICONS_PATHS['lists_for_life'],
            clickable_text="#Lists_for_life /",
            click_command=self.navigate_to_lists_for_life,
            icon_path_2=ICONS_PATHS['reading'],
            text=PAGES_NAMES['reading']
        )

        # Banner add
        self.banner_label, self.banner_image_original = add_banner(
            self,
            banner_path=BANNER_PATHS['reading'],
            bg_color=INTERFACE['bg_color']
        )

        # resize_banner function
        if self.banner_label and self.banner_image_original:
            self.bind("<Configure>", lambda event: resize_banner(
                self,
                self.banner_label,
                self.banner_image_original
            ))

        # Icon and label
        add_icon_and_label(self, text=PAGES_NAMES['reading'], icon_path=ICONS_PATHS['reading'],
                           bg_color=INTERFACE['bg_color'])
        add_separator(parent=self, color=INTERFACE['separator'])

        self.add_quote_and_image()

        self.add_books_database()

        self.load_button_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        self.load_button_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Load button
        load_more_button = tk.Button(self.load_button_frame, text="Load more", font=READING['button_font'],
                                     command=self.load_more_tasks, bg=READING['load_more_button_color'])
        load_more_button.pack(side=tk.BOTTOM, padx=5, pady=(10, 0))
        load_more_button.config(cursor="hand2")

    def add_books_database(self):
        """
        Creates or updates three columns for books based on their status.

        :return: None
        """
        if hasattr(self, 'top_frame'):
            for widget in self.top_frame.winfo_children():
                widget.destroy()
        else:
            self.top_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
            self.top_frame.pack(fill=tk.X, pady=10)

        if hasattr(self, 'columns_frame'):
            for widget in self.columns_frame.winfo_children():
                widget.destroy()
        else:
            self.columns_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
            self.columns_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Add book button
        add_book_button = tk.Button(self.top_frame, text="Add", font=READING['button_font'],
                                    command=self.add_new_book, bg=READING['add_button_color'])
        add_book_button.pack(side=tk.LEFT, padx=5)
        add_book_button.config(cursor="hand2")

        # Filters
        self.author_filter_var = tk.StringVar(value="")
        self.language_filter_var = tk.StringVar(value="")
        self.title_filter_var = tk.StringVar(value="")

        # Author filter
        author_options = [''] + sorted(set(chain.from_iterable(task['authors'] for task in self.tasks)))
        author_filter_menu = ttk.Combobox(self.top_frame, textvariable=self.author_filter_var,
                                          values=author_options, state="readonly", font=READING['filter_font'])
        author_filter_menu.set("")
        author_filter_menu.bind("<<ComboboxSelected>>",
                                self.on_author_selected)  # Apply filter
        author_filter_menu.bind("<ButtonPress>", self.disable_scroll)  # Disable scroll
        author_filter_menu.bind("<ButtonRelease>", self.enable_scroll)  # Enable scroll
        author_filter_menu.pack(side=tk.LEFT, padx=5)
        author_filter_menu.config(cursor="hand2")

        # Language filter
        language_options = [''] + sorted(set(task['language'] for task in self.tasks))
        language_filter_menu = tk.OptionMenu(self.top_frame, self.language_filter_var,
                                             *language_options,
                                             command=self.apply_filters)
        language_filter_menu.config(font=READING['filter_font'])
        language_filter_menu.pack(side=tk.LEFT, padx=5)
        language_filter_menu.config(cursor="hand2")

        # Title filter
        title_filter_entry = tk.Entry(self.top_frame, textvariable=self.title_filter_var, font=READING['filter_font'])
        title_filter_entry.pack(side=tk.LEFT, padx=5)
        title_filter_entry.bind("<KeyRelease>", lambda event: self.apply_filters())

        for i in range(3):
            self.columns_frame.grid_columnconfigure(i, weight=1)

        # Count number
        not_started_count = sum(1 for task in self.tasks if task['status'] == "Not started")
        in_progress_count = sum(1 for task in self.tasks if task['status'] == "In progress")
        done_count = sum(1 for task in self.tasks if task['status'] == "Done")

        not_started_label = create_book_type_label(self.columns_frame, "Not Started",
                                                        font=READING['columns_titles_font'], row=0,
                                                        column=0, text_color=INTERFACE['text_color'],
                                                        bg_color=READING['not_started_label_color'])
        ToolTip(not_started_label, f"{not_started_count}")
        in_progress_label = create_book_type_label(self.columns_frame, "In Progress",
                                                        font=READING['columns_titles_font'], row=0,
                                                        column=1, text_color=INTERFACE['text_color'],
                                                        bg_color=READING['in_progress_label_color'])
        ToolTip(in_progress_label, f"{in_progress_count}")
        done_label = create_book_type_label(self.columns_frame, "Done",
                                                 font=READING['columns_titles_font'], row=0,
                                                 column=2, text_color=INTERFACE['text_color'],
                                                 bg_color=READING['done_label_color'])
        ToolTip(done_label, f"{done_count}")

        # Populate with 50 first books
        self.populate_columns()

    def load_more_tasks(self):
        """
        Adds 50 more books for each status.

        :return: None
        """
        self.not_started_loaded += self.tasks_per_page
        self.in_progress_loaded += self.tasks_per_page
        self.done_loaded += self.tasks_per_page
        self.populate_columns()

    def on_author_selected(self, event):
        """
        Event handler for author selection. Applies filters to display the corresponding data and enables scrolling.

        :param event: The event that triggered the handler. Typically this is the event of selecting an author in the interface.
        :return: None

        Actions:
        1. Applies filters to display the relevant data using the `apply_filters()` method.
        2. Enables scrolling on the page using the `enable_scroll()` method.
        """
        self.apply_filters()  # Apply filters
        self.enable_scroll()  # Enable scroll

    def disable_scroll(self, event):
        """
        Disables scrolling on the page.

        :param event: The event that triggered the handler. Typically this is a scrolling interaction.
        :return: None

        Actions:
        1. Disables the mouse wheel scrolling event by unbinding the handler for the "<MouseWheel>" event.
        """
        self.main_window.unbind_all("<MouseWheel>")  # Remove the mouse wheel scroll event handler

    def enable_scroll(self, event=None):
        """
        Enables the mouse wheel scroll handler, allowing the user to scroll the window content.

        :param event: (optional) The event that may be passed when calling the method. Typically used for handling mouse interactions. If not passed, the handling will be restored.
        :return: None

        Actions:
        1. Restores the mouse wheel scroll event handler by binding it to the `on_mouse_wheel` function in the main window (`main_window`).
        2. After calling this method, the user can again use the mouse wheel to interact with the content of the interface.
        """
        self.main_window.bind_all("<MouseWheel>", self.main_window.on_mouse_wheel)  # Restore the scroll handler

    def populate_columns(self):
        """
        Populate columns with books

        :return: None
        """
        not_started_row = 1
        in_progress_row = 1
        done_row = 1

        # Delete old widgets if any
        for widget in self.columns_frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.destroy()

        # Get filtered books
        filtered_tasks = self.filter_tasks()

        # Get number of books
        not_started_tasks = filtered_tasks[:self.not_started_loaded]
        in_progress_tasks = filtered_tasks[:self.in_progress_loaded]
        done_tasks = filtered_tasks[:self.done_loaded]

        # Add books to columns
        for task in not_started_tasks:
            if task['status'] == 'Not started':
                self.create_book_button(task, self.columns_frame, not_started_row, 0)
                not_started_row += 1

        for task in in_progress_tasks:
            if task['status'] == 'In progress':
                self.create_book_button(task, self.columns_frame, in_progress_row, 1)
                in_progress_row += 1

        for task in done_tasks:
            if task['status'] == 'Done':
                self.create_book_button(task, self.columns_frame, done_row, 2)
                done_row += 1

    def filter_tasks(self):
        """
        Filter books on author, language and title

        :return: None
        """
        filtered_tasks = self.tasks
        author_filter = self.author_filter_var.get()
        language_filter = self.language_filter_var.get()
        title_filter = self.title_filter_var.get().lower()

        # Author filter
        if author_filter != '' and author_filter:
            filtered_tasks = [task for task in filtered_tasks if author_filter in task.get('authors', [])]

        # Language filter
        if language_filter != '' and language_filter:
            filtered_tasks = [task for task in filtered_tasks if task.get('language') == language_filter]

        # Title filter
        if title_filter:
            filtered_tasks = [task for task in filtered_tasks if title_filter in task.get('title', "").lower()]

        return filtered_tasks

    def apply_filters(self, *args):
        """
        Applies filters and updates the displayed books according to the selected filters.

        :param args: Optional parameters that may be used to pass filtering conditions. These parameters can include various filters for displaying books (such as by author, genre, year of publication, etc.).
        :return: None

        Actions:
        1. The method calls the `populate_columns` function, which updates the displayed books in the interface.
        2. The books will be filtered according to the provided filters or default settings if no filters are given.
        """
        self.populate_columns()  # Updates the display of books according to the filters

    def add_new_book(self):
        """
        Opens new window to add new book.

        :return: None
        """
        # Create a new window for adding a book
        add_window = Toplevel(self)
        add_window.withdraw()
        add_window.title("Add New Book")
        add_window.transient(self.winfo_toplevel())

        # Set the icon
        icon_path = APP['icon_path']
        add_window.iconbitmap(icon_path)

        center_window_on_parent(self.main_window, add_window, 500, 400)

        # Font settings
        label_font = READING['toplevel_windows_font']
        entry_font = READING['toplevel_windows_font']

        # Fields for the new book
        fields = {
            "Title": ("title", "", "Enter the title of the book"),
            "Authors": ("authors", "", "Enter the authors separated by commas"),
            "Language": ("language", "", "Enter the language of the book"),
            "Status": ("status", "", "Select the reading status"),
            "Link": ("link", "", "Enter the link to the book"),
            "Series": ("series", "", "Enter the series name if applicable"),
            "Banner Path": ("banner_path", "", "Select an existing banner or enter a new path"),
            "Icon Path": ("icon_path", "", "Select an existing icon or enter a new path"),
            "Cover Path": ("cover_path", "", "Select the cover image path")
        }

        # Create input fields for each item
        entries = {}
        for i, (label_text, (field, value, tooltip_text)) in enumerate(fields.items()):
            label = tk.Label(add_window, text=label_text + ":", font=label_font)
            label.grid(row=i, column=0, padx=10, pady=5, sticky="w")

            if field == "status":
                # Create a dropdown menu for the status
                status_var = tk.StringVar()  # Set default value
                status_menu = tk.OptionMenu(add_window, status_var, "Not started", "In progress", "Done")
                status_menu.config(font=entry_font)
                status_menu.grid(row=i, column=1, padx=10, pady=5, sticky="w")
                entries[field] = status_var  # Save StringVar for later use
            elif field in ["banner_path", "icon_path"]:
                # Create input field for image path and add button for selecting file
                entry = tk.Entry(add_window, font=entry_font, width=30)
                entry.insert(0, value)
                entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
                # Enter
                entry.bind("<Return>", lambda event: save_book())
                # Create button to browse existing images
                select_button = tk.Button(add_window, text="Browse", font=READING['button_font'],
                                          command=lambda field=field, entry=entry: select_existing_image(field, entry))
                select_button.grid(row=i, column=2, padx=5, pady=5)
                select_button.config(cursor="hand2")

                # Create tooltip for the input field
                ToolTip(entry, tooltip_text)

                entries[field] = entry
            elif field == "cover_path":
                # Create field for cover image path with browse button
                entry = tk.Entry(add_window, font=entry_font, width=30)
                entry.insert(0, value)
                entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
                entry.bind("<Return>", lambda event: save_book())
                select_button = tk.Button(add_window, text="Browse", font=READING['button_font'],
                                          command=lambda field=field, entry=entry: select_image(field, entry))
                select_button.grid(row=i, column=2, padx=5, pady=5)
                select_button.config(cursor="hand2")
                ToolTip(entry, tooltip_text)

                entries[field] = entry
            else:
                entry = tk.Entry(add_window, font=entry_font, width=30)
                entry.insert(0, value)
                entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
                entry.bind("<Return>", lambda event: save_book())
                ToolTip(entry, tooltip_text)

                entries[field] = entry

        def select_existing_image(field, entry):
            """
            Opens a dialog window to select an existing image and displays the selected path in the specified input field.

            :param field: A string indicating the type of image being selected (e.g., "banner_path" or "icon_path").
            :param entry: The input field (entry) where the path to the selected image will be displayed.
            :return: None

            Actions:
            1. Depending on the value of the `field` parameter, the initial folder for selecting the image is determined.
            2. A dialog window opens to select an image from the specified folder, with filters applied for image types.
            3. If a file is selected, the current text in the input field is cleared, and the path to the selected image file is inserted.
            """
            if field == "banner_path":
                folder_path = READING['book_banner_path']
            elif field == "icon_path":
                folder_path = READING['book_icon_path']

            file_path = filedialog.askopenfilename(title=f"Select {field.replace('_', ' ').title()}",
                                                   initialdir=folder_path,
                                                   filetypes=(("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"),
                                                              ("All Files", "*.*")))
            if file_path:
                entry.delete(0, tk.END)  # Clear current entry
                entry.insert(0, file_path)  # Insert selected file path
                entry.bind("<Return>", lambda event: save_book())

        def select_image(field, entry):
            """
            Opens a dialog window to select an image and copies the selected file to the appropriate folder,
            then displays the path to the new file in the input field.

            :param field: A string indicating the type of image being selected (e.g., "banner_path" or "icon_path").
            :param entry: The input field (entry) where the path to the new image file will be displayed.
            :return: None

            Actions:
            1. A dialog window opens to select an image.
            2. The selected file is copied to the corresponding image folder based on the image type.
            3. If a file is selected, the current text in the input field is cleared, and the path to the new image file is inserted.
            """
            file_path = filedialog.askopenfilename(title=f"Select {field.replace('_', ' ').title()}",
                                                   filetypes=(("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"),
                                                              ("All Files", "*.*")))
            if file_path:
                # Copy file to corresponding folder
                base_folder = READING['base_folder']
                target_folder = os.path.join(base_folder, "covers")

                os.makedirs(target_folder, exist_ok=True)  # Create folder if it doesn't exist

                file_name = os.path.basename(file_path)
                target_path = os.path.join(target_folder, file_name)

                shutil.copy(file_path, target_path)  # Copy the file
                entry.delete(0, tk.END)  # Clear current entry
                entry.insert(0, target_path)  # Insert path to new file
                entry.bind("<Return>", lambda event: save_book())

        def save_book():
            """
            Saving the book

            :return: None
            """
            # Check if the status is set
            status = entries["status"].get()
            if not status:
                messagebox.showerror("Error", "Please select status for the book!")
                return

            new_book = {}
            for field, entry in entries.items():
                if field == "authors":
                    new_book[field] = entry.get().split(", ")  # Convert authors to list
                elif field == "status":
                    new_book[field] = entry.get()  # Get selected status
                else:
                    new_book[field] = entry.get()

            # Load existing data from JSON
            json_path = DATA_PATHS['reading']  # Make sure the path is correct
            try:
                with open(json_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                data = {"books": []}  # Create empty structure if file is not found or empty

            # Add the new book to the list
            data["books"].append(new_book)

            # Save updated data back to JSON
            with open(json_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            # Update tasks attribute and call the method to refresh frames
            self.tasks = data["books"]  # Update self.tasks with current data

            # Refresh the page
            self.add_books_database()  # Update book list on the page
            messagebox.showinfo("Success", "Book added successfully!")
            add_window.destroy()  # Close the window

        # Button to save the book
        save_button = tk.Button(add_window, text="Save", font=READING['button_font'], command=save_book)
        save_button.grid(row=len(fields), column=0, columnspan=2, pady=10, sticky="e")
        save_button.config(cursor="hand2")

        add_window.deiconify()

    def create_book_button(self, task, parent_frame, row, column):
        """
        Creates a button for a task with the specified text, icon, and assigned action function upon clicking.

        :param task: A dictionary containing the task data, including the title and the icon path.
        :param parent_frame: The parent frame where the button will be placed.
        :param row: The row number in the grid where the button will be placed.
        :param column: The column number in the grid where the button will be placed.
        :return: None

        Actions:
        1. A button is created with text that corresponds to the task's title.
        2. If an icon is specified for the task, it is loaded and added to the button.
        3. The button is placed in the grid inside the parent frame at the specified row and column.
        """
        button = tk.Button(parent_frame, text=task['title'], bg=INTERFACE['bg_color'], font=READING['button_font'],
                           command=lambda: self.open_book_description(task), anchor='w')
        button.config(cursor="hand2")

        if task['icon_path']:
            icon_path = task['icon_path']
            if os.path.exists(icon_path):
                image = Image.open(icon_path)
                image = image.resize((20, 20), Image.Resampling.LANCZOS)
                icon = ImageTk.PhotoImage(image)
                button.config(image=icon, compound='left')
                button.image = icon

        button.grid(row=row, column=column, padx=10, pady=5, sticky="ew")

    def open_book_description(self, task):
        """
        Handles the action when a book is clicked. Opens a new window with detailed information about the book.

        :param task: A dictionary containing task data such as title, description, banner path, etc.
        :return: None

        Actions:
        1. Creates a new window with the task details.
        2. Sets the window's size and icon.
        3. Configures the central canvas to display the content.
        4. If a banner path is provided for the task, it is displayed in the new window.
        5. Displays the task information in the window.
        """
        self.task_window = Toplevel()
        self.task_window.withdraw()
        self.task_window.title(f"{task['title']}")
        self.task_window.iconbitmap(APP['icon_path'])

        center_window_on_parent(self.main_window, self.task_window, 550, 450)
        self.canvas_mini = Canvas(self.task_window, bg=INTERFACE['bg_color'])
        self.canvas_mini_frame = Frame(self.canvas_mini)

        self.task_window.configure(bg=INTERFACE['bg_color'])  # Window bg
        self.canvas_mini.configure(bg=INTERFACE['bg_color'])  # Canvas bg
        self.canvas_mini_frame.configure(bg=INTERFACE['bg_color'])  # Frame bg

        self.canvas_mini.pack(expand=1, fill=tk.BOTH)
        self.window_area_mini = self.canvas_mini.create_window((0, 0), window=self.canvas_mini_frame, anchor="nw")
        self.canvas_mini.focus_set()

        # Banner add
        banner_path = task.get("banner_path")
        if banner_path and os.path.exists(banner_path):
            self.canvas_mini.pack(side=tk.LEFT, expand=1, fill=tk.BOTH)
            self.add_banner_book(self.canvas_mini_frame, banner_path)
        else:
            self.window_area_mini = self.canvas_mini.create_window(
                (0, 0), window=self.canvas_mini_frame, anchor="center"
            )

            # Resize banner
            def center_frame_on_canvas(event):
                canvas_width = self.canvas_mini.winfo_width()
                canvas_height = self.canvas_mini.winfo_height()
                self.canvas_mini.coords(self.window_area_mini, canvas_width // 2, canvas_height // 2)

            self.canvas_mini.bind("<Configure>", center_frame_on_canvas)

        self.add_books_info(task)

        self.task_window.deiconify()

    def add_books_info(self, task):
        """
        Displays information about a book in a window, including title, author, language, status, link, series, and cover image.

        :param task: A dictionary containing book data such as title, author, language, status, link, series, and cover path.
        :return: None

        Actions:
        1. Creates a frame to display the book's information.
        2. Displays the title, author, language, status, link, series, and cover of the book.
        3. For each attribute, checks if data is available, and if so, displays it in the corresponding widget.
        4. Adds buttons for editing and deleting the book.
        """
        books_info_frame = tk.Frame(self.canvas_mini_frame, bg=INTERFACE['bg_color'])
        books_info_frame.pack(pady=10, expand=1, anchor="center")
        rowspan_n = 0

        title_font = READING['books_info_title_font']
        normal_font = READING['books_info_font']
        default_bg_color = READING['add_window_lines_color']

        book_title_label = tk.Label(books_info_frame, text=task["title"], bg=INTERFACE['bg_color'], anchor="w",
                                    font=title_font, wraplength=READING['book_title_wraplength'], justify="left")
        book_title_label.grid(row=0, column=0, padx=10, pady=5, columnspan=3, sticky="w")

        if task.get("authors"):
            authors_label_default = tk.Label(books_info_frame, text="Author", bg=default_bg_color, anchor="w",
                                             font=normal_font)
            authors_label_default.grid(row=1, column=0, padx=10, sticky="w")
            authors_str = ", ".join(task["authors"]) 
            authors_label = tk.Label(books_info_frame, text=authors_str, bg=INTERFACE['bg_color'], anchor="w",
                                     font=normal_font)
            authors_label.grid(row=1, column=1, padx=10, sticky="w")
            rowspan_n += 1

        if task.get("language"):
            language_label_default = tk.Label(books_info_frame, text="Language", bg=default_bg_color, anchor="w",
                                              font=normal_font)
            language_label_default.grid(row=2, column=0, padx=10, sticky="w")
            language_label = tk.Label(books_info_frame, text=task["language"], bg=INTERFACE['bg_color'], anchor="w",
                                      font=normal_font)
            language_label.grid(row=2, column=1, padx=10, sticky="w")
            rowspan_n += 1

        if task.get("status"):
            status_label_default = tk.Label(books_info_frame, text="Status", bg=default_bg_color, anchor="w",
                                            font=normal_font)
            status_label_default.grid(row=3, column=0, padx=10, sticky="w")

            status_color = READING['default_label_color']
            if task["status"] == "Not started":
                status_color = READING['not_started_label_color']
            elif task["status"] == "In progress":
                status_color = READING['in_progress_label_color']
            elif task["status"] == "Done":
                status_color = READING['done_label_color']

            status_label = tk.Label(books_info_frame, text=task["status"], bg=status_color, anchor="w",
                                    font=normal_font)
            status_label.grid(row=3, column=1, padx=10, sticky="w")
            rowspan_n += 1

        if task.get("link"):
            link_label_default = tk.Label(books_info_frame, text="Link", bg=default_bg_color, anchor="w",
                                          font=normal_font)
            link_label_default.grid(row=4, column=0, padx=10, sticky="w")
            link_label = tk.Label(books_info_frame, text="Click", bg=INTERFACE['bg_color'], anchor="w", fg="blue", cursor="hand2",
                                  font=normal_font)
            link_label.bind("<Button-1>", lambda e: open_link(task["link"]))
            link_label.grid(row=4, column=1, padx=10, sticky="w")
            rowspan_n += 1

        if task.get("series"):
            series_label_default = tk.Label(books_info_frame, text="Series", bg=default_bg_color, anchor="w",
                                            font=normal_font)
            series_label_default.grid(row=5, column=0, padx=10, sticky="w")
            series_label = tk.Label(books_info_frame, text=task["series"], bg=INTERFACE['bg_color'], anchor="w",
                                    font=normal_font)
            series_label.grid(row=5, column=1, padx=10, sticky="w")
            rowspan_n += 1

        cover_path = task.get("cover_path")
        if cover_path and os.path.exists(cover_path):
            original_image = Image.open(cover_path)

            cover_image = original_image.resize((READING['cover_width'], READING['cover_height']),
                                                Image.Resampling.LANCZOS)
            cover_image = ImageTk.PhotoImage(cover_image)

            cover_label = tk.Label(books_info_frame, image=cover_image, bg=INTERFACE['bg_color'])
            cover_label.image = cover_image
            cover_label.grid(row=1, column=2, rowspan=rowspan_n, padx=10, sticky="e")

        edit_button = tk.Button(books_info_frame, text="Edit", font=READING['button_font'],
                                command=lambda: self.edit_book_info(task))
        edit_button.grid(row=rowspan_n + 2, column=0, padx=10, pady=10, sticky="w")
        edit_button.config(cursor="hand2")

        delete_button = tk.Button(books_info_frame, text="Delete", font=READING['button_font'],
                                  command=lambda: self.delete_book(task),
                                  bg=READING['delete_button_color'])
        delete_button.grid(row=rowspan_n + 2, column=1, padx=10, pady=10, sticky="w")
        delete_button.config(cursor="hand2")

        self.canvas_mini_frame.update_idletasks()
        self.canvas_mini_frame.winfo_toplevel().geometry(
            f"{self.canvas_mini_frame.winfo_width()}x{self.canvas_mini_frame.winfo_height()}")

    def delete_book(self, task):
        """
        Deletes a book from the JSON file and updates the interface.

        :param task: A dictionary containing the book's data to be deleted.
        :return: None

        Actions:
        1. Loads the current data from the JSON file.
        2. Deletes the book with a title that matches the one in the provided `task` parameter.
        3. Overwrites the JSON file with the updated data.
        4. Updates the book list in the application's memory (self.tasks).
        5. Closes the book details window.
        6. Updates the interface to display the current data.
        """

        json_file_path = DATA_PATHS['reading']

        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Delete book from list
        data["books"] = [book for book in data.get("books", []) if book["title"] != task["title"]]

        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        # Refresh list
        self.tasks = data.get("books", [])

        self.task_window.destroy()

        self.add_books_database()

    def edit_book_info(self, task):
        """
        Opens an edit window for the book's information and saves the changes to the JSON file.

        :param task: A dictionary containing the current data of the book.
        :return: None
        """
        edit_window = Toplevel(self.canvas_mini_frame)
        edit_window.withdraw()
        edit_window.transient(self.canvas_mini_frame.winfo_toplevel())
        edit_window.grab_set()  # Make the edit window modal

        # Set the icon
        icon_path = APP['icon_path']  # Specify your .ico file path
        edit_window.iconbitmap(icon_path)

        center_window_on_parent(self.main_window, edit_window, 500, 400)

        # Font settings
        label_font = READING['toplevel_windows_font']
        entry_font = READING['toplevel_windows_font']

        # Fields for editing
        fields = {
            "Title": ("title", task.get("title", ""), "Enter the title of the book"),
            "Authors": ("authors", ", ".join(task.get("authors", [])), "Enter the authors separated by commas"),
            "Language": ("language", task.get("language", ""), "Enter the language of the book"),
            "Status": (
                "status", task.get("status", ""), "Select the reading status (e.g. Not started, In progress, Done)"),
            "Link": ("link", task.get("link", ""), "Enter the link to the book"),
            "Series": ("series", task.get("series", ""), "Enter the series name if applicable"),
            "Banner Path": (
                "banner_path", task.get("banner_path", ""), "Select an existing banner or enter a new path"),
            "Icon Path": ("icon_path", task.get("icon_path", ""), "Select an existing icon or enter a new path"),
            "Cover Path": ("cover_path", task.get("cover_path", ""), "Select the cover image path")
        }

        # Create input fields for each item
        entries = {}
        for i, (label_text, (field, value, tooltip_text)) in enumerate(fields.items()):
            label = tk.Label(edit_window, text=label_text + ":", font=label_font)
            label.grid(row=i, column=0, padx=10, pady=5, sticky="w")

            if field == "status":
                # Create a variable for status
                status_var = tk.StringVar(value=value)  # Set current value
                status_menu = tk.OptionMenu(edit_window, status_var, "Not started", "In progress", "Done")
                status_menu.config(font=entry_font)
                status_menu.grid(row=i, column=1, padx=10, pady=5, sticky="w")
                entries[field] = status_var  # Save StringVar for status
            elif field in ["banner_path", "icon_path"]:
                entry = tk.Entry(edit_window, font=entry_font, width=30)
                entry.insert(0, value)
                entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
                entry.bind("<Return>", lambda event: save_changes())
                # Create button to browse existing images
                select_button = tk.Button(edit_window, text="Browse", font=READING['button_font'],
                                          command=lambda field=field, entry=entry: select_existing_image(field, entry))
                select_button.grid(row=i, column=2, padx=5, pady=5)
                select_button.config(cursor="hand2")

                # Create tooltip for the input field
                ToolTip(entry, tooltip_text)
                entries[field] = entry
            elif field == "cover_path":
                entry = tk.Entry(edit_window, font=entry_font, width=30)
                entry.insert(0, value)
                entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
                entry.bind("<Return>", lambda event: save_changes())
                # Create button for selecting cover image
                select_button = tk.Button(edit_window, text="Browse", font=READING['button_font'],
                                          command=lambda field=field, entry=entry: select_cover_image(entry))
                select_button.grid(row=i, column=2, padx=5, pady=5)
                select_button.config(cursor="hand2")

                ToolTip(entry, tooltip_text)
                entries[field] = entry
            else:
                entry = tk.Entry(edit_window, font=entry_font, width=30)
                entry.insert(0, value)
                entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
                entry.bind("<Return>", lambda event: save_changes())
                ToolTip(entry, tooltip_text)
                entries[field] = entry

        # Function to select existing images
        def select_existing_image(field, entry):
            """
            Opens a dialog window to select an existing image file from the specified directory
            and inserts the path to the selected file into the corresponding entry field.

            :param field: The type of image being selected (e.g., "banner_path" or "icon_path").
                          This is used to determine the directory from which the images will be chosen.
            :param entry: The Tkinter Entry widget where the path to the selected image will be inserted.

            The function performs the following actions:
            1. Depending on the value of the `field` parameter, the initial directory for the dialog window is set:
               - "banner_path" opens the folder for banners.
               - "icon_path" opens the folder for icons.
            2. A dialog window is opened using `filedialog.askopenfilename`, where the user can select an image file.
            3. If a file is selected, the current text in the entry is cleared, and the path to the selected file is inserted into the entry field.
            """
            folder_path = None
            if field == "banner_path":
                folder_path = READING['book_banner_path']
            elif field == "icon_path":
                folder_path = READING['book_icon_path']

            file_path = filedialog.askopenfilename(title=f"Select {field.replace('_', ' ').title()}",
                                                   initialdir=folder_path,
                                                   filetypes=(("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"),
                                                              ("All Files", "*.*")))
            if file_path:
                entry.delete(0, tk.END)  # Clear current entry
                entry.insert(0, file_path)  # Insert selected file path

                entry.bind("<Return>", lambda event: save_changes())

        # Function to select cover image
        def select_cover_image(entry):
            """
            Opens a dialog window to select a book cover image and copies the selected image
            to the appropriate directory. If an old cover image exists, it is deleted.

            :param entry: The Tkinter Entry widget where the path to the selected cover image will be inserted.

            The function performs the following actions:
            1. Opens a dialog window using `filedialog.askopenfilename`, where the user can select a cover image.
            2. If a file is selected:
                - Deletes the old cover image if it exists, and its path is saved in `task["cover_path"]`.
                - Copies the new image to the cover images folder, creating the folder if it doesn't exist.
                - Updates the path to the new image in the entry field.
            """
            file_path = filedialog.askopenfilename(title="Select Cover Image",
                                                   filetypes=(("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"),
                                                              ("All Files", "*.*")))
            if file_path:
                # Delete the old cover image if it exists
                old_cover_path = task.get("cover_path", "")
                if old_cover_path and os.path.exists(old_cover_path):
                    os.remove(old_cover_path)  # Delete the old cover image

                # Copy the new cover image to the corresponding folder
                base_folder = READING['base_folder']
                target_folder = os.path.join(base_folder, "covers")

                os.makedirs(target_folder, exist_ok=True)  # Create folder if it doesn't exist

                # Get the new cover file name and target path
                file_name = os.path.basename(file_path)
                target_path = os.path.join(target_folder, file_name)

                shutil.copy(file_path, target_path)  # Copy the new cover image
                entry.delete(0, tk.END)  # Clear current entry
                entry.insert(0, target_path)  # Insert path to new file

                entry.bind("<Return>", lambda event: save_changes())

        # Button to save changes
        def save_changes():
            """
            Saves the changes made to the editable task fields in the JSON file.
            Updates the book data, overwrites the file, and refreshes the interface.

            The function performs the following actions:
            1. Updates the task object with values from the input fields.
            2. Loads data from the existing JSON file.
            3. Searches for the book in the list by a unique field (e.g., title) and updates its data.
            4. Overwrites the JSON file with the changes.
            5. Refreshes the task list with the updated data.
            6. Closes the editing window and refreshes the interface.

            :return: None
            """
            original_title = task["title"]

            # Update data in task
            for field, entry in entries.items():
                if field == "authors":
                    task[field] = [author.strip() for author in entry.get().split(",")]
                elif field == "status":
                    task[field] = entry.get()  # Get selected status
                elif field == "title":
                    task[field] = entry.get().strip()
                else:
                    task[field] = entry.get()

            json_file_path = DATA_PATHS['reading']
            # Load current JSON data
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Update the needed book in JSON
            for book in data.get("books", []):
                if book["title"] == original_title:
                    book.update(task)
                    break

            # Rewrite JSON with changes
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            # Update tasks array with new data from JSON
            self.tasks = data.get("books", [])  # Update self.tasks

            # Close the edit window and refresh the interface
            edit_window.destroy()

            # Refresh the interface
            self.refresh_books_view(task)
            self.add_books_database()

        save_button = tk.Button(edit_window, text="Save", font=READING['button_font'], command=save_changes)
        save_button.grid(row=len(fields), column=1, padx=10, pady=10, sticky="e")
        save_button.config(cursor="hand2")

        edit_window.deiconify()

    def refresh_books_view(self, task):
        """
        Updates the display of book information in the interface. Removes old widgets,
        adds a new banner, and updates the book information.

        The function performs the following actions:
        1. Removes all current widgets (books) from the screen.
        2. If there is a book banner path, it adds it to the interface.
        3. Updates the book information using the `add_books_info` method.

        :param task: An object containing the book's data, such as the banner path and other information.
        :return: None
        """
        for widget in self.canvas_mini_frame.winfo_children():
            widget.destroy()

        banner_path = task.get("banner_path")
        if banner_path and os.path.exists(banner_path):
            self.add_banner_book(self.canvas_mini_frame, banner_path)

        self.add_books_info(task)

    def add_banner_book(self, window, banner_path):
        """
        Loads the banner image and adds it to the specified window.
        It also automatically resizes the banner when the window size changes.

        The function performs the following actions:
        1. Loads the banner image from the provided `banner_path`.
        2. Creates a `Label` widget to display this image in the specified `window`.
        3. Performs an initial resizing of the banner using the `resize_banner_book` method.
        4. Binds the window resize event to a function so the banner automatically resizes when the window size changes.

        :param window: The window or container where the banner will be displayed.
        :param banner_path: The path to the banner image.
        :return: None
        """
        try:
            self.banner_image_original_book = Image.open(banner_path)
            self.banner_photo = ImageTk.PhotoImage(self.banner_image_original_book)
            self.banner_label_book = tk.Label(window, image=self.banner_photo, bg=INTERFACE['bg_color'])
            self.banner_label_book.pack(pady=(2, 10), fill=tk.X)

            self.resize_banner_book()

            self.task_window.bind("<Configure>", self.resize_banner_book)
        except Exception as e:
            print(f"Error banner loading: {e}")

    def resize_banner_book(self, event=None):
        """
        Resizes the banner based on the current width of the window, maintaining the image's aspect ratio.

        The function performs the following actions:
        1. Sets a fixed height for the banner.
        2. Retrieves the current width of the window displaying the banner.
        3. Calculates the new width and height of the banner, maintaining the image's aspect ratio.
        4. Applies resizing using the `Image.LANCZOS` method to preserve the image's quality.
        5. Updates the widget displaying the banner with the new image.

        :param event: The event passed when the window is resized. Defaults to None.
        :return: None
        """
        if hasattr(self, 'banner_image_original'):
            fixed_height = 150

            width = self.task_window.winfo_width()

            if width <= 0:
                return

            new_width = width
            new_height = fixed_height

            banner_image = self.banner_image_original_book.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.banner_photo = ImageTk.PhotoImage(banner_image)

            self.banner_label_book.configure(image=self.banner_photo)
            self.banner_label_book.image = self.banner_photo

    def add_quote_and_image(self):
        """
        Adds a frame to the interface with an image and a quote.

        The function performs the following actions:
        1. Creates a frame to hold the image.
        2. Creates a frame for the quote with a vertical line on the left.
        3. Displays the quote using the Arial font, size 12, in italics.
        4. Adds the image in the grid next to the quote.

        :return: None
        """
        image_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        image_frame.pack(pady=5)

        quote_frame = tk.Frame(image_frame, bg=INTERFACE['bg_color'])
        quote_frame.grid(row=0, column=1, padx=(0, 10), pady=5)

        # Vertical line
        line = tk.Canvas(quote_frame, width=2, bg=INTERFACE['separator'], height=100)
        line.pack(side=tk.LEFT, padx=(0, 10))

        # Quote text
        quote_text = READING['quote_text']
        label_quote = tk.Label(quote_frame, text=quote_text, font=READING['quote_font'], bg=INTERFACE['bg_color'],
                               wraplength=READING['quote_wraplength'])
        label_quote.pack(side=tk.LEFT, fill=tk.BOTH)

        add_image_to_grid(image_frame, READING['image_link'], row=0, column=0,
                          height=200, width=300, rowspan=1)

    def navigate_to_lists_for_life(self):
        """
        Function to return to the #Lists_for_life page.

        :return: None
        """
        self.main_window.show_tab_content("lists_for_life")

    def load_tasks(self):
        """
        Load from JSON

        :return: None
        """
        if os.path.exists(self.json_file):
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data['books']
        return []
