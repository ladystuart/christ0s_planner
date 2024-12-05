from config.imports import *
from config.settings import WISHLIST
from config.tooltip import ToolTip
from config.utils import add_source_label_second_level as add_source_label_lists_for_life


def browse_image(image_entry, window):
    """
    Opens a file dialog to select an image and updates the image path entry.

    :param image_entry: Entry widget to display the path of the selected image.
    :param window: The current window that is minimized during file browsing.
    :return: None
    """
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")])

    if file_path:
        # Update the image path in the entry field (no copying yet)
        image_entry.delete(0, tk.END)
        image_entry.insert(0, file_path)

        window.deiconify()


class Wishlist(tk.Frame):
    """
    The Wishlist class is responsible for creating the interface of the 'Wishlist' tab.
    It includes a wishlist page with functionality for users to delete, add, and edit items.
    """
    def __init__(self, parent, json_file, main_window):
        """
        Initializes the Wishlist class.

        :param parent: Parent container where the Wishlist frame will be placed.
        :param json_file: Path to the JSON file storing wishlist items.
        :param main_window: Reference to the main window of the application.
        """
        super().__init__(parent)
        self.parent = parent
        self.main_window = main_window
        self.configure(bg=INTERFACE['bg_color'])  # Background color

        self.json_file = json_file  # Store the json_file path
        self.wishlist_items = self.load_wishlist()  # Initialize wishlist_items

        add_source_label_lists_for_life(
            self,  # Parent element
            icon_path_1=ICONS_PATHS['lists_for_life'],
            clickable_text="#Lists_for_life /",
            click_command=self.navigate_to_lists_for_life,
            icon_path_2=ICONS_PATHS['wishlist'],
            text=PAGES_NAMES['wishlist']
        )

        # Banner add
        self.banner_label, self.banner_image_original = add_banner(
            self,
            banner_path=BANNER_PATHS['wishlist'],  # Path to banner
            bg_color=INTERFACE['bg_color']  # Bg color
        )

        # resize_banner function
        if self.banner_label and self.banner_image_original:
            self.bind("<Configure>", lambda event: resize_banner(
                self,
                self.banner_label,
                self.banner_image_original
            ))

        add_icon_and_label(self, text=PAGES_NAMES['wishlist'], icon_path=ICONS_PATHS['wishlist'],
                           bg_color=INTERFACE['bg_color'])
        add_separator(parent=self, color=INTERFACE['separator'])

        # Add button
        add_button = tk.Button(self, text="Add", bg=WISHLIST['add_button_color'], command=self.open_add_item_window,
                               font=WISHLIST['add_button_font'])
        add_button.pack(pady=10)
        add_button.config(cursor="hand2")

        self.display_tasks()

    def open_add_item_window(self):
        """
        Opens a pop-up window to add a new item to the wishlist. The user can provide a title and an image path.

        :return: None
        """
        add_window = tk.Toplevel(self)
        add_window.withdraw()
        add_window.title("Add new element")
        add_window.iconbitmap(APP['icon_path'])

        center_window_on_parent(self.main_window, add_window, 450, 250)

        task_label = tk.Label(add_window, text="Title", font=WISHLIST['toplevel_windows_font'])
        task_label.pack(pady=(10, 0))

        task_entry = tk.Entry(add_window, font=WISHLIST['toplevel_windows_font'], width=50)
        task_entry.pack(pady=(0, 10))
        task_entry.insert(0, "")
        task_entry.bind("<Return>", lambda event: self.add_item(task_entry.get(), image_entry.get(), add_window))

        ToolTip(task_entry, "Enter title")

        image_label = tk.Label(add_window, text="Path to the image", font=WISHLIST['toplevel_windows_font'])
        image_label.pack(pady=(10, 0))

        image_entry = tk.Entry(add_window, font=WISHLIST['toplevel_windows_font'], width=50)
        image_entry.pack(pady=(0, 10))
        image_entry.insert(0, "")
        image_entry.bind("<Return>", lambda event: self.add_item(task_entry.get(), image_entry.get(), add_window))

        ToolTip(image_entry, "Click before pressing the \"Browse\" button")

        # Browse button
        browse_button = tk.Button(add_window, text="Browse",
                                  command=lambda: browse_image(image_entry, add_window),
                                  font=WISHLIST['browse_button_font'])
        browse_button.pack(pady=5)
        browse_button.config(cursor="hand2")

        # Save button
        add_button = tk.Button(add_window, text="Save", font=WISHLIST['save_button_font'],
                               command=lambda: self.add_item(task_entry.get(), image_entry.get(), add_window))
        add_button.pack(pady=5)
        add_button.config(cursor="hand2")

        add_window.deiconify()

    def load_wishlist(self):
        """
        Load data from JSON

        :return: None
        """
        wishlist_path = self.json_file
        if os.path.exists(wishlist_path):
            with open(wishlist_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('wishlist', [])
        return []  # Return empty list if nothing

    def add_item(self, title, image_path, add_window):
        """
        Adds a new item to the wishlist.

        :param title: The title of the wishlist item.
        :param image_path: The file path of the associated image.
        :param add_window: The pop-up window instance where the item is added.
        :return: None
        """
        if title.strip():  # Checking if title is not empty
            if not image_path.strip():  # Checking if image path is empty
                messagebox.showerror("Error", "Please select an image file.")
                add_window.lift()
                return

            # Copying image in the folder when "Save" is pressed
            destination_path = os.path.join(WISHLIST['dist_folder_path'], os.path.basename(image_path))

            # Checking if file with the same title already exists
            if os.path.exists(destination_path):
                messagebox.showerror("Error",
                                     f"File with title '{os.path.basename(image_path)}' "
                                     f"already exists.\nPlease, rename your file.")
                add_window.lift()
                return

            try:
                shutil.copy(image_path, destination_path)  # Copying file
            except Exception as e:
                print(f"Error copying image: {e}")
                return

            new_item = {
                'title': title,
                'image_path': destination_path  # Updating path to image
            }
            self.wishlist_items.append(new_item)  # Adding new element to the list
            self.save_tasks()  # Saving to JSON
            self.add_items(new_item)  # Show new item in the UI
            add_window.destroy()  # Closing the add window
        else:
            print("Title can't be blank.")

    def display_tasks(self):
        """
        Show elements

        :return: None
        """
        for task in self.wishlist_items:
            self.add_items(task)  # Show elements

    def add_items(self, task):
        """
        Adds a new item to the wishlist interface.

        :param task: A dictionary containing the details of the task (e.g., title and image_path).
        :return: None
        """
        frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        frame.pack(fill=tk.X, padx=10, pady=5)

        # Loading image from path
        if 'image_path' in task:
            try:
                image_path = task['image_path']
                item_image = Image.open(image_path)
                item_image = item_image.resize((50, 50), Image.Resampling.LANCZOS)
                item_photo = ImageTk.PhotoImage(item_image)
                item_label = tk.Label(frame, image=item_photo, bg=INTERFACE['bg_color'])
                item_label.image = item_photo
                item_label.pack(side=tk.LEFT, padx=(0, 10))
            except Exception as e:
                print(f"Error loading image {image_path}: {e}")

        wishlist_item = tk.Label(frame, text=task['title'], bg=INTERFACE['bg_color'],
                                 font=WISHLIST['wishlist_item_font'])
        wishlist_item.pack(side=tk.LEFT)

        # Delete button
        delete_button = tk.Button(frame, text="Delete", bg=WISHLIST['delete_button_color'],
                                  command=lambda: self.remove_task(task, frame),
                                  font=WISHLIST['delete_edit_button_font'])
        delete_button.pack(side=tk.RIGHT, padx=5)
        delete_button.config(cursor="hand2")

        # Edit button
        edit_button = tk.Button(frame, text="Edit",
                                command=lambda: self.edit_task(task, frame),
                                font=WISHLIST['delete_edit_button_font'])
        edit_button.pack(side=tk.RIGHT, padx=5)
        edit_button.config(cursor="hand2")

    def remove_task(self, task, frame):
        """
        Removes a task from the wishlist.

        :param task: The task to be removed (contains the task details, e.g., title and image path).
        :param frame: The frame widget that contains the task UI elements.
        :return: None
        """
        try:
            # Remove the image file if it exists
            if 'image_path' in task and os.path.exists(task['image_path']):
                os.remove(task['image_path'])  # Delete the image file

            # Remove the task from the wishlist items list
            self.wishlist_items.remove(task)
            self.save_tasks()  # Save the updated wishlist to the JSON file

            # Destroy the frame widget to remove the task's UI from the interface
            frame.destroy()

        except Exception as e:
            print(f"Error while removing task: {e}")

    def edit_task(self, task, frame):
        """
        Opens an edit window for modifying a task's details (title and image).

        :param task: The task to be edited (contains the task details, e.g., title and image path).
        :param frame: The frame widget that contains the task UI elements.
        :return: None
        """
        edit_window = tk.Toplevel(self)
        edit_window.withdraw()
        edit_window.title("Edit")
        center_window_on_parent(self.main_window, edit_window, 375, 175)

        try:
            icon_image = Image.open(APP['icon_path'])  # Замените на ваш путь
            icon_photo = ImageTk.PhotoImage(icon_image)
            edit_window.iconphoto(False, icon_photo)  # Устанавливаем иконку окна
        except Exception as e:
            print(f"Icon load error: {e}")

        task_entry = tk.Entry(edit_window, font=WISHLIST['toplevel_windows_font'], width=40)
        task_entry.insert(0, task['title'])  # Adding current title
        task_entry.pack(pady=10)
        task_entry.bind("<Return>",
                        lambda event: self.save_task_changes(task, task_entry.get(), image_entry.get(),
                                                             edit_window, frame))

        image_entry = tk.Entry(edit_window, font=WISHLIST['toplevel_windows_font'], width=40)
        image_entry.insert(0, task.get('image_path', ''))  # Adding current path
        image_entry.pack(pady=10)
        image_entry.bind("<Return>",
                        lambda event: self.save_task_changes(task, task_entry.get(), image_entry.get(),
                                                             edit_window, frame))

        # Browse button
        browse_button = tk.Button(edit_window, text="Browse",
                                  command=lambda: browse_image(image_entry, edit_window),
                                  font=WISHLIST['browse_button_font'])
        browse_button.pack(pady=5)
        browse_button.config(cursor="hand2")

        # Save button
        save_button = tk.Button(edit_window, text="Save", font=WISHLIST['save_button_font'],
                                command=lambda: self.save_task_changes(task, task_entry.get(), image_entry.get(),
                                                                       edit_window, frame))
        save_button.pack(pady=5)
        save_button.config(cursor="hand2")

        edit_window.deiconify()

    def save_task_changes(self, task, new_title, new_image_path, edit_window, frame):
        """
        Saves the changes made to a task's title and image, updates the task display, and stores the changes in JSON.

        :param task: The task to be updated (contains the original task details).
        :param new_title: The new title for the task.
        :param new_image_path: The new path for the task's image.
        :param edit_window: The window where the user edits the task details.
        :param frame: The frame in the UI containing the task's current display.
        :return: None
        """
        # Save the changes to the task
        task['title'] = new_title
        old_path = task['image_path']
        task['image_path'] = new_image_path

        # If a new image is selected, copy it to the working directory
        if new_image_path and new_image_path != old_path:
            # Copy the image to the working directory
            destination_path = os.path.join(WISHLIST['dist_folder_path'], os.path.basename(new_image_path))

            # Check if a file with the same name already exists
            if os.path.exists(destination_path):
                messagebox.showerror("Error",
                                     f"File with title '{os.path.basename(new_image_path)}' already exists.\nPlease, rename your file.")
                edit_window.lift()
                return

            try:
                # Remove the old image from the directory if it exists
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)  # Remove the old image
                    except Exception as e:
                        print(f"Error removing old image: {e}")

                # Copy the new image
                shutil.copy(new_image_path, destination_path)
                task['image_path'] = destination_path  # Update the path
            except Exception as e:
                print(f"Error copying image: {e}")
                return

        # Save the updated task list to the JSON file
        self.save_tasks()

        # Close the edit window
        edit_window.destroy()

        # Update the task's display in the interface to reflect the changes
        self.update_task_display(task, frame)

    def update_task_display(self, task, frame):
        """
        Updates the task display in the user interface after any changes. This includes refreshing the image and title,
        and adding the delete and edit buttons.

        :param task: The task to be updated (contains the task's title and image path).
        :param frame: The frame that holds the task display in the UI.
        :return: None
        """
        for widget in frame.winfo_children():
            widget.destroy()

        # ОShow image if exists
        if task['image_path'] and os.path.exists(task['image_path']):
            img = Image.open(task['image_path'])
            img = img.resize((WISHLIST['image_height'], WISHLIST['image_width']),
                             Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            img_label = tk.Label(frame, image=tk_img)
            img_label.image = tk_img
            img_label.pack(side=tk.LEFT)

        # Update title
        title_label = tk.Label(frame, text=task['title'], font=WISHLIST['wishlist_item_font'])
        title_label.pack(side=tk.LEFT)

        # Delete button
        delete_button = tk.Button(frame, text="Delete", bg=WISHLIST['delete_button_color'],
                                  command=lambda: self.remove_task(task, frame),
                                  font=WISHLIST['delete_edit_button_font'])
        delete_button.pack(side=tk.RIGHT, padx=5)
        delete_button.config(cursor="hand2")

        # Edit button
        edit_button = tk.Button(frame, text="Edit", command=lambda: self.edit_task(task, frame),
                                font=WISHLIST['delete_edit_button_font'])
        edit_button.pack(side=tk.RIGHT, padx=5)
        edit_button.config(cursor="hand2")

    def navigate_to_lists_for_life(self):
        """
        Returning to page #Lists_for_life.

        :return: None
        """
        self.main_window.show_tab_content("lists_for_life")

    def save_tasks(self):
        """
        Save wishlist to JSON

        :return: None
        """
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump({'wishlist': self.wishlist_items}, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving to JSON: {e}")
