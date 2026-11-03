"""Grup fotoğrafından uçtan uca masal sahnesi: tespit, eşleme, üretim, kompozisyon."""

import os
import tkinter as tk
from tkinter import filedialog

from eslestirme import otomatik_esle
from kompozisyon import sahne_olustur
from sablonlar import TEMALAR, komut_satirindan_tema, prompt_olustur
from uretim import MOCK_MODE, UretimHatasi, gorsel_uret
from yuz_tespit import yuzleri_bul, yuzleri_kirp

TEMA_ANAHTARI = komut_satirindan_tema()
STIL_ANAHTARI = "el_cizimi_masal"
KIRPIM_KLASORU = "yuz_kirpimlari"
CIKTI_KLASORU = "sahne_ciktilari"


def sahne_uret(foto_yolu: str, eslesme_degistir=None) -> str | None:
    tema = TEMALAR[TEMA_ANAHTARI]
    yuzler = yuzleri_bul(foto_yolu)
    if not yuzler:
        print("Fotoğrafta yüz bulunamadı.")
        return None

    print(f"{len(yuzler)} yüz bulundu:")
    for yuz in yuzler:
        uyari = f" | UYARI: {', '.join(yuz['uyarilar'])}" if yuz["uyarilar"] else ""
        print(f"  {yuz['id']}: netlik {yuz['netlik']}{uyari}")

    yuzleri_kirp(foto_yolu, yuzler, KIRPIM_KLASORU)
    eslesme = otomatik_esle(yuzler, tema["karakterler"])
    if eslesme_degistir:
        eslesme = eslesme_degistir(eslesme)

    if len(yuzler) > len(eslesme):
        print(f"UYARI: {len(yuzler) - len(eslesme)} yüz için karakter slotu kalmadı.")

    os.makedirs(CIKTI_KLASORU, exist_ok=True)
    parcalar = []
    for yuz in yuzler:
        karakter_id = eslesme.get(yuz["id"])
        if karakter_id is None:
            continue

        karakter = next(k for k in tema["karakterler"] if k["id"] == karakter_id)
        etiket = f"{yuz['id']}_{karakter_id}"
        prompt = prompt_olustur(STIL_ANAHTARI, TEMA_ANAHTARI, karakter_id)
        cikti_yolu = os.path.join(CIKTI_KLASORU, f"{etiket}.png")

        print(f"[{etiket}] üretiliyor...")
        try:
            sonuc_yolu, _ = gorsel_uret(yuz["dosya"], prompt, cikti_yolu, etiket)
            parcalar.append((sonuc_yolu, karakter["rol"]))
        except UretimHatasi as hata:
            print(f"  {etiket} atlandı: {hata}")

    if not parcalar:
        print("Hiçbir karakter üretilemedi, sahne oluşturulmadı.")
        return None

    return sahne_olustur(parcalar, os.path.join(CIKTI_KLASORU, "sahne.png"))


def main():
    root = tk.Tk()
    root.withdraw()

    foto_yolu = filedialog.askopenfilename(
        title="Grup fotoğrafını seç", filetypes=[("JPEG/PNG Dosyaları", "*.jpg;*.jpeg;*.png")]
    )
    if not foto_yolu:
        raise SystemExit("SİSTEM DURDU: fotoğraf seçilmedi.")

    print(f"\n--- GRUP SAHNESİ | MOD: {'MOCK' if MOCK_MODE else 'GERÇEK'} ---\n")
    sonuc = sahne_uret(foto_yolu)
    print(f"\nSahne: {sonuc}" if sonuc else "\nSahne oluşturulamadı.")


if __name__ == "__main__":
    main()
