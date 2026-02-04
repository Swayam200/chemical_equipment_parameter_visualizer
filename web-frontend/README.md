# Carbon Sleuth - Web Portal

Modern React-based web interface for **Carbon Sleuth**. Features interactive dashboards, deep-dive analytics, and AI-powered equipment diagnostics.

## Technology Stack

- **React 18**: UI framework
- **Vite**: Build tool and dev server
- **Chart.js**: Data visualization library
- **Axios**: HTTP client for API communication
- **Tailwind CSS**: Utility-first styling

## Quick Start

```bash
npm install
npm run dev
```

Visit: http://localhost:5173/

---

## Configuration

### Environment Variables

Create a `.env` file in the `web-frontend` directory:

```env
# AI Integration (OpenRouter)
VITE_OPENROUTER_API_KEY=sk-or-v1-your-key-here...
VITE_AI_MODEL=google/gemini-2.0-flash-lite-preview-02-05:free
```

See `.env.example` for a template.

---

## Deployment (Vercel)

This application is optimized for deployment on Vercel.

### 1. Project Configuration

Ensure your `vite.config.js` and `vercel.json` (if present) are configured to handle client-side routing.

### 2. Environment Variables

When deploying to Vercel, you **MUST** add the environment variables in the Vercel Dashboard:

1. Go to **Settings > Environment Variables**.
2. Add `VITE_OPENROUTER_API_KEY`.
3. Add `VITE_AI_MODEL`.

### 3. API Proxying

In development, Vite proxies requests to `http://localhost:8000`.
In production, you must ensure your API requests point to your production backend.

**Option A (Vercel Rewrites):**
Add `vercel.json`:
```json
{
  "rewrites": [
    { "source": "/api/(.*)", "destination": "https://your-backend-url.com/api/$1" }
  ]
}
```

**Option B (Env Var):**
Update `api.js` to use `VITE_API_BASE_URL` and set it in Vercel.

---

## Features Overview

### 1. Dashboard
- **KPI Cards**: Total count, averages, health status
- **Charts**: Doughnut (Type Dist), Bar (Param Avgs)
- **AI Chat**: Natural language query interface

### 2. Advanced Analytics
- **Trends**: Line charts for Flowrate/Pressure/Temp
- **Correlation**: Heatmap of parameter relationships
- **Outliers**: IQR-based anomaly detection table

### 3. Reporting
- **PDF Export**: Download full analysis reports
- **History**: Access last 5 uploads
