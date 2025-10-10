# app.py / streamlit_app.py

import json
import random
import hashlib
from pathlib import Path
from datetime import datetime, timedelta, timezone

import streamlit as st
from streamlit.components.v1 import html  # (también usaremos st.components.v1.html)

# ----------------------- Rutas y recursos -----------------------
ROOT = Path(_file_).parent
IMG = ROOT / "static" / "images"
MENU_PATH = ROOT / "data" / "menu.json"

# --------------------- Configuración de página ------------------
st.set_page_config(page_title="Benessere", page_icon=str(IMG / "logo.jpg"), layout="wide")

# --------------------------- Estilos ----------------------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#0f0718; --card:#1b0f2b; --border:#2a1b40; --text:#ECE8F7; --muted:#B7A8D9; --accent:#7C4DFF;
}
html, body, .main { background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; }
.block-container { max-width: 1200px; padding-top: 0.8rem; }
h1,h2,h3,h4 { color: var(--text); letter-spacing: .2px; }
p { color: var(--muted); }

/* Tarjetas */
.card{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 14px;
  margin: .6rem 0;
  box-shadow: 0 6px 18px rgba(0,0,0,.18);
  transition: transform .12s ease, box-shadow .12s ease, border-color .12s ease;
}
.card:hover{
  transform: translateY(-2px);
  box-shadow: 0 10px 22px rgba(0,0,0,.26);
  border-color:#3a2b57;
}
.price{ background:rgba(124,77,255,.18); padding:.25rem .7rem; border-radius:999px; font-weight:600; }

/* Imagen de producto */
.product-img img{
  border-radius: 12px;
  width: 120px;
  height: 120px;
  object-fit: cover;
  border:1px solid var(--border);
}

/* Avatar equipo */
.team-card img{
  border-radius: 18px;
  width: 100%;
  height: 220px;
  object-fit: cover;
  border:1px solid var(--border);
}

/* Limpieza UI Streamlit */
#MainMenu, header, footer {visibility: hidden;}

/* Ocultar solo el título "Bienestar que se come" */
.ocultar-titulo {
  display: none;
}
</style>
""", unsafe_allow_html=True)

# ------------------------- Utilidades ---------------------------
def _find_image(filename: str):
    candidates = [
        IMG / filename,
        Path.cwd() / "static" / "images" / filename,
        ROOT / "static" / "images" / filename,
        Path(filename),
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return None

def _safe_image(filename: str, **kwargs):
    p = _find_image(filename)
    if p:
        st.image(p, **kwargs)
    else:
        st.info(f"[imagen no encontrada: {filename}]")

def load_menu():
    candidates = [MENU_PATH, Path.cwd() / "data" / "menu.json", ROOT / "data" / "menu.json"]
    for p in candidates:
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    # fallback mínimo
    return {
        "bowls": [
            {"name": "Açaí Zero 180g", "desc": "Açaí sin azúcar + toppings. Tamaño M.", "price": 30},
            {"name": "Açaí Zero 120g", "desc": "Açaí sin azúcar + toppings. Tamaño S.", "price": 25},
        ],
        "bebidas": [
            {"name": "Jugo Natural 350 ml", "desc": "Fruta 100% | vaso S", "price": 7},
            {"name": "Jugo Natural 600 ml", "desc": "Fruta 100% | vaso M", "price": 9},
        ],
    }

MENU = load_menu()

# ------------------- Benessere Loyalty: datos -------------------
DB_PATH = ROOT / "data" / "loyalty.json"
CHECKIN_CODE = "BENESSERE-CHECKIN"         # (si luego quieres añadir UI de check-in)
HAPPY_HOUR = (15, 16)                      # 15:00–16:00

# Recompensas de la ruleta (con tus probabilidades)
SPIN_REWARDS = [
    {"label": "🎟 -10% en Açaí",            "points": 0,   "coupon": "DESC10-ACAI",     "w": 4},
    {"label": "🧃 -15% en Jugo",             "points": 0,   "coupon": "DESC15-JUGO",     "w": 6},
    {"label": "🎉 +100 pts",                 "points": 100, "coupon": None,              "w": 30},
    {"label": "💎 +500 pts",                 "points": 500, "coupon": None,              "w": 5},
    {"label": "⭐ +75 pts",                  "points": 75,  "coupon": None,              "w": 40},
    {"label": "🥣 -15% en Granola",          "points": 0,   "coupon": "DESC15-GRANOLA",  "w": 5},
    {"label": "🥣 -15% en Overnight Oats",   "points": 0,   "coupon": "DESC15-OATS",     "w": 5},
    {"label": "🍧 Açaí GRATIS",              "points": 0,   "coupon": "FREE-ACAI",       "w": 1},
    {"label": "🧃 Jugo GRATIS",              "points": 0,   "coupon": "FREE-JUGO",       "w": 1},
    {"label": "🥣 -50% en Granola",          "points": 0,   "coupon": "DESC50-GRANOLA",  "w": 3},
]

# Zona de canjeo (tus valores)
REDEEM_ITEMS = [
    {"name": "Açaí Zero 120g", "cost": 2500, "coupon": "CANJ-ACAI120"},
    {"name": "Açaí Zero 180g", "cost": 3000, "coupon": "CANJ-ACAI180"},
    {"name": "Jugo Natural 350 ml", "cost": 2000, "coupon": "CANJ-J350"},
    {"name": "Jugo Natural 600 ml", "cost": 2600, "coupon": "CANJ-J600"},
    {"name": "Granola", "cost": 2400, "coupon": "CANJ-GRANOLA"},
]

# ------------------ Persistencia y helpers puntos ---------------
def _now():
    return datetime.now(timezone.utc) - timedelta(hours=4)  # Bolivia

def _today_str():
    return _now().strftime("%Y-%m-%d")

def _load_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        try:
            return json.loads(DB_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def _save_db(db):
    DB_PATH.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")

def _uid(raw: str):
    return hashlib.sha1(raw.strip().lower().encode("utf-8")).hexdigest()[:12]

def get_user(db, user_id):
    u = db.get("users", {}).get(user_id)
    if not u:
        u = {
            "id": user_id,
            "name": "",
            "points": 0,
            "created": _now().isoformat(),
            "last_spin": None,
            "daily": {},            # por fecha: {steps_done, gym_done, food_done, checkin}
            "ref_code": user_id[:6].upper(),
            "referred_by": None,
            "purchases": [],        # reservado
            "coupons": [],
        }
        db.setdefault("users", {})[user_id] = u
    return u

def add_points(u, db, pts, reason=""):
    u["points"] = int(u.get("points", 0)) + int(pts)
    db.setdefault("history", []).append(
        {"uid": u["id"], "ts": _now().isoformat(), "delta": pts, "reason": reason}
    )

def ensure_daily(u):
    d = u["daily"].get(_today_str()) or {
        "steps_done": False,
        "gym_done": False,
        "food_done": False,
        "checkin": False,
    }
    u["daily"][_today_str()] = d
    return d

def can_spin_today(u):
    last = u.get("last_spin")
    return (not last) or (last.split("T")[0] != _today_str())

def spin(u, db):
    if not can_spin_today(u):
        return None, "Ya giraste hoy."
    weights = [r.get("w", 1) for r in SPIN_REWARDS]
    prize = random.choices(SPIN_REWARDS, weights=weights, k=1)[0]
    if prize["points"]:
        add_points(u, db, prize["points"], "Ruleta diaria")
    if prize["coupon"]:
        u.setdefault("coupons", []).append(
            {"code": prize["coupon"], "ts": _now().isoformat(), "source": "Ruleta"}
        )
    u["last_spin"] = _now().isoformat()
    return prize, None

def redeem(u, db, item):
    cost = int(item["cost"])
    if u["points"] < cost:
        return False, "No tienes puntos suficientes."
    u["points"] -= cost
    code = item["coupon"]
    u["coupons"].append({"code": code, "ts": _now().isoformat(), "source":"Canje"})
    db.setdefault("redemptions", []).append({"uid": u["id"], "item": item["name"], "ts": _now().isoformat()})
    return True, code

def leaderboard(db, top_n=10):
    users = list(db.get("users", {}).values())
    users.sort(key=lambda x: x.get("points", 0), reverse=True)
    return users[:top_n]

def is_happy_hour():
    now = _now()
    return HAPPY_HOUR[0] <= now.hour < HAPPY_HOUR[1]

# --------------- Ruleta (HTML/CSS + animación) -----------------
def _wrap_label(txt: str, max_len=16):
    t = txt.strip()
    if len(t) <= max_len:
        return t
    cut = t.rfind(" ", 0, max_len)
    if cut == -1:
        cut = max_len
    return f"{t[:cut].strip()}<br>{t[cut:].strip()}"

def build_wheel_html_anim(labels, start_deg=0, end_deg=0, duration_ms=3200, sound=True):
    n = len(labels)
    step = 360 / n
    colors = ["#8353FF", "#6E42E6"]
    ring   = "#2A1B40"
    text_c = "#FFFFFF"
    pointer_c = "#ECE8F7"
    hub_bg = "#0F0718"
    label_radius = 112
    size = 340

    stops = []
    for i in range(n):
        a0 = i * step
        a1 = (i + 1) * step
        c  = colors[i % 2]
        stops.append(f"{c} {a0}deg {a1}deg")
    gradient = ", ".join(stops)

    safe_labels = [_wrap_label(l, max_len=18) for l in labels]
    label_divs = []
    for i, txt in enumerate(safe_labels):
        center = (i * step) + (step / 2)
        label_divs.append(
            f'''
            <div class="label" style="
                 transform: rotate({center}deg)
                            translate({label_radius}px)
                            rotate({-center}deg);
            ">
              <span class="pill">{txt}</span>
            </div>
            '''
        )

    sound_flag = "true" if sound else "false"
    dur_sec = duration_ms / 1000.0

    html_code = f"""
    <style>
      .wheel-wrap {{
        position: relative; width: {size}px; height: {size}px; margin: 0 auto;
      }}
      .wheel {{
        width: 100%; height: 100%; border-radius: 50%;
        border: 12px solid {ring};
        background: conic-gradient({gradient});
        transform: rotate(-{start_deg}deg);
        box-shadow: 0 14px 28px rgba(0,0,0,.35);
      }}
      .pointer {{
        position: absolute; left: 50%; top: -6px; transform: translateX(-50%);
        width: 0; height: 0;
        border-left: 12px solid transparent; border-right: 12px solid transparent;
        border-bottom: 22px solid {pointer_c};
        filter: drop-shadow(0 2px 6px rgba(0,0,0,.25));
        z-index: 3;
      }}
      .hub {{
        position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%);
        width: 86px; height: 86px; border-radius: 50%;
        background: {hub_bg};
        border: 6px solid {ring};
        box-shadow: inset 0 0 12px rgba(0,0,0,.55);
        z-index: 2;
      }}
      .labels {{ position: absolute; inset: 0; }}
      .label {{
        position: absolute; left: 50%; top: 50%;
        transform-origin: 0 0;
        font-weight: 800; font-size: 13px; line-height: 1.05; letter-spacing:.2px;
        color: {text_c}; text-align: center; z-index: 2;
      }}
      .label .pill {{
        display:inline-block; max-width: 120px;
        padding: 2px 8px; border-radius: 10px;
        background: rgba(15,7,24,.35); text-shadow: 0 1px 1px rgba(0,0,0,.45);
        white-space: normal;
      }}
      @media (max-width: 480px) {{
        .wheel-wrap {{ width: 280px; height: 280px; }}
        .label {{ font-size: 12px; }}
        .label .pill {{ max-width: 100px; }}
      }}
    </style>

    <div class="wheel-wrap">
      <div class="pointer"></div>
      <div id="wheel" class="wheel"></div>
      <div class="labels">
        {''.join(label_divs)}
      </div>
      <div class="hub"></div>
    </div>

    <script>
      (function() {{
        const soundOn = {sound_flag};
        const duration = {duration_ms};
        const end = -({end_deg});
        const wheel = document.getElementById('wheel');

        let ctx, spinOsc, spinGain;
        function ensureCtx() {{
          if (!ctx) {{
            const AC = window.AudioContext || window.webkitAudioContext;
            if (AC) ctx = new AC();
          }}
          if (ctx && ctx.state === 'suspended') ctx.resume();
        }}
        function playSpin() {{
          if (!soundOn) return;
          ensureCtx();
          if (!ctx) return;
          spinOsc = ctx.createOscillator();
          spinGain = ctx.createGain();
          spinOsc.type = 'sawtooth';
          spinOsc.frequency.setValueAtTime(220, ctx.currentTime);
          spinGain.gain.setValueAtTime(0.0001, ctx.currentTime);
          spinGain.gain.exponentialRampToValueAtTime(0.08, ctx.currentTime + 0.2);
          spinOsc.connect(spinGain).connect(ctx.destination);
          spinOsc.start();
          spinOsc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + {dur_sec});
          spinGain.gain.setTargetAtTime(0.0001, ctx.currentTime + {dur_sec} - 0.2, 0.15);
        }}
        function stopSpin() {{
          try {{ if (spinOsc) spinOsc.stop(); }} catch(e) {{}}
          try {{ if (spinOsc) spinOsc.disconnect(); }} catch(e) {{}}
          try {{ if (spinGain) spinGain.disconnect(); }} catch(e) {{}}
          spinOsc = null; spinGain = null;
        }}
        function playPop() {{
          if (!soundOn) return;
          ensureCtx();
          if (!ctx) return;
          const o = ctx.createOscillator();
          const g = ctx.createGain();
          o.type = 'square';
          o.frequency.setValueAtTime(660, ctx.currentTime);
          g.gain.setValueAtTime(0.001, ctx.currentTime);
          g.gain.exponentialRampToValueAtTime(0.12, ctx.currentTime + 0.01);
          g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.15);
          o.connect(g).connect(ctx.destination);
          o.start();
          o.stop(ctx.currentTime + 0.16);
        }}

        requestAnimationFrame(() => {{
          wheel.style.transition = 'transform ' + duration + 'ms cubic-bezier(.17,.67,.29,1.27)';
          playSpin();
          wheel.addEventListener('transitionend', () => {{ stopSpin();
