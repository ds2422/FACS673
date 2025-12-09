// src/types/index.ts

export type SourceType = 'text' | 'url' | 'youtube' | 'pdf';

export interface InputData {
  id: string;
  type: SourceType;
  content: string; // The URL or the raw text
}

export interface SummaryResponse {
  summary: string;
  error?: string;
}

export interface HistoryItem {
  id: string;
  inputs: InputData[];
  summary: string;
  timestamp: string;
}

export interface HistoryItem {
  id: string;
  summary: string;
  timestamp: string; // The backend returns this as an ISO date string
  inputs: InputData[]; // To show what sources were used
}

// src/types/index.ts
export interface SummaryOutputProps {
  summary: string;
  isLoading: boolean;
  activeCount: number;
  errorMessage?: string; // Optional string
}