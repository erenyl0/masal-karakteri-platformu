"""Yüzleri tahmini yaş ve cinsiyete göre tema karakterlerine eşler; eşleme elle de değiştirilebilir."""

from itertools import permutations

COCUK_YAS_SINIRI = 16
YASLI_YAS_SINIRI = 55


def yas_grubu(yas: int) -> str:
    if yas < COCUK_YAS_SINIRI:
        return "cocuk"
    if yas >= YASLI_YAS_SINIRI:
        return "yasli"
    return "yetiskin"


def uygunluk(yuz: dict, karakter: dict) -> float:
    puan = 0.0
    if karakter.get("yas") and "yas" in yuz:
        puan += yas_grubu(yuz["yas"]) == karakter["yas"]
    if karakter.get("cinsiyet") and "kadin_olasiligi" in yuz:
        kadin = yuz["kadin_olasiligi"]
        puan += kadin if karakter["cinsiyet"] == "kadin" else 1 - kadin
    return puan


def otomatik_esle(yuzler: list[dict], karakterler: list[dict]) -> dict[str, str]:
    # aile fotoğraflarında kişi sayısı az, bütün dağılımları denemek yetiyor
    if len(yuzler) <= len(karakterler):
        adaylar = (list(zip(yuzler, secim)) for secim in permutations(karakterler, len(yuzler)))
    else:
        adaylar = (list(zip(secim, karakterler)) for secim in permutations(yuzler, len(karakterler)))

    en_iyi = max(adaylar, key=lambda eslesme: sum(uygunluk(y, k) for y, k in eslesme))
    return {yuz["id"]: karakter["id"] for yuz, karakter in en_iyi}


def elle_degistir(eslesme: dict[str, str], yuz_id: str, karakter_id: str) -> dict[str, str]:
    yeni = dict(eslesme)
    onceki_karakter = yeni.get(yuz_id)

    for diger_yuz, diger_karakter in eslesme.items():
        if diger_karakter == karakter_id and diger_yuz != yuz_id:
            if onceki_karakter is None:
                del yeni[diger_yuz]
            else:
                yeni[diger_yuz] = onceki_karakter

    yeni[yuz_id] = karakter_id
    return yeni
