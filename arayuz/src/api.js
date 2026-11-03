async function istek(yol, secenekler = {}) {
  let yanit;
  try {
    yanit = await fetch(yol, secenekler);
  } catch {
    throw new Error("Sunucuya ulaşılamadı. python api.py çalışıyor mu?");
  }
  const veri = await yanit.json().catch(() => ({}));
  if (!yanit.ok) {
    throw new Error(veri.detail || `Sunucu hatası (${yanit.status})`);
  }
  return veri;
}

function json(metod, govde) {
  return { method: metod, headers: { "Content-Type": "application/json" }, body: JSON.stringify(govde) };
}

export const bilgiGetir = () => istek("/api/bilgi");

export const temalariGetir = () => istek("/api/temalar");

export function fotografYukle(dosya, onay) {
  const form = new FormData();
  form.append("foto", dosya);
  form.append("onay", onay ? "true" : "false");
  return istek("/api/yukle", { method: "POST", body: form });
}

export const eslemeIste = (isId, tema, yuzler) => istek(`/api/is/${isId}/esle`, json("POST", { tema, yuzler }));

export const uretimiBaslat = (isId, tema, eslesme) => istek(`/api/is/${isId}/uret`, json("POST", { tema, eslesme }));

export const durumGetir = (isId) => istek(`/api/is/${isId}/durum`);

export const isiSil = (isId) => istek(`/api/is/${isId}`, { method: "DELETE" });
