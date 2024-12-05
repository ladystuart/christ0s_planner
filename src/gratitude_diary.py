from config.imports import *
from config.settings import GRATITUDE_DIARY
from config.utils import add_source_label_third_level as add_source_label_gratitude_diary, load_tasks_from_json
import calendar
from datetime import datetime
from config.tooltip import ToolTip


def on_day_hover(event):
    """
    This method is triggered when the mouse hovers over a day entry label in the gratitude diary.
    It changes the cursor to a "hand" cursor to indicate that the entry is clickable and displays a tooltip
    informing the user that they can right-click to edit the entry.

    :param event: The event object passed when the mouse enters a label, containing details about the event.
    :return: None
    """
    event.widget.config(cursor="hand2")

    tooltip_text = "Click right button to edit"
    ToolTip(event.widget, tooltip_text)


class GratitudeDiary(tk.Frame):
    """
    A class that represents a Gratitude Diary for a specific year.
    It allows the user to save gratitude entries, view saved entries,
    and navigate between different sections of the app.

    Attributes:
        parent (tk.Widget): The parent widget for this frame.
        main_window (MainWindow): The main window instance.
        year (int): The year for which the gratitude diary is created.
        json_file (str): The path to the JSON file where data is stored.
        tasks (dict): A dictionary containing the tasks or gratitude entries.
        entry_text (tk.Text): A Text widget for entering new gratitude entries.
        save_button (tk.Button): A Button widget for saving entries.
    """
    def __init__(self, parent, main_window, json_file, year):
        """
        Initializes the GratitudeDiary class with the provided parameters.

        :param parent: The parent widget for this frame.
        :param main_window: The main window instance which controls the overall app.
        :param json_file: The path to the JSON file that stores gratitude entries.
        :param year: The year for which the gratitude diary is created.
        """
        super().__init__(parent)
        self.configure(bg=INTERFACE['bg_color'])
        self.main_window = main_window
        self.year = year
        self.parent = parent
        self.json_file = json_file
        self.main_window.check_scrollbar()

        self.tasks = load_tasks_from_json(json_file)

        add_source_label_gratitude_diary(self,
                                         icon_path_1=ICONS_PATHS['yearly_plans'],
                                         clickable_text="Yearly plans /",
                                         click_command_1=self.navigate_to_yearly_plans,
                                         icon_path_2=ICONS_PATHS['year'],
                                         year_name=f"{self.year} /",
                                         icon_path_3=ICONS_PATHS['gratitude_diary'],
                                         text=PAGES_NAMES['gratitude_diary'],
                                         click_command_2=lambda: self.navigate_to_year(self.year))

        # Banner add
        self.banner_label, self.banner_image_original = add_banner(
            self,
            banner_path=BANNER_PATHS['gratitude_diary'],
            bg_color=INTERFACE['bg_color']
        )

        # resize_banner
        if self.banner_label and self.banner_image_original:
            self.bind("<Configure>", lambda event: resize_banner(
                self,
                self.banner_label,
                self.banner_image_original
            ))

        self.icon_image_original = Image.open(ICONS_PATHS['gratitude_diary'])

        add_icon_and_label(self, text=PAGES_NAMES['gratitude_diary'],
                           icon_path=ICONS_PATHS['gratitude_diary'],
                           bg_color=INTERFACE['bg_color'])
        add_separator(parent=self, color=INTERFACE['separator'])

        # Entry
        self.entry_text = tk.Text(self, width=50, height=1, font=GRATITUDE_DIARY['entry_font'])
        self.entry_text.pack(pady=10)
        self.entry_text.bind("<Return>", lambda event: self.save_entry())

        # Save button
        self.save_button = tk.Button(self, text="Save Entry", command=self.save_entry,
                                     font=GRATITUDE_DIARY['buttons_font'],
                                     bg=GRATITUDE_DIARY['add_button_color'])
        self.save_button.pack(pady=5)
        self.save_button.config(cursor="hand2")

        # Display current entries
        self.display_monthly_entries()

    def save_tasks_to_json(self):
        """
        Save entries to JSON.

        :return: None
        """
        with open(self.json_file, "w", encoding="utf-8") as file:
            json.dump(self.tasks, file, ensure_ascii=False, indent=4)

    def display_monthly_entries(self):
        """
        This method displays all the saved gratitude entries for each month in the current year.
        It organizes the entries by month and day and allows the user to view or edit them by right-clicking.
        It also handles clearing the existing labels before displaying new entries.

        :return: None
        """
        for widget in self.winfo_children():
            if isinstance(widget, tk.Label):
                if widget.cget("text").startswith("- ") or widget.cget("text").startswith("    "):
                    widget.destroy()

        gratitude_diary = self.tasks.get("gratitude_diary", {})
        current_year = datetime.now().year

        months_in_reverse = list(calendar.month_name[1:])[::-1]

        for month in months_in_reverse:
            days = gratitude_diary.get(month, {})
            if not days:
                continue

            month_label = tk.Label(self, text=f"- {month}", font=GRATITUDE_DIARY['months_label_font'],
                                   bg=INTERFACE['bg_color'])
            month_label.pack(anchor="w", padx=10, pady=(10, 0))

            month_num = list(calendar.month_name).index(month)
            days_in_month = calendar.monthrange(current_year, month_num)[1]

            for day in range(1, days_in_month + 1):
                day_text = days.get(str(day), "-")

                entry_label = tk.Label(self, text=f"    {day}. {day_text}", font=GRATITUDE_DIARY['tasks_font'],
                                       bg=INTERFACE['bg_color'],
                                       wraplength=300,
                                       justify="left")
                entry_label.bind("<Button-3>", lambda e, m=month, d=day: self.edit_entry(m, d))
                entry_label.pack(anchor="w", padx=20)

                entry_label.bind("<Enter>", lambda event: on_day_hover(event))
                entry_label.bind("<Leave>", lambda event: self.on_day_leave(event))

    def on_day_leave(self, event):
        """
        This method is triggered when the mouse leaves a day entry label in the gratitude diary.
        It removes the cursor change (restores it to the default cursor) and destroys any
        tooltip window that may have been displayed when the mouse entered the label.

        :param event: The event object passed when the mouse leaves the label, containing details about the event.
        :return: None
        """
        if hasattr(self, 'hover_window'):
            self.hover_window.destroy()
        event.widget.config(cursor="")

    def edit_entry(self, month, day):
        """
        This method is triggered when the user wants to edit a specific day's entry in the gratitude diary.
        It opens a new window with a text editor where the user can modify the entry and save the changes.

        :param month: The month of the entry to be edited (e.g., "January")
        :param day: The day of the entry to be edited (e.g., 1)
        :return: None
        """
        day_text = self.tasks["gratitude_diary"].get(month, {}).get(str(day), "")

        edit_window = tk.Toplevel(self)
        edit_window.withdraw()
        edit_window.title(f"Edit Entry - {month} {day}")
        # Добавляем иконку на окно (для Windows)
        center_window_on_parent(self.main_window, edit_window, 400, 100)
        edit_window.iconbitmap(APP['icon_path'])  # Замените на путь к вашему .ico файлу

        text_editor = tk.Text(edit_window, width=40, height=1, font=GRATITUDE_DIARY['toplevel_windows_font'])
        text_editor.insert(tk.END, day_text)
        text_editor.pack(pady=10)
        text_editor.bind("<Return>", lambda event: save_edit())

        def save_edit():
            """
            This function is triggered when the user saves the edited entry. It updates the task data and
            refreshes the interface to reflect the changes.

            :return: None
            """
            new_text = text_editor.get("1.0", tk.END).strip()
            self.tasks["gratitude_diary"].setdefault(month, {})[str(day)] = new_text
            self.save_tasks_to_json()
            self.display_monthly_entries()
            edit_window.destroy()

        save_button = tk.Button(edit_window, text="Save", command=save_edit,
                                font=GRATITUDE_DIARY['toplevel_windows_font'])
        save_button.pack(pady=5)
        save_button.config(cursor="hand2")

        edit_window.deiconify()

    def save_entry(self):
        """
        This method saves the user's gratitude entry for the current day. It retrieves the content from the
        text widget, validates that there is some input, saves it to the tasks dictionary, and updates the display.

        :return: None
        """
        new_entry = self.entry_text.get("1.0", tk.END).strip()
        if not new_entry:
            messagebox.showwarning("Empty Entry", "Please enter some text before saving.")
            return

        today = datetime.now()
        month = calendar.month_name[today.month]
        day = str(today.day)

        self.tasks["gratitude_diary"].setdefault(month, {})[day] = new_entry
        self.save_tasks_to_json()

        self.entry_text.delete("1.0", tk.END)
        self.display_monthly_entries()

    def navigate_to_yearly_plans(self):
        """
        Return to Yearly plans.

        :return: None
        """
        self.main_window.bind_events()
        self.main_window.show_tab_content("yearly_plans")

    def navigate_to_year(self, year):
        """
        This method is responsible for navigating to the year view, where the user can see the data
        related to a particular year. It clears the current screen and loads a new frame for the selected year.

        :param year: The year that the user wishes to view.
        :return: None
        """
        self.main_window.bind_events()
        clear_canvas(self.parent)

        from src.year import Year
        year_frame = Year(self.parent, json_file=f"data/years/{year}.json", main_window=self.main_window, year=year)
        year_frame.pack(fill=tk.BOTH, expand=True)

        reset_canvas_view(self.main_window)
