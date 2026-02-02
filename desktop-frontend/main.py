#!/usr/bin/env python3
"""
Chemical Equipment Parameter Visualizer - Desktop Application
Entry point for the PyQt5 desktop frontend.
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file (web-frontend/.env or current dir)
# Try to find web-frontend .env first
current_dir = os.path.dirname(os.path.abspath(__file__))
web_env = os.path.join(current_dir, '..', 'web-frontend', '.env')
if os.path.exists(web_env):
    load_dotenv(web_env)
else:
    load_dotenv()

from PyQt5.QtWidgets import QApplication, QMessageBox

from app.api_client import ApiClient
from app.dialogs import LoginDialog
from app.windows import MainWindow


def main():
    """Application entry point with login loop."""
    app = QApplication(sys.argv)

    # Single shared API client instance
    api_client = ApiClient()

    def run_app():
        """Run the login -> main window loop."""
        while True:
            # Show login dialog
            login_diag = LoginDialog(api_client)
            result = login_diag.exec_()

            if result != LoginDialog.Accepted:
                # User cancelled login
                break

            # Attempt authentication
            username, password = login_diag.get_credentials()
            success, data = api_client.login(username, password)

            if success:
                # Logged in - show main window with logout callback
                window = MainWindow(
                    api_client=api_client,
                    username=username,
                    logout_callback=lambda: None  # Logout triggers window close -> loop continues
                )
                window.show()
                app.exec_()  # Run until window closes

                # After window closes, clear auth and loop back to login
                api_client.clear_auth()
            else:
                error_msg = data.get('error', 'Login failed')
                QMessageBox.warning(None, "Login Failed", str(error_msg).upper())

    run_app()
    return 0


if __name__ == "__main__":
    sys.exit(main())
