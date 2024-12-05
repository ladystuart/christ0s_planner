from config.imports import *
from config.settings import WORK_PLACE
from config.tooltip import ToolTip
import re
from config.utils import load_tasks_from_json, add_source_label_second_level as add_source_label_work_place


def add_clickable_links(note_text):
    """
    This method scans the text within a Text widget (`note_text`) for any URLs,
    and makes them clickable. It configures each detected URL to appear as a link (blue and underlined),
    and binds mouse events to open the link when clicked and change the cursor on hover.

    :param note_text: The Text widget that contains the note text. The method scans this widget
                      for URLs to make them clickable.
    :return: None
    """
    text = note_text.get("1.0", tk.END)
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)

    for url in urls:
        start_idx = text.find(url)
        end_idx = start_idx + len(url)

        note_text.tag_add("link", f"1.{start_idx}", f"1.{end_idx}")
        note_text.tag_configure("link", foreground="blue", underline=True)

        note_text.tag_bind("link", "<Button-1>", lambda e, url=url: open_link(url))
        note_text.tag_bind("link", "<Enter>", lambda e: note_text.config(cursor="hand2"))
        note_text.tag_bind("link", "<Leave>",
                           lambda e: note_text.config(cursor=""))


class WorkPlace(tk.Frame):
    """
    The WorkPlace class represents a specific screen or section within the main window of a Tkinter-based application.
    It initializes the user interface elements for a work-related page, loads tasks from a JSON file,
    displays a clickable label for navigation, adds a banner, resizes the banner based on window size,
    and includes a note field for additional interaction.

    Attributes:
        parent (tk.Widget): The parent widget that contains this frame.
        main_window (MainWindow): The main window of the application, used to access the check_scrollbar method.
        json_file (str): The path to the JSON file that contains tasks to be loaded.
        button_name (str): The name that will be displayed on the button.
        tasks (list): A list of tasks loaded from the JSON file.
    """
    def __init__(self, parent, main_window, json_file, button_name):
        """
        Initializes the WorkPlace frame with the given parameters and sets up various UI elements.

        :param parent: The parent widget that holds this frame.
        :param main_window: The main window of the application, used to check the scrollbar.
        :param json_file: The path to the JSON file containing tasks.
        :param button_name: The label text for the button that will be displayed.
        """
        super().__init__(parent)
        self.configure(bg=INTERFACE['bg_color'])
        self.main_window = main_window
        self.button_name = button_name

        self.parent = parent
        self.json_file = json_file
        self.main_window.check_scrollbar()

        self.tasks = load_tasks_from_json(json_file)

        add_source_label_work_place(
            self,  # Parent element
            icon_path_1=ICONS_PATHS['work'],
            clickable_text="Work /",
            click_command=self.navigate_to_work,
            icon_path_2=ICONS_PATHS['work_place'],
            text=self.button_name
        )

        # Banner add
        self.banner_label, self.banner_image_original = add_banner(
            self,
            banner_path=BANNER_PATHS['work_place'],
            bg_color=INTERFACE['bg_color']
        )

        # resize_banner
        if self.banner_label and self.banner_image_original:
            self.bind("<Configure>", lambda event: resize_banner(
                self,
                self.banner_label,
                self.banner_image_original
            ))

        add_icon_and_label(self, text=self.button_name, icon_path=ICONS_PATHS['work_place'],
                           bg_color=INTERFACE['bg_color'])
        add_separator(parent=self, color=INTERFACE['separator'])

        self.add_note_field()

    def add_note_field(self):
        """
        This method adds a note field to the current frame. It creates a text area where users can enter and save notes.
        The text field is configured to support word wrapping, custom fonts, and a specific background color. Additionally,
        the method adds a save button for saving the note, provides tooltips, and sets up clickable links within the note text.

        The note field is placed inside a frame, which is packed into the main window with some padding and flexibility to expand.

        :return: None
        """
        note_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        note_frame.pack(padx=10, pady=10, fill="both", expand=True)

        note_text = tk.Text(note_frame, height=10, font=WORK_PLACE['text_font'],
                            wrap="word", bg=WORK_PLACE['text_bg_color'], bd=2)
        note_text.pack(fill="both", expand=True, padx=5, pady=5)

        note_text.tag_configure("link", foreground="blue", underline=True)

        add_clickable_links(note_text)

        save_button = tk.Button(note_frame, text="Save entry", font=WORK_PLACE['buttons_font'],
                                command=lambda: self.save_note(note_text), bg=WORK_PLACE['add_button_color'])
        save_button.pack(pady=10)
        save_button.config(cursor="hand2")
        ToolTip(save_button, "Right click on entry to delete")

        self.update_display_text()

    def save_note(self, note_text):
        """
        Saves the content of the note from the `note_text` widget to a JSON file.
        If the note is non-empty, it appends the note to the corresponding task in the `self.tasks` dictionary
        and writes the updated dictionary to the specified JSON file. It also clears the note text field after saving.

        :param note_text: The Text widget containing the user's note content. The content is retrieved,
                          saved to the tasks dictionary, and written to the JSON file.
        :return: None
        """
        note_content = note_text.get("1.0", tk.END).strip()
        if note_content:
            if self.button_name not in self.tasks:
                self.tasks[self.button_name] = {"notes": []}
            self.tasks[self.button_name]["notes"].append(note_content)

            with open(self.json_file, "w", encoding='utf-8') as file:
                json.dump(self.tasks, file, ensure_ascii=False, indent=4)

            self.update_display_text()

            note_text.delete("1.0", tk.END)

    def update_display_text(self):
        """
        This method updates the display of notes in the UI by creating new Text widgets for each saved note.
        It clears any existing note display widgets, retrieves the notes from the `self.tasks` dictionary,
        and populates the UI with them. It also adds clickable links to the notes and binds events to allow
        for editing and deleting notes directly from the UI.

        :return: None
        """
        for widget in self.winfo_children():
            if isinstance(widget, tk.Text):
                widget.destroy()

        if self.button_name in self.tasks and "notes" in self.tasks[self.button_name]:
            notes = self.tasks[self.button_name]["notes"]

            for display_idx, note_content in enumerate(reversed(notes)):
                original_idx = len(notes) - 1 - display_idx

                text_widget = tk.Text(self, font=WORK_PLACE['text_font'], wrap="word",
                                      bg=WORK_PLACE['text_bg_color'], bd=2)
                text_widget.pack(padx=10, pady=10, fill="both", expand=True)

                lines = note_content.split('\n')
                text_widget.config(height=len(lines))

                text_widget.insert(tk.END, note_content)

                add_clickable_links(text_widget)

                text_widget.bind("<KeyRelease>", lambda e, idx=original_idx: self.save_edited_note_on_the_fly(e, idx))

                text_widget.bind("<Button-3>",
                                 lambda e, idx=original_idx: self.delete_note_on_right_click(e, idx, text_widget))

    def delete_note_on_right_click(self, event, note_idx, text_widget):
        """
        Deletes a note from the displayed list when the user right-clicks on it and confirms the deletion.
        It asks the user for confirmation via a message box. If confirmed, it removes the note from the
        internal tasks dictionary and updates the JSON file. It then refreshes the display of the notes.

        :param event: The event that triggered the method (right-click event).
        :param note_idx: The index of the note in the list of notes to be deleted.
        :param text_widget: The Text widget that displays the note to be deleted.
        :return: None
        """
        response = messagebox.askyesno("Delete", "Are you sure you want to delete this entry?")

        if response:
            text_widget.destroy()

            del self.tasks[self.button_name]["notes"][note_idx]

            with open(self.json_file, "w", encoding='utf-8') as file:
                json.dump(self.tasks, file, ensure_ascii=False, indent=4)

            self.update_display_text()
        else:
            print("Delete aborted.")

    def save_edited_note_on_the_fly(self, event, note_idx):
        """
        Saves the edited content of a note in real-time as the user modifies it.
        This method is called whenever the user makes changes to a note. If the content
        has changed, it updates the internal `self.tasks` dictionary and saves the
        changes to the JSON file.

        :param event: The event that triggered the method (typically a key release or text change event).
        :param note_idx: The index of the note in the list of notes to be updated.
        :return: None
        """
        edited_content = event.widget.get("1.0", tk.END).strip()

        if edited_content != self.tasks[self.button_name]["notes"][note_idx]:
            self.tasks[self.button_name]["notes"][note_idx] = edited_content

            with open(self.json_file, "w", encoding='utf-8') as file:
                json.dump(self.tasks, file, ensure_ascii=False, indent=4)

    def navigate_to_work(self):
        """
        Go to work.

        :return: None
        """
        self.main_window.bind_events()
        self.main_window.show_tab_content("work")
