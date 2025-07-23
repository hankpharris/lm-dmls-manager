#!/usr/bin/env python3
"""
Detailed view windows for database entities
"""

from PyQt6.QtWidgets import (QMainWindow, QTableWidget, QTableWidgetItem, 
                             QVBoxLayout, QHBoxLayout, QWidget, QPushButton, 
                             QLabel, QScrollArea, QFrame, QGridLayout)
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
    def __init__(self, powder_id):
        super().__init__()
        self.powder_id = powder_id
        self.setWindowTitle(f"Powder Details - {powder_id}")
        self.setGeometry(200, 200, 1000, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget for composition and results
        from PyQt6.QtWidgets import QTabWidget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Create composition tab
        self.create_composition_tab(tab_widget)
        
        # Create results tab
        self.create_results_tab(tab_widget)
    
    def create_composition_tab(self, tab_widget):
        """Create tab for powder composition"""
        table = DetailTableWidget()
        tab_widget.addTab(table, "Composition")
        
        try:
            print(f"Loading composition for powder ID: {self.powder_id}")
            powder = Powder.get(Powder.id == self.powder_id)
            print(f"Found powder: {powder.id} - {powder.description}")
            composition = PowderComposition.get(PowderComposition.powder == powder)
            print(f"Found composition with Fe: {composition.Fe}, Cr: {composition.Cr}")
            
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
            table.load_data(headers, data)
            
        except Exception as e:
            print(f"Error loading powder composition: {e}")
            import traceback
            traceback.print_exc()
    
    def create_results_tab(self, tab_widget):
        """Create tab for powder results"""
        table = DetailTableWidget()
        tab_widget.addTab(table, "Results")
        
        try:
            print(f"Loading results for powder ID: {self.powder_id}")
            powder = Powder.get(Powder.id == self.powder_id)
            print(f"Found powder: {powder.id} - {powder.description}")
            results = PowderResults.get(PowderResults.powder == powder)
            print(f"Found results with water content: {results.water_content}, density: {results.skeletal_density}")
            
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
            table.load_data(headers, data)
            
        except Exception as e:
            print(f"Error loading powder results: {e}")
            import traceback
            traceback.print_exc()


class SettingDetailWindow(QMainWindow):
    """Window to display detailed setting information"""
    def __init__(self, setting_id):
        super().__init__()
        self.setting_id = setting_id
        self.setWindowTitle(f"Setting Details - ID: {setting_id}")
        self.setGeometry(200, 200, 1200, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Load setting details
        self.load_setting_details(layout)
    
    def load_setting_details(self, layout):
        """Load and display all feature settings in table format"""
        try:
            print(f"Loading setting details for ID: {self.setting_id}")
            setting = Setting.get(Setting.id == self.setting_id)
            print(f"Found setting: {setting.id} - {setting.name}")
            
            # Setting info header
            header_label = QLabel(f"Setting: {setting.name}")
            header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
            layout.addWidget(header_label)
            
            desc_label = QLabel(f"Description: {setting.description}")
            desc_label.setStyleSheet("margin: 5px;")
            layout.addWidget(desc_label)
            
            # Create table for all feature settings
            table = DetailTableWidget()
            layout.addWidget(table)
            
            # Define parameter names (row labels)
            parameters = ["Power", "Scan Speed", "Layer Thickness", "Hatch Distance"]
            
            # Define feature names (column headers)
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
            
            print(f"Features found: {[(name, fs.id if fs else None) for name, fs in features]}")
            
            # Create headers (Parameter + all feature names)
            headers = ["Parameter"] + [feature_name for feature_name, _ in features if _ is not None]
            
            # Create data rows
            data = []
            for param in parameters:
                row = [param]
                for feature_name, feature_setting in features:
                    if feature_setting is not None:
                        if param == "Power":
                            row.append(feature_setting.power)
                        elif param == "Scan Speed":
                            row.append(feature_setting.scan_speed)
                        elif param == "Layer Thickness":
                            row.append(feature_setting.layer_thick)
                        elif param == "Hatch Distance":
                            row.append(feature_setting.hatch_dist)
                data.append(row)
            
            print(f"Table data: {data}")
            table.load_data(headers, data)
            
        except Exception as e:
            print(f"Error loading setting details: {e}")
            import traceback
            traceback.print_exc()


class CouponArrayDetailWindow(QMainWindow):
    """Window to display detailed coupon array information"""
    def __init__(self, coupon_array_id):
        super().__init__()
        self.coupon_array_id = coupon_array_id
        self.setWindowTitle(f"Coupon Array Details - ID: {coupon_array_id}")
        self.setGeometry(200, 200, 1600, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget for coupons and compositions
        from PyQt6.QtWidgets import QTabWidget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Create coupons tab
        self.create_coupons_tab(tab_widget)
        
        # Create compositions tab
        self.create_compositions_tab(tab_widget)
    
    def create_coupons_tab(self, tab_widget):
        """Create tab for coupon details"""
        table = DetailTableWidget()
        tab_widget.addTab(table, "Coupons")
        
        try:
            coupon_array = CouponArray.get(CouponArray.id == self.coupon_array_id)
            
            # Collect all non-null coupons
            coupons_data = []
            for i in range(1, 257):
                coupon = getattr(coupon_array, f'coupon_{i}', None)
                if coupon:
                    coupons_data.append([
                        i,  # Position
                        coupon.name,
                        coupon.description,
                        coupon.x_position,
                        coupon.y_position,
                        coupon.z_position,
                        coupon.direction,
                        coupon.is_preset
                    ])
            
            headers = ["Position", "Name", "Description", "X Position", "Y Position", "Z Position", "Direction", "Is Preset"]
            table.load_data(headers, coupons_data)
            
        except Exception as e:
            print(f"Error loading coupon details: {e}")
    
    def create_compositions_tab(self, tab_widget):
        """Create tab for coupon compositions"""
        table = DetailTableWidget()
        tab_widget.addTab(table, "Compositions")
        
        try:
            coupon_array = CouponArray.get(CouponArray.id == self.coupon_array_id)
            
            # Collect all non-null coupon compositions
            compositions_data = []
            for i in range(1, 257):
                coupon = getattr(coupon_array, f'coupon_{i}', None)
                if coupon:
                    compositions_data.append([
                        i,  # Position
                        coupon.name,
                        coupon.coupon_composition.H,
                        coupon.coupon_composition.C,
                        coupon.coupon_composition.O,
                        coupon.coupon_composition.Fe
                    ])
            
            headers = ["Position", "Coupon Name", "H (%)", "C (%)", "O (%)", "Fe (%)"]
            table.load_data(headers, compositions_data)
            
        except Exception as e:
            print(f"Error loading composition details: {e}") 