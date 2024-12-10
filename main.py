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

        # Search Bar Layout
        self.searchBar = QtWidgets.QLineEdit()
        self.searchBar.setPlaceholderText("Search tasks...")
        self.searchBar.setObjectName("searchBar")

        # Add Clear Button to Search Bar
        self.searchBar.setClearButtonEnabled(True)
        self.mainLayout.addWidget(self.searchBar)

        # Layout for task input
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
        self.setupFunctions()
        self.updateDateLabel()
        self.allTasks = []  # Store all tasks for search functionality
        self.loadTasks()  # Ensure tasks are loaded when the dialog is created

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
                    # Set ComboBox to the current status of the task
                    if task["status"] == "Completed":
                        self.statusComboBox.setCurrentIndex(1)
                    else:
                        self.statusComboBox.setCurrentIndex(0)
                    break

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

                        if task["status"] == "Completed":
                            selected_item.setForeground(QtGui.QColor("green"))
                            selected_item.setBackground(QtGui.QColor("lightgreen"))
                        elif task["status"] == "Pending":
                            selected_item.setForeground(QtGui.QColor("orange"))
                            selected_item.setBackground(QtGui.QColor("lightyellow"))
                        break




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
                    if task["status"] == "Completed":
                        item.setBackground(QtGui.QColor("lightgreen"))
                    elif task["status"] == "Pending":
                        item.setBackground(QtGui.QColor("lightyellow"))
                    self.taskList.addItem(item)

    def loadTasks(self):
        tasks = self.loadTasksFromFile()
        self.taskList.clear()
        self.allTasks = []  # Clear previous tasks for search

        current_date = datetime.now().strftime("%Y-%m-%d")
        if current_date in tasks:
            for task in tasks[current_date]:
                item_text = task["text"]  # Only the task text, without the status
                item = QtWidgets.QListWidgetItem(item_text)

                # Set color based on status
                if task["status"] == "Completed":
                    item.setBackground(QtGui.QColor("lightgreen"))  # Background color
                    item.setForeground(QtGui.QColor("green"))  # Text color for Completed
                elif task["status"] == "Pending":
                    item.setBackground(QtGui.QColor("lightyellow"))
                    item.setForeground(QtGui.QColor("orange"))  # Text color for Pending

                self.taskList.addItem(item)
                self.allTasks.append(item_text)  # Store task text without status for search

    def loadTasksFromFile(self):
        try:
            with open("tasks.json", "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def saveTasksToFile(self, tasks):
        with open("tasks.json", "w") as file:
            json.dump(tasks, file, indent=4)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    # window.showFullScreen()
    sys.exit(app.exec_())

