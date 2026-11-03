"""Best-of-N kalite kontrolü: aynı prompt'tan birkaç görsel üretip referansa en çok benzeyeni seçer."""

import csv
import os
import tkinter as tk

from sablonlar import STIL_SABITLERI, TEMALAR, komut_satirindan_tema, prompt_olustur
from uretim import MOCK_MODE, KaliciHata, UretimHatasi, benzerlik_olc, dosya_sec, gorsel_uret

CIKTI_KLASORU = "kalite_ciktilari"
CSV_YOLU = "kalite_sonuclari.csv"
BENZERLIK_ESIGI = 60.0
KALITE_MAKS_DENEME = 3


def _skor(aday: dict) -> float:
    return float("-inf") if aday["benzerlik"] is None else aday["benzerlik"]


def en_iyisini_uret(referans_yol: str, prompt: str, cikti_taban_yolu: str, etiket: str) -> dict:
    en_iyi, son_hata = None, None
    for n in range(1, KALITE_MAKS_DENEME + 1):
        try:
            dosya, _ = gorsel_uret(referans_yol, prompt, f"{cikti_taban_yolu}_n{n}.png", f"{etiket}_n{n}")
        except KaliciHata as hata:
            print(f"  Üretim durdu: {hata}")
            son_hata = hata
            break
        except UretimHatasi as hata:
            print(f"  {n}. üretim olmadı: {hata}")
            son_hata = hata
            continue

        benzerlik = None if MOCK_MODE else benzerlik_olc(referans_yol, dosya)
        print(f"  {n}. üretim: {dosya}, benzerlik {'-' if benzerlik is None else f'%{benzerlik}'}")

        aday = {"dosya": dosya, "benzerlik": benzerlik, "kacinci": n}
        if en_iyi is None or _skor(aday) > _skor(en_iyi):
            en_iyi = aday
        if benzerlik is not None and benzerlik >= BENZERLIK_ESIGI:
            break

    if en_iyi is None:
        # hiçbiri üretilemediyse sebebi (ör. kredi bitti) çağırana iletiyoruz, web arayüzü kullanıcıya gösteriyor
        raise son_hata
    return en_iyi


def main():
    tema_anahtari = komut_satirindan_tema()
    root = tk.Tk()
    root.withdraw()
    referans_yol = dosya_sec("Referans yüz fotoğrafını seç")
    os.makedirs(CIKTI_KLASORU, exist_ok=True)

    tema = TEMALAR[tema_anahtari]
    print(f"\nTema: {tema['goruntu_adi']} | {'mock' if MOCK_MODE else 'gerçek'} mod | "
          f"en fazla {KALITE_MAKS_DENEME} üretim, eşik %{BENZERLIK_ESIGI}\n")

    satirlar = []
    for karakter in tema["karakterler"]:
        for stil in STIL_SABITLERI:
            etiket = f"{karakter['id']}_{stil}"
            print(f"{etiket}:")
            satir = {"tema": tema_anahtari, "karakter": karakter["id"], "stil": stil,
                     "mod": "mock" if MOCK_MODE else "gercek", "dosya": "", "benzerlik_yuzde": "",
                     "secilen_n": "", "esik_gecti_mi": "hayır", "durum": "", "hata": ""}

            try:
                en_iyi = en_iyisini_uret(referans_yol, prompt_olustur(stil, tema_anahtari, karakter["id"]),
                                         os.path.join(CIKTI_KLASORU, etiket), etiket)
            except UretimHatasi as hata:
                satir.update(durum="üretilemedi", hata=str(hata))
            else:
                esik_gecti = _skor(en_iyi) >= BENZERLIK_ESIGI
                satir.update(dosya=en_iyi["dosya"], secilen_n=en_iyi["kacinci"],
                             benzerlik_yuzde="" if en_iyi["benzerlik"] is None else en_iyi["benzerlik"],
                             esik_gecti_mi="evet" if esik_gecti else "hayır")
                if MOCK_MODE:
                    satir["durum"] = "mock, skor ölçülmedi"
                else:
                    satir["durum"] = "onaylandı" if esik_gecti else "insan onayı gerekli"

            satirlar.append(satir)
            print(f"  -> {satir['durum']}\n")

    with open(CSV_YOLU, "w", newline="", encoding="utf-8") as f:
        yazici = csv.DictWriter(f, fieldnames=satirlar[0].keys())
        yazici.writeheader()
        yazici.writerows(satirlar)
    print(f"Sonuçlar {CSV_YOLU} dosyasına yazıldı.")


if __name__ == "__main__":
    main()
