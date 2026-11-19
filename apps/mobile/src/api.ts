// Termux'ta API aynı telefonda çalıştığı için localhost yeterli.
export const API_URL = 'http://localhost:8000';

export type Summary = {
  name: string; district: string; level: string; score: number;
  by_time: number[]; sample_data: boolean;
  events: { kind: string; occurred_at: string; source: string; confidence: number }[];
};

const day = 86400000;
const iso = (d: number) => new Date(Date.now() - d * day).toISOString();

// API'ye ulaşılamazsa gösterilen örnek veri
export const FALLBACK: Summary = {
  name: 'Moda', district: 'Kadıköy', level: 'Hafif tedbirli', score: 1.5,
  by_time: [0, 0, 0, 2, 1, 0], sample_data: true,
  events: [
    { kind: 'fight', occurred_at: iso(3), source: 'Haber kaynağı (örnek)', confidence: 0.8 },
    { kind: 'fight', occurred_at: iso(9), source: 'Topluluk bildirimi (örnek)', confidence: 0.5 },
  ],
};

export async function fetchSummary(id = 1): Promise<{ data: Summary; live: boolean }> {
  try {
    const res = await Promise.race([
      fetch(`${API_URL}/areas/${id}/summary`),
      new Promise<never>((_, rej) => setTimeout(() => rej(new Error('timeout')), 4000)),
    ]);
    if (!res.ok) throw new Error('http');
    return { data: await res.json(), live: true };
  } catch {
    return { data: FALLBACK, live: false };
  }
}

export const KIND_TR: Record<string, string> = {
  fight: 'Kavga bildirimi', assault: 'Saldırı bildirimi', stabbing: 'Bıçaklı saldırı bildirimi',
};
export const confidenceTr = (c: number) => (c >= 0.7 ? 'yüksek' : c >= 0.5 ? 'orta' : 'düşük');
export const agoTr = (isoStr: string) => {
  const d = Math.floor((Date.now() - new Date(isoStr).getTime()) / day);
  return d <= 0 ? 'bugün' : `${d} gün önce`;
};
export const levelSegments = (level: string) =>
  ({ 'Sakin': 1, 'Hafif tedbirli': 2, 'Tedbirli': 4, 'Dikkatli ol': 5 } as Record<string, number>)[level] ?? 2;

// Sade Türkçe öneri ve seviye rengi
export const adviceTr = (level: string) =>
  ({
    'Sakin': 'Rahatça gezebilirsin. Her zamanki önlemlerin yeterli.',
    'Hafif tedbirli': 'Gündüz rahat gezebilirsin. Gece ara sokaklar yerine ana caddeleri tercih et.',
    'Tedbirli': 'Gece mümkünse bu bölgeden kaçın. Gerekiyorsa yalnız gitme.',
    'Dikkatli ol': 'Son zamanlarda çok sayıda olay bildirildi. Gerekmedikçe bu bölgeye gitme.',
  } as Record<string, string>)[level] ?? '';
export const levelColor = (level: string) =>
  ({ 'Sakin': '#2E9E8A', 'Hafif tedbirli': '#E8A317', 'Tedbirli': '#F07B3F', 'Dikkatli ol': '#E5484D' } as Record<string, string>)[level] ?? '#E8A317';
