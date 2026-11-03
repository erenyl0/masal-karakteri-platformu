"""Bir temadaki tüm karakter x stil kombinasyonlarını üretip CSV'ye loglar."""

import csv
import os
import time
import tkinter as tk
from tkinter import filedialog

from uretim import MOCK_MODE, UretimHatasi, benzerlik_olc, gorsel_uret
from sablonlar import STIL_SABITLERI, TEMALAR, komut_satirindan_tema, prompt_olustur

TEMA_ANAHTARI = komut_satirindan_tema()
CIKTI_KLASORU = "uretim_ciktilari"
CSV_YOLU = "uretim_sonuclari.csv"


def dosya_sec(baslik: str) -> str:
    yol = filedialog.askopenfilename(
        title=baslik, filetypes=[("JPEG/PNG Dosyaları", "*.jpg;*.jpeg;*.png")]
    )
    if not yol:
        raise SystemExit(f"SİSTEM DURDU: '{baslik}' için dosya seçilmedi.")
    return yol


def main():
    root = tk.Tk()
    root.withdraw()

    referans_yol = dosya_sec("Referans (orijinal) yüz fotoğrafını seç")
    os.makedirs(CIKTI_KLASORU, exist_ok=True)

    tema = TEMALAR[TEMA_ANAHTARI]
    satirlar = []

    print(f"\n--- TEMA: {tema['goruntu_adi']} | MOD: {'MOCK' if MOCK_MODE else 'GERÇEK'} ---\n")

    for karakter in tema["karakterler"]:
        for stil_anahtari in STIL_SABITLERI:
            karakter_id = karakter["id"]
            etiket = f"{karakter_id}_{stil_anahtari}"
            prompt = prompt_olustur(stil_anahtari, TEMA_ANAHTARI, karakter_id)
            cikti_yolu = os.path.join(CIKTI_KLASORU, f"{etiket}.png")

            print(f"[{etiket}] üretiliyor...")
            baslangic = time.time()

            try:
                sonuc_yolu, deneme_sayisi = gorsel_uret(referans_yol, prompt, cikti_yolu, etiket)
                hata_mesaji = ""
            except UretimHatasi as hata:
                sonuc_yolu, deneme_sayisi = None, None
                hata_mesaji = str(hata)

            sure = round(time.time() - baslangic, 2)

            benzerlik = None
            if sonuc_yolu and not MOCK_MODE:
                benzerlik = benzerlik_olc(referans_yol, sonuc_yolu)

            satirlar.append({
                "tema": TEMA_ANAHTARI,
                "karakter": karakter_id,
                "stil": stil_anahtari,
                "mod": "mock" if MOCK_MODE else "gercek",
                "deneme_sayisi": deneme_sayisi if deneme_sayisi is not None else "",
                "sure_sn": sure,
                "benzerlik_yuzde": benzerlik if benzerlik is not None else "",
                "dosya": sonuc_yolu or "",
                "hata": hata_mesaji,
                "prompt": prompt,
            })
            print(f"  Süre: {sure} sn | Dosya: {sonuc_yolu}\n")

    with open(CSV_YOLU, "w", newline="", encoding="utf-8") as f:
        yazici = csv.DictWriter(f, fieldnames=satirlar[0].keys())
        yazici.writeheader()
        yazici.writerows(satirlar)

    print(f"Tüm sonuçlar kaydedildi: {CSV_YOLU}")


if __name__ == "__main__":
    main()
