"""Hafta 1 fizibilite testi: tek fotoğraf ve serbest yazılan bir rolle iki stili karşılaştırır."""

import tkinter as tk
from tkinter import simpledialog

from sablonlar import ORTAK_KISITLAR, STIL_SABITLERI
from uretim import MOCK_MODE, KaliciHata, UretimHatasi, benzerlik_olc, dosya_sec, gorsel_uret


def main():
    root = tk.Tk()
    root.withdraw()
    referans_yol = dosya_sec("Referans yüz fotoğrafını seç")
    rol = simpledialog.askstring("Karakter rolü", "Hangi karakter olsun? (örn. şövalye, kraliçe, cadı)") or "şövalye"

    print(f"\n'{rol}' rolü {len(STIL_SABITLERI)} stille deneniyor ({'mock' if MOCK_MODE else 'gerçek'} mod)\n")

    skorlar = {}
    for stil, stil_tarifi in STIL_SABITLERI.items():
        prompt = (f"{stil_tarifi} Turn the person in the reference photo into a {rol} "
                  f"character in this scene style. {ORTAK_KISITLAR}")
        print(f"{stil}:")
        try:
            dosya, _ = gorsel_uret(referans_yol, prompt, f"fizibilite_{stil}.png", stil)
        except KaliciHata as hata:
            # kredi bitti ya da anahtar yoksa diğer stil de aynı hatayı alacak
            print(f"  üretim durdu: {hata}\n")
            break
        except UretimHatasi as hata:
            print(f"  üretilemedi: {hata}\n")
            continue

        skorlar[stil] = None if MOCK_MODE else benzerlik_olc(referans_yol, dosya)
        skor = skorlar[stil]
        print(f"  {dosya}, benzerlik {'-' if skor is None else f'%{skor}'}\n")

    olculen = {stil: skor for stil, skor in skorlar.items() if skor is not None}
    if olculen:
        en_iyi = max(olculen, key=olculen.get)
        print(f"Yüzü en iyi koruyan stil: {en_iyi} (%{olculen[en_iyi]})")
    elif skorlar:
        print("Görseller üretildi ama benzerlik ölçülmedi (mock mod ya da yüz bulunamadı).")


if __name__ == "__main__":
    main()
