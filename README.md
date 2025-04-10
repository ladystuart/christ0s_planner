# Christ0$

Christ0$ is a Python application with a graphical user interface created using tkinter. 
The main window of the application contains a sidebar with tabs for various functions, including useful links, annual plans, lists and work-related tasks.
Christ0$ is a planner program. 

> ⚠️ **You have to set up a server before using the client.**

## Main Features

- **Main window** with a sidebar displaying tabs for different categories
- Support for dynamic content loading onto the central canvas for each tab
- Support for horizontal scrolling with the mouse for easier navigation
- Support for custom icons and images for tabs

## Project structure

```bash
├── data
│   ├── lists_for_life
│   ├── tabs
│   └── useful_links
├── config
│   ├── imports.py
│   ├── utils.py
│   ├── tooltip.py
│   └── settings.py
├── src
│   └── .py files
├── main.py
├── app_icon.ico
├── icon.ico
├── screenshots
├── .gitignore
├── LICENSE.txt
└── README.md
```

## Screenshots

Welcome window:

![Welcome window](/screenshots/main_window.png)
*Image 1. Welcome window*

Use buttons on the left tab to navigate through the program.

Main tabs:

![Useful links tab](/screenshots/useful_links_tab.png)
*Image 2. Useful links tab*

![Lists for life tab](/screenshots/lists_for_life_tab.png)
*Image 3. #Lists_for_life tab*

![Yearly plans tab](/screenshots/yearly_plans_tab.png)
*Image 4. Yearly plans tab*

![Work tab](/screenshots/work_tab.png)
*Image 5. Work tab*

## Installation


### 1. Set up the server

Follow the instructions in the [server setup guide](../backend/README.md).

### 2. Clone the repository:
   ```bash
   git clone https://gitlab.com/ladystuart/planner.git
   cd planner
   
   # Navigate into the project directory
   cd repository-name

   # Install required packages
   pip install -r requirements.txt
   ```

### 3. Create setup file:
   ```bash
   pip install pyinstaller
   
   # Dist folder
   pyinstaller --onefile --windowed --icon=icon.ico --add-data "src;src" --add-data "data;data" --add-data "config;config" main.py

   # Delete unwanted files
   # Copy icons, data and src folders to Dist
   # Use .iss file to configure the setupper
   ```
## IP

> ⚠️ **Your IP is in the file [config/settings.py](../frontend/config/settings.py) -> SERVER_URL. Make sure you change it before using the app!**

## Errors

- If a **red "Disconnected"** message appears in the bottom left corner of the interface, it indicates a problem with the server connection. Please check the network connection or the server's status.


## Resources used

- [ChatGPT](https://chat.openai.com/)
- [DeepSeek](https://www.deepseek.com/)
- [Icons](https://icons8.com/icons)
- [Stack Overflow](https://stackoverflow.com/)
- [Notion](https://www.notion.so/)

## License
This project is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.
Created by Lady Stuart.

You may use, share, and modify the code under the terms of the [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/).

## Setup

Links to YouTube video on usage (local version used) and exe installation file
- [Quick Tour of Christ0$](https://www.youtube.com/watch?v=y4QgQ3A3YJw&feature=youtu.be)
- [Exe download](https://drive.google.com/file/d/1_sMcZ3WBRUrjJwHVhFl-F52EtoIHfvTM/view?usp=sharing)