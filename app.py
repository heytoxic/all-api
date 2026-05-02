"""
API Server — Toxic • @wiinc
Domain:  e-dev.fun

"""

import os
import re
import time
import json
import requests
from collections import OrderedDict
from functools import wraps

from flask import Flask, request, Response, jsonify
from bs4 import BeautifulSoup

# ─────────────────────────────────────────
# App Setup
# ─────────────────────────────────────────
app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

COPYRIGHT  = "Toxic • @wiinc"
API_KEY    = os.getenv("API_KEY", "toxic")

# ─────────────────────────────────────────
# Security — API Key Guard
# ─────────────────────────────────────────
def require_api_key(f):
    """Reject any request that doesn't carry the correct API key."""
    @wraps(f)
    def decorated(*args, **kwargs):
        key = (
            request.headers.get("X-API-Key")
            or request.args.get("key")
            or (request.get_json(silent=True) or {}).get("key")
        )
        if key != API_KEY:
            return Response(
                json.dumps({
                    "error":   "Unauthorized",
                    "message": "Valid API key required. Contact Toxic • @wiinc.",
                    "hint":    "Pass ?key=<your_key>  or  X-API-Key header"
                }, ensure_ascii=False),
                status=403,
                mimetype="application/json; charset=utf-8"
            )
        return f(*args, **kwargs)
    return decorated


# ═══════════════════════════════════════════════════════════
# ROOT
# ═══════════════════════════════════════════════════════════
@app.route("/", methods=["GET"])
def root_home():
    return Response(_root_html(), mimetype="text/html; charset=utf-8")


def _root_html():
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Techofy API - Toxic</title>
  <style>
    *{margin:0;padding:0;box-sizing:border-box;}
    body{
      font-family:'Segoe UI',system-ui,sans-serif;
      background:#0d0d14;
      color:#e2e2f0;
      min-height:100vh;
      display:flex;
      flex-direction:column;
      align-items:center;
      justify-content:center;
      padding:2rem;
    }
    .glow{
      position:fixed;inset:0;
      background:radial-gradient(ellipse 60% 50% at 50% 0%,rgba(99,102,241,.18),transparent);
      pointer-events:none;
    }
    .card{
      background:rgba(255,255,255,.04);
      border:1px solid rgba(255,255,255,.08);
      border-radius:1.5rem;
      padding:3rem 2.5rem;
      max-width:680px;
      width:100%;
      text-align:center;
      box-shadow:0 8px 40px rgba(0,0,0,.6);
      position:relative;
    }
    .badge{
      display:inline-block;
      background:rgba(99,102,241,.15);
      border:1px solid rgba(99,102,241,.35);
      color:#a5b4fc;
      font-size:.75rem;
      font-weight:600;
      letter-spacing:.12em;
      padding:.3rem .9rem;
      border-radius:999px;
      text-transform:uppercase;
      margin-bottom:1.4rem;
    }
    h1{
      font-size:2.2rem;
      font-weight:700;
      background:linear-gradient(135deg,#a5b4fc,#818cf8 40%,#c4b5fd);
      -webkit-background-clip:text;
      -webkit-text-fill-color:transparent;
      background-clip:text;
      margin-bottom:.6rem;
    }
    .sub{color:#94a3b8;font-size:1rem;line-height:1.6;margin-bottom:2rem;}
    .apis{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:2rem;}
    @media(max-width:480px){.apis{grid-template-columns:1fr;}}
    .api-card{
      background:rgba(255,255,255,.05);
      border:1px solid rgba(255,255,255,.07);
      border-radius:1rem;
      padding:1.4rem;
      text-align:left;
      transition:border-color .2s,background .2s;
      text-decoration:none;color:inherit;display:block;
    }
    .api-card:hover{
      border-color:rgba(99,102,241,.5);
      background:rgba(99,102,241,.08);
    }
    .api-card .icon{font-size:1.8rem;margin-bottom:.6rem;}
    .api-card h3{font-size:1rem;font-weight:600;color:#e2e2f0;margin-bottom:.3rem;}
    .api-card p{font-size:.82rem;color:#94a3b8;line-height:1.5;}
    .api-card .tag{
      display:inline-block;
      margin-top:.6rem;
      font-size:.7rem;
      color:#818cf8;
      background:rgba(99,102,241,.12);
      border:1px solid rgba(99,102,241,.25);
      border-radius:999px;
      padding:.18rem .6rem;
      font-family:monospace;
    }
    .footer{color:#475569;font-size:.8rem;margin-top:1rem;}
    .footer a{color:#6366f1;text-decoration:none;}
  </style>
</head>
<body>
<div class="glow"></div>
<div class="card">
  <div class="badge">Private API Hub</div>
  <h1>Techofy API</h1>
  <p class="sub">
    Secure, private APIs built &amp; maintained by
    <strong style="color:#a5b4fc">Toxic • @wiinc</strong>.<br>
    Access is restricted — a valid API key is required for all endpoints.
  </p>

  <div class="apis">
    <a class="api-card" href="/pakinfo/">
      <div class="icon">🇵🇰</div>
      <h3>Pakistan Info API</h3>
      <p>Lookup mobile numbers &amp; CNIC details from Pakistan's database.</p>
      <span class="tag">/pakinfo/</span>
    </a>
    <a class="api-card" href="/vinfo/">
      <div class="icon">🚗</div>
      <h3>Vehicle Info API</h3>
      <p>Fetch complete RC / vehicle registration details by plate number.</p>
      <span class="tag">/vinfo/</span>
    </a>
  </div>

  <p class="footer">
    &copy; 2026 Toxic • @wiinc &nbsp;|&nbsp; All rights reserved
  </p>
</div>
</body>
</html>"""


# ═══════════════════════════════════════════════════════════
# PAKINFO  /pakinfo/
# ═══════════════════════════════════════════════════════════

TARGET_BASE     = os.getenv("TARGET_BASE", "https://pakistandatabase.com")
TARGET_PATH     = os.getenv("TARGET_PATH", "/databases/sim.php")
MIN_INTERVAL    = float(os.getenv("MIN_INTERVAL", "1.0"))
_LAST_CALL      = {"ts": 0.0}


# ── Helpers ──────────────────────────────

def _is_mobile(v: str) -> bool:
    return bool(re.fullmatch(r"92\d{9,12}", (v or "").strip()))

def _is_cnic(v: str) -> bool:
    return bool(re.fullmatch(r"\d{13}", (v or "").strip()))

def _classify(v: str):
    v = v.strip()
    if _is_mobile(v): return "mobile", v
    if _is_cnic(v):   return "cnic",   v
    raise ValueError("Use mobile with country code (92…) or CNIC (13 digits).")

def _rate_limit():
    now     = time.time()
    elapsed = now - _LAST_CALL["ts"]
    if elapsed < MIN_INTERVAL:
        time.sleep(MIN_INTERVAL - elapsed)
    _LAST_CALL["ts"] = time.time()

def _fetch_pak(query: str) -> str:
    _rate_limit()
    session = requests.Session()
    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/140.0.0.0 Safari/537.36"),
        "Referer": TARGET_BASE.rstrip("/") + "/",
        "Accept-Language": "en-US,en;q=0.9",
    }
    url  = TARGET_BASE.rstrip("/") + TARGET_PATH
    resp = session.post(url, headers=headers, data={"search_query": query}, timeout=20)
    resp.raise_for_status()
    return resp.text

def _parse_pak_table(html: str) -> list:
    soup  = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"class": "api-response"}) or soup.find("table")
    if not table:
        return []
    tbody = table.find("tbody")
    if not tbody:
        return []
    out = []
    for tr in tbody.find_all("tr"):
        cols = [td.get_text(strip=True) for td in tr.find_all("td")]
        out.append({
            "mobile":  cols[0] if len(cols) > 0 else None,
            "name":    cols[1] if len(cols) > 1 else None,
            "cnic":    cols[2] if len(cols) > 2 else None,
            "address": cols[3] if len(cols) > 3 else None,
        })
    return out

def _respond(obj, pretty=False, status=200):
    indent = 2 if pretty else None
    text   = json.dumps(obj, indent=indent, ensure_ascii=False)
    return Response(text, status=status, mimetype="application/json; charset=utf-8")

def _pak_result(query, qtype, results):
    return {
        "query":         query,
        "query_type":    qtype,
        "results_count": len(results),
        "results":       results,
        "copyright":     COPYRIGHT,
    }


# ── Routes ───────────────────────────────

@app.route("/pakinfo/", methods=["GET"])
def pakinfo_home():
    return Response(_pakinfo_html(), mimetype="text/html; charset=utf-8")


@app.route("/pakinfo/lookup", methods=["GET"])
@require_api_key
def pakinfo_get():
    q      = request.args.get("query") or request.args.get("q") or request.args.get("value")
    pretty = request.args.get("pretty") in ("1", "true")
    if not q:
        return _respond({"error": "Use ?query=<mobile or cnic>&key=<your_key>"}, pretty, 400)
    try:
        qtype, norm = _classify(q)
    except ValueError as e:
        return _respond({"error": "Invalid query", "detail": str(e)}, pretty, 400)
    try:
        html = _fetch_pak(norm)
    except Exception as e:
        return _respond({"error": "Fetch failed", "detail": str(e)}, pretty, 500)
    return _respond(_pak_result(norm, qtype, _parse_pak_table(html)), pretty)


@app.route("/pakinfo/lookup/<path:q>", methods=["GET"])
@require_api_key
def pakinfo_path(q):
    pretty = request.args.get("pretty") in ("1", "true")
    try:
        qtype, norm = _classify(q)
    except ValueError as e:
        return _respond({"error": "Invalid query", "detail": str(e)}, pretty, 400)
    try:
        html = _fetch_pak(norm)
    except Exception as e:
        return _respond({"error": "Fetch failed", "detail": str(e)}, pretty, 500)
    return _respond(_pak_result(norm, qtype, _parse_pak_table(html)), pretty)


@app.route("/pakinfo/lookup", methods=["POST"])
@require_api_key
def pakinfo_post():
    pretty = request.args.get("pretty") in ("1", "true")
    body   = request.get_json(force=True, silent=True) or {}
    q      = body.get("query") or body.get("number") or body.get("value")
    if not q:
        return _respond({"error": 'Send JSON {"query":"..."}'}, pretty, 400)
    try:
        qtype, norm = _classify(q)
    except ValueError as e:
        return _respond({"error": "Invalid query", "detail": str(e)}, pretty, 400)
    try:
        html = _fetch_pak(norm)
    except Exception as e:
        return _respond({"error": "Fetch failed", "detail": str(e)}, pretty, 500)
    return _respond(_pak_result(norm, qtype, _parse_pak_table(html)), pretty)


@app.route("/pakinfo/health", methods=["GET"])
@require_api_key
def pakinfo_health():
    return _respond({"status": "ok", "service": "Pakistan Info API By Techofy", "copyright": COPYRIGHT})


# ── HTML Page ────────────────────────────

def _pakinfo_html():
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Pakistan Info API — e-dev.fun</title>
  <style>
    *{margin:0;padding:0;box-sizing:border-box;}
    body{
      font-family:'Segoe UI',system-ui,sans-serif;
      background:#0d0d14;color:#e2e2f0;
      min-height:100vh;display:flex;flex-direction:column;align-items:center;
      padding:2.5rem 1rem;
    }
    .glow{
      position:fixed;inset:0;
      background:radial-gradient(ellipse 60% 40% at 30% 0%,rgba(20,184,166,.15),transparent);
      pointer-events:none;
    }
    .wrap{max-width:720px;width:100%;position:relative;}
    .back{
      display:inline-flex;align-items:center;gap:.4rem;
      color:#64748b;font-size:.82rem;text-decoration:none;margin-bottom:1.5rem;
      transition:color .2s;
    }
    .back:hover{color:#94a3b8;}
    .hero{
      background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);
      border-radius:1.5rem;padding:2.5rem 2rem;margin-bottom:1.5rem;
      text-align:center;
    }
    .icon-wrap{
      width:64px;height:64px;background:rgba(20,184,166,.12);
      border:1px solid rgba(20,184,166,.3);border-radius:1rem;
      display:flex;align-items:center;justify-content:center;
      font-size:2rem;margin:0 auto 1rem;
    }
    h1{font-size:1.8rem;font-weight:700;
       background:linear-gradient(135deg,#5eead4,#2dd4bf);
       -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
       margin-bottom:.5rem;}
    .sub{color:#94a3b8;font-size:.95rem;line-height:1.6;}
    .section{
      background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);
      border-radius:1rem;padding:1.5rem;margin-bottom:1rem;
    }
    .section h2{
      font-size:.85rem;font-weight:600;text-transform:uppercase;
      letter-spacing:.1em;color:#5eead4;margin-bottom:1rem;
    }
    .ep{
      background:#0a0a10;border:1px solid rgba(255,255,255,.06);
      border-radius:.75rem;padding:1rem 1.2rem;margin-bottom:.8rem;
    }
    .ep:last-child{margin-bottom:0;}
    .ep .method{
      display:inline-block;font-size:.7rem;font-weight:700;
      padding:.2rem .55rem;border-radius:.4rem;margin-right:.6rem;font-family:monospace;
    }
    .get {background:rgba(34,197,94,.15);color:#4ade80;border:1px solid rgba(34,197,94,.3);}
    .post{background:rgba(59,130,246,.15);color:#93c5fd;border:1px solid rgba(59,130,246,.3);}
    .ep .path{font-family:monospace;font-size:.9rem;color:#e2e2f0;}
    .ep .desc{font-size:.82rem;color:#94a3b8;margin-top:.4rem;}
    .params{margin-top:.8rem;}
    .param{
      display:flex;gap:.6rem;align-items:flex-start;
      font-size:.8rem;color:#cbd5e1;margin-bottom:.3rem;
    }
    .param code{
      background:#1e1e2e;border:1px solid rgba(255,255,255,.08);
      border-radius:.35rem;padding:.15rem .4rem;
      font-size:.78rem;color:#a5b4fc;white-space:nowrap;flex-shrink:0;
    }
    pre{
      background:#0a0a10;border:1px solid rgba(255,255,255,.06);
      border-radius:.75rem;padding:1rem;overflow-x:auto;
      font-size:.82rem;color:#94a3b8;line-height:1.7;
    }
    pre .key{color:#5eead4;}
    pre .str{color:#fde68a;}
    pre .num{color:#f9a8d4;}
    .footer{color:#475569;font-size:.78rem;text-align:center;margin-top:1.5rem;}
  </style>
</head>
<body>
<div class="glow"></div>
<div class="wrap">
  <a class="back" href="/">← Back to Hub</a>

  <div class="hero">
    <div class="icon-wrap">🇵🇰</div>
    <h1>Pakistan Info API</h1>
    <p class="sub">
      Lookup mobile numbers &amp; CNIC records from Pakistan's database.<br>
      <strong style="color:#5eead4">Authentication required</strong> on all endpoints.
    </p>
  </div>

  <!-- Auth -->
  <div class="section">
    <h2>🔐 Authentication</h2>
    <div class="ep">
      <p class="desc">Every request must carry your API key via one of these methods:</p>
      <div class="params" style="margin-top:.6rem;">
        <div class="param"><code>?key=YOUR_KEY</code> Query parameter (easiest)</div>
        <div class="param"><code>X-API-Key: YOUR_KEY</code> Request Header</div>
        <div class="param"><code>{"key":"YOUR_KEY"}</code> JSON body (POST only)</div>
      </div>
    </div>
  </div>

  <!-- Endpoints -->
  <div class="section">
    <h2>📡 Endpoints</h2>

    <div class="ep">
      <span class="method get">GET</span>
      <span class="path">/pakinfo/lookup?query=&lt;value&gt;&amp;key=&lt;key&gt;</span>
      <p class="desc">Lookup by mobile (92xxxxxxxxxx) or CNIC (13 digits).</p>
      <div class="params">
        <div class="param"><code>query</code> Mobile number or CNIC — required</div>
        <div class="param"><code>key</code> Your API key — required</div>
        <div class="param"><code>pretty=1</code> Pretty-print JSON — optional</div>
      </div>
    </div>

    <div class="ep">
      <span class="method get">GET</span>
      <span class="path">/pakinfo/lookup/&lt;value&gt;?key=&lt;key&gt;</span>
      <p class="desc">Same as above but value passed in the URL path.</p>
    </div>

    <div class="ep">
      <span class="method post">POST</span>
      <span class="path">/pakinfo/lookup</span>
      <p class="desc">Send query in JSON body.</p>
      <div class="params">
        <div class="param"><code>{"query":"92..."}</code> JSON body</div>
      </div>
    </div>

    <div class="ep">
      <span class="method get">GET</span>
      <span class="path">/pakinfo/health?key=&lt;key&gt;</span>
      <p class="desc">Health check for the service.</p>
    </div>
  </div>

  <!-- Example -->
  <div class="section">
    <h2>📦 Example Response</h2>
<pre>{
  <span class="key">"query"</span>:          <span class="str">"923323312487"</span>,
  <span class="key">"query_type"</span>:     <span class="str">"mobile"</span>,
  <span class="key">"results_count"</span>:  <span class="num">1</span>,
  <span class="key">"results"</span>: [
    {
      <span class="key">"mobile"</span>:   <span class="str">"923323312487"</span>,
      <span class="key">"name"</span>:     <span class="str">"Muhammad Ali"</span>,
      <span class="key">"cnic"</span>:     <span class="str">"3520112345671"</span>,
      <span class="key">"address"</span>:  <span class="str">"Lahore, Punjab"</span>
    }
  ],
  <span class="key">"copyright"</span>:      <span class="str">"Toxic • @wiinc"</span>
}</pre>
  </div>

  <p class="footer">Pakistan Info API &nbsp;|&nbsp; e-dev.fun &nbsp;|&nbsp; Toxic • @wiinc</p>
</div>
</body>
</html>"""


# ═══════════════════════════════════════════════════════════
# VINFO  /vinfo/
# ═══════════════════════════════════════════════════════════

VINFO_ORDER = [
    "Owner Name", "Father's Name", "Owner Serial No", "Model Name", "Maker Model",
    "Vehicle Class", "Fuel Type", "Fuel Norms", "Registration Date",
    "Insurance Company", "Insurance No", "Insurance Expiry", "Insurance Upto",
    "Fitness Upto", "Tax Upto", "PUC No", "PUC Upto",
    "Financier Name", "Registered RTO", "Address", "City Name", "Phone",
]

# ── Helpers ──────────────────────────────

def _fetch_vehicle(rc: str) -> dict:
    rc  = rc.strip().upper()
    url = f"https://vahanx.in/rc-search/{rc}"
    headers = {
        "Host": "vahanx.in",
        "Connection": "keep-alive",
        "sec-ch-ua": '"Chromium";v="130","Google Chrome";v="130","Not?A_Brand";v="99"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": ("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36"),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Referer": "https://vahanx.in/rc-search",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {e}"}
    except Exception as e:
        return {"error": str(e)}

    def _val(label):
        try:
            div = soup.find("span", string=label).find_parent("div")
            return div.find("p").get_text(strip=True)
        except AttributeError:
            return None

    return {k: _val(k) for k in VINFO_ORDER}


# ── Routes ───────────────────────────────

@app.route("/vinfo/", methods=["GET"])
def vinfo_home():
    return Response(_vinfo_html(), mimetype="text/html; charset=utf-8")


@app.route("/vinfo/lookup", methods=["GET"])
@require_api_key
def vinfo_lookup():
    rc = request.args.get("rc") or request.args.get("plate") or request.args.get("number")
    if not rc:
        return jsonify({
            "error":     "RC number required",
            "hint":      "Use ?rc=<plate_number>&key=<your_key>",
            "copyright": COPYRIGHT,
        }), 400

    raw     = _fetch_vehicle(rc)
    ordered = OrderedDict()

    if "error" in raw:
        return jsonify({"error": raw["error"], "copyright": COPYRIGHT}), 500

    for k in VINFO_ORDER:
        if raw.get(k) is not None:
            ordered[k] = raw[k]
    ordered["copyright"] = COPYRIGHT

    return Response(
        json.dumps(ordered, ensure_ascii=False, indent=2),
        mimetype="application/json; charset=utf-8",
    )


@app.route("/vinfo/health", methods=["GET"])
@require_api_key
def vinfo_health():
    return jsonify({"status": "ok", "service": "Vehicle Info API By Techofy", "copyright": COPYRIGHT})


# ── HTML Page ────────────────────────────

def _vinfo_html():
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Vehicle Info API — e-dev.fun</title>
  <style>
    *{margin:0;padding:0;box-sizing:border-box;}
    body{
      font-family:'Segoe UI',system-ui,sans-serif;
      background:#0d0d14;color:#e2e2f0;
      min-height:100vh;display:flex;flex-direction:column;align-items:center;
      padding:2.5rem 1rem;
    }
    .glow{
      position:fixed;inset:0;
      background:radial-gradient(ellipse 60% 40% at 70% 0%,rgba(251,191,36,.1),transparent);
      pointer-events:none;
    }
    .wrap{max-width:720px;width:100%;position:relative;}
    .back{
      display:inline-flex;align-items:center;gap:.4rem;
      color:#64748b;font-size:.82rem;text-decoration:none;margin-bottom:1.5rem;
      transition:color .2s;
    }
    .back:hover{color:#94a3b8;}
    .hero{
      background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);
      border-radius:1.5rem;padding:2.5rem 2rem;margin-bottom:1.5rem;text-align:center;
    }
    .icon-wrap{
      width:64px;height:64px;background:rgba(251,191,36,.1);
      border:1px solid rgba(251,191,36,.3);border-radius:1rem;
      display:flex;align-items:center;justify-content:center;
      font-size:2rem;margin:0 auto 1rem;
    }
    h1{font-size:1.8rem;font-weight:700;
       background:linear-gradient(135deg,#fcd34d,#fbbf24);
       -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
       margin-bottom:.5rem;}
    .sub{color:#94a3b8;font-size:.95rem;line-height:1.6;}
    .section{
      background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);
      border-radius:1rem;padding:1.5rem;margin-bottom:1rem;
    }
    .section h2{
      font-size:.85rem;font-weight:600;text-transform:uppercase;
      letter-spacing:.1em;color:#fbbf24;margin-bottom:1rem;
    }
    .ep{
      background:#0a0a10;border:1px solid rgba(255,255,255,.06);
      border-radius:.75rem;padding:1rem 1.2rem;margin-bottom:.8rem;
    }
    .ep:last-child{margin-bottom:0;}
    .method{
      display:inline-block;font-size:.7rem;font-weight:700;
      padding:.2rem .55rem;border-radius:.4rem;margin-right:.6rem;font-family:monospace;
    }
    .get{background:rgba(34,197,94,.15);color:#4ade80;border:1px solid rgba(34,197,94,.3);}
    .path{font-family:monospace;font-size:.9rem;color:#e2e2f0;}
    .desc{font-size:.82rem;color:#94a3b8;margin-top:.4rem;}
    .params{margin-top:.8rem;}
    .param{
      display:flex;gap:.6rem;align-items:flex-start;
      font-size:.8rem;color:#cbd5e1;margin-bottom:.3rem;
    }
    .param code{
      background:#1e1e2e;border:1px solid rgba(255,255,255,.08);
      border-radius:.35rem;padding:.15rem .4rem;
      font-size:.78rem;color:#fbbf24;white-space:nowrap;flex-shrink:0;
    }
    pre{
      background:#0a0a10;border:1px solid rgba(255,255,255,.06);
      border-radius:.75rem;padding:1rem;overflow-x:auto;
      font-size:.82rem;color:#94a3b8;line-height:1.7;
    }
    pre .key{color:#fbbf24;}
    pre .str{color:#fde68a;}
    .footer{color:#475569;font-size:.78rem;text-align:center;margin-top:1.5rem;}
  </style>
</head>
<body>
<div class="glow"></div>
<div class="wrap">
  <a class="back" href="/">← Back to Hub</a>

  <div class="hero">
    <div class="icon-wrap">🚗</div>
    <h1>Vehicle Info API</h1>
    <p class="sub">
      Fetch complete RC / vehicle registration details by plate number.<br>
      <strong style="color:#fbbf24">Authentication required</strong> on all endpoints.
    </p>
  </div>

  <!-- Auth -->
  <div class="section">
    <h2>🔐 Authentication</h2>
    <div class="ep">
      <p class="desc">Every request must carry your API key via one of these methods:</p>
      <div class="params" style="margin-top:.6rem;">
        <div class="param"><code>?key=YOUR_KEY</code> Query parameter (easiest)</div>
        <div class="param"><code>X-API-Key: YOUR_KEY</code> Request Header</div>
      </div>
    </div>
  </div>

  <!-- Endpoints -->
  <div class="section">
    <h2>📡 Endpoints</h2>

    <div class="ep">
      <span class="method get">GET</span>
      <span class="path">/vinfo/lookup?rc=&lt;plate&gt;&amp;key=&lt;key&gt;</span>
      <p class="desc">Fetch full vehicle registration details by RC plate number.</p>
      <div class="params">
        <div class="param"><code>rc</code> Vehicle registration / plate number — required</div>
        <div class="param"><code>key</code> Your API key — required</div>
      </div>
    </div>

    <div class="ep">
      <span class="method get">GET</span>
      <span class="path">/vinfo/health?key=&lt;key&gt;</span>
      <p class="desc">Health check for the service.</p>
    </div>
  </div>

  <!-- Example -->
  <div class="section">
    <h2>📦 Example Response</h2>
<pre>{
  <span class="key">"Owner Name"</span>:        <span class="str">"Rahul Sharma"</span>,
  <span class="key">"Father's Name"</span>:     <span class="str">"Ramesh Sharma"</span>,
  <span class="key">"Model Name"</span>:        <span class="str">"SWIFT DZIRE"</span>,
  <span class="key">"Vehicle Class"</span>:     <span class="str">"LMV"</span>,
  <span class="key">"Fuel Type"</span>:         <span class="str">"PETROL"</span>,
  <span class="key">"Registration Date"</span>: <span class="str">"2019-03-15"</span>,
  <span class="key">"Insurance Company"</span>: <span class="str">"XYZ Insurance"</span>,
  <span class="key">"Insurance Upto"</span>:    <span class="str">"2026-03-14"</span>,
  <span class="key">"Registered RTO"</span>:    <span class="str">"Delhi - DL"</span>,
  <span class="key">"copyright"</span>:         <span class="str">"Toxic • @wiinc"</span>
}</pre>
  </div>

  <p class="footer">Vehicle Info API &nbsp;|&nbsp; e-dev.fun &nbsp;|&nbsp; Toxic • @wiinc</p>
</div>
</body>
</html>"""


# ═══════════════════════════════════════════════════════════
# 404 Handler — no plain "Not Found" ever
# ═══════════════════════════════════════════════════════════
@app.errorhandler(404)
def not_found(_):
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Not Found— e-dev.fun</title>
  <style>
    *{margin:0;padding:0;box-sizing:border-box;}
    body{
      font-family:'Segoe UI',system-ui,sans-serif;
      background:#0d0d14;color:#e2e2f0;
      min-height:100vh;display:flex;align-items:center;
      justify-content:center;padding:2rem;text-align:center;
    }
    .card{max-width:440px;}
    .code{font-size:6rem;font-weight:800;
          background:linear-gradient(135deg,#6366f1,#8b5cf6);
          -webkit-background-clip:text;-webkit-text-fill-color:transparent;
          background-clip:text;line-height:1;}
    h2{font-size:1.4rem;color:#cbd5e1;margin:.8rem 0 .4rem;}
    p{color:#64748b;font-size:.9rem;line-height:1.6;}
    a{
      display:inline-block;margin-top:1.5rem;
      background:rgba(99,102,241,.15);border:1px solid rgba(99,102,241,.35);
      color:#a5b4fc;padding:.6rem 1.4rem;border-radius:.75rem;
      text-decoration:none;font-size:.88rem;transition:background .2s;
    }
    a:hover{background:rgba(99,102,241,.28);}
  </style>
</head>
<body>
<div class="card">
  <div class="code">404</div>
  <h2>Page Not Found</h2>
  <p>This route doesn't exist on e-dev.fun.<br>
     Head back to the hub to explore available APIs.</p>
  <a href="/">← Go to Hub</a>
</div>
</body>
</html>"""
    return Response(html, status=404, mimetype="text/html; charset=utf-8")


# ═══════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    port  = int(os.getenv("PORT", "5000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    print(f"""
╔══════════════════════════════════════════════════════════╗
║          Combined API Server — Toxic • @wiinc            ║
║  /pakinfo/   Pakistan Number & CNIC Info                 ║
║  /vinfo/     Vehicle Registration Info                   ║
╚══════════════════════════════════════════════════════════╝
  Running on http://0.0.0.0:{port}
  API Key   : {API_KEY}
""")
    app.run(host="0.0.0.0", port=port, debug=debug)
