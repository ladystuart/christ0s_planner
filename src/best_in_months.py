from config.imports import *
from config.settings import BEST_IN_MONTHS
from config.utils import add_source_label_third_level as add_source_label_best_in_months, add_icon_image


async def upload_image_to_server(image_path, year):
    """
    Asynchronously uploads an image file to the server.

    This function reads the image from the specified `image_path`, prepares it for upload,
    and sends it to the server using an HTTP POST request. The image is associated with the specified `year`.

    Args:
        image_path (str): The local path to the image file to be uploaded.
        year (int): The year to associate with the uploaded image.

    Returns:
        None: The function does not return any value, but prints the status of the upload to the console.

    Raises:
        aiohttp.ClientError: If there is an error while making the asynchronous HTTP request.
    """
    with open(image_path, "rb") as f:
        image_data = f.read()

    form_data = aiohttp.FormData()
    form_data.add_field('file', image_data, filename=os.path.basename(image_path), content_type='image/jpeg')

    # Make the asynchronous request with aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{SERVER_URL}/upload_best_in_month_image/{year}",
                                data=form_data,
                                ssl=SSL_ENABLED) as response:
            if response.status != 200:
                print(f"Failed to upload image: {response.status}")


async def add_link_to_server(data):
    """
    Asynchronously sends data to the server to add a new link or entry.

    This function sends a JSON payload (`data`) to the server, using a POST request, to
    add information such as image paths or metadata associated with "best in months."

    Args:
        data (dict): A dictionary containing the data to be sent to the server. This could include
                     metadata like image paths, months, and associated information.

    Returns:
        None: The function does not return any value, but it prints an error message if the
              server responds with a status code other than 200.

    Raises:
        aiohttp.ClientError: If there is an error while making the asynchronous HTTP request.
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{SERVER_URL}/add_best_in_months_data",
                                json=data, ssl=SSL_ENABLED) as response:
            if response.status != 200:
                print(f"Failed to upload data. Status code: {response.status}")


async def get_tasks_from_server(year):
    """
    Asynchronously fetches tasks data from the server for the specified year.

    This function sends a GET request to the server with the provided `year` as a parameter,
    and retrieves the associated tasks data. If the request is successful, it returns the
    task data as a dictionary. In case of any errors (e.g., network issues, server errors),
    it handles the exceptions and returns an empty list.

    Args:
        year (int): The year for which tasks data needs to be retrieved.

    Returns:
        list: A list containing the tasks data for the given year. If an error occurs, an empty list is returned.

    Raises:
        aiohttp.ClientError: If there is a problem making the asynchronous HTTP request.
    """
    try:
        data = {"year": int(year)}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SERVER_URL}/get_best_in_months_data",
                                   json=data,
                                   ssl=SSL_ENABLED) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    print(f"Error: {response.status}")
                    return []
    except Exception as e:
        print(f"Server connection error: {e}")
        return []


async def remove_image_from_server(image_path, year):
    """
    Asynchronously removes an image from the server based on its file path and the specified year.

    This function sends a POST request to the server to delete the image with the specified `image_path`
    and `year`. If the request is successful, it will remove the image from the server. If an error occurs
    (e.g., network issues or server-side errors), it prints the error message.

    Args:
        image_path (str): The path of the image to be deleted. The function extracts the file name from this path.
        year (int): The year associated with the image being removed.

    Returns:
        None: The function does not return any value. If successful, the image is deleted from the server.
              If an error occurs, an error message is printed.

    Raises:
        requests.exceptions.RequestException: If there is an issue with making the HTTP request to the server.
    """
    try:
        file_name = image_path.split("/")[-1]

        response = requests.post(f"{SERVER_URL}/delete_best_in_month_image/{int(year)}",
                                 json={"file_name": file_name}, verify=VERIFY_ENABLED)

        if response.status_code != 200:
            print(f"Image delete error: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Server connection error: {e}")


async def remove_task_from_server(year, month):
    """
    Asynchronously removes a task from the server based on the specified year and month.

    This function sends a POST request to the server to delete the task associated with the specified `year`
    and `month`. If the request is successful, the task is deleted from the server. If an error occurs
    (e.g., network issues or server-side errors), an error message is printed.

    Args:
        year (int): The year of the task to be deleted.
        month (int): The month of the task to be deleted.

    Returns:
        None: The function does not return any value. If successful, the task is deleted from the server.
              If an error occurs, an error message is printed.

    Raises:
        requests.exceptions.RequestException: If there is an issue with making the HTTP request to the server.
    """
    try:
        response = requests.post(
            f"{SERVER_URL}/delete_best_in_months_task",
            json={"year": year, "month": month},
            verify=VERIFY_ENABLED
        )

        if response.status_code != 200:
            print(f"Error deleting task: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Server connection error: {e}")


async def fetch_image_from_server(image_path):
    """
    Asynchronously fetches an image from the server.

    This function sends a GET request to the server to fetch the image located at the specified `image_path`.
    If the request is successful (status code 200), the image data is returned as a PIL Image object.
    If the request fails (e.g., the image does not exist), the function returns `None`.

    Args:
        image_path (str): The path of the image on the server to be fetched.

    Returns:
        PIL.Image.Image or None: The image as a PIL Image object if the request is successful,
                                  or `None` if the image cannot be fetched (e.g., if the server returns an error).
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{SERVER_URL}/assets/{image_path}", ssl=VERIFY_ENABLED) as response:
            if response.status == 200:
                image_data = await response.read()
                return Image.open(BytesIO(image_data))
            else:
                return None


class BestInMonths(tk.Frame):
    """
    A Tkinter frame for displaying and interacting with monthly data of a specific year.

    This class is part of a larger application focused on tracking tasks, achievements, or milestones throughout the year.
    It provides an interactive interface for displaying "best" or notable entries for each month, allowing users to navigate through months, view detailed data, and edit or update entries.

    Key Features:
    - **Navigation:** Allows navigation between different pages (e.g., "Yearly Plans" or individual months) through clickable breadcrumbs at the top.
    - **Monthly Data Display:** Displays data for each month, such as notable tasks or achievements, with text and images representing the "best" entry for each month.
    - **Dynamic Month Setup:** Loads and displays the months of the selected year, dynamically fetching data from server.
    - **Interactive Entries:** Allows users to click on specific months to view or edit their entries via a dedicated editor window.
    - **Customizable UI:** Supports customizable UI elements (icons, labels, separators) and dynamically loaded content like month-wise achievements or tasks.
    """
    def __init__(self, parent, main_window, year):
        """
        Initializes the BestInMonths frame and sets up the interface.

        :param parent: The parent widget that holds this frame.
        :param main_window: The main window of the application (likely for general control).
        :param year: The year to be displayed in the UI (used to load year-specific data).
        """
        super().__init__(parent)
        self.configure(bg=INTERFACE['bg_color'])
        self.main_window = main_window
        self.year = year
        self.parent = parent
        self.main_window.check_scrollbar()
        self.main_window.disable_buttons()

        self.tasks = asyncio.run(get_tasks_from_server(year))

        self.first_clickable_label, self.second_clickable_label = (add_source_label_best_in_months
                                                                   (self,
                                                                    icon_path_1=ICONS_PATHS['yearly_plans'],
                                                                    clickable_text="Yearly plans /",
                                                                    click_command_1=self.navigate_to_yearly_plans,
                                                                    icon_path_2=ICONS_PATHS['year'],
                                                                    year_name=f"{self.year} /",
                                                                    icon_path_3=ICONS_PATHS['best_in_months'],
                                                                    text=PAGES_NAMES['best_in_months'],
                                                                    click_command_2=lambda:
                                                                    self.navigate_to_year(self.year)))
        self.first_clickable_label["state"] = "disabled"
        self.second_clickable_label["state"] = "disabled"

        self.icon_image_original = asyncio.run(add_icon_image(ICONS_PATHS['best_in_months']))

        self.add_icon_and_label(self, PAGES_NAMES['best_in_months'])

        add_separator(parent=self, color=INTERFACE['separator'])

        self.months_frame = tk.Frame(self)
        self.months_frame.pack(pady=10, expand=True)

        self.months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        self.images = {}  # Images dict
        self.image_labels = {}

        # Table w months
        self.display_months_table()

    def display_months_table(self):
        """
        Displays a table of months with labels, images (if any), and buttons for uploading or deleting images.
        Each month is shown in a grid layout with:
        - A label for the month's name.
        - An image (if exists) below the label.
        - Upload and Delete buttons for managing the image.

        The method checks for existing images and displays them. It also handles uploading and deleting images
        for each month.

        :return: None
        """
        row = 0
        col = 0

        for month in self.months:
            month_label = tk.Label(self.months_frame, text=month, font=BEST_IN_MONTHS['months_font'],
                                   bg=INTERFACE['bg_color'])
            month_label.grid(row=row, column=col, columnspan=2, padx=10, pady=5, sticky="nsew")

            # Upload button
            upload_button = tk.Button(self.months_frame, text="Upload", font=BEST_IN_MONTHS['buttons_font'],
                                      command=lambda m=month: self.upload_image(m),
                                      bg=BEST_IN_MONTHS['upload_button_color'])
            upload_button.grid(row=row + 2, column=col, padx=10, pady=5)
            upload_button.config(cursor="hand2")

            # Delete button
            delete_button = tk.Button(self.months_frame, text="Delete", font=BEST_IN_MONTHS['buttons_font'],
                                      command=lambda m=month: self.delete_image(m),
                                      bg=BEST_IN_MONTHS['delete_button_color'])
            delete_button.grid(row=row + 2, column=col + 1, padx=10, pady=5)
            delete_button.config(cursor="hand2")

            image_label = tk.Label(self.months_frame, bg=INTERFACE['bg_color'])
            image_label.grid(row=row + 1, column=col, columnspan=2, padx=10, pady=5)

            # Show image
            image_path = next((task["image_path"] for task in self.tasks if task["month"] == month), None)

            if image_path:
                try:
                    image_original = asyncio.run(fetch_image_from_server(image_path))
                    if image_original:
                        image = image_original.resize((BEST_IN_MONTHS['image_width'], BEST_IN_MONTHS['image_height']),
                                                      Image.Resampling.LANCZOS)

                        photo = ImageTk.PhotoImage(image)
                        image_original.close()

                    image_label.config(image=photo)
                    image_label.image = photo
                    self.image_labels[month] = image_label
                except Exception as e:
                    print(f"Error loading image for {month}: {e}")

            col += 2  # Count for table
            if col >= 8:
                col = 0
                row += 3

            self.main_window.enable_buttons()
            self.first_clickable_label["state"] = "normal"
            self.second_clickable_label["state"] = "normal"

    def delete_image(self, month):
        """
        Deletes the image associated with the specified month and updates the task data.

        The method performs the following steps:
        - Finds and removes the image file if it exists.
        - Removes the corresponding entry in the task data.
        - Refreshes the display to reflect the deletion.
        - Displays a success or error message.

        :param month: The month whose image is to be deleted.
        :return: None
        """
        image_path = next((item["image_path"] for item in self.tasks if item["month"] == month), None)

        if image_path:
            try:
                if month in self.images:
                    self.images[month].close()
                    del self.images[month]

                self.tasks = [task for task in self.tasks if task["month"].strip().lower() != month.strip().lower()]

                asyncio.run(remove_image_from_server(image_path, self.year))

                asyncio.run(remove_task_from_server(self.year, month))

                self.remove_month_widgets(month)

                self.display_months_table()

                messagebox.showinfo("Success", f"Image for {month} deleted successfully!")

            except Exception as e:
                print(f"Error deleting image for {month}: {e}")
        else:
            messagebox.showerror("Warning", f"You have to upload the image first!")

    def remove_month_widgets(self, month):
        """
        Removes all widgets (labels and buttons) associated with the specified month from the display.

        The method will search through the month-specific widgets (e.g., labels, buttons) in the
        `months_frame`, and remove them from the layout. It also removes the image associated
        with the month from the display.

        :param month: The month whose associated widgets and image will be removed.
        :return: None
        """
        for widget in self.months_frame.winfo_children():
            if isinstance(widget, tk.Label) or isinstance(widget, tk.Button):
                if widget.cget("text") == month:
                    widget.grid_forget()

        if month in self.image_labels:
            self.image_labels[month].grid_forget()
            del self.image_labels[month]

    def upload_image(self, month):
        """
        Prompts the user to select an image file, uploads it for the specified month,
        and updates the associated image in the tasks JSON.

        The method performs the following:
        1. Asks the user to select an image file.
        2. If an image already exists for the given month, it deletes the old image.
        3. Copies the new image to the appropriate directory.
        4. Updates the `best_in_months` section of the tasks JSON with the new image path.
        5. Refreshes the display to show the newly uploaded image.
        6. If an image with the same name already exists in the target directory, shows a warning message.

        :param month: The month for which the image is being uploaded.
        :return: None
        """
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])

        if file_path:

            if not os.path.exists(file_path):
                messagebox.showerror("Error", f"The selected image file was not found:\n{file_path}")
                return

            # Get the image file name
            image_name = os.path.basename(file_path)

            image_path = f"{BEST_IN_MONTHS['base_folder']}/{self.year}/{image_name}"

            if any(task["image_path"] == image_path for task in self.tasks):
                messagebox.showwarning("Warning",
                                       f"An image with the name '{image_name}' "
                                       f"already exists.\n"
                                       f"Please choose a different image or rename the file.")
                return

            data = {
                "year": self.year,
                "month": month,
                "image_path": image_path
            }

            existing_task = next((task for task in self.tasks if task["month"] == month), None)

            if existing_task:
                old_image_path = existing_task["image_path"]

                self.tasks = [task for task in self.tasks if task["month"] != month]

                if month in self.images:
                    self.images[month].close()
                    del self.images[month]

                asyncio.run(remove_image_from_server(old_image_path, self.year))
                asyncio.run(remove_task_from_server(self.year, month))

            self.tasks.append({"month": month, "image_path": image_path})

            asyncio.run(upload_image_to_server(file_path, self.year))
            asyncio.run(add_link_to_server(data))

            image = asyncio.run(fetch_image_from_server(image_path))
            if image:
                self.images[month] = image.copy()
                image.close()

            if hasattr(self, "image_labels") and month in self.image_labels:
                self.image_labels[month].destroy()
                del self.image_labels[month]

            # Refresh the display to show the new image
            self.display_months_table()

            # Show a success message
            messagebox.showinfo("Success", f"Image for {month} uploaded successfully!")

    def add_icon_and_label(self, parent, text):
        """
        Adds an icon and a label with text to the parent widget.

        This method creates a frame containing an icon and a label. The icon is resized and displayed on the left side,
        and the provided text is displayed to the right of the icon.

        :param parent: The parent widget to which the frame will be added.
        :param text: The text to display next to the icon in the label.
        :return: None
        """
        label_frame = tk.Frame(parent, bg=INTERFACE['bg_color'])
        label_frame.pack(anchor="w", pady=10, padx=10, fill="x")

        try:
            icon_image = self.icon_image_original.resize((30, 30), Image.Resampling.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_image)
            self.icon_image_original.close()

            icon_label = tk.Label(label_frame, image=icon_photo, bg=INTERFACE['bg_color'])
            icon_label.image = icon_photo
            icon_label.pack(anchor="w")
        except Exception as e:
            print(f"Icon load error: {e}")

        text_label = tk.Label(label_frame, text=text,
                              font=BEST_IN_MONTHS['page_title_font'],
                              bg=INTERFACE['bg_color'],
                              anchor="w")
        text_label.pack(anchor="w", pady=(5, 0))

    def navigate_to_yearly_plans(self):
        """
        Return to Yearly plans.

        :return: None
        """
        self.main_window.bind_events()
        self.main_window.show_tab_content("yearly_plans")

    def navigate_to_year(self, year):
        """
        Navigates to the specified year's view by clearing the current canvas and loading the corresponding year frame.

        This method is used to switch the view to the given year by:
        1. Binding events on the main window (presumably for updating UI interactions).
        2. Clearing the current canvas (likely to remove the existing content).
        3. Creating and displaying a new frame corresponding to the selected year.
        4. Attempting to scroll the canvas to the top.

        :param year: The year to navigate to, which corresponds to the data and the frame to be displayed.
        :return: None
        """
        self.main_window.bind_events()
        clear_canvas(self.parent)

        from src.year import Year
        year_frame = Year(self.parent, main_window=self.main_window, year=year)
        year_frame.pack(fill=tk.BOTH, expand=True)

        reset_canvas_view(self.main_window)
