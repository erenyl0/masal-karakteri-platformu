"""Stil/tema/karakter prompt verileri."""

import sys

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

ORTAK_KISITLAR = (
    "Preserve their facial identity, face shape, skin tone, and hair "
    "color/texture as closely as possible. No deformed face, natural hands "
    "with five fingers, consistent single light direction, resolution at "
    "least 1024x1024."
)

TEMALAR = {
    "kirmizi_baslikli_kiz": {
        "goruntu_adi": "Kırmızı Başlıklı Kız",
        "karakterler": [
            {
                "id": "kiz",
                "yas": "cocuk",
                "cinsiyet": "kadin",
                "ad": "Kırmızı Başlıklı Kız",
                "rol": "Red Riding Hood",
                "aciklama": "wearing a red hooded cloak, carrying a small woven basket",
            },
            {
                "id": "kurt",
                "ad": "Kurt",
                "rol": "Big Bad Wolf",
                "aciklama": "anthropomorphic wolf character with grey fur, wearing a "
                             "torn grandmother's nightgown as a costume",
            },
            {
                "id": "avci",
                "yas": "yetiskin",
                "cinsiyet": "erkek",
                "ad": "Avcı",
                "rol": "the Huntsman",
                "aciklama": "wearing a forest-green hunting coat, holding an axe over "
                             "one shoulder",
            },
            {
                "id": "buyukanne",
                "yas": "yasli",
                "cinsiyet": "kadin",
                "ad": "Büyükanne",
                "rol": "the Grandmother",
                "aciklama": "elderly woman with a warm shawl, round glasses, sitting "
                             "in a cozy cottage bed",
            },
        ],
    },
    "pamuk_prenses": {
        "goruntu_adi": "Pamuk Prenses",
        "karakterler": [
            {
                "id": "prenses",
                "yas": "yetiskin",
                "cinsiyet": "kadin",
                "ad": "Prenses",
                "rol": "a kind forest princess",
                "aciklama": "wearing a simple linen dress with embroidered flowers, "
                             "holding a shiny red apple, standing in a sunlit forest glade",
            },
            {
                "id": "kralice",
                "yas": "yetiskin",
                "cinsiyet": "kadin",
                "ad": "Kötü Kraliçe",
                "rol": "the Wicked Queen",
                "aciklama": "wearing a dark purple velvet robe and a silver crown, "
                             "looking into an ornate hand mirror",
            },
            {
                "id": "cuce",
                "yas": "yetiskin",
                "cinsiyet": "erkek",
                "ad": "Madenci Cüce",
                "rol": "a cheerful forest miner",
                "aciklama": "with a long braided beard, a leather apron and a small "
                             "lantern, standing at the entrance of a gem mine",
            },
            {
                "id": "prens",
                "yas": "yetiskin",
                "cinsiyet": "erkek",
                "ad": "Prens",
                "rol": "a wandering prince",
                "aciklama": "wearing a travel cloak over light armor, riding a brown "
                             "horse along a forest path",
            },
        ],
    },
    "hansel_gretel": {
        "goruntu_adi": "Hansel ile Gretel",
        "karakterler": [
            {
                "id": "hansel",
                "yas": "cocuk",
                "cinsiyet": "erkek",
                "ad": "Hansel",
                "rol": "Hansel",
                "aciklama": "wearing short lederhosen and a wool cap, dropping "
                             "breadcrumbs along a dark forest path",
            },
            {
                "id": "gretel",
                "yas": "cocuk",
                "cinsiyet": "kadin",
                "ad": "Gretel",
                "rol": "Gretel",
                "aciklama": "with braided hair and a simple pinafore dress, "
                             "holding a small lantern in a dark forest",
            },
            {
                "id": "cadi",
                "yas": "yasli",
                "cinsiyet": "kadin",
                "ad": "Cadı",
                "rol": "the Gingerbread House Witch",
                "aciklama": "wearing a patched shawl and a pointed hat, standing in "
                             "front of a house made of gingerbread and candy",
            },
            {
                "id": "oduncu",
                "yas": "yetiskin",
                "cinsiyet": "erkek",
                "ad": "Oduncu Baba",
                "rol": "the Woodcutter Father",
                "aciklama": "wearing a plaid wool shirt, carrying a bundle of "
                             "firewood on his back at the forest edge",
            },
        ],
    },
    "kulkedisi": {
        "goruntu_adi": "Külkedisi",
        "karakterler": [
            {
                "id": "kulkedisi",
                "yas": "yetiskin",
                "cinsiyet": "kadin",
                "ad": "Külkedisi",
                "rol": "Cinderella",
                "aciklama": "wearing a patched grey work dress dusted with ash, "
                             "sitting by a stone fireplace with a broom",
            },
            {
                "id": "uvey_anne",
                "yas": "yetiskin",
                "cinsiyet": "kadin",
                "ad": "Üvey Anne",
                "rol": "the Stepmother",
                "aciklama": "wearing a stiff high-collared dark green gown, holding "
                             "a folded fan, standing in a grand hallway",
            },
            {
                "id": "peri_anne",
                "yas": "yasli",
                "cinsiyet": "kadin",
                "ad": "Peri Anne",
                "rol": "the Fairy Godmother",
                "aciklama": "wearing a flowing silver-blue cloak, holding a slender "
                             "wand that sparkles with light, beside a pumpkin",
            },
            {
                "id": "prens",
                "yas": "yetiskin",
                "cinsiyet": "erkek",
                "ad": "Prens",
                "rol": "the Prince",
                "aciklama": "wearing a deep red ceremonial coat with gold buttons, "
                             "holding a single glass slipper in a ballroom",
            },
        ],
    },
    "uc_kucuk_domuz": {
        "goruntu_adi": "Üç Küçük Domuz",
        "karakterler": [
            {
                "id": "saman_domuz",
                "ad": "Saman Evli Domuz",
                "rol": "the first little pig",
                "aciklama": "a friendly anthropomorphic pig character in a straw hat, "
                             "standing proudly beside a house made of straw",
            },
            {
                "id": "odun_domuz",
                "ad": "Tahta Evli Domuz",
                "rol": "the second little pig",
                "aciklama": "a friendly anthropomorphic pig character in overalls, "
                             "holding a bundle of sticks beside a wooden house",
            },
            {
                "id": "tugla_domuz",
                "ad": "Tuğla Evli Domuz",
                "rol": "the third little pig",
                "aciklama": "a friendly anthropomorphic pig character with a builder's "
                             "trowel, beside a sturdy brick house",
            },
            {
                "id": "kurt",
                "ad": "Kurt",
                "rol": "the Big Bad Wolf",
                "aciklama": "anthropomorphic wolf character with grey fur and puffed "
                             "cheeks, about to blow a house down",
            },
        ],
    },
}


def komut_satirindan_tema(varsayilan: str = "kirmizi_baslikli_kiz") -> str:
    tema = sys.argv[1] if len(sys.argv) > 1 else varsayilan
    if tema not in TEMALAR:
        raise SystemExit(f"Bilinmeyen tema: {tema}. Seçenekler: {', '.join(TEMALAR)}")
    return tema


def prompt_olustur(stil_anahtari: str, tema_anahtari: str, karakter_id: str) -> str:
    """Stil + tema + karakter bilgisini tek bir prompt metninde birleştirir."""
    stil = STIL_SABITLERI[stil_anahtari]
    tema = TEMALAR[tema_anahtari]
    karakter = next(k for k in tema["karakterler"] if k["id"] == karakter_id)

    return (
        f"{stil} Turn the person in the reference photo into {karakter['rol']}, "
        f"{karakter['aciklama']}. {ORTAK_KISITLAR}"
    )
