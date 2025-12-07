import React from "react";
import InputCard from "./InputCard";
import type { InputData } from "../types/index.ts"; // Ensure these are imported

interface InputSectionProps {
  inputs: InputData[]; // CHANGED: Now expects array of objects
  onInputChange: (
    index: number,
    field: "content" | "type",
    value: string
  ) => void; // CHANGED: Handles type updates
  activeCount: number;
}

const InputSection: React.FC<InputSectionProps> = ({
  inputs,
  onInputChange,
  activeCount,
}) => {
  return (
    <section className="mb-8">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Input Sources</h2>
        <div className="w-12 h-1 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-full"></div>
        <p className="text-gray-600 text-sm mt-3">
          {activeCount} of 5 sources active
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {inputs.map((inputData, index) => (
          <div
            key={inputData.id || index}
            className="bg-white p-5 rounded-xl shadow-md hover:shadow-lg transition-shadow border border-gray-200"
          >
            <InputCard
              index={index}
              type={inputData.type} // Pass Type
              content={inputData.content} // Pass Content
              onTypeChange={(val) => onInputChange(index, "type", val)} // New Handler
              onContentChange={(val) => onInputChange(index, "content", val)} // New Handler
              isActive={inputData.content.trim() !== ""}
            />
          </div>
        ))}
      </div>
    </section>
  );
};

export default InputSection;
