export default function YuzOnayi({ yuzler, secili, setSecili, onGeri, onDevam }) {
  function degistir(id) {
    setSecili(secili.includes(id) ? secili.filter((s) => s !== id) : [...secili, id]);
  }

  const uyariVar = yuzler.some((yuz) => yuz.uyarilar.length > 0);

  return (
    <section className="kart">
      <h2>{yuzler.length} yüz bulundu</h2>
      <p>Sahneye girmesini istemediğin kişilerin işaretini kaldır.</p>

      <div className="yuzler">
        {yuzler.map((yuz) => (
          <label key={yuz.id} className={secili.includes(yuz.id) ? "yuz secili" : "yuz"}>
            <input type="checkbox" checked={secili.includes(yuz.id)} onChange={() => degistir(yuz.id)} />
            <img src={yuz.gorsel} alt={`${yuz.id} yüzü`} />
            {yuz.yas != null && <span>tahmini yaş {yuz.yas}</span>}
            {yuz.uyarilar.map((uyari) => (
              <span key={uyari} className="uyari">
                {uyari}
              </span>
            ))}
          </label>
        ))}
      </div>

      {uyariVar && (
        <p className="ipucu">Uyarı olan yüzlerde sonuç kötü çıkabilir. İstersen daha iyi bir fotoğraf yükleyebilirsin.</p>
      )}

      <div className="butonlar">
        <button className="ikincil" onClick={onGeri}>
          Başka fotoğraf yükle
        </button>
        <button disabled={secili.length === 0} onClick={onDevam}>
          Devam
        </button>
      </div>
    </section>
  );
}
