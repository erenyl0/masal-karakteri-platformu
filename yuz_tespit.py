"""Fotoğraftaki yüzleri bulur, kalitesini kontrol eder, gözleri yatay olacak şekilde hizalayıp kırpar."""

import math
import os

import cv2
import numpy as np
import PIL.Image

BULANIKLIK_ESIGI = 100.0
NETLIK_OLCUM_GENISLIGI = 256
MIN_YUZ_PIKSEL = 80
PROFIL_ESIGI = 0.35
KIRPMA_PAYI = 0.25


def _egim_ve_profil(landmarks: dict) -> tuple[float, float]:
    sol, sag = sorted([landmarks["right_eye"], landmarks["left_eye"]], key=lambda nokta: nokta[0])
    dx, dy = sag[0] - sol[0], sag[1] - sol[1]
    egim = math.degrees(math.atan2(dy, dx))

    # burun gözlerin ortasından ne kadar kaymışsa yüz o kadar yana dönük
    goz_arasi = math.hypot(dx, dy) or 1
    burun_kaymasi = abs(landmarks["nose"][0] - (sol[0] + sag[0]) / 2) / goz_arasi
    return egim, burun_kaymasi


def yuzleri_bul(foto_yolu: str) -> list[dict]:
    from retinaface import RetinaFace

    bgr = cv2.cvtColor(np.array(PIL.Image.open(foto_yolu).convert("RGB")), cv2.COLOR_RGB2BGR)
    bulunanlar = RetinaFace.detect_faces(bgr)
    if not isinstance(bulunanlar, dict):
        return []

    yuzler = []
    for bilgi in bulunanlar.values():
        x1, y1, x2, y2 = (max(int(v), 0) for v in bilgi["facial_area"])

        # Laplacian varyansı çözünürlükle değişiyor; yüzleri karşılaştırabilmek için aynı genişliğe getiriyoruz
        olcek_boy = max(1, round(NETLIK_OLCUM_GENISLIGI * (y2 - y1) / (x2 - x1)))
        olcekli = cv2.resize(bgr[y1:y2, x1:x2], (NETLIK_OLCUM_GENISLIGI, olcek_boy), interpolation=cv2.INTER_AREA)
        netlik = float(cv2.Laplacian(cv2.cvtColor(olcekli, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var())
        egim, burun_kaymasi = _egim_ve_profil(bilgi["landmarks"])

        uyarilar = []
        if netlik < BULANIKLIK_ESIGI:
            uyarilar.append("bulanık")
        if min(x2 - x1, y2 - y1) < MIN_YUZ_PIKSEL:
            uyarilar.append("çok küçük")
        if burun_kaymasi > PROFIL_ESIGI:
            uyarilar.append("yandan çekilmiş")

        yuzler.append({
            "kutu": (x1, y1, x2, y2),
            "netlik": round(netlik, 1),
            "egim": round(egim, 1),
            "uyarilar": uyarilar,
        })

    yuzler.sort(key=lambda yuz: yuz["kutu"][0])
    for sira, yuz in enumerate(yuzler, start=1):
        yuz["id"] = f"yuz{sira}"
    return yuzler


def yuzleri_kirp(foto_yolu: str, yuzler: list[dict], klasor: str) -> None:
    os.makedirs(klasor, exist_ok=True)
    foto = PIL.Image.open(foto_yolu).convert("RGB")

    for yuz in yuzler:
        x1, y1, x2, y2 = yuz["kutu"]
        duz = foto.rotate(yuz["egim"], center=((x1 + x2) / 2, (y1 + y2) / 2), resample=PIL.Image.BICUBIC)

        pay_x = int((x2 - x1) * KIRPMA_PAYI)
        pay_y = int((y2 - y1) * KIRPMA_PAYI)
        kirpim = duz.crop((max(x1 - pay_x, 0), max(y1 - pay_y, 0),
                           min(x2 + pay_x, foto.width), min(y2 + pay_y, foto.height)))

        yuz["dosya"] = os.path.join(klasor, f"{yuz['id']}.png")
        kirpim.save(yuz["dosya"])
