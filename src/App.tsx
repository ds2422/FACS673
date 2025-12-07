import React, { useState, useEffect } from "react";
import Header from "./components/Header";
import InputSection from "./components/InputSection";
import SummaryOutput from "./components/SummaryOutput";
import SynthesizeButton from "./components/SynthesizeButton";
import HistoryPanel from "./components/HistoryPanel";
import Auth from "./components/Auth";
import { auth } from "./firebaseConfig";
import { onAuthStateChanged } from "firebase/auth";
import type { User } from "firebase/auth";
import type { InputData } from "./types";
import { History as HistoryIcon, LogOut, User as UserIcon } from "lucide-react";
import "./App.css";

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [showHistory, setShowHistory] = useState(false);

  const [inputs, setInputs] = useState<InputData[]>([
    { id: "1", type: "text", content: "" },
    { id: "2", type: "text", content: "" },
    { id: "3", type: "text", content: "" },
    { id: "4", type: "text", content: "" },
    { id: "5", type: "text", content: "" },
  ]);

  const [summary, setSummary] = useState<string>("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
    });
    return () => unsubscribe();
  }, []);

  const handleInputChange = (
    index: number,
    field: "content" | "type",
    value: string
  ) => {
    const newInputs = [...inputs];
    if (field === "type") {
      newInputs[index].type = value as any;
    } else {
      newInputs[index].content = value;
    }
    setInputs(newInputs);
  };

  const handleLogout = () => auth.signOut();

  if (!user) return <Auth />;

  const activeCount = inputs.filter((i) => i.content.trim() !== "").length;

  return (
    <div className="min-h-screen bg-slate-50 selection:bg-indigo-100 selection:text-indigo-700 font-sans">
      {/* Decorative Background Blobs */}
      <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-purple-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
        <div className="absolute top-[-10%] right-[-10%] w-96 h-96 bg-indigo-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-2000"></div>
        <div className="absolute bottom-[-20%] left-[20%] w-96 h-96 bg-pink-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-4000"></div>
      </div>

      <div className="relative z-10">
        <Header />

        {/* Toolbar */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-8 flex flex-col sm:flex-row justify-between items-center gap-4">
          <button
            onClick={() => setShowHistory(true)}
            className="flex items-center gap-2 px-5 py-2.5 bg-white text-slate-700 font-semibold rounded-full border border-slate-200 shadow-sm hover:shadow-md hover:border-indigo-200 transition-all active:scale-95"
          >
            <HistoryIcon size={18} className="text-indigo-600" />
            <span>Past Summaries</span>
          </button>

          <div className="flex items-center gap-3 bg-white px-2 py-2 rounded-full shadow-sm border border-slate-200">
            <div className="flex items-center gap-2 px-3">
              <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600">
                <UserIcon size={16} />
              </div>
              <span className="text-sm font-medium text-slate-600 hidden md:inline">
                {user.email}
              </span>
            </div>
            <div className="h-6 w-px bg-slate-200"></div>
            <button
              onClick={handleLogout}
              className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-full transition-colors"
              title="Logout"
            >
              <LogOut size={18} />
            </button>
          </div>
        </div>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
          <InputSection
            inputs={inputs}
            onInputChange={handleInputChange}
            activeCount={activeCount}
          />

          <SynthesizeButton
            inputs={inputs}
            setSummary={setSummary}
            setLoading={setLoading}
          />

          <SummaryOutput
            summary={summary}
            isLoading={loading}
            activeCount={activeCount}
          />
        </main>
      </div>

      <HistoryPanel
        isOpen={showHistory}
        onClose={() => setShowHistory(false)}
        onSelectSummary={(savedSummary) => setSummary(savedSummary)}
      />
    </div>
  );
}

export default App;
