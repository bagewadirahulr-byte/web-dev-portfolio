"""
URL Shortener - Flask Application
A full-featured URL shortener with analytics, custom codes, and QR code generation.
"""

import os
import string
import random
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, redirect, render_template_string, abort
import qrcode
import qrcode.image.svg
import io
import base64

app = Flask(__name__)
DATABASE = os.environ.get("DATABASE_PATH", "urls.db")

# ──────────────────────────────────────────────
#  Database helpers
# ──────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                original    TEXT    NOT NULL,
                short_code  TEXT    NOT NULL UNIQUE,
                clicks      INTEGER DEFAULT 0,
                created_at  TEXT    NOT NULL,
                expires_at  TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS clicks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                short_code  TEXT NOT NULL,
                clicked_at  TEXT NOT NULL,
                ip_address  TEXT,
                user_agent  TEXT
            )
        """)
        conn.commit()


# ──────────────────────────────────────────────
#  Utility functions
# ──────────────────────────────────────────────

def generate_short_code(length: int = 6) -> str:
    """Generate a random alphanumeric short code."""
    chars = string.ascii_letters + string.digits
    while True:
        code = "".join(random.choices(chars, k=length))
        with get_db() as conn:
            exists = conn.execute(
                "SELECT 1 FROM urls WHERE short_code = ?", (code,)
            ).fetchone()
        if not exists:
            return code


def make_qr_base64(url: str) -> str:
    """Return a base64-encoded PNG QR code for the given URL."""
    img = qrcode.make(url)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


def get_base_url():
    scheme = request.headers.get("X-Forwarded-Proto", request.scheme)
    return f"{scheme}://{request.host}".rstrip("/")


# ──────────────────────────────────────────────
#  HTML Template
# ──────────────────────────────────────────────

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>SnapURL – Instant URL Shortener</title>
  <meta name="description" content="SnapURL – shorten any link instantly, track clicks, generate QR codes.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg:       #0d0f17;
      --surface:  #161928;
      --card:     #1e2235;
      --border:   #2a2f4a;
      --accent:   #6c63ff;
      --accent2:  #00d4aa;
      --text:     #e8eaf6;
      --muted:    #7b82a6;
      --red:      #ff5c7a;
      --radius:   14px;
      --shadow:   0 8px 32px rgba(0,0,0,0.4);
    }

    body {
      font-family: 'Inter', sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      background-image:
        radial-gradient(ellipse 60% 40% at 50% -10%, rgba(108,99,255,.25) 0%, transparent 70%),
        radial-gradient(ellipse 40% 30% at 80% 80%,  rgba(0,212,170,.15) 0%, transparent 70%);
    }

    /* ── NAV ── */
    nav {
      display: flex; align-items: center; justify-content: space-between;
      padding: 1.2rem 2rem;
      border-bottom: 1px solid var(--border);
      backdrop-filter: blur(10px);
      position: sticky; top: 0; z-index: 100;
      background: rgba(13,15,23,.8);
    }
    .logo { font-size: 1.4rem; font-weight: 800; letter-spacing: -0.5px; }
    .logo span { color: var(--accent); }
    .nav-badge {
      background: linear-gradient(135deg, var(--accent), var(--accent2));
      color: #fff; font-size: .72rem; font-weight: 600;
      padding: .25rem .7rem; border-radius: 50px;
    }

    /* ── HERO ── */
    .hero { text-align: center; padding: 5rem 1rem 3rem; }
    .hero h1 {
      font-size: clamp(2rem, 5vw, 3.5rem); font-weight: 800;
      line-height: 1.1; letter-spacing: -1px;
      background: linear-gradient(135deg, #fff 30%, var(--accent));
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .hero p { color: var(--muted); margin-top: .8rem; font-size: 1.1rem; }

    /* ── CARD ── */
    .card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1.75rem;
      box-shadow: var(--shadow);
    }

    /* ── FORM ── */
    .form-container { max-width: 680px; margin: 0 auto 3rem; padding: 0 1rem; }
    .input-group { display: flex; gap: .6rem; flex-wrap: wrap; margin-bottom: 1rem; }
    input[type="url"], input[type="text"] {
      flex: 1 1 260px;
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--text);
      border-radius: 10px;
      padding: .85rem 1.1rem;
      font-size: .95rem; font-family: inherit;
      outline: none;
      transition: border-color .2s, box-shadow .2s;
    }
    input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(108,99,255,.2); }
    input::placeholder { color: var(--muted); }

    .btn {
      padding: .85rem 1.6rem; border-radius: 10px;
      font-size: .95rem; font-weight: 600; cursor: pointer;
      border: none; transition: transform .15s, box-shadow .15s, opacity .15s;
      font-family: inherit;
    }
    .btn:active { transform: scale(.97); }
    .btn-primary {
      background: linear-gradient(135deg, var(--accent), #8b84ff);
      color: #fff;
      box-shadow: 0 4px 20px rgba(108,99,255,.4);
    }
    .btn-primary:hover { box-shadow: 0 6px 28px rgba(108,99,255,.6); transform: translateY(-1px); }
    .btn-sm { padding: .5rem 1rem; font-size: .82rem; border-radius: 8px; }
    .btn-copy {
      background: rgba(0,212,170,.15); color: var(--accent2);
      border: 1px solid rgba(0,212,170,.3);
    }
    .btn-copy:hover { background: rgba(0,212,170,.25); }
    .btn-danger {
      background: rgba(255,92,122,.12); color: var(--red);
      border: 1px solid rgba(255,92,122,.3);
    }
    .btn-danger:hover { background: rgba(255,92,122,.22); }

    .options-row { display: flex; gap: .6rem; flex-wrap: wrap; }
    .options-row input { flex: 1 1 180px; }
    label { font-size: .82rem; color: var(--muted); display: block; margin-bottom: .3rem; }

    /* ── RESULT ── */
    #result { margin-top: 1.2rem; display: none; }
    .result-url {
      font-size: 1.1rem; font-weight: 600;
      color: var(--accent2); word-break: break-all;
    }
    .result-row { display: flex; align-items: center; gap: .8rem; flex-wrap: wrap; margin-top: .6rem; }
    #qr-img { width: 120px; height: 120px; border-radius: 10px; margin-top: .8rem; }

    /* ── STATS ── */
    .section { max-width: 900px; margin: 0 auto 4rem; padding: 0 1rem; }
    .section-title {
      font-size: 1.2rem; font-weight: 700; margin-bottom: 1.2rem;
      display: flex; align-items: center; gap: .6rem;
    }
    .section-title::after {
      content: ''; flex: 1; height: 1px; background: var(--border);
    }

    /* ── TABLE ── */
    .table-wrap { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; font-size: .88rem; }
    th {
      text-align: left; padding: .7rem 1rem;
      color: var(--muted); font-weight: 600; font-size: .78rem;
      text-transform: uppercase; letter-spacing: .06em;
      border-bottom: 1px solid var(--border);
    }
    td { padding: .75rem 1rem; border-bottom: 1px solid rgba(255,255,255,.04); vertical-align: middle; }
    tr:last-child td { border-bottom: none; }
    tr:hover td { background: rgba(255,255,255,.025); }
    .code-badge {
      font-family: monospace; font-size: .88rem; font-weight: 700;
      color: var(--accent); background: rgba(108,99,255,.12);
      padding: .2rem .55rem; border-radius: 6px;
    }
    .click-badge {
      display: inline-flex; align-items: center; gap: .3rem;
      background: rgba(0,212,170,.1); color: var(--accent2);
      padding: .2rem .55rem; border-radius: 50px; font-size: .8rem; font-weight: 600;
    }
    .url-cell { max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--muted); }
    .actions-cell { display: flex; gap: .4rem; }

    /* ── TOAST ── */
    #toast {
      position: fixed; bottom: 2rem; left: 50%; transform: translateX(-50%) translateY(80px);
      background: var(--accent2); color: #0d0f17;
      padding: .7rem 1.4rem; border-radius: 50px;
      font-weight: 600; font-size: .9rem;
      transition: transform .35s cubic-bezier(.34,1.56,.64,1);
      z-index: 999; pointer-events: none;
    }
    #toast.show { transform: translateX(-50%) translateY(0); }

    /* ── EMPTY ── */
    .empty { text-align: center; padding: 3rem 1rem; color: var(--muted); }
    .empty .icon { font-size: 3rem; margin-bottom: .8rem; }

    /* ── ANIMATIONS ── */
    @keyframes fadeIn { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
    .animate-in { animation: fadeIn .5s ease forwards; }
  </style>
</head>
<body>

<nav>
  <div class="logo">Snap<span>URL</span></div>
  <div class="nav-badge">⚡ Free &amp; Fast</div>
</nav>

<section class="hero">
  <h1>Shorten. Share. Track.</h1>
  <p>Transform long URLs into clean, shareable links in one click.</p>
</section>

<!-- ── SHORTEN FORM ── -->
<div class="form-container animate-in">
  <div class="card">
    <div class="input-group">
      <input type="url" id="longUrl" placeholder="Paste your long URL here…" />
      <button class="btn btn-primary" onclick="shortenUrl()" id="shortenBtn">⚡ Shorten</button>
    </div>
    <div class="options-row">
      <div style="flex:1 1 180px">
        <label>Custom alias (optional)</label>
        <input type="text" id="customCode" placeholder="e.g. my-link" maxlength="20" />
      </div>
      <div style="flex:1 1 180px">
        <label>Expires after (days, optional)</label>
        <input type="text" id="expiry" placeholder="e.g. 30" />
      </div>
    </div>

    <!-- result -->
    <div id="result" class="card" style="margin-top:1.2rem; background: var(--surface);">
      <div style="color:var(--muted); font-size:.82rem; margin-bottom:.4rem;">Your short link</div>
      <a id="shortLink" class="result-url" href="#" target="_blank"></a>
      <div class="result-row">
        <button class="btn btn-sm btn-copy" onclick="copyLink()">📋 Copy</button>
        <button class="btn btn-sm" style="background:rgba(108,99,255,.15);color:var(--accent);border:1px solid rgba(108,99,255,.3)" onclick="toggleQR()">🔳 QR Code</button>
      </div>
      <img id="qr-img" src="" alt="QR Code" style="display:none;" />
    </div>
  </div>
</div>

<!-- ── URLS TABLE ── -->
<section class="section">
  <div class="section-title">📊 All Shortened URLs</div>
  <div class="card">
    <div class="table-wrap">
      <table id="urlTable">
        <thead>
          <tr>
            <th>Short Code</th>
            <th>Original URL</th>
            <th>Clicks</th>
            <th>Created</th>
            <th>Expires</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody id="urlBody">
          <tr><td colspan="6"><div class="empty"><div class="icon">🔗</div><p>No links yet — create your first one above!</p></div></td></tr>
        </tbody>
      </table>
    </div>
  </div>
</section>

<div id="toast">✅ Copied to clipboard!</div>

<script>
  const BASE = window.location.origin;
  let currentShortUrl = "";
  let currentQrB64  = "";

  // ── Load table on start ──
  async function loadUrls() {
    const res  = await fetch("/api/urls");
    const data = await res.json();
    const body = document.getElementById("urlBody");
    if (!data.urls || data.urls.length === 0) {
      body.innerHTML = `<tr><td colspan="6"><div class="empty"><div class="icon">🔗</div><p>No links yet — create your first one above!</p></div></td></tr>`;
      return;
    }
    body.innerHTML = data.urls.map(u => `
      <tr id="row-${u.short_code}">
        <td><span class="code-badge">${escHtml(u.short_code)}</span></td>
        <td><div class="url-cell" title="${escHtml(u.original)}">${escHtml(u.original)}</div></td>
        <td><span class="click-badge">👆 ${u.clicks}</span></td>
        <td style="color:var(--muted);font-size:.82rem;">${fmtDate(u.created_at)}</td>
        <td style="color:var(--muted);font-size:.82rem;">${u.expires_at ? fmtDate(u.expires_at) : '—'}</td>
        <td class="actions-cell">
          <button class="btn btn-sm btn-copy" onclick="copyText('${BASE}/${escHtml(u.short_code)}')">📋</button>
          <button class="btn btn-sm btn-danger" onclick="deleteUrl('${escHtml(u.short_code)}')">🗑</button>
        </td>
      </tr>
    `).join("");
  }

  // ── Shorten ──
  async function shortenUrl() {
    const url    = document.getElementById("longUrl").value.trim();
    const code   = document.getElementById("customCode").value.trim();
    const expiry = document.getElementById("expiry").value.trim();
    const btn    = document.getElementById("shortenBtn");

    if (!url) { showToast("⚠️ Please enter a URL", "#ff5c7a"); return; }

    btn.disabled = true; btn.textContent = "⏳ Shortening…";
    try {
      const res  = await fetch("/api/shorten", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, custom_code: code || null, expiry_days: expiry ? parseInt(expiry) : null })
      });
      const data = await res.json();
      if (!res.ok) { showToast("❌ " + (data.error || "Error"), "#ff5c7a"); return; }

      currentShortUrl = data.short_url;
      currentQrB64    = data.qr_code;

      const linkEl = document.getElementById("shortLink");
      linkEl.href        = currentShortUrl;
      linkEl.textContent = currentShortUrl;

      const resultEl = document.getElementById("result");
      resultEl.style.display = "block";
      document.getElementById("qr-img").style.display = "none";

      document.getElementById("longUrl").value   = "";
      document.getElementById("customCode").value = "";
      document.getElementById("expiry").value     = "";

      await loadUrls();
    } finally {
      btn.disabled = false; btn.textContent = "⚡ Shorten";
    }
  }

  // ── Delete ──
  async function deleteUrl(code) {
    if (!confirm(`Delete /${code}?`)) return;
    const res = await fetch(`/api/urls/${code}`, { method: "DELETE" });
    if (res.ok) { showToast("🗑 Deleted!"); await loadUrls(); }
  }

  // ── Copy ──
  function copyLink() { copyText(currentShortUrl); }
  function copyText(text) {
    navigator.clipboard.writeText(text).then(() => showToast("✅ Copied!"));
  }

  // ── QR ──
  function toggleQR() {
    const img = document.getElementById("qr-img");
    if (img.style.display === "none") {
      img.src = `data:image/png;base64,${currentQrB64}`;
      img.style.display = "block";
    } else {
      img.style.display = "none";
    }
  }

  // ── Toast ──
  function showToast(msg, color="#00d4aa") {
    const t = document.getElementById("toast");
    t.textContent = msg; t.style.background = color;
    t.classList.add("show");
    setTimeout(() => t.classList.remove("show"), 2200);
  }

  // ── Helpers ──
  function escHtml(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
  function fmtDate(s) { if (!s) return '—'; return new Date(s).toLocaleDateString('en-US', {month:'short',day:'numeric',year:'numeric'}); }

  // Enter key to shorten
  document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("longUrl").addEventListener("keydown", e => { if (e.key === "Enter") shortenUrl(); });
    loadUrls();
  });
</script>
</body>
</html>
"""


# ──────────────────────────────────────────────
#  Routes
# ──────────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/shorten", methods=["POST"])
def shorten():
    data = request.get_json(force=True, silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON payload"}), 400
        
    original = (data.get("url") or "").strip()
    custom_code = (data.get("custom_code") or "").strip() or None
    expiry_days = data.get("expiry_days")

    if not original:
        return jsonify({"error": "URL is required"}), 400
    if not (original.startswith("http://") or original.startswith("https://")):
        original = "https://" + original

    # Validate / generate short code
    if custom_code:
        allowed = set(string.ascii_letters + string.digits + "-_")
        if not all(c in allowed for c in custom_code):
            return jsonify({"error": "Custom code may only contain letters, digits, - and _"}), 400
        with get_db() as conn:
            if conn.execute("SELECT 1 FROM urls WHERE short_code = ?", (custom_code,)).fetchone():
                return jsonify({"error": "That alias is already taken"}), 409
        short_code = custom_code
    else:
        short_code = generate_short_code()

    created_at = datetime.utcnow().isoformat()
    expires_at = None
    if expiry_days:
        try:
            expires_at = (datetime.utcnow() + timedelta(days=int(expiry_days))).isoformat()
        except (ValueError, TypeError):
            return jsonify({"error": "expiry_days must be an integer"}), 400

    with get_db() as conn:
        conn.execute(
            "INSERT INTO urls (original, short_code, created_at, expires_at) VALUES (?,?,?,?)",
            (original, short_code, created_at, expires_at),
        )
        conn.commit()

    short_url = f"{get_base_url()}/{short_code}"
    qr_b64 = make_qr_base64(short_url)

    return jsonify({
        "short_url": short_url,
        "short_code": short_code,
        "original": original,
        "qr_code": qr_b64,
        "created_at": created_at,
        "expires_at": expires_at,
    }), 201


@app.route("/api/urls", methods=["GET"])
def list_urls():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM urls ORDER BY id DESC LIMIT 100"
        ).fetchall()
    return jsonify({"urls": [dict(r) for r in rows]})


@app.route("/api/urls/<short_code>", methods=["DELETE"])
def delete_url(short_code):
    with get_db() as conn:
        result = conn.execute("DELETE FROM urls WHERE short_code = ?", (short_code,))
        conn.execute("DELETE FROM clicks WHERE short_code = ?", (short_code,))
        conn.commit()
    if result.rowcount == 0:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "Deleted"}), 200


@app.route("/api/urls/<short_code>/stats", methods=["GET"])
def url_stats(short_code):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM urls WHERE short_code = ?", (short_code,)).fetchone()
        if not row:
            return jsonify({"error": "Not found"}), 404
        recent = conn.execute(
            "SELECT clicked_at FROM clicks WHERE short_code = ? ORDER BY clicked_at DESC LIMIT 20",
            (short_code,)
        ).fetchall()
    return jsonify({
        **dict(row),
        "recent_clicks": [r["clicked_at"] for r in recent],
    })


@app.route("/<short_code>")
def redirect_url(short_code):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM urls WHERE short_code = ?", (short_code,)).fetchone()
        if not row:
            abort(404)

        # Check expiry
        if row["expires_at"]:
            if datetime.utcnow() > datetime.fromisoformat(row["expires_at"]):
                abort(410)  # Gone

        # Record click
        conn.execute(
            "INSERT INTO clicks (short_code, clicked_at, ip_address, user_agent) VALUES (?,?,?,?)",
            (short_code, datetime.utcnow().isoformat(),
             request.remote_addr, request.headers.get("User-Agent", ""))
        )
        conn.execute(
            "UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?", (short_code,)
        )
        conn.commit()

    return redirect(row["original"], code=302)


# ──────────────────────────────────────────────
#  Entry point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    print("\n🔗 SnapURL – URL Shortener")
    print(f"   Running at: http://localhost:{port}\n")
    app.run(debug=debug, host="0.0.0.0", port=port)
else:
    # For gunicorn: auto-init database on import
    init_db()
