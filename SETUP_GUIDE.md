# ChemVis AI Setup Guide

This guide helps you set up the AI-powered features for ChemVis.

## 1. Get an OpenRouter API Key
ChemVis uses OpenRouter to access powerful AI models like Gemini Pro and Claude 3.

1.  Go to [OpenRouter.ai](https://openrouter.ai/).
2.  Sign up or Log in.
3.  Go to **Keys** (or settings) and create a new API Key.
4.  Copy the key (it starts with `sk-or-v1-...`).

## 2. Configure the Frontend
You need to tell the frontend application your API key.

1.  Navigate to the `web-frontend` folder in your project.
2.  Check if a file named `.env` exists.
    - If **YES**: Open it.
    - If **NO**: Create a new file named `.env`.
3.  Add the following lines to the file:

    ```env
    VITE_OPENROUTER_API_KEY=sk-or-v1-your-key-here...
    VITE_AI_MODEL=google/gemini-2.0-flash-lite-preview-02-05:free
    ```

    *   **VITE_OPENROUTER_API_KEY**: Replace with your actual key from step 1.
    *   **VITE_AI_MODEL**: (Optional) The ID of the model you want to use.
        *   Default: `google/gemini-2.0-flash-lite-preview-02-05:free` (Free & Fast)
        *   Alternative: `anthropic/claude-3-haiku` (Smart & Fast)
        *   Check [OpenRouter Models](https://openrouter.ai/models) for more IDs.

4.  **Save** the file.

## 3. Restart the Application
For the new environment variable to be loaded, you must restart the frontend server.

1.  Go to the terminal running `npm run dev`.
2.  Press `Ctrl + C` to stop it.
3.  Run `npm run dev` again.

## 4. Test It
1.  Open the app in your browser (e.g., `http://localhost:5173`).
2.  Upload a CSV log file if you haven't already.
3.  In the top search bar, type a question like:
    > "What is the average pressure?"
    > "Are there any critical anomalies?"
4.  Press **Enter**.
5.  Wait a moment for the AI to analyze and respond in the modal!
