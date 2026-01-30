# Desktop Frontend - Chemical Equipment Parameter Visualizer

PyQt5-based desktop application for analyzing and visualizing chemical equipment data with advanced analytics.

## Technology Stack

- **PyQt5**: Desktop GUI framework
- **Matplotlib**: Data visualization library with interactive toolbar
- **Requests**: HTTP client for API communication
- **NumPy**: Numerical computations for visualizations

## Quick Start

**1. Ensure backend is running:**

```bash
cd ../backend
source venv/bin/activate
python manage.py runserver
```

**2. Launch desktop app:**

```bash
cd desktop-frontend
pip install -r requirements.txt
python main.py
```

---

## Features Overview

### 1. Login/Register Dialog

- Toggle between Login and Register modes
- Email field (register only)
- Password confirmation (register only)
- Form validation before submission
- Industrial-themed dark UI

### 2. Main Window Layout

**Size:** 1200x800px (default)

**Structure:**

- **Left Sidebar (250px)**: Upload history with user-scoped numbering
- **Main Content Area**: Dashboard and data table tabs
- **Auto-refresh**: History updates every 30 seconds

### 3. File Upload

- Click "Upload CSV" button
- **File size validation** (5 MB maximum)
- Displays file size during upload (e.g., "Uploading (245.3 KB)...")
- **User-friendly error messages** for failures
- Status updates: ✓ Upload Successful / ✗ Error

### 4. Dashboard Tab

#### Statistics Cards (Top Row)

- **Total Equipment Count**
- **Average Flowrate** with Min/Max
- **Average Pressure** with Min/Max
- **Average Temperature** with Min/Max

#### Outlier Alert Banner

- Red warning banner when outliers detected
- Lists equipment with outlier parameters
- Shows parameter values and acceptable bounds

#### Main Charts with Interactive Toolbar

Charts include a **navigation toolbar** for:

| Button | Name | How to Use |
|--------|------|------------|
| 🏠 | **Home** | Reset to original view |
| ⬅️ | **Back** | Previous zoom state |
| ➡️ | **Forward** | Next zoom state |
| ✚ | **Pan** | Click, then drag on chart |
| 🔍 | **Zoom** | Click, then draw rectangle to zoom |
| ⚙️ | **Configure** | Adjust subplot parameters |
| 💾 | **Save** | Export chart as image (PNG, PDF, SVG) |

**Available Charts:**

1. **Equipment Type Distribution** (Pie Chart)
2. **Average Parameters** (Bar Chart)

#### Advanced Analytics Section (Collapsible)

Click "🔬 Advanced Analytics" to expand:

1. **Type Comparison** - Grouped bar chart by equipment type
2. **Correlation Matrix** - Heatmap showing parameter relationships
3. **Standard Deviation** - Variability in each parameter
4. **Health Status Distribution** - Pie chart of Normal/Warning/Critical

### 5. Raw Data Tab

- Color-coded rows by health status
- Health status icons (✓ / ⚠ / ✗)
- All CSV columns displayed
- Sortable columns

---

## User Guide

### Uploading Files

1. Click **"Upload CSV"** button (green, top-left)
2. Select a CSV file (maximum **5 MB**)
3. Wait for upload confirmation
4. Dashboard updates automatically

**Required CSV columns:**
- Equipment Name (string)
- Type (string)
- Flowrate (float)
- Pressure (float)
- Temperature (float)

### Using Chart Zoom/Pan

1. **Zoom to area**: Click 🔍 button, then drag a rectangle on chart
2. **Pan**: Click ✚ button, then drag to move around
3. **Reset**: Click 🏠 button to restore original view
4. **Save**: Click 💾 to export chart as image

### Viewing Upload History

- History shows **last 5 uploads** per user
- Click any item to load that dataset
- Numbers are **user-scoped** (Upload 1, 2, 3...)
- Auto-refreshes every 30 seconds

### Downloading PDF Reports

1. Select a dataset (upload new or click history item)
2. Click **"Download PDF Report"** button
3. Choose save location
4. Report includes all charts and data

---

## Health Status Classification

| Status | Icon | Color | Criteria |
|--------|------|-------|----------|
| **Normal** | ✓ | Green (#10b981) | All parameters below 75th percentile |
| **Warning** | ⚠ | Yellow (#f59e0b) | Any parameter above 75th percentile |
| **Critical** | ✗ | Red (#ef4444) | Any parameter is a statistical outlier |

### Algorithm Details

**Outlier Detection (IQR Method):**
```
Q1 = 25th percentile
Q3 = 75th percentile
IQR = Q3 - Q1
Lower Bound = Q1 - 1.5 × IQR
Upper Bound = Q3 + 1.5 × IQR

Outlier = value < Lower OR value > Upper
```

**Warning Threshold:**
- Equipment with any parameter above the 75th percentile
- Relative to the dataset (not absolute values)

---

## Error Handling

### Upload Errors

| Error | Solution |
|-------|----------|
| "File Too Large" | Use file under 5 MB |
| "Could not connect to server" | Check backend is running |
| "Upload Failed" | Verify CSV format and columns |

### Connection Errors

- Ensure backend running at `http://127.0.0.1:8000`
- Check firewall settings
- Verify network connection

---

## Configuration

### API Settings

Backend URL is configured in `main.py`:
```python
API_URL = "http://127.0.0.1:8000/api/"
```

### Threshold Settings

Configured in backend `.env` file:
```env
WARNING_PERCENTILE=0.75
OUTLIER_IQR_MULTIPLIER=1.5
```

See [Backend README](../backend/README.md) for configuration details.

---

## Dependencies

```
PyQt5>=5.15
matplotlib>=3.5
requests>=2.28
numpy>=1.21
```

Install:
```bash
pip install -r requirements.txt
```

---

## Troubleshooting

### "Could not connect to server"

- Check backend running: http://127.0.0.1:8000
- No firewall blocking port 8000

### Charts not displaying

```bash
pip install --upgrade matplotlib numpy
```

### PyQt5 import error

**macOS:**
```bash
pip install --upgrade PyQt5
```

**Linux:**
```bash
sudo apt-get install python3-pyqt5
```

### Matplotlib display issues

**macOS:**
```bash
export MPLBACKEND=Qt5Agg
```

---

## Platform Notes

| Platform | Command | Notes |
|----------|---------|-------|
| **macOS** | `python3 main.py` | May need system Python |
| **Windows** | `python main.py` | Ensure Python in PATH |
| **Linux** | `python3 main.py` | May need apt packages |

---

## Future Enhancements

- [ ] Export charts as individual images
- [ ] Offline mode with local cache
- [ ] Multi-file comparison view
- [ ] Custom threshold settings dialog
- [ ] Equipment search/filter in table
- [ ] Customizable dashboard layout
