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
from models.coupons.coupon_composition import CouponComposition


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
        
        # Add powder ID as header and description as subheader
        try:
            powder = Powder.get(Powder.id == self.powder_id)
            header_label = QLabel(f"Powder: {powder.id}")
            header_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
            layout.addWidget(header_label)
            desc_label = QLabel(f"Description: {powder.description}")
            desc_label.setStyleSheet("font-size: 14px; margin: 5px 10px 15px 10px;")
            layout.addWidget(desc_label)
        except Exception as e:
            header_label = QLabel(f"Powder: {self.powder_id}")
            header_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px; color: #a00;")
            layout.addWidget(header_label)
            desc_label = QLabel("Description: (not found)")
            desc_label.setStyleSheet("font-size: 14px; margin: 5px 10px 15px 10px; color: #a00;")
            layout.addWidget(desc_label)
        
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


class CouponDetailWindow(QMainWindow):
    """Window to display only coupon composition information"""
    def __init__(self, coupon_id):
        super().__init__()
        self.coupon_id = coupon_id
        self.setWindowTitle(f"Coupon Composition Details - ID: {coupon_id}")
        self.setGeometry(200, 200, 600, 400)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Only show composition
        self.load_coupon_composition(layout)

    def load_coupon_composition(self, layout):
        """Load and display coupon composition only"""
        from models.coupons.coupon_composition import CouponComposition
        from PyQt6.QtWidgets import QLabel
        try:
            composition = CouponComposition.get(CouponComposition.coupon == self.coupon_id)
            # Create table for composition
            comp_table = DetailTableWidget()
            layout.addWidget(QLabel("Composition:"))
            layout.addWidget(comp_table)
            # Get all non-null composition values
            comp_data = []
            for field_name in ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 
                              'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca',
                              'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn']:
                value = getattr(composition, field_name)
                if value is not None:
                    comp_data.append([field_name, f"{value:.2f}%"])
            if comp_data:
                comp_headers = ["Element", "Value (%)"]
                comp_table.load_data(comp_headers, comp_data)
            else:
                comp_table.setRowCount(1)
                comp_table.setColumnCount(1)
                comp_table.setItem(0, 0, QTableWidgetItem("No composition data available"))
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
    def __init__(self, coupon_array_id):
        super().__init__()
        self.coupon_array_id = coupon_array_id
        self.setWindowTitle(f"Coupon Array Details - ID: {coupon_array_id}")
        self.setGeometry(200, 200, 1600, 800)
        
        # Store detail windows to prevent garbage collection
        self.detail_windows = []
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Load coupon array details
        self.load_coupon_array_details(layout)
    
    def load_coupon_array_details(self, layout):
        """Load and display coupon array information with nested coupon details"""
        try:
            coupon_array = CouponArray.get(CouponArray.id == self.coupon_array_id)
            
            # Coupon array info header
            header_label = QLabel(f"Coupon Array: {coupon_array.name}")
            header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
            layout.addWidget(header_label)
            
            desc_label = QLabel(f"Description: {coupon_array.description}")
            desc_label.setStyleSheet("margin: 5px;")
            layout.addWidget(desc_label)
            
            # Create table for coupons with details buttons
            table = QTableWidget()
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            layout.addWidget(table)
            
            # Collect all non-null coupons that have composition data
            coupons_data = []
            for i in range(1, 257):
                coupon = getattr(coupon_array, f'coupon_{i}', None)
                if coupon:
                    # Check if this coupon has composition data
                    has_composition = False
                    try:
                        CouponComposition.get(CouponComposition.coupon == coupon)
                        has_composition = True
                    except CouponComposition.DoesNotExist:
                        has_composition = False
                    
                    coupons_data.append([
                        i,  # Position
                        coupon.name,
                        coupon.description,
                        coupon.x_position,
                        coupon.y_position,
                        coupon.z_position,
                        coupon.direction,
                        coupon.is_preset,
                        coupon.id,  # Store coupon ID for details button
                        has_composition  # Store whether coupon has composition
                    ])
            
            if not coupons_data:
                table.setRowCount(1)
                table.setColumnCount(1)
                table.setItem(0, 0, QTableWidgetItem("No coupons found in this array"))
                return
            
            headers = ["Position", "Name", "Description", "X Position", "Y Position", "Z Position", "Direction", "Is Preset", "Details"]
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            table.setRowCount(len(coupons_data))
            
            for row, row_data in enumerate(coupons_data):
                for col, value in enumerate(row_data[:-2]):  # Exclude the last two columns (coupon ID and has_composition)
                    table.setItem(row, col, QTableWidgetItem(str(value)))
                
                # Only add details button if coupon has composition data
                if row_data[-1]:  # has_composition is True
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
                    
                    # Use a function factory to bind coupon_id
                    def make_mouse_press_event(coupon_id):
                        def mousePressEvent(event):
                            if event.button() == Qt.MouseButton.LeftButton:
                                self.show_coupon_details(coupon_id)
                        return mousePressEvent
                    details_label.mousePressEvent = make_mouse_press_event(row_data[-2])
                    table.setCellWidget(row, len(headers) - 1, details_label)
                else:
                    # Show "No Data" for coupons without composition
                    no_data_label = QLabel("No Data")
                    no_data_label.setStyleSheet("""
                        QLabel {
                            color: #999;
                            font-style: italic;
                            padding: 2px 6px;
                        }
                    """)
                    no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    table.setCellWidget(row, len(headers) - 1, no_data_label)
            
            table.resizeColumnsToContents()
            
        except Exception as e:
            print(f"Error loading coupon array details: {e}")
            import traceback
            traceback.print_exc()
    
    def show_coupon_details(self, coupon_id):
        """Open coupon details window"""
        try:
            print(f"Opening coupon details for ID: {coupon_id}")
            coupon_window = CouponDetailWindow(coupon_id)
            self.detail_windows.append(coupon_window)  # Store reference to prevent garbage collection
            coupon_window.show()
        except Exception as e:
            print(f"Error showing coupon details: {e}")
            import traceback
            traceback.print_exc() 