from config.imports import *
from config.settings import BEST_IN_MONTHS
from config.utils import add_source_label_third_level as add_source_label_best_in_months, load_tasks_from_json


class BestInMonths(tk.Frame):
    """
    A Tkinter frame for displaying and interacting with monthly data of a specific year.

    This class is part of a larger application focused on tracking tasks, achievements, or milestones throughout the year.
    It provides an interactive interface for displaying "best" or notable entries for each month, allowing users to navigate through months, view detailed data, and edit or update entries.

    Key Features:
    - **Navigation:** Allows navigation between different pages (e.g., "Yearly Plans" or individual months) through clickable breadcrumbs at the top.
    - **Monthly Data Display:** Displays data for each month, such as notable tasks or achievements, with text and images representing the "best" entry for each month.
    - **Dynamic Month Setup:** Loads and displays the months of the selected year, dynamically fetching data from a provided JSON file.
    - **Interactive Entries:** Allows users to click on specific months to view or edit their entries via a dedicated editor window.
    - **Customizable UI:** Supports customizable UI elements (icons, labels, separators) and dynamically loaded content like month-wise achievements or tasks.
    """

    def __init__(self, parent, main_window, json_file, year):
        """
        Initializes the BestInMonths frame and sets up the interface.

        :param parent: The parent widget that holds this frame.
        :param main_window: The main window of the application (likely for general control).
        :param json_file: The path to the JSON file containing the data for the best entries per month.
        :param year: The year to be displayed in the UI (used to load year-specific data).
        """
        super().__init__(parent)
        self.configure(bg=INTERFACE['bg_color'])
        self.main_window = main_window
        self.year = year
        self.parent = parent
        self.json_file = json_file
        self.main_window.check_scrollbar()

        self.tasks = load_tasks_from_json(json_file)

        add_source_label_best_in_months(self,
                                        icon_path_1=ICONS_PATHS['yearly_plans'],
                                        clickable_text="Yearly plans /",
                                        click_command_1=self.navigate_to_yearly_plans,
                                        icon_path_2=ICONS_PATHS['year'],
                                        year_name=f"{self.year} /",
                                        icon_path_3=ICONS_PATHS['best_in_months'],
                                        text=PAGES_NAMES['best_in_months'],
                                        click_command_2=lambda: self.navigate_to_year(self.year))

        self.icon_image_original = Image.open(ICONS_PATHS['best_in_months'])

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
            image_path = self.tasks.get("best_in_months", {}).get(month)
            if image_path and os.path.exists(image_path):
                try:
                    image = Image.open(image_path)
                    image = image.resize((BEST_IN_MONTHS['image_width'], BEST_IN_MONTHS['image_height']))
                    photo = ImageTk.PhotoImage(image)
                    image.close()

                    image_label.config(image=photo)
                    image_label.image = photo
                    self.image_labels[month] = image_label
                except Exception as e:
                    print(f"Error loading image for {month}: {e}")

            col += 2  # Count for table
            if col >= 8:
                col = 0
                row += 3

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
        image_path = self.tasks.get("best_in_months", {}).get(month)

        if image_path and os.path.exists(image_path):
            try:
                if month in self.images:
                    self.images[month].close()
                    del self.images[month]

                os.remove(image_path)

                if "best_in_months" in self.tasks:
                    del self.tasks["best_in_months"][month]

                self.save_tasks_to_json()

                self.remove_month_widgets(month)

                self.display_months_table()

                messagebox.showinfo("Success", f"Image for {month} deleted successfully!")

            except Exception as e:
                print(f"Error deleting image for {month}: {e}")
                messagebox.showerror("Error", f"Error deleting image for {month}: {e}")
        else:
            messagebox.showerror("Error", f"No image found for {month}.")

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
            # Get the image file name
            image_name = os.path.basename(file_path)
            year_folder = f"./assets/yearly_plans/year/{self.year}"

            # Check if the image already exists in the directory
            destination_path = os.path.join(year_folder, image_name)
            if os.path.exists(destination_path):
                messagebox.showwarning("Image Already Exists",
                                       f"An image with the name '{image_name}' already exists in the directory.")
                return  # Do not proceed with uploading if the image already exists

            # If image already exists for the month, delete the old image
            if month in self.tasks.get("best_in_months", {}):
                old_image_path = self.tasks["best_in_months"][month]
                # Delete old image
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

            # Create the folder if it doesn't exist
            if not os.path.exists(year_folder):
                os.makedirs(year_folder)

            # Copy the selected image to the target directory
            shutil.copy(file_path, destination_path)

            # Open the image and store it in the images dictionary
            image = Image.open(destination_path)
            self.images[month] = image.copy()
            image.close()

            # Update the JSON with the new image path
            if "best_in_months" not in self.tasks:
                self.tasks["best_in_months"] = {}
            self.tasks["best_in_months"][month] = destination_path

            self.save_tasks_to_json()

            # Refresh the display to show the new image
            self.display_months_table()

            # Show a success message
            messagebox.showinfo("Success", f"Image for {month} uploaded successfully!")

    def save_tasks_to_json(self):
        """
        Saving data to JSON.

        :return: None
        """
        json_path = f"data/years/{self.year}.json"

        with open(json_path, "w", encoding="utf-8") as json_file:
            json.dump(self.tasks, json_file, ensure_ascii=False, indent=4)

    def update_image_label(self, label, month):
        """
        Updates the given label with the image for the specified month.

        This method resizes the image stored for the given month to fit the designated dimensions
        and updates the label with the resized image.

        :param label: The label widget to display the image.
        :param month: The month for which the image should be displayed.
        :return: None
        """
        image = self.images[month]
        image = image.resize((BEST_IN_MONTHS['image_width'],
                              BEST_IN_MONTHS['image_height']))
        photo = ImageTk.PhotoImage(image)

        label.config(image=photo)
        label.image = photo

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
        year_frame = Year(self.parent, json_file=f"data/years/{year}.json", main_window=self.main_window, year=year)
        year_frame.pack(fill=tk.BOTH, expand=True)

        reset_canvas_view(self.main_window)
