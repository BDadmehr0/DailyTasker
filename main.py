import json
import os
import platform
import sys
from datetime import datetime

from PyQt5 import QtCore, QtGui, QtWidgets  # type: ignore


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(500, 400)
        Dialog.setAutoFillBackground(True)
        Dialog.setSizeGripEnabled(True)

        # Main Layout
        self.mainLayout = QtWidgets.QVBoxLayout(Dialog)

        # Header Layout
        self.headerLayout = self._createHeaderLayout()
        self.mainLayout.addLayout(self.headerLayout)

        # Thin line under the header
        self.headerLine = QtWidgets.QFrame(Dialog)
        self.headerLine.setFrameShape(QtWidgets.QFrame.HLine)
        self.headerLine.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.mainLayout.addWidget(self.headerLine)

        # Input Layout for Task
        self.inputLayout = self._createInputLayout()
        self.mainLayout.addLayout(self.inputLayout)

        # Task List Layout
        self.taskListLayout = self._createTaskListLayout()
        self.mainLayout.addLayout(self.taskListLayout)

        # Status Layout
        self.statusLayout = self._createStatusLayout()
        self.mainLayout.addLayout(self.statusLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def _createHeaderLayout(self):
        headerLayout = QtWidgets.QHBoxLayout()

        # Search Bar
        self.searchBar = QtWidgets.QLineEdit()
        self.searchBar.setPlaceholderText("Search tasks...")
        self.searchBar.setObjectName("searchBar")
        self.searchBar.setClearButtonEnabled(True)
        headerLayout.addWidget(self.searchBar)

        # Add Stretch
        headerLayout.addStretch(1)

        # Settings Button
        self.settingsButton = self._createSettingsButton()
        headerLayout.addWidget(self.settingsButton)

        return headerLayout

    def _createSettingsButton(self):
        settingsButton = QtWidgets.QPushButton(self)
        settingsButton.setIcon(QtGui.QIcon("./icons/setting_icon.png"))
        settingsButton.setIconSize(QtCore.QSize(90, 90))
        settingsButton.setStyleSheet(
            """
            QPushButton { border-radius: 25px; background-color: #f0f0f0; border: none; }
            QPushButton:hover { background-color: #e0e0e0; }
            """
        )
        settingsButton.setFixedSize(50, 50)
        settingsButton.clicked.connect(self.openSettingsMenu)
        return settingsButton

    def _createInputLayout(self):
        inputLayout = QtWidgets.QHBoxLayout()

        # Input Field for adding task
        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.setObjectName("lineEdit")
        inputLayout.addWidget(self.lineEdit)

        # Add Task Button
        self.addTaskButton = QtWidgets.QPushButton("Add Task")
        self.addTaskButton.setObjectName("addTaskButton")
        inputLayout.addWidget(self.addTaskButton)

        # Delete Task Button
        self.deleteTaskButton = QtWidgets.QPushButton("Delete Task")
        self.deleteTaskButton.setObjectName("deleteTaskButton")
        inputLayout.addWidget(self.deleteTaskButton)

        return inputLayout

    def _createTaskListLayout(self):
        taskListLayout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel("Task List")
        self.label.setObjectName("label")
        taskListLayout.addWidget(self.label)
        self.taskList = QtWidgets.QListWidget()
        self.taskList.setObjectName("taskList")
        taskListLayout.addWidget(self.taskList)
        return taskListLayout

    def _createStatusLayout(self):
        statusLayout = QtWidgets.QHBoxLayout()
        self.statusComboBox = QtWidgets.QComboBox()
        self.statusComboBox.setObjectName("statusComboBox")
        self.statusComboBox.addItem("Pending")
        self.statusComboBox.addItem("Completed")
        statusLayout.addWidget(self.statusComboBox)
        self.label_2 = QtWidgets.QLabel()
        self.label_2.setObjectName("label_2")
        statusLayout.addWidget(self.label_2)
        return statusLayout

    def keyPressEvent(self, event):
        if event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter]:
            event.accept()
        else:
            super().keyPressEvent(event)

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
                    "foreground": QtGui.QColor("darkslategray"),
                },
                "Completed": {
                    "background": QtGui.QColor("lightgreen"),
                    "foreground": QtGui.QColor("darkslategray"),
                },
            },
            "Dark": {
                "Pending": {
                    "background": QtGui.QColor(66, 66, 66),
                    "foreground": QtGui.QColor(255, 255, 255),  # White
                },
                "Completed": {
                    "background": QtGui.QColor(34, 139, 34),  # Dark green
                    "foreground": QtGui.QColor(255, 255, 255),  # White
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

        # Adjust styles for UI elements
        self.searchBar.setStyleSheet("background-color: #333333; color: white;")
        self.addTaskButton.setStyleSheet("background-color: #444444; color: white;")
        self.statusComboBox.setStyleSheet("background-color: #444444; color: white;")

        # Reload task list with updated color scheme
        self.loadTasks()

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

        # reset darkmode
        self.searchBar.setStyleSheet("")
        self.addTaskButton.setStyleSheet("")
        self.statusComboBox.setStyleSheet("")

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
        self.deleteTaskButton.clicked.connect(self.deleteTask)
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

    def deleteTask(self):
        selected_item = self.taskList.currentItem()
        if selected_item:
            task_text = selected_item.text()
            current_date = datetime.now().strftime("%Y-%m-%d")
            tasks = self.loadTasksFromFile()

            if current_date in tasks:
                # remove task is list
                tasks[current_date] = [
                    task for task in tasks[current_date] if task["text"] != task_text
                ]

                # save data to file
                self.saveTasksToFile(tasks)

                # remove task text in ui
                self.taskList.takeItem(self.taskList.row(selected_item))

                QtWidgets.QMessageBox.information(
                    self, "Success", f"Task '{task_text}' deleted successfully!"
                )
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Error", "No tasks found for today."
                )
        else:
            QtWidgets.QMessageBox.warning(
                self, "Error", "Please select a task to delete."
            )


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()  # Window display
    sys.exit(app.exec_())
