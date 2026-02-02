"""
API Client for the Desktop App.
Handles all HTTP requests to the Django backend.
"""
import requests
from typing import Optional, Tuple, Dict, Any

# Default API URL (local development)
DEFAULT_API_URL = "http://127.0.0.1:8000/api/"


class ApiClient:
    """
    Encapsulates all API calls to the Django backend.
    Manages auth header and provides typed methods for each endpoint.
    """

    def __init__(self, base_url: str = DEFAULT_API_URL):
        self.base_url = base_url
        self.auth_header: Optional[str] = None

    def set_auth(self, token: str) -> None:
        """Set the JWT auth header for authenticated requests."""
        self.auth_header = f"Bearer {token}"

    def clear_auth(self) -> None:
        """Clear auth credentials (logout)."""
        self.auth_header = None

    def _get_headers(self) -> Dict[str, str]:
        """Build headers dict including auth if available."""
        headers = {}
        if self.auth_header:
            headers['Authorization'] = self.auth_header
        return headers

    # --- Auth Endpoints ---

    def login(self, username: str, password: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Authenticate user and get JWT tokens.
        Returns (success, response_data).
        """
        try:
            res = requests.post(
                f"{self.base_url}login/",
                data={'username': username, 'password': password}
            )
            if res.status_code == 200:
                data = res.json()
                self.set_auth(data['access'])
                return True, data
            return False, res.json() if res.text else {'error': f'Status {res.status_code}'}
        except requests.exceptions.ConnectionError as e:
            return False, {'error': f'Connection failed: {e}'}
        except Exception as e:
            return False, {'error': str(e)}

    def register(self, username: str, email: str, password: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Register a new user.
        Returns (success, response_data).
        """
        try:
            res = requests.post(
                f"{self.base_url}register/",
                json={'username': username, 'email': email, 'password': password}
            )
            if res.status_code == 201:
                return True, res.json()
            return False, res.json() if res.text else {'error': f'Status {res.status_code}'}
        except requests.exceptions.ConnectionError as e:
            return False, {'error': f'Connection failed: {e}'}
        except Exception as e:
            return False, {'error': str(e)}

    # --- Data Endpoints ---

    def upload_file(self, file_path: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Upload a CSV file to the backend.
        Returns (success, response_data).
        """
        try:
            with open(file_path, 'rb') as f:
                res = requests.post(
                    f"{self.base_url}upload/",
                    files={'file': f},
                    headers=self._get_headers()
                )
            if res.status_code == 201:
                return True, res.json()
            return False, res.json() if res.text else {'error': f'Status {res.status_code}'}
        except requests.exceptions.ConnectionError as e:
            return False, {'error': f'Connection failed: {e}'}
        except Exception as e:
            return False, {'error': str(e)}

    def get_history(self) -> Tuple[bool, Any]:
        """
        Fetch the last 5 uploads for the current user.
        Returns (success, response_data).
        """
        try:
            res = requests.get(f"{self.base_url}history/", headers=self._get_headers())
            if res.status_code == 200:
                return True, res.json()
            return False, {'error': f'Status {res.status_code}'}
        except Exception as e:
            return False, {'error': str(e)}

    # --- Threshold Endpoints ---

    def get_thresholds(self) -> Tuple[bool, Dict[str, Any]]:
        """Fetch user's threshold settings."""
        try:
            res = requests.get(f"{self.base_url}thresholds/", headers=self._get_headers())
            if res.status_code == 200:
                return True, res.json()
            return False, {'error': f'Status {res.status_code}'}
        except Exception as e:
            return False, {'error': str(e)}

    def save_thresholds(self, warning_percentile: float, iqr_multiplier: float) -> Tuple[bool, Dict[str, Any]]:
        """Save custom threshold settings."""
        try:
            res = requests.put(
                f"{self.base_url}thresholds/",
                json={'warning_percentile': warning_percentile, 'outlier_iqr_multiplier': iqr_multiplier},
                headers={**self._get_headers(), 'Content-Type': 'application/json'}
            )
            if res.status_code == 200:
                return True, res.json()
            return False, {'error': f'Status {res.status_code}'}
        except Exception as e:
            return False, {'error': str(e)}

    def reset_thresholds(self) -> Tuple[bool, Dict[str, Any]]:
        """Reset threshold settings to defaults."""
        try:
            res = requests.delete(f"{self.base_url}thresholds/", headers=self._get_headers())
            if res.status_code == 200:
                return True, res.json()
            return False, {'error': f'Status {res.status_code}'}
        except Exception as e:
            return False, {'error': str(e)}

    def save_ai_summary(self, upload_id: int, summary_text: str) -> Tuple[bool, Dict[str, Any]]:
        """Save AI summary for an upload."""
        try:
            res = requests.post(
                f"{self.base_url}upload/{upload_id}/summary/",
                json={'summary': summary_text},
                headers={**self._get_headers(), 'Content-Type': 'application/json'}
            )
            if res.status_code == 200:
                return True, res.json()
            return False, res.json() if res.text else {'error': f'Status {res.status_code}'}
        except Exception as e:
            return False, {'error': str(e)}

    # --- Report Endpoints ---

    def download_pdf(self, upload_id: int, save_path: str) -> Tuple[bool, str]:
        """
        Download PDF report for a given upload.
        Returns (success, message_or_error).
        """
        try:
            res = requests.get(
                f"{self.base_url}report/{upload_id}/",
                headers=self._get_headers(),
                stream=True
            )
            if res.status_code == 200:
                with open(save_path, 'wb') as f:
                    for chunk in res.iter_content(chunk_size=8192):
                        f.write(chunk)
                return True, save_path
            return False, f'Server responded: {res.status_code}'
        except Exception as e:
            return False, str(e)
