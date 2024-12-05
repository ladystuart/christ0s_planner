from config.imports import *
from config.settings import WORK
from config.tooltip import ToolTip
from config.utils import load_tasks_from_json
from src.work_place import WorkPlace


class Work(tk.Frame):
    """
    The Work class represents a specific section of the user interface that deals with work-related tasks.
    It loads data from a JSON file, displays an icon, adds banners, buttons, and manages task-related functionality.

    This class is a Tkinter Frame, and it's used to structure the UI elements related to work, including
    the task list and any associated buttons or interactive elements.
    """
    def __init__(self, parent, main_window, json_file):
        """
        Initializes the Work frame with necessary components such as icons, banners, and buttons.

        :param parent: The parent widget (typically the main window) that will contain this frame.
        :param main_window: The main window of the application, often used for global actions.
        :param json_file: The path to a JSON file containing task-related data for this section.
        """
        super().__init__(parent)
        self.configure(bg=INTERFACE['bg_color'])
        self.main_window = main_window
        self.parent = parent
        self.json_file = json_file
        self.work = load_tasks_from_json(json_file)

        self.icon_image_original = Image.open(ICONS_PATHS['work'])  # Year icon path
        self.icon_image = self.icon_image_original.resize((20, 20), Image.Resampling.LANCZOS)
        self.icon_photo = ImageTk.PhotoImage(self.icon_image)

        add_source_label(self, ICONS_PATHS['work'], PAGES_NAMES['work'],
                         bg_color=INTERFACE['bg_color'], font=INTERFACE['source_label_font'])

        # Banner add
        self.banner_label, self.banner_image_original = add_banner(
            self,
            banner_path=BANNER_PATHS['work'],
            bg_color=INTERFACE['bg_color']
        )

        # resize_banner
        if self.banner_label and self.banner_image_original:
            self.bind("<Configure>", lambda event: resize_banner(
                self,
                self.banner_label,
                self.banner_image_original
            ))

        add_icon_and_label(self, text=PAGES_NAMES['work'], icon_path=ICONS_PATHS['work'],
                           bg_color=INTERFACE['bg_color'])
        add_separator(parent=self, color=INTERFACE['separator'])

        self.add_button_creator()

        # Add buttons if exist
        if "buttons" in self.work:
            self.load_existing_buttons(self.work["buttons"])

    def add_button_creator(self):
        """
        Creates and adds a button for creating a new work page to the UI.

        This method creates a frame that contains a button for adding a new work page. The button is
        configured with text, font, background color, and an action (command). When clicked, it will
        open a window to input the name of the new work page. The button is styled with a "hand2" cursor
        to indicate it is clickable.

        :return: None
        """
        button_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        button_frame.pack(pady=10, padx=10, anchor="w")

        add_button = tk.Button(button_frame, text="Add work page", font=WORK['buttons_font'],
                               command=self.open_name_input_window, bg=WORK['add_button_color'],
                               relief=WORK['add_button_relief'])
        add_button.pack(side="left", padx=5)
        add_button.config(cursor="hand2")

    def open_name_input_window(self):
        """
        Opens a popup window that allows the user to enter a title for a new work page.

        This method creates a top-level window (popup) where the user can input a title for a new work page.
        The window includes a label, an input field (entry widget), and a submit button. When the user enters
        a title and clicks the submit button (or presses Enter), the title is used to create a new button on
        the main interface, and the title is saved to a JSON file for persistence.

        :return: None
        """
        popup = tk.Toplevel(self)
        popup.withdraw()
        popup.title("Work title")
        center_window_on_parent(self.main_window, popup, 300, 150)
        popup.configure(bg=INTERFACE['bg_color'])

        try:
            icon_image = Image.open(APP['icon_path']).resize((32, 32), Image.Resampling.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_image)
            popup.iconphoto(False, icon_photo)
        except Exception as e:
            print(f"Error icon load: {e}")

        label = tk.Label(popup, text="Enter work title:", font=WORK['toplevel_windows_font'],
                         bg=INTERFACE['bg_color'])
        label.pack(pady=10)

        input_field = tk.Entry(popup, font=WORK['toplevel_windows_font'])
        input_field.pack(pady=5, padx=10, fill="x")
        input_field.bind("<Return>", lambda event: confirm_name())

        def confirm_name():
            """
            Confirm new button name.

            :return: None
            """
            button_name = input_field.get().strip()
            if button_name:
                self.add_new_button(button_name)
                self.save_button_to_json(button_name)
            popup.destroy()

        confirm_button = tk.Button(popup, text="Submit", font=WORK['toplevel_windows_font'],
                                   bg=INTERFACE['bg_color'], command=confirm_name)
        confirm_button.pack(pady=10)
        confirm_button.config(cursor="hand2")

        popup.deiconify()

    def add_new_button(self, button_name):
        """
        Adds a new button to the interface with the given name and functionality.

        This method dynamically creates a new button and adds it to the frame `new_buttons_frame`.
        The button is configured with the provided `button_name` as its label, and is set up with
        custom font, background color, relief style, and a click command. The button will trigger
        the `button_action` method when clicked. Additionally, a tooltip is added to the button,
        and a context menu is bound to the right-click event (for edit or delete actions).

        :param button_name: The name or label of the new button that will be displayed on the button.
        :return: None
        """
        if not hasattr(self, 'new_buttons_frame'):
            self.new_buttons_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
            self.new_buttons_frame.pack(pady=10, padx=10, anchor="w")

        new_button = tk.Button(self.new_buttons_frame,
                               text=button_name,
                               font=WORK['buttons_font'],
                               bg=INTERFACE['bg_color'],
                               relief=WORK['buttons_relief'],
                               command=lambda: self.button_action(button_name))
        new_button.pack(side="top", pady=5, anchor="w")
        new_button.config(cursor="hand2")

        ToolTip(new_button, "Right click to edit/delete")

        new_button.bind("<Button-3>", lambda event, btn_name=button_name: self.show_context_menu(event, btn_name))

    def show_context_menu(self, event, button_name):
        """
        Displays a context menu when the user right-clicks on a button.

        This method creates a context menu with options to "Delete" or "Edit" the button that was
        right-clicked. The context menu is displayed at the location of the mouse cursor.

        :param event: The event that triggered the context menu (contains mouse coordinates).
        :param button_name: The name of the button that was right-clicked, which is passed to the
                            corresponding action (delete or edit).
        :return: None
        """
        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_command(label="Delete", command=lambda: self.delete_button(button_name))
        context_menu.add_command(label="Edit", command=lambda: self.edit_button(button_name))

        context_menu.post(event.x_root, event.y_root)

    def delete_button(self, button_name):
        """
        Deletes a button from the interface and removes its associated data.

        This method displays a confirmation dialog asking the user whether they are sure they want to
        delete the button specified by `button_name`. If the user confirms the deletion, the button
        is removed from the UI, and any associated data is deleted from the `work` dictionary.
        The changes are then saved to the JSON file.

        :param button_name: The name of the button to delete.
        :return: None
        """
        response = messagebox.askyesno("Delete", f"Are you sure you want to delete '{button_name}'?")
        if response:
            for widget in self.new_buttons_frame.winfo_children():
                if widget.cget("text") == button_name:
                    widget.destroy()

            if button_name in self.work["buttons"]:
                self.work["buttons"].remove(button_name)

            if button_name in self.work:
                del self.work[button_name]

            self.save_tasks_to_json()

    def edit_button(self, button_name):
        """
        Opens a popup window to allow the user to edit the title of an existing button.

        This method creates a popup window where the user can input a new title for the button specified by
        `button_name`. If the user confirms the change, the button's title is updated in the UI, and any related
        data (e.g., button name in `self.work`) is also updated. The changes are then saved to the JSON file.

        :param button_name: The current title of the button to be edited.
        :return: None
        """
        popup = tk.Toplevel(self)
        popup.withdraw()
        popup.title("Edit title")
        center_window_on_parent(self.main_window, popup, 300, 150)
        popup.configure(bg=INTERFACE['bg_color'])
        popup.iconbitmap(APP['icon_path'])

        label = tk.Label(popup, text="Enter new title:", font=WORK['toplevel_windows_font'],
                         bg=INTERFACE['bg_color'])
        label.pack(pady=10)

        input_field = tk.Entry(popup, font=WORK['toplevel_windows_font'])
        input_field.pack(pady=5, padx=10, fill="x")
        input_field.insert(0, button_name)
        input_field.bind("<Return>", lambda event: confirm_name())

        def confirm_name():
            """
            Confirm new name.

            :return: None
            """
            new_button_name = input_field.get().strip()
            if new_button_name and new_button_name != button_name:
                for widget in self.new_buttons_frame.winfo_children():
                    if widget.cget("text") == button_name:
                        widget.config(text=new_button_name)
                        widget.config(command=lambda: self.button_action(new_button_name))

                if button_name in self.work["buttons"]:
                    self.work["buttons"].remove(button_name)
                self.work["buttons"].append(new_button_name)

                if button_name in self.work:
                    self.work[new_button_name] = self.work.pop(button_name)

                self.save_tasks_to_json()
                popup.destroy()

            else:
                if new_button_name == "":
                    messagebox.showwarning("Error", "Title can't be empty.")
                elif new_button_name == button_name:
                    messagebox.showinfo("Info", "Title hasn't been changed.")
                popup.destroy()

        confirm_button = tk.Button(popup, text="Submit", font=WORK['toplevel_windows_font'],
                                   bg=INTERFACE['bg_color'], command=confirm_name)
        confirm_button.pack(pady=10)
        popup.deiconify()

    def button_action(self, button_name):
        """
        Handles the action triggered when a button is clicked.

        This method is called when a button (created dynamically) is clicked. It clears the current content
        from the canvas, creates a new `WorkPlace` frame based on the `button_name`, and packs the frame into
        the parent widget. The `WorkPlace` frame is initialized with a `json_file` and the `button_name`, which
        determines the content shown in the frame. It also attempts to reset the vertical view of the canvas.

        :param button_name: The name of the button that was clicked. This is used to determine what content to show.
        :return: None
        """
        clear_canvas(self.parent)
        work_button_frame = WorkPlace(self.parent, json_file=DATA_PATHS['work'],
                                      main_window=self.main_window, button_name=button_name)
        work_button_frame.pack(fill=tk.BOTH, expand=True)

        reset_canvas_view(self.main_window)

    def load_existing_buttons(self, button_names):
        """
        Loads and displays the existing buttons from a list of button names.

        This method iterates over a list of `button_names` and creates a button for each name. It adds these buttons
        to the `new_buttons_frame` frame. If the `new_buttons_frame` does not already exist, it creates it. This
        method is typically used to load and display buttons that have been saved or previously created, ensuring
        that the UI reflects the current state of the button data.

        :param button_names: A list of button names that need to be displayed as buttons in the UI.
        :return: None
        """
        if not hasattr(self, 'new_buttons_frame'):
            self.new_buttons_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
            self.new_buttons_frame.pack(pady=10, padx=10, anchor="w")

        for button_name in button_names:
            self.add_new_button(button_name)

    def save_button_to_json(self, button_name):
        """
        Saves a new button name to the JSON file containing the list of buttons.

        This method adds the specified `button_name` to the list of buttons stored in the `work` dictionary.
        If the `buttons` key doesn't exist in the `work` dictionary, it initializes it as an empty list.
        The method then ensures that the `button_name` is only added once (if it isn't already in the list)
        and subsequently saves the updated `work` data to the JSON file using the `save_tasks_to_json` method.

        :param button_name: The name of the button to be added to the list of buttons.
        :return: None
        """
        if "buttons" not in self.work:
            self.work["buttons"] = []

        if button_name not in self.work["buttons"]:
            self.work["buttons"].append(button_name)

        self.save_tasks_to_json()

    def save_tasks_to_json(self):
        """
        Save data to JSON.

        :return: None
        """
        try:
            with open(self.json_file, "w", encoding='utf-8') as file:
                json.dump(self.work, file, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving to JSON {self.json_file}: {e}")
