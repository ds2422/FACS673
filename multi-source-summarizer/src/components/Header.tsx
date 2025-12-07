import React from "react";
import { Sparkles, BrainCircuit } from "lucide-react";

const Header: React.FC = () => {
  return (
    <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-slate-200/60 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-indigo-600 to-purple-600 p-2 rounded-xl shadow-lg shadow-indigo-200">
              <BrainCircuit className="text-white h-6 w-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gray-900 to-gray-600">
                Nexus AI
              </h1>
              <p className="text-xs text-slate-500 font-medium tracking-wide uppercase">
                Multi-Source Synthesis
              </p>
            </div>
          </div>

          {/* <div className="hidden md:flex items-center gap-2 text-sm font-medium text-slate-500 bg-slate-100/50 px-3 py-1 rounded-full border border-slate-200">
            <Sparkles size={14} className="text-amber-500" />
            <span>Powered by Gemini 1.5</span>
          </div> */}
        </div>
      </div>
    </header>
  );
};

export default Header;
