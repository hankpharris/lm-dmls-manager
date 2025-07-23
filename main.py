#!/usr/bin/env python3
"""
DMLS Powder Tracking Manager
Main application entry point
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem, 
                             QVBoxLayout, QHBoxLayout, QWidget, QHeaderView, QTabWidget, QPushButton, QLabel)
from PyQt6.QtCore import Qt, QTimer
from database.connection import init_database
from models.builds.build import Build
from models.jobs.job import Job
from models.jobs.work_order import WorkOrder
from models.settings.setting import Setting
from models.powders.powder import Powder
from models.plates.plate import Plate
from models.coupons.coupon_array import CouponArray
from gui.detail_windows import PowderDetailWindow, SettingDetailWindow, CouponArrayDetailWindow




class DatabaseTableWidget(QTableWidget):
    """Reusable table widget for displaying database data"""
    def __init__(self):
        super().__init__()
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.resizeColumnsToContents()
        # Enable double-click signals
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
    
    def load_data(self, headers, data, add_details_column=False, details_callback=None):
        """Load data into the table"""
        if not data:
            self.setRowCount(1)
            self.setColumnCount(1)
            self.setItem(0, 0, QTableWidgetItem("No data found in database"))
            return
        
        # Add details column if requested
        if add_details_column:
            headers = headers + ["Details"]
        
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.setRowCount(len(data))
        
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                self.setItem(row, col, QTableWidgetItem(str(value)))
            
            # Add details button if requested
            if add_details_column and details_callback:
                # Use a clickable label instead of a button to avoid state issues
                details_label = QLabel("Details")
                details_label.setStyleSheet("""
                    QLabel {
                        background-color: rgba(0, 60, 100, 0.8);
                        color: white;
                        padding: 2px 6px;
                        border-radius: 2px;
                        font-size: 10px;
                        border: 1px solid #666666;
                        margin: 2px;
                    }
                    QLabel:hover {
                        background-color: rgba(0, 80, 140, 0.9);
                    }
                """)
                details_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                details_label.setCursor(Qt.CursorShape.PointingHandCursor)
                
                # Make it clickable by handling mouse events
                def mousePressEvent(event):
                    if event.button() == Qt.MouseButton.LeftButton:
                        details_callback(row)
                
                details_label.mousePressEvent = mousePressEvent
                self.setCellWidget(row, len(row_data), details_label)
        
        self.resizeColumnsToContents()


class DatabaseViewerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DMLS Database Viewer")
        self.setGeometry(100, 100, 1400, 800)
        
        # Store detail windows to prevent garbage collection
        self.detail_windows = []
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs for different tables
        self.create_builds_tab()
        self.create_work_orders_tab()
        self.create_jobs_tab()
        self.create_settings_tab()
        self.create_powders_tab()
        self.create_plates_tab()
        self.create_coupon_arrays_tab()
    
    def create_builds_tab(self):
        """Create tab for builds table"""
        table = DatabaseTableWidget()
        self.tab_widget.addTab(table, "Builds")
        
        # Store reference to the builds table for double-click handling
        self.builds_table = table
        
        try:
            builds = Build.select()
            if builds.exists():
                headers = [
                    "ID", "Name", "Description", "DateTime", 
                    "Powder Weight Required", "Powder Weight Loaded",
                    "Powder ID", "Setting ID", "Plate Description", "Coupon Array ID"
                ]
                data = []
                for build in builds:
                    data.append([
                        build.id, build.name, build.description, build.datetime,
                        build.powder_weight_required, build.powder_weight_loaded,
                        build.powder.id if build.powder else 'None',
                        build.setting.id if build.setting else 'None',
                        build.plate.description if build.plate else 'None',
                        build.coupon_array.id if build.coupon_array else 'None'
                    ])
                table.load_data(headers, data)
                
                # Add double-click functionality for setting ID column (column 7)
                table.cellDoubleClicked.connect(self.on_build_table_double_click)
                
                print(f"Loaded {len(data)} builds")
        except Exception as e:
            print(f"Error loading builds: {e}")
    
    def create_work_orders_tab(self):
        """Create tab for work orders table"""
        table = DatabaseTableWidget()
        self.tab_widget.addTab(table, "Work Orders")
        
        try:
            work_orders = WorkOrder.select()
            if work_orders.exists():
                headers = ["ID", "Name", "Description", "PVID", "Parts", "Parent ID"]
                data = []
                for wo in work_orders:
                    data.append([
                        wo.id, wo.name, wo.description, wo.pvid,
                        str(wo.parts), wo.parent.id if wo.parent else 'None'
                    ])
                table.load_data(headers, data)
                print(f"Loaded {len(data)} work orders")
        except Exception as e:
            print(f"Error loading work orders: {e}")
    
    def create_jobs_tab(self):
        """Create tab for jobs table"""
        table = DatabaseTableWidget()
        self.tab_widget.addTab(table, "Jobs")
        
        try:
            jobs = Job.select()
            if jobs.exists():
                headers = ["ID", "Name", "Description", "Parts", "Work Order ID", "Build ID"]
                data = []
                for job in jobs:
                    data.append([
                        job.id, job.name, job.description, str(job.parts),
                        job.work_order.id if job.work_order else 'None',
                        job.build.id if job.build else 'None'
                    ])
                table.load_data(headers, data)
                print(f"Loaded {len(data)} jobs")
        except Exception as e:
            print(f"Error loading jobs: {e}")
    
    def create_settings_tab(self):
        """Create tab for settings table"""
        table = DatabaseTableWidget()
        self.tab_widget.addTab(table, "Settings")
        
        try:
            settings = Setting.select()
            if settings.exists():
                headers = ["ID", "Name", "Description", "Is Preset"]
                data = []
                for setting in settings:
                    data.append([
                        setting.id, setting.name, setting.description, setting.is_preset
                    ])
                
                # Create callback function for details buttons
                def settings_details_callback(row):
                    setting_id = data[row][0]  # ID is first column
                    self.show_setting_details(setting_id)
                
                table.load_data(headers, data, add_details_column=True, details_callback=settings_details_callback)
                print(f"Loaded {len(data)} settings")
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def create_powders_tab(self):
        """Create tab for powders table"""
        table = DatabaseTableWidget()
        self.tab_widget.addTab(table, "Powders")
        
        try:
            powders = Powder.select()
            if powders.exists():
                headers = ["ID", "Description", "Material ID", "Manufacturer Lot", "Subgroup", "Revision", "Initiation Timestamp", "Quantity (Kg)"]
                data = []
                for powder in powders:
                    data.append([
                        powder.id, powder.description, powder.mat_id, powder.man_lot,
                        powder.subgroup, powder.rev, powder.init_date_time, powder.quantity
                    ])
                
                # Create callback function for details buttons
                def powders_details_callback(row):
                    powder_id = data[row][0]  # ID is first column
                    self.show_powder_details(powder_id)
                
                table.load_data(headers, data, add_details_column=True, details_callback=powders_details_callback)
                print(f"Loaded {len(data)} powders")
        except Exception as e:
            print(f"Error loading powders: {e}")
    
    def create_plates_tab(self):
        """Create tab for plates table"""
        table = DatabaseTableWidget()
        self.tab_widget.addTab(table, "Plates")
        
        try:
            plates = Plate.select()
            if plates.exists():
                headers = ["ID", "Description", "Material", "Foreign Keys", "Stamped Heights"]
                data = []
                for plate in plates:
                    data.append([
                        plate.id, plate.description, plate.material,
                        str(plate.foreign_keys_list), str(plate.stamped_heights)
                    ])
                table.load_data(headers, data)
                print(f"Loaded {len(data)} plates")
        except Exception as e:
            print(f"Error loading plates: {e}")
    
    def create_coupon_arrays_tab(self):
        """Create tab for coupon arrays table"""
        table = DatabaseTableWidget()
        self.tab_widget.addTab(table, "Coupon Arrays")
        
        try:
            coupon_arrays = CouponArray.select()
            if coupon_arrays.exists():
                headers = ["ID", "Name", "Description", "Is Preset", "Coupon Count"]
                data = []
                for ca in coupon_arrays:
                    # Count non-None coupons
                    coupon_count = sum(1 for i in range(1, 257) if getattr(ca, f'coupon_{i}', None) is not None)
                    data.append([ca.id, ca.name, ca.description, ca.is_preset, coupon_count])
                
                # Create callback function for details buttons
                def coupon_arrays_details_callback(row):
                    coupon_array_id = data[row][0]  # ID is first column
                    self.show_coupon_array_details(coupon_array_id)
                
                table.load_data(headers, data, add_details_column=True, details_callback=coupon_arrays_details_callback)
                print(f"Loaded {len(data)} coupon arrays")
        except Exception as e:
            print(f"Error loading coupon arrays: {e}")
    
    def show_powder_details(self, powder_id):
        """Show powder details (composition and results)"""
        try:
            print(f"Opening powder details for ID: {powder_id}")
            window = PowderDetailWindow(powder_id)
            self.detail_windows.append(window)  # Store reference to prevent garbage collection
            window.show()
        except Exception as e:
            print(f"Error showing powder details: {e}")
    
    def show_setting_details(self, setting_id):
        """Show setting details"""
        try:
            print(f"Opening setting details for ID: {setting_id}")
            window = SettingDetailWindow(setting_id)
            self.detail_windows.append(window)  # Store reference to prevent garbage collection
            window.show()
        except Exception as e:
            print(f"Error showing setting details: {e}")
    
    def show_coupon_array_details(self, coupon_array_id):
        """Show coupon array details"""
        try:
            print(f"Opening coupon array details for ID: {coupon_array_id}")
            window = CouponArrayDetailWindow(coupon_array_id)
            self.detail_windows.append(window)  # Store reference to prevent garbage collection
            window.show()
        except Exception as e:
            print(f"Error showing coupon array details: {e}")
    
    def on_build_table_double_click(self, row, column):
        """Handle double-click on build table cells"""
        try:
            print(f"Double-click detected at row {row}, column {column}")
            
            # Check if the double-click is on the Powder ID column (column 6)
            if column == 6:  # Powder ID column
                # Get the powder ID from the builds table
                if hasattr(self, 'builds_table') and self.builds_table:
                    powder_id_text = self.builds_table.item(row, column).text()
                    print(f"Powder ID text: {powder_id_text}")
                    if powder_id_text != 'None':
                        powder_id = powder_id_text  # Powder IDs are strings, not integers
                        print(f"Double-clicked on Powder ID: {powder_id}")
                        self.show_powder_details(powder_id)
                    else:
                        print("Powder ID is None, cannot open details")
                else:
                    print("Builds table reference not found")
            
            # Check if the double-click is on the Setting ID column (column 7)
            elif column == 7:  # Setting ID column
                # Get the setting ID from the builds table
                if hasattr(self, 'builds_table') and self.builds_table:
                    setting_id_text = self.builds_table.item(row, column).text()
                    print(f"Setting ID text: {setting_id_text}")
                    if setting_id_text != 'None':
                        setting_id = int(setting_id_text)
                        print(f"Double-clicked on Setting ID: {setting_id}")
                        self.show_setting_details(setting_id)
                    else:
                        print("Setting ID is None, cannot open details")
                else:
                    print("Builds table reference not found")
        except Exception as e:
            print(f"Error handling build table double-click: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("DMLS Powder Tracking Manager")
    app.setApplicationVersion("1.0.0")
    
    # Initialize database
    init_database()
    
    # Create and show database viewer window
    window = DatabaseViewerWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 