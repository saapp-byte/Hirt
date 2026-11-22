// Veriler GitHub Pages'te statik JSON olarak yayınlanır (haber tarama GitHub Actions'ta çalışır).
// Yerel denemede: EXPO_PUBLIC_API_URL=http://localhost:8000 (apps/api/dev_server.py aynı yolları sunar).
export const API_URL = process.env.EXPO_PUBLIC_API_URL ?? 'https://saapp-byte.github.io/Hirt';

export type Ev = {
  kind: string; occurred_at: string; source: string; confidence: number;
  place?: string; precision?: string; street?: string | null;
  time_precision?: string | null; outcome?: string | null; url?: string;
};

export type Summary = {
  name: string; district: string; level: string; score: number; place_level?: string;
  by_time: number[]; sample_data: boolean; time_reliable?: boolean; window_days?: number; event_count?: number;
  events: Ev[];
};

const day = 86400000;
const iso = (d: number) => new Date(Date.now() - d * day).toISOString();

// API'ye ulaşılamazsa gösterilen örnek veri
export const FALLBACK: Summary = {
  name: 'Kadıköy', district: 'İstanbul', level: 'Hafif tedbirli', score: 1.5,
  by_time: [0, 0, 0, 2, 1, 0], sample_data: true,
  events: [
    { kind: 'fight', occurred_at: iso(3), source: 'Haber kaynağı (örnek)', confidence: 0.8 },
    { kind: 'fight', occurred_at: iso(9), source: 'Topluluk bildirimi (örnek)', confidence: 0.5 },
  ],
};

export async function fetchSummary(id = 1): Promise<{ data: Summary; live: boolean }> {
  try {
    const res = await Promise.race([
      fetch(`${API_URL}/summary/${id}.json`),
      new Promise<never>((_, rej) => setTimeout(() => rej(new Error('timeout')), 8000)),
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
const AYLAR = ['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz', 'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara'];
const pad = (n: number) => String(n).padStart(2, '0');

// Haberdeki olay zamanı. Türkiye saatiyle (UTC+3) gösterilir; saat haberde yoksa dürüstçe söylenir.
export function whenTr(e: Ev): string {
  const t = new Date(new Date(e.occurred_at).getTime() + 3 * 3600000); // UTC+3
  const date = `${t.getUTCDate()} ${AYLAR[t.getUTCMonth()]}`;
  const h = t.getUTCHours();
  if (e.time_precision === 'dakika' || e.time_precision === 'saat') return `${date} · ${pad(h)}:${pad(t.getUTCMinutes())}`;
  if (e.time_precision === 'dilim') {
    const part = h < 4 ? 'gece' : h < 6 ? 'sabaha karşı' : h < 11 ? 'sabah' : h < 14 ? 'öğle' : h < 18 ? 'öğleden sonra' : h < 23 ? 'akşam' : 'gece';
    return `${date} · ${part} (yaklaşık)`;
  }
  return `${date} · saati haberde yok`;
}
export const outcomeTr = (o?: string | null) =>
  o === 'died' ? 'Haberde ölüm bildirilmiş' : o === 'injured' ? 'Haberde yaralanma bildirilmiş' : null;

export const confidenceTr = (c: number) => (c >= 0.7 ? 'yüksek' : c >= 0.5 ? 'orta' : 'düşük');
export const agoTr = (isoStr: string) => {
  const d = Math.floor((Date.now() - new Date(isoStr).getTime()) / day);
  return d <= 0 ? 'bugün' : `${d} gün önce`;
};
export const levelSegments = (level: string) =>
  ({ 'Sakin': 1, 'Hafif tedbirli': 2, 'Tedbirli': 4, 'Dikkatli ol': 5, 'Kayıt yok': 0 } as Record<string, number>)[level] ?? 2;

// Sade Türkçe öneri ve seviye rengi
export const adviceTr = (level: string) =>
  ({
    'Sakin': 'Rahatça gezebilirsin. Her zamanki önlemlerin yeterli.',
    'Hafif tedbirli': 'Gündüz rahat gezebilirsin. Gece ara sokaklar yerine ana caddeleri tercih et.',
    'Tedbirli': 'Gece mümkünse bu bölgeden kaçın. Gerekiyorsa yalnız gitme.',
    'Dikkatli ol': 'Son zamanlarda çok sayıda olay bildirildi. Gerekmedikçe bu bölgeye gitme.',
    'Kayıt yok': 'Tarama sonucunda bu bölge için son 30 günde kayıt bulunamadı. Uygulama sınırlı sayıda haberi tarar; bu, bölgede olay olmadığı anlamına gelmez. Çevrene her zaman dikkat et.',
  } as Record<string, string>)[level] ?? '';
export const levelColor = (level: string) =>
  ({ 'Sakin': '#2E9E8A', 'Hafif tedbirli': '#E8A317', 'Tedbirli': '#F07B3F', 'Dikkatli ol': '#E5484D', 'Kayıt yok': '#8A8599' } as Record<string, string>)[level] ?? '#E8A317';

export type Area = { id: number; name: string; level: string; score: number; count: number; sample_data: boolean };

export async function fetchAreas(parent?: number): Promise<Area[]> {
  try {
    const res = await Promise.race([
      fetch(parent ? `${API_URL}/areas/${parent}.json` : `${API_URL}/areas.json`),
      new Promise<never>((_, rej) => setTimeout(() => rej(new Error('timeout')), 8000)),
    ]);
    if (!res.ok) throw new Error('http');
    return await res.json();
  } catch {
    return [];
  }
}
