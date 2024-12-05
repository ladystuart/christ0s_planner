from config.imports import *
from config.settings import BLOG
from config.tooltip import ToolTip
from config.utils import add_header_label


def add_title_icon(header_frame, icon_width, icon_height, row, column, icon):
    """
    Adds an icon (image) to a header frame at a specific position. The icon is resized
    according to the provided width and height, and displayed in the given row and column
    of the frame.

    :param header_frame: The parent frame where the icon will be placed (typically a header frame).
    :param icon_width: The desired width to resize the icon to.
    :param icon_height: The desired height to resize the icon to.
    :param row: The row in the grid where the icon will be placed.
    :param column: The column in the grid where the icon will be placed.
    :param icon: The file path to the icon image that will be added to the header.
    :return: None
    """
    try:
        left_icon_image = Image.open(icon)
        left_icon_resized = left_icon_image.resize((icon_width, icon_height), Image.Resampling.LANCZOS)
        left_icon = ImageTk.PhotoImage(left_icon_resized)

        left_icon_label = tk.Label(header_frame, image=left_icon, bg=INTERFACE['bg_color'])
        left_icon_label.image = left_icon

        left_icon_label.grid(row=row, column=column, padx=5)
    except Exception as e:
        print(f"Error left icon load: {e}")


class Blog(tk.Frame):
    """
    A class representing the blog section of the application, containing various widgets
    like labels, inputs, and images, as well as managing the layout and interactions.
    """

    def __init__(self, parent, json_file, main_window):
        """
        Initializes the Blog frame with the provided parent window, JSON data file, and main window reference.

        :param parent: The parent window that will contain this frame.
        :param json_file: Path to the JSON file containing blog data.
        :param main_window: Reference to the main application window.
        """
        super().__init__(parent)
        self.configure(bg=INTERFACE['bg_color'])
        self.main_window = main_window
        self.parent = parent

        self.header_frames = []
        self.text_widgets = []

        self.json_file = json_file
        self.blog_data = self.load_blog_data()  # Initialize wishlist_items

        self.icon_image_original = Image.open(ICONS_PATHS['blog'])  # Year icon path
        self.icon_image = self.icon_image_original.resize((20, 20), Image.Resampling.LANCZOS)
        self.icon_photo = ImageTk.PhotoImage(self.icon_image)

        add_source_label(self, ICONS_PATHS['blog'], PAGES_NAMES['blog'],
                         bg_color=INTERFACE['bg_color'], font=INTERFACE['source_label_font'])

        # Banner add
        self.banner_label, self.banner_image_original = add_banner(
            self,
            banner_path=BANNER_PATHS['blog'],
            bg_color=INTERFACE['bg_color']
        )

        # resize_banner
        if self.banner_label and self.banner_image_original:
            self.bind("<Configure>", lambda event: resize_banner(
                self,
                self.banner_label,
                self.banner_image_original
            ))

        add_icon_and_label(self, text=PAGES_NAMES['blog'], icon_path=ICONS_PATHS['blog'],
                           bg_color=INTERFACE['bg_color'])
        add_separator(parent=self, color=INTERFACE['separator'])

        self.frame = tk.Frame(self, bg="#E0E0D8", padx=10, pady=10)
        self.frame.pack(fill="both", expand=True)

        pin_icon = PhotoImage(file=BLOG['idea_icon_path']).subsample(2, 2)
        icon_label = tk.Label(self.frame, image=pin_icon, bg=BLOG['email_label_bg'])
        icon_label.image = pin_icon
        icon_label.grid(row=0, column=0, padx=(0, 10))

        email = self.blog_data.get("mail", "No email found")
        email_entry = tk.Entry(self.frame, bg=BLOG['email_label_bg'],
                               fg="black",
                               font=BLOG['email_label_font'],
                               bd=0,
                               readonlybackground=BLOG['email_label_bg'],
                               width=30)
        email_entry.insert(0, email)
        email_entry.config(state="readonly")
        email_entry.grid(row=0, column=1, sticky="w")

        self.add_title_frame_with_icon()
        self.add_table_frame()

        add_separator(parent=self, color=INTERFACE['separator'])

        self.add_title_frame(text="Links")
        self.add_links_list()
        self.add_icon_and_text()

        add_separator(parent=self, color=INTERFACE['separator'])

        self.add_quote_and_image()

        self.add_button()

    def add_button(self):
        """
        Creates and adds a button to the right side of the frame.
        The button displays an icon and text, and when clicked, it triggers the `on_button_click` method.

        :return: None
        """
        right_frame = tk.Frame(self)
        right_frame.pack(side="right", padx=20, pady=20)

        icon_image = Image.open(BLOG['lightbulb_icon_path'])
        icon_image = icon_image.resize((24, 24), Image.Resampling.LANCZOS)
        icon_photo = ImageTk.PhotoImage(icon_image)

        button = tk.Button(
            right_frame,
            text="Ideas and plans",
            command=lambda: self.on_button_click({"title": "Ideas and plans"}),
            bg=INTERFACE['bg_color'],
            bd=1,
            relief=BLOG['ideas_and_plans_button_relief'],
            padx=10,
            pady=10,
            compound='left',
            image=icon_photo,
            font=BLOG['ideas_and_plans_font']
        )
        button.image = icon_photo
        button.config(cursor="hand2")
        button.pack()

    def on_button_click(self, item):
        """
        Handles the button click event. When the button is clicked, it clears the current canvas
        and displays a new frame for 'Ideas and Plans'.

        :param item: A dictionary or data passed with the button click event (not used in this specific implementation)
        :return: None
        """
        clear_canvas(self.parent)

        from src.ideas_and_plans import IdeasAndPlans
        plans_frame = IdeasAndPlans(self.parent, json_file=DATA_PATHS['ideas_and_plans'], main_window=self.main_window)
        plans_frame.pack(fill=tk.BOTH, expand=True)

        reset_canvas_view(self.main_window)

    def add_quote_and_image(self):
        """
        This method adds a quote, an image, and a to-do list to the blog page.
        It also provides functionality to add and delete tasks from the to-do list.

        :return: None
        """
        to_do_items = self.blog_data.get("to_do", [])

        image_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        image_frame.pack(pady=5)

        quote_frame = tk.Frame(image_frame, bg=INTERFACE['bg_color'])
        quote_frame.grid(row=len(to_do_items) + 1, column=0, padx=(0, 10), pady=5)

        line = tk.Canvas(quote_frame, width=2, bg=INTERFACE['separator'], height=100)
        line.pack(side=tk.LEFT, padx=(0, 10))

        quote_text = BLOG['quote_text']
        label_quote = tk.Label(quote_frame, text=quote_text, font=BLOG['quote_font'], bg=INTERFACE['bg_color'],
                               wraplength=BLOG['quote_wraplength'])
        label_quote.pack(side=tk.LEFT, fill=tk.BOTH)

        add_image_to_grid(image_frame, BLOG['image_link'], row=0, column=0, height=450,
                          width=300, rowspan=len(to_do_items) + 1)

        to_do_frame = tk.Frame(image_frame, bg=INTERFACE['bg_color'])
        to_do_frame.grid(row=0, column=1, columnspan=3, sticky="ew", padx=10, pady=10)

        add_header_label(to_do_frame, row=0, column=0, text="To do")

        add_title_icon(to_do_frame, 32, 32, row=0, column=1, icon=BLOG['stars_icon_path'])

        separator = tk.Frame(to_do_frame, bg=INTERFACE['separator'], height=1)
        separator.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)

        new_task_var = tk.StringVar()

        tasks_frame = tk.Frame(image_frame, bg=INTERFACE['bg_color'])
        tasks_frame.grid(row=1, column=1, columnspan=3, sticky="ew", padx=10, pady=10)

        def add_task(event=None):
            """
            Adds a new task to the to-do list.

            :param event: The event triggered by pressing 'Enter' or clicking the "Add Task" button
            :return: None
            """
            new_task = new_task_var.get()
            if new_task:
                to_do_items.append({"task": new_task, "completed": False})
                new_task_var.set('')

                self.blog_data["to_do"] = to_do_items
                self.save_blog_data()

                update_task_list()

        def delete_task(index):
            """
            Deletes a task from the to-do list after confirmation.

            :param index: The index of the task to delete
            :return: None
            """
            confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to delete this task?")

            if confirmation:
                del to_do_items[index]
                self.blog_data["to_do"] = to_do_items
                self.save_blog_data()
                update_task_list()

        def update_task_list():
            """
            Updates the task list by displaying the current to-do items in the tasks_frame.

            :return: None
            """
            for widget in tasks_frame.winfo_children():
                if widget not in [new_task_entry, add_task_button]:
                    widget.destroy()

            for i, task_data in enumerate(to_do_items):
                task = task_data["task"]
                completed = task_data["completed"]

                var = tk.IntVar(value=1 if completed else 0)

                task_check = tk.Checkbutton(tasks_frame, text=task, font=BLOG['window_font'],
                                            bg=INTERFACE['bg_color'], anchor="w",
                                            variable=var, command=lambda i=i: update_task_state(i, var))
                task_check.grid(row=i + 2, column=0, sticky="w", padx=10, pady=5, columnspan=2)

                task_check.bind("<Button-3>", lambda event, index=i: delete_task(index))
                task_check.config(cursor="hand2")

                ToolTip(task_check, "Right click to delete")

        def update_task_state(index, var):
            """
            Updates the completion state of a task.

            :param index: The index of the task to update
            :param var: The variable holding the state of the checkbox (completed or not)
            :return: None
            """
            completed = bool(var.get())

            to_do_items[index]["completed"] = completed

            self.blog_data["to_do"] = to_do_items
            self.save_blog_data()

        new_task_entry = tk.Entry(tasks_frame, textvariable=new_task_var, font=BLOG['entry_font'],
                                  bg=BLOG['entry_color'], width=20)
        new_task_entry.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        new_task_entry.bind("<Return>", add_task)

        add_task_button = tk.Button(tasks_frame, text="Add Task", command=add_task,
                                    bg=BLOG['add_button_color'], font=BLOG['buttons_font'])
        add_task_button.grid(row=1, column=0, sticky="w", padx=10, pady=10)
        add_task_button.config(cursor="hand2")

        update_task_list()

    def save_blog_data(self):
        """
        Save data to JSON.

        :return: None
        """
        with open(self.json_file, 'w') as json_file:
            json.dump(self.blog_data, json_file, indent=4)

    def add_icon_and_text(self):
        """
        This method adds a tip section to the blog page. The section includes an icon and two lines of text,
        where each line contains a color-coded word and its description in English and Russian.

        The first line displays "Blue" (for English) and the second line displays "Green" (for Russian).

        :return: None
        """
        self.tip_frame = tk.Frame(self, bg=BLOG['email_label_bg'], padx=10, pady=10)
        self.tip_frame.pack(fill="both", expand=True)

        pin_icon = tk.PhotoImage(file=BLOG['tip_icon']).subsample(2, 2)

        icon_label = tk.Label(self.tip_frame, image=pin_icon, bg=BLOG['links_label_bg'])
        icon_label.image = pin_icon
        icon_label.grid(row=0, column=0, padx=(0, 10))

        first_line = tk.Label(self.tip_frame, bg=BLOG['links_label_bg'], font=BLOG['window_font'])

        blue_text = tk.Label(first_line, text="Blue", fg="blue", bg=BLOG['links_label_bg'], font=BLOG['window_font'])
        blue_text.pack(side="left", padx=(0, 5))
        first_line_text = tk.Label(first_line, text="is for English", bg=BLOG['links_label_bg'],
                                   font=BLOG['window_font'])
        first_line_text.pack(side="left")

        second_line = tk.Label(self.tip_frame, bg=BLOG['links_label_bg'], font=BLOG['window_font'])

        green_text = tk.Label(second_line, text="Green", fg="green", bg=BLOG['links_label_bg'],
                              font=BLOG['window_font'])
        green_text.pack(side="left", padx=(0, 5))
        second_line_text = tk.Label(second_line, text="is for Russian", bg=BLOG['links_label_bg'],
                                    font=BLOG['window_font'])
        second_line_text.pack(side="left")

        first_line.grid(row=0, column=1, sticky="w")
        second_line.grid(row=1, column=1, sticky="w")

    def add_links_list(self):
        """
        This method creates and displays a list of links (from `self.blog_data["links"]`) in the blog interface.
        Each link is displayed with its associated color and contents, and the links are interactive (clickable).

        For each link:
        - The link itself is displayed with the specified color.
        - The contents (such as a description) are displayed beside the link.
        - Clicking the link opens the URL in a web browser.

        :return: None
        """
        links = self.blog_data.get("links", [])
        for link_data in links:
            link = link_data["link"]
            colour = link_data["colour"]
            contents = link_data["contents"]

            link_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
            link_frame.pack(anchor="w", padx=10, pady=5, fill="x")

            link_label = tk.Label(link_frame, text=link, fg=colour, font=BLOG['window_font'], bg=INTERFACE['bg_color'],
                                  anchor="w")
            link_label.pack(side="left", padx=(0, 10))

            contents_label = tk.Label(link_frame, text=contents, fg="black", font=BLOG['window_font'],
                                      bg=INTERFACE['bg_color'],
                                      anchor="e")
            contents_label.pack(side="right", padx=(10, 0))

            link_label.bind("<Button-1>", lambda e, url=link: open_link(url))

            link_label.bind("<Enter>",
                            lambda e, label=link_label: label.config(cursor="hand2"))
            link_label.bind("<Leave>",
                            lambda e, label=link_label: label.config(cursor=""))

    def add_table_frame(self):
        """
        This method creates a table-like structure with multiple columns in the user interface.
        Each column represents a category (e.g., "Prose", "Drawing", "Poems", "Music"),
        and the user can modify the content of each column. The table is created using a Tkinter `Frame`,
        and each cell is a `Text` widget that allows for text input.

        The method does the following:
        - Creates a frame to hold the table.
        - Adds headers for the columns.
        - Fills the table with current project data (such as "prose", "drawing", "poems", "music").
        - Allows users to edit the content of each project in the table.
        - Binds an event to save any changes made by the user.

        :return: None
        """
        self.table_frame = tk.Frame(self, padx=10, pady=10)
        self.table_frame.pack(fill="both", expand=True)

        colors = [BLOG['table_first_column_color'],
                  BLOG['table_second_column_color'],
                  BLOG['table_third_column_color'],
                  BLOG['table_fourth_column_color']]

        headers = [BLOG['table_first_column_header'],
                   BLOG['table_second_column_header'],
                   BLOG['table_third_column_header'],
                   BLOG['table_fourth_column_header']]

        projects = [
            self.blog_data.get("current_projects", {}).get("prose", ""),
            self.blog_data.get("current_projects", {}).get("drawing", ""),
            self.blog_data.get("current_projects", {}).get("poems", ""),
            self.blog_data.get("current_projects", {}).get("music", "")
        ]

        for col in range(len(headers)):
            self.table_frame.grid_columnconfigure(col, weight=1, uniform="equal")

        for col, header in enumerate(headers):
            label = tk.Label(self.table_frame, text=header, bg=colors[col], font=BLOG['table_title_font'], padx=10,
                             pady=5)
            label.grid(row=0, column=col, sticky="nsew")

        for col, project in enumerate(projects):
            text = tk.Text(self.table_frame, bg=colors[col], font=BLOG['window_font'], wrap="word", height=3, width=20)
            text.insert("1.0", project)
            text.grid(row=1, column=col, sticky="nsew")

            text.config(state=tk.NORMAL)

            self.text_widgets.append(text)

            text.bind("<KeyRelease>", lambda event, text=text: self.save_changes(text))

    def add_title_frame(self, text):
        """
        This method creates a header frame for displaying a title with optional icon support.
        The header is used as a visual title or section heading in the user interface.

        :param text: The text to display as the title in the header.
        :return: None
        """
        header_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        header_frame.pack(pady=5)

        self.header_frames.append(header_frame)

        icon_width, icon_height = BLOG['icon_height'], BLOG['icon_width']

        add_header_label(header_frame, row=0, column=0, text=text)

    def add_title_frame_with_icon(self):
        """
        This method creates a header frame that includes both a title and an icon. The header is used as a
        section title, with an optional icon placed next to the title text.

        :return: None
        """
        header_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        header_frame.pack(pady=5)

        self.header_frames.append(header_frame)

        icon_width, icon_height = BLOG['icon_height'], BLOG['icon_width']

        add_header_label(header_frame, row=0, column=0, text="Current projects")
        add_title_icon(header_frame, icon_width, icon_height, row=0, column=1,
                            icon=BLOG['hearts_icon_path'])

    def save_changes(self, text_widget):
        """
        This method saves the updated content from the text widgets into the JSON file.
        It extracts the text from each text widget (for "prose", "drawing", "poems", and "music")
        and updates the corresponding values in the JSON data under the "current_projects" section.

        :param text_widget: The text widget that triggered the save. (Currently not used directly in this method.)
        :return: None
        """
        updated_projects = {
            "prose": self.text_widgets[0].get("1.0", "end-1c").strip(),
            "drawing": self.text_widgets[1].get("1.0", "end-1c").strip(),
            "poems": self.text_widgets[2].get("1.0", "end-1c").strip(),
            "music": self.text_widgets[3].get("1.0", "end-1c").strip(),
        }

        with open(self.json_file, "r", encoding="utf-8") as file:
            blog_data = json.load(file)

        blog_data["current_projects"] = updated_projects

        with open(self.json_file, "w", encoding="utf-8") as file:
            json.dump(blog_data, file, ensure_ascii=False, indent=4)

    def load_blog_data(self):
        """
        Load data from JSON.

        :return: None
        """
        try:
            with open(self.json_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            print("File not found.")
            return {}
        except json.JSONDecodeError:
            print("Error JSON decode.")
            return {}
