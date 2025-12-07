import React from "react";
import { Sparkles, Loader2, ArrowRight } from "lucide-react";

interface ActionButtonProps {
  onClick: () => void;
  label: string;
  disabled?: boolean;
  isLoading?: boolean;
}

const ActionButton: React.FC<ActionButtonProps> = ({
  onClick,
  label,
  disabled = false,
  isLoading = false,
}) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled || isLoading}
      className={`
        relative group flex items-center justify-center gap-3 px-10 py-5 w-full md:w-auto
        rounded-2xl font-bold text-lg tracking-wide transition-all duration-300
        ${
          disabled
            ? "bg-slate-200 text-slate-400 cursor-not-allowed border border-slate-300"
            : "bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-600 bg-[length:200%_auto] hover:bg-right text-white shadow-xl shadow-indigo-200 hover:shadow-2xl hover:shadow-indigo-300 hover:-translate-y-1"
        }
      `}
    >
      {isLoading ? (
        <Loader2 className="animate-spin" size={24} />
      ) : (
        <>
          <Sparkles
            size={20}
            className={
              disabled
                ? ""
                : "text-indigo-200 group-hover:text-white transition-colors"
            }
          />
          <span>{label}</span>
          {!disabled && (
            <ArrowRight
              size={20}
              className="opacity-70 group-hover:translate-x-1 transition-transform"
            />
          )}
        </>
      )}
    </button>
  );
};

export default ActionButton;
