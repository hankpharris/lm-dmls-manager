#!/usr/bin/env python3
"""
Detailed view windows for database entities
"""

from PyQt6.QtWidgets import (QMainWindow, QTableWidget, QTableWidgetItem, 
                             QVBoxLayout, QHBoxLayout, QWidget, QPushButton, 
                             QLabel, QScrollArea, QFrame, QGridLayout, QTabWidget,
                             QMessageBox)
from PyQt6.QtCore import Qt
from models.powders.powder import Powder
from models.powders.powder_composition import PowderComposition
from models.powders.powder_results import PowderResults
from models.settings.setting import Setting
from models.settings.feature_settings import (
    HatchUpSkin, HatchInfill, HatchDownSkin, ContourOnPart, 
    ContourStandard, ContourDown, Edge, Core, Support
)
from models.coupons.coupon_array import CouponArray
from models.coupons.coupon import Coupon
from models.coupons.coupon_composition import CouponComposition
from models.jobs.work_order import WorkOrder
from models.jobs.job import Job


class DetailTableWidget(QTableWidget):
    """Reusable table widget for detailed views"""
    def __init__(self):
        super().__init__()
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.resizeColumnsToContents()
    
    def load_data(self, headers, data):
        """Load data into the table"""
        if not data:
            self.setRowCount(1)
            self.setColumnCount(1)
            self.setItem(0, 0, QTableWidgetItem("No data found"))
            return
        
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.setRowCount(len(data))
        
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                self.setItem(row, col, QTableWidgetItem(str(value)))
        
        self.resizeColumnsToContents()


class PowderDetailWindow(QMainWindow):
    """Window to display detailed powder information"""
    def __init__(self, powder_id, edit_mode=False):
        super().__init__()
        self.powder_id = powder_id
        self.edit_mode = edit_mode
        self.setWindowTitle(f"Powder Details - {powder_id}")
        self.setGeometry(200, 200, 1000, 600)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Restore parent table info (header and subheader)
        try:
            powder = Powder.get(Powder.id == self.powder_id)
            header_label = QLabel(f"Powder: {powder.id}")
            header_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
            layout.addWidget(header_label)
            desc_label = QLabel(f"Description: {powder.description}")
            desc_label.setStyleSheet("font-size: 14px; margin: 5px 10px 15px 10px;")
            layout.addWidget(desc_label)
        except Exception:
            header_label = QLabel(f"Powder: {self.powder_id}")
            header_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px; color: #a00;")
            layout.addWidget(header_label)
            desc_label = QLabel("Description: (not found)")
            desc_label.setStyleSheet("font-size: 14px; margin: 5px 10px 15px 10px; color: #a00;")
            layout.addWidget(desc_label)
        
        # Add a horizontal layout for the delete button above the tab widget (align left, compact)
        self.delete_btn_layout = QHBoxLayout()
        self.delete_btn = QPushButton()
        self.delete_btn.setStyleSheet("background-color: #c00; color: white; font-weight: bold; min-width: 100px; min-height: 28px; margin: 2px 0px 2px 0px; padding: 2px 8px;")
        self.delete_btn_layout.addWidget(self.delete_btn)
        self.delete_btn_layout.addStretch()
        layout.addLayout(self.delete_btn_layout)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_composition_tab(self.tab_widget)
        self.create_results_tab(self.tab_widget)
        
        # Always connect tab change signal to update delete button
        self.tab_widget.currentChanged.connect(self._update_delete_button)
        # Always call the callback with the current index on initial load
        self._update_delete_button(self.tab_widget.currentIndex())

    def _update_delete_button(self, tab_index):
        """Update delete button based on currently selected tab"""
        print(f"[DEBUG] _update_delete_button called with tab_index={tab_index}, tab_count={self.tab_widget.count()}, edit_mode={self.edit_mode}")
        if not self.edit_mode:
            self.delete_btn.hide()
            return
        self.delete_btn.show()
        # Disconnect all previous signals
        try:
            self.delete_btn.clicked.disconnect()
        except Exception:
            pass
        data_exists = False
        if tab_index == 0:  # Composition tab
            print("[DEBUG] Setting Delete Composition button.")
            self.delete_btn.setText("Delete Composition")
            self.delete_btn.setToolTip("Delete the entire composition record")
            try:
                powder = Powder.get(Powder.id == self.powder_id)
                PowderComposition.get(PowderComposition.powder == powder)
                data_exists = True
            except Exception:
                data_exists = False
            self.delete_btn.clicked.connect(self._delete_composition)
        elif tab_index == 1:  # Results tab
            print("[DEBUG] Setting Delete Results button.")
            self.delete_btn.setText("Delete Results")
            self.delete_btn.setToolTip("Delete the entire results record")
            try:
                powder = Powder.get(Powder.id == self.powder_id)
                PowderResults.get(PowderResults.powder == powder)
                data_exists = True
            except Exception:
                data_exists = False
            self.delete_btn.clicked.connect(self._delete_results)
        else:
            print("[DEBUG] Setting disabled placeholder button.")
            self.delete_btn.setText("Delete (N/A)")
            self.delete_btn.setToolTip("No deletable record for this tab")
            data_exists = False
        self.delete_btn.setEnabled(data_exists)
        print(f"[DEBUG] Delete button updated for tab_index={tab_index}, data_exists={data_exists}")
    
    def _delete_composition(self):
        """Delete composition record"""
        try:
            powder = Powder.get(Powder.id == self.powder_id)
            composition = PowderComposition.get(PowderComposition.powder == powder)
            from main import find_non_nullable_dependencies
            pk = composition.powder.id
            dependencies = find_non_nullable_dependencies(type(composition), pk)
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Confirm Delete")
            warn_text = "Are you sure you want to delete this composition record?"
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
                composition.delete_instance()
                # Reload the composition tab and update the delete button
                self.tab_widget.removeTab(0)
                self.create_composition_tab(self.tab_widget)
                self._update_delete_button(self.tab_widget.currentIndex())
        except Exception as e:
            print(f"Error deleting composition: {e}")
    
    def _delete_results(self):
        """Delete results record"""
        try:
            powder = Powder.get(Powder.id == self.powder_id)
            results = PowderResults.get(PowderResults.powder == powder)
            from main import find_non_nullable_dependencies
            pk = results.powder.id
            dependencies = find_non_nullable_dependencies(type(results), pk)
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Confirm Delete")
            warn_text = "Are you sure you want to delete this results record?"
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
                results.delete_instance()
                # Reload the results tab and update the delete button
                self.tab_widget.removeTab(1)
                self.create_results_tab(self.tab_widget)
                self._update_delete_button(self.tab_widget.currentIndex())
        except Exception as e:
            print(f"Error deleting results: {e}")
    
    def create_composition_tab(self, tab_widget):
        """Create tab for powder composition"""
        table = QTableWidget()
        tab_widget.addTab(table, "Composition")
        try:
            powder = Powder.get(Powder.id == self.powder_id)
            try:
                composition = PowderComposition.get(PowderComposition.powder == powder)
                headers = ["Element", "Value (%)"]
                data = [
                    ["Fe", composition.Fe],
                    ["Cr", composition.Cr],
                    ["Ni", composition.Ni],
                    ["Mo", composition.Mo],
                    ["C", composition.C],
                    ["Mn", composition.Mn],
                    ["Si", composition.Si]
                ]
                if self.edit_mode:
                    table.setColumnCount(3)
                    table.setHorizontalHeaderLabels(["Element", "Value (%)", "Delete"])
                else:
                    table.setColumnCount(2)
                    table.setHorizontalHeaderLabels(headers)
                table.setRowCount(len(data))
                for i, (field, value) in enumerate(data):
                    field_item = QTableWidgetItem(field)
                    field_item.setFlags(field_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    table.setItem(i, 0, field_item)
                    value_item = QTableWidgetItem(str(value) if value is not None else "")
                    if self.edit_mode:
                        value_item.setFlags(value_item.flags() | Qt.ItemFlag.ItemIsEditable)
                    else:
                        value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    table.setItem(i, 1, value_item)
                    if self.edit_mode:
                        delete_btn = QPushButton()
                        delete_btn.setText("🗑️")
                        delete_btn.setStyleSheet("color: #c00; font-size: 16px; font-weight: bold;")
                        delete_btn.setToolTip(f"Delete value for {field}")
                        def make_delete_func(field_name, row_idx):
                            def delete_field():
                                from main import find_non_nullable_dependencies
                                msg = QMessageBox(self)
                                msg.setIcon(QMessageBox.Icon.Warning)
                                msg.setWindowTitle("Confirm Delete")
                                msg.setText(f"Are you sure you want to delete the value for {field_name}?")
                                msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                                msg.setDefaultButton(QMessageBox.StandardButton.No)
                                msg.setStyleSheet("QLabel{min-width:250px; font-size:14px;} QPushButton{min-width:60px;}")
                                reply = msg.exec()
                                if reply == QMessageBox.StandardButton.Yes:
                                    setattr(composition, field_name, None)
                                    composition.save()
                                    table.setItem(row_idx, 1, QTableWidgetItem(""))
                            return delete_field
                        delete_btn.clicked.connect(make_delete_func(field, i))
                        table.setCellWidget(i, 2, delete_btn)
                if self.edit_mode:
                    def on_cell_changed(row, col):
                        if col == 1:
                            field = table.item(row, 0).text()
                            new_value = table.item(row, 1).text()
                            try:
                                float_val = float(new_value) if new_value else None
                            except Exception:
                                float_val = None
                            setattr(composition, field, float_val)
                            composition.save()
                    table.cellChanged.connect(on_cell_changed)
                # Tab-level delete button
                # This logic is now handled by _update_delete_button
            except PowderComposition.DoesNotExist:
                headers = ["Element", "Value (%)"]
                table.setColumnCount(2)
                table.setHorizontalHeaderLabels(headers)
                table.setRowCount(7)
                for i, field in enumerate(["Fe", "Cr", "Ni", "Mo", "C", "Mn", "Si"]):
                    field_item = QTableWidgetItem(field)
                    field_item.setFlags(field_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    table.setItem(i, 0, field_item)
                    table.setItem(i, 1, QTableWidgetItem("No data"))
                table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        except Exception as e:
            print(f"Error loading powder composition: {e}")
            # Don't print full traceback for missing data - this is expected

    def create_results_tab(self, tab_widget):
        """Create tab for powder results"""
        table = QTableWidget()
        tab_widget.addTab(table, "Results")
        try:
            powder = Powder.get(Powder.id == self.powder_id)
            try:
                results = PowderResults.get(PowderResults.powder == powder)
                headers = ["Property", "Value"]
                data = [
                    ["Water Content", results.water_content],
                    ["Skeletal Density", results.skeletal_density],
                    ["Sphericity", results.sphericity],
                    ["Symmetry", results.symmetry],
                    ["Aspect Ratio", results.aspect_ratio],
                    ["D10", results.d10],
                    ["D50", results.d50],
                    ["D90", results.d90],
                    ["XCMin10", results.xcmin10],
                    ["XCMin50", results.xcmin50],
                    ["XCMin90", results.xcmin90],
                    ["% Weight > 53", results.perc_wt_gt_53],
                    ["% Weight > 63", results.perc_wt_gt_63],
                    ["Apparent Density", results.apparent_dens]
                ]
                if self.edit_mode:
                    table.setColumnCount(3)
                    table.setHorizontalHeaderLabels(["Property", "Value", "Delete"])
                else:
                    table.setColumnCount(2)
                    table.setHorizontalHeaderLabels(headers)
                table.setRowCount(len(data))
                for i, (field, value) in enumerate(data):
                    field_item = QTableWidgetItem(field)
                    field_item.setFlags(field_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    table.setItem(i, 0, field_item)
                    value_item = QTableWidgetItem(str(value) if value is not None else "")
                    if self.edit_mode:
                        value_item.setFlags(value_item.flags() | Qt.ItemFlag.ItemIsEditable)
                    else:
                        value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    table.setItem(i, 1, value_item)
                    if self.edit_mode:
                        delete_btn = QPushButton()
                        delete_btn.setText("🗑️")
                        delete_btn.setStyleSheet("color: #c00; font-size: 16px; font-weight: bold;")
                        delete_btn.setToolTip(f"Delete value for {field}")
                        def make_delete_func(field_name, row_idx):
                            def delete_field():
                                from main import find_non_nullable_dependencies
                                msg = QMessageBox(self)
                                msg.setIcon(QMessageBox.Icon.Warning)
                                msg.setWindowTitle("Confirm Delete")
                                msg.setText(f"Are you sure you want to delete the value for {field_name}?")
                                msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                                msg.setDefaultButton(QMessageBox.StandardButton.No)
                                msg.setStyleSheet("QLabel{min-width:250px; font-size:14px;} QPushButton{min-width:60px;}")
                                reply = msg.exec()
                                if reply == QMessageBox.StandardButton.Yes:
                                    setattr(results, field_name.lower().replace(' ', '_').replace('%', 'perc').replace('>', 'gt').replace('.', '').replace('(', '').replace(')', ''), None)
                                    results.save()
                                    table.setItem(row_idx, 1, QTableWidgetItem(""))
                            return delete_field
                        delete_btn.clicked.connect(make_delete_func(field, i))
                        table.setCellWidget(i, 2, delete_btn)
                if self.edit_mode:
                    def on_cell_changed(row, col):
                        if col == 1:
                            field = table.item(row, 0).text()
                            new_value = table.item(row, 1).text()
                            try:
                                float_val = float(new_value) if new_value else None
                            except Exception:
                                float_val = None
                            setattr(results, field.lower().replace(' ', '_').replace('%', 'perc').replace('>', 'gt').replace('.', '').replace('(', '').replace(')', ''), float_val)
                            results.save()
                    table.cellChanged.connect(on_cell_changed)
                # Tab-level delete button
                # This logic is now handled by _update_delete_button
            except PowderResults.DoesNotExist:
                headers = ["Property", "Value"]
                table.setColumnCount(2)
                table.setHorizontalHeaderLabels(headers)
                table.setRowCount(14)
                for i, field in enumerate([
                    "Water Content", "Skeletal Density", "Sphericity", "Symmetry", "Aspect Ratio", "D10", "D50", "D90", "XCMin10", "XCMin50", "XCMin90", "% Weight > 53", "% Weight > 63", "Apparent Density"]):
                    field_item = QTableWidgetItem(field)
                    field_item.setFlags(field_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    table.setItem(i, 0, field_item)
                    table.setItem(i, 1, QTableWidgetItem("No data"))
                table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        except Exception as e:
            print(f"Error loading powder results: {e}")
            # Don't print full traceback for missing data - this is expected


class SettingDetailWindow(QMainWindow):
    """Window to display detailed setting information"""
    def __init__(self, setting_id, edit_mode=False):
        super().__init__()
        self.setting_id = setting_id
        self.edit_mode = edit_mode
        self.setWindowTitle(f"Setting Details - ID: {setting_id}")
        self.setGeometry(200, 200, 1200, 600)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        self.load_setting_details(layout)

    def load_setting_details(self, layout):
        try:
            setting = Setting.get(Setting.id == self.setting_id)
        except Exception:
            header_label = QLabel(f"Setting: {self.setting_id}")
            header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px; color: #a00;")
            layout.addWidget(header_label)
            msg = QLabel("This setting record does not exist or has been deleted.")
            msg.setStyleSheet("color: #a00; font-style: italic; margin: 10px;")
            layout.addWidget(msg)
            return
        try:
            header_label = QLabel(f"Setting: {setting.name}")
            header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
            layout.addWidget(header_label)
            name_label = QLabel(f"Name: {setting.name if setting.name else ''}")
            name_label.setStyleSheet("font-size: 14px; margin: 5px 10px 0 10px;")
            layout.addWidget(name_label)
            desc_label = QLabel(f"Description: {setting.description if setting.description else ''}")
            desc_label.setStyleSheet("font-size: 13px; margin: 0 10px 10px 10px;")
            layout.addWidget(desc_label)
            # Add full-table delete button
            if self.edit_mode:
                self.delete_setting_btn_layout = QHBoxLayout()
                self.delete_setting_btn = QPushButton("Delete Setting")
                self.delete_setting_btn.setToolTip("Delete the entire setting record")
                self.delete_setting_btn.setStyleSheet("background-color: #c00; color: white; font-weight: bold; min-width: 100px; min-height: 28px; margin: 2px 0px 2px 0px; padding: 2px 8px;")
                self.delete_setting_btn_layout.addWidget(self.delete_setting_btn)
                self.delete_setting_btn_layout.addStretch()
                layout.addLayout(self.delete_setting_btn_layout)
                def confirm_delete():
                    from main import find_non_nullable_dependencies
                    pk = setting.id
                    dependencies = find_non_nullable_dependencies(type(setting), pk)
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setWindowTitle("Confirm Delete")
                    warn_text = "Are you sure you want to delete this setting record?"
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
                        setting.delete_instance()
                        self.close()
                self.delete_setting_btn.clicked.connect(confirm_delete)
            parameters = ["Power", "Scan Speed", "Layer Thickness", "Hatch Distance"]
            features = [
                ("Hatch Up Skin", setting.hatch_up_skin),
                ("Hatch Infill", setting.hatch_infill),
                ("Hatch Down Skin", setting.hatch_down_skin),
                ("Contour On Part", setting.contour_on_part),
                ("Contour Standard", setting.contour_standard),
                ("Contour Down", setting.contour_down),
                ("Edge", setting.edge),
                ("Core", setting.core),
                ("Support", setting.support)
            ]
            headers = ["Parameter"] + [feature_name for feature_name, _ in features if _ is not None]
            table_headers = headers + (["Delete"] if self.edit_mode else [])
            table = QTableWidget()
            layout.addWidget(table)
            table.setColumnCount(len(table_headers))
            table.setHorizontalHeaderLabels(table_headers)
            table.setRowCount(len(parameters))
            for row, param in enumerate(parameters):
                param_item = QTableWidgetItem(param)
                param_item.setFlags(param_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(row, 0, param_item)
                for col, (feature_name, feature_setting) in enumerate(features):
                    if feature_setting is not None:
                        if param == "Power":
                            value = feature_setting.power
                        elif param == "Scan Speed":
                            value = feature_setting.scan_speed
                        elif param == "Layer Thickness":
                            value = feature_setting.layer_thick
                        elif param == "Hatch Distance":
                            value = feature_setting.hatch_dist
                        else:
                            value = None
                        value_item = QTableWidgetItem(str(value) if value is not None else "")
                        if self.edit_mode:
                            value_item.setFlags(value_item.flags() | Qt.ItemFlag.ItemIsEditable)
                        else:
                            value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                        table.setItem(row, col + 1, value_item)
                # Row delete button
                if self.edit_mode:
                    delete_btn = QPushButton()
                    delete_btn.setText("🗑️")
                    delete_btn.setStyleSheet("color: #c00; font-size: 16px; font-weight: bold;")
                    delete_btn.setToolTip(f"Clear all values for {param}")
                    def make_delete_func(row_idx, param_name):
                        def delete_param():
                            msg = QMessageBox(self)
                            msg.setIcon(QMessageBox.Icon.Warning)
                            msg.setWindowTitle("Confirm Clear")
                            msg.setText(f"Are you sure you want to clear all values for {param_name}?")
                            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                            msg.setDefaultButton(QMessageBox.StandardButton.No)
                            msg.setStyleSheet("QLabel{min-width:250px; font-size:14px;} QPushButton{min-width:60px;}")
                            reply = msg.exec()
                            if reply == QMessageBox.StandardButton.Yes:
                                for col, (feature_name, feature_setting) in enumerate(features):
                                    if feature_setting is not None:
                                        if param_name == "Power":
                                            feature_setting.power = None
                                        elif param_name == "Scan Speed":
                                            feature_setting.scan_speed = None
                                        elif param_name == "Layer Thickness":
                                            feature_setting.layer_thick = None
                                        elif param_name == "Hatch Distance":
                                            feature_setting.hatch_dist = None
                                        feature_setting.save()
                                        table.setItem(row_idx, col + 1, QTableWidgetItem(""))
                        return delete_param
                    delete_btn.clicked.connect(make_delete_func(row, param))
                    table.setCellWidget(row, len(table_headers)-1, delete_btn)
            if self.edit_mode:
                def on_cell_changed(row, col):
                    if col == 0 or (self.edit_mode and col == len(table_headers)-1):
                        return
                    param = table.item(row, 0).text()
                    feature_name = headers[col]
                    feature_setting = getattr(setting, feature_name.lower().replace(' ', '_'))
                    new_value = table.item(row, col).text()
                    try:
                        float_val = float(new_value) if new_value else None
                    except Exception:
                        float_val = None
                    if param == "Power":
                        feature_setting.power = float_val
                    elif param == "Scan Speed":
                        feature_setting.scan_speed = float_val
                    elif param == "Layer Thickness":
                        feature_setting.layer_thick = float_val
                    elif param == "Hatch Distance":
                        feature_setting.hatch_dist = float_val
                    feature_setting.save()
                table.cellChanged.connect(on_cell_changed)
            table.resizeColumnsToContents()
        except Exception as e:
            print(f"Error loading setting details: {e}")

class CouponDetailWindow(QMainWindow):
    """Window to display only coupon composition information"""
    def __init__(self, coupon_id, edit_mode=False):
        super().__init__()
        self.coupon_id = coupon_id
        self.edit_mode = edit_mode
        self.setWindowTitle(f"Coupon Composition Details - ID: {coupon_id}")
        self.setGeometry(200, 200, 600, 400)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        self.load_coupon_composition(layout)

    def load_coupon_composition(self, layout):
        from models.coupons.coupon_composition import CouponComposition
        from PyQt6.QtWidgets import QLabel
        try:
            composition = CouponComposition.get(CouponComposition.coupon == self.coupon_id)
            comp_table = QTableWidget()
            layout.addWidget(QLabel("Composition:"))
            layout.addWidget(comp_table)
            fields = [f for f in composition._meta.fields.keys() if f != 'coupon']
            if self.edit_mode:
                comp_table.setColumnCount(3)
                comp_table.setHorizontalHeaderLabels(["Element", "Value", "Delete"])
            else:
                comp_table.setColumnCount(2)
                comp_table.setHorizontalHeaderLabels(["Element", "Value"])
            comp_table.setRowCount(len(fields))
            for i, field in enumerate(fields):
                field_item = QTableWidgetItem(field)
                field_item.setFlags(field_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                comp_table.setItem(i, 0, field_item)
                value_item = QTableWidgetItem(str(getattr(composition, field)) if getattr(composition, field) is not None else "")
                if self.edit_mode:
                    value_item.setFlags(value_item.flags() | Qt.ItemFlag.ItemIsEditable)
                else:
                    value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                comp_table.setItem(i, 1, value_item)
                if self.edit_mode:
                    delete_btn = QPushButton()
                    delete_btn.setText("🗑️")
                    delete_btn.setStyleSheet("color: #c00; font-size: 16px; font-weight: bold;")
                    delete_btn.setToolTip(f"Delete value for {field}")
                    def make_delete_func(field_name, row_idx):
                        def delete_field():
                            msg = QMessageBox(self)
                            msg.setIcon(QMessageBox.Icon.Warning)
                            msg.setWindowTitle("Confirm Delete")
                            msg.setText(f"Are you sure you want to delete the value for {field_name}?")
                            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                            msg.setDefaultButton(QMessageBox.StandardButton.No)
                            msg.setStyleSheet("QLabel{min-width:250px; font-size:14px;} QPushButton{min-width:60px;}")
                            reply = msg.exec()
                            if reply == QMessageBox.StandardButton.Yes:
                                setattr(composition, field_name, None)
                                composition.save()
                                comp_table.setItem(row_idx, 1, QTableWidgetItem(""))
                        return delete_field
                    delete_btn.clicked.connect(make_delete_func(field, i))
                    comp_table.setCellWidget(i, 2, delete_btn)
            if self.edit_mode:
                def on_cell_changed(row, col):
                    if col == 1:
                        field = comp_table.item(row, 0).text()
                        new_value = comp_table.item(row, 1).text()
                        try:
                            float_val = float(new_value) if new_value else None
                        except Exception:
                            float_val = None
                        setattr(composition, field, float_val)
                        composition.save()
                comp_table.cellChanged.connect(on_cell_changed)
            # Full-table delete button
            if self.edit_mode:
                delete_btn = QPushButton("Delete Composition")
                delete_btn.setToolTip("Delete the entire composition record")
                delete_btn.setStyleSheet("background-color: #c00; color: white; font-weight: bold; min-width: 100px; min-height: 28px; margin: 2px 0px 2px 0px; padding: 2px 8px;")
                def confirm_delete():
                    from main import find_non_nullable_dependencies
                    pk = composition.coupon.id
                    dependencies = find_non_nullable_dependencies(type(composition), pk)
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setWindowTitle("Confirm Delete")
                    warn_text = "Are you sure you want to delete this composition record?"
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
                        composition.delete_instance()
                        comp_table.setRowCount(0)
                        comp_table.setColumnCount(0)
                delete_btn.clicked.connect(confirm_delete)
                layout.addWidget(delete_btn)
        except CouponComposition.DoesNotExist:
            no_comp_label = QLabel("No composition data available for this coupon")
            no_comp_label.setStyleSheet("color: #666; font-style: italic; margin: 10px;")
            layout.addWidget(no_comp_label)
        except Exception as e:
            print(f"Error loading coupon composition: {e}")
            import traceback
            traceback.print_exc()


class CouponArrayDetailWindow(QMainWindow):
    """Window to display detailed coupon array information"""
    def __init__(self, coupon_array_id, edit_mode=False):
        super().__init__()
        self.coupon_array_id = coupon_array_id
        self.edit_mode = edit_mode
        self.setWindowTitle(f"Coupon Array Details - ID: {coupon_array_id}")
        self.setGeometry(200, 200, 1600, 800)
        self.detail_windows = []
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        self.load_coupon_array_details(layout)

    def load_coupon_array_details(self, layout):
        try:
            coupon_array = CouponArray.get(CouponArray.id == self.coupon_array_id)
        except Exception:
            header_label = QLabel(f"Coupon Array: {self.coupon_array_id}")
            header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px; color: #a00;")
            layout.addWidget(header_label)
            msg = QLabel("This coupon array record does not exist or has been deleted.")
            msg.setStyleSheet("color: #a00; font-style: italic; margin: 10px;")
            layout.addWidget(msg)
            return
        try:
            header_label = QLabel(f"Coupon Array: {coupon_array.name}")
            header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
            layout.addWidget(header_label)
            desc_label = QLabel(f"Description: {coupon_array.description}")
            desc_label.setStyleSheet("margin: 5px;")
            layout.addWidget(desc_label)
            # Add full-table delete button
            if self.edit_mode:
                self.delete_couponarray_btn_layout = QHBoxLayout()
                self.delete_couponarray_btn = QPushButton("Delete Coupon Array")
                self.delete_couponarray_btn.setToolTip("Delete the entire coupon array record")
                self.delete_couponarray_btn.setStyleSheet("background-color: #c00; color: white; font-weight: bold; min-width: 100px; min-height: 28px; margin: 2px 0px 2px 0px; padding: 2px 8px;")
                self.delete_couponarray_btn_layout.addWidget(self.delete_couponarray_btn)
                self.delete_couponarray_btn_layout.addStretch()
                layout.addLayout(self.delete_couponarray_btn_layout)
                def confirm_delete():
                    from main import find_non_nullable_dependencies
                    pk = coupon_array.id
                    dependencies = find_non_nullable_dependencies(type(coupon_array), pk)
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setWindowTitle("Confirm Delete")
                    warn_text = "Are you sure you want to delete this coupon array record?"
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
                        coupon_array.delete_instance()
                        self.close()
                self.delete_couponarray_btn.clicked.connect(confirm_delete)
            # Add full-table clear button (not delete)
            if self.edit_mode:
                self.clear_couponarray_btn_layout = QHBoxLayout()
                self.clear_couponarray_btn = QPushButton("Clear All Coupons")
                self.clear_couponarray_btn.setToolTip("Remove all coupons from this array (does not delete the array itself)")
                self.clear_couponarray_btn.setStyleSheet("background-color: #c00; color: white; font-weight: bold; min-width: 140px; min-height: 28px; margin: 2px 0px 2px 0px; padding: 2px 8px;")
                self.clear_couponarray_btn_layout.addWidget(self.clear_couponarray_btn)
                self.clear_couponarray_btn_layout.addStretch()
                layout.addLayout(self.clear_couponarray_btn_layout)
                def confirm_clear():
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setWindowTitle("Confirm Clear")
                    warn_text = "Are you sure you want to remove all coupons from this array? This cannot be undone. The array object itself will remain."
                    msg.setText(warn_text)
                    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    msg.setDefaultButton(QMessageBox.StandardButton.No)
                    msg.setStyleSheet("QLabel{min-width:250px; font-size:14px;} QPushButton{min-width:60px;}")
                    reply = msg.exec()
                    if reply == QMessageBox.StandardButton.Yes:
                        for i in range(1, 257):
                            setattr(coupon_array, f'coupon_{i}', None)
                        coupon_array.save()
                        # Reload the table to reflect the cleared coupons
                        for row_idx in range(table.rowCount()):
                            for col in range(1, 8):
                                table.setItem(row_idx, col, QTableWidgetItem(""))
                self.clear_couponarray_btn.clicked.connect(confirm_clear)
            headers = ["Slot", "Coupon Name", "Description", "X", "Y", "Z", "Direction", "Is Preset", "Details"]
            if self.edit_mode:
                headers += ["Delete"]
            table = QTableWidget()
            layout.addWidget(table)
            coupon_fields = ["name", "description", "x_position", "y_position", "z_position", "direction", "is_preset"]
            data = []
            for i in range(1, 257):
                coupon = getattr(coupon_array, f'coupon_{i}', None)
                row = [i]
                if coupon:
                    row += [getattr(coupon, f) for f in coupon_fields]
                else:
                    row += ["", "", "", "", "", "", ""]
                data.append(row)
            table.setRowCount(len(data))
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            for row_idx, row_data in enumerate(data):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    if col_idx == 0:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    elif self.edit_mode and col_idx not in (0, 8, len(headers)-1):
                        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                    else:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    table.setItem(row_idx, col_idx, item)
                # Details button (only present if coupon exists and has composition data)
                coupon = getattr(coupon_array, f'coupon_{row_idx+1}', None)
                if coupon:
                    # Check if this coupon has composition data
                    from models.coupons.coupon_composition import CouponComposition
                    try:
                        composition = CouponComposition.get(CouponComposition.coupon == coupon.id)
                        has_composition = True
                    except Exception:
                        has_composition = False
                    
                    if has_composition:
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
                        def make_mouse_press_event(coupon_id):
                            def mousePressEvent(event):
                                if event.button() == Qt.MouseButton.LeftButton:
                                    self.show_coupon_details(coupon_id)
                            return mousePressEvent
                        details_label.mousePressEvent = make_mouse_press_event(coupon.id)
                        table.setCellWidget(row_idx, 8, details_label)
                # Row delete button
                if self.edit_mode:
                    delete_btn = QPushButton()
                    delete_btn.setText("🗑️")
                    delete_btn.setStyleSheet("color: #c00; font-size: 16px; font-weight: bold;")
                    delete_btn.setToolTip(f"Remove coupon from slot {row_idx+1}")
                    def make_delete_func(slot_idx):
                        def delete_field():
                            msg = QMessageBox(self)
                            msg.setIcon(QMessageBox.Icon.Warning)
                            msg.setWindowTitle("Confirm Delete")
                            msg.setText(f"Are you sure you want to remove the coupon from slot {slot_idx+1}?")
                            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                            msg.setDefaultButton(QMessageBox.StandardButton.No)
                            msg.setStyleSheet("QLabel{min-width:250px; font-size:14px;} QPushButton{min-width:60px;}")
                            reply = msg.exec()
                            if reply == QMessageBox.StandardButton.Yes:
                                setattr(coupon_array, f'coupon_{slot_idx+1}', None)
                                coupon_array.save()
                                for col in range(1, 8):
                                    table.setItem(slot_idx, col, QTableWidgetItem(""))
                        return delete_field
                    delete_btn.clicked.connect(make_delete_func(row_idx))
                    table.setCellWidget(row_idx, len(headers)-1, delete_btn)
            if self.edit_mode:
                def on_cell_changed(row, col):
                    if col == 0 or col == 8 or col == len(headers)-1:
                        return
                    coupon = getattr(coupon_array, f'coupon_{row+1}', None)
                    if not coupon:
                        return
                    field = coupon_fields[col-1]
                    new_value = table.item(row, col).text()
                    if field == "is_preset":
                        coupon.is_preset = new_value.lower() in ("yes", "true", "1")
                    elif field == "direction":
                        coupon.direction = new_value
                    elif field in ["x_position", "y_position", "z_position"]:
                        try:
                            coupon.__setattr__(field, float(new_value) if new_value else None)
                        except Exception:
                            coupon.__setattr__(field, None)
                    else:
                        coupon.__setattr__(field, new_value)
                    coupon.save()
                table.cellChanged.connect(on_cell_changed)
            table.resizeColumnsToContents()
        except Exception as e:
            print(f"Error loading coupon array details: {e}")

    def show_coupon_details(self, coupon_id):
        window = CouponDeepDetailWindow(coupon_id, edit_mode=self.edit_mode)
        window.show()
        if not hasattr(self, 'detail_windows'):
            self.detail_windows = []
        self.detail_windows.append(window)

class CouponDeepDetailWindow(QMainWindow):
    """Window to display coupon composition with header info"""
    def __init__(self, coupon_id, edit_mode=False):
        super().__init__()
        self.coupon_id = coupon_id
        self.edit_mode = edit_mode
        self.setWindowTitle(f"Coupon Details - ID: {coupon_id}")
        self.setGeometry(200, 200, 700, 500)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        from models.coupons.coupon import Coupon
        try:
            coupon = Coupon.get(Coupon.id == self.coupon_id)
            header_label = QLabel(f"Coupon: {coupon.id}")
            header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
            layout.addWidget(header_label)
            desc_label = QLabel(f"Description: {coupon.description if coupon.description else ''}")
            desc_label.setStyleSheet("font-size: 13px; margin: 0 10px 10px 10px;")
            layout.addWidget(desc_label)
            self.create_composition_tab(layout)
        except Exception:
            header_label = QLabel(f"Coupon: {self.coupon_id}")
            header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px; color: #a00;")
            layout.addWidget(header_label)
            msg = QLabel("This coupon record does not exist or has been deleted.")
            msg.setStyleSheet("color: #a00; font-style: italic; margin: 10px;")
            layout.addWidget(msg)
            return

    def create_composition_tab(self, layout):
        from models.coupons.coupon_composition import CouponComposition
        from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QLabel, QHBoxLayout
        try:
            composition = CouponComposition.get(CouponComposition.coupon == self.coupon_id)
            # Add full-table delete button (styled and aligned, above the table)
            if self.edit_mode:
                self.delete_composition_btn_layout = QHBoxLayout()
                self.delete_composition_btn = QPushButton("Delete Composition")
                self.delete_composition_btn.setToolTip("Delete the entire composition record")
                self.delete_composition_btn.setStyleSheet("background-color: #c00; color: white; font-weight: bold; min-width: 100px; min-height: 28px; margin: 2px 0px 2px 0px; padding: 2px 8px;")
                self.delete_composition_btn_layout.addWidget(self.delete_composition_btn)
                self.delete_composition_btn_layout.addStretch()
                layout.addLayout(self.delete_composition_btn_layout)
            comp_table = QTableWidget()
            layout.addWidget(QLabel("Composition:"))
            layout.addWidget(comp_table)
            fields = [f for f in composition._meta.fields.keys() if f != 'coupon']
            if self.edit_mode:
                comp_table.setColumnCount(3)
                comp_table.setHorizontalHeaderLabels(["Element", "Value", "Delete"])
            else:
                comp_table.setColumnCount(2)
                comp_table.setHorizontalHeaderLabels(["Element", "Value"])
            comp_table.setRowCount(len(fields))
            for i, field in enumerate(fields):
                field_item = QTableWidgetItem(field)
                field_item.setFlags(field_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                comp_table.setItem(i, 0, field_item)
                value_item = QTableWidgetItem(str(getattr(composition, field)) if getattr(composition, field) is not None else "")
                if self.edit_mode:
                    value_item.setFlags(value_item.flags() | Qt.ItemFlag.ItemIsEditable)
                else:
                    value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                comp_table.setItem(i, 1, value_item)
                if self.edit_mode:
                    delete_btn = QPushButton()
                    delete_btn.setText("🗑️")
                    delete_btn.setStyleSheet("color: #c00; font-size: 16px; font-weight: bold;")
                    delete_btn.setToolTip(f"Delete value for {field}")
                    def make_delete_func(field_name, row_idx):
                        def delete_field():
                            msg = QMessageBox(self)
                            msg.setIcon(QMessageBox.Icon.Warning)
                            msg.setWindowTitle("Confirm Delete")
                            msg.setText(f"Are you sure you want to delete the value for {field_name}?")
                            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                            msg.setDefaultButton(QMessageBox.StandardButton.No)
                            msg.setStyleSheet("QLabel{min-width:250px; font-size:14px;} QPushButton{min-width:60px;}")
                            reply = msg.exec()
                            if reply == QMessageBox.StandardButton.Yes:
                                setattr(composition, field_name, None)
                                composition.save()
                                comp_table.setItem(row_idx, 1, QTableWidgetItem(""))
                        return delete_field
                    delete_btn.clicked.connect(make_delete_func(field, i))
                    comp_table.setCellWidget(i, 2, delete_btn)
            if self.edit_mode:
                def on_cell_changed(row, col):
                    if col == 1:
                        field = comp_table.item(row, 0).text()
                        new_value = comp_table.item(row, 1).text()
                        try:
                            float_val = float(new_value) if new_value else None
                        except Exception:
                            float_val = None
                        setattr(composition, field, float_val)
                        composition.save()
                comp_table.cellChanged.connect(on_cell_changed)
            # Connect delete button after table is created
            if self.edit_mode:
                def confirm_delete():
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setWindowTitle("Confirm Delete")
                    msg.setText("Are you sure you want to delete this composition record?")
                    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    msg.setDefaultButton(QMessageBox.StandardButton.No)
                    msg.setStyleSheet("QLabel{min-width:250px; font-size:14px;} QPushButton{min-width:60px;}")
                    reply = msg.exec()
                    if reply == QMessageBox.StandardButton.Yes:
                        composition.delete_instance()
                        comp_table.setRowCount(0)
                        comp_table.setColumnCount(0)
                self.delete_composition_btn.clicked.connect(confirm_delete)
        except Exception as e:
            msg = QLabel("No composition data available for this coupon.")
            msg.setStyleSheet("color: #a00; font-style: italic; margin: 10px;")
            layout.addWidget(msg)

class WorkOrderDetailWindow(QMainWindow):
    """Window to display and edit WorkOrder details"""
    def __init__(self, work_order_id, edit_mode=False):
        super().__init__()
        self.work_order_id = work_order_id
        self.edit_mode = edit_mode
        self.setWindowTitle(f"Work Order Details - ID: {work_order_id}")
        self.setGeometry(200, 200, 800, 500)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        self.load_work_order_details(layout)

    def load_work_order_details(self, layout):
        from models.jobs.part_list import PartList
        from models.jobs.part import Part
        from models.jobs.work_order import WorkOrder
        try:
            wo = WorkOrder.get(WorkOrder.id == self.work_order_id)
            try:
                part_list = wo.part_list
            except Exception:
                part_list = None
            header_label = QLabel(f"Work Order: {wo.id}")
            header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
            layout.addWidget(header_label)
            name_label = QLabel(f"Name: {wo.name if wo.name else ''}")
            name_label.setStyleSheet("font-size: 14px; margin: 5px 10px 0 10px;")
            layout.addWidget(name_label)
            desc_label = QLabel(f"Description: {wo.description if wo.description else ''}")
            desc_label.setStyleSheet("font-size: 13px; margin: 0 10px 10px 10px;")
            layout.addWidget(desc_label)
            if not part_list:
                msg = QLabel("No Part List associated or it has been deleted.")
                msg.setStyleSheet("color: #a00; font-style: italic; margin: 10px;")
                layout.addWidget(msg)
                return
            # Add full-table delete button
            if self.edit_mode:
                self.delete_partlist_btn_layout = QHBoxLayout()
                self.delete_partlist_btn = QPushButton("Delete Part List")
                self.delete_partlist_btn.setToolTip("Delete the entire part list record")
                self.delete_partlist_btn.setStyleSheet("background-color: #c00; color: white; font-weight: bold; min-width: 100px; min-height: 28px; margin: 2px 0px 2px 0px; padding: 2px 8px;")
                self.delete_partlist_btn_layout.addWidget(self.delete_partlist_btn)
                self.delete_partlist_btn_layout.addStretch()
                layout.addLayout(self.delete_partlist_btn_layout)
                def confirm_delete():
                    from main import find_non_nullable_dependencies
                    pk = part_list.id
                    dependencies = find_non_nullable_dependencies(type(part_list), pk)
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setWindowTitle("Confirm Delete")
                    warn_text = "Are you sure you want to delete this part list record?"
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
                        part_list.delete_instance()
                        self.close()
                self.delete_partlist_btn.clicked.connect(confirm_delete)
            table = QTableWidget()
            layout.addWidget(table)
            part_fields = ["id", "name", "description", "file_path", "is_complete"]
            headers = ["ID", "Name", "Description", "File Path", "Is Complete", "Delete"] if self.edit_mode else ["ID", "Name", "Description", "File Path", "Is Complete"]
            table.setColumnCount(len(headers))
            # Collect all non-null parts
            parts = []
            for i in range(128):
                part = getattr(part_list, f'part_{i+1}', None)
                if part:
                    parts.append(part)
            table.setRowCount(len(parts))
            table.setHorizontalHeaderLabels(headers)
            for row, part in enumerate(parts):
                for col, field in enumerate(part_fields):
                    value = getattr(part, field)
                    item = QTableWidgetItem(str(value) if value is not None else "")
                    if self.edit_mode and field != "id":
                        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                    else:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    table.setItem(row, col, item)
                # Row delete button
                if self.edit_mode:
                    delete_btn = QPushButton()
                    delete_btn.setText("🗑️")
                    delete_btn.setStyleSheet("color: #c00; font-size: 16px; font-weight: bold;")
                    delete_btn.setToolTip(f"Delete this part from list")
                    def make_delete_func(row_idx, part_idx):
                        def delete_part():
                            msg = QMessageBox(self)
                            msg.setIcon(QMessageBox.Icon.Warning)
                            msg.setWindowTitle("Confirm Delete")
                            msg.setText(f"Are you sure you want to remove this part from the list?")
                            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                            msg.setDefaultButton(QMessageBox.StandardButton.No)
                            msg.setStyleSheet("QLabel{min-width:250px; font-size:14px;} QPushButton{min-width:60px;}")
                            reply = msg.exec()
                            if reply == QMessageBox.StandardButton.Yes:
                                # Shift up logic for part_1 (NOT NULL)
                                if part_idx == 0:
                                    for i in range(1, 128):
                                        next_part = getattr(part_list, f'part_{i+1}', None)
                                        setattr(part_list, f'part_{i}', next_part)
                                    setattr(part_list, f'part_{128}', None)
                                else:
                                    setattr(part_list, f'part_{part_idx+1}', None)
                                part_list.save()
                                table.removeRow(row_idx)
                        return delete_part
                    delete_btn.clicked.connect(make_delete_func(row, row))
                    table.setCellWidget(row, len(headers)-1, delete_btn)
            if self.edit_mode:
                def on_cell_changed(row, col):
                    if col == 0 or col == len(headers)-1:
                        return
                    part = parts[row]
                    field = part_fields[col]
                    new_value = table.item(row, col).text()
                    if field == "is_complete":
                        part.is_complete = new_value.lower() in ("yes", "true", "1")
                    else:
                        setattr(part, field, new_value)
                    part.save()
                table.cellChanged.connect(on_cell_changed)
            table.resizeColumnsToContents()
        except Exception as e:
            print(f"Error loading work order details: {e}")

class JobDetailWindow(QMainWindow):
    """Window to display and edit Job details"""
    def __init__(self, job_id, edit_mode=False):
        super().__init__()
        self.job_id = job_id
        self.edit_mode = edit_mode
        self.setWindowTitle(f"Job Details - ID: {job_id}")
        self.setGeometry(200, 200, 800, 500)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        self.load_job_details(layout)

    def load_job_details(self, layout):
        from models.jobs.part_list import PartList
        from models.jobs.part import Part
        from models.jobs.job import Job
        try:
            job = Job.get(Job.id == self.job_id)
            try:
                part_list = job.part_list
            except Exception:
                part_list = None
            header_label = QLabel(f"Job: {job.id}")
            header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
            layout.addWidget(header_label)
            name_label = QLabel(f"Name: {job.name if job.name else ''}")
            name_label.setStyleSheet("font-size: 14px; margin: 5px 10px 0 10px;")
            layout.addWidget(name_label)
            desc_label = QLabel(f"Description: {job.description if job.description else ''}")
            desc_label.setStyleSheet("font-size: 13px; margin: 0 10px 10px 10px;")
            layout.addWidget(desc_label)
            if not part_list:
                msg = QLabel("No Part List associated or it has been deleted.")
                msg.setStyleSheet("color: #a00; font-style: italic; margin: 10px;")
                layout.addWidget(msg)
                return
            # Add full-table delete button
            if self.edit_mode:
                self.delete_partlist_btn_layout = QHBoxLayout()
                self.delete_partlist_btn = QPushButton("Delete Part List")
                self.delete_partlist_btn.setToolTip("Delete the entire part list record")
                self.delete_partlist_btn.setStyleSheet("background-color: #c00; color: white; font-weight: bold; min-width: 100px; min-height: 28px; margin: 2px 0px 2px 0px; padding: 2px 8px;")
                self.delete_partlist_btn_layout.addWidget(self.delete_partlist_btn)
                self.delete_partlist_btn_layout.addStretch()
                layout.addLayout(self.delete_partlist_btn_layout)
                def confirm_delete():
                    from main import find_non_nullable_dependencies
                    pk = part_list.id
                    dependencies = find_non_nullable_dependencies(type(part_list), pk)
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setWindowTitle("Confirm Delete")
                    warn_text = "Are you sure you want to delete this part list record?"
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
                        part_list.delete_instance()
                        self.close()
                self.delete_partlist_btn.clicked.connect(confirm_delete)
            table = QTableWidget()
            layout.addWidget(table)
            part_fields = ["id", "name", "description", "file_path", "is_complete"]
            headers = ["ID", "Name", "Description", "File Path", "Is Complete", "Delete"] if self.edit_mode else ["ID", "Name", "Description", "File Path", "Is Complete"]
            table.setColumnCount(len(headers))
            # Collect all non-null parts
            parts = []
            for i in range(128):
                part = getattr(part_list, f'part_{i+1}', None)
                if part:
                    parts.append(part)
            table.setRowCount(len(parts))
            table.setHorizontalHeaderLabels(headers)
            for row, part in enumerate(parts):
                for col, field in enumerate(part_fields):
                    value = getattr(part, field)
                    item = QTableWidgetItem(str(value) if value is not None else "")
                    if self.edit_mode and field != "id":
                        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                    else:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    table.setItem(row, col, item)
                # Row delete button
                if self.edit_mode:
                    delete_btn = QPushButton()
                    delete_btn.setText("🗑️")
                    delete_btn.setStyleSheet("color: #c00; font-size: 16px; font-weight: bold;")
                    delete_btn.setToolTip(f"Delete this part from list")
                    def make_delete_func(row_idx, part_idx):
                        def delete_part():
                            msg = QMessageBox(self)
                            msg.setIcon(QMessageBox.Icon.Warning)
                            msg.setWindowTitle("Confirm Delete")
                            msg.setText(f"Are you sure you want to remove this part from the list?")
                            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                            msg.setDefaultButton(QMessageBox.StandardButton.No)
                            msg.setStyleSheet("QLabel{min-width:250px; font-size:14px;} QPushButton{min-width:60px;}")
                            reply = msg.exec()
                            if reply == QMessageBox.StandardButton.Yes:
                                # Shift up logic for part_1 (NOT NULL)
                                if part_idx == 0:
                                    for i in range(1, 128):
                                        next_part = getattr(part_list, f'part_{i+1}', None)
                                        setattr(part_list, f'part_{i}', next_part)
                                    setattr(part_list, f'part_{128}', None)
                                else:
                                    setattr(part_list, f'part_{part_idx+1}', None)
                                part_list.save()
                                table.removeRow(row_idx)
                        return delete_part
                    delete_btn.clicked.connect(make_delete_func(row, row))
                    table.setCellWidget(row, len(headers)-1, delete_btn)
            if self.edit_mode:
                def on_cell_changed(row, col):
                    if col == 0 or col == len(headers)-1:
                        return
                    part = parts[row]
                    field = part_fields[col]
                    new_value = table.item(row, col).text()
                    if field == "is_complete":
                        part.is_complete = new_value.lower() in ("yes", "true", "1")
                    else:
                        setattr(part, field, new_value)
                    part.save()
                table.cellChanged.connect(on_cell_changed)
            table.resizeColumnsToContents()
        except Exception as e:
            print(f"Error loading job details: {e}") 