import { useEffect, useState } from "react";
import { durumGetir } from "../api.js";

export default function Uretim({ isId, onBaskaTema, onYeniFoto, onSil }) {
  const [durum, setDurum] = useState({ durum: "sirada", tamamlanan: 0, toplam: 0, mesaj: "Sırada bekliyor.", eksikler: [] });

  useEffect(() => {
    let iptal = false;
    const zamanlayici = setInterval(async () => {
      try {
        const yeni = await durumGetir(isId);
        if (iptal) return;
        setDurum(yeni);
        if (yeni.durum === "bitti" || yeni.durum === "hata") clearInterval(zamanlayici);
      } catch (hata) {
        clearInterval(zamanlayici);
        // sunucu kapandıysa ya da iş silindiyse ekranda takılı kalmasın, butonlar görünsün
        if (!iptal) setDurum((eski) => ({ ...eski, durum: "hata", mesaj: hata.message }));
      }
    }, 1000);

    return () => {
      iptal = true;
      clearInterval(zamanlayici);
    };
  }, [isId]);

  const bitti = durum.durum === "bitti";
  const basarisiz = durum.durum === "hata";
  const yuzde = bitti ? 100 : durum.toplam ? Math.round((durum.tamamlanan / durum.toplam) * 100) : 0;

  return (
    <section className="kart">
      <h2>{bitti ? "Sahnen hazır" : basarisiz ? "Sahne oluşturulamadı" : "Sahne hazırlanıyor"}</h2>

      {!bitti && !basarisiz && (
        <>
          <div className="ilerleme">
            <div style={{ width: `${yuzde}%` }} />
          </div>
          <p>
            {durum.mesaj}
            {durum.toplam > 0 && ` (${durum.tamamlanan}/${durum.toplam})`}
          </p>
        </>
      )}

      {basarisiz && <p className="hata">{durum.mesaj}</p>}

      {bitti && (
        <>
          <img className="sahne" src={durum.sahne} alt="Oluşturulan masal sahnesi" />
          {durum.eksikler.length > 0 && (
            <p className="ipucu">Şu karakterler üretilemediği için sahnede yok: {durum.eksikler.join(", ")}.</p>
          )}
          <a className="buton" href={durum.sahne} download="masal_sahnesi.png">
            İndir
          </a>
        </>
      )}

      {(bitti || basarisiz) && (
        <div className="butonlar">
          <button className="ikincil" onClick={onBaskaTema}>
            Başka masal dene
          </button>
          <button className="ikincil" onClick={onYeniFoto}>
            Yeni fotoğraf
          </button>
          <button className="tehlike" onClick={onSil}>
            Verilerimi sil
          </button>
        </div>
      )}
    </section>
  );
}
