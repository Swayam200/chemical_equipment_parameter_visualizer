from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import UploadedFile
import io
import pandas as pd

class ApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        
        # Create a dummy csv
        data = {
            'Equipment Name': ['P1', 'V1'],
            'Type': ['Pump', 'Valve'],
            'Flowrate': [100, 50],
            'Pressure': [5.0, 4.0],
            'Temperature': [120, 100]
        }
        df = pd.DataFrame(data)
        self.csv_file = io.StringIO()
        df.to_csv(self.csv_file, index=False)
        self.csv_file.seek(0)

    def test_upload_success(self):
        """Test that a valid CSV upload works."""
        self.csv_file.name = 'test.csv'
        response = self.client.post('/api/upload/', {'file': self.csv_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UploadedFile.objects.count(), 1)
        self.assertIn('summary', response.data)

    def test_upload_invalid_columns(self):
        """Test that missing columns triggers an error."""
        invalid_csv = io.StringIO("Col1,Col2\n1,2")
        invalid_csv.name = 'invalid.csv'
        response = self.client.post('/api/upload/', {'file': invalid_csv}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('Missing required columns', response.data['error'])

    def test_history_limit(self):
        """Test that we only keep 5 items."""
        # Create 6 uploads
        for i in range(6):
            f = io.StringIO(f"Equipment Name,Type,Flowrate,Pressure,Temperature\nP{i},Pump,100,5,100")
            f.name = f'test_{i}.csv'
            self.client.post('/api/upload/', {'file': f}, format='multipart')
        
        self.assertEqual(UploadedFile.objects.count(), 5)

    def test_auth_required(self):
        """Test that unauthenticated requests fail."""
        self.client.logout()
        response = self.client.get('/api/history/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
