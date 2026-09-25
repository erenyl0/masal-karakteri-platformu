"""Referans yüz + masal karakteri promptuyla Gemini görsel üretimi ve yüz benzerliği ölçümü."""

import os
from io import BytesIO
import tkinter as tk
from tkinter import filedialog, simpledialog

import cv2
import PIL.Image
from deepface import DeepFace
from google import genai
from google.genai import types

MODEL_ADI = "gemini-3.1-flash-image"

STIL_SABITLERI = {
    "el_cizimi_masal": (
        "Warm-toned, hand-drawn fairy tale book illustration style, soft colored "
        "pencil texture, storybook lighting."
    ),
    "yumusak_suluboya": (
        "Soft watercolor fairy tale illustration, pastel palette, gentle brush "
        "strokes, whimsical children's book art style."
    ),
}


def dosya_sec(baslik: str) -> str:
    yol = filedialog.askopenfilename(
        title=baslik, filetypes=[("JPEG/PNG Dosyaları", "*.jpg;*.jpeg;*.png")]
    )
    if not yol:
        raise SystemExit(f"SİSTEM DURDU: '{baslik}' için dosya seçilmedi.")
    return yol


def gemini_ile_uret(client: genai.Client, referans_yol: str, karakter_rolu: str,
                     stil_anahtari: str, cikti_yolu: str) -> str | None:
    stil = STIL_SABITLERI[stil_anahtari]
    prompt = (
        f"{stil} Turn the person in the reference photo into a {karakter_rolu} "
        f"character in this exact scene style. Preserve their facial identity, "
        f"face shape, skin tone, and hair color/texture as closely as possible. "
        f"No deformed face, consistent single light direction, "
        f"resolution at least 1024x1024."
    )

    referans_goruntu = PIL.Image.open(referans_yol)

    cevap = client.models.generate_content(
        model=MODEL_ADI,
        contents=[referans_goruntu, prompt],
        config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
    )

    for part in cevap.candidates[0].content.parts:
        if part.text is not None:
            print(f"  Model notu: {part.text.strip()}")
        elif part.inline_data is not None:
            img = PIL.Image.open(BytesIO(part.inline_data.data))
            img.save(cikti_yolu)
            print(f"  Görsel kaydedildi: {cikti_yolu}")
            return cikti_yolu

    print("  UYARI: Yanıtta görsel bulunamadı.")
    return None


def benzerlik_olc(referans_yol: str, uretilen_yol: str) -> None:
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
        uzaklik = sonuc["distance"]
        benzerlik_yuzdesi = (1 - uzaklik) * 100
        durum = "BAŞARILI" if sonuc["verified"] else "BAŞARISIZ (eşik altında)"
        print(f"  Benzerlik: %{benzerlik_yuzdesi:.2f} | DeepFace kararı: {durum}")
    except Exception as e:
        print(f"  HATA: Yüz tespiti/kıyas başarısız — {e}")
        print("  Not: Stilize illüstrasyonlarda yüz tespiti bazen başarısız olur; "
              "bu durumda görseli gözle de değerlendir.")


def main():
    root = tk.Tk()
    root.withdraw()

    referans_yol = dosya_sec("Referans (orijinal) yüz fotoğrafını seç")
    karakter_rolu = simpledialog.askstring(
        "Karakter Rolü", "Karakter rolü nedir? (örn: şövalye, kraliçe, cadı)"
    ) or "şövalye"

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    print(f"\n--- {len(STIL_SABITLERI)} STİL VARYASYONU TEST EDİLİYOR ---\n")
    for stil_anahtari in STIL_SABITLERI:
        print(f"[{stil_anahtari}] üretiliyor...")
        cikti_yolu = f"uretim_{stil_anahtari}.png"
        sonuc_yolu = gemini_ile_uret(client, referans_yol, karakter_rolu, stil_anahtari, cikti_yolu)
        if sonuc_yolu:
            benzerlik_olc(referans_yol, sonuc_yolu)
        print()


if __name__ == "__main__":
    main()