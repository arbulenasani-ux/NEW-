#!/usr/bin/env python3
# Builds a single self-contained HTML "project kit" referencing the Higgsfield CDN assets.
BASE = "https://d8j0ntlcm91z4.cloudfront.net/user_3F6CCcooWfznOndonNAH5iSkbmh/"

images = [
    ("01", "Berlin stirbt – Weitwinkel Ruinen", "hf_20260613_225728_94e56418-bbad-4406-b895-2a3da21a5678.png"),
    ("02", "Reichskanzlei-Garten / Bunkereingang", "hf_20260613_225731_bab376ac-1587-4bda-8f7f-91aded377b10.png"),
    ("03", "Bunkerflur – zwei Offiziere", "hf_20260613_225734_cb7db5fd-04f2-4a49-8f83-ef9a6460cb0f.png"),
    ("04", "Diktator am Kartentisch (von hinten)", "hf_20260613_225736_f9234a18-cece-43f2-b7a3-b26027174aec.png"),
    ("05", "Karge Trauung im Bunker", "hf_20260613_225826_801b6542-c1bb-45b4-97c8-7f1bb7c84d43.png"),
    ("06", "Sowjetische Soldaten in Trümmerstraße", "hf_20260613_225743_6e84c954-246b-4377-97a3-bbf29fb69b14.png"),
    ("07", "Geschlossene Tür am Flurende", "hf_20260613_225744_0f56cf19-028c-4139-82d3-59b22bd4389d.png"),
    ("08", "Nachwirkung – weiße Kapitulationsflagge", "hf_20260613_225747_81a42d93-ec67-467a-bf3e-e5bf4dfd69cf.png"),
    ("09", "Zitternde Hände auf der Karte", "hf_20260613_231011_37bd212d-6b2b-4b62-9691-0b8238814fc9.png"),
    ("10", "Leerer Lagebesprechungsraum", "hf_20260613_231012_9bfe8eac-c55f-4a77-9a28-7da2529ef0e7.png"),
    ("11", "Nächtliches Artilleriefeuer über Berlin", "hf_20260613_231014_6c8f849b-9797-4838-9645-47cb8692285e.png"),
    ("12", "Funker im Bunker", "hf_20260613_231016_96e90708-42f1-481d-9675-26052c19a696.png"),
    ("13", "Einzelne Frau (Eva-Motiv)", "hf_20260613_231019_10a5d01e-de21-47cf-ac93-3993db40a914.png"),
    ("14", "Offiziere in angespannter Beratung", "hf_20260613_231021_34a04018-56f8-4fb1-8d56-4f6f2d56ea6b.png"),
    ("15", "Langer leerer Bunkerflur", "hf_20260613_231024_4260982e-83e4-4022-b02c-2ff5eabbcb3a.png"),
    ("16", "Heruntergebrannte Kerze + Taschenuhr", "hf_20260613_231025_33cded3d-ca6e-4e98-a53c-f4f8b77696b3.png"),
    ("17", "Luftbild zerstörtes Berlin (Dämmerung)", "hf_20260613_231028_ba09d6b9-cee9-4310-87d7-26ac8d6c5029.png"),
    ("18", "Historiker-Schreibtisch (Reflexion)", "hf_20260613_231030_b284817a-832c-4c3e-aa8e-3cd954681020.png"),
]

vo = [
    ("HOOK", "Come closer to the fire...", "hf_20260613_231111_642cc074-f683-4d66-a875-75129dfda66c.wav"),
    ("S1", "April 30th, 1945. The city of Berlin was dying...", "hf_20260613_231113_0e8a7718-6e82-452d-a3b9-85fdbedb6549.wav"),
    ("S2", "His armies had collapsed...", "hf_20260613_231116_624630c5-c95e-449f-ac54-63a1359b1c98.wav"),
    ("S3", "For years, Hitler had believed... The end had arrived.", "hf_20260613_231118_9384c48a-8cbd-4d22-9592-539d829267fc.wav"),
    ("S4", "Witnesses later described Hitler as physically broken...", "hf_20260613_231120_c465eee6-653d-453e-8ef6-826be8734e9b.wav"),
    ("S5", "Around him, bunker staff moved through the cramped passages...", "hf_20260613_231138_2927abe1-d458-4f95-b7ca-5abaf4131e7b.wav"),
    ("S6", "Just one day earlier, Hitler had married Eva Braun...", "hf_20260613_231140_4adecbfd-ef17-4b89-a060-bf550f77b6df.wav"),
    ("S7", "As the morning wore on, Hitler met with his inner circle...", "hf_20260613_231141_792b6b42-eebb-406c-aaa6-8c9537c7b8e5.wav"),
    ("S8", "Outside, Soviet soldiers advanced through the rubble...", "hf_20260613_231144_2bb3536a-485c-4efd-86fb-d93e04bcdb3e.wav"),
    ("S9", "Then, shortly after midday, Hitler withdrew...", "hf_20260613_231146_02e17701-2951-4a41-b258-8e48fb1893f9.wav"),
    ("S10", "And then came the sound. A single gunshot...", "hf_20260613_231155_24f7430e-74f3-4796-a7b7-1d8dd2a1806f.wav"),
    ("S11", "Yet outside the bunker, the battle for Berlin still raged...", "hf_20260613_231230_00590a9c-d7ae-4f41-a152-cbf92b4732c9.wav"),
    ("S12", "Even now, decades later, historians still return...", "hf_20260613_231233_9dc5c35d-8573-42b1-ae1d-7afe8ac37fd6.wav"),
    ("OUTRO", "The fire burns low, and the story ends...", "hf_20260613_231235_9232c965-6560-4045-be55-e27a51579292.wav"),
]

music = [
    ("M1 – getragen/düster (Bett unter Erzählung)", "hf_20260613_231035_7b0f8234-3957-4c73-a01f-e79ce6719afc.m4a"),
    ("M2 – dunkel/spannungsvoll", "hf_20260613_231038_5ea6c58d-8ccf-450f-8fe4-a94d16ec95b8.m4a"),
    ("M3 – melancholisches Ende", "hf_20260613_231040_4f9d468e-f1f6-4505-b0cc-763388e7cb12.m4a"),
]

# Storyboard: segment -> recommended image numbers (Ken-Burns reihenfolge)
timeline = [
    ("HOOK", "00:00", "01", "M1"),
    ("S1", "~00:15", "01 → 11", "M1"),
    ("S2", "~00:45", "11 → 02", "M1"),
    ("S3", "~01:20", "04 → 09", "M1"),
    ("S4", "~01:55", "09 → 04", "M1"),
    ("S5", "~02:30", "03 → 10 → 12", "M1"),
    ("S6", "~03:15", "05 → 13", "M2"),
    ("S7", "~03:55", "14 → 04", "M2"),
    ("S8", "~04:35", "06 → 11", "M2"),
    ("S9", "~05:20", "15 → 07 → 16", "M2"),
    ("S10", "~06:05", "07 → 16", "M2"),
    ("S11", "~06:45", "08 → 17", "M3"),
    ("S12", "~07:35", "17 → 18", "M3"),
    ("OUTRO", "~09:30", "16 → 18", "M3"),
]

def img(u): return BASE + u

rows_tl = "\n".join(
    f"<tr><td><b>{s}</b></td><td>{t}</td><td>{im}</td><td>{m}</td></tr>" for s,t,im,m in timeline
)
cards_img = "\n".join(
    f'''<div class="card"><img loading="lazy" src="{img(f)}"><div class="cap"><b>Bild {n}</b> – {d}<br><a href="{img(f)}" download>⬇ Download PNG</a></div></div>'''
    for n,d,f in images
)
rows_vo = "\n".join(
    f'''<div class="arow"><div class="lab"><b>{k}</b><br><span>{t}</span></div><audio controls preload="none" src="{img(f)}"></audio><a href="{img(f)}" download>⬇</a></div>'''
    for k,t,f in vo
)
rows_mu = "\n".join(
    f'''<div class="arow"><div class="lab"><b>{name}</b></div><audio controls preload="none" src="{img(f)}"></audio><a href="{img(f)}" download>⬇</a></div>'''
    for name,f in music
)

html = f"""<!doctype html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Doku-Projektmappe – Hitlers letzte Stunden</title>
<style>
body{{font-family:system-ui,Arial,sans-serif;background:#111;color:#eee;margin:0;padding:18px;max-width:1100px;margin:auto}}
h1{{font-size:1.4rem}} h2{{margin-top:34px;border-bottom:1px solid #444;padding-bottom:6px}}
.note{{background:#1d1d1d;border-left:4px solid #c0883a;padding:12px 14px;border-radius:6px;font-size:.92rem;line-height:1.5}}
table{{width:100%;border-collapse:collapse;font-size:.9rem}} td,th{{border:1px solid #333;padding:6px 8px;text-align:left}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px}}
.card img{{width:100%;border-radius:6px;display:block}} .cap{{font-size:.82rem;margin-top:5px;line-height:1.35}}
a{{color:#e0a955}} .arow{{display:flex;align-items:center;gap:12px;padding:7px 0;border-bottom:1px solid #2a2a2a;flex-wrap:wrap}}
.lab{{min-width:230px;font-size:.85rem}} .lab span{{color:#aaa}} audio{{height:34px}}
</style></head><body>
<h1>🎬 Doku-Projektmappe · „Hitlers letzte Stunden" · ~10 Min · 16:9</h1>
<div class="note"><b>So nutzt du das:</b> Lade unten alle Bilder (18) und Audios (14 Erzähl-Spuren + 3 Musik) herunter.
Importiere sie in CapCut / DaVinci Resolve / Premiere. Lege die Erzähl-Spuren HOOK→S1→…→OUTRO hintereinander auf eine Tonspur,
darunter die Musik (leiser, ~ -18 dB, „Ducking"). Lege über jede Erzähl-Spur das passende Bild (siehe Timeline) mit langsamem
Zoom („Ken Burns"). Exportiere 1920×1080, dann auf YouTube hochladen.<br><br>
<b>Hinweis:</b> Eine fertig gerenderte MP4 konnte hier nicht erzeugt werden, weil die Render-Umgebung keinen Netzwerkzugriff auf den
Datei-Server hatte. Sobald der Host <code>d8j0ntlcm91z4.cloudfront.net</code> in der Egress-Allowlist freigegeben ist, kann die fertige
Datei automatisch erzeugt werden.</div>

<h2>🎞️ Timeline / Schnittplan</h2>
<table><tr><th>Abschnitt</th><th>Start ≈</th><th>Bild(er)</th><th>Musik</th></tr>
{rows_tl}
</table>
<p style="font-size:.82rem;color:#aaa">Startzeiten sind Richtwerte – richte jedes Bild exakt nach der Länge der zugehörigen Erzähl-Spur aus.</p>

<h2>🗣️ Erzählung / Voiceover (Stimme: Theodore)</h2>
{rows_vo}

<h2>🎵 Musik-Tracks</h2>
{rows_mu}

<h2>🖼️ Bilder (18)</h2>
<div class="grid">
{cards_img}
</div>
</body></html>"""

with open("/home/user/NEW-/doku_kit/Doku_Projektmappe.html","w") as f:
    f.write(html)
print("written", len(html), "bytes")
