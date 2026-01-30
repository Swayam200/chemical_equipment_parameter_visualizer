import sys
import os
import requests
import pandas as pd
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QTabWidget, QTableWidget, QTableWidgetItem, QMessageBox, QListWidget, QSplitter, 
                             QDialog, QLineEdit, QFormLayout, QProgressDialog, QScrollArea, QGroupBox, QSlider)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

# Using a standard local URL. In production, this might be an env var.
API_URL = "http://127.0.0.1:8000/api/"

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Access Terminal - Verification Required")
        self.setFixedSize(450, 600)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        
        # Load background image
        # Absolute path to image for reliability in this script
        img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'assets', 'images', 'chemical_plant_login.jpg')
        
        # Main layout with background
        self.setStyleSheet(f"""
            QDialog {{
                background-image: url('{img_path}');
                background-position: center;
                background-repeat: no-repeat;
                border: 2px solid #45a29e;
            }}
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        
        # Glassmorphism Container
        self.container = QWidget()
        self.container.setFixedSize(380, 500)
        self.container.setStyleSheet("""
            QWidget {
                background-color: rgba(11, 12, 16, 0.85);
                border: 1px solid rgba(102, 252, 241, 0.3);
                border-radius: 4px;
            }
        """)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(30, 40, 30, 40)
        container_layout.setSpacing(15)
        
        # Icon / Header
        header_label = QLabel("SYSTEM ACCESS")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("""
            color: #66fcf1;
            font-size: 24px;
            font-weight: bold;
            letter-spacing: 2px;
            background: transparent;
            border: none;
            margin-bottom: 5px;
        """)
        container_layout.addWidget(header_label)
        
        # Sub-header
        self.mode_label = QLabel("> INITIATE LOGIN_SEQUENCE")
        self.mode_label.setAlignment(Qt.AlignCenter)
        self.mode_label.setStyleSheet("""
            color: #45a29e;
            font-family: monospace;
            font-size: 14px;
            background: transparent;
            border: none;
            margin-bottom: 20px;
        """)
        container_layout.addWidget(self.mode_label)
        
        # Form inputs
        self.username = self.create_input("USERNAME")
        self.email = self.create_input("EMAIL_ADDRESS")
        self.password = self.create_input("PASSWORD", is_password=True)
        self.confirm_password = self.create_input("CONFIRM_CREDENTIALS", is_password=True)
        
        container_layout.addWidget(self.username)
        container_layout.addWidget(self.email)
        container_layout.addWidget(self.password)
        container_layout.addWidget(self.confirm_password)
        
        # Hide register fields initially
        self.email.setVisible(False)
        self.confirm_password.setVisible(False)
        
        # Action Button
        self.action_btn = QPushButton("ESTABLISH_LINK")
        self.action_btn.setCursor(Qt.PointingHandCursor)
        self.action_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(69, 162, 158, 0.1); 
                color: #66fcf1; 
                padding: 12px; 
                font-weight: bold; 
                border: 1px solid #45a29e;
                border-radius: 2px;
                font-family: monospace;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #45a29e;
                color: #0b0c10;
            }
        """)
        self.action_btn.clicked.connect(self.handle_action)
        container_layout.addWidget(self.action_btn)
        
        # Toggle Button
        self.toggle_btn = QPushButton("[ NEW_USER? REGISTER ]")
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #8b949e;
                font-family: monospace;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #66fcf1;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_mode)
        container_layout.addWidget(self.toggle_btn)
        
        # Close Button (since frameless)
        self.exit_btn = QPushButton("TERMINATE_SESSION")
        self.exit_btn.setCursor(Qt.PointingHandCursor)
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #fc2044;
                font-family: monospace;
                font-size: 11px;
                margin-top: 10px;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        self.exit_btn.clicked.connect(self.reject)
        container_layout.addWidget(self.exit_btn)
        
        container_layout.addStretch()
        
        main_layout.addWidget(self.container)
        self.setLayout(main_layout)
        
        self.is_register_mode = False

    def create_input(self, placeholder, is_password=False):
        inp = QLineEdit()
        inp.setPlaceholderText(f"[{placeholder}]")
        if is_password:
            inp.setEchoMode(QLineEdit.Password)
        inp.setStyleSheet("""
            QLineEdit {
                background-color: #0d1117;
                border: 1px solid #1f2833;
                color: #66fcf1;
                padding: 10px;
                font-family: monospace;
                border-radius: 0px;
            }
            QLineEdit:focus {
                border: 1px solid #66fcf1;
                background-color: #000;
            }
        """)
        return inp

    def toggle_mode(self):
        self.is_register_mode = not self.is_register_mode
        
        if self.is_register_mode:
            self.mode_label.setText("> INITIATE REGISTRATION_SEQUENCE")
            self.action_btn.setText("CREATE_CREDENTIALS")
            self.toggle_btn.setText("[ EXISTING_USER? LOGIN ]")
            self.email.setVisible(True)
            self.confirm_password.setVisible(True)
        else:
            self.mode_label.setText("> INITIATE LOGIN_SEQUENCE")
            self.action_btn.setText("ESTABLISH_LINK")
            self.toggle_btn.setText("[ NEW_USER? REGISTER ]")
            self.email.setVisible(False)
            self.confirm_password.setVisible(False)
    
    def handle_action(self):
        if self.is_register_mode:
            self.handle_register()
        else:
            self.accept()  # Login
    
    def handle_register(self):
        username = self.username.text()
        email = self.email.text()
        password = self.password.text()
        confirm = self.confirm_password.text()
        
        if not username or not email or not password or not confirm:
            QMessageBox.warning(self, "Error", "MISSING_FIELDS")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Error", "PASSWORD_MISMATCH")
            return
        
        if len(password) < 8:
            QMessageBox.warning(self, "Error", "PASSWORD_TOO_SHORT_MIN_8")
            return
        
        try:
            res = requests.post(f"{API_URL}register/", json={
                'username': username,
                'email': email,
                'password': password
            })
            
            if res.status_code == 201:
                QMessageBox.information(self, "Success", "REGISTRATION_COMPLETE. PROCEED TO LOGIN.")
                self.toggle_mode()
            else:
                error_msg = res.json().get('error', 'REGISTRATION_FAILED')
                QMessageBox.warning(self, "Failed", error_msg.upper())
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"CONNECTION_FAILED: {e}")

    def get_credentials(self):
        return self.username.text(), self.password.text()

class MainWindow(QMainWindow):
    # Signal to notify parent that user wants to logout
    logout_signal = None  # Will be set by parent
    
    def __init__(self, auth_header, username="", logout_callback=None):
        super().__init__()
        self.auth_header = auth_header
        self.username = username
        self.logout_callback = logout_callback
        
        self.setWindowTitle("Chemical Equipment Visualizer (Desktop)")
        self.resize(1200, 800)
        self.current_data = None
        
        # Auto-refresh timer for history (every 30 seconds)
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_history_silent)
        self.timer.start(30000)

        # Let's set up the main layout.
        # We'll use a split view: History Sidebar on the left, Main Content on the right.
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # --- Sidebar (History) ---
        sidebar_layout = QVBoxLayout()
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.load_history_item)
        
        # Styling the sidebar header to pop a bit
        header_label = QLabel("<b>Recent Uploads</b>")
        header_label.setStyleSheet("color: #e6edf3; font-size: 14px; margin-bottom: 5px;")
        
        sidebar_layout.addWidget(header_label)
        sidebar_layout.addWidget(self.history_list)
        
        # Auto-refresh happens every 30 seconds, so manual refresh button is not needed
        # Users can see updates automatically
        
        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar_layout)
        sidebar_widget.setFixedWidth(250)
        # Give the sidebar a distinct background color
        sidebar_widget.setStyleSheet("""
            QWidget {
                background-color: #0b0c10; 
                border-right: 1px solid #1f2833;
            }
            QListWidget {
                border: none;
                background-color: #0b0c10;
                color: #c5c6c7;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #1f2833;
            }
            QListWidget::item:selected {
                background-color: #1f2833;
                color: #66fcf1;
                border-left: 3px solid #66fcf1;
            }
            QListWidget::item:hover {
                background-color: #1f2833;
            }
        """)

        # --- Main Content Area ---
        main_content_layout = QVBoxLayout()
        
        # Top Bar: The primary action is uploading a CSV.
        top_bar = QHBoxLayout()
        self.upload_btn = QPushButton("Upload CSV")
        # Using a nice blue accent for the primary action
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(69, 162, 158, 0.1); 
                color: #66fcf1; 
                padding: 10px 20px; 
                font-weight: bold; 
                border-radius: 2px;
                border: 1px solid #45a29e;
                font-family: monospace;
            }
            QPushButton:hover {
                background-color: #45a29e;
                color: #0b0c10;
            }
        """)
        self.upload_btn.clicked.connect(self.upload_file)
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #8b949e; margin-left: 10px;")
        
        # Download PDF Report button
        self.pdf_btn = QPushButton("📄 Download PDF Report")
        self.pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(32, 252, 143, 0.1); 
                color: #20fc8f; 
                padding: 10px 20px; 
                font-weight: bold; 
                border-radius: 2px;
                border: 1px solid #20fc8f;
                font-family: monospace;
            }
            QPushButton:hover {
                background-color: #20fc8f;
                color: #0b0c10;
            }
            QPushButton:disabled {
                background-color: #1f2833;
                color: #45a29e;
                border: 1px solid #1f2833;
            }
        """)
        self.pdf_btn.clicked.connect(self.download_pdf_report)
        self.pdf_btn.setEnabled(False)  # Disabled until data is loaded
        
        top_bar.addWidget(self.upload_btn)
        top_bar.addWidget(self.pdf_btn)
        top_bar.addWidget(self.status_label)
        top_bar.addStretch()
        
        # User info and logout button
        if self.username:
            user_label = QLabel(f"👤 {self.username}")
            user_label.setStyleSheet("color: #8b949e; font-size: 12px; margin-right: 10px;")
            top_bar.addWidget(user_label)
        
        self.logout_btn = QPushButton("🚪 LOGOUT")
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                color: #fc2044; 
                padding: 10px 20px; 
                font-weight: bold; 
                border-radius: 2px;
                border: 1px solid #fc2044;
                font-family: monospace;
            }
            QPushButton:hover {
                background-color: #fc2044;
                color: #0b0c10;
            }
        """)
        self.logout_btn.clicked.connect(self.handle_logout)
        top_bar.addWidget(self.logout_btn)
        
        main_content_layout.addLayout(top_bar)

        # Tabs for different views (Visual Dashboard vs Raw Data Table)
        self.tabs = QTabWidget()
        self.dashboard_tab = QWidget()
        self.data_tab = QWidget()
        
        # Setting up the individual tab contents
        self.setup_dashboard_ui()
        self.setup_data_ui()
        
        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.addTab(self.data_tab, "Raw Data")
        
        main_content_layout.addWidget(self.tabs)

        main_content_widget = QWidget()
        main_content_widget.setLayout(main_content_layout)
        # Main content background
        main_content_widget.setStyleSheet("background-color: #0b0c10;")

        # Combine them with a Splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(sidebar_widget)
        splitter.addWidget(main_content_widget)
        splitter.setHandleWidth(1)
        layout.addWidget(splitter)
        
        # Remove margins to make it look cleaner
        layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setStyleSheet("background-color: #0b0c10; color: #c5c6c7; font-family: 'JetBrains Mono', 'Consolas', monospace;")

        # Load initial data
        self.refresh_history()
        self.fetch_threshold_settings()

    def setup_dashboard_ui(self):
        """Sets up the charts and summary cards with advanced analytics."""
        # Create scroll area for dashboard
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #0b0c10; }")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # 1. Summary Stats Cards
        stats_layout = QHBoxLayout()
        self.stat_labels = {
            "total": QLabel("Total\n-"),
            "flow": QLabel("Avg Flowrate\n-\n(Min: - | Max: -)"),
            "pressure": QLabel("Avg Pressure\n-\n(Min: - | Max: -)"),
            "temp": QLabel("Avg Temp\n-\n(Min: - | Max: -)")
        }
        
        for lbl in self.stat_labels.values():
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("""
                background-color: rgba(31, 40, 51, 0.6); 
                border: 1px solid #1f2833; 
                border-radius: 2px; 
                color: #66fcf1; 
                padding: 15px; 
                font-size: 12px;
                font-weight: bold;
                font-family: monospace;
            """)
            stats_layout.addWidget(lbl)
        
        layout.addLayout(stats_layout)

        # 2. Outlier Alert (if any)
        self.outlier_group = QGroupBox("⚠️ Outlier Detection")
        self.outlier_group.setStyleSheet("""
            QGroupBox {
                background-color: rgba(252, 32, 68, 0.05);
                border: 1px solid #fc2044;
                border-radius: 2px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                color: #fc2044;
                font-family: monospace;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        outlier_layout = QVBoxLayout()
        self.outlier_label = QLabel("No outliers detected.")
        self.outlier_label.setStyleSheet("color: #8b949e; font-weight: normal;")
        self.outlier_label.setWordWrap(True)
        outlier_layout.addWidget(self.outlier_label)
        self.outlier_group.setLayout(outlier_layout)
        self.outlier_group.setVisible(False)
        layout.addWidget(self.outlier_group)

        # 4. Main Charts Area
        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.figure.patch.set_facecolor('#0b0c10')
        
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: #0b0c10;")
        
        # Add navigation toolbar for zoom/pan
        self.nav_toolbar = NavigationToolbar(self.canvas, self)
        self.nav_toolbar.setStyleSheet("""
            QToolBar {
                background-color: #1f2833;
                border: 1px solid #45a29e;
                border-radius: 4px;
                padding: 4px;
                spacing: 4px;
            }
            QToolButton {
                background-color: #e8e8e8;
                border: 1px solid #45a29e;
                border-radius: 3px;
                padding: 6px;
                margin: 2px;
                min-width: 28px;
                min-height: 28px;
            }
            QToolButton:hover {
                background-color: #66fcf1;
                border-color: #66fcf1;
            }
            QToolButton:pressed, QToolButton:checked {
                background-color: #45a29e;
            }
        """)
        layout.addWidget(self.nav_toolbar)
        layout.addWidget(self.canvas)

        # 5. Advanced Analytics Section (Collapsible)
        self.advanced_group = QGroupBox("🔬 Advanced Analytics (Click to expand)")
        self.advanced_group.setCheckable(True)
        self.advanced_group.setChecked(False)
        self.advanced_group.setStyleSheet("""
            QGroupBox {
                background-color: rgba(31, 40, 51, 0.4);
                border: 1px solid #45a29e;
                border-radius: 2px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                color: #45a29e;
                font-family: monospace;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        advanced_layout = QVBoxLayout()
        
        # Type Comparison Chart
        self.advanced_figure = Figure(figsize=(10, 8), dpi=100)
        self.advanced_figure.patch.set_facecolor('#0b0c10')
        self.advanced_canvas = FigureCanvas(self.advanced_figure)
        self.advanced_canvas.setStyleSheet("background-color: #0b0c10;")
        
        # Add navigation toolbar for advanced charts
        self.advanced_nav_toolbar = NavigationToolbar(self.advanced_canvas, self)
        self.advanced_nav_toolbar.setStyleSheet("""
            QToolBar {
                background-color: #1f2833;
                border: 1px solid #45a29e;
                border-radius: 4px;
                padding: 4px;
                spacing: 4px;
            }
            QToolButton {
                background-color: #e8e8e8;
                border: 1px solid #45a29e;
                border-radius: 3px;
                padding: 6px;
                margin: 2px;
                min-width: 28px;
                min-height: 28px;
            }
            QToolButton:hover {
                background-color: #66fcf1;
                border-color: #66fcf1;
            }
            QToolButton:pressed, QToolButton:checked {
                background-color: #45a29e;
            }
        """)
        advanced_layout.addWidget(self.advanced_nav_toolbar)
        advanced_layout.addWidget(self.advanced_canvas)
        
        # Stats summary
        self.stats_summary_label = QLabel("")
        self.stats_summary_label.setStyleSheet("color: #c5c6c7; padding: 10px; background-color: #0b0c10; font-size: 11px; font-family: monospace;")
        self.stats_summary_label.setWordWrap(True)
        advanced_layout.addWidget(self.stats_summary_label)
        
        self.advanced_group.setLayout(advanced_layout)
        
        # Connect toggle signal to show/hide content
        self.advanced_group.toggled.connect(self.toggle_advanced_analytics)
        
        # Initially hide the content
        self.advanced_nav_toolbar.setVisible(False)
        self.advanced_canvas.setVisible(False)
        self.stats_summary_label.setVisible(False)
        
        layout.addWidget(self.advanced_group)
        
        # 6. Threshold Settings (Collapsible, Editable)
        self.threshold_group = QGroupBox("Threshold Settings (Click to expand)")
        self.threshold_group.setCheckable(True)
        self.threshold_group.setChecked(False)
        self.threshold_group.setStyleSheet("""
            QGroupBox {
                background-color: rgba(69, 162, 158, 0.05);
                border: 1px solid #45a29e;
                border-radius: 2px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                color: #45a29e;
                font-family: monospace;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        threshold_layout = QVBoxLayout()
        
        # Container for all threshold content (hidden initially)
        self.threshold_content = QWidget()
        threshold_content_layout = QVBoxLayout(self.threshold_content)
        
        # Status label (CUSTOM badge)
        self.threshold_status_label = QLabel("")
        self.threshold_status_label.setStyleSheet("color: #45a29e; font-size: 12px; margin-bottom: 8px;")
        threshold_content_layout.addWidget(self.threshold_status_label)
        
        # Warning Percentile Slider
        warning_layout = QHBoxLayout()
        warning_label = QLabel("<b style='color: #e0a800;'>Warning Level:</b>")
        warning_label.setStyleSheet("color: #e0a800; min-width: 120px;")
        self.warning_slider = QSlider(Qt.Horizontal)
        self.warning_slider.setMinimum(50)
        self.warning_slider.setMaximum(95)
        self.warning_slider.setValue(75)
        self.warning_slider.setTickInterval(5)
        self.warning_slider.setStyleSheet("""
            QSlider::groove:horizontal { background: #1f2833; height: 8px; border-radius: 4px; }
            QSlider::handle:horizontal { background: #e0a800; width: 16px; margin: -4px 0; border-radius: 8px; }
            QSlider::sub-page:horizontal { background: #e0a800; border-radius: 4px; }
        """)
        self.warning_value_label = QLabel("75th %ile")
        self.warning_value_label.setStyleSheet("color: #e0a800; min-width: 80px; font-weight: bold;")
        self.warning_slider.valueChanged.connect(lambda v: self.warning_value_label.setText(f"{v}th %ile"))
        warning_layout.addWidget(warning_label)
        warning_layout.addWidget(self.warning_slider)
        warning_layout.addWidget(self.warning_value_label)
        threshold_content_layout.addLayout(warning_layout)
        
        warning_desc = QLabel("<span style='color: #8b949e;'>Equipment above this percentile → ⚠️ Warning</span>")
        warning_desc.setStyleSheet("margin-left: 130px; font-size: 10px;")
        threshold_content_layout.addWidget(warning_desc)
        
        # IQR Multiplier Slider
        iqr_layout = QHBoxLayout()
        iqr_label = QLabel("<b style='color: #fc2044;'>Critical Level:</b>")
        iqr_label.setStyleSheet("color: #fc2044; min-width: 120px;")
        self.iqr_slider = QSlider(Qt.Horizontal)
        self.iqr_slider.setMinimum(5)  # 0.5
        self.iqr_slider.setMaximum(30)  # 3.0
        self.iqr_slider.setValue(15)  # 1.5
        self.iqr_slider.setTickInterval(5)
        self.iqr_slider.setStyleSheet("""
            QSlider::groove:horizontal { background: #1f2833; height: 8px; border-radius: 4px; }
            QSlider::handle:horizontal { background: #fc2044; width: 16px; margin: -4px 0; border-radius: 8px; }
            QSlider::sub-page:horizontal { background: #fc2044; border-radius: 4px; }
        """)
        self.iqr_value_label = QLabel("1.5× IQR")
        self.iqr_value_label.setStyleSheet("color: #fc2044; min-width: 80px; font-weight: bold;")
        self.iqr_slider.valueChanged.connect(lambda v: self.iqr_value_label.setText(f"{v/10:.1f}× IQR"))
        iqr_layout.addWidget(iqr_label)
        iqr_layout.addWidget(self.iqr_slider)
        iqr_layout.addWidget(self.iqr_value_label)
        threshold_content_layout.addLayout(iqr_layout)
        
        iqr_desc = QLabel("<span style='color: #8b949e;'>Values beyond Q3 + multiplier × IQR → 🔴 Critical</span>")
        iqr_desc.setStyleSheet("margin-left: 130px; font-size: 10px;")
        threshold_content_layout.addWidget(iqr_desc)
        
        # Buttons row
        btn_layout = QHBoxLayout()
        self.save_threshold_btn = QPushButton("💾 Save Settings")
        self.save_threshold_btn.setStyleSheet("""
            QPushButton { background-color: #45a29e; color: #0b0c10; padding: 8px 16px; border-radius: 2px; font-weight: bold; }
            QPushButton:hover { background-color: #66fcf1; }
            QPushButton:disabled { background-color: #1f2833; color: #8b949e; }
        """)
        self.save_threshold_btn.clicked.connect(self.save_threshold_settings)
        
        self.reset_threshold_btn = QPushButton("↻ Reset to Defaults")
        self.reset_threshold_btn.setStyleSheet("""
            QPushButton { background-color: transparent; color: #8b949e; padding: 8px 16px; border: 1px solid #1f2833; border-radius: 2px; }
            QPushButton:hover { background-color: #1f2833; color: #c5c6c7; }
            QPushButton:disabled { color: #45a29e; }
        """)
        self.reset_threshold_btn.clicked.connect(self.reset_threshold_settings)
        
        self.threshold_msg_label = QLabel("")
        self.threshold_msg_label.setStyleSheet("margin-left: 10px;")
        
        btn_layout.addWidget(self.save_threshold_btn)
        btn_layout.addWidget(self.reset_threshold_btn)
        btn_layout.addWidget(self.threshold_msg_label)
        btn_layout.addStretch()
        threshold_content_layout.addLayout(btn_layout)
        
        # Info note
        info_label = QLabel("💡 <span style='color: #8b949e;'>Changes apply to all your uploads. Existing data recalculates on view.</span>")
        info_label.setStyleSheet("margin-top: 8px; font-size: 10px;")
        threshold_content_layout.addWidget(info_label)
        
        threshold_layout.addWidget(self.threshold_content)
        self.threshold_content.setVisible(False)
        
        self.threshold_group.setLayout(threshold_layout)
        
        # Connect toggle signal
        self.threshold_group.toggled.connect(self.toggle_thresholds)
        
        layout.addWidget(self.threshold_group)

        scroll.setWidget(container)
        
        # Add scroll area to dashboard tab
        tab_layout = QVBoxLayout(self.dashboard_tab)
        tab_layout.addWidget(scroll)
        tab_layout.setContentsMargins(0, 0, 0, 0)

    def setup_data_ui(self):
        """Sets up the raw data table with health status."""
        layout = QVBoxLayout(self.data_tab)
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #0b0c10;
                color: #c5c6c7;
                gridline-color: #1f2833;
                border: 1px solid #1f2833;
                font-family: monospace;
            }
            QHeaderView::section {
                background-color: #1f2833;
                color: #66fcf1;
                padding: 4px;
                border: 1px solid #0b0c10;
                font-weight: bold;
            }
            QTableCornerButton::section {
                background-color: #1f2833;
            }
        """)
        layout.addWidget(self.table)

    def get_headers(self):
        return {'Authorization': self.auth_header}

    def fetch_threshold_settings(self):
        """Fetches threshold configuration from backend."""
        try:
            res = requests.get(f"{API_URL}thresholds/", headers=self.get_headers())
            if res.status_code == 200:
                self.threshold_settings = res.json()
                self.update_threshold_display()
        except Exception as e:
            print(f"Error fetching threshold settings: {e}")
            self.threshold_settings = None

    def update_threshold_display(self):
        """Updates the threshold sliders and status from fetched settings."""
        if self.threshold_settings:
            warning = self.threshold_settings['warning_percentile']
            iqr = self.threshold_settings['outlier_iqr_multiplier']
            is_custom = self.threshold_settings.get('is_custom', False)
            
            # Update sliders (blocking signals to prevent triggering change events)
            self.warning_slider.blockSignals(True)
            self.warning_slider.setValue(int(warning * 100))
            self.warning_slider.blockSignals(False)
            self.warning_value_label.setText(f"{int(warning * 100)}th %ile")
            
            self.iqr_slider.blockSignals(True)
            self.iqr_slider.setValue(int(iqr * 10))
            self.iqr_slider.blockSignals(False)
            self.iqr_value_label.setText(f"{iqr:.1f}× IQR")
            
            # Update status label
            if is_custom:
                self.threshold_status_label.setText("<b style='color: #66fcf1;'>[CUSTOM SETTINGS ACTIVE]</b>")
                self.reset_threshold_btn.setEnabled(True)
            else:
                self.threshold_status_label.setText("<span style='color: #8b949e;'>Using default settings</span>")
                self.reset_threshold_btn.setEnabled(False)

    def save_threshold_settings(self):
        """Saves custom threshold settings to backend."""
        warning = self.warning_slider.value() / 100.0
        iqr = self.iqr_slider.value() / 10.0
        
        self.save_threshold_btn.setEnabled(False)
        self.threshold_msg_label.setText("<span style='color: #8b949e;'>Saving...</span>")
        QApplication.processEvents()
        
        try:
            res = requests.put(
                f"{API_URL}thresholds/",
                json={'warning_percentile': warning, 'outlier_iqr_multiplier': iqr},
                headers={**self.get_headers(), 'Content-Type': 'application/json'}
            )
            if res.status_code == 200:
                self.threshold_settings = res.json()
                self.update_threshold_display()
                self.threshold_msg_label.setText("<span style='color: #20fc8f;'>✓ Saved!</span>")
                # Refresh current data if any
                if self.current_data:
                    self.load_history_item(self.history_list.currentItem())
            else:
                self.threshold_msg_label.setText(f"<span style='color: #fc2044;'>✗ Error: {res.status_code}</span>")
        except Exception as e:
            self.threshold_msg_label.setText(f"<span style='color: #fc2044;'>✗ {str(e)[:30]}</span>")
        finally:
            self.save_threshold_btn.setEnabled(True)

    def reset_threshold_settings(self):
        """Resets threshold settings to defaults."""
        self.reset_threshold_btn.setEnabled(False)
        self.threshold_msg_label.setText("<span style='color: #8b949e;'>Resetting...</span>")
        QApplication.processEvents()
        
        try:
            res = requests.delete(f"{API_URL}thresholds/", headers=self.get_headers())
            if res.status_code == 200:
                self.threshold_settings = res.json()
                self.update_threshold_display()
                self.threshold_msg_label.setText("<span style='color: #20fc8f;'>✓ Reset to defaults!</span>")
                if self.current_data:
                    self.load_history_item(self.history_list.currentItem())
            else:
                self.threshold_msg_label.setText(f"<span style='color: #fc2044;'>✗ Error: {res.status_code}</span>")
        except Exception as e:
            self.threshold_msg_label.setText(f"<span style='color: #fc2044;'>✗ {str(e)[:30]}</span>")
        finally:
            self.reset_threshold_btn.setEnabled(True)


    def refresh_history(self):
        """Fetches the last 5 uploads from the backend."""
        self.refresh_history_silent(show_error=True)

    def refresh_history_silent(self, show_error=False):
        """Refreshes history without blocking UI, unless error."""
        try:
            res = requests.get(f"{API_URL}history/", headers=self.get_headers())
            if res.status_code == 200:
                # Logic to update list only if changed or just clear/repopulate
                # For simplicity, we just clear/repopulate 
                self.history_list.clear()
                data_list = res.json()
                self.history_map = {}
                
                for item in data_list:
                    try:
                        dt = datetime.fromisoformat(item['uploaded_at'].replace('Z', '+00:00'))
                        local_dt = dt.astimezone()
                        time_str = local_dt.strftime("%Y-%m-%d %H:%M")
                    except ValueError:
                        time_str = item['uploaded_at'][:16] 
                        
                    display_id = item.get('user_upload_index') or item['id']
                    label = f"Upload {display_id} ({time_str})"
                    self.history_map[label] = item
                    self.history_list.addItem(label)
            elif show_error:
                QMessageBox.critical(self, "Error", f"Failed to fetch history: {res.status_code}")
                    
        except Exception as e:
            if show_error:
                print(f"Error fetching history: {e}")

    def upload_file(self):
        """Handles the file dialog and upload request."""
        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
        
        fname, _ = QFileDialog.getOpenFileName(self, 'Open CSV', os.getenv('HOME'), "CSV Files (*.csv)")
        if fname:
            # File size validation
            file_size = os.path.getsize(fname)
            if file_size > MAX_FILE_SIZE:
                size_mb = file_size / (1024 * 1024)
                QMessageBox.warning(
                    self, 
                    "File Too Large", 
                    f"Selected file is {size_mb:.2f} MB.\nMaximum allowed size is 5 MB."
                )
                return
            
            self.status_label.setText(f"Uploading ({file_size / 1024:.1f} KB)...")
            self.upload_btn.setEnabled(False)
            QApplication.processEvents()  # Force UI update
            
            try:
                with open(fname, 'rb') as f:
                    files = {'file': f}
                    res = requests.post(f"{API_URL}upload/", files=files, headers=self.get_headers())
                
                if res.status_code == 201:
                    data = res.json()
                    self.update_ui(data)
                    self.status_label.setText("✓ Upload Successful")
                    self.refresh_history()
                else:
                    self.status_label.setText("✗ Error")
                    # Try to get user-friendly error message
                    try:
                        error_data = res.json()
                        error_msg = error_data.get('error', res.text)
                    except:
                        error_msg = res.text
                    QMessageBox.warning(self, "Upload Failed", f"Server responded:\n{error_msg}")
            except requests.exceptions.ConnectionError:
                self.status_label.setText("✗ Connection Error")
                QMessageBox.critical(self, "Connection Error", "Could not connect to the server.\nPlease check if the backend is running.")
            except Exception as e:
                self.status_label.setText("✗ Error")
                QMessageBox.critical(self, "Upload Error", str(e))
            finally:
                self.upload_btn.setEnabled(True)

    def load_history_item(self, item):
        """Loads data when a history item is clicked."""
        key = item.text()
        data = self.history_map.get(key)
        if data:
            self.update_ui(data)
    
    def download_pdf_report(self):
        """Downloads the PDF report for the current upload."""
        if not self.current_data:
            QMessageBox.warning(self, "No Data", "Please upload or select a dataset first.")
            return
        
        upload_id = self.current_data.get('id')
        if not upload_id:
            QMessageBox.warning(self, "Error", "No upload ID found.")
            return
        
        # Ask user where to save the file
        default_name = f"equipment_report_{upload_id}.pdf"
        fname, _ = QFileDialog.getSaveFileName(self, 'Save PDF Report', 
                                              os.path.join(os.getenv('HOME'), default_name), 
                                              "PDF Files (*.pdf)")
        if fname:
            try:
                self.status_label.setText("Downloading PDF...")
                QApplication.processEvents()
                
                res = requests.get(f"{API_URL}report/{upload_id}/", 
                                 headers=self.get_headers(), 
                                 stream=True)
                
                if res.status_code == 200:
                    with open(fname, 'wb') as f:
                        for chunk in res.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    self.status_label.setText("PDF Downloaded")
                    QMessageBox.information(self, "Success", 
                                          f"Report saved to:\n{fname}")
                else:
                    self.status_label.setText("Download Failed")
                    QMessageBox.warning(self, "Download Failed", 
                                      f"Server responded: {res.status_code}")
            except Exception as e:
                self.status_label.setText("Download Error")
                QMessageBox.critical(self, "Error", f"Failed to download report:\n{str(e)}")
    
    def toggle_advanced_analytics(self, checked):
        """Show/hide advanced analytics content when toggled."""
        self.advanced_nav_toolbar.setVisible(checked)
        self.advanced_canvas.setVisible(checked)
        self.stats_summary_label.setVisible(checked)

    def toggle_thresholds(self, checked):
        """Show/hide threshold content when toggled."""
        self.threshold_content.setVisible(checked)

    def update_ui(self, data):
        """Updates the dashboard and table with new data and advanced analytics."""
        self.current_data = data
        summary = data['summary']
        processed = data['processed_data']

        # 1. Update Stats Cards with Min/Max
        self.stat_labels['total'].setText(f"Total\n{summary['total_count']}")
        self.stat_labels['flow'].setText(
            f"Avg Flowrate\n{summary['avg_flowrate']:.1f}\n"
            f"(Min: {summary.get('min_flowrate', 0):.1f} | Max: {summary.get('max_flowrate', 0):.1f})"
        )
        self.stat_labels['pressure'].setText(
            f"Avg Pressure\n{summary['avg_pressure']:.1f}\n"
            f"(Min: {summary.get('min_pressure', 0):.1f} | Max: {summary.get('max_pressure', 0):.1f})"
        )
        self.stat_labels['temp'].setText(
            f"Avg Temp\n{summary['avg_temperature']:.1f}\n"
            f"(Min: {summary.get('min_temperature', 0):.1f} | Max: {summary.get('max_temperature', 0):.1f})"
        )

        # 2. Update Outlier Alert
        outliers = summary.get('outliers', [])
        if outliers:
            self.outlier_group.setVisible(True)
            outlier_text = f"<b style='color: #fc2044;'>[ALERT] {len(outliers)} DEVICES REPORTING CRITICAL STATUS:</b><br><br>"
            for outlier in outliers[:5]:  # Show first 5
                outlier_text += f"<b>{outlier['equipment']}</b>: "
                params = [f"{p['parameter']} = {p['value']:.2f}" for p in outlier['parameters']]
                outlier_text += ", ".join(params) + "<br>"
            if len(outliers) > 5:
                outlier_text += f">>> and {len(outliers) - 5} more..."
            self.outlier_label.setText(outlier_text)
        else:
            self.outlier_group.setVisible(False)

        # 3. Update Table with Health Status Colors
        if processed:
            # Add health_status column if not present
            headers = list(processed[0].keys())
            if 'health_status' in headers:
                headers.remove('health_status')
            if 'health_color' in headers:
                headers.remove('health_color')
            headers.insert(0, 'Status')
            
            self.table.setColumnCount(len(headers))
            self.table.setRowCount(len(processed))
            self.table.setHorizontalHeaderLabels(headers)
            
            for i, row in enumerate(processed):
                # Status icon
                health_status = row.get('health_status', 'normal')
                status_text = '✓' if health_status == 'normal' else '⚠' if health_status == 'warning' else '✗'
                status_item = QTableWidgetItem(status_text)
                
                if health_status == 'critical':
                    status_item.setBackground(QColor(239, 68, 68, 40))
                    status_item.setForeground(QColor(239, 68, 68))
                elif health_status == 'warning':
                    status_item.setBackground(QColor(245, 158, 11, 40))
                    status_item.setForeground(QColor(245, 158, 11))
                else:
                    status_item.setForeground(QColor(16, 185, 129))
                
                self.table.setItem(i, 0, status_item)
                
                # Other columns
                col_idx = 1
                for key in headers[1:]:
                    val = row.get(key, '')
                    if key not in ['health_status', 'health_color']:
                        item = QTableWidgetItem(str(val))
                        if health_status == 'critical':
                            item.setBackground(QColor(239, 68, 68, 20))
                        elif health_status == 'warning':
                            item.setBackground(QColor(245, 158, 11, 20))
                        self.table.setItem(i, col_idx, item)
                        col_idx += 1

        # 4. Update Main Charts
        self.figure.clear()
        text_color = '#c5c6c7'
        accent_blue = '#66fcf1'
        accent_teal = '#45a29e'
        accent_red = '#fc2044'
        
        # Chart 1: Type Distribution (Pie)
        ax1 = self.figure.add_subplot(121)
        type_dist = summary['type_distribution']
        
        wedges, texts, autotexts = ax1.pie(
            type_dist.values(), 
            labels=type_dist.keys(), 
            autopct='%1.1f%%',
            startangle=90,
            textprops={'color': text_color, 'size': 9}
        )
        ax1.set_title("Equipment Types", color=text_color, fontsize=11)
        
        # Chart 2: Average Parameters (Bar)
        ax2 = self.figure.add_subplot(122)
        params = ['Flowrate', 'Pressure', 'Temp']
        vals = [summary['avg_flowrate'], summary['avg_pressure'], summary['avg_temperature']]
        bars = ax2.bar(params, vals, color=[accent_blue, accent_teal, accent_red])
        
        ax2.set_title("Average Parameters", color=text_color, fontsize=11)
        ax2.tick_params(colors=text_color, labelsize=9)
        ax2.spines['bottom'].set_color('#1f2833')
        ax2.spines['left'].set_color('#1f2833') 
        ax2.spines['top'].set_color('none')
        ax2.spines['right'].set_color('none')
        ax2.set_facecolor('#0b0c10')

        self.figure.tight_layout()
        self.canvas.draw()

        # 5. Update Advanced Analytics
        self.update_advanced_analytics(summary)
        
        # 6. Enable PDF download button
        self.pdf_btn.setEnabled(True)

    def update_advanced_analytics(self, summary):
        """Updates the advanced analytics section."""
        self.advanced_figure.clear()
        text_color = '#c5c6c7'
        accent_blue = '#66fcf1'
        accent_purple = '#c586c0' # Keeping distinct but techy
        accent_red = '#fc2044'
        
        # Type Comparison Chart
        if 'type_comparison' in summary:
            ax1 = self.advanced_figure.add_subplot(221)
            type_comp = summary['type_comparison']
            types = list(type_comp.keys())
            
            x = np.arange(len(types))
            width = 0.25
            
            flowrates = [type_comp[t]['avg_flowrate'] for t in types]
            pressures = [type_comp[t]['avg_pressure'] for t in types]
            temps = [type_comp[t]['avg_temperature'] for t in types]
            
            ax1.bar(x - width, flowrates, width, label='Flowrate', color=accent_blue)
            ax1.bar(x, pressures, width, label='Pressure', color=accent_purple)
            ax1.bar(x + width, temps, width, label='Temperature', color=accent_red)
            
            ax1.set_title('Type Comparison', color=text_color, fontsize=10)
            ax1.set_xticks(x)
            ax1.set_xticklabels(types, rotation=45, ha='right', fontsize=8)
            ax1.tick_params(colors=text_color, labelsize=8)
            ax1.legend(fontsize=8, facecolor='#1f2833', edgecolor='#45a29e', labelcolor=text_color)
            ax1.set_facecolor('#0b0c10')
            for spine in ax1.spines.values():
                spine.set_color('#1f2833')
        
        # Correlation Heatmap
        if 'correlation_matrix' in summary:
            ax2 = self.advanced_figure.add_subplot(222)
            corr_matrix = summary['correlation_matrix']
            params = ['Flowrate', 'Pressure', 'Temperature']
            
            corr_data = np.array([[corr_matrix[row][col] for col in params] for row in params])
            
            im = ax2.imshow(corr_data, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
            ax2.set_xticks(np.arange(len(params)))
            ax2.set_yticks(np.arange(len(params)))
            ax2.set_xticklabels(params, fontsize=8)
            ax2.set_yticklabels(params, fontsize=8)
            ax2.tick_params(colors=text_color, labelsize=8)
            
            # Add correlation values
            for i in range(len(params)):
                for j in range(len(params)):
                    text = ax2.text(j, i, f'{corr_data[i, j]:.2f}',
                                   ha="center", va="center", color='white' if abs(corr_data[i, j]) > 0.5 else '#0b0c10',
                                   fontsize=9)
            
            ax2.set_title('Correlation Matrix', color=text_color, fontsize=10)
            ax2.set_facecolor('#0b0c10')
            
            # Colorbar
            cbar = self.advanced_figure.colorbar(im, ax=ax2)
            cbar.ax.tick_params(colors=text_color, labelsize=7)
        
        # Standard Deviation bars
        ax3 = self.advanced_figure.add_subplot(223)
        std_params = ['Flowrate', 'Pressure', 'Temp']
        std_vals = [
            summary.get('std_flowrate', 0),
            summary.get('std_pressure', 0),
            summary.get('std_temperature', 0)
        ]
        ax3.bar(std_params, std_vals, color=[accent_blue, accent_purple, accent_red])
        ax3.set_title('Standard Deviation', color=text_color, fontsize=10)
        ax3.tick_params(colors=text_color, labelsize=8)
        ax3.set_facecolor('#0b0c10')
        for spine in ax3.spines.values():
            spine.set_color('#1f2833')
        
        # Health Status Distribution
        ax4 = self.advanced_figure.add_subplot(224)
        processed = self.current_data.get('processed_data', [])
        if processed:
            health_counts = {'normal': 0, 'warning': 0, 'critical': 0}
            for row in processed:
                status = row.get('health_status', 'normal')
                health_counts[status] += 1
            
            
            colors_map = {'normal': '#20fc8f', 'warning': '#e0a800', 'critical': '#fc2044'}
            labels = [f"{k.upper()}\n({v})" for k, v in health_counts.items() if v > 0]
            values = [v for v in health_counts.values() if v > 0]
            colors = [colors_map[k] for k, v in health_counts.items() if v > 0]
            
            ax4.pie(values, labels=labels, colors=colors, autopct='%1.1f%%',
                   textprops={'color': text_color, 'size': 8})
            ax4.set_title('Health Status Distribution', color=text_color, fontsize=10)
        
        self.advanced_figure.tight_layout()
        self.advanced_canvas.draw()
        
        # Update stats summary text
        stats_text = (
            f"<b>Statistical Summary:</b><br>"
            f"Flowrate StdDev: {summary.get('std_flowrate', 0):.2f} | "
            f"Pressure StdDev: {summary.get('std_pressure', 0):.2f} | "
            f"Temperature StdDev: {summary.get('std_temperature', 0):.2f}<br>"
            f"<b>Equipment Types:</b> {len(summary.get('type_comparison', {}))} types | "
            f"<b>Outliers:</b> {len(summary.get('outliers', []))} detected"
        )
        self.stats_summary_label.setText(stats_text)

    def handle_logout(self):
        """Handle logout by calling the callback and closing the window."""
        reply = QMessageBox.question(
            self, 
            'Confirm Logout',
            'Are you sure you want to logout?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.timer.stop()  # Stop auto-refresh
            if self.logout_callback:
                self.logout_callback()
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    def run_app():
        """Main application loop that handles login/logout cycle."""
        while True:
            # Login Flow
            login = LoginDialog()
            if login.exec_() != QDialog.Accepted:
                # User cancelled login
                return 0
            
            user, pwd = login.get_credentials()
            try:
                # Request JWT
                res = requests.post(f"{API_URL}login/", data={'username': user, 'password': pwd})
                if res.status_code == 200:
                    token = res.json()['access']
                    auth_header = f"Bearer {token}"
                    
                    # Track if user logged out (vs closed window)
                    logged_out = [False]  # Use list to allow modification in nested function
                    
                    def on_logout():
                        logged_out[0] = True
                    
                    window = MainWindow(auth_header, username=user, logout_callback=on_logout)
                    window.show()
                    app.exec_()
                    
                    # If user logged out, show login again
                    if logged_out[0]:
                        continue
                    else:
                        # Window was closed normally
                        return 0
                else:
                    QMessageBox.critical(None, "Login Failed", "Invalid credentials")
                    continue  # Show login again
            except Exception as e:
                QMessageBox.critical(None, "Connection Error", f"Could not connect to server: {e}")
                continue  # Show login again
    
    sys.exit(run_app())
