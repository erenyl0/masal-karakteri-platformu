"""Ayrı ayrı üretilen karakter görsellerini tek bir masal sahnesinde birleştirir."""

import PIL.Image
from PIL import ImageDraw

ARKA_PLAN = (250, 240, 220)
ETIKET_YUKSEKLIGI = 60


def sahne_olustur(parcalar: list[tuple[str, str]], cikti_yolu: str,
                  boyut: tuple[int, int] = (1536, 1024)) -> str:
    genislik, yukseklik = boyut
    sahne = PIL.Image.new("RGB", boyut, ARKA_PLAN)
    cizim = ImageDraw.Draw(sahne)

    hucre_genislik = genislik // len(parcalar)
    for sira, (gorsel_yolu, etiket) in enumerate(parcalar):
        gorsel = PIL.Image.open(gorsel_yolu).convert("RGB")
        gorsel.thumbnail((hucre_genislik - 40, yukseklik - ETIKET_YUKSEKLIGI - 40))

        x = sira * hucre_genislik + (hucre_genislik - gorsel.width) // 2
        y = (yukseklik - ETIKET_YUKSEKLIGI - gorsel.height) // 2
        sahne.paste(gorsel, (x, y))
        cizim.text((sira * hucre_genislik + 20, yukseklik - ETIKET_YUKSEKLIGI + 15),
                   etiket, fill=(60, 40, 20))

    sahne.save(cikti_yolu)
    return cikti_yolu
