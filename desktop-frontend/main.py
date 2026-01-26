import sys
import os
import requests
import pandas as pd
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QTabWidget, QTableWidget, QTableWidgetItem, QMessageBox, QListWidget, QSplitter, 
                             QDialog, QLineEdit, QFormLayout, QProgressDialog, QScrollArea, QGroupBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

# Using a standard local URL. In production, this might be an env var.
API_URL = "http://127.0.0.1:8000/api/"

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login / Register")
        self.setFixedSize(350, 250)
        
        layout = QVBoxLayout()
        
        # Mode label
        self.mode_label = QLabel("<b>Login to Continue</b>")
        self.mode_label.setAlignment(Qt.AlignCenter)
        self.mode_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(self.mode_label)
        
        # Form layout
        form_layout = QFormLayout()
        self.username = QLineEdit()
        self.email = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        
        form_layout.addRow("Username:", self.username)
        self.email_row = form_layout.addRow("Email:", self.email)
        form_layout.addRow("Password:", self.password)
        self.confirm_row = form_layout.addRow("Confirm:", self.confirm_password)
        
        layout.addLayout(form_layout)
        
        # Hide email and confirm password initially (login mode)
        self.email.setVisible(False)
        self.confirm_password.setVisible(False)
        form_layout.labelForField(self.email).setVisible(False)
        form_layout.labelForField(self.confirm_password).setVisible(False)
        
        # Action button
        self.action_btn = QPushButton("Login")
        self.action_btn.setStyleSheet("""
            QPushButton {
                background-color: #238636; 
                color: white; 
                padding: 8px; 
                font-weight: bold; 
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #2ea043;
            }
        """)
        self.action_btn.clicked.connect(self.handle_action)
        layout.addWidget(self.action_btn)
        
        # Toggle button
        self.toggle_btn = QPushButton("Don't have an account? Register")
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #58a6ff;
                text-decoration: underline;
                padding: 5px;
            }
            QPushButton:hover {
                color: #79c0ff;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_mode)
        layout.addWidget(self.toggle_btn)
        
        self.setLayout(layout)
        self.is_register_mode = False

    def toggle_mode(self):
        self.is_register_mode = not self.is_register_mode
        form_layout = self.layout().itemAt(1).layout()
        
        if self.is_register_mode:
            # Switch to register mode
            self.mode_label.setText("<b>Create New Account</b>")
            self.action_btn.setText("Register")
            self.toggle_btn.setText("Already have an account? Login")
            self.email.setVisible(True)
            self.confirm_password.setVisible(True)
            form_layout.labelForField(self.email).setVisible(True)
            form_layout.labelForField(self.confirm_password).setVisible(True)
        else:
            # Switch to login mode
            self.mode_label.setText("<b>Login to Continue</b>")
            self.action_btn.setText("Login")
            self.toggle_btn.setText("Don't have an account? Register")
            self.email.setVisible(False)
            self.confirm_password.setVisible(False)
            form_layout.labelForField(self.email).setVisible(False)
            form_layout.labelForField(self.confirm_password).setVisible(False)
    
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
        
        # Validation
        if not username or not email or not password or not confirm:
            QMessageBox.warning(self, "Error", "All fields are required")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return
        
        if len(password) < 8:
            QMessageBox.warning(self, "Error", "Password must be at least 8 characters")
            return
        
        try:
            res = requests.post(f"{API_URL}register/", json={
                'username': username,
                'email': email,
                'password': password
            })
            
            if res.status_code == 201:
                QMessageBox.information(self, "Success", "Registration successful! Please login.")
                # Switch to login mode
                self.toggle_mode()
            else:
                error_msg = res.json().get('error', 'Registration failed')
                QMessageBox.warning(self, "Registration Failed", error_msg)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not connect to server: {e}")

    def get_credentials(self):
        return self.username.text(), self.password.text()

class MainWindow(QMainWindow):
    def __init__(self, auth_header):
        super().__init__()
        self.auth_header = auth_header
        
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
        sidebar_widget.setStyleSheet("background-color: #0d1117; border-right: 1px solid #30363d;")

        # --- Main Content Area ---
        main_content_layout = QVBoxLayout()
        
        # Top Bar: The primary action is uploading a CSV.
        top_bar = QHBoxLayout()
        self.upload_btn = QPushButton("Upload CSV")
        # Using a nice blue accent for the primary action
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #238636; 
                color: white; 
                padding: 8px 16px; 
                font-weight: bold; 
                border-radius: 6px;
                border: 1px solid rgba(27,31,35,0.15);
            }
            QPushButton:hover {
                background-color: #2ea043;
            }
        """)
        self.upload_btn.clicked.connect(self.upload_file)
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #8b949e; margin-left: 10px;")
        
        # Download PDF Report button
        self.pdf_btn = QPushButton("📄 Download PDF Report")
        self.pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #58a6ff; 
                color: white; 
                padding: 8px 16px; 
                font-weight: bold; 
                border-radius: 6px;
                border: 1px solid rgba(27,31,35,0.15);
            }
            QPushButton:hover {
                background-color: #79c0ff;
            }
            QPushButton:disabled {
                background-color: #30363d;
                color: #8b949e;
            }
        """)
        self.pdf_btn.clicked.connect(self.download_pdf_report)
        self.pdf_btn.setEnabled(False)  # Disabled until data is loaded
        
        top_bar.addWidget(self.upload_btn)
        top_bar.addWidget(self.pdf_btn)
        top_bar.addWidget(self.status_label)
        top_bar.addStretch()
        
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
        main_content_widget.setStyleSheet("background-color: #0d1117;")

        # Combine them with a Splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(sidebar_widget)
        splitter.addWidget(main_content_widget)
        splitter.setHandleWidth(1)
        layout.addWidget(splitter)
        
        # Remove margins to make it look cleaner
        layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setStyleSheet("background-color: #0d1117; color: #c9d1d9;")

        # Load initial data
        self.refresh_history()

    def setup_dashboard_ui(self):
        """Sets up the charts and summary cards with advanced analytics."""
        # Create scroll area for dashboard
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #0d1117; }")
        
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
                background-color: #161b22; 
                border: 1px solid #30363d; 
                border-radius: 8px; 
                color: #e6edf3; 
                padding: 15px; 
                font-size: 12px;
                font-weight: bold;
            """)
            stats_layout.addWidget(lbl)
        
        layout.addLayout(stats_layout)

        # 2. Outlier Alert (if any)
        self.outlier_group = QGroupBox("⚠️ Outlier Detection")
        self.outlier_group.setStyleSheet("""
            QGroupBox {
                background-color: rgba(239, 68, 68, 0.1);
                border: 1px solid #ef4444;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                color: #ef4444;
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
        self.figure.patch.set_facecolor('#0d1117')
        
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: #0d1117;")
        layout.addWidget(self.canvas)

        # 5. Advanced Analytics Section (Collapsible)
        self.advanced_group = QGroupBox("🔬 Advanced Analytics (Click to expand)")
        self.advanced_group.setCheckable(True)
        self.advanced_group.setChecked(False)
        self.advanced_group.setStyleSheet("""
            QGroupBox {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                color: #58a6ff;
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
        self.advanced_figure.patch.set_facecolor('#0d1117')
        self.advanced_canvas = FigureCanvas(self.advanced_figure)
        self.advanced_canvas.setStyleSheet("background-color: #0d1117;")
        advanced_layout.addWidget(self.advanced_canvas)
        
        # Stats summary
        self.stats_summary_label = QLabel("")
        self.stats_summary_label.setStyleSheet("color: #8b949e; padding: 10px; background-color: #0d1117; font-size: 11px;")
        self.stats_summary_label.setWordWrap(True)
        advanced_layout.addWidget(self.stats_summary_label)
        
        self.advanced_group.setLayout(advanced_layout)
        
        # Connect toggle signal to show/hide content
        self.advanced_group.toggled.connect(self.toggle_advanced_analytics)
        
        # Initially hide the content
        self.advanced_canvas.setVisible(False)
        self.stats_summary_label.setVisible(False)
        
        layout.addWidget(self.advanced_group)
        
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
                background-color: #161b22;
                color: #c9d1d9;
                gridline-color: #30363d;
                border: none;
            }
            QHeaderView::section {
                background-color: #21262d;
                color: #c9d1d9;
                padding: 4px;
                border: 1px solid #30363d;
            }
            QTableCornerButton::section {
                background-color: #21262d;
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
                # Update display if UI is ready
                if hasattr(self, 'threshold_label'):
                    self.update_threshold_display()
        except Exception as e:
            print(f"Error fetching threshold settings: {e}")
            self.threshold_settings = None

    def update_threshold_display(self):
        """Updates the threshold configuration display."""
        if self.threshold_settings:
            warning = self.threshold_settings['warning_percentile']
            iqr = self.threshold_settings['outlier_iqr_multiplier']
            
            threshold_text = (
                f"<b style='color: #58a6ff;'>Current Analysis Thresholds:</b><br><br>"
                f"<b>Warning Level:</b> {int(warning * 100)}th percentile<br>"
                f"<span style='color: #8b949e;'>Equipment with parameters above this level are marked as Warning</span><br><br>"
                f"<b>Critical/Outlier Level:</b> Q3 + {iqr} × IQR<br>"
                f"<span style='color: #8b949e;'>Values beyond this threshold are marked as outliers</span>"
            )
            self.threshold_label.setText(threshold_text)
        else:
            self.threshold_label.setText(
                "<span style='color: #ef4444;'>Unable to load threshold settings</span>"
            )

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
                        
                    label = f"Upload {item['id']} ({time_str})"
                    self.history_map[label] = item
                    self.history_list.addItem(label)
            elif show_error:
                QMessageBox.critical(self, "Error", f"Failed to fetch history: {res.status_code}")
                    
        except Exception as e:
            if show_error:
                print(f"Error fetching history: {e}")

    def upload_file(self):
        """Handles the file dialog and upload request."""
        fname, _ = QFileDialog.getOpenFileName(self, 'Open CSV', os.getenv('HOME'), "CSV Files (*.csv)")
        if fname:
            self.status_label.setText("Uploading...")
            self.upload_btn.setEnabled(False)
            QApplication.processEvents() # Force UI update
            
            try:
                files = {'file': open(fname, 'rb')}
                res = requests.post(f"{API_URL}upload/", files=files, headers=self.get_headers())
                if res.status_code == 201:
                    data = res.json()
                    self.update_ui(data)
                    self.status_label.setText("Upload Successful")
                    self.refresh_history()
                else:
                    self.status_label.setText("Error")
                    QMessageBox.warning(self, "Upload Failed", f"Server responded: {res.text}")
            except Exception as e:
                self.status_label.setText("Connection Error")
                QMessageBox.critical(self, "Connection Error", str(e))
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
        self.advanced_canvas.setVisible(checked)
        self.stats_summary_label.setVisible(checked)

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
            outlier_text = f"<b style='color: #ef4444;'>{len(outliers)} Equipment with Outliers:</b><br><br>"
            for outlier in outliers[:5]:  # Show first 5
                outlier_text += f"<b>{outlier['equipment']}</b>: "
                params = [f"{p['parameter']} = {p['value']:.2f}" for p in outlier['parameters']]
                outlier_text += ", ".join(params) + "<br>"
            if len(outliers) > 5:
                outlier_text += f"<i>...and {len(outliers) - 5} more</i>"
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
        text_color = '#c9d1d9'
        
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
        bars = ax2.bar(params, vals, color=['#58a6ff', '#2ea043', '#f85149'])
        
        ax2.set_title("Average Parameters", color=text_color, fontsize=11)
        ax2.tick_params(colors=text_color, labelsize=9)
        ax2.spines['bottom'].set_color('#30363d')
        ax2.spines['left'].set_color('#30363d') 
        ax2.spines['top'].set_color('none')
        ax2.spines['right'].set_color('none')
        ax2.set_facecolor('#0d1117')

        self.figure.tight_layout()
        self.canvas.draw()

        # 5. Update Advanced Analytics
        self.update_advanced_analytics(summary)
        
        # 6. Enable PDF download button
        self.pdf_btn.setEnabled(True)

    def update_advanced_analytics(self, summary):
        """Updates the advanced analytics section."""
        self.advanced_figure.clear()
        text_color = '#c9d1d9'
        
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
            
            ax1.bar(x - width, flowrates, width, label='Flowrate', color='#58a6ff')
            ax1.bar(x, pressures, width, label='Pressure', color='#ee82ee')
            ax1.bar(x + width, temps, width, label='Temperature', color='#f85149')
            
            ax1.set_title('Type Comparison', color=text_color, fontsize=10)
            ax1.set_xticks(x)
            ax1.set_xticklabels(types, rotation=45, ha='right', fontsize=8)
            ax1.tick_params(colors=text_color, labelsize=8)
            ax1.legend(fontsize=8, facecolor='#161b22', edgecolor='#30363d', labelcolor=text_color)
            ax1.set_facecolor('#0d1117')
            for spine in ax1.spines.values():
                spine.set_color('#30363d')
        
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
                                   ha="center", va="center", color='white' if abs(corr_data[i, j]) > 0.5 else 'black',
                                   fontsize=9)
            
            ax2.set_title('Correlation Matrix', color=text_color, fontsize=10)
            ax2.set_facecolor('#0d1117')
            
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
        ax3.bar(std_params, std_vals, color=['#58a6ff', '#2ea043', '#f85149'])
        ax3.set_title('Standard Deviation', color=text_color, fontsize=10)
        ax3.tick_params(colors=text_color, labelsize=8)
        ax3.set_facecolor('#0d1117')
        for spine in ax3.spines.values():
            spine.set_color('#30363d')
        
        # Health Status Distribution
        ax4 = self.advanced_figure.add_subplot(224)
        processed = self.current_data.get('processed_data', [])
        if processed:
            health_counts = {'normal': 0, 'warning': 0, 'critical': 0}
            for row in processed:
                status = row.get('health_status', 'normal')
                health_counts[status] += 1
            
            colors_map = {'normal': '#10b981', 'warning': '#f59e0b', 'critical': '#ef4444'}
            labels = [f"{k.capitalize()}\n({v})" for k, v in health_counts.items() if v > 0]
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Login Flow
    login = LoginDialog()
    if login.exec_() == QDialog.Accepted:
        user, pwd = login.get_credentials()
        try:
            # Request JWT
            res = requests.post(f"{API_URL}login/", data={'username': user, 'password': pwd})
            if res.status_code == 200:
                token = res.json()['access']
                auth_header = f"Bearer {token}"
                
                window = MainWindow(auth_header)
                window.show()
                sys.exit(app.exec_())
            else:
                QMessageBox.critical(None, "Login Failed", "Invalid credentials")
                sys.exit(0)
        except Exception as e:
            QMessageBox.critical(None, "Connection Error", f"Could not connect to server: {e}")
            sys.exit(0)
    else:
        sys.exit(0)
