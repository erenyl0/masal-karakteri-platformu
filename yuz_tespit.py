"""Fotoğraftaki yüzleri bulur, kalite skoru hesaplar ve kırpar."""

import os

import cv2
from retinaface import RetinaFace

BULANIKLIK_ESIGI = 100.0
MIN_YUZ_PIKSEL = 80
KIRPMA_PAYI = 0.25


def yuzleri_bul(foto_yolu: str) -> list[dict]:
    sonuc = RetinaFace.detect_faces(foto_yolu)
    if not isinstance(sonuc, dict):
        return []

    goruntu = cv2.imread(foto_yolu)
    yuzler = []
    for bilgi in sonuc.values():
        x1, y1, x2, y2 = (max(int(v), 0) for v in bilgi["facial_area"])
        gri = cv2.cvtColor(goruntu[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY)
        netlik = float(cv2.Laplacian(gri, cv2.CV_64F).var())

        uyarilar = []
        if netlik < BULANIKLIK_ESIGI:
            uyarilar.append("bulanık")
        if min(x2 - x1, y2 - y1) < MIN_YUZ_PIKSEL:
            uyarilar.append("çözünürlük düşük")

        yuzler.append({
            "kutu": (x1, y1, x2, y2),
            "skor": round(float(bilgi["score"]), 3),
            "netlik": round(netlik, 1),
            "uyarilar": uyarilar,
        })

    yuzler.sort(key=lambda y: y["kutu"][0])
    for sira, yuz in enumerate(yuzler, start=1):
        yuz["id"] = f"yuz{sira}"
    return yuzler


def yuzleri_kirp(foto_yolu: str, yuzler: list[dict], klasor: str) -> None:
    os.makedirs(klasor, exist_ok=True)
    goruntu = cv2.imread(foto_yolu)
    yukseklik, genislik = goruntu.shape[:2]

    for yuz in yuzler:
        x1, y1, x2, y2 = yuz["kutu"]
        pay_x = int((x2 - x1) * KIRPMA_PAYI)
        pay_y = int((y2 - y1) * KIRPMA_PAYI)
        kirpim = goruntu[max(y1 - pay_y, 0):min(y2 + pay_y, yukseklik),
                         max(x1 - pay_x, 0):min(x2 + pay_x, genislik)]
        yuz["dosya"] = os.path.join(klasor, f"{yuz['id']}.png")
        cv2.imwrite(yuz["dosya"], kirpim)
