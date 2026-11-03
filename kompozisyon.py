"""Ayrı ayrı üretilen karakter görsellerini tek bir sahnede yan yana dizer."""

import PIL.Image
from PIL import ImageDraw, ImageFont, ImageOps

ARKA_PLAN = (250, 240, 220)
YAZI_RENGI = (60, 40, 20)
ALT_BOSLUK = 70
# Pillow'un kendi yazı tipinde ğ, ş, ı gibi harfler yok; sistemde Türkçe destekli olanı arıyoruz
YAZI_TIPLERI = ["segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"]


def _yazi_tipi(boyut: int) -> ImageFont.ImageFont:
    for ad in YAZI_TIPLERI:
        try:
            return ImageFont.truetype(ad, boyut)
        except OSError:
            continue
    return ImageFont.load_default(size=boyut)


def sahne_olustur(parcalar: list[tuple[str, str]], cikti_yolu: str,
                  boyut: tuple[int, int] = (1536, 1024)) -> str:
    genislik, yukseklik = boyut
    sahne = PIL.Image.new("RGB", boyut, ARKA_PLAN)
    cizim = ImageDraw.Draw(sahne)
    yazi_tipi = _yazi_tipi(30)

    hucre = genislik // len(parcalar)
    for sira, (gorsel_yolu, etiket) in enumerate(parcalar):
        gorsel = ImageOps.contain(PIL.Image.open(gorsel_yolu).convert("RGB"),
                                  (hucre - 40, yukseklik - ALT_BOSLUK - 40))
        sol = sira * hucre
        sahne.paste(gorsel, (sol + (hucre - gorsel.width) // 2, (yukseklik - ALT_BOSLUK - gorsel.height) // 2))
        cizim.text((sol + hucre // 2, yukseklik - ALT_BOSLUK // 2), etiket,
                   fill=YAZI_RENGI, font=yazi_tipi, anchor="mm")

    sahne.save(cikti_yolu)
    return cikti_yolu
