import React, { useState, useEffect } from 'react';
import { generateNewsletter } from './services/geminiService';
import { AppState, NewsletterData, NewsItem } from './types';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { NewsletterView } from './components/NewsletterView';
import { SelectionView } from './components/SelectionView';
import { Cpu, Database, LineChart, Sparkles } from 'lucide-react';

const App: React.FC = () => {
  const [appState, setAppState] = useState<AppState>(AppState.IDLE);
  const [data, setData] = useState<NewsletterData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash;
      if (hash.startsWith('#digest=')) {
        try {
          const encoded = hash.substring('#digest='.length);
          const binString = atob(decodeURIComponent(encoded));
          const bytes = Uint8Array.from(binString, (m) => m.charCodeAt(0));
          const jsonStr = new TextDecoder().decode(bytes);
          const sharedData = JSON.parse(jsonStr);
          if (sharedData?.items) {
            setData(sharedData);
            setAppState(AppState.COMPLETE);
          }
        } catch (e) { console.error("Hash parsing error", e); }
      }
    };
    handleHashChange();
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const handleGenerate = async () => {
    setAppState(AppState.GENERATING);
    setError(null);
    try {
      const result = await generateNewsletter();
      setData(result);
      setAppState(AppState.SELECTION);
    } catch (err) {
      setError("Strategic scan failed. Verified MEA nodes unreachable.");
      setAppState(AppState.ERROR);
    }
  };

  return (
    <div className="min-h-screen flex flex-col selection:bg-purple-100">
      <Header />

      <main className="flex-grow">
        {appState === AppState.IDLE && (
          <div className="flex flex-col items-center justify-center min-h-[85vh] px-6 py-20">
            <div className="max-w-5xl w-full text-center">
              <div className="inline-flex items-center gap-3 px-5 py-2.5 bg-purple-50 rounded-full border border-purple-100 text-[#A100FF] font-black text-[11px] uppercase tracking-[0.25em] mb-12 animate-reveal">
                <Cpu className="w-4 h-4" /> MEA Strategy Intelligence Platform
              </div>
              
              <h1 className="text-7xl md:text-[9rem] font-black text-gray-900 mb-10 tracking-tighter leading-[0.85] animate-reveal [animation-delay:100ms] serif-display">
                Strategic <span className="text-[#A100FF]">MEA</span> Intel
              </h1>
              
              <p className="text-2xl text-gray-500 font-light mb-16 max-w-2xl mx-auto leading-relaxed animate-reveal [animation-delay:200ms]">
                Executive monitoring of workforce dynamics across the Middle East & Africa. 
                Targeting UAE, KSA, Egypt, and South Africa.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-10 mb-20 max-w-4xl mx-auto animate-reveal [animation-delay:300ms]">
                {[
                  { icon: Database, title: "Continental Reach", desc: "5 Major Market Nodes" },
                  { icon: LineChart, title: "Sentiment Engine", desc: "Live Market Trend Scoring" },
                  { icon: Sparkles, title: "Executive Layer", desc: "Consultancy-Grade Impact" }
                ].map((item, i) => (
                  <div key={i} className="flex flex-col items-center p-10 bg-white rounded-[2.5rem] border border-gray-100 shadow-sm hover:shadow-xl hover:-translate-y-2 transition-all">
                    <item.icon className="w-10 h-10 text-[#A100FF] mb-6" />
                    <h3 className="font-bold text-lg mb-2 tracking-tight">{item.title}</h3>
                    <p className="text-sm text-gray-400 font-medium">{item.desc}</p>
                  </div>
                ))}
              </div>

              <button
                onClick={handleGenerate}
                className="group relative px-16 py-8 bg-black text-white rounded-full font-black text-xl tracking-tight overflow-hidden transition-all hover:scale-105 active:scale-95 shadow-[0_20px_50px_rgba(0,0,0,0.2)] animate-reveal [animation-delay:400ms]"
              >
                <div className="absolute inset-0 accenture-gradient opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                <span className="relative z-10 flex items-center uppercase tracking-widest">
                   Initiate Strategic Scan
                   <Sparkles className="ml-4 w-7 h-7 animate-pulse" />
                </span>
              </button>
            </div>
          </div>
        )}

        {appState === AppState.GENERATING && (
          <div className="flex flex-col items-center justify-center min-h-[85vh] px-6 text-center">
             <div className="w-40 h-40 relative mb-12">
                <div className="absolute inset-0 border-8 border-gray-100 rounded-full"></div>
                <div className="absolute inset-0 border-8 border-transparent border-t-[#A100FF] rounded-full animate-spin"></div>
                <div className="absolute inset-0 flex items-center justify-center">
                   <Cpu className="w-16 h-16 text-[#A100FF] animate-pulse" />
                </div>
             </div>
             <h3 className="text-4xl font-black text-gray-900 mb-4 tracking-tighter uppercase serif-display">Aggregating Intel</h3>
             <p className="text-gray-400 font-bold tracking-widest text-sm uppercase">
                Querying UAE • KSA • Egypt • South Africa • Qatar
             </p>
          </div>
        )}

        {appState === AppState.SELECTION && data && (
            <SelectionView data={data} onConfirm={(items) => {
              setData({ ...data, items });
              setAppState(AppState.COMPLETE);
            }} />
        )}

        {appState === AppState.COMPLETE && data && (
          <NewsletterView data={data} onCreateNew={() => {
            setAppState(AppState.IDLE);
            setData(null);
            window.history.pushState("", "", window.location.pathname);
          }} />
        )}

        {appState === AppState.ERROR && (
          <div className="flex flex-col items-center justify-center min-h-[85vh]">
             <div className="bg-red-50 p-16 rounded-[3rem] border border-red-100 text-center max-w-xl">
                <h3 className="text-3xl font-black text-red-900 mb-6 uppercase tracking-tighter serif-display">Intelligence Failure</h3>
                <p className="text-red-700 font-medium mb-12 text-lg leading-relaxed">{error}</p>
                <button
                  onClick={() => setAppState(AppState.IDLE)}
                  className="px-12 py-5 bg-red-900 text-white font-black rounded-full transition-all hover:scale-105 uppercase tracking-widest text-xs"
                >
                  Reset Security Protocol
                </button>
             </div>
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
};

export default App;