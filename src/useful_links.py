from config.imports import *
from config.utils import (add_description_label_bold, add_description_label, add_link_button,
                          add_title_description_label)
from config.settings import USEFUL_LINKS


class UsefulLinks(tk.Frame):
    """
    The UsefulLinks class is responsible for creating the interface for the 'Useful Links' tab.
    It includes a header with an icon and banner, as well as a scrollable area with content.
    """
    def __init__(self, parent, json_file, main_window):
        """
        Constructor for initializing the "Useful Links" page.

        :param parent: The parent frame where the page will be placed.
        :param json_file: Path to the JSON file containing the data to load.
        :param main_window: The main window of the application (Tkinter main window) passed for interaction.

        The constructor performs the following actions:
        1. Initializes the frame with the specified parent and sets the background color.
        2. Creates a list `header_frames` to store headers.
        3. Adds a source label using the `add_source_label` function, specifying the icon, title, and style.
        4. Adds a banner to the page:
           - Loads the banner from the specified path.
           - Binds the window resize event to the `resize_banner` function to scale the banner when the window size changes.
        5. Adds an icon with the page title.
        6. Loads data from the specified JSON file into the `self.data` attribute.
        7. Enumerates and loads data from the JSON file's keys, creating attributes for each section: "search", "books", "courses", "forums", "chatgpt", "additional", "link".
        8. Creates sections with headers, descriptions, and content for each section:
           - `search`: Adds a header, description, and items using `self.search_label_constructor`.
           - `books`: Adds a header, description, and items using `self.books_label_constructor`.
           - `courses`: Adds a header, description, items, and additional information (`ps`) using `self.courses_label_constructor` and `self.ps_courses_label_constructor`.
           - `forums`: Adds a header, description, and table with items using `self.add_forums_table`.
           - `chatgpt`: Adds a header, description, and items using `self.chatgpt_label_constructor`.
           - `additional`: Adds a header and items using `self.additional_data_label_constructor`.
        9. Adds a link button for the `link` key in a separate frame using `add_link_button`.
        10. Adds horizontal separators between sections using `add_separator`.
        """
        super().__init__(parent)

        self.parent = parent
        self.main_window = main_window
        self.main_window.disable_buttons()

        self.header_frames = []  # List for headers

        self.configure(bg=INTERFACE['bg_color'])

        add_source_label(self, ICONS_PATHS['useful_links'], PAGES_NAMES['useful_links'],
                         bg_color=INTERFACE['bg_color'], font=INTERFACE['source_label_font'])

        # Banner add
        self.banner_label, self.banner_image_original = add_banner(
            self,
            banner_path=BANNER_PATHS['useful_links'],
            bg_color=INTERFACE['bg_color']
        )

        if self.banner_label and self.banner_image_original:
            self.bind("<Configure>", lambda event: resize_banner(
                self,
                self.banner_label,
                self.banner_image_original
            ))

        # Icon and label
        add_icon_and_label(self, text=PAGES_NAMES['useful_links'], icon_path=ICONS_PATHS['useful_links'],
                           bg_color=INTERFACE['bg_color'])

        # JSON
        with open(json_file, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        # Files list
        data_files = ["search", "books", "courses", "forums", "chatgpt", "additional", "link"]

        for data_file in data_files:
            setattr(self, f"{data_file}_data", self.get_data_from_json(data_file))

        # Useful Links
        add_separator(self, INTERFACE['separator'])
        title_label(self, self.search_data["title"], self.search_data["icon"],
                    USEFUL_LINKS['title_icon_dimensions'], USEFUL_LINKS['title_icon_dimensions'])
        add_title_description_label(self, self.search_data["description"])
        self.search_label_constructor(self.search_data["items"])

        # Books
        add_separator(self, INTERFACE['separator'])
        title_label(self, self.books_data["title"], self.books_data["icon"],
                    USEFUL_LINKS['title_icon_dimensions'], USEFUL_LINKS['title_icon_dimensions'])
        add_title_description_label(self, self.books_data["description"])
        self.books_label_constructor(self.books_data["items"])

        # Courses
        add_separator(self, INTERFACE['separator'])
        title_label(self, self.courses_data["title"], self.courses_data["icon"],
                    USEFUL_LINKS['title_icon_dimensions'], USEFUL_LINKS['title_icon_dimensions'])
        add_title_description_label(self, self.courses_data["description"])
        self.courses_label_constructor(self.courses_data["items"])
        add_title_description_label(self, self.courses_data["ps"])
        self.ps_courses_label_constructor(self.courses_data["items"])

        # Forums
        add_separator(self, INTERFACE['separator'])
        title_label(self, self.forums_data["title"], self.forums_data["icon"],
                    USEFUL_LINKS['title_icon_dimensions'], USEFUL_LINKS['title_icon_dimensions'])
        add_title_description_label(self, self.forums_data["description"])
        self.add_forums_table(self.forums_data["items"])

        # ChatGPT
        add_separator(self, INTERFACE['separator'])
        title_label(self, self.chatgpt_data["title"], self.chatgpt_data["icon"],
                    USEFUL_LINKS['title_icon_dimensions'], USEFUL_LINKS['title_icon_dimensions'])
        add_title_description_label(self, self.chatgpt_data["description"])
        self.chatgpt_label_constructor(self.chatgpt_data)

        # Additional
        add_separator(self, INTERFACE['separator'])
        title_label(self, self.additional_data["title"], self.additional_data["icon"],
                    USEFUL_LINKS['title_icon_dimensions'], USEFUL_LINKS['title_icon_dimensions'])
        self.additional_data_label_constructor(self.additional_data["items"])

        # Link
        add_separator(self, INTERFACE['separator'])

        def add_link_section():
            """
            Add link to the window.

            Returns: None
            """
            link_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
            link_frame.pack(pady=5)
            add_link_button(link_frame, self.link_data["link_text"], self.link_data["link"], row=0, column=0)

        add_link_section()

        # Enable buttons after all elements are added
        self.main_window.enable_buttons()

    def add_forums_table(self, items):
        """
        Creates a table to display forums with the name, description, and link.

        :param items: A list of data for the table. Each item should be a dictionary with the keys "name", "text", and "link".
        :return: None
        """
        # Table frame
        table_frame = tk.Frame(self, bg=INTERFACE['bg_color'], borderwidth=2, relief="solid")
        table_frame.pack(pady=5)

        # Add headers
        header = ["Title", "Description", "Link"]
        for i, text in enumerate(header):
            label = tk.Label(table_frame, text=text, bg=USEFUL_LINKS['table_head_bg_color'],
                             font=USEFUL_LINKS['table_font_bold'], padx=10)
            label.grid(row=0, column=i, sticky="ew")

        # Add data to the table
        for row_index, item in enumerate(items, start=1):
            row_color = USEFUL_LINKS['table_bg_first'] if row_index % 2 == 1 else USEFUL_LINKS[
                'table_bg_second']

            name_label = tk.Label(table_frame, text=item["name"], bg=row_color, font=USEFUL_LINKS['table_font'])
            name_label.grid(row=row_index, column=0, sticky="nsew", padx=2)

            description_text = tk.Text(table_frame, height=1, width=50, wrap="word", bg=row_color,
                                       font=USEFUL_LINKS['table_font'])
            description_text.insert(tk.END, item["text"])
            description_text.configure(state="disabled")
            description_text.grid(row=row_index, column=1, sticky="nsew", padx=2)

            link_button = tk.Button(table_frame, text="Open", command=lambda link=item["link"]: open_link(link))
            link_button.grid(row=row_index, column=2, sticky="nsew", padx=2)
            link_button.config(cursor="hand2")
            link_button.config(bg=row_color)

    def search_label_constructor(self, items):
        """
        Constructor for displaying data about search engines.

        :param items: A list of elements, where each element is a dictionary with the keys "image", "name", "text", "link_text", and "link".
        :return: None
        """
        image_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        image_frame.pack(pady=5)

        for i in range(0, 2):
            add_image_to_grid(image_frame, items[i]["image"], row=0, column=i, height=100, width=100, rowspan=1)
            add_description_label_bold(image_frame, text=items[i]["name"], row=1, column=i)
            add_description_label(image_frame, text=items[i]["text"], row=2, column=i, rowspan=1)

            add_link_button(image_frame, items[i]["link_text"], items[i]["link"], row=3, column=i)

    def books_label_constructor(self, items):
        """
        Constructor for displaying data about books.

        :param items: A list of elements, where each element is a dictionary with the keys "image", "name", "text", "link_text", "link", "height", "width".
        :return: None
        """
        books_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        books_frame.pack(pady=5)

        k = 0  # Counter

        for i in range(0, 3):
            add_image_to_grid(books_frame, items[i]["image"], row=k + 2, column=0, height=items[i]["height"],
                              width=items[i]["width"], rowspan=1)
            add_description_label_bold(books_frame, text=items[i]["name"], row=k, column=0)
            add_description_label(books_frame, text=items[i]["text"], row=k + 1, column=1, rowspan=2)

            add_link_button(books_frame, items[i]["link_text"], items[i]["link"], row=k + 3, column=1)
            k = k + 4

    def ps_courses_label_constructor(self, items):
        """
        Constructor for displaying course data.

        :param items: A list of elements, where each element is a dictionary with the keys "image", "text", "link_text", "link", "height", "width".
        :return: None
        """
        books_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        books_frame.pack(pady=5)

        k = 0  # Counter

        for i in range(3, 5):
            add_image_to_grid(books_frame, items[i]["image"], row=k + 1, column=0, height=items[i]["height"],
                              width=items[i]["width"], rowspan=2)
            add_description_label(books_frame, text=items[i]["text"], row=k + 1, column=1, rowspan=1)

            add_link_button(books_frame, items[i]["link_text"], items[i]["link"], row=k + 2, column=1)
            k = k + 4

    def additional_data_label_constructor(self, items):
        """
        Constructor for displaying additional information.

        :param items: A list of elements, where each element is a dictionary with the keys "image", "text", "link_text", "link", "height", "width".
        :return: None
        """
        image_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        image_frame.pack(pady=5)

        label_search_text = tk.Label(image_frame, text=items[0]["text"], font=("Arial", 13), bg="#F0F0F0")
        label_search_text.grid(row=0, column=0, columnspan=2, pady=5)

        add_image_to_grid(image_frame, items[0]["image"], row=1, column=0, height=items[0]["height"],
                          width=items[0]["width"], rowspan=1)

        add_link_button(image_frame, items[0]["link_text"], items[0]["link"], row=1, column=1)

        label_search_text = tk.Label(image_frame, text=items[1]["text"], font=("Arial", 13), bg="#F0F0F0")
        label_search_text.grid(row=2, column=0, columnspan=2, pady=5)

        add_image_to_grid(image_frame, items[1]["image"], row=3, column=1, height=items[1]["height"],
                          width=items[1]["width"], rowspan=1)

        add_link_button(image_frame, items[1]["link_text"], items[1]["link"], row=3, column=0)

    def courses_label_constructor(self, items):
        """
        Constructor for displaying course information.

        :param items: A list of elements, where each element is a dictionary with the keys "image", "height", "width", "name", "text", "link_text", "link".
        :return: None
        """
        image_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        image_frame.pack(pady=5)

        for i in range(0, 3):
            add_image_to_grid(image_frame, items[i]["image"], row=0, column=i, height=items[i]["height"],
                              width=items[i]["width"], rowspan=1)
            add_description_label_bold(image_frame, text=items[i]["name"], row=1, column=i)
            add_description_label(image_frame, text=items[i]["text"], row=2, column=i, rowspan=1)

            add_link_button(image_frame, items[i]["link_text"], items[i]["link"], row=3, column=i)

    def chatgpt_label_constructor(self, items):
        """
        Constructor for displaying ChatGPT information.

        :param items: A dictionary with the keys "image", "text", "link_text", "link", "height", "width".
        :return: None
        """
        image_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        image_frame.pack(pady=5)

        add_image_to_grid(image_frame, items["image"], row=0, column=0, height=items["height"], width=items["width"],
                          rowspan=1)
        add_description_label(image_frame, text=items["text"], row=1, column=0, rowspan=1)

        add_link_button(image_frame, items["link_text"], items["link"], row=2, column=0)

    def get_data_from_json(self, key):
        """
        Retrieves data by the specified key from the loaded JSON.

        :param key: The key used to retrieve the data.
        :return: The data associated with the key or raises an error message.
        """
        if key in self.data and len(self.data[key]) > 0:
            return self.data[key][0]  # Return first object
        else:
            messagebox.showerror("Error", f"Wrong JSON format: {key}")
            return None
