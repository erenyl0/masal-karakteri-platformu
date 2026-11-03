import { useRef, useState } from "react";
import { eslemeIste, uretimiBaslat } from "../api.js";

function karakterDegistir(eslesme, yuzId, karakterId) {
  const yeni = { ...eslesme };
  const onceki = yeni[yuzId];

  // seçilen karakter başka birindeyse ikisi yer değiştirsin
  for (const [digerYuz, digerKarakter] of Object.entries(eslesme)) {
    if (digerKarakter === karakterId && digerYuz !== yuzId) {
      if (onceki) yeni[digerYuz] = onceki;
      else delete yeni[digerYuz];
    }
  }

  if (karakterId) yeni[yuzId] = karakterId;
  else delete yeni[yuzId];
  return yeni;
}

export default function TemaVeEsleme({ isId, yuzler, temalar, tema, setTema, eslesme, setEslesme, onGeri, onBasladi, hataGoster }) {
  const [bekliyor, setBekliyor] = useState(false);
  const sonSecilenTema = useRef(null);
  const secilenTema = temalar.find((t) => t.anahtar === tema);

  async function temaSec(anahtar) {
    setTema(anahtar);
    setEslesme({});
    hataGoster("");
    sonSecilenTema.current = anahtar;
    try {
      const sonuc = await eslemeIste(isId, anahtar, yuzler.map((yuz) => yuz.id));
      // hızlı tıklamada önceki temanın cevabı sonradan gelebilir, onu yok sayıyoruz
      if (sonSecilenTema.current === anahtar) setEslesme(sonuc.eslesme);
    } catch (hata) {
      if (sonSecilenTema.current === anahtar) hataGoster(hata.message);
    }
  }

  async function baslat() {
    setBekliyor(true);
    hataGoster("");
    try {
      await uretimiBaslat(isId, tema, eslesme);
      onBasladi();
    } catch (hata) {
      hataGoster(hata.message);
      setBekliyor(false);
    }
  }

  return (
    <section className="kart">
      <h2>Bir masal seç</h2>
      <div className="temalar">
        {temalar.map((t) => (
          <button key={t.anahtar} className={t.anahtar === tema ? "tema secili" : "tema"} onClick={() => temaSec(t.anahtar)}>
            {t.ad}
          </button>
        ))}
      </div>

      {secilenTema && (
        <>
          <p>Kimin hangi karakter olacağını yaşa ve cinsiyete göre tahmin ettim, istersen değiştir.</p>
          <div className="eslesmeler">
            {yuzler.map((yuz) => (
              <div key={yuz.id} className="eslesme">
                <img src={yuz.gorsel} alt={`${yuz.id} yüzü`} />
                <select
                  value={eslesme[yuz.id] ?? ""}
                  onChange={(olay) => setEslesme(karakterDegistir(eslesme, yuz.id, olay.target.value))}
                >
                  <option value="">Sahneye girmesin</option>
                  {secilenTema.karakterler.map((k) => (
                    <option key={k.id} value={k.id}>
                      {k.ad}
                    </option>
                  ))}
                </select>
              </div>
            ))}
          </div>
        </>
      )}

      <div className="butonlar">
        <button className="ikincil" onClick={onGeri}>
          Geri
        </button>
        <button disabled={!secilenTema || Object.keys(eslesme).length === 0 || bekliyor} onClick={baslat}>
          {bekliyor ? "Başlatılıyor..." : "Sahneyi oluştur"}
        </button>
      </div>
    </section>
  );
}
