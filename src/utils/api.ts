export const API_KEY = import.meta.env.VITE_GEMINI_API_KEY || "";
export const API_URL = import.meta.env.VITE_API_URL || "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent";

export const SYSTEM_PROMPT = `You are an expert document synthesis AI. Analyze multiple pieces of text and create a single, cohesive, professional summary. Ensure the summary is well-structured, captures all key themes, and maintains a logical flow.`;

export interface ApiPayload {
  contents: Array<{
    parts: Array<{
      text: string;
    }>;
  }>;
  systemInstruction: {
    parts: Array<{
      text: string;
    }>;
  };
}

export const createPayload = (userQuery: string): ApiPayload => ({
  contents: [{ parts: [{ text: userQuery }] }],
  systemInstruction: { parts: [{ text: SYSTEM_PROMPT }] },
});