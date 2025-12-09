import sys
from PySide6.QtWidgets import QApplication
from app.app_context import AppContext
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    context = AppContext()
    window = MainWindow(context)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
