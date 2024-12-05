from config.imports import *
from config.settings import IDEAS_AND_PLANS
from config.utils import add_header_label
from config.utils import add_source_label_second_level as add_source_label_ideas_and_plans


def load_json(file_path):
    """
    Loads and parses a JSON file from the given file path.

    This method opens the specified JSON file, reads its contents, and parses it into a Python dictionary.
    If the file is not found or there is an error in parsing, an exception will be raised.

    :param file_path: The path to the JSON file to be loaded.
                      It should be a valid file path to a JSON file.
    :return: A Python dictionary containing the parsed JSON data.
    :raises json.JSONDecodeError: If the JSON content is invalid or malformed.
    :raises FileNotFoundError: If the specified file does not exist.
    :raises IOError: If there is an issue with reading the file (e.g., permission errors).
    """
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


class IdeasAndPlans(tk.Frame):
    """
    This class represents the Ideas and Plans section of the application.
    It extends from the tk.Frame and is used to display various content related to ideas and plans
    along with interactivity such as navigation, text display, and dynamic resizing of banners.
    """
    def __init__(self, parent, json_file, main_window):
        """
        Initialize the Ideas and Plans frame with all necessary components and interactions.

        :param parent: The parent widget where this frame will be placed.
        :param json_file: The path to a JSON file containing the content data.
        :param main_window: The main window of the application, which can be used for global actions.
        """
        super().__init__(parent)
        self.parent = parent
        self.main_window = main_window
        self.configure(bg=INTERFACE['bg_color'])
        self.json_file = json_file  # Store the json_file path

        self.icon_image_original = Image.open(ICONS_PATHS['ideas_and_plans'])

        add_source_label_ideas_and_plans(
            self,  # Parent element
            icon_path_1=ICONS_PATHS['blog'],
            clickable_text="Blog /",
            click_command=self.navigate_to_blog,
            icon_path_2=ICONS_PATHS['ideas_and_plans'],
            text=PAGES_NAMES['ideas_and_plans']
        )

        # Banner add
        self.banner_label, self.banner_image_original = add_banner(
            self,
            banner_path=BANNER_PATHS['ideas_and_plans'],
            bg_color=INTERFACE['bg_color']
        )

        # resize_banner
        if self.banner_label and self.banner_image_original:
            self.bind("<Configure>", lambda event: resize_banner(
                self,
                self.banner_label,
                self.banner_image_original
            ))

        add_icon_and_label(self, text=PAGES_NAMES['ideas_and_plans'], icon_path=ICONS_PATHS['ideas_and_plans'],
                           bg_color=INTERFACE['bg_color'])
        add_separator(parent=self, color=INTERFACE['separator'])

        self.add_image()

        add_separator(parent=self, color=INTERFACE['separator'])
        self.add_title_frame(text="Ideas")

        self.data = load_json(self.json_file)

        self.text_field = tk.Text(self, wrap="word", font=IDEAS_AND_PLANS['text_font'])
        self.text_field.pack(fill=tk.BOTH, expand=True)

        self.load_text_content()

        self.adjust_height()

        self.text_field.bind("<KeyRelease>", self.on_text_change)

    def adjust_height(self):
        """
        Adjusts the height of the text field based on the number of lines in the content.

        The method calculates the number of lines in the content stored in the 'text' key of the JSON data,
        and adjusts the height of the text field widget to accommodate this content.
        A small buffer of 2 extra lines is added to ensure the content is fully visible.

        :return: None
        """
        text_content = self.data.get("text", "")
        line_count = text_content.count("\n") + 2

        self.text_field.config(height=line_count)

    def save_text_content(self):
        """
        Save content to JSON.

        :return: None
        """
        self.data["text"] = self.text_field.get("1.0", tk.END).strip()
        with open(self.json_file, "w", encoding="utf-8") as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)

    def on_text_change(self, event):
        """
        Handles changes made to the text in the text field. This method is triggered whenever the user types
        or modifies the content in the text field.

        It calls the `save_text_content` method to persist any changes made by the user.

        :param event: The event object passed by the key release event. It contains details about the key event.
        :return: None
        """
        self.save_text_content()

    def load_text_content(self):
        """
        Get text content from JSON.

        :return: None
        """
        text_content = self.data.get("text", "")
        self.text_field.insert("1.0", text_content)

    def add_title_frame(self, text):
        """
        Creates and adds a title frame to the current frame, displaying a header label with the given text.

        This method creates a new frame (styled according to the interface configuration) and places it
        at the top of the current widget. It also adds a header label with the provided text.

        :param text: The text to be displayed in the header label. It will be placed inside the new frame.
        :return: None
        """
        header_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        header_frame.pack(pady=5)

        add_header_label(header_frame, row=0, column=0, text=text)

    def add_image(self):
        """
        Loads an image from a predefined path, resizes it according to the specified dimensions,
        and displays it as a label in the current frame.

        This method reads the image from the path specified in `IDEAS_AND_PLANS['image_path']`, resizes it
        to the dimensions defined in `IDEAS_AND_PLANS['image_width']` and `IDEAS_AND_PLANS['image_height']`,
        and then creates a label containing the resized image. The label is packed into the current frame.

        :return: None
        """
        self.image_path = IDEAS_AND_PLANS['image_path']
        image = Image.open(self.image_path)
        resized_image = image.resize((IDEAS_AND_PLANS['image_width'], IDEAS_AND_PLANS['image_height']),
                                     Image.Resampling.LANCZOS)
        self.image = ImageTk.PhotoImage(resized_image)

        image_label = tk.Label(self, image=self.image)
        image_label.pack()

    def navigate_to_blog(self):
        """
        Return to blog page.

        :return: None
        """
        self.main_window.show_tab_content("blog")
