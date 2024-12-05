from config.imports import *
from config.settings import YEARLY_PLANS
from config.tooltip import ToolTip
import re


def rename_year_file(old_year, new_year):
    """
    Renames the JSON file associated with a specific year.

    :param old_year: The current year whose file is to be renamed.
    :param new_year: The new year value to replace the old one in the file name.
    :return: None
    """
    old_file_path = f"./data/years/{old_year}.json"
    new_file_path = f"./data/years/{new_year}.json"

    if os.path.exists(old_file_path):
        os.rename(old_file_path, new_file_path)
    else:
        messagebox.showerror("Error", f"File for year {old_year} not found.")


def update_year_paths_in_json(old_year, new_year):
    """
    Updates paths in the JSON that reference the old year and replaces it with the new year,
    as well as updating any date strings like 'Week starting 2025-01-01' or '1/21/27' or '01.05.25'
    to match the new year, and changing the old year in filenames and paths.

    :param old_year: Old year
    :param new_year: New year
    :return: None
    """
    # Load the JSON data from the file
    json_file_path = f"./data/years/{old_year}.json"  # Replace with your actual JSON file path

    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    # Create the old year string for matching
    old_year_str = f"{old_year}"
    old_year_path_str = f"./assets/yearly_plans/year/{old_year}"

    # Define a function to recursively update the data
    def recursive_update(obj):
        if isinstance(obj, dict):
            # Iterate over keys to update
            keys_to_update = list(obj.keys())  # Make a list of current keys to modify
            for key in keys_to_update:
                value = obj[key]

                # Check if the key is a date in MM/DD/YY format (e.g., "1/21/26")
                if re.match(r'\d{1,2}/\d{1,2}/\d{2}', key):
                    print(f"Updating date key: {key}")  # Debugging output
                    new_key = re.sub(r'(\d{1,2}/\d{1,2}/)(\d{2})', lambda m: m.group(1) + str(new_year)[2:], key)
                    obj[new_key] = obj.pop(key)  # Replace the old key with the new one
                    print(f"Key updated to: {new_key}")  # Debugging output

                # Check if the key is a date in DD.MM.YY format (e.g., "01.05.25")
                elif re.match(r'\d{2}\.\d{2}\.\d{2}', key):
                    print(f"Updating date key: {key}")  # Debugging output
                    new_key = re.sub(r'(\d{2}\.\d{2}\.)(\d{2})', lambda m: m.group(1) + str(new_year)[2:], key)
                    obj[new_key] = obj.pop(key)  # Replace the old key with the new one
                    print(f"Key updated to: {new_key}")  # Debugging output

                # Check if the key contains the old year and replace it
                elif old_year_str in key:
                    print(f"Updating key: {key}")  # Debugging output
                    new_key = key.replace(old_year_str, str(new_year))
                    obj[new_key] = obj.pop(key)  # Replace the old key with the new one
                    print(f"Key updated to: {new_key}")  # Debugging output

                # Check if the value is a string, and replace the old year
                if isinstance(value, str):
                    # Replace the old year with the new year in paths, filenames, and other strings
                    if old_year_str in value:
                        print(f"Updating value: {value}")  # Debugging output
                        obj[key] = value.replace(old_year_str, str(new_year))

                    # Replace paths that include the old year (e.g., ./assets/yearly_plans/year/{old_year})
                    if old_year_path_str in value:
                        print(f"Updating path: {value}")  # Debugging output
                        obj[key] = value.replace(old_year_path_str, f"./assets/yearly_plans/year/{new_year}")

                    # Update year in date-like strings (e.g., "Week starting 2025-01-01")
                    if re.search(r'\d{4}-\d{2}-\d{2}', value):
                        print(f"Updating date-like string: {value}")  # Debugging output
                        obj[key] = re.sub(r'\b' + old_year_str + r'\b', str(new_year), value)

                    # Update year in MM/DD/YY date format (e.g., "1/21/27" to "1/21/28")
                    if re.search(r'\d{1,2}/\d{1,2}/\d{2}', value):
                        print(f"Updating date (MM/DD/YY): {value}")  # Debugging output
                        obj[key] = re.sub(r'(\d{1,2}/\d{1,2}/)(\d{2})', lambda m: m.group(1) + str(new_year)[2:],
                                          value)

                    # Update year in DD.MM.YY date format (e.g., "01.05.25" to "01.05.26")
                    if re.search(r'\d{2}\.\d{2}\.\d{2}', value):
                        print(f"Updating date (DD.MM.YY): {value}")  # Debugging output
                        obj[key] = re.sub(r'(\d{2}\.\d{2}\.)(\d{2})', lambda m: m.group(1) + str(new_year)[2:],
                                          value)

                # Recurse for nested dictionaries or lists
                elif isinstance(value, (dict, list)):
                    recursive_update(value)

        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    recursive_update(item)

    # Update all year-related values in the JSON data recursively
    recursive_update(data)

    # Save the updated JSON data back to the file
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


def delete_year_file(year):
    """
    Deletes the JSON file corresponding to the specified year.

    :param year: The year for which the file should be deleted.
    :return: None
    """
    year_file_path = f"./data/years/{year}.json"
    if os.path.exists(year_file_path):
        os.remove(year_file_path)  # Delete file
    else:
        print(f"File for year {year} not found.")


def create_year_json(year):
    """
    Creates a new JSON file for the given year with initial data structure if the file does not exist.

    This method creates the necessary folder if it doesn't exist, and then creates a new JSON file for the given
    year, initializing it with a predefined structure. This structure includes sections for a calendar, yearly plans,
    habit tracker, gratitude diary, best-in-months data, monthly plans and diaries, and a review of the year.

    :param year: The year for which the JSON file is to be created.
    :return: None
    """
    year_json_path = f"./data/years/{year}.json"

    # If folder data/years
    os.makedirs(os.path.dirname(year_json_path), exist_ok=True)  # Создаем папку, если она не существует

    # If file exists
    if not os.path.exists(year_json_path):
        year_data = {
            "calendar": {},
            "yearly_plans": [],
            "habit_tracker": {
                f"Week starting {year}-01-01": {
                    "Monday": [
                        {"task": "Reading", "completed": False},
                        {"task": "Dreams", "completed": False},
                        {"task": "Meditation", "completed": False}
                    ],
                    "Tuesday": [
                        {"task": "Reading", "completed": False},
                        {"task": "Sports", "completed": False},
                        {"task": "Dreams", "completed": False},
                        {"task": "Meditation", "completed": False}
                    ],
                    "Wednesday": [
                        {"task": "Reading", "completed": False},
                        {"task": "Dreams", "completed": False},
                        {"task": "Meditation", "completed": False}
                    ],
                    "Thursday": [
                        {"task": "Reading", "completed": False},
                        {"task": "Sports", "completed": False},
                        {"task": "Dreams", "completed": False},
                        {"task": "Meditate", "completed": False}
                    ],
                    "Friday": [
                        {"task": "Reading", "completed": False},
                        {"task": "Dreams", "completed": False},
                        {"task": "Meditation", "completed": False}
                    ],
                    "Saturday": [
                        {"task": "Dreams", "completed": False},
                        {"task": "Meditation", "completed": False},
                        {"task": "Sports", "completed": False}
                    ],
                    "Sunday": [
                        {"task": "Rest :3", "completed": False}
                    ]
                }
            },
            "gratitude_diary": {},
            "best_in_months": {},
            "months": {
                "January": {
                    "plans": [],
                    "diary": {}
                },
                "February": {
                    "plans": [],
                    "diary": {}
                },
                "March": {
                    "plans": [],
                    "diary": {}
                },
                "April": {
                    "plans": [],
                    "diary": {}
                },
                "May": {
                    "plans": [],
                    "diary": {}
                },
                "June": {
                    "plans": [],
                    "diary": {}
                },
                "July": {
                    "plans": [],
                    "diary": {}
                },
                "August": {
                    "plans": [],
                    "diary": {}
                },
                "September": {
                    "plans": [],
                    "diary": {}
                },
                "October": {
                    "plans": [],
                    "diary": {}
                },
                "November": {
                    "plans": [],
                    "diary": {}
                },
                "December": {
                    "plans": [],
                    "diary": {}
                }
            },
            "review": {
                "1. How would you describe this year with a single word?": "",
                "2. What is your biggest challenge this year?": "",
                "3. One thing you are most proud of this year:": "",
                "4. How did you take care of yourself this year?": "",
                "5. How have you changed over the year": "",
                "6. New things you learned:": "",
                "7. What made this year special?": "",
                "8. What are you most grateful for?": "",
                "9. Top 3 priorities for the next year:": "",
                "10. Did you do your best?": ""
            }
        }

        # Save to JSON
        with open(year_json_path, 'w', encoding='utf-8') as file:
            json.dump(year_data, file, indent=4, ensure_ascii=False)


class YearlyPlans(tk.Frame):
    """
    A class that represents the Yearly Plans page in the application. This page allows the user to view,
    create, edit, and delete yearly plans.
    """
    def __init__(self, parent, main_window, json_file):
        """
        Initializes the YearlyPlans page with the provided parent, main window, and JSON file.

        :param parent: The parent widget for this frame.
        :param main_window: The main window of the application.
        :param json_file: The path to the JSON file containing yearly plan data.
        """
        super().__init__(parent)
        self.configure(bg=INTERFACE['bg_color'])
        self.main_window = main_window
        self.parent = parent

        self.year_buttons = []
        self.json_file = json_file

        self.icon_image_original = Image.open(ICONS_PATHS['yearly_plans'])  # Year icon path
        self.icon_image = self.icon_image_original.resize((20, 20), Image.Resampling.LANCZOS)
        self.icon_photo = ImageTk.PhotoImage(self.icon_image)

        add_source_label(self, ICONS_PATHS['yearly_plans'], PAGES_NAMES['yearly_plans'],
                         bg_color=INTERFACE['bg_color'], font=INTERFACE['source_label_font'])

        # Banner add
        self.banner_label, self.banner_image_original = add_banner(
            self,
            banner_path=BANNER_PATHS['yearly_plans'],
            bg_color=INTERFACE['bg_color']
        )

        # resize_banner
        if self.banner_label and self.banner_image_original:
            self.bind("<Configure>", lambda event: resize_banner(
                self,
                self.banner_label,
                self.banner_image_original
            ))

        add_icon_and_label(self, text=PAGES_NAMES['yearly_plans'], icon_path=ICONS_PATHS['yearly_plans'],
                           bg_color=INTERFACE['bg_color'])
        add_separator(parent=self, color=INTERFACE['separator'])

        self.add_quote_and_image()

        self.year_buttons_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        self.year_buttons_frame.pack(pady=5)

        self.load_year_buttons()  # Add year buttons

    def bind_right_click_to_buttons(self):
        """
        Binds the right-click (Button-3) event to each year button. When a button is right-clicked,
        it triggers the context menu (typically for editing or deleting the year).

        :return: None
        """
        for button in self.year_buttons:
            button.bind("<Button-3>", lambda event, button=button: self.show_context_menu(event, button))

    def show_context_menu(self, event, year_button):
        """
        Displays a context menu when a right-click (Button-3) event occurs on a year button.
        The menu includes options to edit or delete the selected year.

        :param event: The event object generated by the right-click.
        :param year_button: The button representing the year that was right-clicked.
        :return: None
        """
        context_menu = tk.Menu(self, tearoff=0)  # Context menu

        context_menu.add_command(label="Edit", command=lambda: self.edit_year(year_button),
                                 font=YEARLY_PLANS['menu_font'])
        context_menu.add_command(label="Delete", command=lambda: self.delete_year(year_button),
                                 font=YEARLY_PLANS['menu_font'])

        # Show menu
        context_menu.post(event.x_root, event.y_root)

    def edit_year(self, year_button):
        """
        Opens a window for editing the year on the selected year button. The user can input a new year.

        :param year_button: The button representing the year to be edited.
        :return: None
        """
        old_year = int(year_button.cget("text"))  # Get current year from button

        edit_window = tk.Toplevel(self)
        edit_window.withdraw()
        edit_window.title("Edit Year")

        center_window_on_parent(self.main_window, edit_window, 300, 200)
        edit_window.iconbitmap(APP['icon_path'])  # Путь к файлу иконки

        label = tk.Label(edit_window, text="Enter the new year:", font=YEARLY_PLANS['toplevel_windows_font'])
        label.pack(padx=10, pady=10)

        # New year entry
        year_entry = tk.Entry(edit_window, font=YEARLY_PLANS['toplevel_windows_font'])
        year_entry.pack(padx=10, pady=10)
        year_entry.focus_set()
        year_entry.bind("<Return>",
                        lambda event: self.submit_year_edit(year_entry.get(), old_year, year_button, edit_window))

        # Save button
        submit_button = tk.Button(edit_window, text="Save",
                                  command=lambda: self.submit_year_edit(year_entry.get(), old_year, year_button,
                                                                        edit_window),
                                  font=YEARLY_PLANS['save_button_font'])
        submit_button.pack(padx=10, pady=10)
        submit_button.config(cursor="hand2")

        # Cancel button
        cancel_button = tk.Button(edit_window, text="Cancel", command=edit_window.destroy,
                                  font=YEARLY_PLANS['cancel_button_font'])
        cancel_button.pack(padx=10, pady=5)
        cancel_button.config(cursor="hand2")

        edit_window.deiconify()

    def submit_year_edit(self, new_year_str, old_year, year_button, edit_window):
        """
        Handles the submission of the year edit form. It updates the year in the JSON data and renames
        the associated JSON file if the new year is valid and doesn't already exist.

        :param new_year_str: The string representation of the new year entered by the user.
        :param old_year: The old year (before the edit) displayed on the year button.
        :param year_button: The button that displays the year. Its text will be updated after a successful edit.
        :param edit_window: The edit window that will be closed after the successful update.
        :return: None
        """
        if new_year_str.isdigit():
            new_year = int(new_year_str)

            # Check if the year exists
            if self.is_year_exists(new_year):
                messagebox.showerror("Error", f"Year {new_year} already exists.")
            else:
                # Update the paths in JSON that reference the old year
                update_year_paths_in_json(old_year, new_year)

                # Update JSON date
                self.update_year_in_json(old_year, new_year)

                # Rename year JSON
                rename_year_file(old_year, new_year)

                # Rename the folder for the year
                old_folder = f"./assets/yearly_plans/year/{old_year}"
                new_folder = f"./assets/yearly_plans/year/{new_year}"

                # Check if the old folder exists and rename it
                if os.path.exists(old_folder):
                    # Rename the folder
                    shutil.move(old_folder, new_folder)

                # Update year button text
                year_button.config(text=str(new_year))

                # Update the command of the year button to use the new year
                year_button.config(command=lambda: self.open_year_page(new_year))

                messagebox.showinfo("Success", f"Year updated to {new_year}")

                edit_window.destroy()
        else:
            messagebox.showerror("Error", "Invalid year entered.")

    def update_year_in_json(self, old_year, new_year):
        """
        Updates the year value and its associated JSON path in the main JSON file.

        :param old_year: The year to be updated (current value).
        :param new_year: The new year value to replace the old one.
        :return: None
        """
        if os.path.exists(self.json_file):
            with open(self.json_file, 'r') as file:
                data = json.load(file)

            # Update year
            for year_data in data["years"]:
                if year_data["year"] == old_year:
                    year_data["year"] = new_year
                    year_data["json_path"] = f"./data/years/{new_year}.json"
                    break

            # Save to JSON
            with open(self.json_file, 'w') as file:
                json.dump(data, file, indent=4)

    def delete_year(self, year_button):
        """
        Deletes the specified year, including its associated data file, folder, and removes the year button.

        :param year_button: The button widget representing the year to be deleted.
        :return: None
        """
        # Get the year
        year = int(year_button.cget("text"))

        # Confirm
        confirm = messagebox.askyesno("Delete Year", f"Are you sure you want to delete year {year}?")
        if confirm:
            # Delete from yearly_plans.json
            self.delete_year_from_json(year)

            # Delete JSON year file
            delete_year_file(year)
            year_folder = f'./assets/yearly_plans/year/{year}'

            # Delete folder
            if os.path.exists(year_folder):
                shutil.rmtree(year_folder)
            else:
                print(f"Folder {year_folder} does not exist.")

            # Delete button
            self.year_buttons = [btn for btn in self.year_buttons if btn != year_button]
            year_button.destroy()

            messagebox.showinfo("Success", f"Year {year} deleted.")
        else:
            messagebox.showinfo("Cancel", "Year deletion cancelled.")

    def delete_year_from_json(self, year):
        """
        Deletes the specified year from the JSON file.

        :param year: The year to be deleted from the JSON file.
        :return: None
        """
        if os.path.exists(self.json_file):
            with open(self.json_file, 'r') as file:
                data = json.load(file)

            # Delete specific year entry
            data["years"] = [item for item in data["years"] if item["year"] != year]

            # Save to JSON
            with open(self.json_file, 'w') as file:
                json.dump(data, file, indent=4)

    def load_year_buttons(self):
        """
        Loads the year buttons from the JSON file and displays them in the interface in reverse order.

        This function will read the years from the JSON file and create buttons for each year, displaying them
        starting from the most recent year. If the file does not exist or is empty, no buttons will be created.

        :return: None
        """
        yearly_plans_path = self.json_file

        if os.path.exists(yearly_plans_path):
            with open(yearly_plans_path, 'r') as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    print("Error loading JSON data. Initializing with empty data.")
                    data = {"years": []}

            # Reverse the list of years to display the most recent first
            years = data.get("years", [])
            years.reverse()  # This will reverse the list in-place

            for item in years:
                year = item.get("year")
                if year is not None:
                    year_button = tk.Button(
                        self.year_buttons_frame,
                        text=str(year),
                        command=lambda y=year: self.open_year_page(y),
                        image=self.icon_photo,
                        compound=tk.LEFT,
                        font=YEARLY_PLANS['year_buttons_font']
                    )
                    year_button.pack(side=tk.TOP, pady=5)
                    year_button.config(cursor="hand2")

                    # Tooltip for right-click instructions
                    ToolTip(year_button, "Right click to edit/delete")
                    self.year_buttons.append(year_button)

            # Bind right-click events to the buttons
            self.bind_right_click_to_buttons()
        else:
            print(f"{yearly_plans_path} does not exist. No buttons created.")

    def add_quote_and_image(self):
        """
        Adds a quote and an image to the user interface, along with a pin label and an "Add Year" button.

        This function creates the following elements:
        - A frame to hold the content.
        - A pin label with an icon and text.
        - An "Add Year" button.
        - A section for displaying a quote and an image.
        - A vertical separator line between the quote and the image.

        :return: None
        """
        image_frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        image_frame.pack(pady=5)

        # Pin frame
        pin_label_frame = tk.Frame(image_frame, bg=YEARLY_PLANS['pin_label_bg'])
        pin_label_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nw")

        # Load pin image
        pin_icon = PhotoImage(file=YEARLY_PLANS['pin_icon_path']).subsample(2, 2)
        smile_icon = PhotoImage(file=YEARLY_PLANS['smile_icon_path']).subsample(2, 2)

        # Pin label
        pin_label_icon = tk.Label(pin_label_frame, image=pin_icon, bg=YEARLY_PLANS['pin_label_bg'])
        pin_label_icon.image = pin_icon
        pin_label_icon.pack(side=tk.LEFT, padx=(0, 5))

        # Text
        pin_text_label = tk.Label(pin_label_frame, text="Choose a year", font=YEARLY_PLANS['pin_frame_font'],
                                  fg=YEARLY_PLANS['pin_frame_text_color'],
                                  bg=YEARLY_PLANS['pin_label_bg'])
        pin_text_label.pack(side=tk.LEFT)

        # Smile icon
        smile_label_icon = tk.Label(pin_label_frame, image=smile_icon, bg=YEARLY_PLANS['pin_label_bg'])
        smile_label_icon.image = smile_icon
        smile_label_icon.pack(side=tk.LEFT, padx=(5, 0))

        # Add year button
        add_year_frame = tk.Frame(image_frame)
        add_year_frame.grid(row=1, column=0, padx=10, pady=(5, 0), sticky="nsew")

        add_year_button = tk.Button(add_year_frame, text="Add Year", command=self.show_year_input,
                                    bg=YEARLY_PLANS['add_button_color'], font=YEARLY_PLANS['add_button_font'])
        add_year_button.pack(anchor="center")
        add_year_button.config(cursor="hand2")

        # Quote and image frame
        quote_with_image_frame = tk.Frame(image_frame, bg=INTERFACE['bg_color'])
        quote_with_image_frame.grid(row=0, column=1, rowspan=10, padx=10, pady=5, sticky="n")

        # Image
        add_image_to_grid(quote_with_image_frame, YEARLY_PLANS['image_link'], row=0, column=0, height=200,
                          width=300, rowspan=1, columnspan=1)

        quote_frame = tk.Frame(quote_with_image_frame, bg=INTERFACE['bg_color'])
        quote_frame.grid(row=1, column=0, sticky="n")

        # Vertical line
        line = tk.Canvas(quote_frame, width=2, bg=INTERFACE['separator'], height=100)
        line.grid(row=0, column=0, padx=(0, 10), sticky="n")

        # Quote text
        quote_text = YEARLY_PLANS['quote_text']
        label_quote = tk.Label(quote_frame, text=quote_text, font=YEARLY_PLANS['quote_font'],
                               bg=INTERFACE['bg_color'], wraplength=YEARLY_PLANS['quote_wraplength'])
        label_quote.grid(row=0, column=1, sticky="w")

        image_frame.pack(pady=5)

    def show_year_input(self):
        """
        Opens a dialog window that allows the user to enter a year and save it.

        The method creates a new top-level window for the user to input a year. The user can either press
        "Enter" or click the "Save" button to save the year. Once the user has entered a year, it is passed
        to the `add_year` method to be added.

        :return: None
        """
        dialog = tk.Toplevel(self)
        dialog.withdraw()
        dialog.title("Add Year")

        center_window_on_parent(self.main_window, dialog, 250, 150)
        dialog.iconbitmap(APP['icon_path'])

        tk.Label(dialog, text="Enter a year:", font=YEARLY_PLANS['toplevel_windows_font']).pack(pady=10)

        year_entry = tk.Entry(dialog, font=YEARLY_PLANS['toplevel_windows_font'])
        year_entry.pack(pady=5)
        year_entry.bind("<Return>", lambda event: self.add_year(year_entry.get(), dialog))

        # Save button
        ok_button = tk.Button(dialog, text="Save", command=lambda: self.add_year(year_entry.get(), dialog),
                              font=YEARLY_PLANS['toplevel_windows_font'])
        ok_button.pack(pady=10)
        ok_button.config(cursor="hand2")

        dialog.deiconify()

    def add_year(self, year_input, dialog):
        """
        Adds a new year to the application by creating a folder, button, and updating the relevant JSON files.

        The method checks if the input year is a valid number and if the year already exists. If not, it creates a
        new folder for the year, a button for the year on the user interface, and updates the `yearly_plans.json`
        file with the new year. It also creates a separate JSON file for the new year and provides the option to
        edit or delete the year using a right-click menu.

        :param year_input: The input year as a string entered by the user.
        :param dialog: The dialog window where the user enters the year, which will be closed after the year is added.
        :return: None
        """
        if year_input and year_input.isdigit():  # Check if number
            year = int(year_input)

            # Check if year in JSON
            if self.is_year_exists(year):
                messagebox.showerror("Error", f"Year {year} already exists.")
                return

            # Create new folder
            year_folder = f'./assets/yearly_plans/year/{year}'
            if not os.path.exists(year_folder):
                os.makedirs(year_folder)

            # Create year button
            year_button = tk.Button(
                self.year_buttons_frame,
                text=str(year),
                command=lambda: self.open_year_page(year),
                image=self.icon_photo,
                compound=tk.LEFT,
                font=("Arial", 12)
            )
            # Pack the new button at the top
            year_button.pack(side=tk.TOP, pady=5, anchor="w")
            year_button.config(cursor="hand2")

            # Add to yearly_plans.json
            self.update_yearly_plans(year)

            # New JSON for year
            create_year_json(year)

            # Add tooltip
            ToolTip(year_button, "Right click to edit/delete")
            self.year_buttons.insert(0, year_button)  # Insert the button at the start of the list
            self.bind_right_click_to_buttons()

            # Rearrange the packing to ensure the new button is on top
            self.rearrange_year_buttons()

            # Close the dialog
            dialog.destroy()

        else:
            messagebox.showerror("Error", "Please enter a valid year.")  # Show error if invalid year

    def rearrange_year_buttons(self):
        """
        Rearranges the year buttons to ensure they are displayed in the correct order,
        with the most recent year appearing at the top.

        :return: None
        """
        # Clear all the year buttons from the frame
        for button in self.year_buttons:
            button.pack_forget()

        # Repack the buttons with the most recent year at the top
        for button in self.year_buttons:
            button.pack(side=tk.TOP, pady=5, anchor="w")

    def is_year_exists(self, year):
        """
        Check if the year exists in the JSON file under the "years" key.

        :param year: The year to check for in the JSON data (can be int or str).
        :return: True if the year exists, False otherwise.
        """
        try:
            with open(self.json_file, 'r') as file:
                data = json.load(file)
            for item in data.get("years", []):
                if item["year"] == year:
                    return True
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return False

    def update_yearly_plans(self, year):
        """
        Updates the yearly_plans.json file by adding the new year to the list of years if it doesn't already exist.

        This method checks if the `yearly_plans.json` file exists and contains valid data. If the file exists and is valid,
        it checks if the year already exists in the list of years. If not, it appends the new year data, including the
        year and the path to its associated JSON file, to the list and saves the updated data back to the file.

        If the file does not exist or is empty, it creates a new file with the list of years containing the provided year.

        :param year: The year to be added to the `yearly_plans.json` file.
        :return: None
        """
        # Path to yearly_plans.json
        yearly_plans_path = self.json_file

        # If file exists
        if os.path.exists(yearly_plans_path):
            with open(yearly_plans_path, 'r') as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = {"years": []}
        else:
            data = {"years": []}

        # Check if the data is a dictionary and contains the "years" key
        if isinstance(data, dict) and "years" in data:
            if not any(item["year"] == year for item in data["years"]):
                year_data = {
                    "year": year,
                    "json_path": f"./data/years/{year}.json"
                }
                data["years"].append(year_data)
        else:
            data = {"years": [{"year": year, "json_path": f"./data/years/{year}.json"}]}

        with open(yearly_plans_path, 'w') as file:
            json.dump(data, file, indent=4)

    def open_year_page(self, year):
        """
        Opens the page for the specified year, clears the main window's canvas, and displays the year's details.

        This method clears the main canvas of the current window and then creates a new instance of the `Year` class,
        passing the path to the corresponding JSON file for the given year. It also makes sure the content is displayed
        in the main window. If a canvas exists, it scrolls it to the top; otherwise, it logs a message indicating no canvas is found.

        :param year: The year for which the page is to be opened.
        :return: None
        """
        self.main_window.clear_canvas()

        from src.year import Year
        year_frame = Year(self.parent, json_file=f"./data/years/{year}.json", main_window=self.main_window, year=year)
        year_frame.pack(fill=tk.BOTH, expand=True)

        reset_canvas_view(self.main_window)
