import json
import sys
import platform
import os
from datetime import datetime

from PyQt5 import QtCore, QtGui, QtWidgets


class ThemeManager:
    def __init__(self):
        self.themes = {
            "Light": {
                "Pending": {"background": QtGui.QColor("lightyellow"), "foreground": QtGui.QColor("darkslategray")},
                "Completed": {"background": QtGui.QColor("lightgreen"), "foreground": QtGui.QColor("darkslategray")},
            },
            "Dark": {
                "Pending": {"background": QtGui.QColor(66, 66, 66), "foreground": QtGui.QColor(255, 255, 255)},
                "Completed": {"background": QtGui.QColor(34, 139, 34), "foreground": QtGui.QColor(255, 255, 255)},
            },
        }

    def get_colors(self, theme_name, status):
        return self.themes.get(theme_name, {}).get(status, {"background": QtGui.QColor("white"), "foreground": QtGui.QColor("black")})


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(600, 500)
        Dialog.setWindowTitle("Daily Task Manager")

        self.mainLayout = QtWidgets.QVBoxLayout(Dialog)

        # Header layout
        self.headerLayout = QtWidgets.QHBoxLayout()
        self.searchBar = QtWidgets.QLineEdit()
        self.searchBar.setPlaceholderText("Search tasks...")
        self.headerLayout.addWidget(self.searchBar)

        self.settingsButton = QtWidgets.QPushButton("⚙️")
        self.settingsButton.setFixedSize(40, 40)
        self.headerLayout.addWidget(self.settingsButton)
        self.mainLayout.addLayout(self.headerLayout)

        self.taskInputLayout = QtWidgets.QHBoxLayout()
        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.setPlaceholderText("Enter a new task...")
        self.taskInputLayout.addWidget(self.lineEdit)

        self.addTaskButton = QtWidgets.QPushButton("Add Task")
        self.taskInputLayout.addWidget(self.addTaskButton)
        self.mainLayout.addLayout(self.taskInputLayout)

        self.taskList = QtWidgets.QListWidget()
        self.mainLayout.addWidget(self.taskList)

        self.statusComboBox = QtWidgets.QComboBox()
        self.statusComboBox.addItems(["Pending", "Completed"])
        self.mainLayout.addWidget(self.statusComboBox)

        self.dateLabel = QtWidgets.QLabel()
        self.mainLayout.addWidget(self.dateLabel)


class MainApp(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.theme_manager = ThemeManager()
        self.current_theme = "Light"
        self.tasks_file = self.get_tasks_file_path()
        self.tasks = self.load_tasks()

        self.setup_connections()
        self.update_ui()

    def setup_connections(self):
        self.addTaskButton.clicked.connect(self.add_task)
        self.taskList.itemClicked.connect(self.select_task)
        self.statusComboBox.currentIndexChanged.connect(self.update_task_status)
        self.searchBar.textChanged.connect(self.search_tasks)
        self.settingsButton.clicked.connect(self.open_settings)

    def update_ui(self):
        self.load_tasks_to_ui()
        self.update_date_label()

    def add_task(self):
        task_text = self.lineEdit.text().strip()
        if not task_text:
            QtWidgets.QMessageBox.warning(self, "Error", "Task cannot be empty.")
            return

        current_date = datetime.now().strftime("%Y-%m-%d")
        if current_date not in self.tasks:
            self.tasks[current_date] = []

        if any(task["text"] == task_text for task in self.tasks[current_date]):
            QtWidgets.QMessageBox.warning(self, "Error", "Task already exists.")
            return

        self.tasks[current_date].append({"text": task_text, "status": "Pending"})
        self.save_tasks()
        self.load_tasks_to_ui()
        self.lineEdit.clear()

    def select_task(self, item):
        task_text = item.text()
        current_date = datetime.now().strftime("%Y-%m-%d")
        for task in self.tasks.get(current_date, []):
            if task["text"] == task_text:
                self.statusComboBox.setCurrentText(task["status"])
                break

    def update_task_status(self):
        selected_item = self.taskList.currentItem()
        if not selected_item:
            return

        task_text = selected_item.text()
        new_status = self.statusComboBox.currentText()
        current_date = datetime.now().strftime("%Y-%m-%d")

        for task in self.tasks.get(current_date, []):
            if task["text"] == task_text:
                task["status"] = new_status
                break

        self.save_tasks()
        self.load_tasks_to_ui()

    def search_tasks(self):
        query = self.searchBar.text().lower().strip()
        self.taskList.clear()
        current_date = datetime.now().strftime("%Y-%m-%d")

        for task in self.tasks.get(current_date, []):
            if query in task["text"].lower():
                self.add_task_to_ui(task)

    def load_tasks_to_ui(self):
        self.taskList.clear()
        current_date = datetime.now().strftime("%Y-%m-%d")

        for task in self.tasks.get(current_date, []):
            self.add_task_to_ui(task)

    def add_task_to_ui(self, task):
        item = QtWidgets.QListWidgetItem(task["text"])
        colors = self.theme_manager.get_colors(self.current_theme, task["status"])
        item.setBackground(colors["background"])
        item.setForeground(colors["foreground"])
        self.taskList.addItem(item)

    def get_tasks_file_path(self):
        app_name = "DailyTaskManager"
        if platform.system() == "Windows":
            base_dir = os.getenv("APPDATA", os.path.expanduser("~/AppData/Roaming"))
        else:
            base_dir = os.path.expanduser("~/.config")
        app_dir = os.path.join(base_dir, app_name)
        os.makedirs(app_dir, exist_ok=True)
        return os.path.join(app_dir, "tasks.json")

    def load_tasks(self):
        try:
            with open(self.tasks_file, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_tasks(self):
        with open(self.tasks_file, "w") as file:
            json.dump(self.tasks, file, indent=4)

    def update_date_label(self):
        self.dateLabel.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def open_settings(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Settings")
        layout = QtWidgets.QVBoxLayout(dialog)

        theme_combo = QtWidgets.QComboBox()
        theme_combo.addItems(["Light", "Dark"])
        theme_combo.setCurrentText(self.current_theme)
        theme_combo.currentIndexChanged.connect(lambda: self.change_theme(theme_combo.currentText()))
        layout.addWidget(QtWidgets.QLabel("Select Theme"))
        layout.addWidget(theme_combo)

        dialog.exec_()

    def change_theme(self, theme_name):
        self.current_theme = theme_name
        self.load_tasks_to_ui()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
