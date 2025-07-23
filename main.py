#!/usr/bin/env python3
"""
DMLS Powder Tracking Manager
Main application entry point
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView
from PyQt6.QtCore import Qt
from database.connection import init_database
from models.builds.build import Build


class BuildTableWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DMLS Build Table")
        self.setGeometry(100, 100, 1200, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create table widget
        self.table = QTableWidget()
        layout.addWidget(self.table)
        
        # Load and display build data
        self.load_build_data()
    
    def load_build_data(self):
        """Load build data from database and display in table"""
        try:
            # Get all builds
            builds = Build.select()
            
            if not builds.exists():
                self.table.setRowCount(1)
                self.table.setColumnCount(1)
                self.table.setItem(0, 0, QTableWidgetItem("No builds found in database"))
                return
            
            # Set up table headers
            headers = [
                "ID", "Name", "Description", "DateTime", 
                "Powder Weight Required", "Powder Weight Loaded",
                "Powder ID", "Setting Name", "Plate Description", "Coupon Array ID"
            ]
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)
            
            # Set up table rows
            build_list = list(builds)
            self.table.setRowCount(len(build_list))
            
            # Populate table with data
            for row, build in enumerate(build_list):
                self.table.setItem(row, 0, QTableWidgetItem(str(build.id)))
                self.table.setItem(row, 1, QTableWidgetItem(str(build.name)))
                self.table.setItem(row, 2, QTableWidgetItem(str(build.description)))
                self.table.setItem(row, 3, QTableWidgetItem(str(build.datetime)))
                self.table.setItem(row, 4, QTableWidgetItem(str(build.powder_weight_required)))
                self.table.setItem(row, 5, QTableWidgetItem(str(build.powder_weight_loaded)))
                self.table.setItem(row, 6, QTableWidgetItem(str(build.powder.id if build.powder else 'None')))
                self.table.setItem(row, 7, QTableWidgetItem(str(build.setting.name if build.setting else 'None')))
                self.table.setItem(row, 8, QTableWidgetItem(str(build.plate.description if build.plate else 'None')))
                self.table.setItem(row, 9, QTableWidgetItem(str(build.coupon_array.id if build.coupon_array else 'None')))
            
            # Auto-resize columns to content
            self.table.resizeColumnsToContents()
            
            # Make table read-only
            self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            
            print(f"Loaded {len(build_list)} builds from database")
            
        except Exception as e:
            print(f"Error loading build data: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("DMLS Powder Tracking Manager")
    app.setApplicationVersion("1.0.0")
    
    # Initialize database
    init_database()
    
    # Create and show build table window
    window = BuildTableWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 