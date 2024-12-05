from config.imports import *
from config.settings import MONTHS
from config.utils import add_source_label_third_level as add_source_label_months, load_tasks_from_json
from src.monthly_plans import MonthlyPlans
from config.tooltip import ToolTip


def load_month_states(json_path):
    """
    Load icons from JSON.

    :param json_path: Path to JSON with icons
    :return: JSON data
    """
    with open(json_path, "r") as file:
        return json.load(file)


def save_month_states(json_path, data):
    """
    Saves the given data to the specified JSON file.

    :param json_path: The path to the JSON file where the data will be saved.
    :param data: The data (usually a dictionary) to be saved in the JSON file.
    :return: None
    """
    with open(json_path, "w") as file:
        json.dump(data, file, indent=4)


class Months(tk.Frame):
    """
    The Months class displays a page for a specific year that shows month-related tasks, quotes, and images.
    This page is part of the "Yearly Plans" section of the application.

    This class manages the following:
    - Displays a clickable header that links back to the "Yearly Plans" and the specific year.
    - Adds a banner image with a resizing feature to fit the screen.
    - Displays month-related content (quotes, images) for the given year.
    - Handles interaction with the user to navigate through the year and other pages.

    Attributes:
        parent (tk.Widget): The parent widget (usually the main window).
        main_window (MainWindow): The main window instance for global management (e.g., scrollbars).
        json_file (str): Path to the JSON file that stores tasks and data related to the year.
        year (int): The year associated with the displayed data.
        tasks (dict): A dictionary containing tasks loaded from the JSON file.
    """
    def __init__(self, parent, main_window, json_file, year):
        """
        Initializes the Months page, sets up the GUI elements, and loads data from the JSON file.

        :param parent: The parent widget for this frame.
        :param main_window: The main window instance for global settings and features.
        :param json_file: The path to the JSON file containing tasks for the year.
        :param year: The year to display tasks for.
        """
        super().__init__(parent)
        self.configure(bg=INTERFACE['bg_color'])
        self.main_window = main_window
        self.year = year
        self.parent = parent
        self.json_file = json_file
        self.main_window.check_scrollbar()

        self.tasks = load_tasks_from_json(json_file)

        add_source_label_months(self,
                                icon_path_1=ICONS_PATHS['yearly_plans'],
                                clickable_text="Yearly plans /",
                                click_command_1=self.navigate_to_yearly_plans,
                                icon_path_2=ICONS_PATHS['year'],
                                year_name=f"{self.year} /",
                                icon_path_3=ICONS_PATHS['months'],
                                text=PAGES_NAMES['months'],
                                click_command_2=lambda: self.navigate_to_year(self.year))

        # Banner add
        self.banner_label, self.banner_image_original = add_banner(
            self,
            banner_path=BANNER_PATHS['months'],
            bg_color=INTERFACE['bg_color']
        )

        # resize_banner
        if self.banner_label and self.banner_image_original:
            self.bind("<Configure>", lambda event: resize_banner(
                self,
                self.banner_label,
                self.banner_image_original
            ))

        self.icon_image_original = Image.open(ICONS_PATHS['months'])

        add_icon_and_label(self, text=PAGES_NAMES['months'],
                           icon_path=ICONS_PATHS['months'],
                           bg_color=INTERFACE['bg_color'])
        add_separator(parent=self, color=INTERFACE['separator'])

        self.add_quote_and_image(DATA_PATHS['months'])

    def on_button_click(self, month):
        """
        Handles the click event for a month button. It clears the current canvas, sets the month, and displays
        the monthly plans for the selected month.

        The method performs the following:
        1. Clears the current content from the parent canvas.
        2. Sets the `month` attribute to the selected month.
        3. Loads the `MonthlyPlans` frame, passing the necessary parameters like the year and month.
        4. Refreshes the view to show the content for the selected month.

        :param month: The month corresponding to the button that was clicked.
        :return: None
        """
        clear_canvas(self.parent)
        self.month = month

        calendar_frame = MonthlyPlans(self.parent, json_file=f"./data/years/{self.year}.json",
                                      main_window=self.main_window, year=self.year, month=self.month)
        calendar_frame.pack(fill=tk.BOTH, expand=True)

        if hasattr(self.main_window, 'canvas') and self.main_window.canvas:
            self.main_window.canvas.yview_moveto(0)
        else:
            print("Canvas not found in main_window.")

    def add_quote_and_image(self, json_path):
        """
        This method adds month buttons with status icons and displays a quote with an image.

        The method loads month states from the given JSON file, creates buttons for each month with a status icon,
        and updates the icons when right-clicked. It also displays a quote and an image on the right side.

        :param json_path: Path to the JSON file containing the month states.
        :return: None
        """
        month_states = load_month_states(json_path)

        main_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        main_frame.pack(pady=5, padx=2)

        # Buttons frame
        left_frame = tk.Frame(main_frame, bg=INTERFACE['bg_color'])
        left_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nw")

        icon_paths = [
            MONTHS['not_started_icon_path'],
            MONTHS['in_progress_icon'],
            MONTHS['done_icon']
        ]

        next_icon = {
            icon_paths[i]: icon_paths[(i + 1) % len(icon_paths)]
            for i in range(len(icon_paths))
        }

        def change_icon(event, button, month):
            """
            Changes the icon of a month button when it is right-clicked.
            Cycles through the three icons: "Not started", "In progress", and "Done".

            :param event: The event generated by the right-click.
            :param button: The button corresponding to the month.
            :param month: The month being edited.
            :return: None
            """
            current_icon = button.icon_path
            next_icon_path = next_icon[current_icon]
            button.config(image=icons[next_icon_path])
            button.icon_path = next_icon_path
            month_states["months"][month]["icon_path"] = next_icon_path
            save_month_states(json_path, month_states)

        icons = {path: PhotoImage(file=path).subsample(2, 2) for path in icon_paths}

        for month, data in month_states["months"].items():
            icon_path = data["icon_path"]
            button = tk.Button(left_frame,
                               text=month,
                               image=icons[icon_path],
                               compound="left",
                               bg=INTERFACE['bg_color'],
                               anchor="w",
                               font=MONTHS['buttons_font'],
                               padx=2,
                               command=lambda month=month: self.on_button_click(month))
            button.icon_path = icon_path
            button.bind("<Button-3>", lambda event, b=button, m=month: change_icon(event, b, m))
            button.config(cursor="hand2")
            button.pack(fill="x", side="top", pady=5, padx=10)
            ToolTip(button, "Right click to edit status")

        # Quote and image frame
        right_frame = tk.Frame(main_frame, bg=INTERFACE['bg_color'])
        right_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ne")
        add_image_to_grid(right_frame, MONTHS['image_link'], row=0, column=0, height=500,
                               width=350,
                               rowspan=1, columnspan=1)

        quote_frame = tk.Frame(right_frame, bg=INTERFACE['bg_color'])
        quote_frame.grid(row=1, column=0, pady=10, sticky="n")

        line = tk.Canvas(quote_frame, width=2, bg=INTERFACE['separator'], height=100)
        line.grid(row=0, column=0, padx=(0, 10), sticky="n")

        quote_text = MONTHS['quote_text']
        label_quote = tk.Label(quote_frame, text=quote_text, font=MONTHS['quote_font'],
                               bg=INTERFACE['bg_color'], wraplength=MONTHS['quote_wraplength'])
        label_quote.grid(row=0, column=1, sticky="w")

    def navigate_to_yearly_plans(self):
        """
        Return to Yearly plans.

        :return: None
        """
        self.main_window.bind_events()
        self.main_window.show_tab_content("yearly_plans")

    def navigate_to_year(self, year):
        """
        Navigates to the year page and updates the view with the selected year's details.

        :param year: The year to which we are navigating.
        :return: None
        """
        self.main_window.bind_events()
        clear_canvas(self.parent)

        from src.year import Year
        year_frame = Year(self.parent, json_file=f"./data/years/{year}.json", main_window=self.main_window, year=year)
        year_frame.pack(fill=tk.BOTH, expand=True)

        reset_canvas_view(self.main_window)


