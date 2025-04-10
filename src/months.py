from config.imports import *
from config.settings import MONTHS
from config.utils import add_source_label_third_level as add_source_label_months, add_icon_image
from src.monthly_plans import MonthlyPlans
from config.tooltip import ToolTip


async def get_months_states(year):
    """
    Fetches the month states for a given year from the server.

    Args:
     year (int): The year for which the month states are to be fetched.

    Returns:
     list: A list of dictionaries containing the month name and its associated icon path.
           If an error occurs during the request, an empty list is returned.

    Raises:
     aiohttp.ClientError: If there is an issue with the HTTP request.
     aiohttp.HTTPStatusError: If the response from the server indicates an error (e.g., 404, 500).
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SERVER_URL}/get_months_states",
                                   params={"year": year}, ssl=SSL_ENABLED) as response:
                response.raise_for_status()
                months_data = await response.json()
                return months_data
    except aiohttp.ClientError as e:
        print(f"An error occurred while requesting months data: {e}")
        return []
    except aiohttp.HTTPStatusError as e:
        print(f"Error response from server: {e}")
        return []


async def load_icon_image(icon_path):
    """
    Asynchronously loads an icon image from the server and returns a resized PhotoImage object.

    Args:
        icon_path (str): The path to the icon image on the server (e.g., "images/icon.png").

    Returns:
        PhotoImage: A resized PhotoImage object representing the icon image, or None if there was an error.

    Raises:
        Exception: If there is any issue with the HTTP request or image loading.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SERVER_URL}/assets/{icon_path}", ssl=SSL_ENABLED) as response:
                if response.status == 200:
                    image_bytes = await response.read()
                    photo = PhotoImage(data=image_bytes)
                    photo = photo.subsample(2, 2)  # Resizes the image by a factor of 2
                    return photo
                else:
                    print(f"Failed to fetch {icon_path}: {response.status}")
                    return None
    except Exception as e:
        print(f"Error fetching {icon_path}: {e}")
        return None


async def save_month_states_to_server(month, year, icon_path):
    """
    Asynchronously sends the updated month icon status to the server.

    Args:
        month (str): The name of the month (e.g., "January", "February").
        year (int): The year associated with the month (e.g., 2023).
        icon_path (str): The path to the updated icon image for the month (e.g., "images/icon.png").

    Returns:
        None: This function does not return any value. It only sends data to the server and handles potential errors.

    Raises:
        aiohttp.ClientError: If there is an issue with the HTTP request.
        aiohttp.HTTPStatusError: If the server returns a non-2xx status code.
    """
    data = {
        "month_name": month,
        "year": int(year),
        "icon_path": icon_path
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{SERVER_URL}/update_months_icon_status",
                                    json=data, ssl=SSL_ENABLED) as response:
                if response.status != 200:
                    print(f"Failed to update {month} icon. Status: {response.status}")
    except aiohttp.ClientError as e:
        print(f"An error occurred while sending data: {e}")
    except aiohttp.HTTPStatusError as e:
        print(f"Error response from server: {e}")


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
        main_window (MainWindow): The main window instance for global management (e.g., scrollbars)
        year (int): The year associated with the displayed data.
    """
    def __init__(self, parent, main_window, year):
        """
        Initializes the Months page, sets up the GUI elements, and loads data from server.

        :param parent: The parent widget for this frame.
        :param main_window: The main window instance for global settings and features.
        :param year: The year to display tasks for.
        """
        super().__init__(parent)
        self.month = None
        self.configure(bg=INTERFACE['bg_color'])
        self.main_window = main_window
        self.year = year
        self.parent = parent
        self.main_window.disable_buttons()
        self.main_window.check_scrollbar()

        self.first_clickable_label, self.second_clickable_label = (add_source_label_months
                                                                   (self,
                                                                    icon_path_1=ICONS_PATHS['yearly_plans'],
                                                                    clickable_text="Yearly plans /",
                                                                    click_command_1=self.navigate_to_yearly_plans,
                                                                    icon_path_2=ICONS_PATHS['year'],
                                                                    year_name=f"{self.year} /",
                                                                    icon_path_3=ICONS_PATHS['months'],
                                                                    text=PAGES_NAMES['months'],
                                                                    click_command_2=lambda:
                                                                    self.navigate_to_year(self.year)))

        self.first_clickable_label["state"] = "disabled"
        self.second_clickable_label["state"] = "disabled"

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

        self.icon_image_original = asyncio.run(add_icon_image(ICONS_PATHS['months']))

        add_icon_and_label(self, text=PAGES_NAMES['months'],
                           icon_path=ICONS_PATHS['months'],
                           bg_color=INTERFACE['bg_color'])
        add_separator(parent=self, color=INTERFACE['separator'])

        self.add_quote_and_image()

        self.main_window.enable_buttons()
        self.first_clickable_label["state"] = "normal"
        self.second_clickable_label["state"] = "normal"

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

        calendar_frame = MonthlyPlans(self.parent, main_window=self.main_window, year=self.year, month=self.month)
        calendar_frame.pack(fill=tk.BOTH, expand=True)

        if hasattr(self.main_window, 'canvas') and self.main_window.canvas:
            self.main_window.canvas.yview_moveto(0)
        else:
            print("Canvas not found in main_window.")

    def add_quote_and_image(self):
        """
        This method adds month buttons with status icons and displays a quote with an image.

        The method loads month states from the server, creates buttons for each month with a status icon,
        and updates the icons when right-clicked. It also displays a quote and an image on the right side.

        :return: None
        """
        month_states = asyncio.run(get_months_states(int(self.year)))

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

            for i, m in enumerate(month_states):
                if m["month_name"] == month:
                    month_states[i]["icon_path"] = next_icon_path
                    break

            asyncio.run(save_month_states_to_server(month, self.year, next_icon_path))

        icons = {path: asyncio.run(load_icon_image(path)) for path in icon_paths}

        MONTH_ORDER = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

        month_states_sorted = sorted(month_states, key=lambda x: MONTH_ORDER.index(x['month_name']))

        for data in month_states_sorted:
            month = data['month_name']
            icon_path = data['icon_path']
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
        year_frame = Year(self.parent, main_window=self.main_window, year=year)
        year_frame.pack(fill=tk.BOTH, expand=True)

        reset_canvas_view(self.main_window)
