import React from 'react';
import { ChevronRight } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="w-full bg-black text-white">
      <div className="accenture-gradient h-2 w-full"></div>
      <div className="max-w-4xl mx-auto px-6 py-6 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <span className="text-xl md:text-2xl font-bold tracking-tight text-white truncate">
            MEA Talent<span className="text-[#A100FF]">Intelligence</span>
          </span>
          <ChevronRight className="text-[#A100FF] w-6 h-6 hidden md:block" />
        </div>
        <div className="hidden md:block text-sm font-semibold uppercase tracking-widest text-gray-400">
          Executive Digest
        </div>
      </div>
    </header>
  );
};