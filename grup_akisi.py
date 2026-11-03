"""Grup fotoğrafından masal sahnesi: yüz tespiti, eşleme, üretim + kalite kontrol, kompozisyon."""

import os
import tkinter as tk

from eslestirme import otomatik_esle
from kalite_kontrol import en_iyisini_uret
from kompozisyon import sahne_olustur
from sablonlar import TEMALAR, komut_satirindan_tema, prompt_olustur
from uretim import MOCK_MODE, UretimHatasi, dosya_sec
from yuz_tespit import yas_cinsiyet_tahmin_et, yuzleri_bul, yuzleri_kirp

STIL = "el_cizimi_masal"


def yuzleri_hazirla(foto_yolu: str, klasor: str) -> list[dict]:
    yuzler = yuzleri_bul(foto_yolu)
    if yuzler:
        yuzleri_kirp(foto_yolu, yuzler, klasor)
        yas_cinsiyet_tahmin_et(yuzler)
    return yuzler


def sahne_uret(yuzler: list[dict], tema_anahtari: str, eslesme: dict[str, str], klasor: str,
               ilerleme=None) -> tuple[str, list[str]]:
    karakterler = {k["id"]: k for k in TEMALAR[tema_anahtari]["karakterler"]}
    secilenler = [yuz for yuz in yuzler if yuz["id"] in eslesme]
    os.makedirs(klasor, exist_ok=True)

    parcalar, eksikler, hatalar = [], [], []
    for sira, yuz in enumerate(secilenler):
        karakter = karakterler[eslesme[yuz["id"]]]
        if ilerleme:
            ilerleme(sira, len(secilenler), f"{karakter['ad']} çiziliyor")

        etiket = f"{yuz['id']}_{karakter['id']}"
        print(f"\n{etiket}:")
        try:
            en_iyi = en_iyisini_uret(yuz["dosya"], prompt_olustur(STIL, tema_anahtari, karakter["id"]),
                                     os.path.join(klasor, etiket), etiket)
        except UretimHatasi as hata:
            print(f"  {etiket} üretilemedi, sahneye eklenmeyecek")
            eksikler.append(karakter["ad"])
            hatalar.append(str(hata))
            continue
        parcalar.append((en_iyi["dosya"], karakter["ad"]))

    if not parcalar:
        # aynı sebep (ör. kredi bitti) her kişide tekrarlanmasın diye mesajları tekilleştiriyoruz
        raise UretimHatasi("Hiçbir karakter üretilemedi: " + " | ".join(dict.fromkeys(hatalar)))
    if ilerleme:
        ilerleme(len(secilenler), len(secilenler), "sahne birleştiriliyor")
    return sahne_olustur(parcalar, os.path.join(klasor, "sahne.png")), eksikler


def main():
    tema_anahtari = komut_satirindan_tema()
    root = tk.Tk()
    root.withdraw()
    foto_yolu = dosya_sec("Grup fotoğrafını seç")

    print(f"\nTema: {TEMALAR[tema_anahtari]['goruntu_adi']} ({'mock' if MOCK_MODE else 'gerçek'} mod)\n")
    yuzler = yuzleri_hazirla(foto_yolu, "yuz_kirpimlari")
    if not yuzler:
        print("Fotoğrafta yüz bulunamadı.")
        return

    eslesme = otomatik_esle(yuzler, TEMALAR[tema_anahtari]["karakterler"])
    print(f"{len(yuzler)} yüz bulundu:")
    for yuz in yuzler:
        tahmin = f", tahmini yaş {yuz['yas']}, kadın %{yuz['kadin_olasiligi'] * 100:.0f}" if "yas" in yuz else ""
        ek = f" ({', '.join(yuz['uyarilar'])}, daha iyi bir fotoğraf denenebilir)" if yuz["uyarilar"] else ""
        print(f"  {yuz['id']}: netlik {yuz['netlik']}, eğim {yuz['egim']}°{tahmin}{ek}"
              f" -> {eslesme.get(yuz['id'], 'karakter kalmadı')}")

    try:
        sahne, eksikler = sahne_uret(yuzler, tema_anahtari, eslesme, "sahne_ciktilari")
    except UretimHatasi as hata:
        print(f"\nSahne oluşmadı. {hata}")
        return
    print(f"\nSahne hazır: {sahne}")
    if eksikler:
        print(f"Üretilemediği için sahnede olmayan karakterler: {', '.join(eksikler)}")


if __name__ == "__main__":
    main()
