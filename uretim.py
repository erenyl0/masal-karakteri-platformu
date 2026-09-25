"""Görsel üretimi + retry + benzerlik ölçümü. MOCK_MODE=True iken sahte üretim yapar."""

import os
import random
import time
import tkinter as tk
from io import BytesIO
from tkinter import filedialog

import cv2
import PIL.Image
from PIL import ImageDraw

from sablonlar import TEMALAR, prompt_olustur

MODEL_ADI = "gemini-3.1-flash-image"
MOCK_MODE = True
MOCK_HATA_OLASILIGI = 0.5
MAKS_DENEME = 3
BASLANGIC_BEKLEME_SN = 2


class UretimHatasi(Exception):
    """Gemini üretim çağrısı, tüm denemelere rağmen başarısız olduğunda fırlatılır."""


def dosya_sec(baslik: str) -> str:
    yol = filedialog.askopenfilename(
        title=baslik, filetypes=[("JPEG/PNG Dosyaları", "*.jpg;*.jpeg;*.png")]
    )
    if not yol:
        raise SystemExit(f"SİSTEM DURDU: '{baslik}' için dosya seçilmedi.")
    return yol


def _mock_cagri(referans_yol: str, cikti_yolu: str, etiket: str) -> str:
    if random.random() < MOCK_HATA_OLASILIGI:
        raise UretimHatasi("MOCK: geçici üretim hatası simüle edildi")

    img = PIL.Image.open(referans_yol).convert("RGB")
    cizim = ImageDraw.Draw(img)
    cizim.rectangle([0, 0, 220, 40], fill=(0, 0, 0))
    cizim.text((10, 10), f"MOCK: {etiket}", fill=(255, 255, 255))
    img.save(cikti_yolu)
    return cikti_yolu


def _gercek_cagri(referans_yol: str, prompt: str, cikti_yolu: str) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    referans_goruntu = PIL.Image.open(referans_yol)

    cevap = client.models.generate_content(
        model=MODEL_ADI,
        contents=[referans_goruntu, prompt],
        config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
    )

    for part in cevap.candidates[0].content.parts:
        if part.inline_data is not None:
            img = PIL.Image.open(BytesIO(part.inline_data.data))
            img.save(cikti_yolu)
            return cikti_yolu

    raise UretimHatasi("Yanıtta görsel bulunamadı")


def gorsel_uret(referans_yol: str, prompt: str, cikti_yolu: str, etiket: str) -> tuple[str, int]:
    son_hata = None
    for deneme in range(1, MAKS_DENEME + 1):
        try:
            if MOCK_MODE:
                sonuc_yolu = _mock_cagri(referans_yol, cikti_yolu, etiket)
            else:
                sonuc_yolu = _gercek_cagri(referans_yol, prompt, cikti_yolu)
            return sonuc_yolu, deneme
        except Exception as hata:
            son_hata = hata
            print(f"  Deneme {deneme}/{MAKS_DENEME} başarısız: {hata}")
            if deneme < MAKS_DENEME:
                bekleme = BASLANGIC_BEKLEME_SN * (2 ** (deneme - 1))
                print(f"  {bekleme} saniye sonra tekrar denenecek...")
                time.sleep(bekleme)

    raise UretimHatasi(f"{MAKS_DENEME} deneme sonunda üretim başarısız: {son_hata}")


def benzerlik_olc(referans_yol: str, uretilen_yol: str) -> float | None:
    from deepface import DeepFace

    referans_matris = cv2.imread(referans_yol)
    uretilen_matris = cv2.imread(uretilen_yol)

    try:
        sonuc = DeepFace.verify(
            img1_path=referans_matris,
            img2_path=uretilen_matris,
            distance_metric="cosine",
            detector_backend="retinaface",
            enforce_detection=False,
        )
        return round((1 - sonuc["distance"]) * 100, 2)
    except Exception as e:
        print(f"  HATA: Yüz tespiti/kıyas başarısız — {e}")
        return None


def main():
    root = tk.Tk()
    root.withdraw()

    referans_yol = dosya_sec("Referans (orijinal) yüz fotoğrafını seç")

    tema_anahtari = "kirmizi_baslikli_kiz"
    karakter = TEMALAR[tema_anahtari]["karakterler"][0]
    stil_anahtari = "el_cizimi_masal"
    etiket = f"{karakter['id']}_{stil_anahtari}"

    prompt = prompt_olustur(stil_anahtari, tema_anahtari, karakter["id"])
    cikti_yolu = f"ornek_{etiket}.png"

    print(f"\n--- Üretiliyor: {etiket} | MOD: {'MOCK' if MOCK_MODE else 'GERÇEK'} ---\n")

    try:
        sonuc_yolu, deneme_sayisi = gorsel_uret(referans_yol, prompt, cikti_yolu, etiket)
        print(f"\nBAŞARILI ({deneme_sayisi}. denemede): {sonuc_yolu}")
    except UretimHatasi as hata:
        print(f"\nSİSTEM DURDU: {hata}")


if __name__ == "__main__":
    main()
