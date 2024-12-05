from config.imports import *
from config.settings import LISTS_FOR_LIFE


def add_image_to_button(button, image_path, width, height):
    """
    Loads an image from the specified path, resizes it, and sets it on the button.

    :param button: The button object to which the image will be added.
    :param image_path: The path to the image file.
    :param width: The width of the image in pixels.
    :param height: The height of the image in pixels.
    :return: None
    """
    try:
        image = Image.open(image_path)
        image = image.resize((width, height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)

        button.config(image=photo)
        button.image = photo
    except Exception as e:
        print(f"Ошибка загрузки изображения {image_path}: {e}")


class ListsForLife(tk.Frame):
    """
    The ListsForLife class is responsible for creating the interface for the '#Lists_for_life' tab.
    It includes four buttons: 'Reading', 'Wishlist', 'Courses', 'Goals'.
    """
    def __init__(self, parent, json_file, main_window):
        """
        Constructor for initializing the "Lists for Life" page.

        :param parent: The parent frame in which the page will be placed.
        :param json_file: The path to the JSON file containing data for loading.
        :param main_window: The main window of the application (Tkinter main window) that is passed for interaction.

        The constructor performs the following actions:
        1. Initializes the frame with the specified parent and sets the background color.
        2. Adds the source label using the `add_source_label` function, specifying the icon, title, and style.
        3. Adds a banner to the page:
           - Loads the banner from the specified path.
           - Binds the window resize event to the `resize_banner` function, so the banner resizes when the window size changes.
        4. Adds an icon with the page title.
        5. Adds a horizontal divider between sections.
        6. Loads data from the specified JSON file into the `self.data` attribute.
        7. Retrieves the data from the "items" key of the JSON file using the `get_data_from_json` method.
        8. Calls the `add_buttons` method to create buttons based on the loaded data.
        """
        super().__init__(parent)
        self.configure(bg=INTERFACE['bg_color'])
        self.parent = parent
        self.main_window = main_window

        add_source_label(self, ICONS_PATHS['lists_for_life'], PAGES_NAMES['lists_for_life'],
                         bg_color=INTERFACE['bg_color'], font=INTERFACE['source_label_font'])

        # Banner add
        self.banner_label, self.banner_image_original = add_banner(
            self,
            banner_path=BANNER_PATHS['lists_for_life'],
            bg_color=INTERFACE['bg_color']
        )

        # resize_banner
        if self.banner_label and self.banner_image_original:
            self.bind("<Configure>", lambda event: resize_banner(
                self,
                self.banner_label,
                self.banner_image_original
            ))

        add_icon_and_label(self, text=PAGES_NAMES['lists_for_life'], icon_path=ICONS_PATHS['lists_for_life'],
                           bg_color=INTERFACE['bg_color'])
        add_separator(parent=self, color=INTERFACE['separator'])

        # JSON
        with open(json_file, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        # Load data
        self.lists_data = self.get_data_from_json("items")

        self.add_buttons(self.lists_data)  # Buttons

    def add_buttons(self, items):
        """
        Creates and places buttons with images and descriptions for the first 4 items from the given list.

        :param items: A list of items, where each item is a dictionary with the following fields:
                      - "title": The title of the button.
                      - "image": The path to the image for the button.
        :return: None
        """
        # Frame to hold buttons
        image_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        image_frame.pack(pady=5)

        for index, item in enumerate(items[:4]):  # Only use the first 4 items
            # Determine the row and column based on index
            row = index // 2  # Each row contains 2 blocks
            column = index % 2  # Alternate between column 0 and column 1

            # Create a button with title, image, and description
            button = tk.Button(
                image_frame,
                text=item["title"],  # Title of the button
                command=lambda i=item.copy(): self.on_button_click(i),  # Pass the current item to the click handler
                bg=INTERFACE['bg_color'],
                bd=1,
                relief="solid",
                padx=10,
                pady=10,
                compound='bottom',  # Image above the text
                font=LISTS_FOR_LIFE['button_font']
            )

            # Load the image and set it to the button
            add_image_to_button(button, item["image"], width=250, height=175)

            # Place the button in the grid
            button.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")  # Added sticky option
            button.config(cursor="hand2")

        # Configure grid weights to ensure buttons resize uniformly and occupy more space
        for i in range(2):  # Assuming you have 2 columns
            image_frame.grid_columnconfigure(i, weight=2)  # Increase weight to make columns larger
        for i in range((len(items[:4]) + 1) // 2):  # Rows based on number of items
            image_frame.grid_rowconfigure(i, weight=2)  # Increase weight for more height

    def on_button_click(self, item):
        """
        Click handler for the button.

        :param item: A dictionary containing information about the button, including keys:
                     - "title": The title of the button.
                     - Additional data specific to each button.
        :return: None
        """
        # Different actions based on item type or identifier
        clear_canvas(self.parent)
        if item["title"] == "Reading":
            from src.reading import Reading
            goals_frame = Reading(self.parent, json_file=DATA_PATHS['reading'], main_window=self.main_window)
            goals_frame.pack(fill=tk.BOTH, expand=True)
        elif item["title"] == "Wishlist":
            from src.wishlist import Wishlist
            goals_frame = Wishlist(self.parent, json_file=DATA_PATHS['wishlist'], main_window=self.main_window)
            goals_frame.pack(fill=tk.BOTH, expand=True)
        elif item["title"] == "Goals":
            from src.goals import Goals
            goals_frame = Goals(self.parent, json_file=DATA_PATHS['goals'], main_window=self.main_window)
            goals_frame.pack(fill=tk.BOTH, expand=True)
        elif item["title"] == "Courses":
            from src.courses import Courses
            goals_frame = Courses(self.parent, json_file=DATA_PATHS['courses'], main_window=self.main_window)
            goals_frame.pack(fill=tk.BOTH, expand=True)

        reset_canvas_view(self.main_window)

    def get_data_from_json(self, key):
        """
        Extracts data from the loaded JSON by the specified key.

        :param key: A string representing the key to extract data for.
        :return: The value for the specified key, or an empty list if the key is not found.
        """
        return self.data.get(key, [])  # Returns the value for the key or an empty list if the key doesn't exist

