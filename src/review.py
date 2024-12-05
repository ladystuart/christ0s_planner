from config.imports import *
from config.settings import REVIEW
from config.utils import add_source_label_third_level as add_source_label_review, load_tasks_from_json


class Review(tk.Frame):
    """
    This class represents the 'Review' page where users can view or interact with
    the review-related tasks or notes for a given year. The page fetches tasks from
    a JSON file, displays them, and allows navigation to other pages (e.g., yearly plans).

    Attributes:
        main_window (tk.Tk): The main window of the application.
        year (int): The current year being reviewed.
        parent (tk.Widget): The parent widget to which this frame belongs.
        json_file (str): Path to the JSON file containing the tasks data.
        tasks (dict): Loaded tasks from the JSON file.
    """
    def __init__(self, parent, main_window, json_file, year):
        """
        Initializes the 'Review' page with the given parent widget, main window,
        JSON file, and year. Sets up the layout and UI components.

        :param parent: The parent widget for this frame.
        :param main_window: The main application window.
        :param json_file: Path to the JSON file containing review tasks.
        :param year: The year for which the review is being displayed.
        """
        super().__init__(parent)
        self.configure(bg=INTERFACE['bg_color'])
        self.main_window = main_window
        self.year = year
        self.parent = parent
        self.json_file = json_file
        self.main_window.check_scrollbar()

        self.tasks = load_tasks_from_json(json_file)

        add_source_label_review(self,
                                icon_path_1=ICONS_PATHS['yearly_plans'],
                                clickable_text="Yearly plans /",
                                click_command_1=self.navigate_to_yearly_plans,
                                icon_path_2=ICONS_PATHS['year'],
                                year_name=f"{self.year} /",
                                icon_path_3=ICONS_PATHS['review'],
                                text=PAGES_NAMES['review'],
                                click_command_2=lambda: self.navigate_to_year(self.year))

        # Banner add
        self.banner_label, self.banner_image_original = add_banner(
            self,
            banner_path=BANNER_PATHS['review'],
            bg_color=INTERFACE['bg_color']
        )

        # resize_banner
        if self.banner_label and self.banner_image_original:
            self.bind("<Configure>", lambda event: resize_banner(
                self,
                self.banner_label,
                self.banner_image_original
            ))

        self.icon_image_original = Image.open(ICONS_PATHS['review'])

        add_icon_and_label(self, text=PAGES_NAMES['review'],
                           icon_path=ICONS_PATHS['review'],
                           bg_color=INTERFACE['bg_color'])

        add_separator(parent=self, color=INTERFACE['separator'])

        self.add_questions(self.tasks.get("review", {}))

    def add_questions(self, review_data):
        """
        Adds review questions and their respective answers to the UI. Each question is displayed with its associated answer,
        and a text entry field is provided for potential modification of the answer.

        The method applies alternating colors to each question's background to enhance readability and organization.
        It binds an event listener to track any changes in the answer fields.

        :param review_data: A dictionary where the keys are review questions and the values are the corresponding answers.
        :return: None
        """
        colors = [
            REVIEW['1. How would you describe this year with a single word?'],
            REVIEW['2. What is your biggest challenge this year?'],
            REVIEW['3. One thing you are most proud of this year:'],
            REVIEW['4. How did you take care of yourself this year?'],
            REVIEW['5. How have you changed over the year'],
            REVIEW['6. New things you learned:'],
            REVIEW['7. What made this year special?'],
            REVIEW['8. What are you most grateful for?'],
            REVIEW['9. Top 3 priorities for the next year:'],
            REVIEW['10. Did you do your best?']
        ]  # Colors
        for idx, (question, answer) in enumerate(review_data.items()):
            color = colors[idx % len(colors)]

            # Question label
            question_label = tk.Label(self, text=question, bg=color, fg=REVIEW['question_label_text_color'],
                                      font=REVIEW['question_label_text_font'],
                                      wraplength=600, justify="left")
            question_label.pack(fill="x", padx=10, pady=(10, 5))

            # Text entry
            text_field = tk.Text(self, height=3, wrap="word", font=REVIEW['entry_text_font'])
            text_field.pack(fill="x", padx=10, pady=(0, 10))

            text_field.insert("1.0", answer)

            text_field.bind("<<Modified>>",
                            lambda event, key=question, widget=text_field: self.on_text_change(key, widget))

    def on_text_change(self, question, widget):
        """
        This method is triggered when the text in the answer field is modified. It updates the review answer in the tasks
        dictionary and saves the changes to the JSON file.

        It checks if the text has been modified, updates the corresponding answer in the `tasks["review"]` dictionary,
        and saves the updated data to the JSON file. After saving, it resets the modified flag on the widget to prevent
        unnecessary saving if the text hasn't changed further.

        :param question: The question, whose answer has been modified.
        :param widget: The Text widget where the answer is being edited.
        :return: None
        """
        if widget.edit_modified():  # If text modified
            self.tasks["review"][question] = widget.get("1.0", "end").strip()
            self.save_tasks_to_json()
            widget.edit_modified(False)

    def save_tasks_to_json(self):
        """
        Saving to JSON.

        :return: None
        """
        with open(self.json_file, 'w') as file:
            json.dump(self.tasks, file, indent=4)

    def navigate_to_yearly_plans(self):
        """
        Return to Yearly plans.

        :return: None
        """
        self.main_window.bind_events()
        self.main_window.show_tab_content("yearly_plans")

    def navigate_to_year(self, year):
        """
        Navigates to the specified year's page by loading the corresponding `Year` frame, clearing the current content,
        and displaying the year-specific data. This function is typically used to switch between different year views.

        The method performs the following steps:
        1. Binds events for the main window to enable interactivity.
        2. Clears the current canvas or frame to prepare for the new content.
        3. Loads the `Year` frame corresponding to the selected year.
        4. Ensures the scroll position is reset to the top of the canvas (if applicable).

        :param year: The year to navigate to, specified as an integer or string.
        :return: None
        """
        self.main_window.bind_events()
        clear_canvas(self.parent)

        from src.year import Year
        year_frame = Year(self.parent, json_file=f"./data/years/{year}.json", main_window=self.main_window, year=year)
        year_frame.pack(fill=tk.BOTH, expand=True)

        reset_canvas_view(self.main_window)
