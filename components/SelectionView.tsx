import React, { useState } from 'react';
import { NewsletterData, NewsItem } from '../types';
import { CheckCircle, Circle, MapPin, Calendar, Building2, Info } from 'lucide-react';

interface SelectionViewProps {
  data: NewsletterData;
  onConfirm: (selectedItems: NewsItem[]) => void;
}

export const SelectionView: React.FC<SelectionViewProps> = ({ data, onConfirm }) => {
  const [selectedIndices, setSelectedIndices] = useState<Set<number>>(new Set());
  
  // Aim for 7, but if fewer items are found, require a reasonable majority
  const maxAvailable = data.items.length;
  const TARGET_COUNT = Math.min(7, maxAvailable);

  const toggleSelection = (index: number) => {
    const newSelection = new Set(selectedIndices);
    if (newSelection.has(index)) {
      newSelection.delete(index);
    } else {
      if (newSelection.size < TARGET_COUNT) {
        newSelection.add(index);
      }
    }
    setSelectedIndices(newSelection);
  };

  const handleConfirm = () => {
    if (selectedIndices.size < TARGET_COUNT) return;
    const selectedItems = data.items.filter((_, idx) => selectedIndices.has(idx));
    onConfirm(selectedItems);
  };

  return (
    <div className="animate-fade-in pb-24">
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
        <div className="max-w-4xl mx-auto px-6 py-4 flex flex-col md:flex-row justify-between items-center gap-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Curate Your Digest</h2>
            <p className="text-gray-500 text-sm">
              Select <span className="font-bold text-[#A100FF]">{TARGET_COUNT} articles</span> to include in your final edition.
            </p>
          </div>
          <div className="flex items-center gap-4">
             <div className="text-sm font-semibold">
                <span className={`${selectedIndices.size === TARGET_COUNT ? 'text-green-600' : 'text-gray-500'}`}>
                    {selectedIndices.size} / {TARGET_COUNT} Selected
                </span>
             </div>
             <button
                onClick={handleConfirm}
                disabled={selectedIndices.size < TARGET_COUNT}
                className={`px-6 py-2 rounded-md font-bold text-sm transition-all ${
                    selectedIndices.size === TARGET_COUNT 
                    ? 'bg-[#A100FF] text-white hover:bg-[#8a00db] shadow-md transform hover:-translate-y-0.5' 
                    : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                }`}
             >
                Generate Final Newsletter
             </button>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8">
        {data.items.length === 0 && (
          <div className="bg-orange-50 border border-orange-200 p-6 rounded-xl text-center">
            <Info className="w-12 h-12 text-orange-400 mx-auto mb-4" />
            <h3 className="text-lg font-bold text-orange-800">No Articles Found</h3>
            <p className="text-orange-700">The AI scan didn't return any specific items. This could be due to strict date filters or a temporary search issue.</p>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {data.items.map((item, index) => {
              const isSelected = selectedIndices.has(index);
              const logoUrl = item.companyDomain ? `https://logo.clearbit.com/${item.companyDomain}` : null;

              return (
                  <div 
                      key={index}
                      onClick={() => toggleSelection(index)}
                      className={`relative cursor-pointer bg-white rounded-xl border-2 transition-all duration-200 overflow-hidden hover:shadow-md ${
                          isSelected 
                          ? 'border-[#A100FF] shadow-purple-100' 
                          : 'border-gray-100 hover:border-gray-300'
                      }`}
                  >
                      <div className="p-5">
                          <div className="flex justify-between items-start mb-3">
                              <div className="flex items-center gap-2">
                                  <div className="w-10 h-10 rounded-md border border-gray-100 bg-gray-50 flex items-center justify-center p-1 overflow-hidden">
                                      {logoUrl ? (
                                          <img 
                                            src={logoUrl} 
                                            alt="Logo" 
                                            className="w-full h-full object-contain" 
                                            onError={(e) => {
                                              e.currentTarget.style.display = 'none';
                                              e.currentTarget.parentElement!.innerHTML = '<div class="text-gray-400 font-bold text-xs uppercase">News</div>';
                                            }} 
                                          />
                                      ) : (
                                          <Building2 className="w-5 h-5 text-gray-400" />
                                      )}
                                  </div>
                                  <div className="flex flex-col">
                                      <span className="text-xs font-bold text-gray-500 uppercase tracking-wide">{item.sourceName || "Industry News"}</span>
                                      <span className="text-xs text-gray-400 flex items-center"><Calendar className="w-3 h-3 mr-1"/> {item.date}</span>
                                  </div>
                              </div>
                              <div>
                                  {isSelected ? (
                                      <CheckCircle className="w-6 h-6 text-[#A100FF] fill-purple-50" />
                                  ) : (
                                      <Circle className="w-6 h-6 text-gray-300" />
                                  )}
                              </div>
                          </div>

                          <h3 className="font-bold text-gray-900 mb-2 leading-snug line-clamp-3 min-h-[4.5rem]">
                              {item.headline}
                          </h3>

                          <div className="flex items-center gap-2 mb-3">
                               <span className="flex items-center text-xs font-semibold text-[#A100FF] bg-purple-50 px-2 py-0.5 rounded border border-purple-100">
                                  <MapPin className="w-3 h-3 mr-1" />
                                  {item.region}
                              </span>
                          </div>

                          <p className="text-sm text-gray-600 line-clamp-3">
                              {item.summary}
                          </p>
                      </div>
                      {isSelected && (
                          <div className="absolute inset-0 bg-[#A100FF] opacity-5 pointer-events-none"></div>
                      )}
                  </div>
              );
          })}
        </div>
      </div>
    </div>
  );
};