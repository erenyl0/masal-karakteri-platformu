"""Stil/tema/karakter prompt verileri."""

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
    "color/texture as closely as possible. No deformed face, consistent "
    "single light direction, resolution at least 1024x1024."
)

TEMALAR = {
    "kirmizi_baslikli_kiz": {
        "goruntu_adi": "Kırmızı Başlıklı Kız",
        "karakterler": [
            {
                "id": "kiz",
                "rol": "Red Riding Hood",
                "aciklama": "wearing a red hooded cloak, carrying a small woven basket",
            },
            {
                "id": "kurt",
                "rol": "Big Bad Wolf",
                "aciklama": "anthropomorphic wolf character with grey fur, wearing a "
                             "torn grandmother's nightgown as a costume",
            },
            {
                "id": "avci",
                "rol": "the Huntsman",
                "aciklama": "wearing a forest-green hunting coat, holding an axe over "
                             "one shoulder",
            },
            {
                "id": "buyukanne",
                "rol": "the Grandmother",
                "aciklama": "elderly woman with a warm shawl, round glasses, sitting "
                             "in a cozy cottage bed",
            },
        ],
    },
}


def prompt_olustur(stil_anahtari: str, tema_anahtari: str, karakter_id: str) -> str:
    """Stil + tema + karakter bilgisini tek bir prompt metninde birleştirir."""
    stil = STIL_SABITLERI[stil_anahtari]
    tema = TEMALAR[tema_anahtari]
    karakter = next(k for k in tema["karakterler"] if k["id"] == karakter_id)

    return (
        f"{stil} Turn the person in the reference photo into {karakter['rol']}, "
        f"{karakter['aciklama']}. {ORTAK_KISITLAR}"
    )
