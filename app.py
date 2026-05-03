"""
Techofy API Hub — Toxic • @wiinc
e-dev.fun  |  Professional White Theme
"""

import os, re, time, json, requests
from collections import OrderedDict
from functools import wraps
from flask import Flask, request, Response, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

COPYRIGHT   = "Toxic • @wiinc"
API_KEY     = os.getenv("API_KEY", "toxic")

# ──────────────────────────────────────────────────────────
# Shared CSS — White theme + 3D animations
# ──────────────────────────────────────────────────────────
_BASE_CSS = """
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');
  :root{
    --bg:#f8faff; --surface:#ffffff; --surface2:#f1f5fe;
    --border:#e2e8f8; --text:#0f172a; --text2:#475569; --text3:#94a3b8;
    --accent:#4f46e5; --accent2:#7c3aed; --accent3:#06b6d4;
    --green:#10b981; --amber:#f59e0b; --red:#ef4444;
    --shadow:0 4px 24px rgba(79,70,229,.08);
    --shadow-lg:0 20px 60px rgba(79,70,229,.13);
    --radius:16px; --radius-sm:10px;
  }
  *{margin:0;padding:0;box-sizing:border-box;}
  html{scroll-behavior:smooth;}
  body{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;overflow-x:hidden;}
  ::selection{background:rgba(79,70,229,.15);color:var(--accent);}

  .bg-mesh{
    position:fixed;inset:0;z-index:0;pointer-events:none;
    background:
      radial-gradient(ellipse 80% 60% at 10% -10%,rgba(79,70,229,.07) 0%,transparent 60%),
      radial-gradient(ellipse 60% 50% at 90% 100%,rgba(6,182,212,.06) 0%,transparent 60%),
      radial-gradient(ellipse 50% 40% at 50% 50%,rgba(124,58,237,.04) 0%,transparent 70%);
  }
  .orb{position:fixed;border-radius:50%;filter:blur(80px);pointer-events:none;z-index:0;animation:orbFloat 8s ease-in-out infinite;}
  .orb1{width:400px;height:400px;background:rgba(79,70,229,.06);top:-100px;left:-100px;}
  .orb2{width:300px;height:300px;background:rgba(6,182,212,.05);bottom:-80px;right:-80px;animation-delay:-3s;}
  .orb3{width:200px;height:200px;background:rgba(124,58,237,.05);top:50%;left:60%;animation-delay:-5s;}
  @keyframes orbFloat{0%,100%{transform:translateY(0) scale(1);}50%{transform:translateY(-30px) scale(1.05);}}

  .page{position:relative;z-index:1;min-height:100vh;display:flex;flex-direction:column;}
  .wrap{max-width:860px;width:100%;margin:0 auto;padding:0 1.5rem;}

  /* Navbar */
  .nav{
    position:sticky;top:0;z-index:100;
    backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
    background:rgba(248,250,255,.88);border-bottom:1px solid var(--border);padding:.9rem 0;
  }
  .nav-inner{max-width:860px;margin:0 auto;padding:0 1.5rem;display:flex;align-items:center;justify-content:space-between;}
  .nav-logo{
    font-size:1.1rem;font-weight:800;text-decoration:none;letter-spacing:-.02em;
    background:linear-gradient(135deg,var(--accent),var(--accent2));
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  }
  .nav-links{display:flex;gap:.2rem;align-items:center;}
  .nav-link{font-size:.82rem;font-weight:500;color:var(--text2);text-decoration:none;padding:.4rem .8rem;border-radius:8px;transition:all .2s;}
  .nav-link:hover{background:var(--surface2);color:var(--accent);}
  .nav-link.active{background:rgba(79,70,229,.08);color:var(--accent);font-weight:600;}

  /* Hero */
  .hero{padding:5rem 0 3.5rem;text-align:center;}
  .hero-badge{
    display:inline-flex;align-items:center;gap:.4rem;
    background:rgba(79,70,229,.07);border:1px solid rgba(79,70,229,.15);
    color:var(--accent);font-size:.72rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;
    padding:.35rem 1rem;border-radius:999px;margin-bottom:1.8rem;
    animation:fadeUp .6s ease both;
  }
  .hero-badge .dot{width:6px;height:6px;background:var(--green);border-radius:50%;animation:pulse 2s infinite;}
  @keyframes pulse{0%,100%{opacity:1;transform:scale(1);}50%{opacity:.5;transform:scale(.8);}}
  .hero h1{
    font-size:clamp(2.4rem,6vw,4rem);font-weight:900;letter-spacing:-.04em;line-height:1.05;margin-bottom:1.2rem;
    background:linear-gradient(135deg,#0f172a 0%,var(--accent) 50%,var(--accent2) 100%);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
    animation:fadeUp .6s .1s ease both;
  }
  .hero p{font-size:1.05rem;color:var(--text2);line-height:1.7;max-width:500px;margin:0 auto 2.5rem;animation:fadeUp .6s .2s ease both;}
  @keyframes fadeUp{from{opacity:0;transform:translateY(20px);}to{opacity:1;transform:translateY(0);}}

  /* Cards */
  .cards-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1.2rem;margin-bottom:2rem;animation:fadeUp .6s .3s ease both;}
  .api-card{
    background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
    padding:1.8rem 1.6rem;text-decoration:none;color:inherit;display:block;
    transition:all .3s cubic-bezier(.34,1.56,.64,1);box-shadow:var(--shadow);
    transform-style:preserve-3d;position:relative;overflow:hidden;
  }
  .api-card::before{content:'';position:absolute;inset:0;background:linear-gradient(135deg,rgba(79,70,229,.04),rgba(124,58,237,.04));opacity:0;transition:opacity .3s;}
  .api-card:hover{transform:translateY(-6px) rotateX(2deg) rotateY(-1deg);box-shadow:var(--shadow-lg);border-color:rgba(79,70,229,.25);}
  .api-card:hover::before{opacity:1;}
  .card-icon{width:48px;height:48px;border-radius:12px;display:flex;align-items:center;justify-content:center;margin-bottom:1rem;}
  .card-icon svg{width:24px;height:24px;stroke-width:1.8;}
  .card-icon.indigo{background:rgba(79,70,229,.1);color:var(--accent);}
  .card-icon.amber-icon{background:rgba(245,158,11,.1);color:var(--amber);}
  .api-card h3{font-size:1rem;font-weight:700;margin-bottom:.4rem;letter-spacing:-.01em;}
  .api-card p{font-size:.82rem;color:var(--text2);line-height:1.55;margin-bottom:1rem;}
  .card-route{display:inline-flex;align-items:center;gap:.3rem;font-family:'JetBrains Mono',monospace;font-size:.72rem;background:var(--surface2);border:1px solid var(--border);color:var(--accent);padding:.25rem .6rem;border-radius:6px;}
  .card-route.amber-route{color:var(--amber);background:rgba(245,158,11,.06);border-color:rgba(245,158,11,.15);}

  /* Stats */
  .stats{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:4rem;animation:fadeUp .6s .4s ease both;}
  .stat{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-sm);padding:1.2rem;text-align:center;box-shadow:var(--shadow);}
  .stat .val{font-size:1.6rem;font-weight:800;letter-spacing:-.03em;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
  .stat .lbl{font-size:.75rem;color:var(--text3);margin-top:.2rem;font-weight:500;}

  /* Page sections */
  .main-content{flex:1;padding:2.5rem 0;}
  .page-hero{
    background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
    padding:2.5rem;margin-bottom:1.5rem;box-shadow:var(--shadow);
    animation:fadeUp .5s ease both;display:flex;align-items:center;gap:1.5rem;
  }
  .page-icon{width:72px;height:72px;border-radius:var(--radius-sm);display:flex;align-items:center;justify-content:center;flex-shrink:0;}
  .page-icon svg{width:32px;height:32px;stroke-width:1.6;}
  .page-icon.indigo{background:rgba(79,70,229,.1);color:var(--accent);}
  .page-icon.amber-pg{background:rgba(245,158,11,.1);color:var(--amber);}
  .page-hero h1{font-size:1.7rem;font-weight:800;letter-spacing:-.03em;margin-bottom:.4rem;}
  .page-hero p{font-size:.9rem;color:var(--text2);line-height:1.6;}
  .auth-pill{
    display:inline-flex;align-items:center;gap:.35rem;margin-top:.6rem;
    font-size:.75rem;font-weight:600;color:var(--accent);
    background:rgba(79,70,229,.07);border:1px solid rgba(79,70,229,.15);padding:.3rem .75rem;border-radius:999px;
  }
  .auth-pill svg{width:12px;height:12px;stroke:currentColor;fill:none;stroke-width:2.5;}

  .section-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.8rem;margin-bottom:1.2rem;box-shadow:var(--shadow);animation:fadeUp .5s ease both;}
  .section-label{font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:var(--text3);margin-bottom:1.2rem;display:flex;align-items:center;gap:.5rem;}
  .section-label::after{content:'';flex:1;height:1px;background:var(--border);}

  /* Endpoints */
  .ep{border:1px solid var(--border);border-radius:var(--radius-sm);padding:1.2rem 1.4rem;margin-bottom:.8rem;transition:border-color .2s,box-shadow .2s;background:var(--surface2);}
  .ep:hover{border-color:rgba(79,70,229,.2);box-shadow:0 4px 16px rgba(79,70,229,.06);}
  .ep:last-child{margin-bottom:0;}
  .ep-top{display:flex;align-items:center;gap:.6rem;flex-wrap:wrap;margin-bottom:.5rem;}
  .method{font-family:'JetBrains Mono',monospace;font-size:.68rem;font-weight:700;padding:.22rem .55rem;border-radius:6px;letter-spacing:.04em;flex-shrink:0;}
  .method-get{background:rgba(16,185,129,.1);color:var(--green);border:1px solid rgba(16,185,129,.2);}
  .method-post{background:rgba(79,70,229,.1);color:var(--accent);border:1px solid rgba(79,70,229,.2);}
  .ep-path{font-family:'JetBrains Mono',monospace;font-size:.82rem;color:var(--text);font-weight:500;}
  .ep-desc{font-size:.82rem;color:var(--text2);line-height:1.55;}
  .params{margin-top:.8rem;display:flex;flex-direction:column;gap:.3rem;}
  .param{display:flex;align-items:flex-start;gap:.6rem;font-size:.8rem;color:var(--text2);}
  .param code{font-family:'JetBrains Mono',monospace;font-size:.73rem;background:rgba(79,70,229,.07);border:1px solid rgba(79,70,229,.12);color:var(--accent);padding:.18rem .45rem;border-radius:5px;white-space:nowrap;flex-shrink:0;}

  /* Auth methods */
  .auth-methods{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:.8rem;}
  .auth-method{background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius-sm);padding:1rem;}
  .auth-method .auth-label{font-size:.7rem;color:var(--text3);font-weight:600;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.4rem;}
  .auth-method code{font-family:'JetBrains Mono',monospace;font-size:.78rem;color:var(--accent);word-break:break-all;}

  /* Code block */
  .code-block{background:#0f172a;border-radius:var(--radius-sm);padding:1.4rem;overflow-x:auto;border:1px solid rgba(255,255,255,.06);}
  .code-block pre{font-family:'JetBrains Mono',monospace;font-size:.82rem;line-height:1.75;color:#94a3b8;}
  .ck{color:#7dd3fc;} .cs{color:#a7f3d0;} .cn{color:#fda4af;}

  /* Fields grid */
  .fields-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(175px,1fr));gap:.5rem;}
  .field-tag{font-size:.75rem;background:var(--surface2);border:1px solid var(--border);border-radius:6px;padding:.35rem .65rem;font-family:'JetBrains Mono',monospace;color:var(--text2);}

  /* Footer */
  footer{border-top:1px solid var(--border);background:var(--surface);padding:3rem 0 2rem;margin-top:auto;}
  .footer-inner{max-width:860px;margin:0 auto;padding:0 1.5rem;display:grid;grid-template-columns:1fr auto;gap:2rem;align-items:start;}
  .footer-brand .logo{font-size:1.1rem;font-weight:800;letter-spacing:-.02em;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
  .footer-brand p{font-size:.8rem;color:var(--text3);margin-top:.4rem;line-height:1.6;}
  .footer-links{display:flex;flex-direction:column;gap:.4rem;text-align:right;}
  .footer-links a{font-size:.8rem;color:var(--text3);text-decoration:none;transition:color .2s;}
  .footer-links a:hover{color:var(--accent);}
  .footer-bottom{max-width:860px;margin:.6rem auto 0;padding:.8rem 1.5rem 0;border-top:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:.5rem;}
  .footer-bottom span{font-size:.75rem;color:var(--text3);}
  .footer-status{display:inline-flex;align-items:center;gap:.4rem;font-size:.72rem;font-weight:600;color:var(--green);}
  .footer-status .dot{width:6px;height:6px;background:var(--green);border-radius:50%;animation:pulse 2s infinite;}

  /* Scroll reveal */
  .reveal{opacity:0;transform:translateY(24px);transition:opacity .6s ease,transform .6s ease;}
  .reveal.visible{opacity:1;transform:none;}

  @media(max-width:600px){
    .hero h1{font-size:2.2rem;}
    .stats{grid-template-columns:1fr;}
    .footer-inner{grid-template-columns:1fr;}
    .footer-links{text-align:left;}
    .page-hero{flex-direction:column;text-align:center;}
    .footer-bottom{flex-direction:column;text-align:center;}
  }
"""

_BASE_JS = """<script>
const io=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('visible');io.unobserve(e.target);}});},{threshold:.1});
document.querySelectorAll('.reveal').forEach(el=>io.observe(el));
document.querySelectorAll('.api-card').forEach(card=>{
  card.addEventListener('mousemove',e=>{
    const r=card.getBoundingClientRect();
    const x=e.clientX-r.left-r.width/2,y=e.clientY-r.top-r.height/2;
    card.style.transform=`translateY(-6px) rotateX(${-y/20}deg) rotateY(${x/20}deg)`;
  });
  card.addEventListener('mouseleave',()=>{card.style.transform='';});
});
</script>"""

def _nav(active="home"):
    links = [("/","Hub","home"),("/pakinfo/","Pakistan Info","pak"),("/vinfo/","Vehicle Info","vinfo")]
    html = '<div class="nav-links">'
    for href, label, key in links:
        cls = "nav-link active" if key == active else "nav-link"
        html += f'<a class="{cls}" href="{href}">{label}</a>'
    html += '</div>'
    return html

_FOOTER_HTML = """<footer>
  <div class="footer-inner">
    <div class="footer-brand">
      <div class="logo">Techofy API</div>
      <p>A private, secure API hub built and<br>maintained by Toxic &bull; @wiinc.</p>
    </div>
    <div class="footer-links">
      <a href="/">Hub</a>
      <a href="/pakinfo/">Pakistan Info API</a>
      <a href="/vinfo/">Vehicle Info API</a>
    </div>
  </div>
  <div class="footer-bottom">
    <span>&copy; 2026 Toxic &bull; @wiinc &mdash; All rights reserved</span>
    <span class="footer-status"><span class="dot"></span>All Systems Operational</span>
  </div>
</footer>"""

# ──────────────────────────────────────────────────────────
# Security
# ──────────────────────────────────────────────────────────
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = (request.headers.get("X-API-Key")
               or request.args.get("key")
               or (request.get_json(silent=True) or {}).get("key"))
        if key != API_KEY:
            return Response(json.dumps({
                "error": "Unauthorized",
                "message": "A valid API key is required. Contact Toxic \u2022 @wiinc.",
                "hint": "Pass ?key=YOUR_KEY or header X-API-Key: YOUR_KEY"
            }, ensure_ascii=False, indent=2), status=403, mimetype="application/json; charset=utf-8")
        return f(*args, **kwargs)
    return decorated

def _json(obj, status=200):
    return Response(json.dumps(obj, ensure_ascii=False, indent=2),
                    status=status, mimetype="application/json; charset=utf-8")

# ══════════════════════════════════════════════════════════
# ROOT /
# ══════════════════════════════════════════════════════════
@app.route("/", methods=["GET"])
def root_home():
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Techofy API &mdash; e-dev.fun</title>
<style>{_BASE_CSS}</style>
</head>
<body>
<div class="bg-mesh"></div><div class="orb orb1"></div><div class="orb orb2"></div><div class="orb orb3"></div>
<div class="page">
<nav class="nav"><div class="nav-inner"><a class="nav-logo" href="/">Techofy API</a>{_nav("home")}</div></nav>
<main class="main-content"><div class="wrap">

  <div class="hero">
    <div class="hero-badge"><span class="dot"></span>Private API Hub &mdash; Active</div>
    <h1>Enterprise-grade<br>API Infrastructure</h1>
    <p>Secure, private APIs built and maintained by<br><strong>Toxic &bull; @wiinc</strong>. Authentication required on all endpoints.</p>
  </div>

  <div class="cards-grid">
    <a class="api-card" href="/pakinfo/">
      <div class="card-icon indigo">
        <svg viewBox="0 0 24 24" stroke="currentColor" fill="none"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></svg>
      </div>
      <h3>Pakistan Info API</h3>
      <p>Lookup mobile numbers and CNIC details from Pakistan's carrier database.</p>
      <span class="card-route">/pakinfo/</span>
    </a>
    <a class="api-card" href="/vinfo/">
      <div class="card-icon amber-icon">
        <svg viewBox="0 0 24 24" stroke="currentColor" fill="none"><rect x="2" y="7" width="20" height="10" rx="3"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/><path d="M2 11h20M7 7l2-4h6l2 4"/></svg>
      </div>
      <h3>Vehicle Info API</h3>
      <p>Fetch complete RC and vehicle registration details by plate number.</p>
      <span class="card-route amber-route">/vinfo/</span>
    </a>
  </div>

  <div class="stats reveal">
    <div class="stat"><div class="val">2</div><div class="lbl">Active APIs</div></div>
    <div class="stat"><div class="val">99.9%</div><div class="lbl">Uptime SLA</div></div>
    <div class="stat"><div class="val">REST</div><div class="lbl">Architecture</div></div>
  </div>

  <div class="section-card reveal">
    <div class="section-label">Authentication</div>
    <div class="auth-methods">
      <div class="auth-method"><div class="auth-label">Query Parameter</div><code>?key=YOUR_KEY</code></div>
      <div class="auth-method"><div class="auth-label">Request Header</div><code>X-API-Key: YOUR_KEY</code></div>
      <div class="auth-method"><div class="auth-label">JSON Body (POST)</div><code>{{"key":"YOUR_KEY"}}</code></div>
    </div>
  </div>

</div></main>
{_FOOTER_HTML}
</div>
{_BASE_JS}
</body></html>"""
    return Response(html, mimetype="text/html; charset=utf-8")


# ══════════════════════════════════════════════════════════
# PAKINFO  /pakinfo/
# ══════════════════════════════════════════════════════════
TARGET_BASE  = os.getenv("TARGET_BASE", "https://pakistandatabase.com")
TARGET_PATH  = os.getenv("TARGET_PATH", "/databases/sim.php")
MIN_INTERVAL = float(os.getenv("MIN_INTERVAL", "1.0"))
_LAST_CALL   = {"ts": 0.0}

def _is_mobile(v): return bool(re.fullmatch(r"92\d{9,12}", (v or "").strip()))
def _is_cnic(v):   return bool(re.fullmatch(r"\d{13}", (v or "").strip()))
def _classify(v):
    v = v.strip()
    if _is_mobile(v): return "mobile", v
    if _is_cnic(v):   return "cnic", v
    raise ValueError("Use mobile with country code (92\u2026) or CNIC (13 digits).")
def _rate_limit():
    now = time.time(); elapsed = now - _LAST_CALL["ts"]
    if elapsed < MIN_INTERVAL: time.sleep(MIN_INTERVAL - elapsed)
    _LAST_CALL["ts"] = time.time()
def _fetch_pak(query):
    _rate_limit()
    s = requests.Session()
    h = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/140.0.0.0 Safari/537.36",
         "Referer": TARGET_BASE.rstrip("/") + "/", "Accept-Language":"en-US,en;q=0.9"}
    r = s.post(TARGET_BASE.rstrip("/")+TARGET_PATH, headers=h, data={"search_query": query}, timeout=20)
    r.raise_for_status(); return r.text
def _parse_pak(html):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"class":"api-response"}) or soup.find("table")
    if not table: return []
    tbody = table.find("tbody")
    if not tbody: return []
    out = []
    for tr in tbody.find_all("tr"):
        cols = [td.get_text(strip=True) for td in tr.find_all("td")]
        out.append({"mobile":cols[0] if len(cols)>0 else None,"name":cols[1] if len(cols)>1 else None,
                    "cnic":cols[2] if len(cols)>2 else None,"address":cols[3] if len(cols)>3 else None})
    return out

@app.route("/pakinfo/", methods=["GET"])
def pakinfo_home():
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Pakistan Info API &mdash; Techofy</title>
<style>{_BASE_CSS}</style>
</head>
<body>
<div class="bg-mesh"></div><div class="orb orb1"></div><div class="orb orb2"></div>
<div class="page">
<nav class="nav"><div class="nav-inner"><a class="nav-logo" href="/">Techofy API</a>{_nav("pak")}</div></nav>
<main class="main-content"><div class="wrap">

  <div class="page-hero">
    <div class="page-icon indigo">
      <svg viewBox="0 0 24 24" stroke="currentColor" fill="none"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></svg>
    </div>
    <div>
      <h1>Pakistan Info API</h1>
      <p>Lookup mobile numbers and CNIC records from Pakistan's carrier database. Supports GET and POST with multiple query formats.</p>
      <div class="auth-pill">
        <svg viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
        Authentication required on all endpoints
      </div>
    </div>
  </div>

  <div class="section-card reveal">
    <div class="section-label">Authentication</div>
    <div class="auth-methods">
      <div class="auth-method"><div class="auth-label">Query Param</div><code>?key=YOUR_KEY</code></div>
      <div class="auth-method"><div class="auth-label">Header</div><code>X-API-Key: YOUR_KEY</code></div>
      <div class="auth-method"><div class="auth-label">JSON Body</div><code>{{"key":"YOUR_KEY"}}</code></div>
    </div>
  </div>

  <div class="section-card reveal">
    <div class="section-label">Endpoints</div>
    <div class="ep">
      <div class="ep-top"><span class="method method-get">GET</span><span class="ep-path">/pakinfo/lookup?query=&lt;value&gt;&amp;key=&lt;key&gt;</span></div>
      <div class="ep-desc">Lookup by mobile number (92xxxxxxxxxx) or CNIC (13 digits).</div>
      <div class="params">
        <div class="param"><code>query</code> Mobile (92&hellip;) or CNIC &mdash; required</div>
        <div class="param"><code>key</code> Your API key &mdash; required</div>
        <div class="param"><code>pretty=1</code> Pretty-print JSON &mdash; optional</div>
      </div>
    </div>
    <div class="ep">
      <div class="ep-top"><span class="method method-get">GET</span><span class="ep-path">/pakinfo/lookup/&lt;value&gt;?key=&lt;key&gt;</span></div>
      <div class="ep-desc">Pass query value directly in the URL path.</div>
    </div>
    <div class="ep">
      <div class="ep-top"><span class="method method-post">POST</span><span class="ep-path">/pakinfo/lookup</span></div>
      <div class="ep-desc">Send query in JSON request body.</div>
      <div class="params"><div class="param"><code>{{"query":"923...","key":"..."}}</code> JSON body</div></div>
    </div>
    <div class="ep">
      <div class="ep-top"><span class="method method-get">GET</span><span class="ep-path">/pakinfo/health?key=&lt;key&gt;</span></div>
      <div class="ep-desc">Service health check endpoint.</div>
    </div>
  </div>

  <div class="section-card reveal">
    <div class="section-label">Example Response</div>
    <div class="code-block"><pre>{{
  <span class="ck">"query"</span>:          <span class="cs">"923323312487"</span>,
  <span class="ck">"query_type"</span>:     <span class="cs">"mobile"</span>,
  <span class="ck">"results_count"</span>:  <span class="cn">1</span>,
  <span class="ck">"results"</span>: [
    {{
      <span class="ck">"mobile"</span>:   <span class="cs">"923323312487"</span>,
      <span class="ck">"name"</span>:     <span class="cs">"Muhammad Ali"</span>,
      <span class="ck">"cnic"</span>:     <span class="cs">"3520112345671"</span>,
      <span class="ck">"address"</span>:  <span class="cs">"Lahore, Punjab"</span>
    }}
  ],
  <span class="ck">"copyright"</span>:      <span class="cs">"Toxic \u2022 @wiinc"</span>
}}</pre></div>
  </div>

</div></main>
{_FOOTER_HTML}
</div>
{_BASE_JS}
</body></html>"""
    return Response(html, mimetype="text/html; charset=utf-8")

@app.route("/pakinfo/lookup", methods=["GET"])
@require_api_key
def pakinfo_get():
    q = request.args.get("query") or request.args.get("q") or request.args.get("value")
    if not q: return _json({"error":"Use ?query=<mobile or cnic>&key=<your_key>"}, 400)
    try: qtype, norm = _classify(q)
    except ValueError as e: return _json({"error":"Invalid query","detail":str(e)}, 400)
    try: html = _fetch_pak(norm)
    except Exception as e: return _json({"error":"Fetch failed","detail":str(e)}, 500)
    r = _parse_pak(html)
    return _json({"query":norm,"query_type":qtype,"results_count":len(r),"results":r,"copyright":COPYRIGHT})

@app.route("/pakinfo/lookup/<path:q>", methods=["GET"])
@require_api_key
def pakinfo_path(q):
    try: qtype, norm = _classify(q)
    except ValueError as e: return _json({"error":"Invalid query","detail":str(e)}, 400)
    try: html = _fetch_pak(norm)
    except Exception as e: return _json({"error":"Fetch failed","detail":str(e)}, 500)
    r = _parse_pak(html)
    return _json({"query":norm,"query_type":qtype,"results_count":len(r),"results":r,"copyright":COPYRIGHT})

@app.route("/pakinfo/lookup", methods=["POST"])
@require_api_key
def pakinfo_post():
    body = request.get_json(force=True, silent=True) or {}
    q = body.get("query") or body.get("number") or body.get("value")
    if not q: return _json({"error":'Send JSON {"query":"..."}'}, 400)
    try: qtype, norm = _classify(q)
    except ValueError as e: return _json({"error":"Invalid query","detail":str(e)}, 400)
    try: html = _fetch_pak(norm)
    except Exception as e: return _json({"error":"Fetch failed","detail":str(e)}, 500)
    r = _parse_pak(html)
    return _json({"query":norm,"query_type":qtype,"results_count":len(r),"results":r,"copyright":COPYRIGHT})

@app.route("/pakinfo/health", methods=["GET"])
@require_api_key
def pakinfo_health():
    return _json({"status":"ok","service":"Pakistan Info API","provider":"Techofy","copyright":COPYRIGHT})


# ══════════════════════════════════════════════════════════
# VINFO  /vinfo/
# ══════════════════════════════════════════════════════════
VINFO_ORDER = [
    "Owner Name","Father's Name","Owner Serial No","Model Name","Maker Model",
    "Vehicle Class","Fuel Type","Fuel Norms","Registration Date",
    "Insurance Company","Insurance No","Insurance Expiry","Insurance Upto",
    "Fitness Upto","Tax Upto","PUC No","PUC Upto",
    "Financier Name","Registered RTO","Address","City Name","Phone",
]

def _fetch_vehicle(rc):
    rc = rc.strip().upper()
    url = f"https://vahanx.in/rc-search/{rc}"
    headers = {
        "Host":"vahanx.in","Connection":"keep-alive",
        "sec-ch-ua":'"Chromium";v="130","Google Chrome";v="130","Not?A_Brand";v="99"',
        "sec-ch-ua-mobile":"?1","sec-ch-ua-platform":'"Android"',"Upgrade-Insecure-Requests":"1",
        "User-Agent":"Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 Chrome/130.0.0.0 Mobile Safari/537.36",
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer":"https://vahanx.in/rc-search","Accept-Encoding":"gzip, deflate, br","Accept-Language":"en-US,en;q=0.9",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10); resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
    except requests.exceptions.RequestException as e: return {"error": f"Network error: {e}"}
    except Exception as e: return {"error": str(e)}
    def _val(label):
        try:
            div = soup.find("span", string=label).find_parent("div")
            return div.find("p").get_text(strip=True)
        except AttributeError: return None
    return {k: _val(k) for k in VINFO_ORDER}

@app.route("/vinfo/", methods=["GET"])
def vinfo_home():
    fields_html = "".join(f'<div class="field-tag">{k}</div>' for k in VINFO_ORDER)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Vehicle Info API &mdash; Techofy</title>
<style>{_BASE_CSS}
.page-icon.amber-pg{{background:rgba(245,158,11,.1);color:var(--amber);}}
.auth-pill{{background:rgba(245,158,11,.07);border-color:rgba(245,158,11,.18);color:var(--amber);}}
</style>
</head>
<body>
<div class="bg-mesh" style="background:radial-gradient(ellipse 80% 60% at 10% -10%,rgba(245,158,11,.05) 0%,transparent 60%),radial-gradient(ellipse 60% 50% at 90% 100%,rgba(245,158,11,.04) 0%,transparent 60%);"></div>
<div class="orb orb1" style="background:rgba(245,158,11,.05);"></div>
<div class="orb orb2" style="background:rgba(251,191,36,.04);"></div>
<div class="page">
<nav class="nav"><div class="nav-inner"><a class="nav-logo" href="/">Techofy API</a>{_nav("vinfo")}</div></nav>
<main class="main-content"><div class="wrap">

  <div class="page-hero">
    <div class="page-icon amber-pg">
      <svg viewBox="0 0 24 24" stroke="currentColor" fill="none"><rect x="2" y="7" width="20" height="10" rx="3"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/><path d="M2 11h20M7 7l2-4h6l2 4"/></svg>
    </div>
    <div>
      <h1>Vehicle Info API</h1>
      <p>Retrieve complete RC and vehicle registration details by plate number. Includes owner info, insurance, fitness, PUC, and more.</p>
      <div class="auth-pill">
        <svg viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
        Authentication required on all endpoints
      </div>
    </div>
  </div>

  <div class="section-card reveal">
    <div class="section-label">Authentication</div>
    <div class="auth-methods">
      <div class="auth-method"><div class="auth-label">Query Param</div><code>?key=YOUR_KEY</code></div>
      <div class="auth-method"><div class="auth-label">Header</div><code>X-API-Key: YOUR_KEY</code></div>
    </div>
  </div>

  <div class="section-card reveal">
    <div class="section-label">Endpoints</div>
    <div class="ep">
      <div class="ep-top"><span class="method method-get">GET</span><span class="ep-path">/vinfo/lookup?rc=&lt;plate&gt;&amp;key=&lt;key&gt;</span></div>
      <div class="ep-desc">Fetch full vehicle registration details by RC plate number.</div>
      <div class="params">
        <div class="param"><code>rc</code> Vehicle plate number &mdash; required</div>
        <div class="param"><code>key</code> Your API key &mdash; required</div>
      </div>
    </div>
    <div class="ep">
      <div class="ep-top"><span class="method method-get">GET</span><span class="ep-path">/vinfo/health?key=&lt;key&gt;</span></div>
      <div class="ep-desc">Service health check endpoint.</div>
    </div>
  </div>

  <div class="section-card reveal">
    <div class="section-label">Fields Returned</div>
    <div class="fields-grid">{fields_html}</div>
  </div>

  <div class="section-card reveal">
    <div class="section-label">Example Response</div>
    <div class="code-block"><pre>{{
  <span class="ck">"Owner Name"</span>:        <span class="cs">"Rahul Sharma"</span>,
  <span class="ck">"Father's Name"</span>:     <span class="cs">"Ramesh Sharma"</span>,
  <span class="ck">"Model Name"</span>:        <span class="cs">"SWIFT DZIRE"</span>,
  <span class="ck">"Vehicle Class"</span>:     <span class="cs">"LMV"</span>,
  <span class="ck">"Fuel Type"</span>:         <span class="cs">"PETROL"</span>,
  <span class="ck">"Registration Date"</span>: <span class="cs">"2019-03-15"</span>,
  <span class="ck">"Insurance Upto"</span>:    <span class="cs">"2026-03-14"</span>,
  <span class="ck">"Registered RTO"</span>:    <span class="cs">"Delhi - DL"</span>,
  <span class="ck">"copyright"</span>:         <span class="cs">"Toxic \u2022 @wiinc"</span>
}}</pre></div>
  </div>

</div></main>
{_FOOTER_HTML}
</div>
{_BASE_JS}
</body></html>"""
    return Response(html, mimetype="text/html; charset=utf-8")

@app.route("/vinfo/lookup", methods=["GET"])
@require_api_key
def vinfo_lookup():
    rc = request.args.get("rc") or request.args.get("plate") or request.args.get("number")
    if not rc: return _json({"error":"RC number required","hint":"Use ?rc=<plate>&key=<your_key>","copyright":COPYRIGHT}, 400)
    raw = _fetch_vehicle(rc)
    if "error" in raw: return _json({"error":raw["error"],"copyright":COPYRIGHT}, 500)
    ordered = OrderedDict()
    for k in VINFO_ORDER:
        if raw.get(k) is not None: ordered[k] = raw[k]
    ordered["copyright"] = COPYRIGHT
    return Response(json.dumps(ordered, ensure_ascii=False, indent=2), mimetype="application/json; charset=utf-8")

@app.route("/vinfo/health", methods=["GET"])
@require_api_key
def vinfo_health():
    return _json({"status":"ok","service":"Vehicle Info API","provider":"Techofy","copyright":COPYRIGHT})


# ══════════════════════════════════════════════════════════
# 404
# ══════════════════════════════════════════════════════════
@app.errorhandler(404)
def not_found(_):
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>404 &mdash; Not Found</title>
<style>
{_BASE_CSS}
.nf{{min-height:calc(100vh - 57px);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:2rem;}}
.nf-code{{font-size:clamp(5rem,18vw,10rem);font-weight:900;letter-spacing:-.06em;line-height:1;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;animation:fadeUp .5s ease both;}}
.nf-title{{font-size:1.5rem;font-weight:700;margin:.6rem 0 .5rem;animation:fadeUp .5s .08s ease both;}}
.nf-sub{{color:var(--text2);font-size:.9rem;line-height:1.6;max-width:360px;animation:fadeUp .5s .14s ease both;}}
.nf-btn{{display:inline-flex;align-items:center;gap:.4rem;margin-top:2rem;background:var(--accent);color:#fff;padding:.7rem 1.6rem;border-radius:var(--radius-sm);text-decoration:none;font-size:.88rem;font-weight:600;box-shadow:0 4px 20px rgba(79,70,229,.3);transition:all .2s;animation:fadeUp .5s .2s ease both;}}
.nf-btn:hover{{background:#4338ca;transform:translateY(-2px);box-shadow:0 8px 28px rgba(79,70,229,.4);}}
.nf-btn svg{{width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:2.5;}}
.nf-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:.8rem;margin-top:2.5rem;max-width:400px;animation:fadeUp .5s .25s ease both;}}
.nf-card{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-sm);padding:.9rem 1rem;text-decoration:none;color:var(--text2);font-size:.8rem;transition:all .2s;}}
.nf-card:hover{{border-color:rgba(79,70,229,.25);color:var(--accent);background:rgba(79,70,229,.03);}}
.nf-card strong{{color:var(--text);font-size:.82rem;display:block;margin-bottom:.2rem;}}
</style>
</head>
<body>
<div class="bg-mesh"></div><div class="orb orb1"></div><div class="orb orb2"></div>
<div class="page">
<nav class="nav"><div class="nav-inner"><a class="nav-logo" href="/">Techofy API</a>{_nav()}</div></nav>
<div class="nf">
  <div class="nf-code">404</div>
  <div class="nf-title">Page Not Found</div>
  <p class="nf-sub">This route does not exist on e-dev.fun. Navigate back to the hub or explore available APIs below.</p>
  <a class="nf-btn" href="/">
    <svg viewBox="0 0 24 24"><path d="M19 12H5M12 5l-7 7 7 7"/></svg>
    Back to Hub
  </a>
  <div class="nf-grid">
    <a class="nf-card" href="/pakinfo/"><strong>Pakistan Info API</strong>/pakinfo/</a>
    <a class="nf-card" href="/vinfo/"><strong>Vehicle Info API</strong>/vinfo/</a>
  </div>
</div>
</div>
</body></html>"""
    return Response(html, status=404, mimetype="text/html; charset=utf-8")


# ══════════════════════════════════════════════════════════
# Entry Point
# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    port  = int(os.getenv("PORT", "5000"))
    debug = os.getenv("DEBUG","false").lower() == "true"
    print(f"""
\u2554{'='*56}\u2557
\u2551  Techofy API Hub \u2014 Toxic \u2022 @wiinc{' '*22}\u2551
\u2551  /          Home Hub{' '*37}\u2551
\u2551  /pakinfo/  Pakistan Number & CNIC Info{' '*19}\u2551
\u2551  /vinfo/    Vehicle Registration Info{' '*21}\u2551
\u255a{'='*56}\u255d
  Running  \u2192  http://0.0.0.0:{port}
  API Key  \u2192  {API_KEY}
""")
    app.run(host="0.0.0.0", port=port, debug=debug)
