"""Yüzleri tema karakterlerine eşler; kullanıcı eşlemeyi elle değiştirebilir."""


def otomatik_esle(yuzler: list[dict], karakterler: list[dict]) -> dict[str, str]:
    return {
        yuz["id"]: karakter["id"]
        for yuz, karakter in zip(yuzler, karakterler)
    }


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
