import React from "react";
import { Loader } from "lucide-react";
import { useState } from "react";

const [isLoading, setIsLoading] = useState(false);

const SynthesizeButton = ({
  isLoading,
  isDisabled,
  onClick,
}: {
  isLoading: boolean;
  isDisabled: boolean;
  onClick: () => void;
}) => {
  const handleSynthesize = () => {
    if (!isLoading && !isDisabled) {
      onClick();
    }
  };
  return (
    <button
      onClick={onClick}
      disabled={isLoading || isDisabled}
      className={`
        px-8 py-3.5 text-base font-bold rounded-full shadow-xl transition duration-300 transform
        flex items-center justify-center gap-2 min-w-max
        ${
          isLoading || isDisabled
            ? "bg-gray-400 text-gray-600 cursor-not-allowed"
            : "bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:shadow-2xl hover:scale-105 active:scale-95"
        }
      `}
    >
      {isLoading ? (
        <>
          <Loader size={20} className="animate-spin" />
          Synthesizing...
        </>
      ) : (
        <>
          <span>✨</span>
          Synthesize Summary
        </>
      )}
    </button>
  );
};
export default SynthesizeButton;
