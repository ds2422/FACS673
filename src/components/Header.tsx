import React from "react";
import { AlertCircle } from "lucide-react";

const Header: React.FC = () => {
  return (
    <header className="text-center mb-12 pt-4">
      <div className="mb-3 inline-block">
        <div className="text-5xl font-black bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-500 bg-clip-text text-transparent">
          Content Synthesizer
        </div>
      </div>
      <p className="text-lg text-gray-600 mb-6 max-w-2xl mx-auto">
        Intelligently combine multiple sources into comprehensive, coherent
        summaries powered by AI
      </p>
      <div className="flex items-start gap-3 bg-blue-50 p-4 rounded-lg border border-blue-200 max-w-2xl mx-auto">
        <div className="text-blue-600 flex-shrink-0 mt-0.5">
          <AlertCircle size={20} />
        </div>
        <p className="text-sm text-blue-800">
          <span className="font-semibold">How to use:</span> Paste up to 5
          sources (web content, documents, transcripts) and let AI synthesize
          them into a unified summary.
        </p>
      </div>
    </header>
  );
};

export default Header;
