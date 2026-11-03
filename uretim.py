"""Tek görsel üretimi (hata olursa tekrar dener) ve üretilen görselin referans yüze benzerliği."""

import base64
import io
import os
import random
import time
import tkinter as tk
from tkinter import filedialog

import cv2
import numpy as np
from PIL import ImageDraw

from sablonlar import TEMALAR, prompt_olustur
from yuz_tespit import foto_ac

MODEL_ADI = "gpt-image-1"
MOCK_MODE = True  # API anahtarı ya da kredi yokken True kalsın
MOCK_HATA_OLASILIGI = 0.2
MAKS_DENEME = 3
BASLANGIC_BEKLEME_SN = 2


class UretimHatasi(Exception):
    pass


class KaliciHata(UretimHatasi):
    """Tekrar denemenin işe yaramayacağı hata: anahtar yok, kredi bitti, istek reddedildi."""


def dosya_sec(baslik: str) -> str:
    yol = filedialog.askopenfilename(title=baslik, filetypes=[("Fotoğraflar", "*.jpg;*.jpeg;*.png")])
    if not yol:
        raise SystemExit("Dosya seçilmedi, çıkılıyor.")
    return yol


def goruntu_oku(yol: str) -> np.ndarray:
    # cv2.imread Windows'ta Türkçe karakterli yolları açamıyor, o yüzden PIL ile okuyoruz
    return cv2.cvtColor(np.array(foto_ac(yol)), cv2.COLOR_RGB2BGR)


def _mock_cagri(referans_yol: str, cikti_yolu: str, etiket: str) -> str:
    if random.random() < MOCK_HATA_OLASILIGI:
        raise UretimHatasi("mock: geçici hata")

    img = foto_ac(referans_yol)
    cizim = ImageDraw.Draw(img)
    cizim.rectangle([0, 0, 220, 40], fill=(0, 0, 0))
    cizim.text((10, 10), f"MOCK: {etiket}", fill=(255, 255, 255))
    img.save(cikti_yolu)
    return cikti_yolu


def _gercek_cagri(referans_yol: str, prompt: str, cikti_yolu: str) -> str:
    import openai

    anahtar = os.environ.get("OPENAI_API_KEY")
    if not anahtar:
        raise KaliciHata('OPENAI_API_KEY tanımlı değil. Terminalde $env:OPENAI_API_KEY="sk-..." ile tanımla.')

    tampon = io.BytesIO()
    foto_ac(referans_yol).save(tampon, "JPEG", quality=95)

    client = openai.OpenAI(api_key=anahtar)
    try:
        # input_fidelity="high": model referanstaki yüz hatlarına daha sadık kalıyor
        cevap = client.images.edit(model=MODEL_ADI, image=("referans.jpg", tampon.getvalue(), "image/jpeg"),
                                   prompt=prompt, size="1024x1024", input_fidelity="high")
    except (openai.AuthenticationError, openai.PermissionDeniedError, openai.BadRequestError,
            openai.NotFoundError) as hata:
        raise KaliciHata(f"istek reddedildi: {hata.message}") from hata
    except openai.RateLimitError as hata:
        if hata.type == "insufficient_quota":
            raise KaliciHata("hesapta kredi kalmamış, platform.openai.com üzerinden yüklemek gerekiyor") from hata
        raise

    kodlanmis = cevap.data[0].b64_json
    if not kodlanmis:
        raise UretimHatasi("yanıtta görsel yok")

    with open(cikti_yolu, "wb") as dosya:
        dosya.write(base64.b64decode(kodlanmis))
    return cikti_yolu


def gorsel_uret(referans_yol: str, prompt: str, cikti_yolu: str, etiket: str) -> tuple[str, int]:
    for deneme in range(1, MAKS_DENEME + 1):
        try:
            if MOCK_MODE:
                return _mock_cagri(referans_yol, cikti_yolu, etiket), deneme
            return _gercek_cagri(referans_yol, prompt, cikti_yolu), deneme
        except KaliciHata:
            raise
        except Exception as hata:
            print(f"  {deneme}. deneme olmadı: {hata}")
            if deneme == MAKS_DENEME:
                raise UretimHatasi(f"{MAKS_DENEME} denemede de üretilemedi ({hata})") from hata
            bekleme = BASLANGIC_BEKLEME_SN * 2 ** (deneme - 1)
            print(f"  {bekleme} sn bekleyip tekrar deniyorum...")
            time.sleep(bekleme)


def benzerlik_olc(referans_yol: str, uretilen_yol: str) -> float | None:
    from deepface import DeepFace

    try:
        sonuc = DeepFace.verify(
            img1_path=goruntu_oku(referans_yol),
            img2_path=goruntu_oku(uretilen_yol),
            distance_metric="cosine",
            detector_backend="retinaface",
            enforce_detection=False,
        )
    except Exception as hata:
        print(f"  Benzerlik ölçülemedi: {hata}")
        return None
    return round((1 - sonuc["distance"]) * 100, 2)


def main():
    root = tk.Tk()
    root.withdraw()
    referans_yol = dosya_sec("Referans yüz fotoğrafını seç")

    tema = "kirmizi_baslikli_kiz"
    karakter_id = TEMALAR[tema]["karakterler"][0]["id"]
    stil = "el_cizimi_masal"
    etiket = f"{karakter_id}_{stil}"

    print(f"\n{etiket} üretiliyor ({'mock' if MOCK_MODE else 'gerçek'} mod)\n")
    try:
        yol, deneme = gorsel_uret(referans_yol, prompt_olustur(stil, tema, karakter_id), f"ornek_{etiket}.png", etiket)
        print(f"\nTamam, {deneme}. denemede üretildi: {yol}")
    except UretimHatasi as hata:
        print(f"\nÜretilemedi: {hata}")


if __name__ == "__main__":
    main()
