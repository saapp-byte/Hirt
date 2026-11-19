# Mimari

```
Haber/RSS/resmi kaynaklar -> services/ingest -> PostgreSQL + PostGIS <- apps/api <- apps/mobile
                                   |                                       ^
                                   +--> packages/risk (skor hesabı) -------+
```

## Akış
1. **Toplama:** `ingest` kaynakları periyodik tarar.
2. **Ayıklama:** Haberden olay türü (kavga, bıçaklama, saldırı...) ve konum çıkarılır, Nominatim/OSM ile koordinata çevrilir.
3. **Tekilleştirme:** Aynı olayı anlatan haberler birleştirilir.
4. **Skor:** `risk` bölge ve saat dilimi bazında tahmini risk üretir.
5. **Sunum:** `api` bölge özetini verir, `mobile` haritada gösterir.

## Teknoloji
- Mobil: Expo (React Native, TypeScript), harita için MapLibre (geliştirme build'i gerekir, Expo Go yetmez)
- API: Python, FastAPI
- Veri: PostgreSQL + PostGIS
- Harita altlığı: OpenStreetMap tabanlı vektör karolar

## Sonraki aşamalar
Topluluk oylaması ve "şu an var/yok" bildirimleri: hesap doğrulama, hız sınırı ve eşik kuralları hazır olunca eklenir.
