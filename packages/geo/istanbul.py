"""İstanbul ilçeleri (yaklaşık ilçe merkezi koordinatları). Olaylar ilçe düzeyinde konumlandırılır."""

# (id, ad, enlem, boylam, ek yazımlar, belirsiz_mi)
# belirsiz_mi: özel isim olarak da kullanılan adlar (Fatih, Kartal...). Bunlar ancak "İstanbul" geçen
# ve "Fatih'te" gibi ek almış biçimde eşleşir.
_RAW = [
    (1, "Kadıköy", 40.9917, 29.0277, [], False),
    (2, "Üsküdar", 41.0226, 29.0153, [], False),
    (3, "Beşiktaş", 41.0422, 29.0067, [], False),
    (4, "Şişli", 41.0602, 28.9877, [], False),
    (5, "Beyoğlu", 41.0369, 28.9770, [], False),
    (6, "Fatih", 41.0186, 28.9497, [], True),
    (7, "Bakırköy", 40.9819, 28.8772, [], False),
    (8, "Esenyurt", 41.0343, 28.6800, [], False),
    (9, "Avcılar", 40.9792, 28.7219, [], False),
    (10, "Küçükçekmece", 41.0020, 28.7770, [], False),
    (11, "Başakşehir", 41.0930, 28.8020, [], False),
    (12, "Bağcılar", 41.0390, 28.8570, [], False),
    (13, "Güngören", 41.0220, 28.8720, [], False),
    (14, "Esenler", 41.0430, 28.8760, [], False),
    (15, "Bayrampaşa", 41.0470, 28.9120, [], False),
    (16, "Zeytinburnu", 40.9900, 28.9020, [], False),
    (17, "Gaziosmanpaşa", 41.0620, 28.9150, [], False),
    (18, "Eyüpsultan", 41.0480, 28.9330, ["Eyüp"], False),
    (19, "Kağıthane", 41.0850, 28.9720, ["Kâğıthane"], False),
    (20, "Sarıyer", 41.1680, 29.0500, [], False),
    (21, "Beykoz", 41.1300, 29.1000, [], False),
    (22, "Ümraniye", 41.0165, 29.1240, [], False),
    (23, "Ataşehir", 40.9830, 29.1270, [], False),
    (24, "Maltepe", 40.9350, 29.1310, [], False),
    (25, "Kartal", 40.9070, 29.1870, [], True),
    (26, "Pendik", 40.8760, 29.2330, [], False),
    (27, "Tuzla", 40.8160, 29.3030, [], False),
    (28, "Sancaktepe", 41.0020, 29.2300, [], False),
    (29, "Sultanbeyli", 40.9660, 29.2650, [], False),
    (30, "Çekmeköy", 41.0330, 29.1780, [], False),
    (31, "Sultangazi", 41.1070, 28.8670, [], False),
    (32, "Arnavutköy", 41.1850, 28.7400, [], False),
    (33, "Beylikdüzü", 41.0020, 28.6420, [], False),
    (34, "Büyükçekmece", 41.0200, 28.5850, [], False),
    (35, "Çatalca", 41.1430, 28.4600, [], False),
    (36, "Silivri", 41.0740, 28.2480, [], False),
    (37, "Şile", 41.1750, 29.6120, [], True),
    (38, "Adalar", 40.8760, 29.0910, [], True),
    (39, "Bahçelievler", 40.9980, 28.8600, [], False),
]

DISTRICTS = [
    {"id": i, "name": n, "lat": la, "lng": lo, "aliases": al, "ambiguous": amb}
    for i, n, la, lo, al, amb in _RAW
]
BY_ID = {d["id"]: d for d in DISTRICTS}
