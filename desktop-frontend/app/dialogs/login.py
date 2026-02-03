"""
Login Dialog for the Desktop App.
Provides user authentication and registration UI.
"""
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt

from ..api_client import ApiClient
from .. import styles


class LoginDialog(QDialog):
    """
    Frameless login dialog with glassmorphism styling.
    Supports login/register mode toggle.
    """

    def __init__(self, api_client: ApiClient):
        super().__init__()
        self.api_client = api_client
        self.is_register_mode = False

        self._setup_window()
        self._setup_ui()

    def _setup_window(self) -> None:
        """Configure window properties."""
        self.setWindowTitle("Access Terminal - Verification Required")
        self.setFixedSize(450, 600)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        # Background image from assets
        img_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'src', 'assets', 'images', 'chemical_plant_login.jpg'
        )
        self.setStyleSheet(styles.get_login_dialog_style(img_path))

    def _setup_ui(self) -> None:
        """Build the login form UI."""
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        # Glassmorphism container
        self.container = QWidget()
        self.container.setFixedSize(380, 500)
        self.container.setStyleSheet(styles.LOGIN_CONTAINER_STYLE)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(30, 40, 30, 40)
        container_layout.setSpacing(15)

        # Logo
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'logo.png')
        if os.path.exists(logo_path):
            from PyQt5.QtGui import QPixmap, QImage
            # Load and scale logo
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                 scaled = pixmap.scaled(200, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                 logo_label.setPixmap(scaled)
                 logo_label.setAlignment(Qt.AlignCenter)
                 container_layout.addWidget(logo_label)

        # Header
        header_label = QLabel("SYSTEM ACCESS")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet(styles.LOGIN_HEADER_STYLE)
        container_layout.addWidget(header_label)

        # Subheader (mode indicator)
        self.mode_label = QLabel("> INITIATE LOGIN_SEQUENCE")
        self.mode_label.setAlignment(Qt.AlignCenter)
        self.mode_label.setStyleSheet(styles.LOGIN_SUBHEADER_STYLE)
        container_layout.addWidget(self.mode_label)

        # Form inputs
        self.username = self._create_input("USERNAME")
        self.email = self._create_input("EMAIL_ADDRESS")
        self.password = self._create_input("PASSWORD", is_password=True)
        self.confirm_password = self._create_input("CONFIRM_CREDENTIALS", is_password=True)

        container_layout.addWidget(self.username)
        container_layout.addWidget(self.email)
        container_layout.addWidget(self.password)
        container_layout.addWidget(self.confirm_password)

        # Hide register-only fields initially
        self.email.setVisible(False)
        self.confirm_password.setVisible(False)

        # Action button (Login/Register)
        self.action_btn = QPushButton("ESTABLISH_LINK")
        self.action_btn.setCursor(Qt.PointingHandCursor)
        self.action_btn.setStyleSheet(styles.LOGIN_ACTION_BUTTON_STYLE)
        self.action_btn.clicked.connect(self._handle_action)
        container_layout.addWidget(self.action_btn)

        # Toggle mode button
        self.toggle_btn = QPushButton("[ NEW_USER? REGISTER ]")
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.setStyleSheet(styles.LOGIN_TOGGLE_BUTTON_STYLE)
        self.toggle_btn.clicked.connect(self._toggle_mode)
        container_layout.addWidget(self.toggle_btn)

        # Exit button (frameless window needs explicit close)
        self.exit_btn = QPushButton("TERMINATE_SESSION")
        self.exit_btn.setCursor(Qt.PointingHandCursor)
        self.exit_btn.setStyleSheet(styles.LOGIN_EXIT_BUTTON_STYLE)
        self.exit_btn.clicked.connect(self.reject)
        container_layout.addWidget(self.exit_btn)

        container_layout.addStretch()
        main_layout.addWidget(self.container)
        self.setLayout(main_layout)

    def _create_input(self, placeholder: str, is_password: bool = False) -> QLineEdit:
        """Create a styled input field."""
        inp = QLineEdit()
        inp.setPlaceholderText(f"[{placeholder}]")
        if is_password:
            inp.setEchoMode(QLineEdit.Password)
        inp.setStyleSheet(styles.LOGIN_INPUT_STYLE)
        return inp

    def _toggle_mode(self) -> None:
        """Switch between login and register modes."""
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

    def _handle_action(self) -> None:
        """Handle the primary action button click."""
        if self.is_register_mode:
            self._handle_register()
        else:
            self.accept()  # Login flow handled by caller

    def _handle_register(self) -> None:
        """Process registration form."""
        username = self.username.text().strip()
        email = self.email.text().strip()
        password = self.password.text()
        confirm = self.confirm_password.text()

        # Validation
        if not username or not email or not password or not confirm:
            QMessageBox.warning(self, "Error", "MISSING_FIELDS")
            return

        if password != confirm:
            QMessageBox.warning(self, "Error", "PASSWORD_MISMATCH")
            return

        if len(password) < 8:
            QMessageBox.warning(self, "Error", "PASSWORD_TOO_SHORT_MIN_8")
            return

        # API call
        success, data = self.api_client.register(username, email, password)
        if success:
            QMessageBox.information(self, "Success", "REGISTRATION_COMPLETE. PROCEED TO LOGIN.")
            self._toggle_mode()
        else:
            error_msg = data.get('error', 'REGISTRATION_FAILED')
            QMessageBox.warning(self, "Failed", error_msg.upper())

    def get_credentials(self) -> tuple:
        """Return entered username and password."""
        return self.username.text().strip(), self.password.text()
