// src/components/HistoryPanel.tsx
import React, { useEffect, useState } from "react";
import { X, Clock, FileText, ChevronRight } from "lucide-react";
import { fetchHistory } from "../utils/api";
import type { HistoryItem } from "../types";

interface HistoryPanelProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectSummary: (summary: string) => void; // Function to load summary into main view
}

const HistoryPanel: React.FC<HistoryPanelProps> = ({
  isOpen,
  onClose,
  onSelectSummary,
}) => {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(false);

  // Fetch history whenever the panel opens
  useEffect(() => {
    if (isOpen) {
      loadHistory();
    }
  }, [isOpen]);

  const loadHistory = async () => {
    setLoading(true);
    const data = await fetchHistory();
    // Sort by date (newest first)
    const sorted = data.sort(
      (a, b) =>
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
    setHistory(sorted);
    setLoading(false);
  };

  return (
    <>
      {/* Dark Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-30 z-40 transition-opacity"
          onClick={onClose}
        />
      )}

      {/* Sliding Panel */}
      <div
        className={`fixed right-0 top-0 h-full w-full sm:w-96 bg-white shadow-2xl z-50 transform transition-transform duration-300 ease-in-out ${
          isOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        {/* Header */}
        <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50">
          <div className="flex items-center gap-2 text-indigo-900">
            <Clock size={20} />
            <h2 className="font-bold text-xl">History</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-200 rounded-full transition"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="overflow-y-auto h-[calc(100%-80px)] p-4 space-y-4">
          {loading ? (
            <div className="text-center py-10 text-gray-500">
              Loading history...
            </div>
          ) : history.length === 0 ? (
            <div className="text-center py-10 text-gray-400">
              No history found.
            </div>
          ) : (
            history.map((item) => (
              <div
                key={item.id}
                onClick={() => {
                  onSelectSummary(item.summary);
                  onClose();
                }}
                className="group p-4 bg-white border border-gray-200 rounded-xl hover:shadow-md hover:border-indigo-300 cursor-pointer transition-all"
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="text-xs font-semibold text-indigo-600 bg-indigo-50 px-2 py-1 rounded">
                    {new Date(item.timestamp).toLocaleDateString()}
                  </span>
                  <ChevronRight
                    size={16}
                    className="text-gray-300 group-hover:text-indigo-500"
                  />
                </div>

                {/* Preview of summary */}
                <p className="text-sm text-gray-600 line-clamp-3 mb-3">
                  {item.summary.replace(/\*\*/g, "")}{" "}
                  {/* Remove markdown stars for preview */}
                </p>

                <div className="flex items-center gap-2 text-xs text-gray-400">
                  <FileText size={12} />
                  <span>
                    {item.inputs.length} Source
                    {item.inputs.length !== 1 ? "s" : ""}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </>
  );
};

export default HistoryPanel;
