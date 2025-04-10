from config.imports import *
from config.settings import WORK
from config.tooltip import ToolTip
from config.utils import load_icon_image
from src.work_place import WorkPlace


async def add_work_place_to_server(work_name):
    """
    Sends a request to the server to add a new work place with the given name.

    This function makes an asynchronous HTTP POST request to the server to add a work place. It sends the work
    name in the request body as JSON. If the request fails (i.e., the server returns a status code other than 200),
    an error message is printed. If an exception occurs during the request, the error is caught and logged.

    Args:
        work_name (str): The name of the work place to be added.

    Returns:
        None
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{SERVER_URL}/add_work_place",
                                    json={"work_name": work_name}, ssl=SSL_ENABLED) as response:
                if response.status != 200:
                    print(f"Failed to add work place. Status code: {response.status}")
        except Exception as e:
            print(f"Error sending work place to server: {e}")


async def load_work_places_from_server():
    """
    Fetches the list of work places from the server.

    This function makes an asynchronous HTTP GET request to the server to retrieve a list of work places.
    If the server responds with a status code of 200, the response is parsed as JSON and returned.
    If the request fails or an exception occurs, an empty dictionary with a "buttons" key is returned.

    Returns:
        dict: A dictionary containing the work places. If the request is successful, the dictionary will contain
              the list of work places under the "buttons" key. If there is an error or failure, an empty list
              will be returned under the "buttons" key.
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{SERVER_URL}/get_work_place", ssl=SSL_ENABLED) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    print(f"Failed to load work places. Status code: {response.status}")
                    return {"buttons": []}
        except Exception as e:
            print(f"Error loading work places from server: {e}")
            return {"buttons": []}


async def delete_work_place(button_name):
    """
    Deletes a work place from the server by its name.

    This function makes an asynchronous HTTP POST request to the server to delete a work place identified by the
    given `button_name`. If the deletion is successful (status code 200), the response is returned as JSON.
    If the deletion fails, the error details are printed and a dictionary with the error message is returned.

    Args:
        button_name (str): The name of the work place to be deleted.

    Returns:
        dict: If the request is successful, a dictionary containing the server's response is returned. If there is an error,
              a dictionary with an `"error"` key and the error message is returned.
    """
    try:
        data = {"work_name": button_name}
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{SERVER_URL}/delete_work_place",
                                    json=data, ssl=SSL_ENABLED) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Failed to delete: {button_name}. Status code: {response.status}")
                    error_data = await response.json()
                    print(f"Error details: {error_data.get('detail', 'Unknown error')}")
                    return {"error": error_data.get('detail', 'Unknown error')}
    except Exception as e:
        print(f"Error deleting work place: {e}")
        return {"error": str(e)}


async def update_work_place_title(old_name, new_name):
    """
    Updates the title of a work place on the server.

    This function sends an asynchronous HTTP POST request to the server to update the title of a work place identified by
    the `old_name` to the new title `new_name`. If the update is successful (status code 200), the response is returned
    as JSON. If the update fails, the error details are printed and a dictionary with the error message is returned.

    Args:
        old_name (str): The current name of the work place to be updated.
        new_name (str): The new name for the work place.

    Returns:
        dict: If the request is successful, a dictionary containing the server's response is returned. If there is an error,
              a dictionary with an `"error"` key and the error message is returned.
    """
    try:
        data = {"new_work_name": new_name, "old_work_name": old_name}

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{SERVER_URL}/update_work_place_title",
                                    json=data, ssl=SSL_ENABLED) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    error_data = await response.json()
                    print(f"Failed to update work place title. Reason: {error_data.get('detail', 'Unknown error')}")
                    return {"error": error_data.get('detail', 'Unknown error')}
    except Exception as e:
        print(f"Error updating work place title: {e}")
        return {"error": str(e)}


class Work(tk.Frame):
    """
    The Work class represents a specific section of the user interface that deals with work-related tasks.
    It loads data from server, displays an icon, adds banners, buttons, and manages task-related functionality.

    This class is a Tkinter Frame, and it's used to structure the UI elements related to work, including
    the task list and any associated buttons or interactive elements.
    """
    def __init__(self, parent, main_window):
        """
        Initializes the Work frame with necessary components such as icons, banners, and buttons.

        :param parent: The parent widget (typically the main window) that will contain this frame.
        :param main_window: The main window of the application, often used for global actions.
        """
        super().__init__(parent)
        self.configure(bg=INTERFACE['bg_color'])
        self.main_window = main_window
        self.main_window.disable_buttons()
        self.parent = parent
        self.work = asyncio.run(load_work_places_from_server())

        self.icon_image_original = asyncio.run(load_icon_image(SERVER_URL, ICONS_PATHS['work'], VERIFY_ENABLED))

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

        self.main_window.enable_buttons()

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
        the main interface, and the title is saved to server.

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
                if button_name in self.work["buttons"]:
                    messagebox.showerror("Error", f"The work title '{button_name}' already exists.")
                    popup.lift()
                    return

                if "buttons" not in self.work:
                    self.work["buttons"] = []

                self.add_new_button(button_name)

                if button_name not in self.work["buttons"]:
                    self.work["buttons"].append(button_name)

                asyncio.run(add_work_place_to_server(button_name))

                popup.destroy()
            else:
                messagebox.showerror("Error", "Work title cannot be empty.")
                popup.lift()
                return

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

            asyncio.run(delete_work_place(button_name))

    def edit_button(self, button_name):
        """
        Opens a popup window to allow the user to edit the title of an existing button.

        This method creates a popup window where the user can input a new title for the button specified by
        `button_name`. If the user confirms the change, the button's title is updated in the UI, and any related
        data (e.g., button name in `self.work`) is also updated. The changes are then saved to server.

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

                if new_button_name in self.work["buttons"]:
                    messagebox.showwarning("Error", f"A work place with the name '{new_button_name}' already exists.")
                    popup.lift()
                    return

                for widget in self.new_buttons_frame.winfo_children():
                    if widget.cget("text") == button_name:
                        widget.config(text=new_button_name)
                        widget.config(command=lambda: self.button_action(new_button_name))
                        # Update button command
                        widget.bind("<Button-3>", lambda event: self.show_context_menu(event, new_button_name))

                if button_name in self.work["buttons"]:
                    self.work["buttons"].remove(button_name)
                self.work["buttons"].append(new_button_name)

                asyncio.run(update_work_place_title(button_name, new_button_name))
                popup.destroy()
            else:
                if new_button_name == "":
                    messagebox.showwarning("Error", "Title can't be empty.")
                    popup.lift()
                elif new_button_name == button_name:
                    messagebox.showinfo("Info", "Title hasn't been changed.")
                    popup.lift()

        confirm_button = tk.Button(popup, text="Submit", font=WORK['toplevel_windows_font'],
                                   bg=INTERFACE['bg_color'], command=confirm_name)
        confirm_button.pack(pady=10)
        popup.deiconify()

    def button_action(self, button_name):
        """
        Handles the action triggered when a button is clicked.

        This method is called when a button (created dynamically) is clicked. It clears the current content
        from the canvas, creates a new `WorkPlace` frame based on the `button_name`, and packs the frame into
        the parent widget. The `WorkPlace` frame is initialized with `button_name`, which
        determines the content shown in the frame. It also attempts to reset the vertical view of the canvas.

        :param button_name: The name of the button that was clicked. This is used to determine what content to show.
        :return: None
        """
        clear_canvas(self.parent)
        work_button_frame = WorkPlace(self.parent, main_window=self.main_window, button_name=button_name)
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
        for button_name in button_names:
            self.add_new_button(button_name)
