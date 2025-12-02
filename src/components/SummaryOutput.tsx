import React, { useState } from "react";
import { Loader, AlertCircle, Copy } from "lucide-react";
import type { SummaryOutputProps } from "../types";

const SummaryOutput: React.FC<SummaryOutputProps> = ({
  summary,
  isLoading,
  activeCount,
  errorMessage,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (summary) {
      navigator.clipboard.writeText(summary);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <section className="mb-8">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Summary Result
        </h2>
        <div className="w-12 h-1 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-full"></div>
      </div>

      <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
        {errorMessage && (
          <div className="p-6 bg-red-50 border-b-2 border-red-200 flex gap-3">
            <AlertCircle className="text-red-600 flex-shrink-0" size={24} />
            <div>
              <p className="font-semibold text-red-900">Error</p>
              <p className="text-red-800 text-sm mt-1">{errorMessage}</p>
            </div>
          </div>
        )}

        {summary ? (
          <div className="p-8">
            <div className="flex justify-between items-center mb-6">
              <p className="text-sm text-gray-500">AI-Generated Summary</p>
              <button
                onClick={handleCopy}
                className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition text-sm font-medium"
              >
                <Copy size={16} />
                {copied ? "Copied!" : "Copy"}
              </button>
            </div>
            <article className="prose prose-sm max-w-none text-gray-800 leading-relaxed space-y-4">
              {summary.split("\n").map(
                (paragraph, index) =>
                  paragraph.trim() && (
                    <p key={index} className="text-base">
                      {paragraph}
                    </p>
                  )
              )}
            </article>
          </div>
        ) : (
          <div className="p-12 text-center">
            {isLoading ? (
              <div className="space-y-3">
                <div className="flex justify-center">
                  <Loader size={32} className="animate-spin text-indigo-600" />
                </div>
                <p className="text-lg text-gray-700 font-semibold">
                  Analyzing {activeCount} source
                  {activeCount !== 1 ? "s" : ""}
                </p>
                <p className="text-gray-500 text-sm">
                  This may take a few moments...
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="text-4xl mb-3">📄</div>
                <p className="text-lg text-gray-600">
                  Paste your content above and click the button to generate a
                  summary.
                </p>
                <p className="text-gray-500 text-sm">
                  The more detailed your sources, the better the synthesis.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
};

export default SummaryOutput;
