"""Best-of-N: aynı prompt'tan birden fazla üretip en iyi skorlu görseli seçer."""

import csv
import os
import tkinter as tk
from tkinter import filedialog

from uretim import MOCK_MODE, UretimHatasi, benzerlik_olc, gorsel_uret
from sablonlar import STIL_SABITLERI, TEMALAR, prompt_olustur

TEMA_ANAHTARI = "kirmizi_baslikli_kiz"
CIKTI_KLASORU = "kalite_ciktilari"
CSV_YOLU = "kalite_sonuclari.csv"
BENZERLIK_ESIGI = 60.0
KALITE_MAKS_DENEME = 3


def dosya_sec(baslik: str) -> str:
    yol = filedialog.askopenfilename(
        title=baslik, filetypes=[("JPEG/PNG Dosyaları", "*.jpg;*.jpeg;*.png")]
    )
    if not yol:
        raise SystemExit(f"SİSTEM DURDU: '{baslik}' için dosya seçilmedi.")
    return yol


def en_iyisini_uret(referans_yol: str, prompt: str, cikti_taban_yolu: str, etiket: str) -> dict | None:
    en_iyi = None

    for n in range(1, KALITE_MAKS_DENEME + 1):
        cikti_yolu = f"{cikti_taban_yolu}_n{n}.png"
        try:
            sonuc_yolu, uretim_deneme_sayisi = gorsel_uret(referans_yol, prompt, cikti_yolu, f"{etiket}_n{n}")
        except UretimHatasi as hata:
            print(f"  [n={n}] üretim başarısız: {hata}")
            continue

        benzerlik = benzerlik_olc(referans_yol, sonuc_yolu) if not MOCK_MODE else None
        gosterge = f"%{benzerlik:.2f}" if benzerlik is not None else "ölçülmedi (mock)"
        print(f"  [n={n}] üretildi: {sonuc_yolu} | benzerlik: {gosterge}")

        aday = {
            "dosya": sonuc_yolu,
            "benzerlik": benzerlik,
            "en_iyi_n": n,
            "uretim_deneme_sayisi": uretim_deneme_sayisi,
        }
        if en_iyi is None or (benzerlik or -1) > (en_iyi["benzerlik"] or -1):
            en_iyi = aday

        if benzerlik is not None and benzerlik >= BENZERLIK_ESIGI:
            break

    return en_iyi


def main():
    root = tk.Tk()
    root.withdraw()

    referans_yol = dosya_sec("Referans (orijinal) yüz fotoğrafını seç")
    os.makedirs(CIKTI_KLASORU, exist_ok=True)

    tema = TEMALAR[TEMA_ANAHTARI]
    satirlar = []

    print(f"\n--- TEMA: {tema['goruntu_adi']} | MOD: {'MOCK' if MOCK_MODE else 'GERÇEK'} "
          f"| Best-of-{KALITE_MAKS_DENEME} | Eşik: %{BENZERLIK_ESIGI} ---\n")

    for karakter in tema["karakterler"]:
        for stil_anahtari in STIL_SABITLERI:
            karakter_id = karakter["id"]
            etiket = f"{karakter_id}_{stil_anahtari}"
            prompt = prompt_olustur(stil_anahtari, TEMA_ANAHTARI, karakter_id)
            cikti_taban_yolu = os.path.join(CIKTI_KLASORU, etiket)

            print(f"[{etiket}] best-of-{KALITE_MAKS_DENEME} başlıyor...")
            en_iyi = en_iyisini_uret(referans_yol, prompt, cikti_taban_yolu, etiket)

            if en_iyi is None:
                satirlar.append({
                    "tema": TEMA_ANAHTARI,
                    "karakter": karakter_id,
                    "stil": stil_anahtari,
                    "mod": "mock" if MOCK_MODE else "gercek",
                    "dosya": "",
                    "benzerlik_yuzde": "",
                    "secilen_n": "",
                    "esik_gecti_mi": "hayır",
                    "durum": "üretim tamamen başarısız",
                })
                print(f"  SONUÇ: tüm denemeler başarısız\n")
                continue

            esik_gecti = en_iyi["benzerlik"] is not None and en_iyi["benzerlik"] >= BENZERLIK_ESIGI
            durum = "onaylandı" if (MOCK_MODE or esik_gecti) else "insan onayı gerekli"

            satirlar.append({
                "tema": TEMA_ANAHTARI,
                "karakter": karakter_id,
                "stil": stil_anahtari,
                "mod": "mock" if MOCK_MODE else "gercek",
                "dosya": en_iyi["dosya"],
                "benzerlik_yuzde": en_iyi["benzerlik"] if en_iyi["benzerlik"] is not None else "",
                "secilen_n": en_iyi["en_iyi_n"],
                "esik_gecti_mi": "evet" if esik_gecti else "hayır",
                "durum": durum,
            })
            print(f"  SEÇİLEN: {en_iyi['dosya']} ({en_iyi['en_iyi_n']}. üretim) | Durum: {durum}\n")

    with open(CSV_YOLU, "w", newline="", encoding="utf-8") as f:
        yazici = csv.DictWriter(f, fieldnames=satirlar[0].keys())
        yazici.writeheader()
        yazici.writerows(satirlar)

    print(f"Tüm sonuçlar kaydedildi: {CSV_YOLU}")


if __name__ == "__main__":
    main()
