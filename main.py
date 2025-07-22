#!/usr/bin/env python3
"""
DMLS Powder Tracking Manager
Main application entry point
"""

import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("DMLS Powder Tracking Manager")
    app.setApplicationVersion("1.0.0")
    
    # Initialize database
    from database.connection import init_database
    init_database()
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 