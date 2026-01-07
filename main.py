"""Main entry point for the payment statement writer application.

This module launches the PySide6 GUI application.
"""

import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow


def main():
    """Main function to start the application."""
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
