# Masal Karakteri Platformu

Staj projem. Bir fotoğraftaki kişiyi, ya da bir aile fotoğrafındaki herkesi, masal kitabı illüstrasyonundaki bir karaktere dönüştürmeye çalışan bir sistem.

Fikir şu: fotoğrafı veriyorsun, bir masal seçiyorsun. Sistem fotoğraftaki yüzleri buluyor, her birini o masaldaki bir karaktere eşliyor, yapay zekâyla karakter görsellerini üretiyor, yüzün ne kadar korunduğunu ölçüyor ve hepsini tek bir sahnede birleştiriyor.

8 haftalık bir yol haritasına göre ilerliyorum ([Masal_Karakteri_Platformu_Gorev_ve_Yol_Haritasi.pdf](Masal_Karakteri_Platformu_Gorev_ve_Yol_Haritasi.pdf)), şu an son haftadayım.

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
| `eslestirme.py` | Yüzleri tahmini yaş ve cinsiyete göre karakterlere eşliyor, eşleme elle de değiştirilebiliyor |
| `kompozisyon.py` | Üretilen karakterleri tek bir sahnede birleştiriyor |
| `grup_akisi.py` | Hepsini bir araya getiriyor: grup fotoğrafından tek sahne |
| `api.py` | Web arayüzünün konuştuğu sunucu (FastAPI): yükleme, eşleme, üretim, indirme, silme |
| `arayuz/` | React ile yazılmış web arayüzü: fotoğraf → yüz onayı → masal ve eşleme → sahne |
| `degerlendirme.py` | Test fotoğraflarını uçtan uca akıştan geçirip sonuçları yol haritasındaki hedeflerle karşılaştırıyor (8. hafta) |

## Kurulum

Python 3.10 veya üstü gerekiyor.

```
pip install -r requirements.txt
```

Varsayılan olarak mock modda çalışıyor, API anahtarı gerekmiyor. Gerçek üretim için `uretim.py` içinde `MOCK_MODE = False` yapıp anahtarı terminalde tanımlamak lazım:

```powershell
$env:OPENAI_API_KEY="sk-..."
```

İlk çalıştırmada yüz tespiti, yüz tanıma ve yaş/cinsiyet modelleri indiriliyor (toplam 1,8 GB civarı), biraz sürebilir.

## Web arayüzü

Arayüz için ayrıca [Node.js](https://nodejs.org) (LTS) gerekiyor. İlk seferde arayüzü derlemek lazım:

```
cd arayuz
npm install
npm run build
cd ..
```

Sonra sunucuyu başlatıp tarayıcıda http://127.0.0.1:8000 adresini açmak yetiyor:

```
python api.py
```

Arayüz üzerinde çalışırken `python api.py` açıkken `arayuz` klasöründe `npm run dev` çalıştırılırsa, değişiklikler http://localhost:5173 adresinde anında görünüyor.

Fotoğraf yüklenmeden önce, fotoğraftaki kişilerin kendin ya da ailen olduğunu onaylaman gerekiyor. Yüklenen fotoğraflar 1 saat sonra, sunucu yeniden başladığında ya da "Verilerimi sil" butonuna basınca siliniyor.

## Komut satırından çalıştırma

```
python fizibilite.py
python uretim_dongusu.py
python kalite_kontrol.py
python grup_akisi.py hansel_gretel
```

Hepsi açılışta fotoğraf seçmek için bir pencere açıyor. Tema adı verilmezse Kırmızı Başlıklı Kız ile çalışıyor. Diğer temalar: `pamuk_prenses`, `hansel_gretel`, `kulkedisi`, `uc_kucuk_domuz`.

## Değerlendirme

Test fotoğraflarını `test_fotograflari/` klasörüne koyup şunu çalıştırıyorum:

```
python degerlendirme.py
```

Her fotoğrafta kaç yüz bulunduğunu, hangi uyarıların çıktığını, adımların ne kadar sürdüğünü ve üretimin başarılı olup olmadığını ölçüp `degerlendirme_ozeti.md` dosyasına bir tablo yazıyor. Dosya adına kişi sayısını yazarsam (ör. `aile_4kisi.jpg`) doğru sayıda yüz bulunup bulunmadığını da kontrol ediyor.

Şimdilik mock modda ve elimdeki fotoğraflardan türettiğim senaryolarla (tek kişi, aile, 6 kişilik kalabalık, düşük ışık, bulanık, küçük yüzler, yan çekilmiş telefon fotoğrafı, yüzsüz fotoğraf) denedim. 8 fotoğrafın hepsinde doğru sayıda yüz bulundu ve sorunlu fotoğraflar uyarı aldı. Yüzleri bulma, hizalama ve yaş/cinsiyet tahmini tek kişilik fotoğraflarda 6 saniye civarında sürüyor, kalabalık fotoğraflarda 20 saniyeye çıkıyor. Üretim süresi ve yüz benzerliği ancak gerçek API ile ölçülebilecek.

## Eksikler

- Yüzleri karakterlere tahmini yaş ve cinsiyete göre eşliyorum (DeepFace). Tahminler yanılabiliyor, o yüzden eşleme elle de değiştirilebiliyor. Temadaki slotlara uymayan bir aile (ör. üç yetişkin erkek ve Hansel ile Gretel) olursa biri yine de uymayan bir role düşüyor.
- Gerçek görsellerle deneme yapamadığım için benzerlik eşiğini (%60) ve temaların görsel tutarlılığını henüz kontrol edemedim.
- Web arayüzü tek kişilik bir demo için yapıldı: yol haritasında önerilen Celery + Redis kuyruğu yerine basit bir sıra kullanıyorum, işler sunucunun belleğinde tutuluyor (sunucu kapanınca siliniyor) ve kullanıcı girişi yok.
- Yol haritasındaki KPI'lardan kişi başına üretim süresi, üretim başarı oranı ve yüz benzerliği gerçek API olmadan ölçülemiyor. "Bana benziyor" memnuniyeti ve çoklu kişi eşleme doğruluğu için de gerçek kişilerle kullanıcı testi gerekiyor.
- Bulanıklık eşiğini gerçek aile fotoğraflarıyla ayarlamadım; düşük çözünürlüklü yüzler kolayca "bulanık" uyarısı alabiliyor.

## Gizlilik

Kendi test fotoğraflarım depoda yok. Denemek için kendi fotoğrafını kullan; başkalarının, özellikle çocukların fotoğraflarını izinsiz kullanma.

## Yapay zekâ kullanımı

Projeyi geliştirirken Anthropic'in yapay zekâ kodlama asistanı Claude Code'dan yardım aldım. Commit geçmişindeki `Co-Authored-By: Claude` satırları da bu yüzden var.
