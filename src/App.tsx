// src/App.tsx
import React, { useState, useCallback, useMemo } from "react";
import {
  Header,
  InputSection,
  SynthesizeButton,
  SummaryOutput,
} from "./components";
import { withBackoff } from "./utils/backoff";
import { createPayload, API_URL, API_KEY } from "./utils/api";
import "./App.css"; // Add this import

const App: React.FC = () => {
  const [inputContents, setInputContents] = useState<string[]>(
    Array(5).fill("")
  );
  const [summary, setSummary] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleInputChange = useCallback((index: number, value: string) => {
    setInputContents((prev) => {
      const newContents = [...prev];
      newContents[index] = value;
      return newContents;
    });
  }, []);

  const compileContent = useMemo(() => {
    const activeContents = inputContents.filter((c) => c.trim() !== "");
    if (activeContents.length === 0) return "";

    let combined = `Please provide a comprehensive, multi-paragraph summary of the following documents/transcripts. Synthesize the main points across all sources, noting any overlaps or contradictions:\n\n`;
    activeContents.forEach((content, index) => {
      combined += `\n--- SOURCE ${index + 1} ---\n${content.trim()}\n`;
    });
    combined += `\n--- END ---`;
    return combined;
  }, [inputContents]);

  const activeInputCount = inputContents.filter((c) => c.trim() !== "").length;

  const handleSummarize = useCallback(async () => {
    setSummary(null);
    setErrorMessage(null);

    if (compileContent.length < 50) {
      setErrorMessage(
        "Please provide at least 50 characters across your sources."
      );
      return;
    }

    setIsLoading(true);

    const payload = createPayload(compileContent);

    try {
      const result = await withBackoff(async () => {
        const response = await fetch(`${API_URL}?key=${API_KEY}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          throw new Error(`API Error: ${response.status}`);
        }

        return response.json();
      });

      const generatedText = result.candidates?.[0]?.content?.parts?.[0]?.text;

      if (generatedText) {
        setSummary(generatedText);
      } else {
        setErrorMessage("Failed to generate summary. Please try again.");
      }
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "An unexpected error occurred."
      );
    } finally {
      setIsLoading(false);
    }
  }, [compileContent]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-indigo-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Header />

        <div className="space-y-8">
          <InputSection
            inputContents={inputContents}
            onInputChange={handleInputChange}
            activeCount={activeInputCount}
          />

          <div className="flex justify-center">
            <SynthesizeButton
              isLoading={isLoading}
              isDisabled={activeInputCount === 0}
              onClick={handleSummarize}
            />
          </div>

          <SummaryOutput
            summary={summary}
            isLoading={isLoading}
            activeCount={activeInputCount}
            errorMessage={errorMessage}
          />
        </div>
      </div>
    </div>
  );
};

export default App;
