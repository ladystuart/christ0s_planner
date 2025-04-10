import datetime
from config.imports import *
from config.settings import WORK_PLACE
from config.tooltip import ToolTip
import re
from config.utils import add_source_label_second_level as add_source_label_work_place


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


async def add_note_to_server(note_content, work_place):
    """
    Adds a note to the server by sending a POST request with the note content and work place name.

    Args:
        note_content (str): The content of the note to be added.
        work_place (str): The name of the work place where the note is associated.

    Returns:
        dict: A dictionary containing error information if the request fails, otherwise returns None.
    """
    try:
        async with aiohttp.ClientSession() as session:
            payload = {"work_name": work_place, "note_text": note_content}
            async with session.post(f"{SERVER_URL}/add_work_note",
                                    json=payload, ssl=SSL_ENABLED) as response:
                if response.status != 200:
                    error_message = await response.text()
                    raise Exception(f"Failed to add note: {error_message}")
    except Exception as e:
        print(f"Error adding note: {e}")
        return {"error": str(e)}


async def get_notes_from_server(work_name):
    """
    Retrieves the notes associated with a specific work place from the server by sending a GET request.

    Args:
        work_name (str): The name of the work place whose notes are to be retrieved.

    Returns:
        list: A list of notes associated with the specified work place. If an error occurs, an empty list or
              an error message dictionary is returned.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SERVER_URL}/get_work_place_notes",
                                   params={"work_name": work_name}, ssl=SSL_ENABLED) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("notes", [])
                else:
                    print(f"Error: {response.status}")
                    return []
    except Exception as e:
        print(f"Error getting notes: {e}")
        return {"error": str(e)}


async def delete_note_on_server(note_text, work_place):
    """
    Deletes a note from the server by sending a POST request with the note content and work place name.

    Args:
        note_text (str): The content of the note to be deleted.
        work_place (str): The name of the work place where the note is associated.

    Returns:
        dict: A dictionary containing error information if the request fails, otherwise returns None.
    """
    try:
        payload = {"work_name": work_place, "note_text": note_text}
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{SERVER_URL}/delete_work_place_note",
                                    json=payload, ssl=SSL_ENABLED) as response:
                if response.status != 200:
                    print(f"Error deleting note: {await response.text()}")
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}


async def edit_task_on_server(work_place, new_text, old_text, btn):
    """
    Edits an existing note on the server by sending a POST request with the old and new note text and work place name.

    Args:
        btn (tk.Button): "Save" button. State updates to "disabled".
        work_place (str): The name of the work place where the note is associated.
        new_text (str): The updated content of the note.
        old_text (str): The original content of the note to be updated.

    Returns:
        dict or None: Returns the server's response as a dictionary if the request is successful,
                      otherwise returns None if there's an error or failure.
    """
    payload = {
        "work_name": work_place,
        "new_text": new_text,
        "old_text": old_text
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{SERVER_URL}/edit_work_place_note",
                                    json=payload, ssl=SSL_ENABLED) as response:
                if response.status == 200:
                    btn.config(state="disabled")
                    return await response.json()
                else:
                    error_message = await response.text()
                    print(f"Note update error: {error_message}")
                    return None
    except Exception as e:
        print(f"Error: {e}")
        return None


class WorkPlace(tk.Frame):
    """
    The WorkPlace class represents a specific screen or section within the main window of a Tkinter-based application.
    It initializes the user interface elements for a work-related page, loads tasks from server,
    displays a clickable label for navigation, adds a banner, resizes the banner based on window size,
    and includes a note field for additional interaction.

    Attributes:
        parent (tk.Widget): The parent widget that contains this frame.
        main_window (MainWindow): The main window of the application, used to access the check_scrollbar method.
        button_name (str): The name that will be displayed on the button.
        tasks (list): A list of tasks loaded from server.
    """
    def __init__(self, parent, main_window, button_name):
        """
        Initializes the WorkPlace frame with the given parameters and sets up various UI elements.

        :param parent: The parent widget that holds this frame.
        :param main_window: The main window of the application, used to check the scrollbar.
        :param button_name: The label text for the button that will be displayed.
        """
        super().__init__(parent)
        self.configure(bg=INTERFACE['bg_color'])
        self.main_window = main_window
        self.main_window.disable_buttons()
        self.button_name = button_name
        self.parent = parent
        self.main_window.check_scrollbar()

        self.tasks = asyncio.run(get_notes_from_server(self.button_name))

        self.first_clickable_label = add_source_label_work_place(self,  # Parent element
                                                                 icon_path_1=ICONS_PATHS['work'],
                                                                 clickable_text="Work /",
                                                                 click_command=self.navigate_to_work,
                                                                 icon_path_2=ICONS_PATHS['work_place'],
                                                                 text=self.button_name
                                                                 )

        self.first_clickable_label["state"] = "disabled"

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

        self.main_window.enable_buttons()
        self.first_clickable_label["state"] = "normal"

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

        self.frame = tk.Frame(self)
        self.frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.update_display_text()

    def save_note(self, note_text):
        """
        Saves the content of the note from the `note_text` widget to server.
        If the note is non-empty, it appends the note to the corresponding task in the `self.tasks` dictionary
        and writes the updated dictionary to server. It also clears the note text field after saving.

        :param note_text: The Text widget containing the user's note content. The content is retrieved,
                          saved to the tasks dictionary, and written to the server.
        :return: None
        """
        note_content = note_text.get("1.0", tk.END).strip()

        if not note_content:
            messagebox.showwarning("Error", "Cannot save an empty note!")
            return

        existing_texts = {task["text"] for task in self.tasks}
        if note_content in existing_texts:
            messagebox.showwarning("Error", "This note already exists!")
            return

        if note_content:
            note_data = {
                "text": note_content,
                "created_at": datetime.datetime.now(datetime.UTC).isoformat()
            }

            self.tasks.append(note_data)

            asyncio.run(add_note_to_server(note_content, self.button_name))

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
        if hasattr(self, 'frame') and self.frame is not None:
            for widget in self.frame.winfo_children():
                widget.destroy()

        if not self.tasks:
            return

        sorted_tasks = sorted(self.tasks, key=lambda x: x["created_at"], reverse=True)

        for display_idx, note in enumerate(sorted_tasks):
            note_text = note.get("text", "")
            created_at = note.get("created_at", "")

            # Create a frame for the note
            task_frame = tk.Frame(self.frame)
            task_frame.pack(padx=10, pady=10, fill="both", expand=True)

            # Create the Text widget
            text_widget = tk.Text(task_frame, font=WORK_PLACE['text_font'], wrap="word",
                                  bg=WORK_PLACE['text_bg_color'], bd=2)
            text_widget.grid(row=0, column=0, sticky="nsew", padx=10)

            lines = note_text.split('\n')
            text_widget.config(height=len(lines))
            text_widget.insert(tk.END, note_text)
            add_clickable_links(text_widget)

            old_text = note_text

            # Save button
            save_button = tk.Button(task_frame, text="Save", font=WORK_PLACE['buttons_font'],
                                    bg=WORK_PLACE['save_button_color'], cursor="hand2",
                                    command=lambda idx=display_idx, text_widget=text_widget, old_text=old_text:
                                    self.save_edited_note(idx, text_widget, old_text, save_button), state="disabled")
            save_button.grid(row=0, column=1, padx=10)

            def on_modified(event, old_text=old_text, btn=save_button, txt=text_widget):
                """
                Handles the modification event of a specific text widget and updates the state of the associated Save button.

                This function compares the current content of the text widget with its original value (old_text).
                If the content has changed, the Save button is enabled. If the content matches the original, the button is disabled.

                Args:
                    event: The <<Modified>> Tkinter virtual event triggered when the text widget is edited.
                    old_text (str): The original, unmodified text of the widget.
                    btn (tk.Button): The Save button that should be enabled or disabled depending on changes.
                    txt (tk.Text): The text widget being monitored for changes.

                Returns:
                    None
                """
                current = txt.get("1.0", tk.END).strip()
                if current != old_text:
                    btn.config(state="normal")
                else:
                    btn.config(state="disabled")
                txt.edit_modified(False)

            text_widget.bind("<<Modified>>", on_modified)
            text_widget.edit_modified(False)

            # Delete button
            delete_button = tk.Button(task_frame, text="Delete", font=WORK_PLACE['buttons_font'],
                                      bg=WORK_PLACE['delete_button_color'], cursor="hand2",
                                      command=lambda idx=display_idx, text_widget=text_widget: self.delete_note(idx,
                                                                                                      text_widget))
            delete_button.grid(row=0, column=2, padx=5)

            # Make text widget expandable
            task_frame.grid_columnconfigure(0, weight=1)

    def delete_note(self, note_idx, text_widget):
        """
        Deletes a note from the displayed list when the user right-clicks on it and confirms the deletion.
        It asks the user for confirmation via a message box. If confirmed, it removes the note from the
        internal tasks dictionary and updates the server data. It then refreshes the display of the notes.

        :param note_idx: The index of the note in the list of notes to be deleted.
        :param text_widget: The Text widget that displays the note to be deleted.
        :return: None
        """
        response = messagebox.askyesno("Delete", "Are you sure you want to delete this entry?")

        current_scroll_position = self.main_window.canvas.yview()

        text_content = text_widget.get("1.0", tk.END).strip()

        if response:
            text_widget.destroy()

            del self.tasks[note_idx]

            asyncio.run(delete_note_on_server(text_content, self.button_name))

            self.update_display_text()

            self.main_window.after(100, lambda: self.main_window.canvas.yview_moveto(current_scroll_position[0]))

    def save_edited_note(self, note_idx, text_widget, old_text, btn):
        """
        Saves the edited content of a note in real-time as the user modifies it.
        This method is called whenever the user makes changes to a note. If the content
        has changed, it updates the internal `self.tasks` dictionary and saves the changes
        to the server.

        Args:
            note_idx (int): The index of the note in the list of notes to be updated.
            text_widget (tk.Text): The Text widget containing the edited note content.
            old_text (str): The original content of the note before it was edited.

        Returns:
            None
        """
        current_scroll_position = self.main_window.canvas.yview()

        edited_content = text_widget.get("1.0", tk.END).strip()

        # 1. If the note hasn't been modified
        if edited_content == old_text:
            messagebox.showwarning("No Changes", "The note has not been modified.")
            return

        # 2. If the same note already exists in another entry
        all_texts = [task["text"] for i, task in enumerate(self.tasks) if i != note_idx]
        if edited_content in all_texts:
            messagebox.showwarning("Duplicate Entry", "This note already exists.")
            return

        # 3. If the note is empty
        if not edited_content:
            messagebox.showwarning("Error", "Cannot save an empty note.")
            return

        for task in self.tasks:
            if task["text"] == old_text:
                task["text"] = edited_content
                break

        asyncio.run(edit_task_on_server(self.button_name, edited_content, old_text, btn))

        self.update_display_text()

        messagebox.showinfo("Success", "Note successfully edited.")

        self.main_window.after(100, lambda: self.main_window.canvas.yview_moveto(current_scroll_position[0]))

    def navigate_to_work(self):
        """
        Go to work.

        :return: None
        """
        self.main_window.bind_events()
        self.main_window.show_tab_content("work")
