"""
Application Stylesheet
Defines QSS styles for the PyQt5 application.
"""

# Colors
COLOR_BG = "#0b0c10"
COLOR_SIDEBAR = "#1f2833"
COLOR_TEXT_PRIMARY = "#c5c6c7"
COLOR_TEXT_SECONDARY = "#8b949e"
COLOR_ACCENT_BLUE = "#66fcf1"
COLOR_ACCENT_TEAL = "#45a29e"

# Window
MAIN_WINDOW_STYLE = f"""
    background-color: {COLOR_BG};
    color: {COLOR_TEXT_PRIMARY};
"""

# Sidebar
SIDEBAR_STYLE = f"""
    background-color: {COLOR_SIDEBAR};
    border-right: 1px solid #000;
    padding: 10px;
"""

# Buttons
BUTTON_BASE = """
    QPushButton {
        border-radius: 4px;
        padding: 6px 12px;
        font-weight: bold;
        border: none;
    }
    QPushButton:disabled {
        background-color: #2d333b;
        color: #444c56;
    }
"""

BUTTON_PRIMARY = BUTTON_BASE + f"""
    QPushButton {{
        background-color: {COLOR_ACCENT_BLUE};
        color: #0b0c10;
    }}
    QPushButton:hover {{
        background-color: #45a29e;
    }}
"""

BUTTON_SUCCESS = BUTTON_BASE + """
    QPushButton {
        background-color: #20fc8f;
        color: #0b0c10;
    }
    QPushButton:hover {
        background-color: #16c973;
    }
"""

BUTTON_DANGER = BUTTON_BASE + """
    QPushButton {
        background-color: #fc2044;
        color: white;
    }
    QPushButton:hover {
        background-color: #c91936;
    }
"""

BUTTON_SAVE = BUTTON_BASE + f"""
    QPushButton {{
        background-color: {COLOR_ACCENT_TEAL};
        color: #0b0c10;
    }}
    QPushButton:hover {{
        background-color: #3b8c89;
    }}
"""

BUTTON_RESET = BUTTON_BASE + """
    QPushButton {
        background-color: #2d333b;
        color: #c5c6c7;
        border: 1px solid #444c56;
    }
    QPushButton:hover {
        background-color: #373e47;
    }
"""

# Other elements
SCROLL_AREA_STYLE = f"background-color: {COLOR_BG}; border: none;"
STAT_CARD_STYLE = f"""
    background-color: {COLOR_SIDEBAR};
    border-radius: 8px;
    padding: 10px;
    color: {COLOR_TEXT_PRIMARY};
    font-size: 13px;
    font-weight: bold;
"""
OUTLIER_GROUP_STYLE = f"""
    QGroupBox {{
        background-color: rgba(252, 32, 68, 0.1);
        border: 1px solid #fc2044;
        border-radius: 6px;
        margin-top: 20px; /* Increased margin to clear title */
        font-size: 13px;
        color: #fc2044;
        font-weight: bold;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 10px;
        padding: 0 5px;
        background-color: transparent; /* Ensure no background block */
    }}
"""

ADVANCED_GROUP_STYLE = f"""
    QGroupBox {{
        border: 1px solid {COLOR_SIDEBAR};
        border-radius: 6px;
        margin-top: 20px;
        padding-top: 10px;
        font-weight: bold;
        color: {COLOR_TEXT_PRIMARY};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }}
"""

THRESHOLD_GROUP_STYLE = ADVANCED_GROUP_STYLE

THRESHOLD_GROUP_STYLE = ADVANCED_GROUP_STYLE

# Make toolbar background light so black icons are visible
NAV_TOOLBAR_STYLE = f"background-color: #e6edf3; border-radius: 4px; padding: 2px;"

WARNING_SLIDER_STYLE = """
    QSlider::groove:horizontal {
        border: 1px solid #bbb;
        background: white;
        height: 6px;
        border-radius: 3px;
    }
    QSlider::sub-page:horizontal {
        background: #e0a800;
        border-radius: 3px;
    }
    QSlider::handle:horizontal {
        background: #e0a800;
        border: 1px solid #e0a800;
        width: 14px;
        height: 14px;
        margin: -5px 0; 
        border-radius: 7px;
    }
"""

IQR_SLIDER_STYLE = """
    QSlider::groove:horizontal {
        border: 1px solid #bbb;
        background: white;
        height: 6px;
        border-radius: 3px;
    }
    QSlider::sub-page:horizontal {
        background: #fc2044;
        border-radius: 3px;
    }
    QSlider::handle:horizontal {
        background: #fc2044;
        border: 1px solid #fc2044;
        width: 14px;
        height: 14px;
        margin: -5px 0; 
        border-radius: 7px;
    }
"""

TABLE_STYLE = f"""
    QTableWidget {{
        background-color: {COLOR_BG};
        gridline-color: {COLOR_SIDEBAR};
        color: {COLOR_TEXT_PRIMARY};
    }}
    QHeaderView::section {{
        background-color: {COLOR_SIDEBAR};
        color: {COLOR_TEXT_SECONDARY};
        padding: 5px;
        border: none;
    }}
    QTableCornerButton::section {{
        background-color: {COLOR_SIDEBAR};
        border: none;
    }}
"""

# --- Login Dialog Styles ---

def get_login_dialog_style(img_path: str) -> str:
    # Use forward slashes for CSS path compatibility
    clean_path = img_path.replace("\\", "/")
    return f"""
        QDialog {{
            background-image: url('{clean_path}');
            background-position: center;
            background-repeat: no-repeat;
            background-color: #0b0c10;
        }}
    """

LOGIN_CONTAINER_STYLE = f"""
    QWidget {{
        background-color: rgba(11, 12, 16, 0.85);
        border: 1px solid {COLOR_SIDEBAR};
        border-radius: 12px;
    }}
"""

LOGIN_HEADER_STYLE = f"""
    color: {COLOR_ACCENT_BLUE};
    font-size: 24px;
    font-weight: bold;
    letter-spacing: 2px;
"""

LOGIN_SUBHEADER_STYLE = f"""
    color: {COLOR_TEXT_SECONDARY};
    font-family: 'Courier New';
    font-size: 11px;
    margin-bottom: 20px;
"""

LOGIN_INPUT_STYLE = f"""
    QLineEdit {{
        background-color: rgba(31, 40, 51, 0.6);
        border: 1px solid {COLOR_SIDEBAR};
        border-radius: 4px;
        color: {COLOR_ACCENT_TEAL};
        padding: 10px;
        font-family: 'Courier New';
        font-size: 13px;
    }}
    QLineEdit:focus {{
        border: 1px solid {COLOR_ACCENT_BLUE};
        background-color: rgba(31, 40, 51, 0.9);
    }}
"""

LOGIN_ACTION_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {COLOR_ACCENT_BLUE};
        color: #0b0c10;
        border: none;
        border-radius: 4px;
        padding: 12px;
        font-weight: bold;
        letter-spacing: 1px;
    }}
    QPushButton:hover {{
        background-color: #45a29e;
    }}
"""

LOGIN_TOGGLE_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: transparent;
        color: {COLOR_TEXT_SECONDARY};
        border: none;
        font-family: monospace;
        font-size: 11px;
    }}
    QPushButton:hover {{
        color: {COLOR_TEXT_PRIMARY};
        text-decoration: underline;
    }}
"""

LOGIN_EXIT_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: transparent;
        color: #fc2044;
        border: 1px solid #fc2044;
        border-radius: 4px;
        padding: 8px;
        font-size: 10px;
        margin-top: 10px;
    }}
    QPushButton:hover {{
        background-color: rgba(252, 32, 68, 0.1);
    }}
"""
