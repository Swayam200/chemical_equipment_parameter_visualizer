from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .models import UploadedFile
from .serializers import UploadedFileSerializer
import pandas as pd
import os
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        # Validation
        if not username or not email or not password:
            return Response(
                {'error': 'All fields are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Username already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(password) < 8:
            return Response(
                {'error': 'Password must be at least 8 characters'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }, status=status.HTTP_200_OK)
        
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        # Simple check: did they actually send a file?
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        # We only want CSVs here.
        if not file.name.endswith('.csv'):
             return Response({"error": "Only CSV files are allowed"}, status=status.HTTP_400_BAD_REQUEST)

        # Save the file temporarily so we can pass the path to Pandas.
        # This creates a record in the DB and puts the file in /media/uploads
        # Associate upload with the logged-in user
        upload_instance = UploadedFile(file=file, user=request.user)
        upload_instance.save() 

        try:
            # Time to crunch some numbers.
            file_path = upload_instance.file.path
            df = pd.read_csv(file_path)
            
            # Validation: Check for required columns
            required_columns = {'Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'}
            if not required_columns.issubset(df.columns):
                raise ValueError(f"Missing required columns. Expected: {required_columns}")

            # We're calculating some basic stats to show on the dashboard immediately.
            # This saves the frontend from having to iterate through thousands of rows for simple counts.
            stats = {
                "total_count": int(len(df)),
                # Using .get() style defaults just in case columns are missing or named slightly differently
                "avg_flowrate": float(df['Flowrate'].mean()) if 'Flowrate' in df.columns else 0,
                "avg_pressure": float(df['Pressure'].mean()) if 'Pressure' in df.columns else 0,
                "avg_temperature": float(df['Temperature'].mean()) if 'Temperature' in df.columns else 0,
                "type_distribution": df['Type'].value_counts().to_dict() if 'Type' in df.columns else {}
            }

            # We also send back the raw data so the frontend can display the table.
            # .to_dict('records') gives us a nice list of JSON objects.
            data_json = df.to_dict(orient='records')

            # Save the results back to the instance so we don't have to re-process it later.
            upload_instance.summary = stats
            upload_instance.processed_data = data_json
            upload_instance.save()

            # Housekeeping: We only want to keep the last 5 uploads PER USER to avoid cluttering the server.
            # If we represent a real production app, we might archive these instead or use S3 with lifecycle policies.
            user_files = UploadedFile.objects.filter(user=request.user)
            if user_files.count() > 5:
                # Get the IDs of the 5 newest files for this user, and delete anything that's NOT in that list.
                ids_to_keep = user_files[:5].values_list('id', flat=True)
                UploadedFile.objects.filter(user=request.user).exclude(id__in=ids_to_keep).delete()

            serializer = UploadedFileSerializer(upload_instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # If anything goes wrong (bad CSV format, permissions, etc), cleanup the database record.
            upload_instance.delete()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HistoryView(generics.ListAPIView):
    serializer_class = UploadedFileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Return only the current user's uploads
        return UploadedFile.objects.filter(user=self.request.user)[:5]

class PDFReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        try:
            # Ensure user can only access their own reports
            instance = UploadedFile.objects.get(pk=pk, user=request.user)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="report_{pk}.pdf"'

            p = canvas.Canvas(response)
            p.drawString(100, 800, f"Equipment Data Analysis Report - ID {pk}")
            p.drawString(100, 780, f"Uploaded At: {instance.uploaded_at}")
            
            stats = instance.summary
            p.drawString(100, 750, "Summary Statistics:")
            p.drawString(120, 730, f"Total Equipment Count: {stats.get('total_count', 0)}")
            p.drawString(120, 715, f"Average Flowrate: {stats.get('avg_flowrate', 0):.2f}")
            p.drawString(120, 700, f"Average Pressure: {stats.get('avg_pressure', 0):.2f}")
            p.drawString(120, 685, f"Average Temperature: {stats.get('avg_temperature', 0):.2f}")

            p.drawString(100, 650, "Type Distribution:")
            y = 635
            for k, v in stats.get('type_distribution', {}).items():
                p.drawString(120, y, f"{k}: {v}")
                y -= 15
            
            p.showPage()
            p.save()
            return response
        except UploadedFile.DoesNotExist:
            return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
