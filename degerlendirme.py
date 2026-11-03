"""Hafta 8 değerlendirmesi: test fotoğraflarını uçtan uca akıştan geçirip yol haritasındaki KPI'larla karşılaştırır.

Fotoğrafları test_fotograflari/ klasörüne koy. Dosya adında kişi sayısı varsa (ör. aile_4kisi.jpg)
yüz tespitinin doğru sayıyı bulup bulmadığı da ölçülür.
"""

import csv
import os
import re
import statistics
import time

from eslestirme import otomatik_esle
from grup_akisi import STIL, yuzleri_hazirla
from kalite_kontrol import BENZERLIK_ESIGI, en_iyisini_uret
from sablonlar import TEMALAR, komut_satirindan_tema, prompt_olustur
from uretim import MOCK_MODE, UretimHatasi

FOTO_KLASORU = "test_fotograflari"
CIKTI_KLASORU = "degerlendirme_ciktilari"
CSV_YOLU = "degerlendirme_sonuclari.csv"
OZET_YOLU = "degerlendirme_ozeti.md"
HEDEF_SURE_SN = 30
HEDEF_BASARI = 0.90


def beklenen_kisi_sayisi(dosya_adi: str) -> int | None:
    bulunan = re.search(r"(\d+)kisi", dosya_adi)
    return int(bulunan.group(1)) if bulunan else None


def fotografi_degerlendir(foto_yolu: str, tema_anahtari: str) -> dict:
    ad = os.path.splitext(os.path.basename(foto_yolu))[0]
    klasor = os.path.join(CIKTI_KLASORU, ad)

    baslangic = time.time()
    yuzler = yuzleri_hazirla(foto_yolu, os.path.join(klasor, "yuzler"))
    hazirlik_sn = time.time() - baslangic

    eslesme = otomatik_esle(yuzler, TEMALAR[tema_anahtari]["karakterler"])
    sureler, skorlar, basarili = [], [], 0
    for yuz in yuzler:
        karakter_id = eslesme.get(yuz["id"])
        if karakter_id is None:
            continue
        baslangic = time.time()
        try:
            en_iyi = en_iyisini_uret(yuz["dosya"], prompt_olustur(STIL, tema_anahtari, karakter_id),
                                     os.path.join(klasor, f"{yuz['id']}_{karakter_id}"), yuz["id"])
        except UretimHatasi:
            en_iyi = None
        sureler.append(time.time() - baslangic)
        if en_iyi:
            basarili += 1
            if en_iyi["benzerlik"] is not None:
                skorlar.append(en_iyi["benzerlik"])

    return {
        "foto": os.path.basename(foto_yolu),
        "beklenen_kisi": beklenen_kisi_sayisi(ad),
        "bulunan_yuz": len(yuzler),
        "uyarilar": "; ".join(f"{y['id']}: {', '.join(y['uyarilar'])}" for y in yuzler if y["uyarilar"]),
        "tahminler": "; ".join(f"{y['id']}: {y['yas']} yaş, kadın %{y['kadin_olasiligi'] * 100:.0f}"
                               for y in yuzler if "yas" in y),
        "hazirlik_sn": round(hazirlik_sn, 1),
        "uretilen": basarili,
        "denenen": len(sureler),
        "kisi_basi_sn": round(statistics.mean(sureler), 1) if sureler else None,
        "benzerlikler": skorlar,
    }


def ozet_yaz(sonuclar: list[dict], tema_anahtari: str) -> str:
    sayili = [s for s in sonuclar if s["beklenen_kisi"] is not None]
    dogru_sayim = sum(1 for s in sayili if s["bulunan_yuz"] == s["beklenen_kisi"])
    denenen = sum(s["denenen"] for s in sonuclar)
    uretilen = sum(s["uretilen"] for s in sonuclar)
    # fotoğrafların ortalamasını değil kişilerin ortalamasını istiyoruz, kalabalık fotoğraf daha çok ağırlık taşımalı
    toplam_sure = sum(s["kisi_basi_sn"] * s["denenen"] for s in sonuclar if s["kisi_basi_sn"] is not None)
    skorlar = [skor for s in sonuclar for skor in s["benzerlikler"]]
    hazirlik = [s["hazirlik_sn"] for s in sonuclar]
    mock_notu = " (mock mod, gerçek değil)" if MOCK_MODE else ""

    kisi_basi = f"{toplam_sure / denenen:.1f} sn{mock_notu}" if denenen else "ölçülmedi"
    basari = f"%{uretilen / denenen * 100:.0f} ({uretilen}/{denenen}){mock_notu}" if denenen else "ölçülmedi"
    benzerlik = (f"ortalama %{statistics.mean(skorlar):.1f}, eşiği (%{BENZERLIK_ESIGI:.0f}) geçen "
                 f"%{sum(s >= BENZERLIK_ESIGI for s in skorlar) / len(skorlar) * 100:.0f}") if skorlar else \
        "ölçülmedi (mock modda benzerlik ölçülmüyor)"
    slotlar = sorted({len(t["karakterler"]) for t in TEMALAR.values()})

    satirlar = [
        f"# Değerlendirme özeti ({TEMALAR[tema_anahtari]['goruntu_adi']}, {'mock' if MOCK_MODE else 'gerçek'} mod)",
        "",
        f"{len(sonuclar)} fotoğraf, {sum(s['bulunan_yuz'] for s in sonuclar)} yüz.",
        "",
        "| KPI | Hedef | Ölçülen |",
        "|---|---|---|",
        f"| Kişi başına üretim süresi | < {HEDEF_SURE_SN} sn | {kisi_basi} |",
        f"| Otomatik yeniden üretim sonrası başarı | ≥ %{HEDEF_BASARI * 100:.0f} | {basari} |",
        f"| Yüz benzerliği (otomatik ölçüm) | - | {benzerlik} |",
        f"| Hazır masal teması | ≥ 5 tema, ≥ 3 slot | {len(TEMALAR)} tema, {'/'.join(map(str, slotlar))} slot |",
        "| Yüz benzerliği memnuniyeti | ≥ %80 \"bana benziyor\" | kullanıcı testi gerekiyor |",
        "| Çoklu kişi eşleme doğruluğu | ≥ %85 | elle kontrol gerekiyor |",
        "",
        f"Yüz tespiti: dosya adında kişi sayısı olan {len(sayili)} fotoğrafın {dogru_sayim} tanesinde doğru sayı bulundu.",
        f"Yüz bulma + hizalama + yaş/cinsiyet tahmini: fotoğraf başına ortanca {statistics.median(hazirlik):.1f} sn "
        f"(ilk fotoğraf modellerin yüklenmesini de içeriyor).",
        "",
        "| Fotoğraf | Beklenen | Bulunan | Uyarılar | Hazırlık (sn) | Üretilen |",
        "|---|---|---|---|---|---|",
    ]
    for s in sonuclar:
        beklenen = "-" if s["beklenen_kisi"] is None else s["beklenen_kisi"]
        satirlar.append(f"| {s['foto']} | {beklenen} | {s['bulunan_yuz']} | {s['uyarilar'] or '-'} | "
                        f"{s['hazirlik_sn']} | {s['uretilen']}/{s['denenen']} |")
    return "\n".join(satirlar) + "\n"


def main():
    tema_anahtari = komut_satirindan_tema()
    if not os.path.isdir(FOTO_KLASORU):
        raise SystemExit(f"{FOTO_KLASORU}/ klasörü yok. Test fotoğraflarını oraya koyup tekrar çalıştır.")
    fotograflar = sorted(f for f in os.listdir(FOTO_KLASORU) if f.lower().endswith((".jpg", ".jpeg", ".png")))
    if not fotograflar:
        raise SystemExit(f"{FOTO_KLASORU}/ içinde fotoğraf yok.")

    sonuclar = []
    for dosya in fotograflar:
        print(f"\n=== {dosya} ===")
        sonuclar.append(fotografi_degerlendir(os.path.join(FOTO_KLASORU, dosya), tema_anahtari))

    with open(CSV_YOLU, "w", newline="", encoding="utf-8") as f:
        yazici = csv.DictWriter(f, fieldnames=[k for k in sonuclar[0] if k != "benzerlikler"] + ["benzerlikler"])
        yazici.writeheader()
        for s in sonuclar:
            yazici.writerow({**s, "benzerlikler": " ".join(map(str, s["benzerlikler"]))})

    ozet = ozet_yaz(sonuclar, tema_anahtari)
    with open(OZET_YOLU, "w", encoding="utf-8") as f:
        f.write(ozet)
    print("\n" + ozet)
    print(f"Ayrıntılar {CSV_YOLU}, özet {OZET_YOLU} dosyasında.")


if __name__ == "__main__":
    main()
