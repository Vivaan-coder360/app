import json
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class UIChanger(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Todo List")
        self.resize(900, 500)

        # -------------------------
        # UI Elements
        # -------------------------

        self.label = QLabel("Todo List")

        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter your task")

        self.button1 = QPushButton("View tasks")
        self.button2 = QPushButton("Save")
        self.button3 = QPushButton("Light Mode")

        self.delete_button = QPushButton("Delete checked tasks")

        # -------------------------
        # Task list
        # -------------------------

        self.tasks_container = QWidget()

        self.tasks_layout = QVBoxLayout(self.tasks_container)
        self.tasks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.tasks_scroll = QScrollArea()
        self.tasks_scroll.setWidgetResizable(True)
        self.tasks_scroll.setWidget(self.tasks_container)
        self.tasks_scroll.setMinimumHeight(150)
        self.tasks_scroll.setMaximumHeight(250)

        self.tasks_scroll.hide()
        self.delete_button.hide()

        # -------------------------
        # Main Layout
        # -------------------------

        layout = QVBoxLayout()

        layout.addWidget(self.label)
        layout.addWidget(self.input)
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        layout.addWidget(self.tasks_scroll)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.button3)

        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

        # -------------------------
        # Connections
        # -------------------------

        self.button1.clicked.connect(self.view)
        self.button2.clicked.connect(self.save)
        self.button3.clicked.connect(self.theme)
        self.delete_button.clicked.connect(self.delete_checked_tasks)

        # -------------------------
        # Variables
        # -------------------------

        self.task_checkboxes = []
        self.tasks_visible = False
        self.is_light_mode = False

        # Apply initial theme
        self.apply_theme()

    # =====================================
    # THEME
    # =====================================

    def theme(self):
        self.is_light_mode = not self.is_light_mode
        self.apply_theme()

    def apply_theme(self):

        if self.is_light_mode:

            self.button3.setText("Dark Mode")

            stylesheet = """
                QWidget {
                    background-color: white;
                    color: #202124;
                }

                QLineEdit {
                    background-color: #ffffff;
                    border: 1px solid #b8b8b8;
                    border-radius: 20px;
                    padding: 5px;
                }

                QScrollArea {
                    background-color: #ffffff;
                    border: 1px solid #b8b8b8;
                    border-radius: 20px;
                }

                QPushButton {
                    background-color: #f0f0f0;
                    color: #202124;
                    border: 1px solid #b8b8b8;
                    border-radius: 20px;
                    padding: 6px 10px;
                }

                QPushButton:hover {
                    background-color: #e2e2e2;
                }

                QCheckBox {
                    color: #202124;
                    padding: 5px;
                }

                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border: 2px solid #888888;
                    border-radius: 4px;
                    background-color: white;
                }

                QCheckBox::indicator:checked {
                    background-color: #4CAF50;
                    border: 2px solid #4CAF50;
                }
            """

        else:

            self.button3.setText("Light Mode")

            stylesheet = """
                QWidget {
                    background-color: #252526;
                    color: #f1f1f1;
                }

                QLineEdit {
                    background-color: #333333;
                    color: #f1f1f1;
                    border: 1px solid #555555;
                    border-radius: 20px;
                    padding: 5px;
                }

                QScrollArea {
                    background-color: #333333;
                    border: 1px solid #555555;
                    border-radius: 20px;
                }

                QPushButton {
                    background-color: #3c3c3c;
                    color: #f1f1f1;
                    border: 1px solid #5a5a5a;
                    border-radius: 20px;
                    padding: 6px 10px;
                }

                QPushButton:hover {
                    background-color: #505050;
                }

                QCheckBox {
                    color: #f1f1f1;
                    padding: 5px;
                }

                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border: 2px solid #888888;
                    border-radius: 4px;
                    background-color: #333333;
                }

                QCheckBox::indicator:checked {
                    background-color: #4CAF50;
                    border: 2px solid #4CAF50;
                }
            """

        self.setStyleSheet(stylesheet)

    # =====================================
    # JSON
    # =====================================

    def _load_tasks(self):

        try:
            with open("tasks.json", "r", encoding="utf-8") as file:
                data = json.load(file)

        except FileNotFoundError:
            return []

        except json.JSONDecodeError:
            QMessageBox.warning(
                self,
                "Invalid Data",
                "The saved tasks file is invalid.",
            )
            return []

        if not isinstance(data, dict):
            return []

        tasks = data.get("tasks", [])

        if not isinstance(tasks, list):
            return []

        return [
            str(task)
            for task in tasks
            if str(task).strip()
        ]

    def _save_tasks(self, tasks):

        with open("tasks.json", "w", encoding="utf-8") as file:
            json.dump(
                {"tasks": tasks},
                file,
                indent=2
            )

    # =====================================
    # VIEW TASKS
    # =====================================

    def view(self):

        self.tasks_visible = not self.tasks_visible

        self.tasks_scroll.setVisible(self.tasks_visible)
        self.delete_button.setVisible(self.tasks_visible)

        if self.tasks_visible:
            self.button1.setText("Hide tasks")
            self.refresh_task_list()
        else:
            self.button1.setText("View tasks")

    # =====================================
    # REFRESH TASK LIST
    # =====================================

    def refresh_task_list(self):

        # Remove old widgets
        while self.tasks_layout.count():

            item = self.tasks_layout.takeAt(0)

            if item is None:
                continue

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        self.task_checkboxes = []

        # Load tasks from JSON
        tasks = self._load_tasks()

        if not tasks:

            self.tasks_layout.addWidget(
                QLabel("No tasks saved yet.")
            )

            return

        # Create checkboxes
        for index, task in enumerate(tasks):

            checkbox = QCheckBox(task)

            self.task_checkboxes.append(
                (index, checkbox)
            )

            self.tasks_layout.addWidget(checkbox)

    # =====================================
    # SAVE TASK
    # =====================================

    def save(self, checked=False):

        task = self.input.text().strip()

        if not task:

            QMessageBox.warning(
                self,
                "Missing Task",
                "Please enter a task before saving."
            )

            return

        tasks = self._load_tasks()

        tasks.append(task)

        self._save_tasks(tasks)

        self.input.clear()
        self.input.setFocus()

        if self.tasks_visible:
            self.refresh_task_list()

    # =====================================
    # DELETE CHECKED TASKS
    # =====================================

    def delete_checked_tasks(self):

        tasks = self._load_tasks()

        checked_indexes = {
            index
            for index, checkbox in self.task_checkboxes
            if checkbox.isChecked()
        }

        if not checked_indexes:

            QMessageBox.information(
                self,
                "Delete checked tasks",
                "Select one or more tasks in the list first."
            )

            return

        remaining_tasks = [
            task
            for index, task in enumerate(tasks)
            if index not in checked_indexes
        ]

        deleted_count = len(tasks) - len(remaining_tasks)

        self._save_tasks(remaining_tasks)

        self.refresh_task_list()

        QMessageBox.information(
            self,
            "Delete checked tasks",
            f"Deleted {deleted_count} task(s)."
        )


# =====================================
# APPLICATION
# =====================================

app = QApplication(sys.argv)

window = UIChanger()
window.show()

sys.exit(app.exec())