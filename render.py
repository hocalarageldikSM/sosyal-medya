"""HG sosyal medya şablon motoru: JSON veri -> PNG (1080x1350).
Kullanım: python render.py ornek_veri.json cikti_klasoru"""
import json, sys, html, pathlib
from playwright.sync_api import sync_playwright
KOK = pathlib.Path(__file__).parent
T = KOK / "templates"

def esc(s): return html.escape(str(s))

# Başlık alanı: başlangıç puntosu ve izin verilen maksimum yükseklik (px)
SIGDIR = {"gundem": (104, 330), "tuyo": (84, 260), "haftalik_ozet": (96, 220), "duyuru": (118, 380), "sube": (112, 260), "karusel_kapak": (150, 560),
          "karusel_adim": (88, 300), "karusel_son": (104, 440)}

def doldur(sablon, v):
    s = (T / f"{sablon}.html").read_text(encoding="utf-8")
    alanlar = dict(v)
    if sablon == "duyuru":
        alanlar["satirlar"] = "".join(f'<div class="satir"><b>{esc(k)}</b><span>{esc(d)}</span></div>' for k, d in v["satirlar"])
    if sablon == "duyuru":
        logo = v.get("kaynak_logo")  # resmi kurum logosu dosyası (varsa); yoksa metin rozeti
        ic = f'<img src="{esc(logo)}">' if logo else f'<div class="yer">{esc(v["kaynak"])}<br>logosu</div>'
        alanlar["kaynak_rozet"] = f'<div class="rozet">{ic}<div><small>Kaynak</small><b>{esc(v["kaynak"])}</b></div></div>'
    SERI = {"Öğretmen gündemi": "#3A589E", "Memur gündemi": "#184077", "KPSS gündemi": "#F19107", "Bilgi kartı": "#3A589E"}
    if sablon == "gundem":
        alanlar["seri_renk"] = SERI.get(v["seri"], "#3A589E")
        alanlar["maddeler"] = "".join(f'<div class="madde"><b>{esc(k)}</b><span>{esc(d)}</span></div>' for k, d in v["maddeler"])
        logo = v.get("kaynak_logo")
        ic = f'<img src="{esc(logo)}">' if logo else f'<div class="yer">{esc(v["kaynak"])}<br>logosu</div>'
        alanlar["kaynak_rozet"] = f'<div class="rozet">{ic}<div><small>Kaynak</small><b>{esc(v["kaynak"])}</b></div></div>'
    if sablon == "tuyo":
        o = v.get("ornek")
        alanlar["ornek_kutu"] = f'<div class="ornek"><small>{esc(o[0])}</small><div>{esc(o[1])}</div></div>' if o else ""
        c = v.get("cagri")  # şube çağrısı (isteğe bağlı)
        k = v.get("anahtar")  # DM anahtar kelimesi (ör. PLAN)
        alanlar["alt_blok"] = (f'<div class="cagri"><b>{esc(c)}</b>' + (f'<span>{esc(k)}</span>' if k else '') + '</div>' if c
                               else '')  # logo zaten üstte; alta ikinci logo konmaz
    if sablon == "haftalik_ozet":
        R = {"Öğretmen": "#3A589E", "Memur": "#F15725", "KPSS": "#F19107", "LGS": "#3A589E", "YKS": "#F19107"}
        alanlar["ogeler"] = "".join(f'<div class="oge"><i style="background:{R.get(k,"#3A589E")}">{esc(k)}</i><span>{esc(d)}</span></div>' for k, d in v["ogeler"])
    if sablon == "sube":
        alanlar["bilgiler"] = "".join(f'<div><b>{esc(k)}</b><span>{esc(d)}</span></div>' for k, d in v["bilgiler"])
    if sablon == "karusel_adim":
        alanlar["ilerleme"] = "".join(f'<i class="{"on" if i == v["sira"] else ""}"></i>' for i in range(1, v["toplam"] + 1))
    alanlar["baslik_boyut"] = SIGDIR[sablon][0]
    if v.get("sira", 1) % 2 == 0:  # karuselde sayfalar arası çeşitlilik
        s = s.replace('<div class="frame">', '<div class="frame ayna">', 1)
    for k, d in alanlar.items():
        if isinstance(d, (str, int)):
            d = d if k in ("satirlar", "bilgiler", "ilerleme", "kaynak_rozet", "maddeler", "ornek_kutu", "alt_blok", "ogeler", "seri_renk") else esc(d)
            s = s.replace("{{" + k + "}}", str(d))
    return s

def uret(isler, cikti):
    cikti = pathlib.Path(cikti); cikti.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for is_ in isler:
            gecici = T / "_gecici.html"
            gecici.write_text(doldur(is_["sablon"], is_["veri"]), encoding="utf-8")
            pg.goto(gecici.as_uri()); pg.evaluate("document.fonts.ready")
            # başlığı alana sığana kadar küçült (taşma olmasın)
            maks = SIGDIR[is_["sablon"]][1]
            pg.evaluate("""(maks)=>{const h=document.querySelector('h1,h2');if(!h)return;
              let f=parseFloat(getComputedStyle(h).fontSize);
              while(h.getBoundingClientRect().height>maks && f>40){f-=4;h.style.fontSize=f+'px';}}""", maks)
            tasma = pg.evaluate("""()=>[...document.querySelectorAll('.frame *')].filter(e=>{const r=e.getBoundingClientRect();
              return r.bottom>1350.5||r.right>1080.5}).filter(e=>!e.classList.contains('amblem')&&!e.classList.contains('tarama')).map(e=>e.className||e.tagName)""")
            if tasma: print("UYARI taşma:", is_["dosya"], tasma)
            pg.screenshot(path=str(cikti / is_["dosya"]))
            print("ok", is_["dosya"])
        b.close()
    (T / "_gecici.html").unlink(missing_ok=True)

if __name__ == "__main__":
    uret(json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")), sys.argv[2])
