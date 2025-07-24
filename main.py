#!/usr/bin/env python3
"""
DMLS Powder Tracking Manager
Main application entry point
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem, 
                             QVBoxLayout, QHBoxLayout, QWidget, QHeaderView, QTabWidget, QPushButton, QLabel, QToolBar, QStyle, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, QSize
from database.connection import init_database
from models.builds.build import Build
from models.jobs.job import Job
from models.jobs.work_order import WorkOrder
from models.settings.setting import Setting
from models.powders.powder import Powder
from models.plates.plate import Plate
from models.coupons.coupon_array import CouponArray
from gui.detail_windows import PowderDetailWindow, SettingDetailWindow, CouponArrayDetailWindow, CouponDetailWindow, WorkOrderDetailWindow, JobDetailWindow
import peewee as pw




def find_non_nullable_dependencies(model_cls, pk):
    import peewee as pw
    dependencies = []
    obj = model_cls.get_by_id(pk)
    from models.builds.build import Build
    from models.jobs.job import Job
    from models.jobs.work_order import WorkOrder
    from models.jobs.part_list import PartList
    from models.settings.setting import Setting
    from models.powders.powder import Powder
    from models.plates.plate import Plate
    from models.coupons.coupon_array import CouponArray
    from models.powders.powder_composition import PowderComposition
    from models.powders.powder_results import PowderResults
    # Build
    if isinstance(obj, Setting):
        for build in Build.select().where(Build.setting == obj):
            dependencies.append(f"Build (ID {build.id}) - setting")
    if isinstance(obj, Powder):
        for build in Build.select().where(Build.powder == obj):
            dependencies.append(f"Build (ID {build.id}) - powder")
    if isinstance(obj, Plate):
        for build in Build.select().where(Build.plate == obj):
            dependencies.append(f"Build (ID {build.id}) - plate")
    if isinstance(obj, CouponArray):
        for build in Build.select().where(Build.coupon_array == obj):
            dependencies.append(f"Build (ID {build.id}) - coupon_array")
    if isinstance(obj, Build):
        for job in Job.select().where(Job.build == obj):
            dependencies.append(f"Job (ID {job.id}) - build")
    if isinstance(obj, WorkOrder):
        for job in Job.select().where(Job.work_order == obj):
            dependencies.append(f"Job (ID {job.id}) - work_order")
    if isinstance(obj, PartList):
        for pl in PartList.select().where(PartList.part_1 == obj):
            dependencies.append(f"PartList (ID {pl.id}) - part_1")
    if isinstance(obj, Job):
        pass
    if isinstance(obj, Setting):
        for field in [
            'hatch_up_skin', 'hatch_infill', 'hatch_down_skin', 'contour_on_part',
            'contour_standard', 'contour_down', 'edge', 'core', 'support']:
            val = getattr(obj, field, None)
            if val is not None:
                dependencies.append(f"Setting (ID {obj.id}) - {field}")
    # Add more as needed for other models
    return dependencies


class DatabaseTableWidget(QTableWidget):
    """Reusable table widget for displaying database data"""
    def __init__(self, parent=None, model_cls=None, exclude_columns=None):
        super().__init__(parent)
        self.model_cls = model_cls
        self.exclude_columns = exclude_columns or []
        self.edit_mode = False
        self.delete_col_index = None
        self._suppress_cell_changed = False
        self.cellChanged.connect(self._on_cell_changed)

    def set_edit_mode(self, enabled):
        self.edit_mode = enabled
        if enabled:
            self.setEditTriggers(QTableWidget.EditTrigger.AllEditTriggers)
        else:
            self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._update_delete_column()

    def _update_delete_column(self):
        # Remove existing delete column if present
        if self.delete_col_index is not None:
            self.removeColumn(self.delete_col_index)
            self.delete_col_index = None
        if self.edit_mode:
            col = self.columnCount()
            self.insertColumn(col)
            self.setHorizontalHeaderItem(col, QTableWidgetItem(""))
            self.delete_col_index = col
            for row in range(self.rowCount()):
                btn = QPushButton()
                btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
                btn.setIconSize(QSize(24, 24))
                btn.setStyleSheet("background-color: #c00; border-radius: 4px; margin: 2px;")
                btn.setToolTip("Delete this row")
                btn.clicked.connect(lambda _, r=row: self._confirm_delete(r))
                self.setCellWidget(row, col, btn)
        self.resizeColumnsToContents()

    def _confirm_delete(self, row):
        pk = self.item(row, 0).text()
        dependencies = find_non_nullable_dependencies(self.model_cls, pk)
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Confirm Delete")
        warn_text = "Are you sure you want to delete this item?"
        if dependencies:
            warn_text += "\n\nWarning: This item is referenced by the following (deletion will break these references):\n"
            for dep in dependencies:
                warn_text += f"- {dep}\n"
        msg.setText(warn_text)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        msg.setStyleSheet("QLabel{min-width:250px; font-size:14px;} QPushButton{min-width:60px;}")
        reply = msg.exec()
        if reply == QMessageBox.StandardButton.Yes:
            self._delete_row(row)

    def _delete_row(self, row):
        if self.model_cls:
            pk = self.item(row, 0).text()
            obj = self.model_cls.get_by_id(pk)
            obj.delete_instance()
            self.removeRow(row)

    def _on_cell_changed(self, row, col):
        if self._suppress_cell_changed or not self.edit_mode:
            return
        if self.delete_col_index is not None and col == self.delete_col_index:
            return
        if self.model_cls:
            pk = self.item(row, 0).text()
            obj = self.model_cls.get_by_id(pk)
            field = self.horizontalHeaderItem(col).text().lower().replace(" ", "_")
            value = self.item(row, col).text()
            # Type conversion for booleans
            if hasattr(obj, field):
                attr = getattr(obj, field)
                if isinstance(attr, bool):
                    value = value.lower() in ("yes", "true", "1")
                setattr(obj, field, value)
                obj.save()

    def load_data(self, headers, data, add_details_column=False, details_callback=None):
        self._suppress_cell_changed = True
        # Remove details column from editable columns
        self.exclude_columns = []
        details_col_index = None
        if add_details_column:
            headers = headers + ["Details"]
            details_col_index = len(headers) - 1
            self.exclude_columns.append(details_col_index)
        super().setColumnCount(len(headers))
        super().setHorizontalHeaderLabels(headers)
        super().setRowCount(len(data))
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                if col in self.exclude_columns:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                super().setItem(row, col, item)
            if add_details_column and details_callback:
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
                def make_mouse_press_event(row):
                    def mousePressEvent(event):
                        if event.button() == Qt.MouseButton.LeftButton:
                            details_callback(row)
                    return mousePressEvent
                details_label.mousePressEvent = make_mouse_press_event(row)
                super().setCellWidget(row, details_col_index, details_label)
        self._suppress_cell_changed = False
        self._update_delete_column()
        if self.edit_mode:
            self.setEditTriggers(QTableWidget.EditTrigger.AllEditTriggers)
        else:
            self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
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
        
        # Restore global toolbar
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setIconSize(QSize(32, 32))
        self.toolbar.setFixedHeight(48)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        self.create_btn = QPushButton()
        self.create_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        self.create_btn.setIconSize(QSize(32, 32))
        self.create_btn.setFixedSize(40, 40)
        self.create_btn.setToolTip("Create new item (not implemented yet)")
        self.toolbar.addWidget(self.create_btn)
        self.edit_mode = False
        self.edit_btn = QPushButton()
        self.edit_btn.setCheckable(True)
        self.edit_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton))
        self.edit_btn.setIconSize(QSize(32, 32))
        self.edit_btn.setFixedSize(40, 40)
        self.edit_btn.setToolTip("Toggle edit mode for all tables")
        self.edit_btn.toggled.connect(self.toggle_edit_mode)
        self.toolbar.addWidget(self.edit_btn)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        self.tab_widget.currentChanged.connect(self.update_create_button_tooltip)
        
        # Create tabs for different tables
        self.create_builds_tab()
        self.create_work_orders_tab()
        self.create_jobs_tab()
        self.create_settings_tab()
        self.create_powders_tab()
        self.create_plates_tab()
        self.create_coupon_arrays_tab()
        self.update_create_button_tooltip()
    
    def create_builds_tab(self):
        """Create tab for builds table"""
        table = DatabaseTableWidget(model_cls=Build)
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
                    try:
                        powder_id = build.powder.id if build.powder else 'None'
                    except Exception:
                        powder_id = 'Missing (deleted)'
                    try:
                        setting_id = build.setting.id if build.setting else 'None'
                    except Exception:
                        setting_id = 'Missing (deleted)'
                    try:
                        plate_description = build.plate.description if build.plate else 'None'
                    except Exception:
                        plate_description = 'Missing (deleted)'
                    try:
                        coupon_array_id = build.coupon_array.id if build.coupon_array else 'None'
                    except Exception:
                        coupon_array_id = 'Missing (deleted)'
                    data.append([
                        build.id, build.name, build.description, build.datetime,
                        build.powder_weight_required, build.powder_weight_loaded,
                        powder_id, setting_id, plate_description, coupon_array_id
                    ])
                table.load_data(headers, data)
                
                # Add double-click functionality for setting ID column (column 7)
                table.cellDoubleClicked.connect(self.on_build_table_double_click)
                
                print(f"Loaded {len(data)} builds")
        except Exception as e:
            print(f"Error loading builds: {e}")
    
    def create_work_orders_tab(self):
        """Create tab for work orders table"""
        table = DatabaseTableWidget(model_cls=WorkOrder)
        self.tab_widget.addTab(table, "Work Orders")
        try:
            work_orders = WorkOrder.select()
            if work_orders.exists():
                headers = ["ID", "Name", "Description", "PVID", "Part List"]
                data = []
                for wo in work_orders:
                    try:
                        part_list_id = wo.part_list.id if wo.part_list else 'None'
                    except Exception:
                        part_list_id = 'None'
                    data.append([
                        wo.id, wo.name, wo.description, wo.pvid,
                        part_list_id
                    ])
                def work_order_details_callback(row):
                    wo_id = data[row][0]
                    window = WorkOrderDetailWindow(wo_id, edit_mode=self.edit_mode)
                    self.detail_windows.append(window)
                    window.show()
                table.load_data(headers, data, add_details_column=True, details_callback=work_order_details_callback)
                print(f"Loaded {len(data)} work orders")
        except Exception as e:
            print(f"Error loading work orders: {e}")
    
    def create_jobs_tab(self):
        """Create tab for jobs table"""
        table = DatabaseTableWidget(model_cls=Job)
        self.tab_widget.addTab(table, "Jobs")
        try:
            jobs = Job.select()
            if jobs.exists():
                headers = ["ID", "Name", "Description", "Part List", "Work Order ID", "Build ID"]
                data = []
                for job in jobs:
                    try:
                        part_list_id = job.part_list.id if job.part_list else 'None'
                    except Exception:
                        part_list_id = 'None'
                    try:
                        work_order_id = job.work_order.id if job.work_order else 'None'
                    except Exception:
                        work_order_id = 'None'
                    try:
                        build_id = job.build.id if job.build else 'None'
                    except Exception:
                        build_id = 'None'
                    data.append([
                        job.id, job.name, job.description, part_list_id,
                        work_order_id,
                        build_id
                    ])
                def job_details_callback(row):
                    job_id = data[row][0]
                    window = JobDetailWindow(job_id, edit_mode=self.edit_mode)
                    self.detail_windows.append(window)
                    window.show()
                table.load_data(headers, data, add_details_column=True, details_callback=job_details_callback)
                print(f"Loaded {len(data)} jobs")
        except Exception as e:
            print(f"Error loading jobs: {e}")
    
    def create_settings_tab(self):
        """Create tab for settings table"""
        table = DatabaseTableWidget(model_cls=Setting)
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
        table = DatabaseTableWidget(model_cls=Powder)
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
        table = DatabaseTableWidget(model_cls=Plate)
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
        table = DatabaseTableWidget(model_cls=CouponArray)
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
            window = PowderDetailWindow(powder_id, edit_mode=self.edit_mode)
            self.detail_windows.append(window)  # Store reference to prevent garbage collection
            window.show()
        except Exception as e:
            print(f"Error showing powder details: {e}")
    
    def show_setting_details(self, setting_id):
        """Show setting details"""
        try:
            print(f"Opening setting details for ID: {setting_id}")
            window = SettingDetailWindow(setting_id, edit_mode=self.edit_mode)
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
    
    def show_part_list_details(self, part_list):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel
        dialog = QDialog(self)
        dialog.setWindowTitle("Part List Details")
        dialog.resize(800, 500)
        layout = QVBoxLayout(dialog)
        header_label = QLabel("Part List Details")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(header_label)
        if not part_list:
            layout.addWidget(QLabel("No Part List associated."))
        else:
            # Show PartList meta fields
            name_label = QLabel(f"Name: {part_list.name if part_list.name else ''}")
            name_label.setStyleSheet("font-size: 14px; margin: 5px 10px 0 10px;")
            layout.addWidget(name_label)
            desc_label = QLabel(f"Description: {part_list.description if part_list.description else ''}")
            desc_label.setStyleSheet("font-size: 13px; margin: 0 10px 5px 10px;")
            layout.addWidget(desc_label)
            preset_label = QLabel(f"Preset: {'Yes' if part_list.is_preset else 'No'}")
            preset_label.setStyleSheet("font-size: 13px; margin: 0 10px 10px 10px;")
            layout.addWidget(preset_label)
            # Collect all non-null parts
            parts = []
            for i in range(128):
                part = getattr(part_list, f'part_{i+1}', None)
                if part:
                    parts.append(part)
            if not parts:
                layout.addWidget(QLabel("No parts in this Part List."))
            else:
                table = QTableWidget()
                table.setColumnCount(5)
                table.setHorizontalHeaderLabels(["ID", "Name", "Description", "File Path", "Is Complete"])
                table.setRowCount(len(parts))
                for row, part in enumerate(parts):
                    table.setItem(row, 0, QTableWidgetItem(str(part.id)))
                    table.setItem(row, 1, QTableWidgetItem(str(part.name)))
                    table.setItem(row, 2, QTableWidgetItem(str(part.description)))
                    table.setItem(row, 3, QTableWidgetItem(str(part.file_path)))
                    table.setItem(row, 4, QTableWidgetItem("Yes" if part.is_complete else "No"))
                table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
                table.resizeColumnsToContents()
                layout.addWidget(table)
        dialog.setLayout(layout)
        dialog.exec()

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

    def toggle_edit_mode(self, checked):
        self.edit_mode = checked
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if isinstance(widget, DatabaseTableWidget):
                widget.set_edit_mode(checked)

    def update_create_button_tooltip(self):
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index >= 0:
            tab_name = self.tab_widget.tabText(current_tab_index)
            # Remove trailing 's' for singular (basic approach)
            item_type = tab_name[:-1] if tab_name.endswith('s') else tab_name
            self.create_btn.setToolTip(f"Create new {item_type}")
        else:
            self.create_btn.setToolTip("Create new item")


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