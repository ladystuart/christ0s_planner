from config.imports import *
from config.utils import add_source_label_second_level as add_source_label_year
from config.settings import YEAR
from src.habit_tracker import HabitTracker
from src.year_calendar import Calendar
from src.yearly_plans_inner import YearlyPlansInner
from src.gratitude_diary import GratitudeDiary
from src.best_in_months import BestInMonths
from src.review import Review
from src.months import Months


class Year(tk.Frame):
    """
    This class represents a frame for a specific year page. It displays various elements like the
    year, icons, and navigational elements within the main window of the application.
    """
    def __init__(self, parent, main_window, json_file, year):
        """
        Initializes the Year page with the given parameters.

        :param parent: The parent widget to contain this frame.
        :param main_window: The main window of the application.
        :param json_file: The path to the JSON file containing data related to the year.
        :param year: The year for which this page is being created.
        """
        super().__init__(parent)
        self.configure(bg=INTERFACE['bg_color'])
        self.main_window = main_window
        self.parent = parent
        self.year = year

        self.icon_image_original = Image.open(ICONS_PATHS['year'])

        add_source_label_year(
            self,  # Parent element
            icon_path_1=ICONS_PATHS['yearly_plans'],
            clickable_text="Yearly plans /",
            click_command=self.navigate_to_yearly_plans,
            icon_path_2=ICONS_PATHS['year'],
            text=self.year
        )

        self.add_icon_and_label(self, self.year)  # Page title
        self.add_quote_and_image()

    def on_button_click(self, label):
        """
        Handles the button click event, determines which frame to display based on the clicked label,
        and clears the current content before displaying the new frame.

        :param label: The label of the page to navigate to (e.g., calendar, yearly plans, etc.)
        :return: None
        """
        clear_canvas(self.parent)  # Clear canvas
        if label == PAGES_NAMES['calendar']:
            calendar_frame = Calendar(self.parent, json_file=f"./data/years/{self.year}.json",
                                      main_window=self.main_window, year=self.year)
            calendar_frame.pack(fill=tk.BOTH, expand=True)

        elif label == PAGES_NAMES['yearly_plans_inner']:
            yearly_plans_inner_frame = YearlyPlansInner(self.parent, json_file=f"./data/years/{self.year}.json",
                                                        main_window=self.main_window, year=self.year)
            yearly_plans_inner_frame.pack(fill=tk.BOTH, expand=True)

        elif label == PAGES_NAMES['habit_tracker']:
            habit_tracker_frame = HabitTracker(self.parent, json_file=f"./data/years/{self.year}.json",
                                               main_window=self.main_window, year=self.year)
            habit_tracker_frame.pack(fill=tk.BOTH, expand=True)

        elif label == PAGES_NAMES['gratitude_diary']:
            gratitude_diary_frame = GratitudeDiary(self.parent, json_file=f"./data/years/{self.year}.json",
                                                   main_window=self.main_window, year=self.year)
            gratitude_diary_frame.pack(fill=tk.BOTH, expand=True)

        elif label == PAGES_NAMES['best_in_months']:
            best_in_months_frame = BestInMonths(self.parent, json_file=f"./data/years/{self.year}.json",
                                                main_window=self.main_window, year=self.year)
            best_in_months_frame.pack(fill=tk.BOTH, expand=True)

        elif label == PAGES_NAMES['months']:
            months_frame = Months(self.parent, json_file=f"./data/years/{self.year}.json",
                                  main_window=self.main_window, year=self.year)
            months_frame.pack(fill=tk.BOTH, expand=True)

        elif label == PAGES_NAMES['review']:
            review_frame = Review(self.parent, json_file=f"./data/years/{self.year}.json",
                                  main_window=self.main_window, year=self.year)
            review_frame.pack(fill=tk.BOTH, expand=True)

        # Go to the top
        reset_canvas_view(self.main_window)

    def add_quote_and_image(self):
        """
        Add image, quote and buttons.

        :return: None
        """
        main_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        main_frame.pack(pady=5, padx=2)

        # Quote and image
        left_frame = tk.Frame(main_frame, bg="#F0F0F0")
        left_frame.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Image
        add_image_to_grid(left_frame, YEAR['image_link'], row=0, column=0, height=500, width=300,
                          rowspan=1, columnspan=1)

        # Quote with line
        quote_frame = tk.Frame(left_frame, bg=INTERFACE['bg_color'])
        quote_frame.grid(row=1, column=0, pady=10, sticky="n")

        # Vertical line
        line = tk.Canvas(quote_frame, width=2, bg=INTERFACE['separator'], height=100)
        line.grid(row=0, column=0, padx=(0, 10), sticky="n")

        # Quote
        quote_text = YEAR['quote_text']
        label_quote = tk.Label(quote_frame, text=quote_text, font=YEAR['quote_font'],
                               bg=INTERFACE['bg_color'], wraplength=YEAR['quote_wraplength'])
        label_quote.grid(row=0, column=1, sticky="w")

        # Buttons frame
        right_frame = tk.Frame(main_frame, bg=INTERFACE['bg_color'])
        right_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ne")

        # Buttons w icons
        button_data = [
            (PAGES_NAMES['calendar'], ICONS_PATHS['calendar']),
            (PAGES_NAMES['yearly_plans_inner'], ICONS_PATHS['yearly_plans_inner']),
            (PAGES_NAMES['habit_tracker'], ICONS_PATHS['habit_tracker']),
            (PAGES_NAMES['gratitude_diary'], ICONS_PATHS['gratitude_diary']),
            (PAGES_NAMES['best_in_months'], ICONS_PATHS['best_in_months']),
            (PAGES_NAMES['months'], ICONS_PATHS['months']),
            (PAGES_NAMES['review'], ICONS_PATHS['review'])
        ]

        # Add buttons
        for label, icon_path in button_data:
            button_image = PhotoImage(file=icon_path).subsample(2, 2)
            button = tk.Button(right_frame, text=label,
                               image=button_image,
                               compound="left",
                               bg=INTERFACE['bg_color'],
                               anchor="w",
                               font=YEAR['buttons_font'],
                               padx=2,
                               command=lambda label=label: self.on_button_click(label))
            button.image = button_image
            button.pack(fill="x", side="top", pady=5, padx=10)
            button.config(cursor="hand2")

        main_frame.pack(pady=5)

    def add_icon_and_label(self, parent, text):
        """
        Adds an icon and a label with the provided text to the parent frame.
        The icon is loaded, resized, and displayed above the label. The label is placed below the icon.

        :param parent: The parent Tkinter widget where the icon and label will be added.
        :param text: The text to be displayed in the label.
        :return: None
        """
        label_frame = tk.Frame(parent, bg=INTERFACE['bg_color'])
        label_frame.pack(anchor="w", pady=2, padx=10, fill="x")

        icon_and_text_frame = tk.Frame(label_frame, bg=INTERFACE['bg_color'])
        icon_and_text_frame.pack(anchor="w", pady=2, padx=5)

        # Load title icon
        try:
            icon_image = self.icon_image_original.resize((50, 50), Image.Resampling.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_image)
            icon_label = tk.Label(icon_and_text_frame, image=icon_photo, bg=INTERFACE['bg_color'])
            icon_label.image = icon_photo
            icon_label.pack(side="top", pady=40, padx=40)
        except Exception as e:
            print(f"Error icon load: {e}")

        # Add title
        text_label = tk.Label(icon_and_text_frame, text=text, font=YEAR['title_text_font'],
                              bg=INTERFACE['bg_color'], anchor="w")
        text_label.pack(side="top", padx=40)

    def navigate_to_yearly_plans(self):
        """
        Return to Yearly plans window.

        :return: None
        """
        self.main_window.show_tab_content("yearly_plans")
