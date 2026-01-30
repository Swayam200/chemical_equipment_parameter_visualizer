from rest_framework import serializers
from .models import UploadedFile
import pandas as pd
import os

# Import the helper function from views
def get_threshold_settings_for_serializer(user=None):
    """
    Get threshold settings with priority:
    1. User's custom settings (if exists in database)
    2. .env file settings
    3. Hardcoded defaults (0.75, 1.5)
    """
    if user:
        try:
            from .models import UserThresholdSettings
            settings = UserThresholdSettings.objects.get(user=user)
            return settings.warning_percentile, settings.outlier_iqr_multiplier
        except:
            pass  # Fall through to defaults
    
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

class UploadedFileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UploadedFile
        fields = ['id', 'user_upload_index', 'file', 'uploaded_at', 'summary', 'processed_data', 'username']
        read_only_fields = ['summary', 'processed_data', 'username', 'user_upload_index']
    
    def to_representation(self, instance):
        """
        Override to recalculate health status using current thresholds
        when old uploads are retrieved.
        """
        representation = super().to_representation(instance)
        
        # Get user from request context (if available) for per-user thresholds
        request = self.context.get('request')
        user = request.user if request and hasattr(request, 'user') else instance.user
        
        # Get current thresholds for this user
        warning_percentile, iqr_multiplier = get_threshold_settings_for_serializer(user)
        
        # Recalculate health status if file exists
        try:
            file_path = instance.file.path
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                numeric_cols = ['Flowrate', 'Pressure', 'Temperature']
                
                # Recalculate outliers with current thresholds
                outliers = []
                for col in numeric_cols:
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - iqr_multiplier * IQR
                    upper_bound = Q3 + iqr_multiplier * IQR
                    
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
                
                # Update outliers in summary
                representation['summary']['outliers'] = outliers
                
                # Recalculate health status for each equipment
                data_json = df.to_dict(orient='records')
                for i, row in enumerate(data_json):
                    equipment_name = row['Equipment Name']
                    is_outlier = any(o['equipment'] == equipment_name for o in outliers)
                    
                    if is_outlier:
                        health_status = 'critical'
                        health_color = '#ef4444'
                    elif (row['Flowrate'] > df['Flowrate'].quantile(warning_percentile) or 
                          row['Pressure'] > df['Pressure'].quantile(warning_percentile) or 
                          row['Temperature'] > df['Temperature'].quantile(warning_percentile)):
                        health_status = 'warning'
                        health_color = '#f59e0b'
                    else:
                        health_status = 'normal'
                        health_color = '#10b981'
                    
                    data_json[i]['health_status'] = health_status
                    data_json[i]['health_color'] = health_color
                
                # Update processed_data with new health status
                representation['processed_data'] = data_json
        
        except Exception:
            # If recalculation fails, return stored data (graceful fallback)
            pass
        
        return representation
