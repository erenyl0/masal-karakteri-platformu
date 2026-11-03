"""Web arayüzünün konuştuğu API: yükleme, yüz onayı, eşleme, üretim, indirme ve silme."""

import io
import os
import shutil
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from eslestirme import otomatik_esle
from grup_akisi import sahne_uret, yuzleri_hazirla
from sablonlar import TEMALAR
from uretim import MOCK_MODE, UretimHatasi
from yuz_tespit import foto_ac

PROJE = os.path.dirname(os.path.abspath(__file__))
IS_KLASORU = os.path.join(PROJE, "isler")
ARAYUZ_KLASORU = os.path.join(PROJE, "arayuz", "dist")
SAKLAMA_SURESI_SN = 60 * 60
TEMIZLIK_ARALIGI_SN = 60
MAKS_DOSYA_BOYUTU = 15 * 1024 * 1024

app = FastAPI(title="Masal Karakteri Platformu")

# Modeller aynı anda iki işte çalışmasın diye tek işçi var, istekler sırayla işleniyor
isci = ThreadPoolExecutor(max_workers=1)
isler: dict[str, dict] = {}
# temizlik ayrı bir iş parçacığında çalıştığı için işin durumunu değiştiren yerler sırayla girsin
kilit = threading.Lock()

# önceki çalıştırmadan kalan fotoğraflar kimseye ait değil artık, siliyoruz
shutil.rmtree(IS_KLASORU, ignore_errors=True)


class EslemeIstegi(BaseModel):
    tema: str
    yuzler: list[str]


class UretimIstegi(BaseModel):
    tema: str
    eslesme: dict[str, str]


def _is_getir(is_id: str) -> dict:
    if is_id not in isler:
        raise HTTPException(404, "Böyle bir iş yok ya da süresi dolup silindi.")
    return isler[is_id]


def _tema_getir(tema: str) -> dict:
    if tema not in TEMALAR:
        raise HTTPException(400, f"Bilinmeyen tema: {tema}")
    return TEMALAR[tema]


def _calisiyor_mu(is_: dict) -> bool:
    return is_["durum"] in ("sirada", "uretiliyor")


def _eski_isleri_sil():
    with kilit:
        for is_id, is_ in list(isler.items()):
            if time.time() - is_["zaman"] > SAKLAMA_SURESI_SN and not _calisiyor_mu(is_):
                shutil.rmtree(is_["klasor"], ignore_errors=True)
                del isler[is_id]


def _temizlik_dongusu():
    # kimse yeni fotoğraf yüklemese de süresi dolan fotoğraflar silinsin
    while True:
        time.sleep(TEMIZLIK_ARALIGI_SN)
        _eski_isleri_sil()


threading.Thread(target=_temizlik_dongusu, daemon=True).start()


@app.get("/api/bilgi")
def bilgi():
    return {"mock": MOCK_MODE, "saklama_suresi_dk": SAKLAMA_SURESI_SN // 60}


@app.get("/api/temalar")
def temalar():
    return [
        {"anahtar": anahtar, "ad": tema["goruntu_adi"],
         "karakterler": [{"id": k["id"], "ad": k["ad"]} for k in tema["karakterler"]]}
        for anahtar, tema in TEMALAR.items()
    ]


@app.post("/api/yukle")
def yukle(foto: UploadFile = File(...), onay: bool = Form(False)):
    if not onay:
        raise HTTPException(400, "Onay kutusu işaretlenmeden fotoğraf işlenmiyor.")

    veri = foto.file.read(MAKS_DOSYA_BOYUTU + 1)
    if len(veri) > MAKS_DOSYA_BOYUTU:
        raise HTTPException(413, "Fotoğraf 15 MB'tan büyük olamaz.")
    try:
        gorsel = foto_ac(io.BytesIO(veri))
    except Exception:
        raise HTTPException(400, "Bu dosya bir fotoğraf olarak açılamadı.") from None

    _eski_isleri_sil()
    is_id = uuid.uuid4().hex
    klasor = os.path.join(IS_KLASORU, is_id)
    os.makedirs(klasor)

    # yeniden kaydedince konum gibi EXIF bilgileri de atılmış oluyor
    foto_yolu = os.path.join(klasor, "orijinal.jpg")
    gorsel.save(foto_yolu, quality=95)

    yuzler = []
    try:
        yuzler = isci.submit(yuzleri_hazirla, foto_yolu, os.path.join(klasor, "yuzler")).result()
    finally:
        # yüz yoksa ya da analiz çöktüyse fotoğraf diskte sahipsiz kalmasın
        if not yuzler:
            shutil.rmtree(klasor, ignore_errors=True)
    if not yuzler:
        raise HTTPException(422, "Fotoğrafta yüz bulunamadı. Yüzlerin net göründüğü başka bir fotoğraf dene.")

    isler[is_id] = {"klasor": klasor, "yuzler": yuzler, "durum": "yuklendi", "zaman": time.time(),
                    "tamamlanan": 0, "toplam": 0, "mesaj": "", "sahne": None, "eksikler": []}
    return {
        "is_id": is_id,
        "yuzler": [{"id": yuz["id"], "gorsel": f"/api/is/{is_id}/yuz/{yuz['id']}", "uyarilar": yuz["uyarilar"],
                    "yas": yuz.get("yas"), "kadin_olasiligi": yuz.get("kadin_olasiligi")} for yuz in yuzler],
    }


@app.get("/api/is/{is_id}/yuz/{yuz_id}")
def yuz_gorseli(is_id: str, yuz_id: str):
    yuz = next((y for y in _is_getir(is_id)["yuzler"] if y["id"] == yuz_id), None)
    if yuz is None:
        raise HTTPException(404, "Böyle bir yüz yok.")
    return FileResponse(yuz["dosya"])


@app.post("/api/is/{is_id}/esle")
def esle(is_id: str, istek: EslemeIstegi):
    tema = _tema_getir(istek.tema)
    secilenler = [yuz for yuz in _is_getir(is_id)["yuzler"] if yuz["id"] in istek.yuzler]
    if not secilenler:
        raise HTTPException(400, "En az bir yüz seçmelisin.")
    return {"eslesme": otomatik_esle(secilenler, tema["karakterler"])}


def _uretim_isi(is_id: str, tema: str, eslesme: dict[str, str]):
    is_ = isler[is_id]

    def ilerleme(tamamlanan, toplam, mesaj):
        is_.update(tamamlanan=tamamlanan, toplam=toplam, mesaj=mesaj)

    is_["durum"] = "uretiliyor"
    try:
        sahne, eksikler = sahne_uret(is_["yuzler"], tema, eslesme, os.path.join(is_["klasor"], "sahne"), ilerleme)
    except UretimHatasi as hata:
        is_.update(durum="hata", mesaj=str(hata))
        return
    except Exception as hata:
        is_.update(durum="hata", mesaj=f"Beklenmeyen bir hata oldu: {hata}")
        return

    is_.update(durum="bitti", sahne=sahne, eksikler=eksikler, mesaj="Sahne hazır.")


@app.post("/api/is/{is_id}/uret")
def uret(is_id: str, istek: UretimIstegi):
    tema = _tema_getir(istek.tema)
    if not MOCK_MODE and not os.environ.get("OPENAI_API_KEY"):
        raise HTTPException(503, "Sunucuda OPENAI_API_KEY tanımlı değil.")

    with kilit:
        is_ = _is_getir(is_id)
        if _calisiyor_mu(is_):
            raise HTTPException(409, "Bu fotoğraf için üretim zaten sürüyor.")

        karakter_idleri = {k["id"] for k in tema["karakterler"]}
        yuz_idleri = {y["id"] for y in is_["yuzler"]}
        if not istek.eslesme:
            raise HTTPException(400, "En az bir kişiye karakter vermelisin.")
        if not set(istek.eslesme) <= yuz_idleri or not set(istek.eslesme.values()) <= karakter_idleri:
            raise HTTPException(400, "Eşlemede bu fotoğrafa ya da temaya ait olmayan bir değer var.")
        if len(set(istek.eslesme.values())) != len(istek.eslesme):
            raise HTTPException(400, "Aynı karakter iki kişiye verilemez.")

        is_.update(durum="sirada", tamamlanan=0, toplam=len(istek.eslesme), mesaj="Sırada bekliyor.", sahne=None,
                   eksikler=[], uretim_no=is_.get("uretim_no", 0) + 1)
    isci.submit(_uretim_isi, is_id, istek.tema, istek.eslesme)
    return {"durum": is_["durum"]}


@app.get("/api/is/{is_id}/durum")
def durum(is_id: str):
    is_ = _is_getir(is_id)
    return {
        "durum": is_["durum"],
        "tamamlanan": is_["tamamlanan"],
        "toplam": is_["toplam"],
        "mesaj": is_["mesaj"],
        "eksikler": is_["eksikler"],
        "sahne": f"/api/is/{is_id}/sahne?v={is_['uretim_no']}" if is_["sahne"] else None,
    }


@app.get("/api/is/{is_id}/sahne")
def sahne(is_id: str):
    is_ = _is_getir(is_id)
    if not is_["sahne"]:
        raise HTTPException(404, "Sahne henüz hazır değil.")
    return FileResponse(is_["sahne"], filename="masal_sahnesi.png")


@app.delete("/api/is/{is_id}")
def isi_sil(is_id: str):
    with kilit:
        is_ = _is_getir(is_id)
        if _calisiyor_mu(is_):
            raise HTTPException(409, "Üretim sürerken silinemez, bitmesini bekle.")
        shutil.rmtree(is_["klasor"], ignore_errors=True)
        del isler[is_id]
    return {"silindi": True}


if os.path.isdir(ARAYUZ_KLASORU):
    app.mount("/", StaticFiles(directory=ARAYUZ_KLASORU, html=True), name="arayuz")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
