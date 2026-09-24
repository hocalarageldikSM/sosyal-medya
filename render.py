"""HG sosyal medya şablon motoru: JSON veri -> PNG (1080x1350).
Kullanım: python render.py ornek_veri.json cikti_klasoru"""
import json, sys, html, pathlib
from playwright.sync_api import sync_playwright
KOK = pathlib.Path(__file__).parent
T = KOK / "templates"


# ---- Zemin dokusu: kareli defter + karalama + turuncu tarama (bkz. blueprint 4b) ----
import math, random
ZEMIN_TUR = {"duyuru": ("koyu", "#FFFFFF", .13, .55), "karusel_kapak": ("koyu", "#FFFFFF", .13, .55),
             "karusel_son": ("koyu", "#FFFFFF", .13, .55), "haftalik_ozet": ("koyu", "#FFFFFF", .13, .55),
             "tuyo": ("koyu", "#FFFFFF", .14, .9), "karusel_adim": ("acik", "#3A589E", .16, .45),
             "gundem": ("beyaz", "#3A589E", .12, .35), "sube": ("beyaz", "#3A589E", .12, .35)}
NOTLAR = [("x² + y² = r²", 830, 210, 54, -9), ("√2 ≈ 1,41", 60, 1150, 50, 6), ("π", 960, 560, 110, 12),
          ("Δ = b² − 4ac", 610, 1010, 50, -5), ("f(x)", 900, 880, 64, 8), ("%", 120, 690, 90, -12),
          ("H₂O", 880, 1190, 52, -6), ("∑", 470, 1180, 84, 4)]

def zemin(sablon):
    grid, renk, op, to = ZEMIN_TUR[sablon]
    r = random.Random(7)
    yol = lambda pts: "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in pts)
    cx, cy, R = 990, 420, 38
    yildiz = [(cx + (R if i % 2 == 0 else R * .45) * math.cos(-math.pi / 2 + i * math.pi / 5) + r.uniform(-2, 2),
               cy + (R if i % 2 == 0 else R * .45) * math.sin(-math.pi / 2 + i * math.pi / 5) + r.uniform(-2, 2)) for i in range(11)]
    daire = [(170 + (70 + r.uniform(-4, 4)) * math.cos(t / 10), 520 + (56 + r.uniform(-4, 4)) * math.sin(t / 10)) for t in range(75)]
    dalga = [(80 + i * 14, 1265 + 6 * math.sin(i * .9)) for i in range(26)]
    svg = (f'<svg class="zemin" viewBox="0 0 1080 1350" style="opacity:{op}" fill="none" stroke="{renk}" stroke-width="6" '
           f'stroke-linecap="round" stroke-linejoin="round"><path d="{yol(yildiz)}"/><path d="{yol(daire)}"/>'
           '<path d="M700,1120 C760,1070 840,1080 900,1040"/><path d="M872,1030 L902,1040 L885,1068"/>'
           f'<path d="{yol(dalga)}"/><path d="M60,330 L120,230 L175,335 Z"/></svg>')
    notlar = "".join(f'<div class="not-yazi" style="left:{x}px;top:{y}px;font-size:{b}px;transform:rotate({a}deg);'
                     f'color:{renk};opacity:{op}">{t}</div>' for t, x, y, b, a in NOTLAR)
    return (f'<div class="zemin kareli-{grid}"></div><div class="tarama" style="color:#F19107;opacity:{to};'
            f'width:360px;height:300px;right:-110px;top:-90px"></div>{svg}<div class="zemin">{notlar}</div>')

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
        logo = v.get("kaynak_logo")  # resmi kurum logosu dosyası (varsa); yoksa sadece metin rozeti
        ic = f'<img src="{esc(logo)}">' if logo else ''
        alanlar["kaynak_rozet"] = f'<div class="rozet">{ic}<div><small>Kaynak</small><b>{esc(v["kaynak"])}</b></div></div>'
    SERI = {"Öğretmen gündemi": "#3A589E", "Memur gündemi": "#184077", "KPSS gündemi": "#F19107", "Bilgi kartı": "#3A589E"}
    if sablon == "gundem":
        alanlar["seri_renk"] = SERI.get(v["seri"], "#3A589E")
        alanlar["maddeler"] = "".join(f'<div class="madde"><b>{esc(k)}</b><span>{esc(d)}</span></div>' for k, d in v["maddeler"])
        logo = v.get("kaynak_logo")
        ic = f'<img src="{esc(logo)}">' if logo else ''
        alanlar["kaynak_rozet"] = f'<div class="rozet">{ic}<div><small>Kaynak</small><b>{esc(v["kaynak"])}</b></div></div>'
        if str(v.get("kaynak", "")).strip().lower() in ("hocalara geldik", ""):
            alanlar["kaynak_rozet"] = "<div></div>"  # genel tavsiye: kaynak rozeti gosterme
    if sablon == "tuyo":
        o = v.get("ornek")
        alanlar["ornek_kutu"] = f'<div class="ornek"><small>{esc(o[0])}</small><div>{esc(o[1])}</div></div>' if o else ""
        c = v.get("cagri")  # şube çağrısı (isteğe bağlı)
        k = v.get("anahtar")  # DM anahtar kelimesi (ör. PLAN)
        alanlar["alt_blok"] = (f'<div class="cagri"><b style="font-size:{32 if len(str(c)) > 44 else 40}px">{esc(c)}</b>' + (f'<span>{esc(k)}</span>' if k else '') + '</div>' if c
                               else '')  # logo zaten üstte; alta ikinci logo konmaz
    if sablon == "haftalik_ozet":
        R = {"Öğretmen": "#3A589E", "Memur": "#F15725", "KPSS": "#F19107", "LGS": "#3A589E", "YKS": "#F19107"}
        alanlar["ogeler"] = "".join(f'<div class="oge"><i style="background:{R.get(k,"#3A589E")}">{esc(k)}</i><span>{esc(d)}</span></div>' for k, d in v["ogeler"])
    if sablon == "sube":
        alanlar["bilgiler"] = "".join(f'<div><b>{esc(k)}</b><span>{esc(d)}</span></div>' for k, d in v["bilgiler"])
    if sablon == "karusel_adim":
        alanlar["ilerleme"] = "".join(f'<i class="{"on" if i == v["sira"] else ""}"></i>' for i in range(1, v["toplam"] + 1))
    alanlar["baslik_boyut"] = SIGDIR[sablon][0]
    alanlar["zemin"] = zemin(sablon)
    if v.get("sira", 1) % 2 == 0:  # karuselde sayfalar arası çeşitlilik
        s = s.replace('<div class="frame">', '<div class="frame ayna">', 1)
    for k, d in alanlar.items():
        if isinstance(d, (str, int)):
            d = d if k in ("satirlar", "bilgiler", "ilerleme", "kaynak_rozet", "maddeler", "ornek_kutu", "alt_blok", "ogeler", "seri_renk", "zemin") else esc(d)
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
            dosya = is_["dosya"]
            jpg = dosya.lower().endswith((".jpg", ".jpeg"))  # Instagram API yalnizca JPEG kabul eder
            pg.screenshot(path=str(cikti / dosya), **({"type": "jpeg", "quality": 92} if jpg else {}))
            print("ok", is_["dosya"])
        b.close()
    (T / "_gecici.html").unlink(missing_ok=True)

if __name__ == "__main__":
    uret(json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")), sys.argv[2])
