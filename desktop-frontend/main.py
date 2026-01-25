import sys
import os
import requests
import pandas as pd
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QTabWidget, QTableWidget, QTableWidgetItem, QMessageBox, QListWidget, QSplitter, 
                             QDialog, QLineEdit, QFormLayout, QProgressDialog)
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

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
        
        # Simple refresh button in case the user uploaded from the web app
        refresh_btn = QPushButton("Refresh History")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #21262d; 
                color: #c9d1d9; 
                border: 1px solid #30363d;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #30363d;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_history)
        sidebar_layout.addWidget(refresh_btn)
        
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
        
        top_bar.addWidget(self.upload_btn)
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
        """Sets up the charts and summary cards."""
        layout = QVBoxLayout(self.dashboard_tab)
        
        # 1. Summary Stats Cards
        stats_layout = QHBoxLayout()
        self.stat_labels = {
            "total": QLabel("Total\n-"),
            "flow": QLabel("Avg Flowrate\n-"),
            "pressure": QLabel("Avg Pressure\n-"),
            "temp": QLabel("Avg Temp\n-")
        }
        
        for lbl in self.stat_labels.values():
            lbl.setAlignment(Qt.AlignCenter)
            # Dark card style with a subtle border and shadow effect
            lbl.setStyleSheet("""
                background-color: #161b22; 
                border: 1px solid #30363d; 
                border-radius: 8px; 
                color: #e6edf3; 
                padding: 15px; 
                font-size: 14px;
                font-weight: bold;
            """)
            stats_layout.addWidget(lbl)
        
        layout.addLayout(stats_layout)

        # 2. Charts Area
        # We use Matplotlib backend for Qt
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.figure.patch.set_facecolor('#0d1117') # Match app background
        
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: #0d1117;")
        layout.addWidget(self.canvas)

    def setup_data_ui(self):
        """Sets up the raw data table."""
        layout = QVBoxLayout(self.data_tab)
        self.table = QTableWidget()
        # Styling the table to match dark theme
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

    def update_ui(self, data):
        """Updates the dashboard and table with new data."""
        self.current_data = data
        summary = data['summary']
        processed = data['processed_data']

        # 1. Update Stats Cards
        self.stat_labels['total'].setText(f"Total\n{summary['total_count']}")
        self.stat_labels['flow'].setText(f"Avg Flowrate\n{summary['avg_flowrate']:.2f}")
        self.stat_labels['pressure'].setText(f"Avg Pressure\n{summary['avg_pressure']:.2f}")
        self.stat_labels['temp'].setText(f"Avg Temp\n{summary['avg_temperature']:.2f}")

        # 2. Update Table
        if processed:
            headers = processed[0].keys()
            self.table.setColumnCount(len(headers))
            self.table.setRowCount(len(processed))
            self.table.setHorizontalHeaderLabels(headers)
            for i, row in enumerate(processed):
                for j, (key, val) in enumerate(row.items()):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))

        # 3. Update Charts using Matplotlib
        self.figure.clear()
        
        # Common text color for charts
        text_color = '#c9d1d9'
        
        # Chart 1: Type Distribution (Pie)
        ax1 = self.figure.add_subplot(121)
        type_dist = summary['type_distribution']
        
        wedges, texts, autotexts = ax1.pie(
            type_dist.values(), 
            labels=type_dist.keys(), 
            autopct='%1.1f%%',
            startangle=90,
            textprops={'color': text_color}
        )
        ax1.set_title("Equipment Types", color=text_color)
        
        # Chart 2: Average Parameters (Bar)
        ax2 = self.figure.add_subplot(122)
        params = ['Flowrate', 'Pressure', 'Temp']
        vals = [summary['avg_flowrate'], summary['avg_pressure'], summary['avg_temperature']]
        bars = ax2.bar(params, vals, color=['#58a6ff', '#2ea043', '#f85149'])
        
        ax2.set_title("Average Parameters", color=text_color)
        ax2.tick_params(colors=text_color)
        ax2.spines['bottom'].set_color('#30363d')
        ax2.spines['left'].set_color('#30363d') 
        ax2.spines['top'].set_color('none')
        ax2.spines['right'].set_color('none')
        ax2.set_facecolor('#0d1117') # Chart area background

        self.canvas.draw()


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
