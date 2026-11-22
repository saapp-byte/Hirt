import * as Location from 'expo-location';
import { API_URL } from './api';

type Place = { id: number; level: 'il' | 'ilce'; name: string; il: string; lat: number; lng: number };
export type Found = { id: number; name: string; km: number };

const toRad = (d: number) => (d * Math.PI) / 180;
function km(aLat: number, aLng: number, bLat: number, bLng: number) {
  const dLat = toRad(bLat - aLat), dLng = toRad(bLng - aLng);
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(aLat)) * Math.cos(toRad(bLat)) * Math.sin(dLng / 2) ** 2;
  return 6371 * 2 * Math.asin(Math.sqrt(h));
}

// Telefonun konumuna en yakın ilçeyi (yoksa ili) bulur. Konum cihazdan çıkmaz: sadece yer listesi indirilir.
export async function findMyPlace(): Promise<Found | { error: string }> {
  try {
    const perm = await Location.requestForegroundPermissionsAsync();
    if (perm.status !== 'granted') return { error: 'Konum izni verilmedi. İstersen yukarıdan yeri elle seçebilirsin.' };
    const pos = (await Location.getLastKnownPositionAsync()) ?? (await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced }));
    const { latitude, longitude } = pos.coords;
    const res = await fetch(`${API_URL}/places.json`);
    if (!res.ok) throw new Error('http');
    const places: Place[] = await res.json();
    const best = (lvl: Place['level']) =>
      places.filter((p) => p.level === lvl)
        .map((p) => ({ p, d: km(latitude, longitude, p.lat, p.lng) }))
        .sort((a, b) => a.d - b.d)[0];
    // Yakında yüklenmiş bir ilçe varsa onu, yoksa en yakın ili seç
    const ilce = best('ilce');
    const pick = ilce && ilce.d <= 40 ? ilce : best('il');
    if (!pick) return { error: 'Yakında bir bölge bulunamadı.' };
    return { id: pick.p.id, name: pick.p.level === 'ilce' ? `${pick.p.name}, ${pick.p.il}` : pick.p.name, km: Math.round(pick.d) };
  } catch {
    return { error: 'Konum alınamadı. Konum özelliğinin açık olduğundan ve internetin çalıştığından emin ol.' };
  }
}
