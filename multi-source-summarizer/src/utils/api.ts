// src/utils/api.ts
import { auth } from "../firebaseConfig";
import type { InputData, SummaryResponse, HistoryItem } from "../types";

const API_BASE_URL = "http://127.0.0.1:8000/api"; // Your Django URL

export const generateSummary = async (inputs: InputData[]): Promise<string> => {
  const user = auth.currentUser;
  
  if (!user) {
    throw new Error("User must be logged in to generate summaries.");
  }

  // Get the Firebase Token to prove identity to Django
  const token = await user.getIdToken();

  try {
    const response = await fetch(`${API_BASE_URL}/summarize/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`, // Send token
      },
      // Backend expects a list of objects with 'type' and 'value'
      body: JSON.stringify({
        inputs: inputs.map(i => ({
          type: i.type,
          value: i.content
        })) 
      }),
    });

    const data: SummaryResponse = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Failed to generate summary");
    }

    return data.summary;
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
};


export const fetchHistory = async (): Promise<HistoryItem[]> => {
  const user = auth.currentUser;
  if (!user) return [];

  const token = await user.getIdToken();

  try {
    const response = await fetch(`${API_BASE_URL}/history/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error("Failed to fetch history");
    }

    return await response.json();
  } catch (error) {
    console.error("History Error:", error);
    return [];
  }
};