import json
import sys
import platform
import os
from datetime import datetime

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(500, 400)
        Dialog.setAutoFillBackground(True)
        Dialog.setSizeGripEnabled(True)

        # Main Layout
        self.mainLayout = QtWidgets.QVBoxLayout(Dialog)

        # Layout for header (with search bar on the left and settings button on the right)
        self.headerLayout = QtWidgets.QHBoxLayout()

        # Create the search bar and add it to the header layout (left side)
        self.searchBar = QtWidgets.QLineEdit()
        self.searchBar.setPlaceholderText("Search tasks...")
        self.searchBar.setObjectName("searchBar")
        self.searchBar.setClearButtonEnabled(True)
        self.headerLayout.addWidget(self.searchBar)

        # Add a stretch to push the settings button to the right
        self.headerLayout.addStretch(1)

        # Create the settings button (right side)
        self.settingsButton = QtWidgets.QPushButton(self)
        self.settingsButton.setIcon(
            QtGui.QIcon("./icons/setting_icon.png")
        )  # Path to the gear icon
        self.settingsButton.setIconSize(QtCore.QSize(90, 90))  # Smaller icon size

        # Make the settings button circular
        self.settingsButton.setStyleSheet(
            """
            QPushButton {
                border-radius: 25px; 
                background-color: #f0f0f0;
                border: none;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """
        )

        self.settingsButton.setFixedSize(50, 50)  # Set the button size
        self.settingsButton.clicked.connect(self.openSettingsMenu)

        # Add settings button to header layout (right side)
        self.headerLayout.addWidget(self.settingsButton)

        # Add header layout to the main layout
        self.mainLayout.addLayout(self.headerLayout)

        # Add a thin line under the header
        self.headerLine = QtWidgets.QFrame(Dialog)
        self.headerLine.setFrameShape(QtWidgets.QFrame.HLine)
        self.headerLine.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.mainLayout.addWidget(self.headerLine)

        # Continue with the rest of the UI setup...

        self.inputLayout = QtWidgets.QHBoxLayout()
        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.setObjectName("lineEdit")
        self.inputLayout.addWidget(self.lineEdit)
        self.addTaskButton = QtWidgets.QPushButton()
        self.addTaskButton.setObjectName("addTaskButton")
        self.inputLayout.addWidget(self.addTaskButton)
        self.mainLayout.addLayout(self.inputLayout)

        # Task list layout
        self.taskListLayout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel()
        self.label.setObjectName("label")
        self.taskListLayout.addWidget(self.label)
        self.taskList = QtWidgets.QListWidget()
        self.taskList.setObjectName("taskList")
        self.taskListLayout.addWidget(self.taskList)
        self.mainLayout.addLayout(self.taskListLayout)

        # Status and date layout
        self.statusLayout = QtWidgets.QHBoxLayout()
        self.statusComboBox = QtWidgets.QComboBox()
        self.statusComboBox.setObjectName("statusComboBox")
        self.statusComboBox.addItem("Pending")
        self.statusComboBox.addItem("Completed")
        self.statusLayout.addWidget(self.statusComboBox)
        self.label_2 = QtWidgets.QLabel()
        self.label_2.setObjectName("label_2")
        self.statusLayout.addWidget(self.label_2)
        self.mainLayout.addLayout(self.statusLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def keyPressEvent(self, event):
        # Detect Enter key press and prevent it from triggering settings button click
        if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
            # Prevent Enter key from triggering settings button
            event.accept()  # Consume the event and stop it from propagating further
        else:
            super().keyPressEvent(event)  # Allow other key presses to pass through

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "TODO"))
        self.addTaskButton.setText(_translate("Dialog", "Add Task"))
        self.label.setText(_translate("Dialog", "Task List"))
        self.label_2.setText(_translate("Dialog", ""))


class MainApp(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.current_theme = "Light"  # Default theme

        # Set the tasks file path
        self.tasks_file = self.get_tasks_file_path()

        # Define colors for each theme and task status
        self.theme_colors = {
            "Light": {
                "Pending": {
                    "background": QtGui.QColor("lightyellow"),
                    "foreground": QtGui.QColor("orange"),
                },
                "Completed": {
                    "background": QtGui.QColor("lightgreen"),
                    "foreground": QtGui.QColor("green"),
                },
            },
            "Dark": {
                "Pending": {
                    "background": QtGui.QColor(66, 66, 66),
                    "foreground": QtGui.QColor(255, 165, 0),  # Orange
                },
                "Completed": {
                    "background": QtGui.QColor(34, 139, 34),  # Dark green
                    "foreground": QtGui.QColor(144, 238, 144),  # Light green
                },
            },
        }

        self.setupFunctions()  # Initialize functions after setting the theme
        self.updateDateLabel()
        self.allTasks = []  # Store all tasks for search functionality
        self.loadTasks()  # Ensure tasks are loaded when the dialog is created


    def get_tasks_file_path(self):
        """
        Returns the appropriate path for tasks.json based on the operating system.
        """
        app_name = "DailyTasker"  # Application name
        system = platform.system()  # Detect operating system

        if system == "Windows":
            base_path = os.getenv("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
        elif system == "Darwin":  # macOS
            base_path = os.path.expanduser("~/Library/Application Support")
        elif system == "Linux":
            base_path = os.path.expanduser("~/.config")
        else:
            base_path = os.path.expanduser("~")  # Default to home directory

        # Final directory for the application
        app_directory = os.path.join(base_path, app_name)

        # Create the directory if it doesn't exist
        os.makedirs(app_directory, exist_ok=True)

        # Return the full path to tasks.json
        return os.path.join(app_directory, "tasks.json")



    def loadTasks(self):
        tasks = self.loadTasksFromFile()
        self.taskList.clear()
        self.allTasks = []  # Clear previous tasks for search

        current_date = datetime.now().strftime("%Y-%m-%d")
        if current_date in tasks:
            for task in tasks[current_date]:
                item_text = task["text"]  # Only the task text, without the status
                item = QtWidgets.QListWidgetItem(item_text)

                # Set color based on status and current theme
                status = task["status"]
                colors = self.theme_colors[self.current_theme][status]
                item.setBackground(colors["background"])
                item.setForeground(colors["foreground"])

                self.taskList.addItem(item)
                self.allTasks.append(
                    item_text
                )  # Store task text without status for search

    def setDarkMode(self):
        dark_palette = QtGui.QPalette()
        dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
        dark_palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(42, 42, 42))
        dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(66, 66, 66))
        dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        dark_palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))

        self.setPalette(dark_palette)

        # Update task list colors for dark mode
        self.loadTasks()  # Reload tasks with new color scheme

    def setLightMode(self):
        light_palette = QtGui.QPalette()
        light_palette.setColor(QtGui.QPalette.Window, QtCore.Qt.white)
        light_palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.black)
        light_palette.setColor(QtGui.QPalette.Base, QtCore.Qt.white)
        light_palette.setColor(
            QtGui.QPalette.AlternateBase, QtGui.QColor(240, 240, 240)
        )
        light_palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
        light_palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.black)
        light_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.black)
        light_palette.setColor(QtGui.QPalette.Button, QtCore.Qt.white)
        light_palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.black)
        light_palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        light_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))

        self.setPalette(light_palette)

        # Update task list colors for light mode
        self.loadTasks()  # Reload tasks with new color scheme

    def changeTheme(self, selected_theme):
        if selected_theme == "Dark Mode":
            self.setDarkMode()
            self.current_theme = "Dark"
        else:
            self.setLightMode()
            self.current_theme = "Light"

        self.updateTaskColors()

    def setupFunctions(self):
        self.addTaskButton.clicked.connect(self.addTask)
        self.taskList.itemClicked.connect(self.updateStatusComboBox)
        self.statusComboBox.currentIndexChanged.connect(self.changeTaskStatus)
        self.searchBar.textChanged.connect(self.searchTasks)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateDateLabel)
        self.timer.start(1000)

    def updateDateLabel(self):
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.label_2.setText(current_date)

    def updateTaskColors(self):
        """
        Update colors of all tasks in the task list based on the current theme and their status.
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        tasks = self.loadTasksFromFile()

        if current_date in tasks:
            for index in range(self.taskList.count()):
                item = self.taskList.item(index)
                task_text = item.text()
                for task in tasks[current_date]:
                    if task["text"] == task_text:
                        # Update color based on task status and theme
                        status = task["status"]
                        colors = self.theme_colors[self.current_theme][status]
                        item.setBackground(colors["background"])
                        item.setForeground(colors["foreground"])


    def keyPressEvent(self, event):
        # Detect Enter key press and prevent it from triggering settings button click
        if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
            # Prevent Enter key from triggering settings button
            event.accept()  # Consume the event and stop it from propagating further
        else:
            super(MainApp, self).keyPressEvent(
                event
            )  # Allow other key presses to pass through

    def addTask(self):
        task_text = self.lineEdit.text().strip()
        if task_text:
            current_date = datetime.now().strftime("%Y-%m-%d")
            tasks = self.loadTasksFromFile()

            if current_date not in tasks:
                tasks[current_date] = []

            if any(task["text"] == task_text for task in tasks[current_date]):
                QtWidgets.QMessageBox.warning(
                    self, "Error", "This task has already been added for today."
                )
                return

            tasks[current_date].append({"text": task_text, "status": "Pending"})

            self.saveTasksToFile(tasks)

            self.loadTasks()

            self.lineEdit.clear()

    def updateStatusComboBox(self, item):
        current_date = datetime.now().strftime("%Y-%m-%d")
        tasks = self.loadTasksFromFile()

        if current_date in tasks:
            selected_task_text = item.text()
            for task in tasks[current_date]:
                if task["text"] == selected_task_text:
                    # Setting ComboBox based on task status
                    if task["status"] == "Completed":
                        self.statusComboBox.setCurrentIndex(1)
                    else:
                        self.statusComboBox.setCurrentIndex(0)
                    break

        # Update the color of the selected task.
        self.updateTaskColor(item)  # Calling the color update method

    def changeTaskStatus(self):
        selected_item = self.taskList.currentItem()
        if selected_item:
            current_date = datetime.now().strftime("%Y-%m-%d")
            tasks = self.loadTasksFromFile()

            if current_date in tasks:
                selected_task_text = selected_item.text()

                for task in tasks[current_date]:
                    if task["text"] == selected_task_text:
                        task["status"] = self.statusComboBox.currentText()
                        self.saveTasksToFile(tasks)

                        updated_text = task["text"]
                        selected_item.setText(updated_text)

                        # Update item color based on status and current theme
                        self.updateTaskColor(
                            selected_item, task
                        )  # Update color for the selected item

                        break

    def updateTaskColor(self, item, task=None):
        """
        Update task color based on current status and theme.
        """
        if task is None:
            # If the task is not entered specifically, we load it from the list.
            current_date = datetime.now().strftime("%Y-%m-%d")
            tasks = self.loadTasksFromFile()
            if current_date in tasks:
                selected_task_text = item.text()
                for t in tasks[current_date]:
                    if t["text"] == selected_task_text:
                        task = t
                        break

        # If the task is specified, we get its status.
        if task:
            status = task["status"]
            # Get colors from the color palette based on the current status and theme
            colors = self.theme_colors[self.current_theme][status]
            item.setBackground(colors["background"])
            item.setForeground(colors["foreground"])

    def searchTasks(self):
        query = self.searchBar.text().strip().lower()
        self.taskList.clear()  # Clear the task list

        tasks = self.loadTasksFromFile()
        current_date = datetime.now().strftime("%Y-%m-%d")
        if current_date in tasks:
            for task in tasks[current_date]:
                task_text = task["text"]
                if query in task_text.lower():
                    item = QtWidgets.QListWidgetItem(task_text)
                    # Adjust color based on situation
                    colors = self.theme_colors[self.current_theme][task["status"]]
                    item.setBackground(colors["background"])
                    item.setForeground(colors["foreground"])
                    self.taskList.addItem(item)

    def loadTasksFromFile(self):
        """
        Load tasks from JSON file.
        """
        try:
            with open(self.tasks_file, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def saveTasksToFile(self, tasks):
        """
        Save tasks to JSON file.
        """
        with open(self.tasks_file, "w") as file:
            json.dump(tasks, file, indent=4)

    def openSettingsMenu(self):
        settings_dialog = QtWidgets.QDialog(self)
        settings_dialog.setWindowTitle("Settings")
        settings_layout = QtWidgets.QVBoxLayout(settings_dialog)

        theme_combobox = QtWidgets.QComboBox()
        theme_combobox.addItems(["Light Mode", "Dark Mode"])
        theme_combobox.setCurrentText(self.current_theme)
        theme_combobox.currentIndexChanged.connect(
            lambda: self.changeTheme(theme_combobox.currentText())
        )

        settings_layout.addWidget(theme_combobox)
        settings_dialog.exec_()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()  # Window display
    sys.exit(app.exec_())
