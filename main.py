import json
import sys
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
                    # تنظیم ComboBox بر اساس وضعیت تسک
                    if task["status"] == "Completed":
                        self.statusComboBox.setCurrentIndex(1)
                    else:
                        self.statusComboBox.setCurrentIndex(0)
                    break

        # بروزرسانی رنگ تسک انتخاب شده
        self.updateTaskColor(item)  # فراخوانی متد به‌روز رسانی رنگ

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
        به‌روزرسانی رنگ تسک بر اساس وضعیت و تم فعلی.
        """
        if task is None:
            # اگر تسک به صورت مشخص وارد نشده باشد، آن را از لیست بارگذاری می‌کنیم
            current_date = datetime.now().strftime("%Y-%m-%d")
            tasks = self.loadTasksFromFile()
            if current_date in tasks:
                selected_task_text = item.text()
                for t in tasks[current_date]:
                    if t["text"] == selected_task_text:
                        task = t
                        break

        # اگر تسک مشخص شده باشد، وضعیت آن را می‌گیریم
        if task:
            status = task["status"]
            # دریافت رنگ‌ها از پالت رنگ‌ها بر اساس وضعیت و تم فعلی
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
                    # تنظیم رنگ بر اساس وضعیت
                    colors = self.theme_colors[self.current_theme][task["status"]]
                    item.setBackground(colors["background"])
                    item.setForeground(colors["foreground"])
                    self.taskList.addItem(item)

                        
    def loadTasksFromFile(self):
        try:
            with open("tasks.json", "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def saveTasksToFile(self, tasks):
        with open("tasks.json", "w") as file:
            json.dump(tasks, file, indent=4)

    def openSettingsMenu(self):
        settings_dialog = QtWidgets.QDialog(self)
        settings_dialog.setWindowTitle("Settings")
        settings_layout = QtWidgets.QVBoxLayout(settings_dialog)

        # Add a dropdown to choose between Dark and Light mode
        theme_combobox = QtWidgets.QComboBox(settings_dialog)
        theme_combobox.addItem("Light Mode")
        theme_combobox.addItem("Dark Mode")
        theme_combobox.setCurrentText(self.current_theme)
        settings_layout.addWidget(theme_combobox)

        # Connect theme change
        theme_combobox.currentIndexChanged.connect(
            lambda: self.changeTheme(theme_combobox.currentText())
        )

        settings_dialog.setLayout(settings_layout)
        settings_dialog.exec_()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()  # نمایش پنجره
    sys.exit(app.exec_())

