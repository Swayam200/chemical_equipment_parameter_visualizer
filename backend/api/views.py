from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .models import UploadedFile, UserThresholdSettings
from .serializers import UploadedFileSerializer
import pandas as pd
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from datetime import datetime

def get_threshold_settings(user=None):
    """
    Get threshold settings with priority:
    1. User's custom settings (if exists in database)
    2. .env file settings
    3. Hardcoded defaults (0.75, 1.5)
    
    Returns: (warning_percentile, outlier_iqr_multiplier)
    """
    # Check for user-specific settings first
    if user:
        try:
            settings = UserThresholdSettings.objects.get(user=user)
            return settings.warning_percentile, settings.outlier_iqr_multiplier
        except UserThresholdSettings.DoesNotExist:
            pass  # Fall through to .env defaults
    
    # Existing .env logic as fallback
    try:
        warning = float(os.getenv('WARNING_PERCENTILE', '0.75'))
        if not (0.5 <= warning <= 0.95):
            warning = 0.75
    except (ValueError, TypeError):
        warning = 0.75
    
    try:
        outlier = float(os.getenv('OUTLIER_IQR_MULTIPLIER', '1.5'))
        if not (0.5 <= outlier <= 3.0):
            outlier = 1.5
    except (ValueError, TypeError):
        outlier = 1.5
    
    return warning, outlier

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

class ThresholdSettingsView(APIView):
    """
    API endpoint to retrieve and update threshold configuration.
    GET: Returns current effective settings (user's custom or defaults)
    PUT: Create or update user's custom settings
    DELETE: Reset to defaults (remove custom settings)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user's effective threshold settings."""
        # Check if user has custom settings
        is_custom = UserThresholdSettings.objects.filter(user=request.user).exists()
        warning_percentile, iqr_multiplier = get_threshold_settings(request.user)
        
        return Response({
            'warning_percentile': warning_percentile,
            'outlier_iqr_multiplier': iqr_multiplier,
            'is_custom': is_custom,
            'description': {
                'warning_percentile': f'Equipment with parameters above the {int(warning_percentile * 100)}th percentile are marked as Warning',
                'outlier_iqr_multiplier': f'Values beyond Q3 + {iqr_multiplier} × IQR are marked as outliers (Critical)'
            }
        }, status=status.HTTP_200_OK)
    
    def put(self, request):
        """Create or update user's custom threshold settings."""
        warning_percentile = request.data.get('warning_percentile')
        iqr_multiplier = request.data.get('outlier_iqr_multiplier')
        
        # Validate inputs
        errors = {}
        if warning_percentile is not None:
            try:
                warning_percentile = float(warning_percentile)
                if not (0.5 <= warning_percentile <= 0.95):
                    errors['warning_percentile'] = 'Must be between 0.50 and 0.95'
            except (ValueError, TypeError):
                errors['warning_percentile'] = 'Must be a valid number'
        
        if iqr_multiplier is not None:
            try:
                iqr_multiplier = float(iqr_multiplier)
                if not (0.5 <= iqr_multiplier <= 3.0):
                    errors['outlier_iqr_multiplier'] = 'Must be between 0.5 and 3.0'
            except (ValueError, TypeError):
                errors['outlier_iqr_multiplier'] = 'Must be a valid number'
        
        if errors:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create user's settings
        settings, created = UserThresholdSettings.objects.get_or_create(
            user=request.user,
            defaults={
                'warning_percentile': warning_percentile or 0.75,
                'outlier_iqr_multiplier': iqr_multiplier or 1.5
            }
        )
        
        # Update if not created
        if not created:
            if warning_percentile is not None:
                settings.warning_percentile = warning_percentile
            if iqr_multiplier is not None:
                settings.outlier_iqr_multiplier = iqr_multiplier
            settings.save()
        
        return Response({
            'warning_percentile': settings.warning_percentile,
            'outlier_iqr_multiplier': settings.outlier_iqr_multiplier,
            'is_custom': True,
            'message': 'Settings saved successfully'
        }, status=status.HTTP_200_OK)
    
    def delete(self, request):
        """Reset to defaults by removing custom settings."""
        deleted, _ = UserThresholdSettings.objects.filter(user=request.user).delete()
        
        # Get the default settings to return
        warning_percentile, iqr_multiplier = get_threshold_settings()
        
        return Response({
            'warning_percentile': warning_percentile,
            'outlier_iqr_multiplier': iqr_multiplier,
            'is_custom': False,
            'message': 'Settings reset to defaults' if deleted else 'Already using defaults'
        }, status=status.HTTP_200_OK)

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

            # === ENHANCED ANALYTICS ===
            
            # 1. Basic Statistics with Min/Max/Std Dev
            numeric_cols = ['Flowrate', 'Pressure', 'Temperature']
            stats = {
                "total_count": int(len(df)),
                "avg_flowrate": float(df['Flowrate'].mean()),
                "avg_pressure": float(df['Pressure'].mean()),
                "avg_temperature": float(df['Temperature'].mean()),
                "min_flowrate": float(df['Flowrate'].min()),
                "max_flowrate": float(df['Flowrate'].max()),
                "std_flowrate": float(df['Flowrate'].std()),
                "min_pressure": float(df['Pressure'].min()),
                "max_pressure": float(df['Pressure'].max()),
                "std_pressure": float(df['Pressure'].std()),
                "min_temperature": float(df['Temperature'].min()),
                "max_temperature": float(df['Temperature'].max()),
                "std_temperature": float(df['Temperature'].std()),
                "type_distribution": df['Type'].value_counts().to_dict()
            }
            
            # 2. Type-based Comparison
            type_comparison = {}
            for eq_type in df['Type'].unique():
                type_df = df[df['Type'] == eq_type]
                type_comparison[eq_type] = {
                    "count": int(len(type_df)),
                    "avg_flowrate": float(type_df['Flowrate'].mean()),
                    "avg_pressure": float(type_df['Pressure'].mean()),
                    "avg_temperature": float(type_df['Temperature'].mean())
                }
            stats['type_comparison'] = type_comparison
            
            # 3. Correlation Matrix
            correlation_matrix = df[numeric_cols].corr().to_dict()
            stats['correlation_matrix'] = correlation_matrix
            
            # 4. Outlier Detection (using IQR method)
            # Get configurable thresholds - user's custom or defaults
            warning_percentile, iqr_multiplier = get_threshold_settings(request.user)
            
            outliers = []
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - iqr_multiplier * IQR  # Configurable
                upper_bound = Q3 + iqr_multiplier * IQR  # Configurable
                
                outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
                for idx in df[outlier_mask].index:
                    equipment_name = df.loc[idx, 'Equipment Name']
                    if equipment_name not in [o['equipment'] for o in outliers]:
                        outliers.append({
                            'equipment': equipment_name,
                            'parameters': []
                        })
                    
                    outlier_entry = next(o for o in outliers if o['equipment'] == equipment_name)
                    outlier_entry['parameters'].append({
                        'parameter': col,
                        'value': float(df.loc[idx, col]),
                        'lower_bound': float(lower_bound),
                        'upper_bound': float(upper_bound)
                    })
            
            stats['outliers'] = outliers
            
            # 5. Health Status for each equipment
            data_json = df.to_dict(orient='records')
            for i, row in enumerate(data_json):
                equipment_name = row['Equipment Name']
                
                # Check if equipment has outliers
                is_outlier = any(o['equipment'] == equipment_name for o in outliers)
                
                # Simple health status based on parameter ranges
                # Critical: Any parameter is an outlier
                # Warning: Parameters above warning_percentile (configurable)
                # Normal: Everything else
                if is_outlier:
                    health_status = 'critical'
                    health_color = '#ef4444'  # red
                elif (row['Flowrate'] > df['Flowrate'].quantile(warning_percentile) or 
                      row['Pressure'] > df['Pressure'].quantile(warning_percentile) or 
                      row['Temperature'] > df['Temperature'].quantile(warning_percentile)):
                    health_status = 'warning'
                    health_color = '#f59e0b'  # yellow
                else:
                    health_status = 'normal'
                    health_color = '#10b981'  # green
                
                data_json[i]['health_status'] = health_status
                data_json[i]['health_color'] = health_color

            # We also send back the raw data so the frontend can display the table.
            # .to_dict('records') gives us a nice list of JSON objects.

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

class UpdateAISummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            instance = UploadedFile.objects.get(pk=pk, user=request.user)
            summary_text = request.data.get('summary')
            if not summary_text:
                return Response({"error": "No summary provided"}, status=status.HTTP_400_BAD_REQUEST)
            
            instance.ai_summary_text = summary_text
            instance.save()
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        except UploadedFile.DoesNotExist:
            return Response({"error": "Upload not found"}, status=status.HTTP_404_NOT_FOUND)

class PDFReportView(APIView):
    permission_classes = [IsAuthenticated]
    
    # Professional color scheme
    COLORS = {
        'primary': colors.HexColor('#1a1a2e'),      # Dark navy
        'secondary': colors.HexColor('#16213e'),    # Darker blue
        'accent': colors.HexColor('#0f3460'),       # Blue accent
        'highlight': colors.HexColor('#e94560'),    # Red highlight
        'success': colors.HexColor('#10b981'),      # Green
        'warning': colors.HexColor('#f59e0b'),      # Amber
        'danger': colors.HexColor('#ef4444'),       # Red
        'text': colors.HexColor('#333333'),         # Dark gray text
        'text_light': colors.HexColor('#666666'),   # Light gray text
        'header_bg': colors.HexColor('#1f2937'),    # Header background
        'table_header': colors.HexColor('#374151'), # Table header
        'table_alt': colors.HexColor('#f3f4f6'),    # Alternating row
    }
    
    def draw_header(self, p, width, height, title="Chemical Equipment Analysis Report"):
        """Draw a professional header bar on the page."""
        # Header background
        p.setFillColor(self.COLORS['header_bg'])
        p.rect(0, height - 80, width, 80, fill=True, stroke=False)
        
        # Header title
        p.setFillColor(colors.white)
        p.setFont("Helvetica-Bold", 22)
        p.drawString(50, height - 50, title)
        
        # Accent line
        p.setStrokeColor(self.COLORS['highlight'])
        p.setLineWidth(3)
        p.line(50, height - 65, 250, height - 65)
        
        return height - 100  # Return new Y position
    
    def draw_footer(self, p, width, page_num, total_pages=3):
        """Draw a professional footer."""
        p.setFillColor(self.COLORS['header_bg'])
        p.rect(0, 0, width, 40, fill=True, stroke=False)
        
        p.setFillColor(colors.white)
        p.setFont("Helvetica", 9)
        p.drawString(50, 15, "Chemical Equipment Visualizer")
        p.drawRightString(width - 50, 15, f"Page {page_num} of {total_pages}")
    
    # Fix 406 error by allowing any content type
    def get(self, request, pk, *args, **kwargs):
        try:
            # Ensure user can only access their own reports
            instance = UploadedFile.objects.get(pk=pk, user=request.user)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="equipment_report_{pk}.pdf"'

            # Create PDF with A4 page size
            p = canvas.Canvas(response, pagesize=A4)
            width, height = A4
            
            stats = instance.summary
            processed_data = instance.processed_data
            df = pd.DataFrame(processed_data)
            
            # --- PAGE 1: Summary ---
            current_y = self.draw_header(p, width, height)
            
            # Metadata box
            p.setFillColor(self.COLORS['table_alt'])
            p.roundRect(40, current_y - 80, width - 80, 70, 5, fill=True, stroke=False)
            
            p.setFillColor(self.COLORS['text'])
            p.setFont("Helvetica", 10)
            
            # Use local timezone for both timestamps
            import pytz
            from datetime import datetime as dt
            
            local_tz = pytz.timezone('Asia/Kolkata')
            generated_at = dt.now(local_tz)
            uploaded_at_local = instance.uploaded_at.astimezone(local_tz)
            
            p.drawString(50, current_y - 25, f"Report ID: #{pk}")
            p.drawString(250, current_y - 25, f"User: {request.user.username}")
            p.drawString(50, current_y - 45, f"Generated: {generated_at.strftime('%d %b %Y, %H:%M:%S IST')}")
            p.drawString(50, current_y - 65, f"Data Uploaded: {uploaded_at_local.strftime('%d %b %Y, %H:%M:%S IST')}")
            
            current_y -= 100
            
            # Summary Statistics Header with styled background
            p.setFillColor(self.COLORS['accent'])
            p.roundRect(40, current_y - 25, 200, 25, 3, fill=True, stroke=False)
            p.setFillColor(colors.white)
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, current_y - 18, "📊 Summary Statistics")
            current_y -= 40
            
            # Summary Table Data with better styling
            summary_data = [
                ["Metric", "Value", "Metric", "Value"],
                ["Total Equipment", str(stats.get('total_count', 0)), "Avg Flowrate", f"{stats.get('avg_flowrate', 0):.2f}"],
                ["Avg Pressure", f"{stats.get('avg_pressure', 0):.2f}", "Avg Temperature", f"{stats.get('avg_temperature', 0):.2f}"],
                ["Min Flowrate", f"{stats.get('min_flowrate', 0):.2f}", "Max Flowrate", f"{stats.get('max_flowrate', 0):.2f}"],
                ["Min Pressure", f"{stats.get('min_pressure', 0):.2f}", "Max Pressure", f"{stats.get('max_pressure', 0):.2f}"],
                ["Min Temperature", f"{stats.get('min_temperature', 0):.2f}", "Max Temperature", f"{stats.get('max_temperature', 0):.2f}"],
            ]
            
            table = Table(summary_data, colWidths=[120, 80, 120, 80])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['table_header']),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('BACKGROUND', (0, 2), (-1, 2), self.COLORS['table_alt']),
                ('BACKGROUND', (0, 4), (-1, 4), self.COLORS['table_alt']),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                ('ROUNDEDCORNERS', [5, 5, 5, 5]),
            ]))
            
            w, h = table.wrap(width - 100, height)
            table.drawOn(p, 50, current_y - h)
            current_y -= (h + 30)
            
            # --- AI Insights Section ---
            ai_text = getattr(instance, 'ai_summary_text', None)
            if ai_text:
                # Header
                p.setFillColor(self.COLORS['accent'])
                p.roundRect(40, current_y - 25, 200, 25, 3, fill=True, stroke=False)
                p.setFillColor(colors.white)
                p.setFont("Helvetica-Bold", 12)
                p.drawString(50, current_y - 18, "🤖 AI Analysis & Insights")
                current_y -= 40
                
                # Import styles
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.platypus import Paragraph, Table as PlatyTable, TableStyle as PlatyTableStyle
                from reportlab.lib.enums import TA_LEFT
                
                styles = getSampleStyleSheet()
                normal_style = styles['Normal']
                normal_style.fontName = 'Helvetica'
                normal_style.fontSize = 10
                normal_style.leading = 14
                
                # Custom styles/tags
                # We will parse the text manually into blocks: Paragraphs vs Tables
                import re
                
                # Improved Markdown Parsing
                import re
                
                # Split by double newlines to get paragraphs
                raw_paragraphs = re.split(r'\n\s*\n', ai_text)
                
                for raw_p in raw_paragraphs:
                    raw_p = raw_p.strip()
                    if not raw_p: continue
                    
                    # Detect Table syntax (simple check)
                    if '|' in raw_p and '-|-' in raw_p:
                        # Process as table
                        lines = raw_p.split('\n')
                        rows = []
                        for line in lines:
                             if not line.strip(): continue
                             cells = [c.strip() for c in line.strip('|').split('|')]
                             rows.append(cells)
                        
                        # Filter separator
                        rows = [r for r in rows if not all(all(c in '-:' for c in text) for text in r)]
                        
                        if len(rows) > 0:
                            num_cols = len(rows[0])
                            col_width = (width - 100) / num_cols
                            t = PlatyTable(rows, colWidths=[col_width] * num_cols)
                            
                            ts = [
                                ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['header_bg']),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                                ('fontName', (0, 0), (-1, 0), "Helvetica-Bold"),
                                ('fontSize', (0, 0), (-1, -1), 9),
                                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('PADDING', (0, 0), (-1, -1), 6),
                            ]
                            # Zebra
                            for r_idx in range(1, len(rows)):
                                if r_idx % 2 == 0:
                                    ts.append(('BACKGROUND', (0, r_idx), (-1, r_idx), self.COLORS['table_alt']))
                                    
                            t.setStyle(PlatyTableStyle(ts))
                            w, h = t.wrap(width - 100, height)
                            
                            if current_y - h < 50:
                                self.draw_footer(p, width, 1)
                                p.showPage()
                                current_y = self.draw_header(p, width, height, "AI Analysis (continued)")
                                
                            t.drawOn(p, 50, current_y - h)
                            current_y -= (h + 15)
                        
                    else:
                        # Process as Text Paragraph
                        text = raw_p
                        
                        # Headers (Markdown ### or just Title Case lines)
                        if text.startswith('###'):
                             text = f'<font size="12" color="#1a1a2e"><b>{text.replace("###", "").strip()}</b></font>'
                             space_after = 6
                        elif text.startswith('##'):
                             text = f'<font size="14" color="#0f3460"><b>{text.replace("##", "").strip()}</b></font>'
                             space_after = 10
                        else:
                             # Bold
                             text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
                             # Bullets (replace * or - at start of lines)
                             text = re.sub(r'(?m)^[\*\-■] ', r'&bull; ', text)
                             # Normalize newlines within paragraph to spaces (reflow)
                             # But keep manual breaks if needed? simpler to just replace single \n with space
                             if not text.startswith('<font'):
                                text = text.replace('\n', ' ')
                             space_after = 10
                        
                        para = Paragraph(text, normal_style)
                        w, h = para.wrap(width - 100, height)
                        
                        if current_y - h < 50:
                            self.draw_footer(p, width, 1)
                            p.showPage()
                            current_y = self.draw_header(p, width, height, "AI Analysis (continued)")
                        
                        para.drawOn(p, 50, current_y - h)
                        current_y -= (h + space_after)

            # Type Distribution with styled header
            p.setFillColor(self.COLORS['accent'])
            p.roundRect(40, current_y - 25, 220, 25, 3, fill=True, stroke=False)
            p.setFillColor(colors.white)
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, current_y - 18, "🔧 Equipment Type Distribution")
            current_y -= 40
            
            type_dist = stats.get('type_distribution', {})
            p.setFont("Helvetica", 10)
            p.setFillColor(self.COLORS['text'])
            
            for k, v in type_dist.items():
                if current_y < 80:
                    self.draw_footer(p, width, 1)
                    p.showPage()
                    current_y = self.draw_header(p, width, height, "Summary (continued)")
                    p.setFont("Helvetica", 10)
                    p.setFillColor(self.COLORS['text'])
                    
                p.drawString(70, current_y, f"• {k}: {v} units")
                current_y -= 18
            
            # Outlier Alert with styled TABLE (No artifacts)
            outliers = stats.get('outliers', [])
            if outliers and len(outliers) > 0:
                current_y -= 25
                if current_y < 80:
                    self.draw_footer(p, width, 1)
                    p.showPage()
                    current_y = self.draw_header(p, width, height, "Summary (continued)")
                
                # Header for alert
                p.setFillColor(self.COLORS['danger'])
                p.setFont("Helvetica-Bold", 14)
                p.drawString(50, current_y, f"⚠️ ALERT: {len(outliers)} Critical Anomalies Detected")
                current_y -= 20
                
                # Create Table data for outliers
                # Columns: Equipment, Parameter, Value, Limit (Lower/Upper)
                alert_data = [["Equipment", "Parameter", "Value", "Limit", "Status"]]
                
                for out in outliers:
                    eq_name = out['equipment']
                    for param in out.get('parameters', []):
                        val = param['value']
                        l_bound = param['lower_bound']
                        u_bound = param['upper_bound']
                        p_name = param['parameter']
                        
                        limit_str = f"{l_bound:.2f} - {u_bound:.2f}"
                        status_str = "High" if val > u_bound else "Low"
                        
                        alert_data.append([
                            eq_name, 
                            p_name, 
                            f"{val:.2f}",
                            limit_str,
                            status_str.upper()
                        ])
                
                # ALERT Table
                t_alert = PlatyTable(alert_data, colWidths=[120, 100, 80, 120, 80])
                t_style = [
                    ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['danger']),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 0.5, self.COLORS['danger']),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fef2f2')),
                    ('TEXTCOLOR', (0, 1), (-1, -1), self.COLORS['danger']),
                ]
                t_alert.setStyle(PlatyTableStyle(t_style))
                
                w, h = t_alert.wrap(width - 100, height)
                t_alert.drawOn(p, 50, current_y - h)
                current_y -= (h + 20)

            self.draw_footer(p, width, 1)
            p.showPage()
            
            # --- PAGE 2: Charts ---
            current_y = self.draw_header(p, width, height, "Visualization Charts")
            
            # Generate charts
            fig = None
            try:
                chart_buffer = BytesIO()
                fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 14))
                fig.patch.set_facecolor('white')
                
                # Chart 1: Type Distribution (Pie)
                if type_dist and len(type_dist) > 0:
                    ax1.pie(type_dist.values(), labels=type_dist.keys(), autopct='%1.1f%%', startangle=90)
                    ax1.set_title('Equipment Type Distribution', fontweight='bold')
                else:
                    ax1.text(0.5, 0.5, 'No Type Data', ha='center', va='center', transform=ax1.transAxes)
                    ax1.axis('off')
                
                # Chart 2: Parameter Averages (Bar)
                params = ['Flowrate', 'Pressure', 'Temperature']
                avg_vals = [stats['avg_flowrate'], stats['avg_pressure'], stats['avg_temperature']]
                bars = ax2.bar(params, avg_vals, color=['#58a6ff', '#2ea043', '#f85149'])
                ax2.set_title('Average Parameters', fontweight='bold')
                ax2.set_ylabel('Value')
                ax2.grid(axis='y', alpha=0.3)
                
                # Chart 3: Type Comparison
                if stats.get('type_comparison') and len(stats['type_comparison']) > 0:
                    types = list(stats['type_comparison'].keys())
                    flow_avgs = [stats['type_comparison'][t]['avg_flowrate'] for t in types]
                    press_avgs = [stats['type_comparison'][t]['avg_pressure'] for t in types]
                    
                    x = np.arange(len(types))
                    width_bar = 0.35
                    ax3.bar(x - width_bar/2, flow_avgs, width_bar, label='Flowrate', color='#58a6ff')
                    ax3.bar(x + width_bar/2, press_avgs, width_bar, label='Pressure', color='#ee82ee')
                    ax3.set_title('Parameter by Type', fontweight='bold')
                    ax3.set_xticks(x)
                    ax3.set_xticklabels(types, rotation=45, ha='right')
                    ax3.legend()
                    ax3.grid(axis='y', alpha=0.3)
                else:
                    ax3.text(0.5, 0.5, 'No Type Comparison', ha='center', va='center', transform=ax3.transAxes)
                    ax3.axis('off')
                
                # Chart 4: Health Status Distribution
                if processed_data and len(processed_data) > 0:
                    health_counts = {'normal': 0, 'warning': 0, 'critical': 0}
                    for row in processed_data:
                        status_val = row.get('health_status', 'normal')
                        health_counts[status_val] += 1
                    
                    filtered_counts = {k: v for k, v in health_counts.items() if v > 0}
                    if filtered_counts:
                        colors_map = {'normal': '#10b981', 'warning': '#f59e0b', 'critical': '#ef4444'}
                        labels = [f"{k.capitalize()}\n({v})" for k, v in filtered_counts.items()]
                        values = list(filtered_counts.values())
                        chart_colors = [colors_map[k] for k in filtered_counts.keys()]
                        ax4.pie(values, labels=labels, colors=chart_colors, autopct='%1.1f%%')
                        ax4.set_title('Health Status Distribution', fontweight='bold')
                    else:
                        ax4.text(0.5, 0.5, 'No Health Data', ha='center', va='center', transform=ax4.transAxes)
                        ax4.axis('off')
                else:
                    ax4.text(0.5, 0.5, 'No Data', ha='center', va='center', transform=ax4.transAxes)
                    ax4.axis('off')

                plt.tight_layout(pad=3.0)
                plt.savefig(chart_buffer, format='png', dpi=300, bbox_inches='tight', facecolor='white')
                
                chart_buffer.seek(0)
                img = ImageReader(chart_buffer)
                
                # Draw image with proper sizing
                img_height = 650
                p.drawImage(img, 10, current_y - img_height, width=width-20, height=img_height, preserveAspectRatio=True)
                
            except Exception as chart_error:
                p.setFont("Helvetica", 10)
                p.drawString(50, current_y - 50, f"Chart generation error: {str(chart_error)}")
            finally:
                if fig:
                    plt.close(fig)

            self.draw_footer(p, width, 2)
            p.showPage()
            
            # --- PAGE 3: Data Table ---
            current_y = self.draw_header(p, width, height, "Equipment Data Table")
            
            # Prepare table data
            table_data = [list(df.columns[:5])]
            for idx, row in df.head(25).iterrows():
                table_data.append([str(row[col]) for col in df.columns[:5]])
            
            data_table = Table(table_data, colWidths=[100, 80, 80, 80, 80])
            data_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['table_header']),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                # Alternating row colors
                *[('BACKGROUND', (0, i), (-1, i), self.COLORS['table_alt']) for i in range(2, len(table_data), 2)],
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ]))
            
            # Dynamic height calculation for the Data Table
            w, h = data_table.wrap(width, height)
            data_table.drawOn(p, 50, current_y - h)
            
            if len(df) > 25:
                p.setFillColor(self.COLORS['text_light'])
                p.setFont("Helvetica-Italic", 9)
                p.drawString(50, current_y - h - 15, f"Showing first 25 of {len(df)} equipment items")
            
            self.draw_footer(p, width, 3)
            p.showPage()
            p.save()
            return response
            
        except UploadedFile.DoesNotExist:
            return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Failed to generate report: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
