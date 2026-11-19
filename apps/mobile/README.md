# apps/mobile
Expo + React Native + TypeScript. Ekranlar: karşılama, harita (şimdilik çizim), bölge kartı.

## Kurulum (ilk kez, Termux)
Bu klasörde yalnızca kaynak kodlar var. Expo'nun proje dosyalarını eklemek için:
```
cd ~
npx create-expo-app@latest mobile-tmp --template blank-typescript
cp -rn mobile-tmp/. hirt-iptal/apps/mobile/
cd hirt-iptal/apps/mobile
npx expo install react-native-svg
npx expo start
```
(`cp -n` bizim `App.tsx` ve `src/` dosyalarının üzerine yazmaz.)

Telefondaki **Expo Go** ile okutup aç. API'yi ayrı bir Termux oturumunda `python dev_server.py` ile çalıştır.
API'ye ulaşamazsa uygulama örnek veriyle açılır.
