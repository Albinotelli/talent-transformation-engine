export interface NewsItem {
  headline: string;
  sourceName: string;
  date?: string;
  region: string;
  summary: string;
  impactAnalysis: string;
  companyDomain?: string;
  category: 'Upskilling' | 'Leadership' | 'Policy' | 'Tech' | 'Economy';
  sentimentScore: number; // 0 to 100
  pillar: 'Digital' | 'Strategy' | 'Operations';
}

export interface NewsletterData {
  title: string;
  edition: string;
  items: NewsItem[];
  groundingUrls: { title: string; url: string }[];
  marketSentiment: number;
}

export enum AppState {
  IDLE = 'IDLE',
  GENERATING = 'GENERATING',
  SELECTION = 'SELECTION',
  COMPLETE = 'COMPLETE',
  ERROR = 'ERROR'
}