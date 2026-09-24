# Hocalara Geldik — Sosyal Medya Görsel Motoru

Yalnızca Hocalara Geldik içindir. Nanomorf varlıkları bu depoya konmaz.

- `MARKA_BLUEPRINT.md` — marka ve içerik kuralları (tek doğruluk kaynağı)
- `templates/` — HTML şablonlar, `logos/` — HG logoları, `fonts/` — fontlar
- `render.py` — JSON işlerden PNG üretir
- `.github/workflows/render.yml` — n8n'in tetiklediği üretim akışı

## Nasıl çalışır
n8n, `HG gorsel uret` iş akışını `paylasim_id` ve `isler` (JSON) ile tetikler.
Görseller `cikti/<paylasim_id>/` altına kaydedilir ve şu adresten erişilir:
`https://raw.githubusercontent.com/<hesap>/<depo>/main/cikti/<paylasim_id>/<dosya>.png`

Yerel deneme: `python render.py ornek/ornek_isler.json cikti/deneme`
