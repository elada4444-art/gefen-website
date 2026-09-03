"""Build a self-contained browser preview of the explainer: the animation stage + narration audio, in a player shell."""
import base64, json, pathlib, subprocess
S = pathlib.Path("/tmp/claude-0/-home-user-gefen-website/d7cc3944-8b91-561b-b675-19160c1e1a80/scratchpad")
V = S / "video"
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
opus = V / "out" / "mix.opus"
subprocess.run([FF, "-y", "-v", "error", "-i", str(V / "out" / "mix.wav"), "-ac", "1", "-ar", "48000", "-c:a", "libopus", "-b:a", "40k", str(opus)], check=True)
audio_uri = "data:audio/ogg;base64," + base64.b64encode(opus.read_bytes()).decode()
logo_uri = "data:image/png;base64," + base64.b64encode(pathlib.Path("/home/user/gefen-website/assets/logo.png").read_bytes()).decode()
timeline = json.loads((V / "timeline.json").read_text())
anim = (V / "anim.html").read_text()

# pull the stage markup + its <style> + <script> out of anim.html
style = anim.split("<style>")[1].split("</style>")[0].replace("/* __FONTS__ */", "")
style = style.replace("html,body{margin:0;padding:0;background:var(--navy-deep);}", "").replace("body{font-family:", "#stage{font-family:")
stage = anim.split('<div id="stage">')[1].split("\n<script>")[0]
stage = '<div id="stage">' + stage
script = anim.split("<script>")[1].split("</script>")[0]
script = script.replace("window.TIMELINE = window.TIMELINE ||", "window.TIMELINE = " + json.dumps(timeline, ensure_ascii=False) + " ||")
script = script.replace("if(!window.__RENDER_MODE__){", "if(false){")
stage = stage.replace("__LOGO__", logo_uri)

total = round(sum(s["dur"] for s in timeline["scenes"]), 1)
facts = [
 ("21.8 מיליארד ₪", "גיוסים לפוליסות חיסכון, מחצית ראשונה 2026 (לעומת 13.9 מיליארד אשתקד, +57%)"),
 ("הפניקס · 7.55 מיליארד ₪", "מקום ראשון, עלייה של 18% לעומת 6.37 מיליארד במחצית הראשונה של 2025"),
 ("איילון · 3.19 מיליארד ₪", "מקום שני, מ-315 מיליון ₪ בלבד אשתקד (כ-910%+)"),
 ("מגדל · הכשרה", "מגדל שלישית בפער קטן מאיילון; הכשרה עם כ-2.5 מיליארד ₪"),
 ("ביטוח ישיר · 160 מיליון ₪", "לעומת 52 מיליון אשתקד, עלייה של כ-208%"),
 ("איילון גמל · כ-1 מיליארד ₪", "הערכות בענף לגיוסים בקופות הגמל וההשתלמות של איילון כבר בחודש הפעילות הראשון"),
]
facts_html = "".join(f'<div class="fact"><div class="fv">{a}</div><div class="fl">{b}</div></div>' for a, b in facts)
lines = (S / "video" / "narration.txt").read_text().strip().splitlines()
script_html = "".join(f'<li>{l}</li>' for l in lines)

page = f"""<title>גיוסי פוליסות החיסכון 2026</title>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;600;800;900&display=swap">
<style>
:root{{--navy:#1c2a4a;--navy-deep:#121d36;--navy-soft:#26365e;--orange:#f07d1a;--orange-soft:#ffa14e;--cream:#f7f4ee;--green:#25d366;--white:#ffffff;
  --page:#f7f4ee;--ink:#1c2a4a;--ink-soft:#4a5673;--rule:#e2dccf;--panel:#ffffff;--accent:#f07d1a;}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--page:#0e1628;--ink:#f7f4ee;--ink-soft:#aeb7cc;--rule:#26365e;--panel:#162139;--accent:#ffa14e;}}}}
:root[data-theme="dark"]{{--page:#0e1628;--ink:#f7f4ee;--ink-soft:#aeb7cc;--rule:#26365e;--panel:#162139;--accent:#ffa14e;}}
html,body{{margin:0;background:var(--page);color:var(--ink);font-family:'Heebo','Segoe UI',Arial,sans-serif;}}
.wrap{{max-width:1180px;margin:0 auto;padding:32px 20px 64px;direction:rtl;}}
header{{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;margin-bottom:20px;}}
header h1{{font-size:26px;font-weight:900;margin:0;text-wrap:balance;}}
header .meta{{font-size:14px;color:var(--ink-soft);}}
.grid{{display:grid;grid-template-columns:minmax(300px,420px) 1fr;gap:28px;align-items:start;}}
@media (max-width:820px){{.grid{{grid-template-columns:1fr;}}}}
.player{{position:relative;width:100%;aspect-ratio:9/16;background:var(--navy-deep);border-radius:22px;overflow:hidden;box-shadow:0 24px 60px rgba(18,29,54,.35);}}
.player .fit{{position:absolute;left:0;top:0;width:1080px;height:1920px;transform-origin:0 0;}}
.ctl{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(18,29,54,.35);cursor:pointer;border:0;padding:0;}}
.ctl.playing{{background:transparent;}} .ctl.playing .btn{{opacity:0;}}
.ctl .btn{{width:118px;height:118px;border-radius:50%;background:var(--orange);display:flex;align-items:center;justify-content:center;box-shadow:0 20px 50px rgba(240,125,26,.5);transition:transform .15s;}}
.ctl:hover .btn{{transform:scale(1.05);}} .ctl:focus-visible{{outline:3px solid var(--orange-soft);outline-offset:-6px;}}
.ctl svg{{width:48px;height:48px;fill:#fff;margin-inline-start:6px;}}
.bar{{display:flex;align-items:center;gap:12px;margin-top:12px;font-size:13px;color:var(--ink-soft);font-variant-numeric:tabular-nums;}}
.bar input{{flex:1;accent-color:var(--orange);}}
.facts{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;}}
@media (max-width:520px){{.facts{{grid-template-columns:1fr;}}}}
.fact{{background:var(--panel);border:1px solid var(--rule);border-radius:14px;padding:14px 16px;}}
.fv{{font-weight:900;font-size:19px;color:var(--accent);font-variant-numeric:tabular-nums;}}
.fl{{font-size:14px;color:var(--ink-soft);margin-top:4px;line-height:1.45;}}
h2{{font-size:15px;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-soft);font-weight:800;margin:26px 0 10px;}}
ol{{margin:0;padding-inline-start:22px;line-height:1.6;font-size:15px;max-width:62ch;}} ol li{{margin-bottom:6px;}}
.src{{font-size:13px;color:var(--ink-soft);margin-top:18px;line-height:1.5;}} .src a{{color:var(--accent);}}
{style}
</style>
<div class="wrap">
<header>
  <h1>הגיוסים לפוליסות החיסכון בשמיים</h1>
  <div class="meta">סרטון הסבר · {total} שניות · 9:16 · קריינות בעברית</div>
</header>
<div class="grid">
  <div>
    <div class="player" id="player"><div class="fit" id="fit">{stage}</div>
      <button class="ctl" id="ctl" aria-label="נגן"><div class="btn"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></div></button>
    </div>
    <div class="bar"><span id="tcur">0:00</span><input type="range" id="seek" min="0" max="{total}" step="0.05" value="0" aria-label="מיקום"><span>{int(total//60)}:{int(total%60):02d}</span></div>
    <audio id="aud" preload="auto" src="{audio_uri}"></audio>
  </div>
  <div>
    <div class="facts">{facts_html}</div>
    <h2>תסריט הקריינות</h2>
    <ol>{script_html}</ol>
    <div class="src">מקור הנתונים: כתבה ב-FUNDER, 30.8.2026 — <a href="https://www.funder.co.il/article/208647" target="_blank" rel="noopener">funder.co.il/article/208647</a>. הנתונים מתייחסים לחברות הביטוח המופיעות בטבלת הכתבה.</div>
  </div>
</div>
</div>
<script>
{script}
(function(){{
  const fit=document.getElementById('fit'), player=document.getElementById('player');
  function resize(){{ const s=player.clientWidth/1080; fit.style.transform='scale('+s+')'; }}
  window.addEventListener('resize',resize); resize();
  const aud=document.getElementById('aud'), ctl=document.getElementById('ctl'), seek=document.getElementById('seek'), tcur=document.getElementById('tcur');
  const T=window.TIMELINE.total; let raf=null;
  const fmt=t=>Math.floor(t/60)+':'+String(Math.floor(t%60)).padStart(2,'0');
  function frame(){{ const t=Math.min(aud.currentTime,T-0.05); render(t); seek.value=t; tcur.textContent=fmt(t); if(!aud.paused) raf=requestAnimationFrame(frame); }}
  ctl.addEventListener('click',()=>{{ if(aud.paused){{ if(aud.currentTime>=T-0.1) aud.currentTime=0; aud.play(); }} else aud.pause(); }});
  aud.addEventListener('play',()=>{{ ctl.classList.add('playing'); ctl.setAttribute('aria-label','השהה'); frame(); }});
  aud.addEventListener('pause',()=>{{ ctl.classList.remove('playing'); ctl.setAttribute('aria-label','נגן'); cancelAnimationFrame(raf); }});
  aud.addEventListener('ended',()=>{{ ctl.classList.remove('playing'); }});
  seek.addEventListener('input',()=>{{ aud.currentTime=parseFloat(seek.value); render(aud.currentTime); tcur.textContent=fmt(aud.currentTime); }});
  render(3.0);
}})();
</script>
"""
out = V / "preview.html"
out.write_text(page)
print("wrote", out, out.stat().st_size, "bytes; audio", opus.stat().st_size)
