# Yayına alma: TAMAMEN ÜCRETSİZ yol (GitHub Actions + GitHub Pages)

Sunucu kiralamaya gerek yok. Public bir repoda GitHub'ın bulutu ücretsiz çalışır:

```
GitHub Actions (her 3 saatte bir, kendiliğinden)
   ├─ 81 ilin ilçe/mahalle verisini tamamlar (her turda ~40 dk, birkaç turda biter)
   ├─ doğrudan RSS kaynaklarını + Google Haberler'i tarar, haber sayfalarını okur
   ├─ olayları çıkarır, birleştirir
   └─ statik JSON üretir → GitHub Pages'te yayınlar:  https://saapp-byte.github.io/Hirt/
Uygulama bu adresten okur (kullanıcının telefonuna veri indirilmez, Termux gerekmez).
Kalıcı durum: `data` adlı dalda tutulur (her tur tek commit olarak ezilir, repo şişmez).
```

## Bir kez yapılacaklar
**1) Kodu GitHub'a gönder (Termux):**
```
cd ~/hirt-iptal
unzip -o ~/storage/downloads/guncelleme-10.zip
git add .
git commit -m "Ucretsiz yayin hatti"
git push
```
**2) GitHub'da (telefon tarayıcısı, repo sayfası):**
- **Settings → Pages → Build and deployment → Source: "GitHub Actions"** seç.
- **Actions** sekmesi → (gerekirse "I understand my workflows, enable them") → soldan **"Haberleri güncelle ve yayınla"** → **Run workflow** → Run workflow.
- İlk tur 1-2 saat sürebilir. Bitince `https://saapp-byte.github.io/Hirt/status.json` adresini aç: konum veritabanı ilerlemesi ve olay sayısı görünür.

Sonra her 3 saatte bir kendiliğinden yenilenir.

## Uygulama
Uygulama varsayılan olarak bu adresi kullanır; Expo Go'da (`npx expo start`) ek ayar gerekmez. Başkalarına vermek için APK:
```
cd ~/hirt-iptal/apps/mobile
python prepare_build.py
npm install -g eas-cli
eas login
eas build -p android --profile preview
```
(Derleme Expo'nun bulutunda yapılır; ücretsiz planın derleme/kuyruk sınırı vardır, güncel sınırı Expo sitesinden kontrol et. APK'yı doğrudan paylaşmak ücretsizdir; Play Store ayrıca tek seferlik geliştirici ücreti ister.)

## Sınırlar (dürüstçe)
- Google Haberler, GitHub'ın paylaşımlı IP'lerine 429 verebilir. Bu durumda doğrudan RSS kaynakları (`sources.json`) ana kaynak olur; `status.json` ve Actions günlüklerinden izlenir.
- Actions tarama sonuçları 3 saatte bir yenilenir (anlık değil).
- GitHub, 60 gün hiç etkinlik olmayan public repolarda zamanlanmış çalışmaları durdurabilir; durursa Actions sekmesinden yeniden etkinleştir.
- Kalıcı durum `data` dalında olduğu için olay veritabanı herkese açıktır (zaten yayınlanan bilgiler: başlık, bağlantı, konum, saat).

## Alternatif (ücretli, ileride): `render.yaml` ile Render (~7 $/ay). Gerekirse kullanılabilir; şimdilik gerekmez.

## Yayın öncesi kalanlar
LICENSE, gizlilik politikası/KVKK, nötr uygulama adı, OSM ve haber kaynağı atıfları, Google Haberler yerine izinli kaynaklar.
