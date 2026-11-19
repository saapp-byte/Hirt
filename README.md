# Hırt İPTAL

Açık kaynaklı, topluluk destekli bir şehir güvenliği haritası. Haberlerden, resmi açıklamalardan ve kullanıcı bildirimlerinden olayları toplar; bir bölgenin **bu gece ve bu saatlerde** nasıl olduğunu sakin ve anlaşılır bir dille gösterir.

> Çalışma adıdır. Mağaza yayını öncesi daha nötr bir ad düşünülecek.

## İlkeler
- **Kişileri değil, olayları ve yerleri gösteririz.** Hiçbir kişi veya grup etiketlenmez.
- **Tahmini risk, kesin hüküm değil.** Her bilginin kaynağı ve güven seviyesi yanında görünür.
- **Gizlilik önce.** Konum cihazda kalır, kullanıcı bildirimleri anonim ve süreli tutulur.
- **Şeffaf algoritma.** Risk hesabı `packages/risk` içinde herkesin incelemesine açıktır.

## Yapı
| Klasör | Görev |
|---|---|
| `apps/mobile` | Expo + React Native + TypeScript istemci (Android/iOS) |
| `apps/api` | FastAPI arka uç (bölge, olay, bildirim, oylama) |
| `services/ingest` | Haber toplama, olay türü ve konum çıkarma |
| `packages/risk` | Risk skoru hesabı |
| `docs` | Mimari, veri modeli, etik ilkeler |

## Durum
Erken tasarım aşaması. MVP: tek şehir (İstanbul), haberlerden gelen olaylar harita üzerinde, bölge özeti.

## Lisans
AGPL-3.0 (öneri). Resmi lisans metnini https://www.gnu.org/licenses/agpl-3.0.txt adresinden `LICENSE` dosyasına ekleyin.
