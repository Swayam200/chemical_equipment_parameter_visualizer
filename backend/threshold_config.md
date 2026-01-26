# Health Status Threshold Configuration Guide

## Overview

This document explains the health status classification system, the specific threshold values used, and how administrators can make these values configurable.

## Current Implementation

### Health Status Categories

The system classifies equipment into three health statuses:

| Status   | Display | Color  | Hex Code  | User Action                  |
| -------- | ------- | ------ | --------- | ---------------------------- |
| Normal   | ✓       | Green  | `#10b981` | No action needed             |
| Warning  | ⚠       | Yellow | `#f59e0b` | Monitor equipment            |
| Critical | ✗       | Red    | `#ef4444` | Immediate attention required |

### Classification Algorithm

**Location:** `backend/api/views.py` (lines 195-208)

```python
# Step 1: Check for outliers
if is_outlier:
    health_status = 'critical'
    health_color = '#ef4444'

# Step 2: Check for warning conditions
elif (row['Flowrate'] > df['Flowrate'].quantile(0.75) or
      row['Pressure'] > df['Pressure'].quantile(0.75) or
      row['Temperature'] > df['Temperature'].quantile(0.75)):
    health_status = 'warning'
    health_color = '#f59e0b'

# Step 3: Default to normal
else:
    health_status = 'normal'
    health_color = '#10b981'
```

## Threshold Values Explained

### 1. Critical Threshold: IQR Outlier Detection

**Current Value:** `1.5 × IQR`

**Location:** `backend/api/views.py` (lines 159-164)

**Algorithm:**

```
Q1 = 25th percentile (first quartile)
Q3 = 75th percentile (third quartile)
IQR = Q3 - Q1 (interquartile range)

Lower Bound = Q1 - (1.5 × IQR)
Upper Bound = Q3 + (1.5 × IQR)

IF value < Lower Bound OR value > Upper Bound:
    → Equipment is CRITICAL
```

**Statistical Basis:**

- **1.5 × IQR** is the standard Tukey method for outlier detection
- Used by box plots, statistical software (R, Python, SPSS)
- Approximately captures values beyond 2.7 standard deviations from mean (assuming normal distribution)

**Why 1.5?**

- **Balance:** Not too strict (wouldn't catch 1.0) or too lenient (wouldn't catch 3.0)
- **Industry Standard:** Established statistical practice since 1970s
- **Proven:** Works well across various data distributions

**Adjustable Range:**
| Multiplier | Sensitivity | Use Case |
|------------|-------------|----------|
| 1.0 | Very Strict | High-precision equipment, safety-critical systems |
| 1.5 | Standard | General purpose, balanced detection |
| 2.0 | Moderate | Less critical systems, reduce false alarms |
| 3.0 | Lenient | Exploratory analysis, very tolerant |

### 2. Warning Threshold: 75th Percentile

**Current Value:** `0.75` (75th percentile)

**Location:** `backend/api/views.py` (line 197)

**Meaning:**

- Equipment parameter is higher than **75% of all equipment** in the dataset
- Equipment is in the **top 25%** (upper quartile)
- Relative threshold (calculated per dataset, not absolute)

**Why 75th Percentile?**

- **Early Warning:** Catches potential issues before they become critical
- **Statistical Standard:** Upper quartile is a recognized threshold in quality control
- **Action Trigger:** Top 25% equipment should be monitored more closely

**Interpretation Example:**

If 100 equipment have Flowrate values:

- Normal: Equipment with Flowrate ≤ 75th highest value (75 equipment)
- Warning: Equipment with Flowrate > 75th highest value (25 equipment)
- Critical: Equipment with Flowrate outside IQR bounds (typically 5-10 equipment)

**Adjustable Range:**
| Percentile | Sensitivity | Equipment Flagged | Use Case |
|------------|-------------|-------------------|----------|
| 0.70 (70th) | Strict | Top 30% | Aggressive monitoring |
| 0.75 (75th) | **Standard** | Top 25% | **Recommended** |
| 0.80 (80th) | Moderate | Top 20% | Reduce warnings |
| 0.85 (85th) | Lenient | Top 15% | Focus on extremes only |
| 0.90 (90th) | Very Lenient | Top 10% | Minimal warnings |

## Making Thresholds Admin-Configurable

### Feasibility Analysis

**Overall Feasibility: HIGH** ✅

**Technical Complexity:** Low to Medium (depending on approach)

**Benefits:**

1. **Flexibility:** Adapt thresholds to specific industry needs
2. **No Code Changes:** Adjust without redeployment
3. **Experimentation:** Test different sensitivities easily
4. **Documentation:** Settings documented in admin panel
5. **Auditability:** Track who changed thresholds when

### Implementation Options

#### Option 1: Django Admin Model ⭐ RECOMMENDED

**Effort:** 2-3 hours  
**Difficulty:** Low  
**Maintenance:** Low

**Implementation:**

1. **Create Model** (`backend/api/models.py`):

```python
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class AnalyticsSettings(models.Model):
    # Warning threshold (75th percentile by default)
    warning_percentile = models.FloatField(
        default=0.75,
        validators=[
            MinValueValidator(0.5, message="Percentile must be at least 50%"),
            MaxValueValidator(0.95, message="Percentile must be at most 95%")
        ],
        help_text="Percentile threshold for warning status (0.5 to 0.95). Default: 0.75 (75th percentile)"
    )

    # Critical threshold (1.5 × IQR by default)
    outlier_iqr_multiplier = models.FloatField(
        default=1.5,
        validators=[
            MinValueValidator(0.5, message="Multiplier must be at least 0.5"),
            MaxValueValidator(3.0, message="Multiplier must be at most 3.0")
        ],
        help_text="IQR multiplier for outlier detection (0.5 to 3.0). Default: 1.5 (standard)"
    )

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='settings_updates'
    )

    class Meta:
        verbose_name = "Analytics Setting"
        verbose_name_plural = "Analytics Settings"

    def __str__(self):
        return f"Warning: {self.warning_percentile*100}% | IQR: {self.outlier_iqr_multiplier}x"
```

2. **Register in Admin** (`backend/api/admin.py`):

```python
from django.contrib import admin
from .models import AnalyticsSettings

@admin.register(AnalyticsSettings)
class AnalyticsSettingsAdmin(admin.ModelAdmin):
    list_display = ['warning_percentile', 'outlier_iqr_multiplier', 'updated_at', 'updated_by']
    readonly_fields = ['updated_at', 'updated_by']

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
```

3. **Update Views** (`backend/api/views.py`):

```python
from .models import AnalyticsSettings

class FileUploadView(APIView):
    def post(self, request, *args, **kwargs):
        # ... existing code ...

        # Get thresholds from database
        settings = AnalyticsSettings.objects.first()
        warning_percentile = settings.warning_percentile if settings else 0.75
        iqr_multiplier = settings.outlier_iqr_multiplier if settings else 1.5

        # Use in outlier detection
        lower_bound = Q1 - iqr_multiplier * IQR  # Instead of 1.5 * IQR
        upper_bound = Q3 + iqr_multiplier * IQR

        # Use in warning check
        if (row['Flowrate'] > df['Flowrate'].quantile(warning_percentile) or ...):
            health_status = 'warning'
```

4. **Create Migration:**

```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create Initial Settings:**

```bash
python manage.py shell
>>> from api.models import AnalyticsSettings
>>> AnalyticsSettings.objects.create()
>>> exit()
```

**Pros:**

- ✅ Uses existing Django admin interface
- ✅ Validation built-in
- ✅ Version history tracking possible
- ✅ User-friendly for admins
- ✅ No new UI needed
- ✅ Can implement in one sprint

**Cons:**

- ⚠️ Changes may require server restart (unless cached)
- ⚠️ Only accessible to Django admin users
- ⚠️ Not real-time (query on each upload)

---

#### Option 2: Environment Variables

**Effort:** 30 minutes  
**Difficulty:** Very Low  
**Maintenance:** Low

**Implementation:**

1. **Add to `.env`:**

```env
WARNING_PERCENTILE=0.75
OUTLIER_IQR_MULTIPLIER=1.5
```

2. **Update Views:**

```python
import os

warning_percentile = float(os.getenv('WARNING_PERCENTILE', '0.75'))
iqr_multiplier = float(os.getenv('OUTLIER_IQR_MULTIPLIER', '1.5'))
```

**Pros:**

- ✅ Fastest to implement
- ✅ No database changes needed
- ✅ Good for Docker/container deployments
- ✅ DevOps-friendly

**Cons:**

- ⚠️ Requires server restart to apply
- ⚠️ No validation (can input invalid values)
- ⚠️ Not user-friendly for non-technical admins
- ⚠️ No audit trail

---

#### Option 3: REST API + Admin Dashboard UI

**Effort:** 1-2 days  
**Difficulty:** High  
**Maintenance:** Medium

**Implementation:**

1. **Backend API:**

```python
# serializers.py
class AnalyticsSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsSettings
        fields = ['warning_percentile', 'outlier_iqr_multiplier', 'updated_at']

# views.py
from rest_framework.permissions import IsAdminUser

class SettingsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        settings = AnalyticsSettings.objects.first()
        serializer = AnalyticsSettingsSerializer(settings)
        return Response(serializer.data)

    def put(self, request):
        settings = AnalyticsSettings.objects.first()
        serializer = AnalyticsSettingsSerializer(settings, data=request.data)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
```

2. **Frontend Admin Page** (React):

```jsx
function AdminSettings() {
  const [warningPercentile, setWarningPercentile] = useState(0.75);
  const [iqrMultiplier, setIqrMultiplier] = useState(1.5);

  return (
    <div>
      <h2>Analytics Thresholds</h2>

      <label>
        Warning Percentile: {warningPercentile * 100}%
        <input
          type="range"
          min="0.5"
          max="0.95"
          step="0.05"
          value={warningPercentile}
          onChange={(e) => setWarningPercentile(e.target.value)}
        />
      </label>

      <label>
        IQR Multiplier: {iqrMultiplier}x
        <input
          type="range"
          min="0.5"
          max="3.0"
          step="0.1"
          value={iqrMultiplier}
          onChange={(e) => setIqrMultiplier(e.target.value)}
        />
      </label>

      <button onClick={handleSave}>Save Settings</button>
    </div>
  );
}
```

3. **Desktop Integration:**

```python
# Add settings dialog in main.py
class SettingsDialog(QDialog):
    def __init__(self, auth_header):
        # ... slider for warning percentile
        # ... slider for IQR multiplier
        # ... save button
```

**Pros:**

- ✅ Best user experience
- ✅ Real-time updates (with caching)
- ✅ Visual feedback
- ✅ Preview impact before applying
- ✅ Accessible from both web and desktop
- ✅ Validation and error messages

**Cons:**

- ⚠️ Significant development time
- ⚠️ Requires authentication/authorization
- ⚠️ More testing needed
- ⚠️ Cache invalidation complexity

---

### Recommended Implementation Path

**Phase 1: MVP (Current Sprint)**

- Implement **Option 2** (Environment Variables)
- Quick win for testing different thresholds
- Good enough for demo/screening task

**Phase 2: Production Ready (Next Sprint)**

- Implement **Option 1** (Django Admin Model)
- Professional admin interface
- Proper validation and audit trail
- Documented in admin panel

**Phase 3: Enhanced UX (Future)**

- Implement **Option 3** (REST API + Dashboard)
- Full-featured admin UI
- Real-time updates
- Role-based access control

## Testing Threshold Changes

### Test Scenarios

**Scenario 1: More Strict Warning (70th percentile)**

```python
warning_percentile = 0.70  # Instead of 0.75
```

**Expected:** 30% of equipment flagged as Warning (instead of 25%)

**Scenario 2: More Lenient Critical (2.0 × IQR)**

```python
iqr_multiplier = 2.0  # Instead of 1.5
```

**Expected:** Fewer equipment flagged as Critical (only extreme outliers)

**Scenario 3: Combination**

```python
warning_percentile = 0.80  # More lenient warnings
iqr_multiplier = 1.0       # More strict critical
```

**Expected:** Fewer warnings, more critical alerts

### Validation Rules

**Warning Percentile:**

- **Minimum:** 0.5 (50th percentile / median)
- **Maximum:** 0.95 (95th percentile)
- **Recommended:** 0.70 - 0.85

**IQR Multiplier:**

- **Minimum:** 0.5 (very strict)
- **Maximum:** 3.0 (very lenient)
- **Recommended:** 1.0 - 2.0

**Invalid Configurations:**

- Warning percentile > 0.95 (would flag too few)
- IQR multiplier < 0.5 (would flag too many)
- Warning percentile < 0.5 (would flag over 50% of equipment)

## Documentation for Admins

### Admin User Guide

**Accessing Settings (Option 1 - Django Admin):**

1. Visit: http://127.0.0.1:8000/admin/
2. Login with admin credentials
3. Navigate to "Analytics Settings"
4. Click on the existing settings record (only one allowed)
5. Adjust sliders or input values
6. Click "Save"
7. Restart backend server (or wait for cache invalidation)

**Understanding Impact:**

| Setting Change              | Result                               |
| --------------------------- | ------------------------------------ |
| Increase Warning Percentile | Fewer warnings (more lenient)        |
| Decrease Warning Percentile | More warnings (more strict)          |
| Increase IQR Multiplier     | Fewer critical alerts (more lenient) |
| Decrease IQR Multiplier     | More critical alerts (more strict)   |

**Best Practices:**

- Test threshold changes with sample data first
- Document why you changed thresholds
- Monitor false positive/negative rates
- Adjust gradually (don't jump from 0.75 to 0.90)
- Consider industry standards for your domain

## Conclusion

The current implementation uses **scientifically validated thresholds** (75th percentile for warnings, 1.5 × IQR for critical).

Making these thresholds **admin-configurable is highly feasible** with three viable options:

1. **Environment Variables** (quick MVP)
2. **Django Admin Model** (production-ready)
3. **REST API + Dashboard** (best UX)

**Recommendation:** Start with Option 1 for immediate testing, then implement Option 1 (Django Admin) for long-term use.

---

**Author:** Development Team  
**Last Updated:** January 2026  
**Version:** 1.0
