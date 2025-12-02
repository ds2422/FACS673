// src/components/InputCard.tsx
import React, { useState } from "react";
import { CheckCircle, Loader, Link as LinkIcon } from "lucide-react";
import type { InputCardProps } from "../types";
import {
  fetchUrlContent,
  fetchYouTubeTranscript,
  isYouTubeUrl,
} from "../utils/urlFetcher";

const InputCard: React.FC<InputCardProps> = ({
  index,
  content,
  onChange,
  isActive,
}) => {
  const [isFetching, setIsFetching] = useState(false);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [urlInput, setUrlInput] = useState("");

  const handleFetchUrl = async () => {
    if (!urlInput.trim()) {
      setFetchError("Please enter a URL");
      return;
    }

    setIsFetching(true);
    setFetchError(null);

    try {
      // Check if it's a YouTube URL
      if (isYouTubeUrl(urlInput)) {
        const result = await fetchYouTubeTranscript(urlInput);
        if (!result.success) {
          setFetchError(result.error ?? "Failed to fetch YouTube transcript");
        }
      } else {
        // Fetch regular URL content
        const result = await fetchUrlContent(urlInput);

        if (result.success && result.content) {
          onChange(index, result.content);
          setUrlInput("");
          setFetchError(null);
        } else {
          setFetchError(result.error || "Failed to fetch URL content");
        }
      }
    } catch (error) {
      setFetchError(
        error instanceof Error ? error.message : "An error occurred"
      );
    } finally {
      setIsFetching(false);
    }
  };

  const handleClearInput = () => {
    onChange(index, "");
    setUrlInput("");
    setFetchError(null);
  };

  return (
    <div className="flex flex-col h-full">
      <label className="mb-3 text-sm font-semibold text-gray-700 flex items-center gap-2">
        <div
          className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold text-white transition-all ${
            isActive
              ? "bg-gradient-to-br from-indigo-500 to-purple-600 shadow-lg"
              : "bg-gray-300"
          }`}
        >
          {index + 1}
        </div>
        <span>Source {index + 1}</span>
      </label>

      {/* URL Fetcher Section */}
      <div className="mb-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
        <div className="flex gap-2 items-end">
          <div className="flex-1">
            <label className="text-xs font-medium text-blue-800 mb-1 block">
              Fetch from URL
            </label>
            <input
              type="text"
              placeholder="Paste URL here..."
              value={urlInput}
              onChange={(e) => {
                setUrlInput(e.target.value);
                setFetchError(null);
              }}
              onKeyPress={(e) => {
                if (e.key === "Enter") {
                  handleFetchUrl();
                }
              }}
              disabled={isFetching}
              className="w-full px-3 py-2 text-sm border border-blue-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            />
          </div>
          <button
            onClick={handleFetchUrl}
            disabled={isFetching || !urlInput.trim()}
            className={`px-3 py-2 rounded text-sm font-medium flex items-center gap-1 transition ${
              isFetching || !urlInput.trim()
                ? "bg-gray-300 text-gray-600 cursor-not-allowed"
                : "bg-blue-500 text-white hover:bg-blue-600"
            }`}
          >
            {isFetching ? (
              <>
                <Loader size={16} className="animate-spin" />
                <span>Fetching</span>
              </>
            ) : (
              <>
                <LinkIcon size={16} />
                <span>Fetch</span>
              </>
            )}
          </button>
        </div>

        {fetchError && (
          <div className="mt-2 p-2 bg-red-100 border border-red-300 rounded text-xs text-red-800">
            {fetchError}
          </div>
        )}
      </div>

      {/* Text Input Section */}
      <textarea
        className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition duration-200 h-40 resize-none text-sm bg-white hover:border-gray-400"
        placeholder="Or paste your document, transcript, or web content here..."
        value={content}
        onChange={(e) => onChange(index, e.target.value)}
      />

      {/* Footer */}
      <div className="mt-2 flex justify-between items-center">
        {content.trim() && (
          <div className="text-xs text-gray-500 flex items-center gap-1">
            <CheckCircle size={14} className="text-green-500" />
            {content.length} characters
          </div>
        )}
        {content.trim() && (
          <button
            onClick={handleClearInput}
            className="text-xs text-red-600 hover:text-red-800 font-medium"
          >
            Clear
          </button>
        )}
      </div>
    </div>
  );
};

export default InputCard;
