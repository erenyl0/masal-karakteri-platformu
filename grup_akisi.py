"""Grup fotoğrafından masal sahnesi: yüz tespiti, eşleme, üretim + kalite kontrol, kompozisyon."""

import os
import tkinter as tk

from eslestirme import otomatik_esle
from kalite_kontrol import en_iyisini_uret
from kompozisyon import sahne_olustur
from sablonlar import TEMALAR, komut_satirindan_tema, prompt_olustur
from uretim import MOCK_MODE, dosya_sec
from yuz_tespit import yuzleri_bul, yuzleri_kirp

STIL = "el_cizimi_masal"
KIRPIM_KLASORU = "yuz_kirpimlari"
CIKTI_KLASORU = "sahne_ciktilari"


def sahne_uret(foto_yolu: str, tema_anahtari: str, eslesme: dict[str, str] | None = None) -> str | None:
    karakterler = {k["id"]: k for k in TEMALAR[tema_anahtari]["karakterler"]}

    yuzler = yuzleri_bul(foto_yolu)
    if not yuzler:
        print("Fotoğrafta yüz bulunamadı.")
        return None

    print(f"{len(yuzler)} yüz bulundu:")
    for yuz in yuzler:
        ek = f" ({', '.join(yuz['uyarilar'])}, daha iyi bir fotoğraf denenebilir)" if yuz["uyarilar"] else ""
        print(f"  {yuz['id']}: netlik {yuz['netlik']}, eğim {yuz['egim']}°{ek}")

    yuzleri_kirp(foto_yolu, yuzler, KIRPIM_KLASORU)
    if eslesme is None:
        eslesme = otomatik_esle(yuzler, list(karakterler.values()))

    disarida = [yuz["id"] for yuz in yuzler if yuz["id"] not in eslesme]
    if disarida:
        print(f"Karakter kalmadığı için sahneye girmeyenler: {', '.join(disarida)}")

    os.makedirs(CIKTI_KLASORU, exist_ok=True)
    parcalar = []
    for yuz in yuzler:
        karakter_id = eslesme.get(yuz["id"])
        if karakter_id is None:
            continue

        etiket = f"{yuz['id']}_{karakter_id}"
        print(f"\n{etiket}:")
        en_iyi = en_iyisini_uret(yuz["dosya"], prompt_olustur(STIL, tema_anahtari, karakter_id),
                                 os.path.join(CIKTI_KLASORU, etiket), etiket)
        if en_iyi:
            parcalar.append((en_iyi["dosya"], karakterler[karakter_id]["rol"]))
        else:
            print(f"  {etiket} üretilemedi, sahneye eklenmeyecek")

    if not parcalar:
        print("Hiçbir karakter üretilemedi, sahne oluşmadı.")
        return None
    return sahne_olustur(parcalar, os.path.join(CIKTI_KLASORU, "sahne.png"))


def main():
    tema_anahtari = komut_satirindan_tema()
    root = tk.Tk()
    root.withdraw()
    foto_yolu = dosya_sec("Grup fotoğrafını seç")

    print(f"\nTema: {TEMALAR[tema_anahtari]['goruntu_adi']} ({'mock' if MOCK_MODE else 'gerçek'} mod)\n")
    sahne = sahne_uret(foto_yolu, tema_anahtari)
    if sahne:
        print(f"\nSahne hazır: {sahne}")


if __name__ == "__main__":
    main()
