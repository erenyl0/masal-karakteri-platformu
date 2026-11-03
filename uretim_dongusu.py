"""Bir temadaki her karakteri her stille bir kez üretip sonuçları CSV'ye yazar."""

import csv
import os
import time
import tkinter as tk

from sablonlar import STIL_SABITLERI, TEMALAR, komut_satirindan_tema, prompt_olustur
from uretim import MOCK_MODE, UretimHatasi, benzerlik_olc, dosya_sec, gorsel_uret

CIKTI_KLASORU = "uretim_ciktilari"
CSV_YOLU = "uretim_sonuclari.csv"


def main():
    tema_anahtari = komut_satirindan_tema()
    root = tk.Tk()
    root.withdraw()
    referans_yol = dosya_sec("Referans yüz fotoğrafını seç")
    os.makedirs(CIKTI_KLASORU, exist_ok=True)

    tema = TEMALAR[tema_anahtari]
    print(f"\nTema: {tema['goruntu_adi']} ({'mock' if MOCK_MODE else 'gerçek'} mod)\n")

    satirlar = []
    for karakter in tema["karakterler"]:
        for stil in STIL_SABITLERI:
            etiket = f"{karakter['id']}_{stil}"
            prompt = prompt_olustur(stil, tema_anahtari, karakter["id"])
            print(f"{etiket} üretiliyor...")

            baslangic = time.time()
            dosya, deneme, hata_mesaji = "", "", ""
            try:
                dosya, deneme = gorsel_uret(referans_yol, prompt, os.path.join(CIKTI_KLASORU, f"{etiket}.png"), etiket)
            except UretimHatasi as hata:
                hata_mesaji = str(hata)
            sure = round(time.time() - baslangic, 2)

            benzerlik = benzerlik_olc(referans_yol, dosya) if dosya and not MOCK_MODE else None

            satirlar.append({
                "tema": tema_anahtari,
                "karakter": karakter["id"],
                "stil": stil,
                "mod": "mock" if MOCK_MODE else "gercek",
                "deneme_sayisi": deneme,
                "sure_sn": sure,
                "benzerlik_yuzde": "" if benzerlik is None else benzerlik,
                "dosya": dosya,
                "hata": hata_mesaji,
                "prompt": prompt,
            })
            print(f"  {sure} sn" + (f", hata: {hata_mesaji}" if hata_mesaji else "") + "\n")

    with open(CSV_YOLU, "w", newline="", encoding="utf-8") as f:
        yazici = csv.DictWriter(f, fieldnames=satirlar[0].keys())
        yazici.writeheader()
        yazici.writerows(satirlar)
    print(f"Sonuçlar {CSV_YOLU} dosyasına yazıldı.")


if __name__ == "__main__":
    main()
