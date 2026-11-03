import { useState } from "react";
import { fotografYukle } from "../api.js";

export default function Yukleme({ saklamaSuresi, onYuklendi, hataGoster }) {
  const [dosya, setDosya] = useState(null);
  const [onizleme, setOnizleme] = useState(null);
  const [onay, setOnay] = useState(false);
  const [bekliyor, setBekliyor] = useState(false);

  function dosyaSecildi(olay) {
    const secilen = olay.target.files[0];
    if (!secilen) return;
    if (onizleme) URL.revokeObjectURL(onizleme);
    setDosya(secilen);
    setOnizleme(URL.createObjectURL(secilen));
  }

  async function gonder() {
    setBekliyor(true);
    hataGoster("");
    try {
      onYuklendi(await fotografYukle(dosya, onay));
    } catch (hata) {
      hataGoster(hata.message);
      setBekliyor(false);
    }
  }

  return (
    <section className="kart">
      <h2>Fotoğrafını yükle</h2>
      <p>Tek kişilik ya da aile fotoğrafı olabilir. Yüzlerin karşıdan ve net göründüğü fotoğraflar en iyi sonucu verir.</p>

      <label className="dosya-sec">
        <input type="file" accept="image/jpeg,image/png" onChange={dosyaSecildi} />
        {dosya ? dosya.name : "Fotoğraf seç"}
      </label>
      {onizleme && <img className="onizleme" src={onizleme} alt="Seçilen fotoğraf" />}

      <label className="onay">
        <input type="checkbox" checked={onay} onChange={(olay) => setOnay(olay.target.checked)} />
        <span>
          Fotoğraftaki kişiler ben ya da ailem, fotoğrafın sahne üretmek için işlenmesine izin veriyorum.
          Fotoğraf {saklamaSuresi} dakika sonra ya da ben silince sunucudan silinir.
        </span>
      </label>

      <button disabled={!dosya || !onay || bekliyor} onClick={gonder}>
        {bekliyor ? "Yüzler aranıyor..." : "Yüzleri bul"}
      </button>
      {bekliyor && <p className="ipucu">İlk seferde yüz tanıma modelleri yüklendiği için biraz sürebilir.</p>}
    </section>
  );
}
