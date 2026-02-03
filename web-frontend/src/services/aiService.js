import axios from 'axios';

const OPENROUTER_API_KEY = import.meta.env.VITE_OPENROUTER_API_KEY;
const SITE_URL = 'http://localhost:5173'; // Update for production
const SITE_NAME = 'Carbon Sleuth';

const PRIMARY_MODEL = import.meta.env.VITE_AI_MODEL || "google/gemini-2.0-flash-lite-preview-02-05:free";
const FALLBACK_MODEL = "google/gemma-2-9b-it:free"; // Robust fallback

const callOpenRouter = async (model, contextData, userQuery) => {
    const systemPrompt = `
    You are an industrial AI assistant for a chemical plant monitoring dashboard.
    
    CONTEXT DATA:
    ${JSON.stringify(contextData, null, 2)}

    USER QUERY: "${userQuery}"

    INSTRUCTIONS:
    1.  **PRIORITY:** If the user's request corresponds to a dashboard action (filtering, searching, navigating), **output the ACTION TAG ALONE**. Do not write a paragraph unless necessary.
    2.  **Filtering/Searching:** If the user asks to "Show me X", "Filter by X", "List X", "Show components with X" or simply types a keyword like "Pressure":
        -   **Step 1:** Generate a clean, comprehensive **Markdown Filtered Table** of the matching equipment from the context data. Include all relevant columns.
        -   **Step 2:** Append the Action Tag: \`|ACTION:SEARCH:X|\` at the very end.
    3.  **Navigation:** If the user asks for "Analytics", "Charts", "Dashboard", or "Home":
        -   Response: \`|ACTION:NAVIGATE:/analytics|\` (or other path)
    4.  **Analysis:** Only if the user asks a complex question ("Why is pressure high?", "Explain root cause"), then provide a text answer.
    5.  **Tables:** If you must generate a table, use standard Markdown tables.
    
    EXAMPLES:
    - User: "Show me warning components" -> AI: \`|ACTION:SEARCH:warning|\`
    - User: "Go to analytics" -> AI: \`|ACTION:NAVIGATE:/analytics|\`
    - User: "Pressure" -> AI: \`|ACTION:SEARCH:pressure|\`
    `;

    return await axios.post("https://openrouter.ai/api/v1/chat/completions", {
        "model": model,
        "messages": [
            { "role": "system", "content": systemPrompt },
            { "role": "user", "content": userQuery }
        ]
    }, {
        headers: {
            "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
            "HTTP-Referer": window.location.origin,
            "X-Title": SITE_NAME,
            "Content-Type": "application/json"
        }
    });
};

export const queryAI = async (contextData, userQuery) => {
    if (!OPENROUTER_API_KEY) {
        return "Error: OpenRouter API Key is missing. Please configure VITE_OPENROUTER_API_KEY in .env";
    }

    try {
        console.log(`Attempting AI Query with Primary Model: ${PRIMARY_MODEL}`);
        const response = await callOpenRouter(PRIMARY_MODEL, contextData, userQuery);
        return response.data.choices[0].message.content;

    } catch (primaryError) {
        console.warn(`Primary Model (${PRIMARY_MODEL}) Failed. Switching to Fallback (${FALLBACK_MODEL}).`, primaryError.message);

        try {
            const fallbackResponse = await callOpenRouter(FALLBACK_MODEL, contextData, userQuery);
            return fallbackResponse.data.choices[0].message.content + "\n\n*(Answered by Fallback Model)*";
        } catch (fallbackError) {
            console.error("All AI Models Failed Details:", {
                primary: primaryError.message,
                fallback: fallbackError.message
            });
            return "Sorry, both primary and fallback AI models are currently unavailable. Please check your API usage or internet connection.";
        }
    }
};
