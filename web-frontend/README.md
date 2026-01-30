# Web Frontend - Chemical Equipment Parameter Visualizer

React-based web application for analyzing and visualizing chemical equipment data with advanced analytics.

## Technology Stack

- **React 18**: UI framework
- **Vite**: Build tool and dev server
- **Chart.js**: Data visualization library
- **chartjs-plugin-zoom**: Interactive chart zoom/pan functionality
- **Axios**: HTTP client for API communication
- **react-dropzone**: Drag & drop file upload

## Quick Start

```bash
npm install
npm run dev
```

Visit: http://localhost:5173/

---

## Features Overview

### 1. User Authentication

- Register new accounts with email validation
- Login with JWT token-based authentication
- **Automatic token refresh** when tokens expire (no manual re-login needed)
- Toggle between login/register modes with a single click

### 2. File Upload

- Drag & drop CSV files or click to browse
- **File size validation** (5MB maximum limit)
- **Real-time progress bar** during upload
- Displays file name and size during upload
- Automatic data processing and validation
- User-friendly error messages for validation failures

### 3. Dashboard Visualizations

#### Basic Statistics Cards

- **Total Equipment Count**: Number of equipment entries
- **Average Flowrate**: Mean value with min/max ranges
- **Average Pressure**: Mean value with min/max ranges
- **Average Temperature**: Mean value with min/max ranges

#### Interactive Charts

All charts support:
- **Scroll to zoom** in/out on data
- **Ctrl+drag to pan** across the chart
- **Reset Zoom button** to restore original view

##### Equipment Type Distribution (Pie Chart)
- Breakdown by equipment type with percentages
- Interactive tooltips on hover

##### Flowrate & Temperature Trends (Line Chart)
- Dual-axis visualization
- **Enhanced tooltips** showing:
  - Equipment name
  - Parameter values
  - Equipment type
  - Health status
- Zoom and pan enabled

### 4. Upload History

- Last 5 uploads displayed in sidebar
- Click to load any previous upload
- **User-scoped sequential numbering** (Upload #1, #2, #3...)
- Timestamps in local timezone

### 5. PDF Report Generation

- Download comprehensive PDF reports
- Professional styling with header/footer
- Includes all charts and data tables
- Color-coded health status indicators

---

## Advanced Analytics (Expandable Section)

### A. Outlier Detection

**Algorithm:** IQR (Interquartile Range) Method

```
Q1 = 25th percentile
Q3 = 75th percentile
IQR = Q3 - Q1
Lower Bound = Q1 - 1.5 × IQR
Upper Bound = Q3 + 1.5 × IQR

Outlier if: value < Lower Bound OR value > Upper Bound
```

**Display:**

- Red alert banner when outliers are detected
- Lists up to 5 equipment with outlier parameters
- Shows which parameters are outliers with actual values and bounds

### B. Type Comparison Chart

- Compare average parameters across equipment types
- Grouped bar chart with Flowrate, Pressure, Temperature
- Identify which types operate at higher/lower parameters

### C. Correlation Heatmap

- Pearson correlation coefficient (-1 to +1)
- Color coding: Red (positive), Blue (negative), Green (neutral)

### D. Health Status Indicators

| Status | Color | Criteria |
|--------|-------|----------|
| 🟢 **Normal** | Green | All parameters below 75th percentile, no outliers |
| 🟡 **Warning** | Yellow | Any parameter above 75th percentile |
| 🔴 **Critical** | Red | Any parameter is an outlier |

---

## User Guide

### Uploading Files

1. Click the upload area or drag a CSV file onto it
2. Maximum file size: **5 MB**
3. Required CSV columns:
   - Equipment Name
   - Type
   - Flowrate
   - Pressure
   - Temperature
4. Wait for the progress bar to complete
5. Dashboard updates automatically

### Using Chart Zoom/Pan

| Action | Result |
|--------|--------|
| **Scroll wheel** | Zoom in/out |
| **Ctrl + drag** | Pan the chart |
| **Click Reset Zoom** | Return to original view |

### Understanding Tooltips

Hover over any data point to see:
- Equipment name
- Parameter values (Flowrate, Temperature)
- Equipment type
- Current health status

### Downloading PDF Reports

1. Upload or select a dataset from history
2. Click the **"Download PDF Report"** button
3. Report includes:
   - Summary statistics
   - Type distribution chart
   - Complete data table
   - Outlier alerts

---

## Error Handling

### File Upload Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "File too large" | File exceeds 5 MB | Reduce file size or split data |
| "Invalid file type" | Not a CSV file | Use .csv extension |
| "Network error" | Connection issue | Check backend is running |

### Authentication Errors

- **Token expired**: Automatically refreshed (no action needed)
- **Invalid credentials**: Check username/password
- **Network error**: Verify backend server is running at http://127.0.0.1:8000

---

## Configuration

### Threshold Settings

Thresholds are configured in the backend `.env` file:

```env
WARNING_PERCENTILE=0.75          # 75th percentile for warnings
OUTLIER_IQR_MULTIPLIER=1.5       # IQR multiplier for critical
```

See [Backend README](../backend/README.md) for detailed configuration guide.

---

## API Integration

**Base URL:** `http://127.0.0.1:8000/api/`

**Authentication:** JWT tokens with automatic refresh

```javascript
// Tokens stored in localStorage
localStorage.getItem('access_token')
localStorage.getItem('refresh_token')
```

**Key Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/register/` | POST | Create account |
| `/api/login/` | POST | Get JWT tokens |
| `/api/token/refresh/` | POST | Refresh expired token |
| `/api/upload/` | POST | Upload CSV file |
| `/api/history/` | GET | Get last 5 uploads |
| `/api/report/<id>/` | GET | Download PDF report |

---

## Build for Production

```bash
npm run build
```

Output in `dist/` directory. Serve with any static file server.

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions

---

## Dependencies

```json
{
  "react": "^18.x",
  "vite": "^6.x",
  "chart.js": "^4.x",
  "chartjs-plugin-zoom": "^2.x",
  "axios": "^1.x",
  "react-dropzone": "^14.x",
  "react-icons": "^5.x"
}
```

Install all dependencies:
```bash
npm install
```
