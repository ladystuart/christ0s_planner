import asyncio
import tkinter as tk
from tkinter import Frame, Label
from PIL import Image, ImageTk
import webbrowser
import requests
from io import BytesIO
from config.settings import INTERFACE, USEFUL_LINKS, SERVER_URL, VERIFY_ENABLED


async def add_icon_image(path):
    """
    Asynchronously fetches an icon or image from the server and returns it as a PIL Image object.

    This function sends a GET request to the server to retrieve an image, using the `ICONS_PATHS['habit_tracker']` path.
    If the request is successful, the image content is loaded into a PIL Image object and returned.

    Returns:
        PIL.Image: The image object representing the icon fetched from the server.

    Raises:
        requests.exceptions.RequestException: If the request to the server fails (e.g., network error or invalid URL).
    """
    response = requests.get(f"{SERVER_URL}/assets/{path}", verify=VERIFY_ENABLED)
    response.raise_for_status()

    return Image.open(BytesIO(response.content))


async def load_icon_image(url, icon_path, verify, size=(20, 20)):
    """
    This function loads an icon image from a given URL, resizes it to the specified size, and returns a Tkinter-compatible image.

    Args:
        url (str): The base URL where the icon is hosted.
        icon_path (str): The relative path to the icon file on the server.
        verify (bool): A flag indicating whether SSL certificates should be verified.
        size (tuple): A tuple indicating the desired size of the image (width, height). Defaults to (20, 20).

    Returns:
        ImageTk.PhotoImage: A Tkinter-compatible image object that can be used in GUI components like labels or buttons.
    """
    response = requests.get(f"{url}/assets/{icon_path}", verify=verify)
    response.raise_for_status()

    icon_image_original = Image.open(BytesIO(response.content))

    icon_image = icon_image_original.resize(size, Image.Resampling.LANCZOS)

    return ImageTk.PhotoImage(icon_image)


def add_source_label(parent, link, title, bg_color, font):
    """
    Adds a source label with an optional icon to a parent frame. This function creates a frame containing
    a small icon (if the image is accessible) and a title label. The icon is resized to fit the layout,
    and both the icon and title are displayed next to each other. If the icon cannot be loaded, only the
    title label is shown.

    :param parent: The parent widget (typically a frame or window) to which the label and icon will be added.
    :param link: The file path or URL to the image/icon that will be displayed next to the title.
    :param title: The text to be displayed in the label next to the icon.
    :param bg_color: The background color for the frame and labels.
    :param font: The font to be used for the title label.
    :return: None
    """
    header_frame = tk.Frame(parent, bg=bg_color)
    header_frame.pack(anchor="nw", pady=(5, 2), padx=10)

    try:
        icon_data = asyncio.run(add_icon_image(link))

        with icon_data as img:
            icon_image_original = img.copy()
            icon_image_resized = icon_image_original.resize(
                (INTERFACE['source_icon_dimensions'], INTERFACE['source_icon_dimensions']),
                Image.Resampling.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_image_resized)

        icon_label = tk.Label(header_frame, image=icon_photo, bg=bg_color)
        icon_label.image = icon_photo
        icon_label.pack(side="left")
    except Exception as e:
        print(f"Error icon load: {e}")

    source_label = tk.Label(header_frame, text=title, font=font, bg=bg_color)
    source_label.pack(side="left", padx=(5, 0))


def add_banner(parent, banner_path, bg_color, fixed_height=200, padding=(2, 10)):
    """
    Adds a banner to the parent widget. The banner is an image that is loaded from the
    provided `banner_path`. The image is resized to a fixed height while maintaining its aspect ratio.
    The banner is then displayed in the parent widget with the specified background color
    and padding.

    :param parent: The parent widget (typically a frame or window) where the banner will be added.
    :param banner_path: The file path or URL to the banner image that will be displayed.
    :param bg_color: The background color for the banner.
    :param fixed_height: The fixed height to which the banner image will be resized (default is 200).
    :param padding: A tuple (top, bottom) that specifies the padding around the banner (default is (2, 10)).
    :return: A tuple containing the banner label widget and the original image (used for resizing).
             If there is an error loading the image, returns (None, None).
    """
    try:
        # Add image
        image_data = asyncio.run(add_icon_image(banner_path))

        # Open image
        with image_data as img:
            banner_image_original = img.copy()
            banner_image_resized = banner_image_original.resize(
                (int(banner_image_original.width * (fixed_height / banner_image_original.height)), fixed_height),
                Image.Resampling.LANCZOS
            )
            banner_photo = ImageTk.PhotoImage(banner_image_resized)

        banner_label = tk.Label(parent, bg=bg_color, image=banner_photo)
        banner_label.image = banner_photo
        banner_label.pack(pady=padding, fill=tk.X)

        return banner_label, banner_image_original
    except Exception as e:
        print(f"Error banner load: {e}")
        return None, None


def resize_banner(parent, banner_label, banner_image_original, fixed_height=200):
    """
    Resizes the banner image displayed in the given `banner_label` to fit the width of the parent widget
    while maintaining a fixed height. The banner is resized dynamically whenever the parent widget's width
    changes. This ensures that the banner always fits the available space and maintains its aspect ratio.

    :param parent: The parent widget (usually a frame or window) whose width will determine the resized width of the banner.
    :param banner_label: The label widget that displays the banner image.
    :param banner_image_original: The original image object that will be resized.
    :param fixed_height: The fixed height to which the banner will be resized (default is 200).
    :return: None
    """
    try:
        width = parent.winfo_width()

        if width <= 0:
            return

        new_width = width
        new_height = fixed_height

        resized_image = banner_image_original.resize((new_width, new_height), Image.Resampling.LANCZOS)
        banner_photo = ImageTk.PhotoImage(resized_image)

        banner_label.configure(image=banner_photo)
        banner_label.image = banner_photo
    except Exception as e:
        print(f"Error banner load: {e}")


def add_icon_and_label(parent, text, icon_path, bg_color):
    """
    Adds an icon and a text label to the parent widget in a horizontally arranged layout.
    The icon is loaded from the given path, resized to a specified dimension, and displayed
    alongside the provided text.

    :param parent: The parent widget (typically a frame or window) where the icon and text will be added.
    :param text: The text to be displayed next to the icon.
    :param icon_path: The file path to the image that will be used as the icon.
    :param bg_color: The background color for both the label and icon.
    :return: None
    """
    label_frame = Frame(parent, bg=bg_color)
    label_frame.pack(anchor="w", pady=2, padx=10, fill="x")

    try:
        icon_data = asyncio.run(add_icon_image(icon_path))

        with icon_data as img:
            icon_image_original = img.copy()
            icon_image_resized = icon_image_original.resize(
                (INTERFACE['icon_dimensions'], INTERFACE['icon_dimensions']),
                Image.Resampling.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_image_resized)

        icon_label = Label(label_frame, image=icon_photo, bg=bg_color)
        icon_label.image = icon_photo
        icon_label.pack(side="left", padx=5)

        text_label = Label(label_frame, text=text, font=INTERFACE['page_title_font'], bg=bg_color, anchor="w")
        text_label.pack(side="left", padx=5)

    except Exception as e:
        print(f"Error icon load: {e}")


def add_separator(parent, color):
    """
    Adds a horizontal separator (line) to the given parent widget, useful for visually
    separating sections within the UI. The separator is a thin frame with a specified background color.

    :param parent: The parent widget (typically a frame or window) to which the separator will be added.
    :param color: The color of the separator (background color of the frame).
    :return: None
    """
    separator = tk.Frame(parent, bg=color, height=1)
    separator.pack(fill='x', padx=5, pady=5)


def open_link(url):
    """
    Opens the specified URL in the default web browser.

    This function attempts to open the provided URL using the system's default web browser.
    If the operation is successful, the URL will be loaded in the browser. If there is an error
    (e.g., invalid URL or web browser issue), an error message will be printed.

    :param url: The URL to open in the default web browser.
    :return: None
    """
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Error opening link {url}: {e}")


def title_label(parent, text, icon, icon_width, icon_height):
    """
    Creates a header section with a title and icon on a specified parent widget. The header contains
    an icon at the start and end positions and a label with the provided text in the middle.

    :param parent: The parent widget (e.g., a frame or window) where the header will be placed.
    :param text: The text to be displayed in the center of the header label.
    :param icon: The icon image (usually a file path) to be displayed at the start and end of the header.
    :param icon_width: The width to which the icon should be resized.
    :param icon_height: The height to which the icon should be resized.
    :return: None
    """
    header_frame = tk.Frame(parent, bg=INTERFACE['bg_color'])
    header_frame.pack(pady=5)

    if not hasattr(parent, 'header_frames'):
        parent.header_frames = []

    parent.header_frames.append(header_frame)

    add_title_icon(header_frame, icon_width, icon_height, row=0, column=0, icon=icon)

    add_header_label(header_frame, row=0, column=1, text=text)

    add_title_icon(header_frame, icon_width, icon_height, row=0, column=2, icon=icon)


async def load_icon_or_image_with_custom_size(icon_path, icon_width, icon_height):
    """
    Asynchronously fetches an image from the server, resizes it to the specified dimensions,
    and returns it as a Tkinter-compatible PhotoImage.

    This function performs the following steps:
    1. Sends a GET request to the server to retrieve the image located at the given `icon_path`.
    2. Converts the response content into a PIL Image.
    3. Resizes the image to the specified `icon_width` and `icon_height` using high-quality resampling.
    4. Converts the resized image into an `ImageTk.PhotoImage` object for use in Tkinter widgets.

    Args:
        icon_path (str): Relative path to the image on the server.
        icon_width (int): Desired width of the image in pixels.
        icon_height (int): Desired height of the image in pixels.

    Returns:
        ImageTk.PhotoImage: A Tkinter-compatible image object ready to be used in labels, buttons, etc.

    Raises:
        requests.exceptions.RequestException: If the image cannot be fetched from the server.
        PIL.UnidentifiedImageError: If the image content is invalid or cannot be opened.
    """
    response = requests.get(f"{SERVER_URL}/assets/{icon_path}", verify=VERIFY_ENABLED)
    response.raise_for_status()

    icon_image_original = Image.open(BytesIO(response.content))

    icon_image = icon_image_original.resize((icon_width, icon_height), Image.Resampling.LANCZOS)

    return ImageTk.PhotoImage(icon_image)


def add_title_icon(header_frame, icon_width, icon_height, row, column, icon):
    """
    Adds an icon to the given header frame at a specified position, resizing the icon
    to the given dimensions before adding it.

    This function attempts to open an image file specified by `icon`, resize it to the
    provided dimensions (`icon_width`, `icon_height`), and add it to a header frame at
    the specified grid position (`row`, `column`).

    :param header_frame: The Tkinter frame where the icon should be placed.
    :param icon_width: The width to which the icon image should be resized.
    :param icon_height: The height to which the icon image should be resized.
    :param row: The row position in the header frame's grid where the icon will be placed.
    :param column: The column position in the header frame's grid where the icon will be placed.
    :param icon: The file path of the image icon to be loaded and displayed.
    :return: None
    """
    try:
        icon_photo = asyncio.run(load_icon_or_image_with_custom_size(icon, icon_width, icon_height))

        icon_label = tk.Label(header_frame, image=icon_photo, bg=INTERFACE['bg_color'])
        icon_label.image = icon_photo

        icon_label.grid(row=row, column=column, padx=5)

    except requests.RequestException as e:
        print(f"Error icon load {icon}: {e}")
    except Exception as e:
        print(f"Error icon parse {icon}: {e}")


def add_header_label(header_frame, row, column, text):
    """
    Adds a label with the specified text to a given header frame at a specific grid position.

    This function creates a Tkinter label with the provided text and places it in the
    specified row and column of the grid within the given `header_frame`. The label's
    font and background color are defined by the `INTERFACE['headers_font']` and
    `INTERFACE['bg_color']` settings, respectively.

    :param header_frame: The Tkinter frame where the label should be placed.
    :param row: The row position in the header frame's grid where the label will be placed.
    :param column: The column position in the header frame's grid where the label will be placed.
    :param text: The text to be displayed on the label.
    :return: None
    """
    header_label = tk.Label(header_frame, text=text, font=INTERFACE['headers_font'], bg=INTERFACE['bg_color'])
    header_label.grid(row=row, column=column, padx=5)


def add_image_to_grid(parent, image_path, row, column, height, width, rowspan, columnspan=None):
    """
    Adds an image to a specified grid cell within a parent widget in Tkinter.

    This function loads an image from the specified file path, resizes it to the specified
    height and width, and then places it into the specified grid position in the parent widget.
    The image is displayed using a Tkinter label, and the function uses grid placement with optional
    row and column spans.

    :param parent: The parent widget where the image will be placed (e.g., a Tkinter Frame or Window).
    :param image_path: The file path to the image that will be loaded and displayed.
    :param row: The row position in the grid where the image will be placed.
    :param column: The column position in the grid where the image will be placed.
    :param height: The desired height of the image after resizing.
    :param width: The desired width of the image after resizing.
    :param rowspan: The number of rows the image should span (useful for large images that need to take up multiple rows).
    :param columnspan: The number of columns the image should span (optional, defaults to 1 if not provided).
    :return: None
    """
    try:
        photo = asyncio.run(load_icon_or_image_with_custom_size(image_path, width, height))

        image_label = tk.Label(parent, image=photo)
        image_label.image = photo
        image_label.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, padx=10, pady=10)

    except requests.RequestException as e:
        print(f"Error loading image from {image_path}: {e}")
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")


def add_description_label_bold(frame, text, row, column):
    """
    Adds a label with bold text to a specified grid cell within a frame.

    This function creates a label widget containing the provided text, with a bold font style,
    and places it into a specified grid position within the provided frame.

    :param frame: The parent widget (typically a Tkinter Frame) where the label will be placed.
    :param text: The text content to be displayed in the label.
    :param row: The row position in the grid where the label will be placed.
    :param column: The column position in the grid where the label will be placed.
    :return: None
    """
    label_search_text = tk.Label(frame, text=text, font=USEFUL_LINKS['description_font_bold'],
                                 bg=INTERFACE['bg_color'])
    label_search_text.grid(row=row, column=column, pady=5)


def add_description_label(frame, text, row, column, rowspan):
    """
    Adds a label with regular text to a specified grid cell within a frame.

    This function creates a label widget containing the provided text and places it in a specified
    grid position within the provided frame. The label will span multiple rows if needed, as specified
    by the `rowspan` parameter.

    :param frame: The parent widget (typically a Tkinter Frame) where the label will be placed.
    :param text: The text content to be displayed in the label.
    :param row: The row position in the grid where the label will be placed.
    :param column: The column position in the grid where the label will be placed.
    :param rowspan: The number of rows the label should span in the grid layout.
    :return: None
    """
    label_search_text = tk.Label(frame, text=text, font=USEFUL_LINKS['description_label'],
                                 bg=INTERFACE['bg_color'])
    label_search_text.grid(row=row, column=column, rowspan=rowspan, pady=5)


def add_link_button(parent_frame, display_text, link, row, column):
    """
    Adds a clickable button that acts as a hyperlink within the specified parent frame.

    This function creates a button with the provided display text that, when clicked, opens a specified URL.
    The button is styled to look like a link (using a specific font and color), and it is placed within the
    specified grid position.

    :param parent_frame: The parent widget (typically a Tkinter Frame) where the button will be placed.
    :param display_text: The text to display on the button. This text will appear as a hyperlink.
    :param link: The URL to open when the button is clicked.
    :param row: The row position in the grid where the button will be placed.
    :param column: The column position in the grid where the button will be placed.
    :return: None
    """
    button = tk.Button(parent_frame, text=display_text, font=USEFUL_LINKS['link_font'], fg=USEFUL_LINKS['link_color'],
                       bg=INTERFACE['bg_color'], borderwidth=1, anchor='w', wraplength=200)
    button.grid(row=row, column=column, padx=5)
    button.config(cursor="hand2")

    button.bind("<Button-1>", lambda e: open_link(link))


def add_title_description_label(parent, text):
    """
    Adds a label displaying a description text in a frame, with some styling and padding.

    This function creates a `Tkinter` label with the provided text and places it within a frame that
    is styled with a specific background color. The label will display the provided description text
    and will have padding to space it from other widgets.

    :param parent: The parent widget (typically a Tkinter Frame) where the label will be placed.
    :param text: The description text to display on the label.
    :return: None
    """
    header_description_frame = tk.Frame(parent, bg=INTERFACE['bg_color'])
    header_description_frame.pack(pady=5)
    label_descr_text = tk.Label(header_description_frame, text=text, font=USEFUL_LINKS['description_label'],
                                bg=INTERFACE['bg_color'])
    label_descr_text.grid(row=0, column=0, pady=5)


def clear_canvas(parent):
    """
    Clears all the widgets (children) from the given parent widget.

    This function iterates through all the child widgets of the specified parent
    widget and destroys them, effectively clearing the parent widget's content.

    :param parent: The parent widget whose child widgets are to be destroyed.
    :type parent: tkinter.Widget
    :return: None
    """
    for widget in parent.winfo_children():
        widget.destroy()


def reset_canvas_view(main_window):
    """
    Resets the view of the canvas within the given main window to the top.

    This function checks if the `main_window` contains a `canvas` attribute and
    if the canvas exists. If so, it resets the vertical scroll position of the
    canvas to the top by setting the y-axis view to 0. If the canvas does not
    exist, it prints an error message.

    :param main_window: The main window containing the canvas to be reset.
    :type main_window: tkinter.Tk or tkinter.Toplevel
    :return: None
    """
    if hasattr(main_window, 'canvas') and main_window.canvas:
        main_window.canvas.yview_moveto(0)
    else:
        print("Canvas not found in main_window.")


def add_source_label_second_level(parent, icon_path_1, clickable_text, click_command, icon_path_2, text):
    """
    Adds a header-like frame to the given parent widget, which contains:
    - an icon (from the first icon path)
    - a clickable text element
    - another icon (from the second icon path)
    - a regular text label

    The clickable text element is associated with a command that gets triggered
    when the text is clicked.

    :param parent: The parent widget (usually a frame or window) where the header will be added.
    :type parent: tkinter.Widget
    :param icon_path_1: File path for the first icon to be displayed.
    :type icon_path_1: str
    :param clickable_text: The text that will be clickable.
    :type clickable_text: str
    :param click_command: The function to be executed when the clickable text is clicked.
    :type click_command: callable
    :param icon_path_2: File path for the second icon to be displayed.
    :type icon_path_2: str
    :param text: The regular text label to be displayed next to the second icon.
    :type text: str
    :return: clickable_label
    """
    header_frame = tk.Frame(parent, bg=INTERFACE['bg_color'])
    header_frame.pack(anchor="nw", pady=(5, 2), padx=10)

    create_icon_label(header_frame, icon_path_1)

    clickable_label = create_clickable_text(header_frame, clickable_text, command=click_command)

    create_icon_label(header_frame, icon_path_2)

    create_text_label(header_frame, text)

    return clickable_label


def add_source_label_third_level(parent, icon_path_1, year_name, clickable_text, click_command_1, icon_path_2,
                                 icon_path_3, text, click_command_2):
    """
    Adds a header-like frame to the parent widget, consisting of:
    - an icon (from the first icon path)
    - a clickable text element (with an associated command)
    - another icon (from the second icon path)
    - a clickable year label (with its own associated command)
    - a third icon (from the third icon path)
    - a regular text label

    This function is useful for creating a more complex hierarchical structure where
    each clickable element is associated with specific actions.

    :param parent: The parent widget (usually a frame or window) where the header will be added.
    :type parent: tkinter.Widget
    :param icon_path_1: The file path for the first icon to be displayed.
    :type icon_path_1: str
    :param year_name: The text (e.g., a year) that will be clickable.
    :type year_name: str
    :param clickable_text: The text that will be clickable.
    :type clickable_text: str
    :param click_command_1: The function to be executed when the first clickable text is clicked.
    :type click_command_1: callable
    :param icon_path_2: The file path for the second icon to be displayed.
    :type icon_path_2: str
    :param icon_path_3: The file path for the third icon to be displayed.
    :type icon_path_3: str
    :param text: The regular text label to be displayed next to the third icon.
    :type text: str
    :param click_command_2: The function to be executed when the second clickable text (year_name) is clicked.
    :type click_command_2: callable
    :return: first_clickable_label, second_clickable_label
    """
    header_frame = tk.Frame(parent, bg=INTERFACE['bg_color'])
    header_frame.pack(anchor="nw", pady=(5, 2), padx=10)

    create_icon_label(header_frame, icon_path_1)

    first_clickable_label = create_clickable_text(header_frame, clickable_text, command=click_command_1)

    create_icon_label(header_frame, icon_path_2)

    second_clickable_label = create_clickable_text(header_frame, year_name, command=click_command_2)

    create_icon_label(header_frame, icon_path_3)

    create_text_label(header_frame, text)

    return first_clickable_label, second_clickable_label


def create_icon_label(frame, icon_path, icon_size=(INTERFACE['source_icon_dimensions'],
                                                   INTERFACE['source_icon_dimensions']),
                      bg_color=INTERFACE['bg_color']):
    """
    Creates an icon label inside a given frame by loading an image from the provided path or URL,
    resizing it to the specified size, and setting a background color. The icon is displayed
    as a label widget in the specified frame.

    :param frame: The parent widget (usually a frame or window) where the icon label will be placed.
    :param icon_path: The file path or URL to the icon image that will be displayed.
    :param icon_size: The size (width, height) to which the icon will be resized. Defaults to
                      `INTERFACE['source_icon_dimensions']`.
    :param bg_color: The background color to be used for the label. Defaults to `INTERFACE['bg_color']`.
    :return: None
    """
    try:
        icon_data = asyncio.run(load_icon_image(SERVER_URL, icon_path, VERIFY_ENABLED))

        icon_label = tk.Label(frame, image=icon_data, bg=bg_color)
        icon_label.image = icon_data
        icon_label.pack(side="left")
    except Exception as e:
        print(f"Icon load error from {icon_path}: {e}")


def create_text_label(frame, text, font=INTERFACE['text_label_font'], bg_color=INTERFACE['bg_color']):
    """
    Creates a text label inside a given frame with the specified text, font, and background color.

    This function creates a `tkinter.Label` widget that displays the provided text with a specified
    font and background color, and then packs the label into the given frame.

    :param frame: The parent widget (usually a frame or window) where the text label will be placed.
    :type frame: tkinter.Widget
    :param text: The text to be displayed on the label.
    :type text: str
    :param font: The font style and size for the label's text. Defaults to `INTERFACE['text_label_font']`.
    :type font: tuple(str, int)
    :param bg_color: The background color for the label. Defaults to `INTERFACE['bg_color']`.
    :type bg_color: str
    :return: None
    """
    source_label = tk.Label(frame, text=text, font=font, bg=bg_color)
    source_label.pack(side="left", padx=(5, 0))


def create_clickable_text(frame, text, font=INTERFACE['text_label_font'],
                          bg_color=INTERFACE['bg_color'], command=None):
    """
    Creates a clickable text label inside the given frame. The label displays the specified text,
    and if a command is provided, the text becomes clickable and triggers the command when clicked.

    The clickable label is styled with a hand cursor to indicate interactivity. When clicked,
    the associated command is executed.

    :param frame: The parent widget (usually a frame or window) where the clickable text label will be placed.
    :type frame: tkinter.Widget
    :param text: The text to be displayed on the clickable label.
    :type text: str
    :param font: The font style and size for the text. Defaults to `INTERFACE['text_label_font']`.
    :type font: tuple(str, int)
    :param bg_color: The background color for the label. Defaults to `INTERFACE['bg_color']`.
    :type bg_color: str
    :param command: The function to be executed when the label is clicked. If not provided, the label is non-clickable.
    :type command: callable, optional
    :return: clickable_label
    """
    clickable_label = tk.Label(frame, text=text, font=font, fg="black", cursor="hand2", bg=bg_color)
    clickable_label.pack(side="left", padx=(5, 0))

    if command:
        clickable_label.bind("<Button-1>", lambda e: command())

    return clickable_label


def center_window_on_parent(parent_window, new_window, width, height):
    """
    Centers a new window on top of the parent window.

    This function calculates the position of the new window based on the size of the
    parent window's canvas, and positions the new window at the center relative to the parent.

    :param parent_window: The parent window or widget containing the canvas. The new window will be centered
                          relative to this parent.
    :type parent_window: tkinter.Widget
    :param new_window: The window to be centered on the parent window.
    :type new_window: tkinter.Toplevel
    :param width: The width of the new window.
    :type width: int
    :param height: The height of the new window.
    :type height: int
    :return: None
    """
    new_window.update_idletasks()

    canvas_width = parent_window.canvas.winfo_width()
    canvas_height = parent_window.canvas.winfo_height()
    canvas_x = parent_window.canvas.winfo_rootx()
    canvas_y = parent_window.canvas.winfo_rooty()

    center_x = canvas_x + (canvas_width - width) // 2
    center_y = canvas_y + (canvas_height - height) // 2

    new_window.geometry(f"{width}x{height}+{center_x}+{center_y}")
