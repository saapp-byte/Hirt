"""Aynı olayı anlatan kayıtları uyumluluk kuralıyla birleştirme."""
RANK = {"il": 0, "ilce": 1, "mahalle": 2}
PLACE_KEYS = ("province_id", "district_id", "neighborhood_id", "lat", "lng", "precision", "label")

def compatible(a, b):
    """Aynı il ve çelişmeyen ilçe/mahalle: 'Ankara'da' ile 'Mamak'ta' aynı olay olabilir."""
    if a["province_id"] != b["province_id"]:
        return False
    for k in ("district_id", "neighborhood_id"):
        x, y = a.get(k), b.get(k)
        if x and y and x != y:
            return False
    return True

def merge_place(dst, src):
    """src daha kesin bir konum içeriyorsa dst'ye taşır."""
    if RANK[src["precision"]] > RANK[dst["precision"]]:
        for k in PLACE_KEYS:
            dst[k] = src[k]
