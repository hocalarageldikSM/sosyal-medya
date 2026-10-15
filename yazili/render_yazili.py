"""HG yazılı karuselleri: yazili/veri/<id>.json -> cikti/yazili/<id>/01..NN.jpg (1080x1350).
Kullanım: python yazili/render_yazili.py <id1,id2,...> <cikti_klasoru>"""
import json, sys, html, math, random, pathlib
from playwright.sync_api import sync_playwright

Y = pathlib.Path(__file__).resolve().parent
KOK = Y.parent

RENK = {  # sınıf rengi (ana, koyu)
    9: ("#3A589E", "#184077"), 10: ("#1F8A70", "#0F5A48"),
    11: ("#6B4FA0", "#44306E"), 12: ("#B8323F", "#7A1F2A")}

NOTLAR = [("x² + y² = r²", 830, 210, 54, -9), ("√2 ≈ 1,41", 60, 1150, 50, 6), ("π", 960, 560, 110, 12),
          ("Δ = b² − 4ac", 610, 1010, 50, -5), ("f(x)", 900, 880, 64, 8), ("%", 120, 690, 90, -12),
          ("H₂O", 880, 1190, 52, -6), ("∑", 470, 1180, 84, 4)]

def zemin(koyu, renk, op, to):
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
    izgara = "kareli-koyu" if koyu else "kareli-acik"
    return (f'<div class="zemin {izgara}"></div><div class="tarama" style="color:#F19107;opacity:{to};'
            f'width:360px;height:300px;right:-110px;top:-90px"></div>{svg}<div class="zemin">{notlar}</div>')

def css(ana, koyu):
    return f"""<link href="https://fonts.googleapis.com/css2?family=Luckiest+Guy&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../base.css"><style>
@font-face{{font-family:"Anton";src:url("../Anton-Regular.ttf");}}
@font-face{{font-family:"Montserrat";src:url("../Montserrat.ttf");font-weight:100 900;}}
@font-face{{font-family:"Caveat";src:url("../Caveat.ttf");font-weight:400 700;}}
@font-face{{font-family:"LuckyYerel";src:local("Luckiest Guy"),url("LuckiestGuy.ttf");}}
:root{{--ana:{ana};--koyu:{koyu}}}
.lucky,.no,.etiket,.h,.n{{font-family:"Luckiest Guy","LuckyYerel";font-weight:400;letter-spacing:1px}}
.lucky{{line-height:1.05}}
.kok{{border-top:3px solid currentColor;padding-top:2px}}
sup,sub{{font-size:62%;line-height:0}}
.logo{{position:absolute!important;left:50%;transform:translateX(-50%);height:118px;bottom:46px}}
.ilerleme{{position:absolute!important;left:80px;bottom:88px;display:flex;gap:8px}}
.ilerleme i{{width:26px;height:8px;border-radius:4px;background:#C9D3E8}}.ilerleme i.on{{background:#F19107}}
.sayfa{{position:absolute!important;right:80px;bottom:84px;font:700 24px Montserrat;color:#5A6F95}}
</style>"""

LOGO = '<img class="logo hg-logo" src="../bm_kutu_planlama.png">'

def sayfa(ana, koyu, govde, z, ayna=False, ek=""):
    return (f'<!doctype html><html lang="tr"><head><meta charset="utf-8">{css(ana, koyu)}<style>{ek}</style></head>'
            f'<body><div class="frame{" ayna" if ayna else ""}">{z}{govde}</div></body></html>')

KAPAK = """.frame{background:var(--ana);color:#fff;padding:110px 84px}
.amblem{position:absolute;left:50%;top:560px;width:960px;transform:translateX(-50%) rotate(-8deg);opacity:.09}
.etiket{background:#F19107;font-size:46px;padding:20px 36px 14px}
h1{font-size:150px;margin-top:70px}
h1 span{display:inline-block;background:#F19107;color:var(--koyu);padding:18px 26px 4px;border-radius:18px;transform:rotate(-2.5deg);margin-top:18px}
.el{font-family:Caveat;font-weight:700;font-size:70px;color:#FFD08A;margin-top:40px;transform:rotate(-3deg)}
.alt{margin-top:46px;font-size:38px;font-weight:600;line-height:1.4;max-width:860px}
.kaydir{position:absolute!important;left:84px;bottom:200px;font-size:30px;font-weight:700;display:flex;align-items:center;gap:18px}
.kaydir i{display:block;width:84px;height:6px;background:#F19107;border-radius:3px}
.logo{height:150px;bottom:56px}"""

SORU = """.frame{background:#F2F5FB;padding:84px 80px 190px}
.cizgi{position:absolute!important;left:0;top:0;bottom:0;width:18px;background:var(--ana)}
.ust{display:flex;align-items:center;gap:26px}
.no{font-size:118px;color:#F19107;line-height:.9;padding-top:12px}
.kaz{background:var(--ana);color:#fff;font:700 24px Montserrat;padding:10px 20px;border-radius:14px;transform:rotate(-2.5deg)}
.govde{margin-top:44px;font-size:var(--fs,41px);font-weight:500;line-height:1.45;color:#184077}
.govde i{font-family:serif;font-size:110%}
.mad{margin-top:26px;background:#fff;border-radius:22px;padding:20px 26px;box-shadow:0 4px 0 #dfe6f3;display:flex;gap:18px}
.mad .h{color:#F19107;font-size:1.15em;line-height:1.1;flex:0 0 auto}
.puan{color:#5A6F95;font-weight:700;font-size:.72em;white-space:nowrap}
.fig{text-align:center;margin:18px 0 4px}
table{border-collapse:collapse;margin:18px auto 0;background:#fff;font-size:.8em}
td,th{border:2px solid #9fb3d8;padding:6px 18px;text-align:center}th{background:var(--ana);color:#fff}"""

CEVAP = """.frame{background:var(--koyu);color:#fff;padding:84px 80px 190px}
h2{font-size:84px}h2 span{color:#F19107}
.cv{margin-top:28px;display:flex;flex-direction:column;gap:16px;font-size:var(--fs,33px)}
.c{background:rgba(255,255,255,.08);border-left:8px solid #F19107;border-radius:16px;padding:14px 22px;line-height:1.42;font-weight:500}
.c .n{color:#F19107;font-size:1.25em;margin-right:10px}
.c i{font-family:serif;font-size:110%}"""

SON = """.frame{background:var(--koyu);color:#fff;padding:96px 88px;display:flex;flex-direction:column;justify-content:center}
h2{font-size:104px}h2 span{color:#F19107}
.metin{margin-top:40px;font-size:40px;font-weight:600;line-height:1.42;max-width:880px}
.etiket{background:#F19107;margin-top:60px;align-self:flex-start;font-size:48px;padding:22px 36px 14px}
.logo{width:440px;height:auto;bottom:70px}"""

def tablo(t):
    if not t: return ""
    b = "".join(f"<th>{x}</th>" for x in t["basliklar"])
    s = "".join("<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>" for r in t["satirlar"])
    return f"<table><tr>{b}</tr>{s}</table>"

def sayfalar(d):
    ana, koyu = RENK[int(d["sinif"])]
    zk = lambda: zemin(True, "#FFFFFF", .13, .55)
    za = lambda: zemin(False, ana, .16, .45)
    tr = lambda x: x.replace("i", "İ").replace("ı", "I").upper()
    etiket = f'{d["sinif"]}. SINIF {tr(d.get("kisa_ad", d["ders"]))}'
    out = [sayfa(ana, koyu, f"""<img class="amblem" src="../amblem_beyaz.png" style="position:absolute">
<div class="etiket">{etiket}</div>
<h1 class="lucky">1. DÖNEM<br><span>1. YAZILI</span></h1>
<div class="el">{html.escape(d.get("program", "Maarif Modeli"))} · 10 soru</div>
<p class="alt">Kazanımlara uygun 10 yazılı sorusu. Kaydet, çöz, cevapları son sayfalarda kontrol et.</p>
<div class="kaydir"><i></i>Kaydır</div>{LOGO}""", zk(), ek=KAPAK)]
    for n, s in enumerate(d["sorular"], 1):
        md = "".join(f'<div class="mad"><span class="h">{m["h"].upper()})</span><div>{m["t"]} <span class="puan">({m["puan"]} puan)</span></div></div>'
                     for m in s["maddeler"])
        ilr = "".join(f'<i class="{"on" if i == n else ""}"></i>' for i in range(1, 11))
        g = (f'<div class="cizgi"></div><div class="ust"><div class="no">SORU {n}</div><div class="kaz">{s["kazanim"]}</div></div>'
             f'<div class="govde">{s["metin"]}{s.get("svg", "")}{tablo(s.get("tablo"))}{md}</div>'
             f'<div class="ilerleme">{ilr}</div><div class="sayfa">{n} / 10</div>{LOGO}')
        out.append(sayfa(ana, koyu, g, za(), ayna=n % 2 == 0, ek=SORU))
    C = d["cevaplar"]
    for k, (a, b) in enumerate([(0, 5), (5, 10)], 1):
        c = "".join(f'<div class="c"><span class="n">{i + 1}</span>{C[i]}</div>' for i in range(a, b))
        out.append(sayfa(ana, koyu, f'<h2 class="lucky">CEVAP <span>ANAHTARI</span> {k}/2</h2><div class="cv">{c}</div>{LOGO}',
                         zk(), ayna=k == 2, ek=CEVAP))
    out.append(sayfa(ana, koyu, f"""<h2 class="lucky">YAZILIYA<br><span>HAZIR MISIN?</span></h2>
<p class="metin">{html.escape(d["kanca"])}</p>
<div class="etiket">BAŞARI MERKEZİNE #GEL.</div>{LOGO}""", zk(), ek=SON))
    return out

def uret(kimlik, cikti):
    tek = Y / "veri" / f"{kimlik}.json"
    d = (json.loads(tek.read_text(encoding="utf-8")) if tek.exists()
         else json.loads((Y / "veri" / f"{kimlik.split('_')[0]}.json").read_text(encoding="utf-8"))[kimlik])
    cikti = pathlib.Path(cikti); cikti.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for n, h in enumerate(sayfalar(d), 1):
            f = Y / "_gecici.html"; f.write_text(h, encoding="utf-8")
            pg.goto(f.as_uri(), wait_until="networkidle"); pg.evaluate("document.fonts.ready")
            for _ in range(20):  # içerik logo alanına taşarsa yazıyı küçült
                alt = pg.evaluate("()=>{const e=document.querySelector('.govde,.cv');return e?e.getBoundingClientRect().bottom:0}")
                if alt <= 1170: break
                pg.evaluate("()=>{const e=document.querySelector('.govde,.cv');const fs=parseFloat(getComputedStyle(e).fontSize);e.style.setProperty('--fs',(fs-1.5)+'px')}")
            if alt > 1170: print("UYARI taşma", kimlik, n, alt)
            pg.screenshot(path=str(cikti / f"{n:02d}.jpg"), type="jpeg", quality=90)
        b.close()
        (Y / "_gecici.html").unlink(missing_ok=True)
    print("ok", kimlik, n, "sayfa")

if __name__ == "__main__":
    kok = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else pathlib.Path("cikti/yazili")
    for k in sys.argv[1].split(","):
        uret(k.strip(), kok / k.strip())
