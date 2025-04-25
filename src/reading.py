from pathlib import Path
from config.imports import *
from config.tooltip import ToolTip
from config.utils import add_source_label_second_level as add_source_label_lists_for_life, load_icon_image, \
    add_icon_image
from config.settings import READING


async def upload_image(file_path: str):
    """
    Uploads an image to the server.

    Args:
        file_path (str): The local file path of the image to be uploaded.

    Returns:
        str: The name of the uploaded image file if successful, otherwise raises an error message.
    """
    file_name = Path(file_path).name
    try:
        async with aiohttp.ClientSession() as session:
            with open(file_path, "rb") as file:
                form = aiohttp.FormData()
                form.add_field("file", file, filename=file_name)

                async with session.post(f"{SERVER_URL}/upload_book_image", data=form, ssl=SSL_ENABLED) as response:
                    if response.status == 200:
                        result = await response.json()
                        return Path(result["file_path"]).name
                    elif response.status == 400:
                        messagebox.showerror("Error", "File already exists on server!")
                    else:
                        messagebox.showerror("Error", f"Failed to upload image: {response.status}")
    except Exception as e:
        messagebox.showerror("Error", f"Image upload failed: {e}")


async def save_book(new_book, add_window):
    """
    Sends a request to the server to add a new book.

    Args:
        new_book (dict): A dictionary containing the details of the new book to be added.
        add_window (tk.Toplevel): The window where the book details are entered.

    Returns:
        None: Displays success or error message based on the server's response.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{SERVER_URL}/add_book", json=new_book, ssl=SSL_ENABLED) as response:
                if response.status == 200:
                    result = await response.json()
                    messagebox.showinfo("Success", "Book added successfully!")
                    add_window.destroy()
                else:
                    messagebox.showerror("Error", f"Failed to add book: {response.status}")
    except Exception as e:
        messagebox.showerror("Error", f"Error adding book: {e}")


async def get_files_from_server(endpoint):
    """
    Sends a GET request to the server to fetch files from a specific endpoint.

    Args:
        endpoint (str): The endpoint of the server where the files are stored or listed.

    Returns:
        list: A list of files retrieved from the server in JSON format. If an error occurs, returns an empty list.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SERVER_URL}/{endpoint}", ssl=SSL_ENABLED) as response:
                response.raise_for_status()
                return await response.json()
    except aiohttp.ClientError as e:
        print(f"Error fetching {endpoint}: {e}")
        return []


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
            async with session.get(f"{SERVER_URL}/get_books", ssl=SSL_ENABLED) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Failed to load tasks: {response.status}")
    except aiohttp.ClientError as e:
        print(f"Connection error: {e}")
    return []


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


async def get_banner_image(banner_path):
    """
    Gets banner from server.

    Args:
        banner_path: Banner path on server

    Returns:
        BytesIO: The image of the banner fetched from the server.

    """
    response = requests.get(f"{SERVER_URL}/assets/{banner_path}", verify=VERIFY_ENABLED)
    response.raise_for_status()

    return BytesIO(response.content)


async def save_changes_to_the_server_image(entries, old_cover, old_cover_path_data):
    """
    Asynchronously updates the cover image on the server by deleting the old image and uploading the new one.

    This method checks if the cover image path has changed, and if so, it deletes the old cover image from the server
    and uploads the new one. The image file is sent as part of a POST request, and any errors encountered during
    the process are caught and printed.

    Args:
        entries (dict): A dictionary containing the updated book details, including the new cover image path.
        old_cover (str): The previous cover image path that needs to be deleted from the server.
        old_cover_path_data (dict): A dictionary containing the path to the old cover image, used for deletion on the server.

    Returns:
        None
    """
    async with aiohttp.ClientSession() as session:
        if entries["cover_path"] and entries["cover_path"] != old_cover:
            async with session.delete(f"{SERVER_URL}/delete_book_image",
                                      json=old_cover_path_data, ssl=SSL_ENABLED) as image_response:
                image_response.raise_for_status()

            file_path = entries["cover_path"]
            new_file_name = Path(file_path).name

            try:
                with open(file_path, "rb") as file:
                    form = aiohttp.FormData()
                    form.add_field("file", file, filename=new_file_name)

                    async with session.post(f"{SERVER_URL}/upload_book_image",
                                            data=form, ssl=SSL_ENABLED) as response:
                        response.raise_for_status()
            except Exception as e:
                print(f"Error image load: {e}")


async def save_changes_to_the_server_info(updated_book_data):
    """
    Asynchronously updates the book information on the server.

    This method sends a PUT request to update the book details on the server. It includes the updated book data
    in JSON format. If any errors occur during the request, they are caught and printed.

    Args:
        updated_book_data (dict): A dictionary containing the updated information of the book, such as title, authors,
                                   status, etc.

    Returns:
        None
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.put(f"{SERVER_URL}/update_books_info",
                                   json=updated_book_data, ssl=SSL_ENABLED) as update_response:
                update_response.raise_for_status()
    except Exception as e:
        print(f"Error updating data: {e}")


class Reading(tk.Frame):
    """
    The Reading class is responsible for creating the interface for the 'Reading' tab.
    It includes a book database with the ability to delete, add, and view books by the user.
    """
    def __init__(self, parent, main_window):
        """
        Initializes the window for displaying tasks, a banner, and other interface elements.

        :param parent: The parent element for the current window (e.g., main frame or window).
        :param main_window: The main window of the application, passed for interacting with the main interface.

        The constructor performs the following actions:
        1. Sets the background color of the current window to #F0F0F0.
        2. Initializes variables for the number of tasks displayed by categories (Not Started, In Progress, Done).
        3. Loads tasks from the server.
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
        self.main_window.disable_buttons()

        self.not_started_loaded = 50  # "Not Started" books number
        self.in_progress_loaded = 50  # "In Progress" books number
        self.done_loaded = 50  # "Done" books number
        self.tasks_per_page = 50  # Iteration number

        self.tasks = asyncio.run(load_tasks_from_server())

        self.clickable_label = add_source_label_lists_for_life(
            self,  # Parent
            icon_path_1=ICONS_PATHS['lists_for_life'],
            clickable_text="#Lists_for_life /",
            click_command=self.navigate_to_lists_for_life,
            icon_path_2=ICONS_PATHS['reading'],
            text=PAGES_NAMES['reading']
        )
        self.clickable_label["state"] = "disable"

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
                                             command=self.populate_columns)
        language_filter_menu.config(font=READING['filter_font'])
        language_filter_menu.pack(side=tk.LEFT, padx=5)
        language_filter_menu.config(cursor="hand2")

        # Title filter
        title_filter_entry = tk.Entry(self.top_frame, textvariable=self.title_filter_var, font=READING['filter_font'])
        title_filter_entry.pack(side=tk.LEFT, padx=5)
        title_filter_entry.bind("<KeyRelease>", lambda event: self.populate_columns())

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

        # Remove load button if it exists
        if hasattr(self, 'load_button_frame'):
            for widget in self.load_button_frame.winfo_children():
                widget.destroy()  # Remove the old button
            self.load_button_frame.destroy()  # Remove the frame if it exists

        self.add_load_button()

        self.main_window.enable_buttons()
        self.clickable_label["state"] = "normal"

    def add_load_button(self):
        """
        Creates and adds a "Load more" button to the interface. The button is placed in a frame
        that expands vertically and has padding around it. When clicked, the button triggers the
        `load_more_tasks` method to load additional tasks.

        The button is styled with custom font and background color as defined in the `READING` dictionary,
        and the cursor changes to a hand when hovered over the button to indicate it's clickable.

        Returns:
            None
        """
        self.load_button_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        self.load_button_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Load button
        load_more_button = tk.Button(self.load_button_frame, text="Load more", font=READING['button_font'],
                                     command=self.load_more_tasks, bg=READING['load_more_button_color'])
        load_more_button.pack(side=tk.BOTTOM, padx=5, pady=(10, 0))
        load_more_button.config(cursor="hand2")

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
        self.populate_columns()
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

    def populate_columns(self, *args):
        """
        Populate columns with books.

        Args:
            *args: Optional arguments passed automatically when used as an event handler
                  (e.g., from OptionMenu).

        Returns: None

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

    def save_book_sync(self, entries, add_window):
        """
        Validates the book data, processes the book information, and saves it. This function ensures that all required fields are filled
        and handles the image upload before saving the book to the database.

        Args:
            entries (dict): A dictionary containing the book details (e.g., title, authors, language, status, cover image, etc.).
            add_window (Tkinter.Toplevel): The window that holds the form for adding a new book. This will be closed upon successful save.

        Returns:
            None: The function does not return anything. It either shows error/warning messages or proceeds with the save operation.
        """
        existing_titles = {book["title"].lower() for book in self.tasks}
        if entries["title"].lower() in existing_titles:
            messagebox.showwarning("Warning", f'A book with the title "{entries["title"]}" already exists!')
            add_window.lift()
            return

        if not entries["title"]:
            messagebox.showerror("Error", "Please enter the title of the book!")
            add_window.lift()
            return

        if not entries["authors"]:
            messagebox.showerror("Error", "Please enter authors of the book!")
            add_window.lift()
            return

        if not entries["language"]:
            messagebox.showerror("Error", "Please select a language for the book!")
            add_window.lift()
            return

        if not entries["status"]:
            messagebox.showerror("Error", "Please select a status for the book!")
            add_window.lift()
            return

        if not entries["cover_path"]:
            messagebox.showerror("Error", "Please upload a cover image for the book!")
            add_window.lift()
            return

        if not os.path.exists(entries["cover_path"]):
            messagebox.showerror("Error", f"The selected image file was not found:\n{entries["cover_path"]}")
            add_window.lift()
            return

        new_book = {}
        for field, entry in entries.items():
            if field == "authors":
                authors = entries[field].split(",")
                new_book[field] = [author.strip() for author in authors]
            else:
                new_book[field] = entries[field]

        if new_book["cover_path"]:
            uploaded_cover = asyncio.run(upload_image(new_book["cover_path"]))
            new_book["cover_path"] = f"{READING['base_folder']}/{uploaded_cover}"

        if new_book["icon_path"]:
            new_book["icon_path"] = f"{READING['book_icon_path']}/{new_book['icon_path']}.png"

        if new_book["banner_path"]:
            new_book["banner_path"] = f"{READING['book_banner_path']}/{new_book['banner_path']}.png"

        if uploaded_cover is not None:
            asyncio.run(save_book(new_book, add_window))

            self.tasks.append(new_book)
            self.add_books_database()

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
        icons = asyncio.run(get_files_from_server("icons"))
        banners = asyncio.run(get_files_from_server("banners"))

        icons = icons.get('icons', []) if isinstance(icons, dict) else icons
        banners = banners.get('banners', []) if isinstance(banners, dict) else banners

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
            elif field == "banner_path":
                banners = [""] + banners
                banner_var = tk.StringVar(value=banners[0] if banners else "")  # Set default value
                banner_menu = ttk.Combobox(add_window, textvariable=banner_var, values=banners, font=entry_font,
                                           state="readonly")
                banner_menu.grid(row=i, column=1, padx=10, pady=5, sticky="w")
                entries[field] = banner_var
                banner_menu.bind("<ButtonPress>", self.disable_scroll)  # Disable scroll
                banner_menu.bind("<ButtonRelease>", self.enable_scroll)  # Enable scroll
            elif field == "icon_path":
                icons = [""] + icons
                icon_var = tk.StringVar(value=icons[0] if icons else "")  # Set default value
                icon_menu = ttk.Combobox(add_window, textvariable=icon_var, values=icons, font=entry_font,
                                         state="readonly")
                icon_menu.grid(row=i, column=1, padx=10, pady=5, sticky="w")
                entries[field] = icon_var
                icon_menu.bind("<ButtonPress>", self.disable_scroll)  # Disable scroll
                icon_menu.bind("<ButtonRelease>", self.enable_scroll)  # Enable scroll
            elif field == "cover_path":
                # Create field for cover image path with browse button
                entry = tk.Entry(add_window, font=entry_font, width=30)
                entry.insert(0, value)
                entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
                entry.bind("<Return>", lambda event: self.save_book_sync({
                    'title': entries['title'].get(),
                    'authors': entries['authors'].get(),
                    'language': entries['language'].get(),
                    'status': entries['status'].get(),
                    'link': entries['link'].get(),
                    'series': entries['series'].get(),
                    'banner_path': entries['banner_path'].get(),
                    'icon_path': entries['icon_path'].get(),
                    'cover_path': entries['cover_path'].get()
                }, add_window))
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
                entry.bind("<Return>", lambda event: self.save_book_sync({
                    'title': entries['title'].get(),
                    'authors': entries['authors'].get(),
                    'language': entries['language'].get(),
                    'status': entries['status'].get(),
                    'link': entries['link'].get(),
                    'series': entries['series'].get(),
                    'banner_path': entries['banner_path'].get(),
                    'icon_path': entries['icon_path'].get(),
                    'cover_path': entries['cover_path'].get()
                }, add_window))
                ToolTip(entry, tooltip_text)

                entries[field] = entry

        def select_image(field, entry):
            """
            Opens a dialog window to select an image,
            then displays the path to the new file in the input field.

            :param field: A string indicating the type of image being selected.
            :param entry: The input field (entry) where the path to the new image file will be displayed.
            :return: None

            Actions:
            1. A dialog window opens to select an image.
            2. The selected file is copied to the corresponding image folder on server.
            3. If a file is selected, the current text in the input field is cleared, and the path to the new image file is inserted.
            """
            file_path = filedialog.askopenfilename(title=f"Select {field.replace('_', ' ').title()}",
                                                   filetypes=(("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"),
                                                              ("All Files", "*.*")))
            if file_path:
                entry.delete(0, tk.END)  # Clear current entry
                entry.insert(0, file_path)  # Insert path to the selected file
                entry.bind("<Return>",
                           lambda event: self.save_book_sync({
                               'title': entries['title'].get(),
                               'authors': entries['authors'].get(),
                               'language': entries['language'].get(),
                               'status': entries['status'].get(),
                               'link': entries['link'].get(),
                               'series': entries['series'].get(),
                               'banner_path': entries['banner_path'].get(),
                               'icon_path': entries['icon_path'].get(),
                               'cover_path': entries['cover_path'].get()
                           }, add_window))  # Optional: handle save if needed

        # Button to save the book
        save_button = tk.Button(add_window, text="Save", font=READING['button_font'],
                                command=lambda: self.save_book_sync({
                                    'title': entries['title'].get(),
                                    'authors': entries['authors'].get(),
                                    'language': entries['language'].get(),
                                    'status': entries['status'].get(),
                                    'link': entries['link'].get(),
                                    'series': entries['series'].get(),
                                    'banner_path': entries['banner_path'].get(),
                                    'icon_path': entries['icon_path'].get(),
                                    'cover_path': entries['cover_path'].get()
                                }, add_window))
        save_button.grid(row=len(fields), column=0, columnspan=3, pady=10, sticky="n")
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

            icon = asyncio.run(load_icon_image(SERVER_URL, icon_path, VERIFY_ENABLED))
            button.config(image=icon, compound='left', padx=5)
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
        if banner_path:
            self.canvas_mini.pack(side=tk.LEFT, expand=1, fill=tk.BOTH)
            self.add_banner_book(self.canvas_mini_frame, banner_path)
        else:
            self.window_area_mini = self.canvas_mini.create_window(
                (0, 0), window=self.canvas_mini_frame, anchor="center"
            )

            # Resize banner
            def center_frame_on_canvas(event):
                """
                Centers the specified frame (window_area_mini) on the canvas when the canvas is resized.
                The method calculates the center of the canvas and moves the frame to that position.

                Args:
                    event: The event object triggered by a canvas resize. It contains information about the
                           current size of the canvas.

                Returns:
                    None
                """
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
            link_label = tk.Label(books_info_frame, text="Click", bg=INTERFACE['bg_color'], anchor="w", fg="blue",
                                  cursor="hand2",
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
        if cover_path:
            original_image = asyncio.run(add_icon_image(cover_path))

            cover_image = original_image.resize(
                (READING['cover_width'], READING['cover_height']),
                Image.Resampling.LANCZOS
            )
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
        Deletes a book from the server.

        :param task: A dictionary containing the book's data to be deleted.
        :return: None
        """
        asyncio.run(self.delete_book_from_server(task))

        self.add_books_database()

        self.task_window.destroy()

    async def delete_book_from_server(self, task):
        """
        Deletes a book from the server and its image.

        :param task: A dictionary containing the book's data to be deleted.
        :return: None
        """
        book_data = {
            "title": task["title"]
        }

        cover_path_data = {
            "cover_path": task["cover_path"]
        }

        async with aiohttp.ClientSession() as session:
            try:
                # Delete the book
                async with session.delete(f"{SERVER_URL}/delete_book", json=book_data, ssl=SSL_ENABLED) as response:
                    response.raise_for_status()

                # Delete image
                if task["cover_path"]:
                    async with session.delete(f"{SERVER_URL}/delete_book_image",
                                              json=cover_path_data, ssl=SSL_ENABLED) as image_response:
                        image_response.raise_for_status()

                self.tasks = [book for book in self.tasks if book["title"] != task["title"]]

            except aiohttp.ClientResponseError as e:
                print(f"HTTP error occurred: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")

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

        old_title = task.get("title", "")
        old_cover = task.get("cover_path", "")

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
        icons = asyncio.run(get_files_from_server("icons"))
        banners = asyncio.run(get_files_from_server("banners"))
        icons = icons.get('icons', []) if isinstance(icons, dict) else icons
        banners = banners.get('banners', []) if isinstance(banners, dict) else banners

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
            elif field == "banner_path":
                banners = [""] + banners
                banner_var = tk.StringVar()
                file_name = os.path.splitext(os.path.basename(value))[0]
                banner_value = file_name if file_name in banners else banners[0]
                banner_var.set(banner_value)

                banner_menu = ttk.Combobox(edit_window, textvariable=banner_var, values=banners, font=entry_font,
                                           state="readonly")
                banner_menu.grid(row=i, column=1, padx=10, pady=5, sticky="w")
                entries[field] = banner_var

                banner_menu.bind("<ButtonPress>", self.disable_scroll)  # Disable scroll
                banner_menu.bind("<ButtonRelease>", self.enable_scroll)  # Enable scroll
            elif field == "icon_path":
                icons = [""] + icons
                icon_var = tk.StringVar()
                file_name = os.path.splitext(os.path.basename(value))[0]
                icon_value = file_name if file_name in icons else icons[0]
                icon_var.set(icon_value)

                icon_menu = ttk.Combobox(edit_window, textvariable=icon_var, values=icons, font=entry_font,
                                         state="readonly")
                icon_menu.grid(row=i, column=1, padx=10, pady=5, sticky="w")
                entries[field] = icon_var

                icon_menu.bind("<ButtonPress>", self.disable_scroll)  # Disable scroll
                icon_menu.bind("<ButtonRelease>", self.enable_scroll)  # Enable scroll
            elif field == "cover_path":
                # Create field for cover image path with browse button
                entry = tk.Entry(edit_window, font=entry_font, width=30)
                entry.insert(0, value)
                entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
                entry.config(state="readonly")
                entry.bind("<Return>", lambda event: self.save_changes({
                    'title': entries['title'].get(),
                    'authors': entries['authors'].get(),
                    'language': entries['language'].get(),
                    'status': entries['status'].get(),
                    'link': entries['link'].get(),
                    'series': entries['series'].get(),
                    'banner_path': entries['banner_path'].get(),
                    'icon_path': entries['icon_path'].get(),
                    'cover_path': entries['cover_path'].get()
                }, edit_window, old_title, old_cover))
                select_button = tk.Button(edit_window, text="Browse", font=READING['button_font'],
                                          command=lambda field=field, entry=entry: select_image(field, entry))
                select_button.grid(row=i, column=2, padx=5, pady=5)
                select_button.config(cursor="hand2")
                ToolTip(entry, tooltip_text)

                entries[field] = entry
            else:
                entry = tk.Entry(edit_window, font=entry_font, width=30)
                entry.insert(0, value)
                entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
                entry.bind("<Return>", lambda event: self.save_changes(
                    {
                        'title': entries['title'].get(),
                        'authors': entries['authors'].get(),
                        'language': entries['language'].get(),
                        'status': entries['status'].get(),
                        'link': entries['link'].get(),
                        'series': entries['series'].get(),
                        'banner_path': entries['banner_path'].get(),
                        'icon_path': entries['icon_path'].get(),
                        'cover_path': entries['cover_path'].get()
                    }, edit_window, old_title, old_cover
                ))
                ToolTip(entry, tooltip_text)
                entries[field] = entry

        def select_image(field, entry):
            """
            Opens a dialog window to select an image file from the specified directory
            and inserts the path to the selected file into the corresponding entry field.

            :param field: The type of image being selected.
            :param entry: The Tkinter Entry widget where the path to the selected image will be inserted.

            The function performs the following actions:
            1. A dialog window is opened using `filedialog.askopenfilename`, where the user can select an image file.
            2. If a file is selected, the current text in the entry is cleared, and the path to the selected file is inserted into the entry field.
            """
            file_path = filedialog.askopenfilename(title=f"Select {field.replace('_', ' ').title()}",
                                                   filetypes=(("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"),
                                                              ("All Files", "*.*")))

            if file_path:
                entry.config(state="normal")
                entry.delete(0, tk.END)  # Clear current entry
                entry.insert(0, file_path)  # Insert selected file path
                entry.config(state="readonly")

                entry.bind("<Return>", lambda event: self.save_changes(
                    {
                        'title': entries['title'].get(),
                        'authors': entries['authors'].get(),
                        'language': entries['language'].get(),
                        'status': entries['status'].get(),
                        'link': entries['link'].get(),
                        'series': entries['series'].get(),
                        'banner_path': entries['banner_path'].get(),
                        'icon_path': entries['icon_path'].get(),
                        'cover_path': entries['cover_path'].get()
                    }, edit_window, old_title, old_cover
                ))

        save_button = tk.Button(edit_window, text="Save", font=READING['button_font'],
                                command=lambda: self.save_changes(
                                    {
                                        'title': entries['title'].get(),
                                        'authors': entries['authors'].get(),
                                        'language': entries['language'].get(),
                                        'status': entries['status'].get(),
                                        'link': entries['link'].get(),
                                        'series': entries['series'].get(),
                                        'banner_path': entries['banner_path'].get(),
                                        'icon_path': entries['icon_path'].get(),
                                        'cover_path': entries['cover_path'].get()
                                    }, edit_window, old_title, old_cover
                                ))
        save_button.grid(row=len(fields), column=1, padx=10, pady=10, sticky="n")
        save_button.config(cursor="hand2")

        edit_window.deiconify()

    def save_changes(self, entries, edit_window, old_title, old_cover):
        """
        Saves the changes made to a book's information and updates the server with the new data.

        This method processes the updated book information, including the title, authors, cover, and icon paths.
        It also uploads the new cover image and other relevant data to the server, then refreshes the local
        book list and updates the view accordingly.

        Args:
            entries (dict): A dictionary containing the updated book details such as title, authors, language, etc.
            edit_window (tk.Toplevel): The window where the book information was being edited. It is closed after saving the changes.
            old_title (str): The title of the book before the changes were made. Used to identify the book for updates.
            old_cover (str): The current cover image path, used to manage the old cover when replacing it.

        Returns:
            None
        """
        existing_titles = {book["title"] for book in self.tasks if book["title"] != old_title}

        if entries["title"] in existing_titles:
            messagebox.showwarning("Warning", f'A book with the title "{entries["title"]}" already exists!')
            edit_window.lift()
            return

        if not entries["title"]:
            messagebox.showerror("Error", "Please enter the title of the book!")
            edit_window.lift()
            return

        if not entries["authors"]:
            messagebox.showerror("Error", "Please enter authors of the book!")
            edit_window.lift()
            return

        if not entries["language"]:
            messagebox.showerror("Error", "Please select a language for the book!")
            edit_window.lift()
            return

        if not entries["status"]:
            messagebox.showerror("Error", "Please select a status for the book!")
            edit_window.lift()
            return

        if not entries["cover_path"]:
            messagebox.showerror("Error", "Please upload a cover image for the book!")
            edit_window.lift()
            return

        entries['authors'] = [author.strip() for author in entries['authors'].split(',')]
        old_filename = os.path.basename(old_cover)
        new_filename = os.path.basename(entries['cover_path'])

        new_cover_filename = os.path.basename(entries['cover_path'])
        new_cover_server_path = f"{READING['base_folder']}/{new_cover_filename}"

        for book in self.tasks:
            if (book["cover_path"] == new_cover_server_path
                    and book["title"] != old_title):
                messagebox.showerror(
                    "Error",
                    f"Cover image '{new_cover_filename}' is already used by book '{book['title']}'!\n"
                    "Please use a different image."
                )
                edit_window.lift()
                return

        if entries['icon_path']:
            entries['icon_path'] = f"{READING['book_icon_path']}/{entries['icon_path']}.png"

        if entries['banner_path']:
            entries['banner_path'] = f"{READING['book_banner_path']}/{entries['banner_path']}.png"

        old_cover_path_data = {"cover_path": f"{READING['base_folder']}/{old_filename}"}

        asyncio.run(
            save_changes_to_the_server_image(entries, old_cover, old_cover_path_data))

        entries['cover_path'] = f"{READING['base_folder']}/{new_filename}"

        updated_book_data = {
            "old_title": old_title,
            "title": entries["title"],
            "authors": entries["authors"],
            "language": entries["language"],
            "status": entries["status"],
            "link": entries["link"],
            "series": entries["series"],
            "banner_path": entries["banner_path"],
            "icon_path": entries["icon_path"],
            "cover_path": entries["cover_path"]
        }

        asyncio.run(save_changes_to_the_server_info(updated_book_data))

        self.tasks = asyncio.run(load_tasks_from_server())

        edit_window.destroy()
        self.refresh_books_view(entries)
        self.add_books_database()

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
        if banner_path:
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
            banner_path = asyncio.run(get_banner_image(banner_path))

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

            if hasattr(self, 'banner_label_book') and self.banner_label_book.winfo_exists():
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
