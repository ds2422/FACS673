import React, { useRef } from "react";
import type { SourceType } from "../types";
import {
  Youtube,
  Link as LinkIcon,
  AlignLeft,
  CheckCircle2,
  FileText,
  UploadCloud,
  Trash2,
} from "lucide-react";

interface InputCardProps {
  index: number;
  type: SourceType;
  content: string;
  onTypeChange: (value: string) => void;
  onContentChange: (value: string) => void;
  isActive: boolean;
}

const InputCard: React.FC<InputCardProps> = ({
  index,
  type,
  content,
  onTypeChange,
  onContentChange,
  isActive,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Helper to convert file to Base64
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.type !== "application/pdf") {
      alert("Please upload a valid PDF file.");
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      const base64String = event.target?.result as string;
      onContentChange(base64String); // Save Base64 to state
    };
    reader.readAsDataURL(file);
  };

  const clearFile = () => {
    onContentChange("");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const getIcon = () => {
    switch (type) {
      case "youtube":
        return <Youtube size={18} className="text-red-500" />;
      case "url":
        return <LinkIcon size={18} className="text-blue-500" />;
      case "pdf":
        return <FileText size={18} className="text-orange-500" />;
      default:
        return <AlignLeft size={18} className="text-gray-500" />;
    }
  };

  return (
    <div
      className={`
        group relative h-full flex flex-col bg-white rounded-2xl transition-all duration-300
        border-2 ${
          isActive
            ? "border-indigo-500 shadow-xl shadow-indigo-100 translate-y-[-4px]"
            : "border-transparent shadow-md hover:shadow-lg hover:border-slate-200"
        }
    `}
    >
      {/* Header */}
      <div className="p-4 border-b border-slate-100 bg-slate-50/50 rounded-t-2xl flex justify-between items-center">
        <div className="flex items-center gap-2">
          <span
            className={`
                flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold
                ${
                  isActive
                    ? "bg-indigo-600 text-white"
                    : "bg-slate-200 text-slate-500"
                }
            `}
          >
            {index + 1}
          </span>
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Source
          </span>
        </div>

        <div className="relative">
          <div className="absolute left-2.5 top-1/2 -translate-y-1/2 pointer-events-none">
            {getIcon()}
          </div>
          <select
            value={type}
            onChange={(e) => {
              onTypeChange(e.target.value);
              onContentChange(""); // Clear content when switching types
            }}
            className="pl-9 pr-3 py-1.5 text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 cursor-pointer hover:bg-slate-50 transition-colors appearance-none"
          >
            <option value="text">Text</option>
            <option value="youtube">YouTube</option>
            <option value="url">Website</option>
            <option value="pdf">PDF Document</option>
          </select>
        </div>
      </div>

      {/* Input Area */}
      <div className="flex-grow p-4">
        {type === "pdf" ? (
          // PDF Upload UI
          <div className="h-full min-h-[140px] flex flex-col justify-center">
            {!content ? (
              <div
                onClick={() => fileInputRef.current?.click()}
                className="h-full border-2 border-dashed border-slate-300 rounded-xl flex flex-col items-center justify-center cursor-pointer hover:border-indigo-400 hover:bg-indigo-50/30 transition-all p-4"
              >
                <UploadCloud size={32} className="text-indigo-400 mb-2" />
                <span className="text-sm font-medium text-slate-600">
                  Click to Upload PDF
                </span>
                <span className="text-xs text-slate-400 mt-1">
                  Max size 5MB
                </span>
                <input
                  type="file"
                  accept="application/pdf"
                  ref={fileInputRef}
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </div>
            ) : (
              <div className="h-full border border-slate-200 rounded-xl bg-slate-50 p-4 flex flex-col items-center justify-center relative">
                <FileText size={40} className="text-orange-500 mb-2" />
                <span className="text-sm font-medium text-slate-700">
                  PDF Uploaded
                </span>
                <span className="text-xs text-green-600 font-medium">
                  Ready to summarize
                </span>

                <button
                  onClick={clearFile}
                  className="absolute top-2 right-2 p-1.5 bg-white text-red-500 rounded-full shadow hover:bg-red-50 transition"
                  title="Remove PDF"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            )}
          </div>
        ) : (
          // Standard Text Area for Text/URL/YouTube
          <textarea
            data-testid={`input-textarea-${index}`}
            className="w-full h-full min-h-[140px] text-sm text-slate-700 placeholder-slate-400 bg-transparent border-none resize-none focus:ring-0 p-0 leading-relaxed"
            placeholder={
              type === "youtube"
                ? "Paste YouTube Link..."
                : type === "url"
                ? "Paste Article URL..."
                : "Start typing or paste content here..."
            }
            value={content}
            onChange={(e) => onContentChange(e.target.value)}
          />
        )}
      </div>

      {/* Active Indicator */}
      <div className="px-4 pb-4 flex justify-end">
        <div
          className={`transition-all duration-500 ${
            isActive ? "opacity-100" : "opacity-0"
          }`}
        >
          <CheckCircle2 size={20} className="text-emerald-500" />
        </div>
      </div>
    </div>
  );
};

export default InputCard;
