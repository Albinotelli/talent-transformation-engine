import React, { useState } from 'react';
import { NewsletterData, NewsItem } from '../types';
import { 
  ExternalLink, TrendingUp, Building2, MapPin, Share2, Check, 
  Plus, BarChart3, ShieldCheck, Zap, Globe, Users, Calendar 
} from 'lucide-react';

interface NewsletterViewProps {
  data: NewsletterData;
  onCreateNew: () => void;
}

const MarketPulse: React.FC<{ data: NewsletterData }> = ({ data }) => (
  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
    <div className="glass-card p-8 rounded-3xl shadow-sm border border-gray-100 flex flex-col justify-between">
      <div className="flex justify-between items-start mb-6">
        <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest">MEA Sentiment Pulse</span>
        <BarChart3 className="w-5 h-5 text-[#A100FF]" />
      </div>
      <div className="flex items-end gap-3">
        <span className="text-5xl font-extrabold text-gray-900 tracking-tighter">{data.marketSentiment}%</span>
        <span className="text-sm text-emerald-500 font-bold mb-1 flex items-center">
          <TrendingUp className="w-4 h-4 mr-1" /> Bullish
        </span>
      </div>
      <div className="w-full bg-gray-100 h-2 rounded-full mt-6 overflow-hidden">
        <div 
          className="accenture-gradient h-full rounded-full transition-all duration-1000" 
          style={{ width: `${data.marketSentiment}%` }}
        ></div>
      </div>
    </div>

    <div className="glass-card p-8 rounded-3xl shadow-sm border border-gray-100">
      <div className="flex justify-between items-start mb-6">
        <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Strategic Vectors</span>
        <Zap className="w-5 h-5 text-[#A100FF]" />
      </div>
      <div className="flex flex-wrap gap-2">
        {['Digitalization', 'Giga-Projects', 'AI Sovereignty', 'Reskilling'].map(tag => (
          <span key={tag} className="px-3 py-1 bg-purple-50 text-[#A100FF] rounded-lg text-[10px] font-black border border-purple-100 uppercase">
            {tag}
          </span>
        ))}
      </div>
      <p className="text-[11px] text-gray-400 mt-6 font-medium italic">Cross-continental trend cluster</p>
    </div>

    <div className="glass-card p-8 rounded-3xl shadow-sm border border-gray-100">
      <div className="flex justify-between items-start mb-6">
        <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Regional Node Coverage</span>
        <Globe className="w-5 h-5 text-[#A100FF]" />
      </div>
      <div className="flex items-center gap-4">
        <div className="flex -space-x-3">
          {['UAE', 'KSA', 'EG', 'SA', 'QA'].map((code, i) => (
            <div key={code} className="w-10 h-10 rounded-full border-4 border-white bg-gray-50 flex items-center justify-center text-[10px] font-black text-gray-400 shadow-sm" style={{zIndex: 10 - i}}>
              {code}
            </div>
          ))}
        </div>
        <span className="text-xs font-bold text-gray-900 ml-2">5 Integrated Hubs</span>
      </div>
      <p className="text-[11px] text-gray-400 mt-6 font-medium uppercase tracking-tight">Active Intelligence Stream</p>
    </div>
  </div>
);

const NewsCard: React.FC<{ item: NewsItem; index: number }> = ({ item, index }) => {
  const [imgError, setImgError] = useState(false);
  const logoUrl = item.companyDomain ? `https://logo.clearbit.com/${item.companyDomain}` : null;

  return (
    <div 
      className="group relative bg-white rounded-[2rem] border border-gray-100 overflow-hidden mb-10 transition-all hover:shadow-2xl hover:-translate-y-1 animate-reveal"
      style={{ animationDelay: `${index * 150}ms` }}
    >
      <div className="p-10">
        <div className="flex flex-col lg:flex-row gap-10">
          <div className="flex-shrink-0">
             <div className="w-24 h-24 rounded-3xl border border-gray-50 bg-gray-50 flex items-center justify-center overflow-hidden shadow-sm group-hover:scale-110 transition-transform">
                {logoUrl && !imgError ? (
                  <img src={logoUrl} alt="" className="w-full h-full object-contain p-3" onError={() => setImgError(true)} />
                ) : (
                  <Building2 className="w-12 h-12 text-gray-300" />
                )}
             </div>
          </div>

          <div className="flex-grow">
            <div className="flex flex-wrap items-center gap-4 mb-6">
              <span className="text-[11px] font-black uppercase tracking-widest text-[#A100FF] px-3 py-1 bg-purple-50 rounded-full border border-purple-100">
                {item.pillar}
              </span>
              <span className="text-[11px] font-bold uppercase tracking-widest text-gray-400">
                {item.sourceName}
              </span>
              <div className="w-1 h-1 bg-gray-200 rounded-full"></div>
              <span className="flex items-center text-[11px] font-bold text-gray-500">
                <MapPin className="w-3 h-3 mr-1.5" /> {item.region}
              </span>
            </div>
            
            <h3 className="text-3xl font-bold text-gray-900 mb-6 leading-tight group-hover:text-[#A100FF] transition-colors tracking-tight">
              {item.headline}
            </h3>
            
            <p className="text-gray-600 leading-relaxed mb-10 text-xl font-light">
              {item.summary}
            </p>

            <div className="relative bg-[#FAFAFB] rounded-[1.5rem] p-8 border-l-[6px] border-[#A100FF] group-hover:bg-purple-50/20 transition-all">
              <div className="flex items-start gap-6">
                <div className="mt-1 flex-shrink-0 bg-white p-2 rounded-xl shadow-sm">
                   <ShieldCheck className="w-7 h-7 text-[#A100FF]" />
                </div>
                <div>
                  <h4 className="text-[11px] font-black text-[#460073] uppercase mb-3 tracking-widest">
                    Strategic Repercussions
                  </h4>
                  <p className="text-lg text-gray-800 font-medium italic leading-relaxed">
                    "{item.impactAnalysis}"
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export const NewsletterView: React.FC<NewsletterViewProps> = ({ data, onCreateNew }) => {
  const [copied, setCopied] = useState(false);

  const handleShare = () => {
    try {
        const jsonStr = JSON.stringify(data);
        const encoded = encodeURIComponent(btoa(new TextEncoder().encode(jsonStr).reduce((data, byte) => data + String.fromCharCode(byte), '')));
        const url = `${window.location.origin}${window.location.pathname}#digest=${encoded}`;
        navigator.clipboard.writeText(url).then(() => {
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        });
    } catch (e) { console.error(e); }
  };

  return (
    <div className="pb-32">
      <div className="relative bg-white pt-32 pb-24 px-6 overflow-hidden border-b border-gray-100">
         <div className="absolute top-0 left-0 w-full h-2 accenture-gradient"></div>
         <div className="max-w-4xl mx-auto relative text-center">
            <span className="text-[12px] font-black text-[#A100FF] uppercase tracking-[0.4em] mb-6 block">Executive Intelligence Bulletin</span>
            <h1 className="text-6xl md:text-8xl font-black text-gray-900 mb-8 tracking-tighter leading-none serif-display">
               {data.title}
            </h1>
            <div className="flex items-center justify-center gap-4 text-xs font-bold text-gray-500 uppercase tracking-widest mb-12">
              <Calendar className="w-4 h-4" /> {data.edition}
              <div className="w-1.5 h-1.5 bg-gray-200 rounded-full"></div>
              <Users className="w-4 h-4" /> Accenture Stakeholders
            </div>

            <button 
                onClick={handleShare}
                className="inline-flex items-center gap-4 px-10 py-5 bg-black text-white rounded-full hover:bg-gray-800 transition-all shadow-2xl active:scale-95 group"
            >
                {copied ? <Check className="w-5 h-5 text-emerald-400" /> : <Share2 className="w-5 h-5 group-hover:rotate-12 transition-transform" />}
                <span className="text-sm font-black tracking-tight uppercase">{copied ? "Encoded Link Copied" : "Share Intelligence Digest"}</span>
            </button>
         </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 mt-20">
        <MarketPulse data={data} />

        <div className="flex items-center gap-6 mb-12">
          <div className="h-px bg-gray-200 flex-grow"></div>
          <span className="text-[10px] font-black uppercase tracking-[0.6em] text-gray-400">Validated Intelligence</span>
          <div className="h-px bg-gray-200 flex-grow"></div>
        </div>

        <div className="space-y-6">
          {data.items.map((item, index) => <NewsCard key={index} item={item} index={index} />)}
        </div>

        {data.groundingUrls.length > 0 && (
          <div className="mt-32 p-16 glass-card rounded-[3rem] border border-gray-100 shadow-sm">
            <h3 className="text-2xl font-bold text-gray-900 mb-10 flex items-center tracking-tight">
              <ExternalLink className="w-7 h-7 mr-4 text-[#A100FF]" />
              Verified Source Nodes
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {data.groundingUrls.map((link, idx) => (
                <a 
                  key={idx} 
                  href={link.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex flex-col p-6 rounded-[1.5rem] bg-white border border-gray-100 hover:border-[#A100FF] hover:shadow-lg group transition-all"
                >
                  <span className="text-[10px] font-black text-gray-400 group-hover:text-[#A100FF] mb-2 uppercase">Source Node {idx + 1}</span>
                  <span className="text-sm font-bold text-gray-800 group-hover:text-gray-900 line-clamp-2">{link.title}</span>
                </a>
              ))}
            </div>
          </div>
        )}

        <div className="mt-32 text-center">
            <button
                onClick={onCreateNew}
                className="px-12 py-6 bg-white border border-gray-200 shadow-sm rounded-[2rem] text-sm font-black text-gray-900 hover:border-[#A100FF] transition-all flex items-center gap-3 mx-auto uppercase tracking-tighter"
            >
                <Plus className="w-5 h-5 text-[#A100FF]" />
                Initiate New Intel Scan
            </button>
        </div>
      </div>
    </div>
  );
};