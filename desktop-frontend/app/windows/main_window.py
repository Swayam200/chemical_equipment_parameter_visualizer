"""
Main Window for the Desktop App.
Contains the primary application UI with dashboard, charts, and data table.
"""
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QTabWidget, QTableWidget, QTableWidgetItem, QMessageBox,
    QListWidget, QSplitter, QScrollArea, QGroupBox, QSlider, QApplication,
    QLineEdit, QComboBox, QCheckBox, QDialog, QTextBrowser
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QColor, QPixmap, QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np

from ..api_client import ApiClient
from .. import styles
from ..ai_service import generate_ai_response
from ..workers.ai_worker import AIWorker


class MainWindow(QMainWindow):
    """
    Main application window with sidebar, dashboard charts, and data table.
    """

    # Chart colors for dark theme
    CHART_COLORS = {
        'text': '#c5c6c7',
        'accent_blue': '#66fcf1',
        'accent_teal': '#45a29e',
        'accent_red': '#fc2044',
        'accent_purple': '#c586c0',
        'bg': '#0b0c10',
        'border': '#1f2833'
    }

    def __init__(self, api_client: ApiClient, username: str = "", logout_callback=None):
        super().__init__()
        self.api_client = api_client
        self.username = username
        self.logout_callback = logout_callback
        self.current_data = None
        self.history_map = {}
        self.threshold_settings = None
        
        # View Settings
        self.view_settings = {
            'show_trends': True,
            'show_correlation': True,
            'show_efficiency': True, # Replaces 'Comparisons' in web
            'show_table': True
        }
        self.table_filter = 'all' # all, normal, warning, critical

        self._setup_window()
        self._setup_ui()
        self._start_auto_refresh()
        self._load_initial_data()

    def _setup_window(self) -> None:
        """
        Configure basic window properties (title, dimensions).
        """
        self.setWindowTitle("Carbon Sleuth - Industrial Analytics (Desktop)")
        self.resize(1280, 850)

    def _setup_ui(self) -> None:
        """
        Build the main window UI structure.
        Uses a QSplitter to separate the Sidebar (History) and Main Content (Dashboard).
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet(styles.MAIN_WINDOW_STYLE)

        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # --- Sidebar ---
        sidebar_widget = self._create_sidebar()

        # --- Main Content ---
        main_content_widget = self._create_main_content()

        # Combine with splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(sidebar_widget)
        splitter.addWidget(main_content_widget)
        splitter.setHandleWidth(1)
        layout.addWidget(splitter)

    def _create_sidebar(self) -> QWidget:
        """Create the history sidebar with Logo."""
        sidebar_layout = QVBoxLayout()
        
        # LOGO
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'logo.png')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(200, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            sidebar_layout.addWidget(logo_label)
        else:
             title = QLabel("Carbon Sleuth")
             title.setStyleSheet("font-size: 18px; font-weight: bold; color: #66fcf1; margin-bottom: 10px;")
             title.setAlignment(Qt.AlignCenter)
             sidebar_layout.addWidget(title)

        header_label = QLabel("<b>Recent Uploads</b>")
        header_label.setStyleSheet("color: #e6edf3; font-size: 14px; margin-top: 15px; margin-bottom: 5px;")
        sidebar_layout.addWidget(header_label)

        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self._load_history_item)
        sidebar_layout.addWidget(self.history_list)

        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar_layout)
        sidebar_widget.setFixedWidth(260)
        sidebar_widget.setStyleSheet(styles.SIDEBAR_STYLE)

        return sidebar_widget

    def _create_main_content(self) -> QWidget:
        """Create the main content area with tabs."""
        main_layout = QVBoxLayout()

        # Top bar with actions
        top_bar = self._create_top_bar()
        main_layout.addLayout(top_bar)

        # Tabs
        self.tabs = QTabWidget()
        self.dashboard_tab = QWidget()
        self.data_tab = QWidget()

        self._setup_dashboard_tab()
        self._setup_data_tab()
        
        # --- Prediction Tab ---
        self.prediction_tab = QWidget()
        self._setup_prediction_tab()

        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.addTab(self.data_tab, "Raw Data")
        self.tabs.addTab(self.prediction_tab, "🔮 Predictions")
        main_layout.addWidget(self.tabs)

        widget = QWidget()
        widget.setLayout(main_layout)
        widget.setStyleSheet("background-color: #0b0c10;") # Dark theme
        return widget

    def _create_top_bar(self) -> QHBoxLayout:
        """Create the top action bar with Search and AI."""
        top_bar = QHBoxLayout()

        # Search / AI Input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ask AI (e.g., 'Show me critical pumps' or 'Compare pressure')")
        self.search_input.setStyleSheet("padding: 6px; border-radius: 4px; border: 1px solid #444c56; background: #0d1117; color: white; min-width: 300px;")
        self.search_input.returnPressed.connect(self._handle_ai_query)
        top_bar.addWidget(self.search_input)

        self.ask_ai_btn = QPushButton("✨ Ask AI")
        self.ask_ai_btn.setStyleSheet(styles.BUTTON_PRIMARY)
        self.ask_ai_btn.clicked.connect(self._handle_ai_query)
        top_bar.addWidget(self.ask_ai_btn)

        top_bar.addSpacing(20)

        # Upload button
        self.upload_btn = QPushButton("Upload CSV")
        self.upload_btn.setStyleSheet(styles.BUTTON_PRIMARY)
        self.upload_btn.clicked.connect(self._upload_file)
        top_bar.addWidget(self.upload_btn)

        # PDF download button
        self.pdf_btn = QPushButton("📄 PDF Report")
        self.pdf_btn.setStyleSheet(styles.BUTTON_SUCCESS)
        self.pdf_btn.clicked.connect(self._download_pdf_report)
        self.pdf_btn.setEnabled(False)
        top_bar.addWidget(self.pdf_btn)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #8b949e; margin-left: 10px;")
        top_bar.addWidget(self.status_label)
        top_bar.addStretch()

        # User info
        if self.username:
            user_label = QLabel(f"👤 {self.username}")
            user_label.setStyleSheet("color: #8b949e; font-size: 12px; margin-right: 10px;")
            top_bar.addWidget(user_label)

        # Logout button
        logout_btn = QPushButton("🚪")
        logout_btn.setToolTip("Logout")
        logout_btn.setStyleSheet(styles.BUTTON_DANGER)
        logout_btn.setFixedWidth(40)
        logout_btn.clicked.connect(self._handle_logout)
        top_bar.addWidget(logout_btn)

        return top_bar

    # --- Dashboard Tab Setup ---

    def _setup_dashboard_tab(self) -> None:
        """
        Set up the dashboard tab with charts and stats.
        Includes:
        - View Filters (CheckBoxes)
        - KPI Stats Cards
        - Outlier Alert Banner
        - Primary Matplotlib Canvas (Trends)
        - Advanced Analytics Group (Correlation/Efficiency)
        - Threshold Settings Group
        """
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(styles.SCROLL_AREA_STYLE)

        container = QWidget()
        layout = QVBoxLayout(container)

        # --- Customize View Controls ---
        view_layout = QHBoxLayout()
        view_label = QLabel("<b>Customize View:</b>")
        view_label.setStyleSheet("color: #8b949e; margin-right: 10px;")
        view_layout.addWidget(view_label)

        self.check_trends = QCheckBox("Trend Analysis")
        self.check_trends.setChecked(True)
        self.check_trends.setStyleSheet("color: #c5c6c7;")
        self.check_trends.toggled.connect(lambda c: self._toggle_section('show_trends', c))
        view_layout.addWidget(self.check_trends)

        self.check_corr = QCheckBox("Correlation Matrix")
        self.check_corr.setChecked(True)
        self.check_corr.setStyleSheet("color: #c5c6c7;")
        self.check_corr.toggled.connect(lambda c: self._toggle_section('show_correlation', c))
        view_layout.addWidget(self.check_corr)

        self.check_eff = QCheckBox("Efficiency Comparisons")
        self.check_eff.setChecked(True)
        self.check_eff.setStyleSheet("color: #c5c6c7;")
        self.check_eff.toggled.connect(lambda c: self._toggle_section('show_efficiency', c))
        view_layout.addWidget(self.check_eff)

        view_layout.addStretch()
        layout.addLayout(view_layout)


        # Stats cards
        stats_layout = QHBoxLayout()
        self.stat_labels = {
            "total": QLabel("Total\n-"),
            "flow": QLabel("Avg Flowrate\n-\n(Min: - | Max: -)"),
            "pressure": QLabel("Avg Pressure\n-\n(Min: - | Max: -)"),
            "temp": QLabel("Avg Temp\n-\n(Min: - | Max: -)")
        }
        for lbl in self.stat_labels.values():
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(styles.STAT_CARD_STYLE)
            stats_layout.addWidget(lbl)
        layout.addLayout(stats_layout)

        # Outlier alert group
        self.outlier_group = QGroupBox("⚠️ Outlier Detection")
        self.outlier_group.setStyleSheet(styles.OUTLIER_GROUP_STYLE)
        outlier_layout = QVBoxLayout()
        self.outlier_label = QLabel("No outliers detected.")
        self.outlier_label.setStyleSheet("color: #8b949e; font-weight: normal;")
        self.outlier_label.setWordWrap(True)
        outlier_layout.addWidget(self.outlier_label)
        self.outlier_group.setLayout(outlier_layout)
        self.outlier_group.setVisible(False)
        layout.addWidget(self.outlier_group)

        # Main charts
        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.figure.patch.set_facecolor(self.CHART_COLORS['bg'])
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet(f"background-color: {self.CHART_COLORS['bg']};")

        self.nav_toolbar = NavigationToolbar(self.canvas, self)
        self.nav_toolbar.setStyleSheet(styles.NAV_TOOLBAR_STYLE)
        layout.addWidget(self.nav_toolbar)
        layout.addWidget(self.canvas)

        # Advanced analytics (collapsible)
        self.advanced_group = self._create_advanced_analytics_group()
        layout.addWidget(self.advanced_group)

        # Threshold settings (collapsible)
        self.threshold_group = self._create_threshold_settings_group()
        layout.addWidget(self.threshold_group)

        scroll.setWidget(container)

        tab_layout = QVBoxLayout(self.dashboard_tab)
        tab_layout.addWidget(scroll)
        tab_layout.setContentsMargins(0, 0, 0, 0)

    def _create_advanced_analytics_group(self) -> QGroupBox:
        """Create the advanced analytics expandable section."""
        group = QGroupBox("🔬 Advanced Analytics (Click to expand)")
        group.setCheckable(True)
        group.setChecked(False)
        group.setStyleSheet(styles.ADVANCED_GROUP_STYLE)

        layout = QVBoxLayout()

        self.advanced_figure = Figure(figsize=(10, 8), dpi=100)
        self.advanced_figure.patch.set_facecolor(self.CHART_COLORS['bg'])
        self.advanced_canvas = FigureCanvas(self.advanced_figure)
        self.advanced_canvas.setStyleSheet(f"background-color: {self.CHART_COLORS['bg']};")

        self.advanced_nav_toolbar = NavigationToolbar(self.advanced_canvas, self)
        self.advanced_nav_toolbar.setStyleSheet(styles.NAV_TOOLBAR_STYLE)

        self.stats_summary_label = QLabel("")
        self.stats_summary_label.setStyleSheet(
            f"color: #c5c6c7; padding: 10px; background-color: {self.CHART_COLORS['bg']}; "
            "font-size: 11px; font-family: monospace;"
        )
        self.stats_summary_label.setWordWrap(True)

        layout.addWidget(self.advanced_nav_toolbar)
        layout.addWidget(self.advanced_canvas)
        layout.addWidget(self.stats_summary_label)
        group.setLayout(layout)

        # Initially hidden
        self.advanced_nav_toolbar.setVisible(False)
        self.advanced_canvas.setVisible(False)
        self.stats_summary_label.setVisible(False)

        group.toggled.connect(self._toggle_advanced_analytics)
        return group

    def _create_threshold_settings_group(self) -> QGroupBox:
        """Create the threshold settings expandable section."""
        group = QGroupBox("Threshold Settings (Click to expand)")
        group.setCheckable(True)
        group.setChecked(False)
        group.setStyleSheet(styles.THRESHOLD_GROUP_STYLE)

        threshold_layout = QVBoxLayout()

        # Container for content
        self.threshold_content = QWidget()
        content_layout = QVBoxLayout(self.threshold_content)

        # Status label
        self.threshold_status_label = QLabel("")
        self.threshold_status_label.setStyleSheet("color: #45a29e; font-size: 12px; margin-bottom: 8px;")
        content_layout.addWidget(self.threshold_status_label)

        # Warning slider
        warning_layout = QHBoxLayout()
        warning_label = QLabel("<b style='color: #e0a800;'>Warning Level:</b>")
        warning_label.setStyleSheet("color: #e0a800; min-width: 120px;")
        self.warning_slider = QSlider(Qt.Horizontal)
        self.warning_slider.setMinimum(50)
        self.warning_slider.setMaximum(95)
        self.warning_slider.setValue(75)
        self.warning_slider.setStyleSheet(styles.WARNING_SLIDER_STYLE)
        self.warning_value_label = QLabel("75th %ile")
        self.warning_value_label.setStyleSheet("color: #e0a800; min-width: 80px; font-weight: bold;")
        self.warning_slider.valueChanged.connect(lambda v: self.warning_value_label.setText(f"{v}th %ile"))
        warning_layout.addWidget(warning_label)
        warning_layout.addWidget(self.warning_slider)
        warning_layout.addWidget(self.warning_value_label)
        content_layout.addLayout(warning_layout)

        warning_desc = QLabel("<span style='color: #8b949e;'>Equipment above this percentile → ⚠️ Warning</span>")
        warning_desc.setStyleSheet("margin-left: 130px; font-size: 10px;")
        content_layout.addWidget(warning_desc)

        # IQR slider
        iqr_layout = QHBoxLayout()
        iqr_label = QLabel("<b style='color: #fc2044;'>Critical Level:</b>")
        iqr_label.setStyleSheet("color: #fc2044; min-width: 120px;")
        self.iqr_slider = QSlider(Qt.Horizontal)
        self.iqr_slider.setMinimum(5)
        self.iqr_slider.setMaximum(30)
        self.iqr_slider.setValue(15)
        self.iqr_slider.setStyleSheet(styles.IQR_SLIDER_STYLE)
        self.iqr_value_label = QLabel("1.5× IQR")
        self.iqr_value_label.setStyleSheet("color: #fc2044; min-width: 80px; font-weight: bold;")
        self.iqr_slider.valueChanged.connect(lambda v: self.iqr_value_label.setText(f"{v/10:.1f}× IQR"))
        iqr_layout.addWidget(iqr_label)
        iqr_layout.addWidget(self.iqr_slider)
        iqr_layout.addWidget(self.iqr_value_label)
        content_layout.addLayout(iqr_layout)

        iqr_desc = QLabel("<span style='color: #8b949e;'>Values beyond Q3 + multiplier × IQR → 🔴 Critical</span>")
        iqr_desc.setStyleSheet("margin-left: 130px; font-size: 10px;")
        content_layout.addWidget(iqr_desc)

        # Buttons
        btn_layout = QHBoxLayout()
        self.save_threshold_btn = QPushButton("💾 Save Settings")
        self.save_threshold_btn.setStyleSheet(styles.BUTTON_SAVE)
        self.save_threshold_btn.clicked.connect(self._save_threshold_settings)

        self.reset_threshold_btn = QPushButton("↻ Reset to Defaults")
        self.reset_threshold_btn.setStyleSheet(styles.BUTTON_RESET)
        self.reset_threshold_btn.clicked.connect(self._reset_threshold_settings)

        self.threshold_msg_label = QLabel("")
        self.threshold_msg_label.setStyleSheet("margin-left: 10px;")

        btn_layout.addWidget(self.save_threshold_btn)
        btn_layout.addWidget(self.reset_threshold_btn)
        btn_layout.addWidget(self.threshold_msg_label)
        btn_layout.addStretch()
        content_layout.addLayout(btn_layout)

        # Info note
        info_label = QLabel("💡 <span style='color: #8b949e;'>Changes apply to all your uploads.</span>")
        info_label.setStyleSheet("margin-top: 8px; font-size: 10px;")
        content_layout.addWidget(info_label)

        threshold_layout.addWidget(self.threshold_content)
        self.threshold_content.setVisible(False)
        group.setLayout(threshold_layout)

        group.toggled.connect(self._toggle_thresholds)
        return group

    # --- Data Tab Setup ---

    # --- Data Tab Setup ---

    def _setup_data_tab(self) -> None:
        """Set up the raw data table tab with filtering."""
        layout = QVBoxLayout(self.data_tab)

        # Filter Controls
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter Status:")
        filter_label.setStyleSheet("color: #c5c6c7; font-weight: bold;")
        filter_layout.addWidget(filter_label)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Statuses", "Normal", "Warning", "Critical"])
        self.status_filter.setStyleSheet("background: #0d1117; color: white; border: 1px solid #444c56; padding: 4px; border-radius: 4px;")
        self.status_filter.currentTextChanged.connect(self._handle_filter_change)
        filter_layout.addWidget(self.status_filter)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setStyleSheet(styles.TABLE_STYLE)
        layout.addWidget(self.table)

    # --- Feature implementation ---

    def _toggle_section(self, section_key: str, checked: bool) -> None:
        """Toggle visibility of dashboard sections."""
        self.view_settings[section_key] = checked
        
        if section_key == 'show_trends':
            # Toggle main chart canvas container if possible?
            # Actually, main chart (trends) is self.canvas
            self.canvas.setVisible(checked)
            self.nav_toolbar.setVisible(checked)
            
        elif section_key == 'show_correlation':
            # Part of advanced analytics
            if self.advanced_group.isChecked():
                self._update_advanced_charts(self.current_data['summary'], self.current_data['processed_data'])

        elif section_key == 'show_efficiency':
             if self.advanced_group.isChecked():
                self._update_advanced_charts(self.current_data['summary'], self.current_data['processed_data'])

    def _handle_filter_change(self, text: str) -> None:
        """Update table based on status filter."""
        mapping = {"All Statuses": "all", "Normal": "normal", "Warning": "warning", "Critical": "critical"}
        self.table_filter = mapping.get(text, "all")
        if self.current_data:
            self._update_table(self.current_data['processed_data'])

    def _handle_ai_query(self) -> None:
        """
        Handle user AI queries from the search bar.
        1. Validates input and data presence.
        2. Spawns a background thread (AIWorker) to prevent UI freezing.
        3. Updates status label to 'Thinking...'.
        """
        query = self.search_input.text().strip()
        if not query:
            return
            
        if not self.current_data:
            QMessageBox.warning(self, "No Data", "Please upload data first so the AI has context.")
            return

        # UI updates
        self.ask_ai_btn.setEnabled(False)
        self.search_input.setEnabled(False)
        self.status_label.setText("Thinking...")
        
        # Prepare context
        context = {
            "summary": self.current_data['summary'],
            "sample_records": self.current_data['processed_data'][:10]
        }
        
        # Start Worker
        self.ai_worker = AIWorker(query, context)
        self.ai_worker.finished.connect(self._on_ai_success)
        self.ai_worker.error.connect(self._on_ai_error)
        self.ai_worker.start()

    def _on_ai_error(self, error_msg: str) -> None:
        """Handle AI error."""
        self.status_label.setText("Error")
        self.ask_ai_btn.setEnabled(True)
        self.search_input.setEnabled(True)
        QMessageBox.warning(self, "AI Error", f"Failed to get response:\n{error_msg}")

    def _on_ai_success(self, result: dict) -> None:
        """Handle successful AI response."""
        self.status_label.setText("Ready")
        self.ask_ai_btn.setEnabled(True)
        self.search_input.setEnabled(True)

        if result:
            response_text = result['response']
            action = result.get('action')
            
            # Show Response
            dlg = QDialog(self)
            dlg.setWindowTitle("Carbon Sleuth AI")
            dlg.resize(600, 400)
            dlg_layout = QVBoxLayout(dlg)
            
            browser = QTextBrowser()
            browser.setOpenExternalLinks(True)
            browser.setMarkdown(response_text)
            browser.setStyleSheet("background-color: #0d1117; color: #c5c6c7; font-family: .AppleSystemUIFont; padding: 10px;")
            dlg_layout.addWidget(browser)
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dlg.accept)
            close_btn.setStyleSheet(styles.BUTTON_PRIMARY)
            dlg_layout.addWidget(close_btn)
            
            # Execute Action
            if action and action['type'] == 'SEARCH':
                term = action['payload'].lower()
                self.status_filter.setCurrentText("All Statuses") # Reset first
                if term in ['normal', 'warning', 'critical']:
                     self.status_filter.setCurrentText(term.capitalize())
                     self.tabs.setCurrentWidget(self.data_tab) # Switch to data tab
                     QMessageBox.information(dlg, "AI Action", f"Filtered table for '{term}' status.")
            
            dlg.exec_()

    # --- Prediction Tab ---

    def _setup_prediction_tab(self) -> None:
        """Set up the anomaly prediction and analysis tab."""
        layout = QVBoxLayout(self.prediction_tab)
        
        # Header
        header = QLabel("AI Anomaly Prediction & Insights")
        header.setStyleSheet("color: #66fcf1; font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Description
        desc = QLabel(
            "Use our AI engine to analyze current equipment data, detect subtle anomalies, "
            "and predict potential failures based on parameter correlations."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #c5c6c7; font-size: 13px; margin-bottom: 20px;")
        layout.addWidget(desc)
        
        # Action Button
        self.predict_btn = QPushButton("🚀 Run Deep Analysis")
        self.predict_btn.setMinimumHeight(50)
        self.predict_btn.setStyleSheet(styles.BUTTON_PRIMARY)
        self.predict_btn.clicked.connect(self._run_prediction_analysis)
        layout.addWidget(self.predict_btn)
        
        # Results Area
        self.prediction_result = QTextBrowser()
        self.prediction_result.setPlaceholderText("Analysis results will appear here...")
        self.prediction_result.setStyleSheet("""
            background-color: #0b0c10; 
            border: 1px solid #1f2833; 
            color: #c5c6c7; 
            padding: 15px; 
            font-family: 'Courier New';
            font-size: 13px;
        """)
        layout.addWidget(self.prediction_result)

    def _run_prediction_analysis(self) -> None:
        """Execute AI prediction analysis."""
        if not self.current_data:
            QMessageBox.warning(self, "No Data", "Please upload data first.")
            return
            
        self.predict_btn.setEnabled(False)
        self.predict_btn.setText("Analying Data Patterns...")
        self.prediction_result.setText("Process initiated...\nScancning parameters...\nIdentifying correlations...")
        QApplication.processEvents()
        
        query = (
            "Analyze this industrial equipment data for anomalies. "
            "Identify potential failure risks based on Flowrate, Pressure, and Temperature correlations. "
            "Provide a 'Future Risk Prediction' section."
        )
        
        context = {
            "summary": self.current_data['summary'],
            "outliers": self.current_data['summary'].get('outliers', [])
        }
        
        self.pred_worker = AIWorker(query, context)
        self.pred_worker.finished.connect(self._on_prediction_success)
        self.pred_worker.error.connect(self._on_prediction_error)
        self.pred_worker.start()

    def _format_ai_response_to_html(self, text: str) -> str:
        """
        Convert Markdown text to HTML with custom styling for tables.
        """
        import re
        
        # 1. Convert Headers
        # ### Header
        text = re.sub(r'^### (.*)$', r'<h3 style="color: #66fcf1; font-family: sans-serif; margin-top: 20px;">\1</h3>', text, flags=re.MULTILINE)
        # ## Header
        text = re.sub(r'^## (.*)$', r'<h2 style="color: #45a29e; font-family: sans-serif; margin-top: 25px;">\1</h2>', text, flags=re.MULTILINE)
        # **Bold**
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        
        # 2. Convert Tables (Simple Regex Parser)
        # Detect table block
        def replace_table(match):
            block = match.group(0)
            lines = block.strip().split('\n')
            if len(lines) < 2: return block
            
            html = '<table border="1" style="border-collapse: collapse; width: 100%; border-color: #45a29e; margin-bottom: 20px;">'
            
            # Header
            headers = [h.strip() for h in lines[0].strip('|').split('|')]
            html += '<thead><tr style="background-color: #1f2833; color: #66fcf1;">'
            for h in headers:
                html += f'<th style="padding: 10px; text-align: left; border: 1px solid #45a29e;">{h}</th>'
            html += '</tr></thead><tbody>'
            
            # Rows (skip separator line 1)
            for i in range(2, len(lines)):
                cells = [c.strip() for c in lines[i].strip('|').split('|')]
                bg_color = "#0b0c10" if i % 2 == 0 else "#14171f" # Stripe
                html += f'<tr style="background-color: {bg_color}; color: #c5c6c7;">'
                for c in cells:
                    # Clean up bold in cells
                    c = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', c)
                    html += f'<td style="padding: 8px; border: 1px solid #45a29e;">{c}</td>'
                html += '</tr>'
            
            html += '</tbody></table>'
            return html

        # Look for table patterns (lines starting with |)
        text = re.sub(r'((\|[^\n]+\|\n)+)', replace_table, text)
        
        # 3. Line Breaks
        text = text.replace('\n', '<br>')
        
        return f'<div style="font-family: sans-serif; font-size: 13px; line-height: 1.6;">{text}</div>'

    def _on_prediction_success(self, result: dict) -> None:
        self.predict_btn.setEnabled(True)
        self.predict_btn.setText("🚀 Run Deep Analysis")
        
        formatted_html = self._format_ai_response_to_html(result['response'])
        self.prediction_result.setHtml(formatted_html)
        
    def _on_prediction_error(self, error: str) -> None:
        self.predict_btn.setEnabled(True)
        self.predict_btn.setText("🚀 Run Deep Analysis")
        self.prediction_result.setText(f"Analysis Failed: {error}")

    # --- Auto Refresh ---

    def _start_auto_refresh(self) -> None:
        """Start the history auto-refresh timer."""
        self.timer = QTimer()
        self.timer.timeout.connect(self._refresh_history_silent)
        self.timer.start(30000)  # 30 seconds

    def _load_initial_data(self) -> None:
        """Load history and threshold settings on startup."""
        self._refresh_history()
        self._fetch_threshold_settings()

    # --- Event Handlers ---

    def _toggle_advanced_analytics(self, checked: bool) -> None:
        """Show/hide advanced analytics content."""
        self.advanced_nav_toolbar.setVisible(checked)
        self.advanced_canvas.setVisible(checked)
        self.stats_summary_label.setVisible(checked)

    def _toggle_thresholds(self, checked: bool) -> None:
        """Show/hide threshold settings content."""
        self.threshold_content.setVisible(checked)

    def _load_history_item(self, item) -> None:
        """Load data when a history item is clicked."""
        key = item.text()
        data = self.history_map.get(key)
        if data:
            self._update_ui(data)

    def _handle_logout(self) -> None:
        """Handle logout confirmation and cleanup."""
        reply = QMessageBox.question(
            self, 'Confirm Logout', 'Are you sure you want to logout?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.timer.stop()
            if self.logout_callback:
                self.logout_callback()
            self.close()

    # --- API Calls ---

    def _refresh_history(self) -> None:
        """Fetch history with error display."""
        self._refresh_history_silent(show_error=True)

    def _refresh_history_silent(self, show_error: bool = False) -> None:
        """Fetch history without blocking UI."""
        success, data = self.api_client.get_history()
        if success:
            self.history_list.clear()
            self.history_map = {}
            for item in data:
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
            QMessageBox.critical(self, "Error", f"Failed to fetch history: {data.get('error')}")

    def _fetch_threshold_settings(self) -> None:
        """Fetch threshold configuration from backend."""
        success, data = self.api_client.get_thresholds()
        if success:
            self.threshold_settings = data
            self._update_threshold_display()

    def _update_threshold_display(self) -> None:
        """Update threshold sliders and status from fetched settings."""
        if not self.threshold_settings:
            return

        warning = self.threshold_settings['warning_percentile']
        iqr = self.threshold_settings['outlier_iqr_multiplier']
        is_custom = self.threshold_settings.get('is_custom', False)

        # Update sliders without triggering signals
        self.warning_slider.blockSignals(True)
        self.warning_slider.setValue(int(warning * 100))
        self.warning_slider.blockSignals(False)
        self.warning_value_label.setText(f"{int(warning * 100)}th %ile")

        self.iqr_slider.blockSignals(True)
        self.iqr_slider.setValue(int(iqr * 10))
        self.iqr_slider.blockSignals(False)
        self.iqr_value_label.setText(f"{iqr:.1f}× IQR")

        # Update status
        if is_custom:
            self.threshold_status_label.setText("<b style='color: #66fcf1;'>[CUSTOM SETTINGS ACTIVE]</b>")
            self.reset_threshold_btn.setEnabled(True)
        else:
            self.threshold_status_label.setText("<span style='color: #8b949e;'>Using default settings</span>")
            self.reset_threshold_btn.setEnabled(False)

    def _save_threshold_settings(self) -> None:
        """Save custom threshold settings to backend."""
        warning = self.warning_slider.value() / 100.0
        iqr = self.iqr_slider.value() / 10.0

        self.save_threshold_btn.setEnabled(False)
        self.threshold_msg_label.setText("<span style='color: #8b949e;'>Saving...</span>")
        QApplication.processEvents()

        success, data = self.api_client.save_thresholds(warning, iqr)
        if success:
            self.threshold_settings = data
            self._update_threshold_display()
            self.threshold_msg_label.setText("<span style='color: #20fc8f;'>✓ Saved!</span>")
            if self.current_data:
                self._load_history_item(self.history_list.currentItem())
        else:
            self.threshold_msg_label.setText(f"<span style='color: #fc2044;'>✗ Error</span>")

        self.save_threshold_btn.setEnabled(True)

    def _reset_threshold_settings(self) -> None:
        """Reset threshold settings to defaults."""
        self.reset_threshold_btn.setEnabled(False)
        self.threshold_msg_label.setText("<span style='color: #8b949e;'>Resetting...</span>")
        QApplication.processEvents()

        success, data = self.api_client.reset_thresholds()
        if success:
            self.threshold_settings = data
            self._update_threshold_display()
            self.threshold_msg_label.setText("<span style='color: #20fc8f;'>✓ Reset!</span>")
            if self.current_data:
                self._load_history_item(self.history_list.currentItem())
        else:
            self.threshold_msg_label.setText(f"<span style='color: #fc2044;'>✗ Error</span>")

        self.reset_threshold_btn.setEnabled(True)

    def _upload_file(self) -> None:
        """Handle CSV file upload."""
        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

        fname, _ = QFileDialog.getOpenFileName(
            self, 'Open CSV', os.getenv('HOME'), "CSV Files (*.csv)"
        )
        if not fname:
            return

        file_size = os.path.getsize(fname)
        if file_size > MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            QMessageBox.warning(
                self, "File Too Large",
                f"Selected file is {size_mb:.2f} MB.\nMaximum allowed size is 5 MB."
            )
            return

        self.status_label.setText(f"Uploading ({file_size / 1024:.1f} KB)...")
        self.upload_btn.setEnabled(False)
        QApplication.processEvents()

        success, data = self.api_client.upload_file(fname)
        if success:
            self._update_ui(data)
            self.status_label.setText("✓ Upload Successful")
            self._refresh_history()
        else:
            self.status_label.setText("✗ Error")
            error_msg = data.get('error', 'Unknown error')
            QMessageBox.warning(self, "Upload Failed", f"Server responded:\n{error_msg}")

        self.upload_btn.setEnabled(True)

    def _download_pdf_report(self) -> None:
        """Download PDF report, ensuring AI summary exists first."""
        if not self.current_data:
            QMessageBox.warning(self, "No Data", "Please upload or select a dataset first.")
            return

        upload_id = self.current_data.get('id')
        if not upload_id:
            QMessageBox.warning(self, "Error", "No upload ID found.")
            return

        # Check if summary already exists locally (you might want to fetch from backend to be sure, 
        # but for now let's assume if we haven't generated it this session, we do it now)
        # Actually, let's just generate it fresh or update it.
        
        reply = QMessageBox.question(
            self, 'Generate Report', 
            'Would you like to include a fresh AI-generated summary in the PDF?\n(This takes a few seconds)',
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes
        )
        
        if reply == QMessageBox.Cancel:
            return
            
        if reply == QMessageBox.Yes:
            self._generate_summary_and_download(upload_id)
        else:
            self._proceed_download_pdf(upload_id)

    def _generate_summary_and_download(self, upload_id: int) -> None:
        """Generate AI summary, save to backend, then download."""
        self.status_label.setText("Generating AI Summary...")
        self.pdf_btn.setEnabled(False)
        
        query = (
            "Generate a professional executive summary for this equipment data report. "
            "Highlight key statistics, the number of outliers, and the general health of the system. "
            "Keep it concise (approx 150 words) and suitable for a formal PDF report."
        )
        
        context = {
            "summary": self.current_data['summary']
        }
        
        # Use a separate worker to avoid conflict if main search is running
        self.summary_worker = AIWorker(query, context)
        self.summary_worker.finished.connect(lambda res: self._on_summary_generated(res, upload_id))
        self.summary_worker.error.connect(lambda err: self._on_summary_error(err, upload_id))
        self.summary_worker.start()

    def _on_summary_generated(self, result: dict, upload_id: int) -> None:
        """Save summary to backend then download."""
        self.status_label.setText("Saving Summary...")
        summary_text = result['response']
        
        # Run save in background or main thread? Main thread is fine for quick API call, 
        # but technically should be threaded. `api_client` is synchronous. 
        # Let's hope it's fast.
        success, _ = self.api_client.save_ai_summary(upload_id, summary_text)
        
        if success:
            self._proceed_download_pdf(upload_id)
        else:
            QMessageBox.warning(self, "Warning", "Failed to save AI summary to report. Downloading without it.")
            self._proceed_download_pdf(upload_id)

    def _on_summary_error(self, error: str, upload_id: int) -> None:
        QMessageBox.warning(self, "AI Error", f"Failed to generate summary: {error}\nDownloading standard report.")
        self._proceed_download_pdf(upload_id)

    def _proceed_download_pdf(self, upload_id: int) -> None:
        """Actual download logic."""
        default_name = f"equipment_report_{upload_id}.pdf"
        fname, _ = QFileDialog.getSaveFileName(
            self, 'Save PDF Report',
            os.path.join(os.getenv('HOME'), default_name),
            "PDF Files (*.pdf)"
        )
        if not fname:
            self.status_label.setText("Ready")
            self.pdf_btn.setEnabled(True)
            return

        self.status_label.setText("Downloading PDF...")
        QApplication.processEvents()

        success, result_or_path = self.api_client.download_pdf(upload_id, fname)
        self.pdf_btn.setEnabled(True)
        self.status_label.setText("Ready")
        
        if success:
            QMessageBox.information(self, "Success", f"Report saved to:\n{fname}")
        else:
            self.status_label.setText("Download Failed")
            QMessageBox.warning(self, "Download Failed", result_or_path)

    # --- UI Updates ---

    def _update_ui(self, data: dict) -> None:
        """Update dashboard and table with new data."""
        self.current_data = data
        summary = data['summary']
        processed = data['processed_data']

        # Update stats cards
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

        # Update outlier alert
        outliers = summary.get('outliers', [])
        if outliers:
            self.outlier_group.setVisible(True)
            self.outlier_group.setTitle(f"[ALERT] {len(outliers)} DEVICES CRITICAL:")
            
            outlier_text = ""
            for outlier in outliers[:5]:
                outlier_text += f"<b>{outlier['equipment']}</b>: "
                params = [f"{p['parameter']} = {p['value']:.2f}" for p in outlier['parameters']]
                outlier_text += ", ".join(params) + "<br>"
            if len(outliers) > 5:
                outlier_text += f">>> and {len(outliers) - 5} more..."
            self.outlier_label.setText(outlier_text)
        else:
            self.outlier_group.setVisible(False)

        # Update table
        self._update_table(processed)

        # Update charts
        self._update_main_charts(summary)
        self._update_advanced_charts(summary, processed)

        # Enable PDF button
        self.pdf_btn.setEnabled(True)

    def _update_table(self, processed: list) -> None:
        """Update the data table with health status colors and filtering."""
        if not processed:
            return
            
        # Apply Filter
        filtered_data = processed
        if self.table_filter != 'all':
             filtered_data = [row for row in processed if row.get('health_status') == self.table_filter]

        if not filtered_data and processed:
            # If filtered result is empty but original is not, show placeholder or empty
            self.table.setRowCount(0)
            return

        # Use first row of *processed* (original) to get headers to ensure consistency
        # Or better, use filtered_data[0] if exists, else keep existing headers?
        # Let's use processed[0] for headers structure
        headers = list(processed[0].keys())
        if 'health_status' in headers:
            headers.remove('health_status')
        if 'health_color' in headers:
            headers.remove('health_color')
        headers.insert(0, 'Status')

        self.table.setColumnCount(len(headers))
        self.table.setRowCount(len(filtered_data))
        self.table.setHorizontalHeaderLabels(headers)

        for i, row in enumerate(filtered_data):
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

    def _update_main_charts(self, summary: dict) -> None:
        """Update the main dashboard charts."""
        self.figure.clear()
        colors = self.CHART_COLORS

        # Pie chart: Equipment types
        ax1 = self.figure.add_subplot(121)
        type_dist = summary['type_distribution']
        ax1.pie(
            type_dist.values(), labels=type_dist.keys(),
            autopct='%1.1f%%', startangle=90,
            textprops={'color': colors['text'], 'size': 9}
        )
        ax1.set_title("Equipment Types", color=colors['text'], fontsize=11)

        # Bar chart: Average parameters
        ax2 = self.figure.add_subplot(122)
        params = ['Flowrate', 'Pressure', 'Temp']
        vals = [summary['avg_flowrate'], summary['avg_pressure'], summary['avg_temperature']]
        ax2.bar(params, vals, color=[colors['accent_blue'], colors['accent_teal'], colors['accent_red']])
        ax2.set_title("Average Parameters", color=colors['text'], fontsize=11)
        ax2.tick_params(colors=colors['text'], labelsize=9)
        ax2.spines['bottom'].set_color(colors['border'])
        ax2.spines['left'].set_color(colors['border'])
        ax2.spines['top'].set_color('none')
        ax2.spines['right'].set_color('none')
        ax2.set_facecolor(colors['bg'])

        self.figure.tight_layout()
        self.canvas.draw()

    def _update_advanced_charts(self, summary: dict, processed: list) -> None:
        """Update the advanced analytics charts."""
        self.advanced_figure.clear()
        colors = self.CHART_COLORS

        # Type comparison bar chart
        if 'type_comparison' in summary and self.view_settings['show_efficiency']:
            ax1 = self.advanced_figure.add_subplot(221)
            type_comp = summary['type_comparison']
            types = list(type_comp.keys())
            x = np.arange(len(types))
            width = 0.25

            flowrates = [type_comp[t]['avg_flowrate'] for t in types]
            pressures = [type_comp[t]['avg_pressure'] for t in types]
            temps = [type_comp[t]['avg_temperature'] for t in types]

            ax1.bar(x - width, flowrates, width, label='Flowrate', color=colors['accent_blue'])
            ax1.bar(x, pressures, width, label='Pressure', color=colors['accent_purple'])
            ax1.bar(x + width, temps, width, label='Temperature', color=colors['accent_red'])

            ax1.set_title('Type Comparison', color=colors['text'], fontsize=10)
            ax1.set_xticks(x)
            ax1.set_xticklabels(types, rotation=45, ha='right', fontsize=8)
            ax1.tick_params(colors=colors['text'], labelsize=8)
            ax1.legend(fontsize=8, facecolor=colors['border'], edgecolor=colors['accent_teal'], labelcolor=colors['text'])
            ax1.set_facecolor(colors['bg'])
            for spine in ax1.spines.values():
                spine.set_color(colors['border'])

        # Correlation heatmap
        if 'correlation_matrix' in summary and self.view_settings['show_correlation']:
            ax2 = self.advanced_figure.add_subplot(222)
            corr_matrix = summary['correlation_matrix']
            params = ['Flowrate', 'Pressure', 'Temperature']
            corr_data = np.array([[corr_matrix[row][col] for col in params] for row in params])

            im = ax2.imshow(corr_data, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
            ax2.set_xticks(np.arange(len(params)))
            ax2.set_yticks(np.arange(len(params)))
            ax2.set_xticklabels(params, fontsize=8)
            ax2.set_yticklabels(params, fontsize=8)
            ax2.tick_params(colors=colors['text'], labelsize=8)

            for i in range(len(params)):
                for j in range(len(params)):
                    text_color = 'white' if abs(corr_data[i, j]) > 0.5 else colors['bg']
                    ax2.text(j, i, f'{corr_data[i, j]:.2f}', ha="center", va="center", color=text_color, fontsize=9)

            ax2.set_title('Correlation Matrix', color=colors['text'], fontsize=10)
            ax2.set_facecolor(colors['bg'])
            cbar = self.advanced_figure.colorbar(im, ax=ax2)
            cbar.ax.tick_params(colors=colors['text'], labelsize=7)

        # Standard deviation bars
        ax3 = self.advanced_figure.add_subplot(223)
        std_params = ['Flowrate', 'Pressure', 'Temp']
        std_vals = [
            summary.get('std_flowrate', 0),
            summary.get('std_pressure', 0),
            summary.get('std_temperature', 0)
        ]
        ax3.bar(std_params, std_vals, color=[colors['accent_blue'], colors['accent_purple'], colors['accent_red']])
        ax3.set_title('Standard Deviation', color=colors['text'], fontsize=10)
        ax3.tick_params(colors=colors['text'], labelsize=8)
        ax3.set_facecolor(colors['bg'])
        for spine in ax3.spines.values():
            spine.set_color(colors['border'])

        # Health status pie chart
        ax4 = self.advanced_figure.add_subplot(224)
        if processed:
            health_counts = {'normal': 0, 'warning': 0, 'critical': 0}
            for row in processed:
                status = row.get('health_status', 'normal')
                health_counts[status] += 1

            colors_map = {'normal': '#20fc8f', 'warning': '#e0a800', 'critical': '#fc2044'}
            labels = [f"{k.upper()}\n({v})" for k, v in health_counts.items() if v > 0]
            values = [v for v in health_counts.values() if v > 0]
            pie_colors = [colors_map[k] for k, v in health_counts.items() if v > 0]

            ax4.pie(values, labels=labels, colors=pie_colors, autopct='%1.1f%%',
                    textprops={'color': colors['text'], 'size': 8})
            ax4.set_title('Health Status Distribution', color=colors['text'], fontsize=10)

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
