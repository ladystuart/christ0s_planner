from config.imports import *
from config.settings import REVIEW
from config.utils import add_source_label_third_level as add_source_label_review, add_icon_image


async def get_review_from_server(year):
    """
    Fetches review data from the server for a specific year.

    Args:
        year: The year for which the review data is requested.

    Returns:
        List of dictionaries containing review questions and answers.
    """
    params = {"year": int(year)}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{SERVER_URL}/get_review",
                                   params=params, ssl=SSL_ENABLED) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Error: {response.status}")
                    return []
        except Exception as e:
            print(f"Error fetching data: {e}")
            return []


class Review(tk.Frame):
    """
    This class represents the 'Review' page where users can view or interact with
    the review-related tasks or notes for a given year. The page fetches tasks from
    server, displays them, and allows navigation to other pages (e.g., yearly plans).

    Attributes:
        main_window (tk.Tk): The main window of the application.
        year (int): The current year being reviewed.
        parent (tk.Widget): The parent widget to which this frame belongs.
        tasks (dict): Loaded tasks from server.
    """
    def __init__(self, parent, main_window, year):
        """
        Initializes the 'Review' page with the given parent widget, main window, and year.
        Sets up the layout and UI components.

        :param parent: The parent widget for this frame.
        :param main_window: The main application window.
        :param year: The year for which the review is being displayed.
        """
        super().__init__(parent)
        self.original_answers = []
        self.text_fields = []
        self.configure(bg=INTERFACE['bg_color'])
        self.main_window = main_window
        self.year = year
        self.parent = parent
        self.main_window.disable_buttons()
        self.main_window.check_scrollbar()

        self.tasks = asyncio.run(get_review_from_server(self.year))

        self.first_clickable_label, self.second_clickable_label = (add_source_label_review
                                                                   (self,
                                                                    icon_path_1=ICONS_PATHS['yearly_plans'],
                                                                    clickable_text="Yearly plans /",
                                                                    click_command_1=self.navigate_to_yearly_plans,
                                                                    icon_path_2=ICONS_PATHS['year'],
                                                                    year_name=f"{self.year} /",
                                                                    icon_path_3=ICONS_PATHS['review'],
                                                                    text=PAGES_NAMES['review'],
                                                                    click_command_2=lambda:
                                                                    self.navigate_to_year(self.year)))

        self.first_clickable_label["state"] = "disabled"
        self.second_clickable_label["state"] = "disabled"

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

        self.icon_image_original = asyncio.run(add_icon_image(ICONS_PATHS['review']))

        add_icon_and_label(self, text=PAGES_NAMES['review'],
                           icon_path=ICONS_PATHS['review'],
                           bg_color=INTERFACE['bg_color'])

        add_separator(parent=self, color=INTERFACE['separator'])

        self.add_questions(self.tasks)

        self.main_window.enable_buttons()
        self.first_clickable_label["state"] = "normal"
        self.second_clickable_label["state"] = "normal"

    async def save_data_to_server(self, year, review_data):
        """
        Sends review data to the server for a specified year.

        Args:
            year (int): The year for which the review data is being updated.
            review_data (list of dict): A list of dictionaries, each containing a question and its corresponding answer.

        Returns:
            None

        Raises:
            Displays a message box if the data is successfully updated.
            Logs an error message if the request fails.
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                        f"{SERVER_URL}/update_review",
                        json={"year": int(year), "reviews": review_data}, ssl=SSL_ENABLED
                ) as response:
                    if response.status == 200:
                        messagebox.showinfo("Success", "Data successfully updated!")
                        self.save_button.config(state="disabled")
                        self.original_answers = [
                            text_field.get("1.0", "end-1c").strip()
                            for text_field in self.text_fields
                        ]
                    else:
                        print(f"Data update error: {await response.text()}")
            except Exception as e:
                print(f"Error: {e}")

    def add_questions(self, review_data):
        """
        Adds review questions and their respective answers to the UI.
        Each question is displayed with its associated answer,
        and a text entry field is provided for potential modification of the answer.

        The method applies alternating colors to each question's background to enhance readability and organization.
        It adds a button to save user changes.

        :param review_data: A list of dictionaries where each dictionary contains a 'question' and an 'answer'.
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

        for idx, data in enumerate(review_data):
            question = data['question']
            answer = data['answer']
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

            text_field.edit_modified(False)
            text_field.bind("<<Modified>>", self.on_text_modified)

            self.text_fields.append(text_field)
            self.original_answers.append(answer.strip())

        self.save_button = tk.Button(self, text="Save", font=REVIEW['button_text_font'],
                                command=lambda: self.save_review_data(self.year),
                                     bg=REVIEW['button_color'], state="disabled")
        self.save_button.pack(pady=20)
        self.save_button.config(cursor="hand2")

    def on_text_modified(self, event):
        """
        Event handler for detecting changes in any of the text fields.

        Compares the current text content of each field with the original answers.
        If any of them has been changed, the Save button is enabled.
        If all fields are unchanged (i.e., reverted to original), the Save button is disabled again.

        Args:
            event: The <<Modified>> event triggered by a change in a Text widget.

        Returns:
            None
        """
        any_changed = False
        for idx, text_field in enumerate(self.text_fields):
            current_text = text_field.get("1.0", "end-1c").strip()
            if current_text != self.original_answers[idx]:
                any_changed = True
                break

        if any_changed:
            self.save_button.config(state="normal")
        else:
            self.save_button.config(state="disabled")

        event.widget.edit_modified(False)

    def save_review_data(self, year):
        """
        Collects review questions and answers from the UI and sends them to the server.

        Args:
            year (int): The year for which the review data is being saved.

        Returns:
            None
        """
        review_data = []

        for widget in self.winfo_children():
            if isinstance(widget, tk.Label):
                question = widget.cget("text")
            elif isinstance(widget, tk.Text):
                answer = widget.get("1.0", "end").strip()
                review_data.append({"question": question, "answer": answer})

        asyncio.run(self.save_data_to_server(int(year), review_data))

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
        year_frame = Year(self.parent, main_window=self.main_window, year=year)
        year_frame.pack(fill=tk.BOTH, expand=True)

        reset_canvas_view(self.main_window)
