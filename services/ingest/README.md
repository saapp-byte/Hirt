# services/ingest
Türkiye geneli haber toplama. İki kaynak türü:
- **Doğrudan RSS/Atom** (`sources.json` + keşfedilenler): gerçek haber adresi -> sayfa içi okuma (robots.txt'e uyarak) -> mahalle, saat, sokak.
- **Google Haberler** arama sorguları: yalnızca başlık; keşif ve tamamlayıcı (bağlantıları yönlendirmeli, sayfası okunmaz).

Haber **metni saklanmaz**; yalnızca çıkarılan bilgi (konum, saat, sokak, sonuç), başlık ve bağlantı tutulur. Kişi adı çıkarılmaz.

## Kurulum sırası
```
python build_gazetteer.py --all        # 81 il ilçe/mahalle (uzun; arka planda: nohup python build_gazetteer.py --all > data/gazetteer.log 2>&1 &)
python check_sources.py --apply        # RSS kaynaklarını dene, çalışmayanları devre dışı bırak
python ingest.py                       # ilk tarama (30 gün)
python discover.py --limit 40          # Google'da çıkan sitelerin kendi RSS'ini keşfet (yerel gazeteler)
```
## Günlük güncelleme
```
termux-wake-lock
nohup python ingest.py --loop-hours 6 > data/ingest.log 2>&1 &
```
İlk tur 30 gün, sonraki turlar son 3 gün. Daha önce görülen haberler atlanır (`--reprocess` ile yeniden işlenir).
Telefon arka planda kapanabilir; kalıcı çözüm bir sunucudur.

## Diğer bayraklar
`--no-google` (yalnızca doğrudan kaynaklar) · `--no-pages` (sayfa okuma) · `--max-pages 150` · `--only Ankara,34` · `--quick` · `--dry-run`

## Testler
`python test_nlp.py && python test_process.py && python test_geo.py && python test_extract.py && python test_articles.py`

## Sınırlar (bilerek)
- Konum belirsizse bir üst düzeyde kalınır; "Ankara'ya sevk edildi" gibi varış/ayrılış ekli yerler olay yeri sayılmaz.
- Mahkeme, "X yıldır aranan", "yıl önce" haberleri eski olay sayılıp elenir.
- Saat yalnızca haberde yazıyorsa ("dün gece saat 02.30", "sabah") kullanılır; yoksa yayın zamanı ve saat bilinmiyor olarak işaretlenir.
- robots.txt izin vermeyen sayfalar okunmaz (başlık/özetle devam edilir). Google Haberler akışı geliştirme içindir; üretimde izinli kaynaklar gerekir.
