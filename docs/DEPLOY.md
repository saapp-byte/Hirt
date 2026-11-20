# Yayına alma (herkesin kullanabilmesi için)

Sistem tek bir **sunucuda** çalışır: API + haber tarama + konum veritabanı. Kullanıcıların telefonu yalnızca sonuçları çeker; hiçbir veri indirmez.

## Maliyet (Kasım 2026'da doğrulandı, değişebilir)
Render "Starter" web servisi (her zaman açık) ≈ 7 $/ay + 1 GB kalıcı disk ≈ 0,25 $/ay. Ücretsiz plan 15 dk boşta kalınca uyur ve disk bağlayamaz; bu proje için uygun değildir.

## 1) Kodu GitHub'a gönder (Termux)
```
cd ~/hirt-iptal
unzip -o ~/storage/downloads/guncelleme-9.zip
git add .
git commit -m "Sunucu hazirligi"
git push
```
## 2) Render'da sunucuyu kur (telefon tarayıcısından)
1. render.com → GitHub ile giriş.
2. New → **Blueprint** → `saapp-byte/Hirt` deposunu seç → Apply (`render.yaml` her şeyi tanımlar; ödeme kartı istenir).
3. Kurulum bitince servis adresi görünür: `https://hirt-api-xxxx.onrender.com`
4. Tarayıcıda `ADRES/status` aç: konum veritabanı ilerlemesi (`yuklenen_il`/81), olay sayısı ve son tarama zamanı orada görünür.
İlk günlerde: konum veritabanı birkaç saatte tamamlanır, ilk haber taraması 20-30 dk sürer, sonra her 3 saatte bir kendiliğinden yenilenir.

## 3) Uygulamayı APK yap (Termux, derleme bulutta olur)
```
cd ~/hirt-iptal/apps/mobile
python prepare_build.py
sed -i 's#https://CHANGE-ME.onrender.com#https://SUNUCU-ADRESIN#' eas.json
npm install -g eas-cli
eas login
eas build -p android --profile preview
```
Derleme bitince indirme bağlantısı verir; APK'yı paylaşabilirsin. (Expo Go ile denemek için: `EXPO_PUBLIC_API_URL=https://SUNUCU-ADRESIN npx expo start`)

## Yayın öncesi kalanlar
LICENSE, gizlilik politikası/KVKK, nötr uygulama adı, OSM ve haber kaynağı atıfları, Google Haberler yerine izinli kaynaklar, Play Store hesabı.
