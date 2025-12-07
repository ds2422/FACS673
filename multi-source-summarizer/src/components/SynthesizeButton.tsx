import React from "react";
import ActionButton from "./ActionButton";
import { generateSummary } from "../utils/api";
import type { InputData } from "../types";

interface SynthesizeButtonProps {
  inputs: InputData[];
  setSummary: (s: string) => void;
  setLoading: (l: boolean) => void;
}

const SynthesizeButton: React.FC<SynthesizeButtonProps> = ({
  inputs,
  setSummary,
  setLoading,
}) => {
  // Check if at least one input has text content
  const hasValidInput = inputs.some(
    (input) => input.content && input.content.trim().length > 0
  );

  const handleSynthesize = async () => {
    if (!hasValidInput) return;

    setLoading(true);
    setSummary("");

    try {
      const validInputs = inputs.filter((i) => i.content.trim() !== "");
      const result = await generateSummary(validInputs);
      setSummary(result);
    } catch (error) {
      console.error(error);
      setSummary("Error generating summary. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex justify-center mt-8">
      <ActionButton
        onClick={handleSynthesize}
        label="Synthesize Summary"
        // Logic: Disable if no valid input OR if currently loading
        disabled={!hasValidInput}
      />
    </div>
  );
};

export default SynthesizeButton;
