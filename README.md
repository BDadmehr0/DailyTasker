# DailyTasker

DailyTasker is a simple and efficient To-Do list application built with Python and PyQt5. It allows users to create, manage, and track their tasks with ease. The app organizes tasks by date and provides options to mark them as "Pending" or "Completed."

## Features

- **Add Tasks**: Users can input tasks and add them to the list.
- **Task Status**: Each task can be marked as either "Pending" or "Completed."
- **Task List Display**: Displays tasks for the current day.
- **Date Display**: Shows the current date and time, updated every second.
- **Persistent Storage**: Tasks are saved in a `tasks.json` file.

## Requirements

- Python 3.x
- PyQt5

You can install the required packages using pip:

```bash
pip install pyqt5
```

## File Structure

- `main.py`: The main application file containing the PyQt5 UI and logic.
- `tasks.json`: The file used for saving tasks (created automatically when the app is run).

## How to Run

1. Clone or download this repository to your local machine.
2. Ensure you have Python 3.x and PyQt5 installed.
3. Open a terminal or command prompt in the directory containing `main.py`.
4. Run the following command:

```bash
python main.py
```

The application window will open, allowing you to interact with the TODO list.

## Usage

- **Add Task**: Type the task name in the input field and click the "Add Task" button.
- **Change Task Status**: Click on a task in the list and select the status (Pending or Completed) from the combo box.
- **Current Date and Time**: The current date and time will be displayed at the bottom of the window, updated every second.

## Notes

- Tasks are stored in a `tasks.json` file in the same directory as the program. The tasks are grouped by date, and each task has a status ("Pending" or "Completed").
- If the `tasks.json` file is missing or corrupted, the application will create a new file.

## License

This project is licensed under the [GNU License](https://github.com/BDadmehr0/DailyTasker/blob/main/LICENSE).
