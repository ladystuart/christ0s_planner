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
        image_entry.config(state='normal')
        image_entry.delete(0, tk.END)
        image_entry.insert(0, file_path)
        image_entry.config(state='readonly')

    window.deiconify()


async def load_tasks_from_server():
    """
    Asynchronously fetches the wishlist items from the server.

    Makes a GET request to the server to retrieve the list of wishlist items. If the request is successful (status code 200),
    the function returns the response as a JSON object. In case of failure, an error message is printed, and an empty list is returned.

    Returns:
        list: A list of wishlist items fetched from the server in JSON format, or an empty list if the request fails.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{SERVER_URL}/get_wishlist_items", ssl=SSL_ENABLED) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Failed to fetch tasks: {response.status}")
                return []


async def fetch_image(image_path):
    """
    Fetch image from the server.

    :param image_path: The path to the image on the server.
    :return: The image object.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SERVER_URL}/get_image/{image_path}", ssl=SSL_ENABLED) as response:
                if response.status == 200:
                    img_data = await response.read()
                    image = Image.open(BytesIO(img_data))
                    return image
                else:
                    raise Exception(f"Error loading image from {image_path}: {response.status}")
    except Exception as e:
        print(f"Failed to fetch image: {e}")
        return None


class Wishlist(tk.Frame):
    """
    The Wishlist class is responsible for creating the interface of the 'Wishlist' tab.
    It includes a wishlist page with functionality for users to delete, add, and edit items.
    """
    def __init__(self, parent, main_window):
        """
        Initializes the Wishlist class.

        :param parent: Parent container where the Wishlist frame will be placed.
        :param main_window: Reference to the main window of the application.
        """
        super().__init__(parent)
        self.image_load_count = 0
        self.parent = parent
        self.main_window = main_window
        self.configure(bg=INTERFACE['bg_color'])  # Background color
        self.main_window.disable_buttons()
        self.wishlist_items = asyncio.run(load_tasks_from_server())  # Load tasks from server

        self.clickable_label = add_source_label_lists_for_life(
            self,  # Parent element
            icon_path_1=ICONS_PATHS['lists_for_life'],
            clickable_text="#Lists_for_life /",
            click_command=self.navigate_to_lists_for_life,
            icon_path_2=ICONS_PATHS['wishlist'],
            text=PAGES_NAMES['wishlist']
        )
        self.clickable_label["state"] = "disabled"

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

        self.add_button()

        if self.wishlist_items:
            self.display_tasks()
        else:
            self.main_window.enable_buttons()
            self.clickable_label["state"] = "normal"

    def add_button(self):
        # Add button
        add_button = tk.Button(self, text="Add item", bg=WISHLIST['add_button_color'], command=self.open_add_item_window,
                               font=WISHLIST['add_button_font'])
        add_button.pack(pady=10)
        add_button.config(cursor="hand2")

    def open_add_item_window(self):
        """
        Opens a pop-up window to add a new item to the wishlist. The user can provide a title and an image path.

        :return: None
        """
        add_window = tk.Toplevel(self)
        add_window.withdraw()
        add_window.title("Add new element")
        add_window.iconbitmap(APP['icon_path'])

        center_window_on_parent(self.main_window, add_window, 375, 225)

        task_label = tk.Label(add_window, text="Title", font=WISHLIST['toplevel_windows_font'])
        task_label.pack(pady=(10, 0))

        task_entry = tk.Entry(add_window, font=WISHLIST['toplevel_windows_font'], width=40)
        task_entry.pack(pady=(0, 10))
        task_entry.insert(0, "")
        task_entry.bind("<Return>",
                        lambda event: asyncio.run(self.add_item(task_entry.get(), image_entry.get(), add_window)))

        ToolTip(task_entry, "Enter title")

        image_label = tk.Label(add_window, text="Path to the image", font=WISHLIST['toplevel_windows_font'])
        image_label.pack(pady=(10, 0))

        image_entry = tk.Entry(add_window, font=WISHLIST['toplevel_windows_font'], width=40)
        image_entry.pack(pady=(0, 10))
        image_entry.insert(0, "")
        image_entry.bind("<Return>",
                         lambda event: asyncio.run(self.add_item(task_entry.get(), image_entry.get(), add_window)))

        ToolTip(image_entry, "Click before pressing the \"Browse\" button")

        # Browse button
        browse_button = tk.Button(add_window, text="Browse",
                                  command=lambda: browse_image(image_entry, add_window),
                                  font=WISHLIST['browse_button_font'])
        browse_button.pack(pady=5)
        browse_button.config(cursor="hand2")

        # Save button
        add_button = tk.Button(add_window, text="Save", font=WISHLIST['save_button_font'],
                               command=lambda: asyncio.run(
                                   self.add_item(task_entry.get(), image_entry.get(), add_window)))
        add_button.pack(pady=5)
        add_button.config(cursor="hand2")

        add_window.deiconify()

    async def add_item(self, title, image_path, add_window):
        """
        Adds a new item to the wishlist with the provided title and image.

        Args:
            title (str): The title of the wishlist item.
            image_path (str): The local file path to the image associated with the wishlist item.
            add_window (tkinter.Toplevel): The window to be closed after the item is added.

        Returns:
            None

        This function performs several steps:
            1. Validates the input to ensure the title is not blank and an image file is selected.
            2. Ensures that the title and image path are unique in the wishlist.
            3. Uploads the image file to the server.
            4. Receives the filename of the uploaded image from the server.
            5. Sends the title and image path to the server to store in the wishlist database.
            6. Updates the local wishlist and interface with the new item.
            7. Closes the 'add_window' after the item is successfully added.

        If any step fails (e.g., duplicate title or image, upload failure, or database error), an error message is shown.
        """
        if not title.strip():
            messagebox.showerror("Error", "Title can't be blank!")
            add_window.lift()
            return

        if not image_path.strip():
            messagebox.showerror("Error", "Please select an image file!")
            add_window.lift()
            return

        if not os.path.exists(image_path):
            messagebox.showerror("Error", f"The selected image file was not found:\n{image_path}")
            add_window.lift()
            return

        # Adjust the image path
        image_name_check = os.path.basename(image_path.strip())  # Extract the image name (e.g., 'ava.jpg')
        image_name_check = os.path.join(WISHLIST['dist_folder_path'],
                                        image_name_check)  # Combine it with dist_folder_path
        image_name_check = image_name_check.replace("\\", "/")  # Ensure the correct format for file paths

        # Check if the title or image path already exists in the wishlist
        for item in self.wishlist_items:
            if item['title'] == title:
                messagebox.showerror("Error", "This title already exists in your wishlist!")
                add_window.lift()
                return
            if item['image_path'] == image_name_check:
                messagebox.showerror("Error", "Image with the same title already exists!\n"
                                              "Please, rename your image!")
                add_window.lift()
                return

        image_filename = None
        try:
            async with aiohttp.ClientSession() as session:
                with open(image_path, "rb") as img_file:
                    data = aiohttp.FormData()
                    data.add_field("file", img_file, filename=os.path.basename(image_path))

                    async with session.post(f"{SERVER_URL}/upload_image", data=data, ssl=SSL_ENABLED) as response:
                        response.raise_for_status()
                        image_filename = (await response.json()).get("filename")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload image: {e}")
            return

        # Path to image on server
        image_server_path = os.path.join(WISHLIST['dist_folder_path'], image_filename)
        image_server_path = image_server_path.replace("\\", "/")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{SERVER_URL}/add_wishlist_item",
                                        json={"title": title, "image_path": image_server_path},
                                        ssl=SSL_ENABLED) as response:
                    response.raise_for_status()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add item: {e}")
            return

        new_item = {"title": title, "image_path": image_server_path}
        self.wishlist_items.append(new_item)
        await self.add_items(new_item)
        add_window.destroy()

    def display_tasks(self):
        """
        Show elements

        :return: None
        """
        for task in self.wishlist_items:
            asyncio.run(self.add_items(task))  # Show elements

    async def add_items(self, task):
        """
        Adds a new item to the wishlist interface, asynchronously fetching image from the server.

        :param task: A dictionary containing the details of the task (e.g., title and image_path).
        :return: None
        """
        frame = tk.Frame(self, bg=INTERFACE['bg_color'])
        frame.pack(fill=tk.X, padx=10, pady=5)

        # Loading image from server or local path asynchronously
        if 'image_path' in task:
            try:
                image_path = os.path.basename(task['image_path'])

                item_image = await fetch_image(image_path)

                if item_image:
                    # Resize the image and display it
                    item_image = item_image.resize((50, 50), Image.Resampling.LANCZOS)
                    item_photo = ImageTk.PhotoImage(item_image)

                    item_label = tk.Label(frame, image=item_photo, bg=INTERFACE['bg_color'])
                    item_label.image = item_photo
                    item_label.pack(side=tk.LEFT, padx=(0, 10))

                    self.image_load_count += 1
                else:
                    print(f"Failed to load image for {task['title']}")
            except Exception as e:
                print(f"Error loading image {image_path}: {e}")
        else:
            # If no image, still increment count to avoid blocking
            self.image_load_count += 1

        # Title of the wishlist item
        wishlist_item = tk.Label(frame, text=task['title'], bg=INTERFACE['bg_color'],
                                 font=WISHLIST['wishlist_item_font'])
        wishlist_item.pack(side=tk.LEFT)

        # Delete button
        delete_button = tk.Button(frame, text="Delete", bg=WISHLIST['delete_button_color'],
                                  command=lambda: asyncio.run(self.remove_task(task, frame)),
                                  font=WISHLIST['delete_edit_button_font'])
        delete_button.pack(side=tk.RIGHT, padx=5)
        delete_button.config(cursor="hand2")

        # Edit button
        edit_button = tk.Button(frame, text="Edit",
                                command=lambda: self.edit_task(task, frame),
                                font=WISHLIST['delete_edit_button_font'])
        edit_button.pack(side=tk.RIGHT, padx=5)
        edit_button.config(cursor="hand2")

        if self.image_load_count == len(self.wishlist_items):
            self.main_window.enable_buttons()
            self.clickable_label["state"] = "normal"

    async def remove_task(self, task, frame):
        """
        Removes a task from the wishlist, deletes the image file locally and remotely, and removes the task from the server.

        :param task: The task to be removed (contains the task details, e.g., title and image path).
        :param frame: The frame widget that contains the task UI elements.
        :return: None
        """
        try:
            # Send request to remove the task and its associated image from the server
            async with aiohttp.ClientSession() as session:
                task_data = {"title": task['title'], "image_path": task['image_path']}
                async with session.post(f"{SERVER_URL}/remove_wishlist_item", json=task_data, ssl=SSL_ENABLED) as response:
                    response.raise_for_status()

            # Remove the image file locally if it exists
            if 'image_path' in task and os.path.exists(task['image_path']):
                os.remove(task['image_path'])  # Delete the image file

            # Remove the task from the wishlist items list
            self.wishlist_items.remove(task)

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
            icon_image = Image.open(APP['icon_path'])
            icon_photo = ImageTk.PhotoImage(icon_image)
            edit_window.iconphoto(False, icon_photo)
        except Exception as e:
            print(f"Icon load error: {e}")

        task_entry = tk.Entry(edit_window, font=WISHLIST['toplevel_windows_font'], width=40)
        task_entry.insert(0, task['title'])  # Adding current title
        task_entry.pack(pady=10)
        task_entry.bind("<Return>",
                        lambda event: asyncio.run(self.save_task_changes(task, task_entry.get(), image_entry.get(),
                                                                         edit_window, frame)))

        image_entry = tk.Entry(edit_window, font=WISHLIST['toplevel_windows_font'], width=40)
        image_entry.insert(0, task.get('image_path', ''))  # Adding current path
        image_entry.config(state='readonly')
        image_entry.pack(pady=10)
        image_entry.bind("<Return>",
                         lambda event: asyncio.run(self.save_task_changes(task, task_entry.get(), image_entry.get(),
                                                                          edit_window, frame)))

        # Browse button
        browse_button = tk.Button(edit_window, text="Browse",
                                  command=lambda: browse_image(image_entry, edit_window),
                                  font=WISHLIST['browse_button_font'])
        browse_button.pack(pady=5)
        browse_button.config(cursor="hand2")

        # Save button
        save_button = tk.Button(edit_window, text="Save", font=WISHLIST['save_button_font'],
                                command=lambda: asyncio.run(
                                    self.save_task_changes(task, task_entry.get(), image_entry.get(),
                                                           edit_window, frame)))
        save_button.pack(pady=5)
        save_button.config(cursor="hand2")

        edit_window.deiconify()

    async def save_task_changes(self, task, new_title, new_image_path, edit_window, frame):
        """
        Saves the changes made to a task's title and image in the wishlist.

        Args:
            task (dict): The current task that is being edited. Contains the original title and image path.
            new_title (str): The new title for the task.
            new_image_path (str): The new local file path for the image associated with the task.
            edit_window (tkinter.Toplevel): The window to be closed after the changes are saved.
            frame (tkinter.Frame): The frame where the task is displayed, which will be updated with the new task details.

        Returns:
            None

        This function performs the following steps:
            1. Validates that the new title and image path are unique in the wishlist to prevent duplicates.
            2. If the image has been changed, uploads the new image to the server.
            3. Sends a request to the server to update the task data in the wishlist database.
            4. Updates the local task data with the new title and image path.
            5. Updates the UI with the changes by calling the `update_task_display` method.
            6. Closes the `edit_window` if the task was successfully updated.

        If any step fails (e.g., duplicate title, image upload failure, or database update error), an error message is displayed using a message box (`messagebox.showerror`).
        """
        image_filename = os.path.basename(new_image_path)
        new_image_server_path = os.path.join(WISHLIST['dist_folder_path'], image_filename).replace("\\", "/")
        if not image_filename.strip():
            messagebox.showerror("Error", "Image path cannot be empty!")
            edit_window.lift()
            return

        if not new_title.strip():
            messagebox.showerror("Error", "Task title cannot be empty!")
            edit_window.lift()
            return

        if new_image_server_path != task['image_path']:
            if not os.path.exists(new_image_path):
                messagebox.showerror("Error", f"The selected image file was not found:\n{new_image_path}")
                edit_window.lift()
                return

        if task['title'] == new_title:
            messagebox.showerror("Error", "You didn't change the title!")
            edit_window.lift()
            return

        for item in self.wishlist_items:
            if item['title'] == new_title:
                messagebox.showerror("Error", "This title already exists in your wishlist!")
                edit_window.lift()
                return
            if item['image_path'] == new_image_server_path and item['image_path'] != task['image_path']:
                messagebox.showerror("Error", "Image with the same title already exists!\n"
                                              "Please, rename your image!")
                edit_window.lift()
                return

        try:
            data = {
                "new_title": new_title,
                "old_title": task["title"],
                "old_image_path": task["image_path"],
                "new_image_path": new_image_server_path
            }

            async with aiohttp.ClientSession() as session:
                if new_image_path != task["image_path"]:
                    if os.path.exists(new_image_path):
                        with open(new_image_path, "rb") as image_file:
                            form_data = aiohttp.FormData()
                            form_data.add_field("file", image_file, filename=os.path.basename(new_image_path))

                            async with session.post(f"{SERVER_URL}/upload_image", data=form_data,
                                                    ssl=SSL_ENABLED) as response:
                                response_text = await response.text()
                                if response.status != 200:
                                    raise Exception(f"Failed to upload image: {response_text}")
                    else:
                        raise FileNotFoundError(f"Image file '{new_image_path}' not found.")

                form_data = aiohttp.FormData()
                form_data.add_field("new_title", new_title)
                form_data.add_field("old_title", task["title"])
                form_data.add_field("old_image_path", task["image_path"])
                form_data.add_field("new_image_path",
                                    new_image_server_path if new_image_path != task["image_path"] else task[
                                        "image_path"])

                async with session.post(f"{SERVER_URL}/update_wishlist_item", json=data, ssl=SSL_ENABLED) as response:
                    response_text = await response.text()

                    if response.status == 200:
                        task["title"] = new_title
                        if new_image_path != task["image_path"]:
                            task["image_path"] = new_image_server_path

                        self.update_task_display(task, frame)
                        if edit_window.winfo_exists():
                            edit_window.destroy()
                    else:
                        print(f"Failed to update task: {response_text}")
                        messagebox.showerror("Error", f"Failed to update task: {response_text}")
                        edit_window.lift()

        except Exception as e:
            print(f"Error communicating with the server: {str(e)}")
            messagebox.showerror("Error", f"Error communicating with the server: {str(e)}")
            edit_window.lift()

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
        if task['image_path']:
            try:
                image_url = f"{SERVER_URL}/get_image/{os.path.basename(task['image_path'])}"
                response = requests.get(image_url, verify=VERIFY_ENABLED)
                if response.status_code == 200:
                    img_data = BytesIO(response.content)
                    img = Image.open(img_data)
                    img = img.resize((WISHLIST['image_height'], WISHLIST['image_width']), Image.Resampling.LANCZOS)
                    tk_img = ImageTk.PhotoImage(img)

                    img_label = tk.Label(frame, image=tk_img)
                    img_label.image = tk_img
                    img_label.pack(side=tk.LEFT)
            except Exception as e:
                print(f"Error loading image from server: {e}")

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

