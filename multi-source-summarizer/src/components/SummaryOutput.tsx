import React, { useState } from "react";
import { Loader2, AlertTriangle, Copy, Check, FileText } from "lucide-react";
import type { SummaryOutputProps } from "../types";
import { Sparkles } from "lucide-react";

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

  const renderFormattedText = (text: string) => {
    return text.split("\n").map((line, index) => {
      const trimmedLine = line.trim();
      if (!trimmedLine) return <br key={index} />;

      // Lists
      if (trimmedLine.startsWith("* ") || trimmedLine.startsWith("- ")) {
        const content = trimmedLine.substring(2);
        const parts = content.split(/(\*\*.*?\*\*)/g);
        return (
          <div key={index} className="flex gap-3 mb-2">
            <div className="min-w-[6px] h-[6px] rounded-full bg-indigo-500 mt-2.5"></div>
            <p className="text-slate-700 leading-7">
              {parts.map((part, i) =>
                part.startsWith("**") ? (
                  <strong key={i} className="text-slate-900 font-bold">
                    {part.slice(2, -2)}
                  </strong>
                ) : (
                  part
                )
              )}
            </p>
          </div>
        );
      }

      // Headers/Bold
      const parts = trimmedLine.split(/(\*\*.*?\*\*)/g);
      return (
        <p key={index} className="mb-4 text-slate-700 leading-relaxed text-lg">
          {parts.map((part, i) => {
            if (part.startsWith("**") && part.endsWith("**")) {
              return (
                <strong
                  key={i}
                  className="text-slate-900 font-bold text-xl block mb-2 mt-4"
                >
                  {part.slice(2, -2)}
                </strong>
              );
            }
            return part;
          })}
        </p>
      );
    });
  };

  return (
    <section className="relative">
      <div className="flex items-center gap-4 mb-6">
        <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white shadow-lg shadow-emerald-100">
          <FileText size={20} />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-slate-800">Results</h2>
          <p className="text-slate-500 text-sm">AI-Generated Synthesis</p>
        </div>
      </div>

      <div
        className={`
         relative min-h-[400px] bg-white rounded-3xl border border-slate-200 overflow-hidden transition-all duration-500
         ${summary ? "shadow-2xl shadow-indigo-100/50" : "shadow-sm"}
      `}
      >
        {errorMessage && (
          <div className="absolute inset-0 z-20 bg-white/90 backdrop-blur-sm flex items-center justify-center p-8">
            <div className="bg-red-50 border border-red-100 p-6 rounded-2xl max-w-md text-center">
              <div className="mx-auto w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mb-3">
                <AlertTriangle className="text-red-500" size={24} />
              </div>
              <h3 className="font-bold text-red-900 mb-2">Generation Failed</h3>
              <p className="text-red-700 text-sm">{errorMessage}</p>
            </div>
          </div>
        )}

        {summary ? (
          <div className="relative">
            {/* Toolbar */}
            <div className="sticky top-0 z-10 flex justify-end p-4 bg-white/80 backdrop-blur-sm border-b border-slate-100">
              <button
                onClick={handleCopy}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-600 bg-slate-50 hover:bg-indigo-50 hover:text-indigo-600 rounded-lg transition-colors"
              >
                {copied ? <Check size={16} /> : <Copy size={16} />}
                {copied ? "Copied" : "Copy to Clipboard"}
              </button>
            </div>

            {/* Content */}
            <article className="p-8 sm:p-12 max-w-none">
              {renderFormattedText(summary)}
            </article>
          </div>
        ) : (
          <div className="absolute inset-0 flex flex-col items-center justify-center p-8 text-center bg-slate-50/30">
            {isLoading ? (
              <div className="flex flex-col items-center">
                <div className="relative w-20 h-20 mb-6">
                  <div className="absolute inset-0 border-4 border-indigo-100 rounded-full"></div>
                  <div className="absolute inset-0 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                  <Sparkles
                    className="absolute inset-0 m-auto text-indigo-500 animate-pulse"
                    size={24}
                  />
                </div>
                <h3 className="text-xl font-bold text-slate-800 mb-2">
                  Synthesizing...
                </h3>
                <p className="text-slate-500 max-w-xs mx-auto">
                  Analyzing {activeCount} source{activeCount !== 1 ? "s" : ""}{" "}
                  and generating a coherent summary.
                </p>
              </div>
            ) : (
              <div className="opacity-40 hover:opacity-60 transition-opacity duration-500">
                <div className="w-24 h-24 bg-indigo-50 rounded-3xl rotate-12 mx-auto mb-6 flex items-center justify-center">
                  <FileText className="text-indigo-300 -rotate-12" size={48} />
                </div>
                <p className="text-lg font-medium text-slate-600">
                  Ready to Generate
                </p>
                <p className="text-slate-400 text-sm mt-1">
                  Add content sources above
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
