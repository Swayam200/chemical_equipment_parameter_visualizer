import React from 'react';

/**
 * Highlights search query within text
 * @param {string} text - The text to search in
 * @param {string} query - The search query to highlight
 * @returns {React.ReactNode[]} - Array of text and highlighted spans
 */
export const highlightText = (text, query) => {
    if (!query) return text;
    const parts = text.toString().split(new RegExp(`(${query})`, 'gi'));
    return parts.map((part, i) =>
        part.toLowerCase() === query.toLowerCase() ?
            <span key={i} className="bg-yellow-200 dark:bg-yellow-900 text-slate-900 dark:text-white px-0.5 rounded">{part}</span>
            : part
    );
};
