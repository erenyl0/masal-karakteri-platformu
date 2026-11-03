import { useEffect, useState } from "react";
import { bilgiGetir, isiSil, temalariGetir } from "./api.js";
import Yukleme from "./adimlar/Yukleme.jsx";
import YuzOnayi from "./adimlar/YuzOnayi.jsx";
import TemaVeEsleme from "./adimlar/TemaVeEsleme.jsx";
import Uretim from "./adimlar/Uretim.jsx";

const ADIMLAR = ["Fotoğraf", "Yüzler", "Tema", "Sahne"];

export default function App() {
  const [bilgi, setBilgi] = useState(null);
  const [temalar, setTemalar] = useState([]);
  const [adim, setAdim] = useState(0);
  const [yukleme, setYukleme] = useState(null);
  const [seciliYuzler, setSeciliYuzler] = useState([]);
  const [tema, setTema] = useState(null);
  const [eslesme, setEslesme] = useState({});
  const [hata, setHata] = useState("");
  const [bildirim, setBildirim] = useState("");

  useEffect(() => {
    bilgiGetir().then(setBilgi).catch(() => setHata("Sunucuya ulaşılamadı. python api.py çalışıyor mu?"));
    temalariGetir().then(setTemalar).catch(() => {});
  }, []);

  function yuklendi(sonuc) {
    setYukleme(sonuc);
    setSeciliYuzler(sonuc.yuzler.map((yuz) => yuz.id));
    setTema(null);
    setEslesme({});
    setBildirim("");
    setAdim(1);
  }

  function yuzSecimiDegisti(yeniSecim) {
    // seçim değişince eski eşleme geçersiz, yoksa çıkarılan kişi görünmeden sahneye girer
    setSeciliYuzler(yeniSecim);
    setTema(null);
    setEslesme({});
  }

  async function bastanBasla(mesaj = "") {
    let silmeHatasi = "";
    if (yukleme) {
      await isiSil(yukleme.is_id).catch((hata) => (silmeHatasi = hata.message));
    }
    setYukleme(null);
    // "Verilerimi sil" denince silme başarısızsa "silindi" demeyelim
    setHata(mesaj && silmeHatasi ? `Silinemedi: ${silmeHatasi}` : "");
    setBildirim(silmeHatasi ? "" : mesaj);
    setAdim(0);
  }

  const seciliYuzVerisi = yukleme ? yukleme.yuzler.filter((yuz) => seciliYuzler.includes(yuz.id)) : [];

  return (
    <div className="sayfa">
      <header>
        <h1>Masal Karakteri</h1>
        <p>Fotoğrafındaki kişileri bir masalın karakterlerine dönüştür.</p>
        {bilgi?.mock && (
          <p className="mock">Deneme modu: görseller gerçekten üretilmiyor, fotoğrafın üstüne etiket basılıyor.</p>
        )}
      </header>

      <ol className="adimlar">
        {ADIMLAR.map((ad, sira) => (
          <li key={ad} className={sira === adim ? "aktif" : sira < adim ? "gecildi" : ""}>
            {ad}
          </li>
        ))}
      </ol>

      {hata && <p className="hata">{hata}</p>}
      {bildirim && <p className="bildirim">{bildirim}</p>}

      {adim === 0 && (
        <Yukleme saklamaSuresi={bilgi?.saklama_suresi_dk ?? 60} onYuklendi={yuklendi} hataGoster={setHata} />
      )}
      {adim === 1 && (
        <YuzOnayi
          yuzler={yukleme.yuzler}
          secili={seciliYuzler}
          setSecili={yuzSecimiDegisti}
          onGeri={() => bastanBasla()}
          onDevam={() => setAdim(2)}
        />
      )}
      {adim === 2 && (
        <TemaVeEsleme
          isId={yukleme.is_id}
          yuzler={seciliYuzVerisi}
          temalar={temalar}
          tema={tema}
          setTema={setTema}
          eslesme={eslesme}
          setEslesme={setEslesme}
          onGeri={() => setAdim(1)}
          onBasladi={() => setAdim(3)}
          hataGoster={setHata}
        />
      )}
      {adim === 3 && (
        <Uretim
          isId={yukleme.is_id}
          onBaskaTema={() => setAdim(2)}
          onYeniFoto={() => bastanBasla()}
          onSil={() => bastanBasla("Fotoğrafın ve üretilen görseller sunucudan silindi.")}
        />
      )}
    </div>
  );
}
