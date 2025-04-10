from config.imports import *
from config.settings import SERVER_URL
from config.utils import load_icon_image
from src.useful_links import UsefulLinks
from src.yearly_plans import YearlyPlans
from src.lists_for_life import ListsForLife
from src.work import Work


def load_tabs():
    """
    Add side panel tabs from JSON.

    :return: None
    """
    with open(DATA_PATHS['tabs'], "r", encoding="utf-8") as file:
        data = json.load(file)
    return data["tabs"]


class MainWindow(tk.Tk):
    """
    The main application class, inheriting from tk.Tk and representing the main window.
    Responsible for creating the interface, handling events, and loading content and tabs.
    """
    def __init__(self, **kwargs):
        """
        Constructor for the main application window.

        :param kwargs: Additional arguments for the tk.Tk constructor.

        Main constructor actions:
        1. Sets the window title and size.
        2. Loads the application icon.
        3. Creates a sidebar for tab navigation.
        4. Configures the central canvas with a frame and a vertical scrollbar.
        5. Binds events for interface handling.
        6. Loads the initial content of the application.
        """
        super().__init__(**kwargs)

        self.withdraw()
        self.title(APP['title'])  # Window title
        self.geometry(APP['geometry'])  # Dimensions

        self.load_app_icon()  # Add icon

        # Left panel
        self.side_panel = tk.Frame(self, bg=SIDE_PANEL['bg_color'],
                                   width=SIDE_PANEL['width'])
        self.side_panel.pack(side=tk.LEFT, fill=tk.Y)

        # Create label for connection status
        self.connection_status_label = tk.Label(self.side_panel,
                                                text="Disconnected",
                                                bg=SIDE_PANEL['bg_color'],
                                                fg=SIDE_PANEL['connection_failed_color'],
                                                font=SIDE_PANEL['connection_status_font'])
        self.connection_status_label.pack(side=tk.BOTTOM, anchor="w", padx=5, pady=5)

        self.tabs = load_tabs()

        # Check the connection status upon startup
        self.check_connection()

        # Add buttons only if connected
        if self.is_connected:
            for tab in self.tabs:
                self.add_tab_button(tab)

        self.canvas = tk.Canvas(self, bg=INTERFACE['bg_color'], highlightthickness=0, bd=0)
        self.canvas_frame = tk.Frame(self.canvas, highlightthickness=0, bd=0)

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, expand=1, fill=tk.BOTH)

        self.window_area = self.canvas.create_window((0, 0), window=self.canvas_frame, anchor="nw")

        self.bind_events()

        self.load_content()  # Load welcome frame

        self.after(100, self.deiconify)

    def check_connection(self):
        """
        Checks the connection to the server upon startup and updates the label.

        :return: None
        """
        try:
            response = requests.get(f"{SERVER_URL}/check_server_connection", timeout=10, verify=VERIFY_ENABLED)
            if response.status_code == 200:
                self.update_connection_status(True)
            else:
                self.update_connection_status(False)
        except requests.RequestException:
            self.update_connection_status(False)

    def load_app_icon(self):
        """
        Load app icon.

        :return: None
        """
        try:
            self.iconbitmap(APP['icon_path'])
        except Exception as e:
            print(f"Icon load error: {e}")

    def update_connection_status(self, is_connected):
        """
        Updates the connection status label based on the connection state.

        :param is_connected: Boolean value indicating the connection status.

        :return: None
        """
        self.is_connected = is_connected
        if is_connected:
            self.connection_status_label.config(text="Connected",
                                                fg=SIDE_PANEL['connection_successful_color'],
                                                font=SIDE_PANEL['connection_status_font'])
        else:
            self.connection_status_label.config(text="Disconnected",
                                                fg=SIDE_PANEL['connection_failed_color'],
                                                font=SIDE_PANEL['connection_status_font'])

    def add_tab_button(self, tab):
        """
        Adds a button for a tab to the sidebar.

        This method creates a button representing the tab on the sidebar. The button contains an icon and the tab's name.
        When the button is clicked, the content associated with the tab is displayed. The icon and text are displayed in the button using
        the `compound` and `anchor` parameters to position the elements within the button.

        :param tab: A dictionary containing information about the tab.
            It should include the following keys:
            - "icon": The path to the icon image for the tab (string).
            - "name": The name of the tab, which will be displayed on the button (string).
            - "content": The content of the tab, which will be displayed when the button is clicked (usually a frame or other widget).

        :return: None
        """
        try:
            icon_photo = asyncio.run(load_icon_image(SERVER_URL, tab["icon"], VERIFY_ENABLED))

            button = tk.Button(
                self.side_panel,
                text=tab["name"],
                command=lambda: self.show_tab_content(tab["content"]),
                bg=INTERFACE['button_bg_color'],
                image=icon_photo,
                compound='left',
                padx=5,
                font=SIDE_PANEL['font'],
                anchor=tk.W
            )
            button.image = icon_photo
            button.pack(fill=tk.X, pady=10, padx=5)
            button.config(cursor="hand2")

        except requests.RequestException as e:
            print(f"Error icon GET '{tab['name']}': {e}")
        except Exception as e:
            print(f"Error icon upload '{tab['name']}': {e}")

    def bind_events(self):
        """
        Binds event handlers for the window and canvas.

        :return: None
        """
        # Window resize
        self.bind('<Configure>', self.on_frame_resized)

        # Updates the display area width when the canvas size changes
        self.canvas.bind('<Configure>', self.area_width)

        # Mousewheel
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

    def area_width(self, event):
        """
        Sets the display area width inside the canvas,
        automatically adjusting to window resizing.

        This method is called when a resize event occurs (e.g., when the window's width changes).
        It updates the width of a specified area (e.g., a rectangle or other object) on the canvas
        to match the new width of the window.

        :param event: The event object containing information about the new window size.
            It has a `width` attribute indicating the new canvas width.

        :return: None
        """
        canvas_width = event.width
        self.canvas.itemconfig(self.window_area, width=canvas_width)

    def on_mouse_wheel(self, event):
        """
        Handles mouse wheel scrolling for vertical scrolling of the canvas content.

        This method is called when the mouse wheel is scrolled and is used to scroll the content
        of the canvas up or down depending on the scroll direction.

        The mouse wheel scroll event provides a `delta` attribute indicating the scroll direction:
        - Positive values for scrolling up.
        - Negative values for scrolling down.

        :param event: The event object passed when the mouse wheel is scrolled.
            The `delta` attribute determines the amount of scrolling:
            - Positive values mean scrolling up.
            - Negative values mean scrolling down.

        :return: None
        """
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_frame_resized(self, event=None):
        """
        Handles the window resize event to update the scroll area
        and adjust the sidebar width based on the new window size.

        This method is called every time the window size changes and performs the following actions:
        1. Updates the canvas scroll area to match the new content size.
        2. Recalculates and adjusts the sidebar width relative to the window width (25% of the total width).
        3. Checks and adjusts the visibility of the vertical scrollbar if necessary.

        :param event: The event object passed when the window is resized. It is typically used to access
                      the new window dimensions. This parameter may be `None` if the method is called manually.
        :return: None
        """
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Left panel width
        new_width = int(self.winfo_width() * 0.25)
        self.side_panel.config(width=new_width)

        self.check_scrollbar()

    def load_content(self):
        """
        Load content

        :return: None
        """
        self.clear_canvas()
        welcome_label = tk.Label(self.canvas_frame, text=APP['welcome_text'], font=APP['welcome_text_font'],
                                 bg=INTERFACE['bg_color'])
        welcome_label.pack(pady=20, padx=20)
        self.check_scrollbar()

    def check_scrollbar(self):
        """
        Checks if the scrollbar is displayed and disables scrolling if the content height is less than the window height.

        :return: None
        """
        self.canvas.update_idletasks()

        # Get full height
        content_height = self.canvas.bbox("all")[3]  # y2 coordinate
        canvas_height = self.canvas.winfo_height()  # Canvas height

        if content_height < canvas_height:
            self.bind_all("<MouseWheel>", lambda e: "break")
        else:
            self.bind_all("<MouseWheel>", self.on_mouse_wheel)

    def clear_canvas(self):
        """
        Delete all widgets from canvas frame.

        :return: None
        """
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

    def show_tab_content(self, content):
        """
        Displays the content of the tab based on the provided content.
        This method performs the following actions:
        1. Clears the current content on the canvas.
        2. Loads and displays the corresponding frame based on the value of the `content` parameter.
        3. If the content does not match any known tabs, it displays text content on the canvas.

        :param content: The name of the tab or type of content to display.
                        It can be one of the following values:
                        "useful_links", "yearly_plans", "lists_for_life", "work".
        :return: None
        """
        self.clear_canvas()
        if content == "useful_links":
            useful_links_frame = UsefulLinks(self.canvas_frame, json_file=DATA_PATHS['useful_links'], main_window=self)
            useful_links_frame.pack(fill=tk.BOTH, expand=True)
        elif content == "yearly_plans":
            yearly_plans_frame = YearlyPlans(self.canvas_frame, main_window=self)
            yearly_plans_frame.pack(fill=tk.BOTH, expand=True)
        elif content == "lists_for_life":
            lists_for_life_frame = ListsForLife(self.canvas_frame, json_file=DATA_PATHS['lists_for_life'],
                                                main_window=self)
            lists_for_life_frame.pack(fill=tk.BOTH, expand=True)
        elif content == "work":
            work_frame = Work(self.canvas_frame, main_window=self)
            work_frame.pack(fill=tk.BOTH, expand=True)
        else:
            content_label = tk.Label(self.canvas_frame, text=content, bg=INTERFACE['bg_color'])
            content_label.pack(pady=20, padx=20)

        self.check_scrollbar()
        # Move canvas
        self.canvas.yview_moveto(0)

    def disable_buttons(self):
        """
        Disable all the buttons on the sidebar.
        """
        for widget in self.side_panel.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(state=tk.DISABLED)

    def enable_buttons(self):
        """
        Enable all the buttons on the sidebar.
        """
        for widget in self.side_panel.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(state=tk.NORMAL)


if __name__ == '__main__':
    f = MainWindow()
    f.mainloop()
