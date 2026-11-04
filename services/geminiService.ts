import { GoogleGenAI } from "@google/genai";
import { NewsletterData, NewsItem } from "../types";

const parseGeneratedText = (text: string): { items: NewsItem[], title: string, edition: string, marketSentiment: number } => {
  const items: NewsItem[] = [];
  let currentItem: Partial<NewsItem> = {};
  let title = "MEA Strategic Talent Intelligence";
  let edition = `${new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}`;
  let marketSentiment = 75;

  const lines = text.split('\n');
  
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;

    if (trimmed.includes('::TITLE::')) title = trimmed.split('::TITLE::')[1]?.trim() || title;
    else if (trimmed.includes('::EDITION::')) edition = trimmed.split('::EDITION::')[1]?.trim() || edition;
    else if (trimmed.includes('::MARKET_SENTIMENT::')) marketSentiment = parseInt(trimmed.split('::MARKET_SENTIMENT::')[1]) || 75;
    else if (trimmed.includes('::NEW_ITEM::')) {
      if (currentItem.headline) items.push(currentItem as NewsItem);
      currentItem = {};
    } 
    else if (trimmed.includes('::HEADLINE::')) {
      if (currentItem.headline) items.push(currentItem as NewsItem);
      currentItem = { headline: trimmed.split('::HEADLINE::')[1]?.trim() };
    }
    else if (trimmed.includes('::DATE::')) currentItem.date = trimmed.split('::DATE::')[1]?.trim();
    else if (trimmed.includes('::REGION::')) currentItem.region = trimmed.split('::REGION::')[1]?.trim();
    else if (trimmed.includes('::SOURCE::')) currentItem.sourceName = trimmed.split('::SOURCE::')[1]?.trim();
    else if (trimmed.includes('::DOMAIN::')) currentItem.companyDomain = trimmed.split('::DOMAIN::')[1]?.trim();
    else if (trimmed.includes('::SUMMARY::')) currentItem.summary = trimmed.split('::SUMMARY::')[1]?.trim();
    else if (trimmed.includes('::IMPACT::')) currentItem.impactAnalysis = trimmed.split('::IMPACT::')[1]?.trim();
    else if (trimmed.includes('::CAT::')) currentItem.category = (trimmed.split('::CAT::')[1]?.trim() as any) || 'Economy';
    else if (trimmed.includes('::SCORE::')) currentItem.sentimentScore = parseInt(trimmed.split('::SCORE::')[1]) || 50;
    else if (trimmed.includes('::PILLAR::')) currentItem.pillar = (trimmed.split('::PILLAR::')[1]?.trim() as any) || 'Strategy';
  }

  if (currentItem.headline) items.push(currentItem as NewsItem);
  return { items, title, edition, marketSentiment };
};

export const generateNewsletter = async (): Promise<NewsletterData> => {
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  const today = new Date();
  const thirtyDaysAgo = new Date();
  thirtyDaysAgo.setDate(today.getDate() - 30);
  const cutOffStr = thirtyDaysAgo.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });

  const prompt = `
    Identity: Senior Market Intelligence Lead for Accenture MEA.
    Scope: MEA region specifically focusing on UAE, Saudi Arabia (KSA), Qatar, Egypt, and South Africa.
    Target: Extract exactly 10 high-impact developments in HR, Talent, and Workforce Strategy from the last 30 days (since ${cutOffStr}).

    Requirement for each of the 10 items:
    ::NEW_ITEM::
    ::HEADLINE:: [Concise, professional headline]
    ::DATE:: [Specific date]
    ::REGION:: [Country]
    ::SOURCE:: [Major news outlet]
    ::DOMAIN:: [Corporate domain for logo mapping, e.g., aramco.com]
    ::SUMMARY:: [2-3 sentence strategic summary]
    ::IMPACT:: [Accenture-specific strategic repercussions for our consulting business]
    ::CAT:: [One of: Upskilling, Leadership, Policy, Tech, Economy]
    ::SCORE:: [0-100 sentiment score for the news]
    ::PILLAR:: [One of: Digital, Strategy, Operations]

    Include Overall Metrics:
    ::TITLE:: MEA Talent Intelligence
    ::EDITION:: ${today.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
    ::MARKET_SENTIMENT:: [Average regional sentiment 0-100]
  `;

  try {
    const response = await ai.models.generateContent({
      model: "gemini-3-pro-preview",
      contents: prompt,
      config: { 
        tools: [{ googleSearch: {} }],
        thinkingConfig: { thinkingBudget: 16000 }
      },
    });

    const parsed = parseGeneratedText(response.text || "");
    const chunks = response.candidates?.[0]?.groundingMetadata?.groundingChunks || [];
    const groundingUrls = chunks.map((c: any) => ({ 
      title: c.web?.title || "Intelligence Source", 
      url: c.web?.uri 
    })).filter((c: any) => c.url);

    return { ...parsed, groundingUrls };
  } catch (error) {
    console.error("Critical failure in Intelligence Scan:", error);
    throw error;
  }
};