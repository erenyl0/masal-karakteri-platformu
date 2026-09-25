# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Proje genel bakış

Bu depo, **"Kişiselleştirilmiş Masal Karakteri Platformu"** adlı bir staj projesinin ilk aşamalarını içerir: kullanıcının yüklediği bir referans yüz fotoğrafını, Google Gemini görsel üretim modelini kullanarak masal karakteri illüstrasyonuna dönüştüren ve sonucun orijinal yüze ne kadar benzediğini otomatik ölçen bir sistem. Nihai hedef; yüz tespiti, kimlik korumalı görsel üretim, çoklu kişi kompozisyonu, kalite kontrolü ve bir web arayüzünü bir araya getiren uçtan uca bir üretim platformu kurmak (bkz. [Masal_Karakteri_Platformu_Gorev_ve_Yol_Haritasi.pdf](Masal_Karakteri_Platformu_Gorev_ve_Yol_Haritasi.pdf) — 8 haftalık detaylı yol haritası, mimari ve KPI'lar).

Depo şu an henüz bir git deposu değil ve paket yöneticisi manifestosu (requirements.txt / pyproject.toml) yok. Dosyalar, yol haritasındaki haftalık teslimlere karşılık gelir ama isimleri konuya göre verilmiştir:

- [fizibilite.py](fizibilite.py) — Hafta 1: tek referans fotoğraf + tek karakter rolü ile fizibilite testi (2 stil varyasyonu). Bağımsız çalışır, diğer dosyaları kullanmaz.
- [sablonlar.py](sablonlar.py) — Hafta 2: stil/tema/karakter verisini kod dışında tutan veri modülü (`STIL_SABITLERI`, `TEMALAR`, `prompt_olustur()`).
- [uretim.py](uretim.py) — Hafta 3: tek bir yüz + tek bir karakter şablonundan görsel üreten `gorsel_uret()` fonksiyonu; hata/timeout durumunda artan bekleme süreleriyle (`BASLANGIC_BEKLEME_SN` katlanarak) en fazla `MAKS_DENEME` kere otomatik yeniden dener, başarılı olduğunda `(dosya_yolu, deneme_sayisi)` döner. Ayrıca `benzerlik_olc()` (DeepFace ile referans/üretim benzerlik yüzdesi) de burada — üretim + kalite ölçme mantığı aynı dosyada, diğer dosyalar buradan import ediyor. `MOCK_MODE` (mock/gerçek mod anahtarı, tek kaynak burada) ve `MOCK_HATA_OLASILIGI` (mock modda kasıtlı hata üretme olasılığı, retry'ı API'siz test etmek için) de burada tanımlı.
- [uretim_dongusu.py](uretim_dongusu.py) — Hafta 2'nin üretim mantığı: `sablonlar.py`'den okuduğu bir temadaki tüm karakter × stil kombinasyonlarını, her biri için `uretim.gorsel_uret()`'i çağırarak üretir (retry buraya otomatik yansır) ve sonuçları `uretim_sonuclari.csv`'ye loglar. Bir kombinasyon tüm denemelere rağmen başarısız olursa döngü durmaz, o satır `hata` sütunuyla loglanıp devam edilir.
- [kalite_kontrol.py](kalite_kontrol.py) — Hafta 4: her kombinasyon için aynı prompt ile en fazla `KALITE_MAKS_DENEME` kere üretim yapan (best-of-N) `en_iyisini_uret()` fonksiyonu; benzerlik skorunu ölçer, `BENZERLIK_ESIGI`'ni geçen ilk sonuçta erken durur, hiçbiri geçemezse en yüksek skorlu olanı yine de döndürüp "insan onayı gerekli" işaretler. Sonuçlar `kalite_sonuclari.csv`'ye loglanır.

## Kurulum ve çalıştırma

Bağımlılıkları kur:
```bash
pip install google-genai deepface opencv-python pillow
```

Gemini API anahtarını ortam değişkeni olarak ayarla:
```bash
$env:GEMINI_API_KEY="anahtarınız"   # PowerShell
set GEMINI_API_KEY=anahtarınız      # cmd
```
Ortam değişkenleri yalnızca tanımlandıkları terminal penceresinde geçerlidir — script'i farklı bir pencerede çalıştırırsan yeniden tanımlaman gerekir (kalıcı yapmak için `[System.Environment]::SetEnvironmentVariable(...,"User")` kullanılabilir).

Script'leri çalıştır:
```bash
python fizibilite.py
python uretim_dongusu.py
python uretim.py
python kalite_kontrol.py
```
Hepsi interaktiftir: `tkinter` ile native dosya seçme diyaloğu açar (referans fotoğraf seçimi ve Hafta 1'de karakter rolü girişi için) — CLI argümanı arayüzü yoktur.

**Önemli / bilinen kısıtlama:** Gemini'nin görsel üretim modelleri (`gemini-3.1-flash-image` / "Nano Banana" ailesi) Google AI Studio'nun ücretsiz katmanında **çalışmaz** — `429 RESOURCE_EXHAUSTED` / `limit: 0` hatası, geçici bir kota sınırı değil, hesapta billing (faturalandırma) aktif olmadığını gösterir. Görsel üretim test etmeden önce https://aistudio.google.com/apikey üzerinden ilgili projede billing etkinleştirilmiş olmalı. Billing yokken `uretim.py` içindeki `MOCK_MODE = True` bayrağıyla (referans fotoğrafın üzerine "MOCK" etiketi basan sahte üretim) kod akışı yine de test edilebilir — bu bayrak `uretim_dongusu.py` ve `kalite_kontrol.py`'yi de etkiler, çünkü ikisi de üretimi `uretim.py` üzerinden yapıyor.

## Mimari

### Dosyalar arası bağımlılık

`sablonlar.py` (veri) ← `uretim.py` (tek görsel üretimi + retry + kalite ölçümü) ← `uretim_dongusu.py` (bir temadaki tüm kombinasyonları tek seferlik üretip CSV'ye loglama) ve ← `kalite_kontrol.py` (aynı kombinasyonları best-of-N + kalite eşiğiyle üretip CSV'ye loglama). `fizibilite.py` bu zincirin dışında, tamamen bağımsız duruyor (kendi stil sabitlerini kendi içinde tekrar tanımlıyor). `uretim_dongusu.py` ve `kalite_kontrol.py` birbirini değil, `uretim.py`'yi (üretim + kalite ölçümü) ve `sablonlar.py`'yi (veri) ortak kaynak olarak kullanır — retry/mock ayarları (`MOCK_MODE` vb.) tek bir yerden, `uretim.py`'den kontrol edilir.

### Uçtan uca akış

1. Kullanıcı bir referans yüz fotoğrafı seçer (`tkinter.filedialog`).
2. Stil sabiti (`STIL_SABITLERI`, örn. `el_cizimi_masal`, `yumusak_suluboya`) + karakter/rol bilgisi birleştirilerek `prompt_olustur()` ile bir Gemini prompt'u oluşturulur.
3. `uretim.gorsel_uret()` bu prompt'u Gemini'ye gönderir (`google.genai`, `response_modalities=["TEXT","IMAGE"]`); hata alırsa artan bekleme süreleriyle (`BASLANGIC_BEKLEME_SN` katlanarak) en fazla `MAKS_DENEME` kere yeniden dener, son denemede de başarısız olursa `UretimHatasi` fırlatır (çağıran taraf bunu yakalayıp kontrollü şekilde loglar/devam eder, çökmez).
4. Üretilen görsel, `benzerlik_olc()` (DeepFace, cosine mesafe, `retinaface` dedektörü, `enforce_detection=False`) ile referans fotoğrafla karşılaştırılıp bir benzerlik yüzdesi hesaplanır (yalnızca `MOCK_MODE = False` iken; mock çıktı gerçek bir yüz olmadığından mock modda benzerlik ölçülmez). Stilize illüstrasyonlarda yüz tespiti başarısız olabileceği için hata durumunda akış çökmez, sadece uyarı basılır.
5. `kalite_kontrol.py`'de bu 3-4 adımı `en_iyisini_uret()` içinde en fazla `KALITE_MAKS_DENEME` kere tekrarlar (best-of-N): skor `BENZERLIK_ESIGI`'ni geçen ilk sonuçta erken durur; hiçbiri geçemezse en yüksek skorlu sonuç yine de seçilir ama `"insan onayı gerekli"` işaretlenir.

Yeni bir tema veya karakter eklemek yalnızca `sablonlar.py`'deki `TEMALAR` sözlüğüne yeni bir blok eklemeyi gerektirir; üretim koduna dokunulmaz. `uretim_dongusu.py`'nin sonuçları `uretim_sonuclari.csv`'ye, `kalite_kontrol.py`'nin sonuçları `kalite_sonuclari.csv`'ye `csv.DictWriter` ile satır satır loglanır — 30 saniye altı üretim süresi ve benzerlik skoru hedefleri buradan takip edilir.

### Hedeflenen tam sistem (yol haritasındaki bileşenler)

Yol haritası dokümanına göre planlanan uçtan uca mimari: Yükleme Servisi (FastAPI) → Yüz Tespit Modülü (MediaPipe/OpenCV, kırpma + kalite skoru) → Eşleme Motoru (yüz → karakter slotu) → Prompt Oluşturucu (Jinja2 şablonları) → Üretim Katmanı (Gemini API, retry/best-of-N) → Kalite Kontrol (benzerlik eşiği altında otomatik yeniden üretim, maks. 3 deneme) → Kompozisyon (Pillow/OpenCV ile çoklu karakteri tek sahnede birleştirme) → React/Next.js frontend. Şu anki script'ler bu hattın "Prompt Oluşturucu + Üretim Katmanı + Kalite Kontrol (retry + best-of-N)" kısmını karşılıyor; Yüz Tespit Modülü, Eşleme Motoru, Kompozisyon ve Frontend henüz yazılmadı (bkz. Hafta 5-7).

## Uyum / riskler (yol haritasından)

- Çocuk verisi işleniyorsa KVKK/GDPR'a uygun açık rıza akışı gerekli.
- Yüklenen orijinal fotoğraflar şifreli saklanmalı, kullanıcı talebiyle kalıcı silinebilmeli.
- Disney vb. marka bağlantılı karakterler yerine özgün, telif riski taşımayan tasarımlar kullanılmalı.

## Konvansiyonlar

- Kod genelinde (değişken/fonksiyon adları, konsol çıktıları) Türkçe kullanılıyor — yeni kodda da bu tutarlılığı koru, İngilizceye geçme.
- Model adı gibi sabitler dosya başında büyük harfli sabit olarak tutuluyor (`MODEL_ADI`, `MOCK_MODE`, `TEMA_ANAHTARI`).
- Docstring/yorumlar kısa tutuluyor (genelde tek satır) — uzun açıklama blokları yazılmıyor.
