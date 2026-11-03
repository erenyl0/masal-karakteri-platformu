# Masal Karakteri Platformu

Staj projem. Bir fotoğraftaki kişiyi, ya da bir aile fotoğrafındaki herkesi, masal kitabı illüstrasyonundaki bir karaktere dönüştürmeye çalışan bir sistem.

Fikir şu: fotoğrafı veriyorsun, bir masal seçiyorsun. Sistem fotoğraftaki yüzleri buluyor, her birini o masaldaki bir karaktere eşliyor, yapay zekâyla karakter görsellerini üretiyor, yüzün ne kadar korunduğunu ölçüyor ve hepsini tek bir sahnede birleştiriyor.

8 haftalık bir yol haritasına göre ilerliyorum ([Masal_Karakteri_Platformu_Gorev_ve_Yol_Haritasi.pdf](Masal_Karakteri_Platformu_Gorev_ve_Yol_Haritasi.pdf)), şu an 6. haftanın sonundayım.

## Şu anki durum

Görsel üretimi henüz gerçek API ile çalıştıramadım. Önce Google Gemini ile başladım ama görsel modeli ücretsiz katmanda çalışmıyordu. Sonra OpenAI'a (`gpt-image-1`) geçtim, orada da hesapta kredi yok.

Bu yüzden her şeyi "mock mod" ile test ettim: kod gerçek API'ye gitmek yerine fotoğrafın üstüne "MOCK" yazıp kaydediyor. Akışın geri kalanı (hata yönetimi, kalite kontrol, yüz tespiti, eşleme, sahne oluşturma) böylece API olmadan da çalışıyor. Kredi olunca `uretim.py` içinde tek satırı değiştirmek yetecek.

## Dosyalar

| Dosya | Ne yapıyor |
|---|---|
| `fizibilite.py` | Tek fotoğraf ve istediğin bir rolle iki çizim stilini deniyor, yüzü hangisinin daha iyi koruduğunu söylüyor (1. hafta) |
| `sablonlar.py` | Masal temaları, karakterler ve prompt'lar (5 tema, 20 karakter) |
| `uretim.py` | Tek görsel üretimi, hata olunca tekrar deneme, yüz benzerliği ölçümü |
| `uretim_dongusu.py` | Bir temadaki her karakteri her stille üretip sonuçları CSV'ye yazıyor |
| `kalite_kontrol.py` | Her karakter için birkaç görsel üretip yüze en çok benzeyeni seçiyor |
| `yuz_tespit.py` | Fotoğraftaki yüzleri bulup netlik/açı kontrolü yapıyor, düzeltip kırpıyor |
| `eslestirme.py` | Yüzleri karakterlere eşliyor, eşleme elle de değiştirilebiliyor |
| `kompozisyon.py` | Üretilen karakterleri tek bir sahnede birleştiriyor |
| `grup_akisi.py` | Hepsini bir araya getiriyor: grup fotoğrafından tek sahne |

## Kurulum

Python 3.10 veya üstü gerekiyor.

```
pip install openai deepface tf-keras retina-face opencv-python pillow
```

Varsayılan olarak mock modda çalışıyor, API anahtarı gerekmiyor. Gerçek üretim için `uretim.py` içinde `MOCK_MODE = False` yapıp anahtarı terminalde tanımlamak lazım:

```powershell
$env:OPENAI_API_KEY="sk-..."
```

İlk çalıştırmada yüz tespiti ve yüz tanıma modelleri indiriliyor (toplam 700 MB civarı), biraz sürebilir.

## Çalıştırma

```
python fizibilite.py
python uretim_dongusu.py
python kalite_kontrol.py
python grup_akisi.py hansel_gretel
```

Hepsi açılışta fotoğraf seçmek için bir pencere açıyor. Tema adı verilmezse Kırmızı Başlıklı Kız ile çalışıyor. Diğer temalar: `pamuk_prenses`, `hansel_gretel`, `kulkedisi`, `uc_kucuk_domuz`.

## Eksikler

- Yüzleri karakterlere şimdilik soldan sağa sırayla eşliyorum. Yol haritasında yaş ve cinsiyet tahminine göre yapılması gerekiyor; şu haliyle bir yetişkin erkek Gretel olabiliyor.
- Gerçek görsellerle deneme yapamadığım için benzerlik eşiğini (%60) ve temaların görsel tutarlılığını henüz kontrol edemedim.
- 7. hafta (web arayüzü) ve 8. hafta (test ve sunum) daha yapılmadı.

## Gizlilik

Kendi test fotoğraflarım depoda yok. Denemek için kendi fotoğrafını kullan; başkalarının, özellikle çocukların fotoğraflarını izinsiz kullanma.

## Yapay zekâ kullanımı

Projeyi geliştirirken Anthropic'in yapay zekâ kodlama asistanı Claude Code'dan yardım aldım. Commit geçmişindeki `Co-Authored-By: Claude` satırları da bu yüzden var.
