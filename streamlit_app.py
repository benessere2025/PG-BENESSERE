import json
import streamlit as st
from pathlib import Path
from streamlit.components.v1 import html

ROOT = Path(__file__).parent
IMG = ROOT / "static" / "images"
MENU_PATH = ROOT / "data" / "menu.json"


def load_menu():
    candidates = [
        MENU_PATH,
        Path.cwd() / "data" / "menu.json",
        ROOT / "data" / "menu.json",
    ]
    for p in candidates:
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
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


st.set_page_config(page_title="Benessere", page_icon=str(IMG / "logo.jpg"), layout="wide")

# ✅ Bloque CSS limpio y funcional
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
</style>
""", unsafe_allow_html=True)


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
# ================== Benessere Loyalty Utils ==================
import random, hashlib
from datetime import datetime, timedelta, timezone

DB_PATH = ROOT / "data" / "loyalty.json"
CHECKIN_CODE = "BENESSERE-CHECKIN"            # texto que mostrará el QR del kiosco
HAPPY_HOUR = (15, 16)                         # 15:00–16:00

SPIN_REWARDS = [
    # prob: 4%
    {"label": "🎟️ -10% en Açaí",            "points": 0,   "coupon": "DESC10-ACAI",     "w": 4},
    # prob: 6%
    {"label": "🧃 -15% en Jugo",             "points": 0,   "coupon": "DESC15-JUGO",     "w": 6},
    # prob: 30%
    {"label": "🎉 +100 pts",                 "points": 100, "coupon": None,              "w": 30},
    # prob: 5%
    {"label": "💎 +500 pts",                 "points": 500, "coupon": None,              "w": 5},
    # prob: 40%
    {"label": "⭐ +75 pts",                  "points": 75,  "coupon": None,              "w": 40},
    # prob: 5%
    {"label": "🥣 -15% en Granola",          "points": 0,   "coupon": "DESC15-GRANOLA",  "w": 5},
    # prob: 5%
    {"label": "🥣 -15% en Overnight Oats",   "points": 0,   "coupon": "DESC15-OATS",     "w": 5},
    # prob: 1%
    {"label": "🍧 Açaí GRATIS",              "points": 0,   "coupon": "FREE-ACAI",       "w": 1},
    # prob: 1%
    {"label": "🧃 Jugo GRATIS",              "points": 0,   "coupon": "FREE-JUGO",       "w": 1},
    # prob: 3%
    {"label": "🥣 -50% en Granola",          "points": 0,   "coupon": "DESC50-GRANOLA",  "w": 3},
]


# 🪙 Sistema de canjeo Benessere actualizado (valores altos pero alcanzables)
REDEEM_ITEMS = [
    {"name": "Açaí Zero 120g", "cost": 2500, "coupon": "CANJ-ACAI120"},
    {"name": "Açaí Zero 180g", "cost": 3000, "coupon": "CANJ-ACAI180"},
    {"name": "Jugo Natural 350 ml", "cost": 2000, "coupon": "CANJ-J350"},
    {"name": "Jugo Natural 600 ml", "cost": 2600, "coupon": "CANJ-J600"},
    {"name": "Granola", "cost": 2400, "coupon": "CANJ-GRANOLA"},
]

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
            "daily": {},            # por fecha: {steps_done, water_done, checkin}
            "ref_code": user_id[:6].upper(),
            "referred_by": None,
            "purchases": [],       # [{"date":..., "product":"..."}]
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
        "water_done": False,   # se mantiene por compatibilidad, ya no se usa
        "checkin": False,
        "gym_done": False,     # NUEVO
        "food_done": False     # NUEVO
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
        u.setdefault("coupons", []).append({
            "code": prize["coupon"],
            "ts": _now().isoformat(),
            "source": "Ruleta"
        })
    u["last_spin"] = _now().isoformat()
    return prize, None


def checkin(u, db, code: str):
    d = ensure_daily(u)
    if d["checkin"]:
        return False, "Check-in de hoy ya registrado."
    if code.strip().upper() != CHECKIN_CODE:
        return False, "Código inválido."
    d["checkin"] = True
    add_points(u, db, 20, "Check-in local")
    return True, None

def log_steps(u, db, steps: int):
    d = ensure_daily(u)
    if d["steps_done"]:
        return False, "Reto de pasos ya completado hoy."
    if steps >= 7000:
        d["steps_done"] = True
        add_points(u, db, 30, "Reto diario: pasos")
        return True, None
    return False, "Aún no llegas a 7.000 pasos."

def log_water(u, db, liters: float):
    d = ensure_daily(u)
    if d["water_done"]:
        return False, "Reto de agua ya completado hoy."
    if liters >= 2.0:
        d["water_done"] = True
        add_points(u, db, 30, "Reto diario: agua")
        return True, None
    return False, "Aún no llegas a 2 litros."

def record_purchase(u, db, product_name):
    u["purchases"].append({"date": _now().isoformat(), "product": product_name})
    if len(u["purchases"]) >= 2:
        last, prev = u["purchases"][-1]["product"], u["purchases"][-2]["product"]
        if last == prev:
            code = f"FREE-{_today_str()}-{_uid(last)[:4]}".upper()
            u["coupons"].append({"code": code, "ts": _now().isoformat(), "source":"Semana Zero"})
            return code
    return None

def redeem(u, db, item):
    cost = int(item["cost"])
    if u["points"] < cost:
        return False, "No tienes puntos suficientes."
    u["points"] -= cost
    code = item["coupon"]
    u["coupons"].append({"code": code, "ts": _now().isoformat(), "source":"Canje"})
    db.setdefault("redemptions", []).append({"uid": u["id"], "item": item["name"], "ts": _now().isoformat()})
    return True, code

def apply_referral(db, new_user, ref_code):
    if not ref_code:
        return
    for u in db.get("users", {}).values():
        if u.get("ref_code") == ref_code.upper() and u["id"] != new_user["id"]:
            new_user["referred_by"] = u["id"]
            add_points(new_user, db, 50, "Registro con referido")
            add_points(u, db, 50, "Invitó a un amigo")
            break

def leaderboard(db, top_n=10):
    users = list(db.get("users", {}).values())
    users.sort(key=lambda x: x.get("points", 0), reverse=True)
    return users[:top_n]

def is_happy_hour():
    now = _now()
    return HAPPY_HOUR[0] <= now.hour < HAPPY_HOUR[1]
# ===========================================================
# ========= Helpers de ruleta (HTML/CSS animado) =========
def build_wheel_html(labels, active_angle_deg=0):
    n = len(labels)
    colors = ["#7C4DFF", "#9A6BFF"]  # alterna
    # fondo como conic-gradient
    stops = []
    step = 360 / n
    for i, _ in enumerate(labels):
        a0 = i * step
        a1 = (i + 1) * step
        c = colors[i % 2]
        stops.append(f"{c} {a0}deg {a1}deg")
    gradient = ", ".join(stops)
    # HTML + CSS con animación hacia el ángulo deseado
    html_code = f"""
    <style>
    .wheel-wrap {{
        position: relative; width: 320px; height: 320px; margin: 0 auto;
    }}
    .wheel {{
        width: 100%; height: 100%; border-radius: 50%;
        border: 10px solid #2a1b40;
        background: conic-gradient({gradient});
        transition: transform 3.2s cubic-bezier(.17,.67,.29,1.27);
        transform: rotate(-{active_angle_deg}deg);
        box-shadow: 0 10px 22px rgba(0,0,0,.35);
    }}
    .pointer {{
        position: absolute; left: 50%; top: -8px; transform: translateX(-50%);
        width: 0; height: 0; border-left: 12px solid transparent; border-right: 12px solid transparent;
        border-bottom: 22px solid #ECE8F7; filter: drop-shadow(0 2px 6px rgba(0,0,0,.35));
    }}
    .labels {{ position: absolute; inset: 0; }}
    .label {{
        position: absolute; left: 50%; top: 50%; transform-origin: 0 0;
        color: #0f0718; font-weight: 800; font-size: 12px; text-shadow: 0 1px 0 rgba(255,255,255,.35);
    }}
    </style>
    <div class="wheel-wrap">
      <div class="pointer"></div>
      <div class="wheel"></div>
      <div class="labels">
        {''.join([f'<div class="label" style="transform: rotate({(i*step)+(step/2)}deg) translate(100px) rotate(90deg);">{labels[i]}</div>' for i in range(n)])}
      </div>
    </div>
    """
    return html_code
# ========================================================

# ========= Chequeos simples de imagen (beta, sin romper) =========
def _try_import_pil_numpy():
    try:
        from PIL import Image, ImageStat
        import numpy as np
        return Image, ImageStat, np
    except Exception:
        return None, None, None

def verify_gym_photo(file) -> bool:
    """Heurística básica: resolución mínima + nitidez/contraste (proxy).
       Si PIL/Numpy no disponible, devolvemos True para no romper UX."""
    Image, ImageStat, np = _try_import_pil_numpy()
    if not Image:  # fallback
        return True
    try:
        img = Image.open(file).convert("RGB")
        if img.width < 300 or img.height < 300:
            return False
        # varianza de luminancia como proxy de 'real / no captura borrosa'
        gray = img.convert("L")
        arr = np.array(gray, dtype=np.float32)
        var = float(arr.var())
        return var > 300.0
    except Exception:
        return False

def verify_healthy_food(file) -> bool:
    """Heurística: proporción de verdes/colores naturales + saturación general."""
    Image, ImageStat, np = _try_import_pil_numpy()
    if not Image:
        return True
    try:
        img = Image.open(file).convert("RGB").resize((256,256))
        arr = np.asarray(img) / 255.0
        r,g,b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
        # 'verde saludable' proxy: g alto y g > r y g > b
        green_mask = (g > 0.35) & (g > r+0.05) & (g > b+0.05)
        green_ratio = green_mask.mean()
        # saturación aproximada
        maxc = arr.max(axis=2); minc = arr.min(axis=2)
        sat = (maxc - minc).mean()
        return (green_ratio > 0.20 and sat > 0.15)
    except Exception:
        return False
# ================================================================


def _safe_image(filename: str, **kwargs):
    p = _find_image(filename)
    if p:
        st.image(p, **kwargs)
    else:
        st.info(f"[imagen no encontrada: {filename}]")


MENU = load_menu()

st.sidebar.image(_find_image("logo.jpg"), width=140)
page = st.sidebar.radio(
    "Navegación",
    ["Inicio", "Repertorio", "Nosotros", "Ubicación", "Recompensas", "Zona de canjeo", "Ranking", "Más detalles"]
)

st.sidebar.markdown(
    '<div class="btn"><a target="_blank" href="https://wa.me/59176073314?text=Hola,%20quiero%20pedir%20un%20Açaí%20Zero%20180g%20y%20un%20Açaí%20Zero%20120g.">Pedir por WhatsApp</a></div>',
    unsafe_allow_html=True,
)
st.sidebar.write("Horario: **9:00 – 21:00**")
# --------- Registro simple de usuario ----------
db = _load_db()
default_name = st.session_state.get("name", "")
name = st.sidebar.text_input("Tu nombre o celular", value=default_name, placeholder="Ej: 76073314")
ref_in = st.sidebar.text_input("Código de referido (opcional)", value=st.session_state.get("ref", ""))

if st.sidebar.button("Entrar"):
    if not name.strip():
        st.sidebar.error("Ingresa tu nombre o celular")
    else:
        uid = _uid(name)
        st.session_state["uid"] = uid
        st.session_state["name"] = name.strip()
        u = get_user(db, uid)
        if not u["name"]:
            u["name"] = name.strip()
            apply_referral(db, u, ref_in)
        _save_db(db)
        st.sidebar.success(f"¡Hola, {name}! Tu código: {get_user(db, uid)['ref_code']}")

uid = st.session_state.get("uid")
current_user = get_user(db, uid) if uid else None

if current_user:
    st.sidebar.markdown(f"**Benessere Points:** {current_user['points']}")
    st.sidebar.caption(f"Código de referidos: `{current_user['ref_code']}`")
else:
    st.sidebar.info("Inicia sesión para usar Recompensas y Canjeo.")


if page == "Inicio":
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.title("Bienestar que se come")
        st.write("Bowls de **Açaí Zero** (120g/180g), ensaladas, cereales y jugos 100% naturales. Ideal para campus.")
    with col2:
        _safe_image("bowl2.jpg", use_container_width=True)

    st.markdown("### Destacados")
    cols = st.columns(4)
    sample = []
    for cat in MENU.values():
        sample += cat[:2]
    for i, it in enumerate(sample[:4]):
        with cols[i]:
            st.markdown(
                f'<div class="card"><h4>{it["name"]}</h4><p>{it["desc"]}</p>'
                f'<span class="price">Bs {it["price"]:.2f}</span></div>',
                unsafe_allow_html=True,
            )
    _safe_image("kiosk.jpg", width=360)
    _safe_image("bowl.jpg", width=360)

elif page == "Repertorio":
    st.title("Repertorio")

    order = ["bowls", "cereales", "bebidas"]
    for cat in order:
        if cat not in MENU:
            continue
        items = MENU[cat]
        st.subheader(cat.capitalize())

        for it in items:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            c1, c2 = st.columns([1, 3])
            with c1:
                st.markdown('<div class="product-img">', unsafe_allow_html=True)
                _safe_image(it.get("img", ""), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f"### {it['name']}")
                st.write(it.get("desc", ""))
                st.markdown(
                    f'<span class="price">Bs {float(it["price"]):.2f}</span>',
                    unsafe_allow_html=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)

elif page == "Nosotros":
    st.title("Nuestro equipo")
    st.write("Conoce a las personas detrás de Benessere. Energía, servicio y buena vibra todos los días en la Univalle.")

    team = [
        {"name": "Daniel S", "role": "CEO", "img": "team_1.jpg"},
        {"name": "Luis V", "role": "CFO", "img": "team_2.jpg"},
        {"name": "Antonio G", "role": "DCI", "img": "team_3.jpg"},
        {"name": "Bruno C", "role": "COO", "img": "team_4.jpg"},
        {"name": "Nicolas D", "role": "CMO", "img": "team_5.jpg"},
    ]

    cols = st.columns(3)
    for i, m in enumerate(team):
        with cols[i % 3]:
            _safe_image(m["img"], use_container_width=True)
            st.markdown(f"**{m['name']}**")
            st.caption(m["role"])

elif page == "Ubicación":
    st.title("Ubicación")
    st.write("Benessere — Campus **Universidad Privada del Valle (Santa Cruz de la Sierra)**.")
    _safe_image("univalle_sc.jpg", use_container_width=True)
    html(
        """
        <iframe
          src="https://www.google.com/maps?q=Universidad%20Privada%20del%20Valle%20Santa%20Cruz%20de%20la%20Sierra&output=embed"
          width="100%" height="380" style="border:0;border-radius:16px;"
          allowfullscreen="" loading="lazy"></iframe>
        """,
        height=400,
    )
    st.markdown(
        '<div class="btn"><a target="_blank" href="https://www.google.com/maps/search/?api=1&query=Universidad%20Privada%20del%20Valle%20Santa%20Cruz%20de%20la%20Sierra">Abrir en Google Maps</a></div>',
        unsafe_allow_html=True,
    )
    st.write("Horario: **9:00 – 21:00**")
elif page == "Recompensas":
    st.title("Recompensas")
    if not current_user:
        st.warning("Inicia sesión en la barra lateral para usar esta sección.")
        st.stop()

    u = current_user
    st.subheader(f"Tus puntos: {u['points']}")
    if is_happy_hour():
        st.success("⏰ **Happy Hour** activo: ¡descuentos especiales en tienda por 1 hora!")

    # ---------- Retos diarios ----------
    st.markdown("### Retos diarios")

    d = ensure_daily(u)
    c1, c2, c3 = st.columns(3)

    with c1:
        # Pasos (conexión futura a Apple/Samsung; por ahora manual)
        steps = st.number_input("Pasos de hoy", min_value=0, value=0, step=500)
        if st.button("Confirmar 7.000 pasos"):
            ok, msg = log_steps(u, db, int(steps))
            st.success("Reto completado +30 pts") if ok else st.error(msg)
        with st.expander("Conectar Apple/Samsung (próximamente)"):
            st.info("Para verificar pasos automáticamente se requiere app nativa (iOS/Android) "
                    "con permisos HealthKit (Apple) o Samsung Health. En web no se puede acceder "
                    "a estos datos por seguridad. Dejamos UI lista para conexión futura.")

    with c2:
        # NUEVO: Foto gym/actividad física
        st.caption("Sube foto en el gym o haciendo actividad física")
        gym_file = st.file_uploader("Foto de actividad física", type=["jpg","jpeg","png"], key="gym_up")
        if st.button("Validar foto de actividad"):
            d = ensure_daily(u)
            if d["gym_done"]:
                st.info("Este reto ya está completado hoy.")
            elif not gym_file:
                st.error("Sube una foto primero.")
            else:
                ok = verify_gym_photo(gym_file)
                if ok:
                    d["gym_done"] = True
                    add_points(u, db, 30, "Reto diario: actividad física (foto)")
                    st.success("Foto válida ✔ +30 pts")
                else:
                    st.error("No parece una foto válida de actividad física. Intenta otra.")

    with c3:
        # NUEVO: Foto de snack/comida saludable
        st.caption("Sube foto de snack/comida saludable")
        food_file = st.file_uploader("Foto de comida saludable", type=["jpg","jpeg","png"], key="food_up")
        if st.button("Validar comida saludable"):
            d = ensure_daily(u)
            if d["food_done"]:
                st.info("Este reto ya está completado hoy.")
            elif not food_file:
                st.error("Sube una foto primero.")
            else:
                ok = verify_healthy_food(food_file)
                if ok:
                    d["food_done"] = True
                    add_points(u, db, 30, "Reto diario: comida saludable (foto)")
                    st.success("¡Se ve saludable! ✔ +30 pts")
                else:
                    st.error("No parece una comida saludable (según verificación básica). Intenta otra.")

    # ---------- Ruleta del bienestar (ANIMADA) ----------
    st.markdown("### Ruleta del bienestar (diaria)")
    labels = [r["label"] for r in SPIN_REWARDS]
    spin_state = st.session_state.get("spin_state", {"angle": 0, "idx": None, "label": None})

    colA, colB = st.columns([1,1])
    with colA:
        # Render rueda con el ángulo actual (si giró, muestra animación a ese ángulo)
        st.components.v1.html(build_wheel_html(labels, spin_state["angle"]), height=380)

    with colB:
        if can_spin_today(u):
            if st.button("🎡 Girar la ruleta"):
                # Elegimos premio ponderado y calculamos ángulo exacto de llegada
                weights = [r.get("w", 1) for r in SPIN_REWARDS]
                prize = random.choices(SPIN_REWARDS, weights=weights, k=1)[0]
                idx = labels.index(prize["label"])
                n = len(labels); step = 360 / n
                center = idx * step + (step/2)
                angle = 360*4 + center  # 4 vueltas completas + caer al centro del premio

                # Aplicamos recompensa
                if prize["points"]:
                    add_points(u, db, prize["points"], "Ruleta diaria")
                if prize["coupon"]:
                    u.setdefault("coupons", []).append({
                        "code": prize["coupon"],
                        "ts": _now().isoformat(),
                        "source": "Ruleta"
                    })
                u["last_spin"] = _now().isoformat()

                # Guardamos para renderizar animación
                spin_state = {"angle": angle, "idx": idx, "label": prize["label"]}
                st.session_state["spin_state"] = spin_state
                _save_db(db)
                st.rerun()
        else:
            st.info("Ya giraste hoy. Vuelve mañana ✨")

        if spin_state["label"]:
            st.success(f"Resultado: **{spin_state['label']}**")

    # ---------- Tus cupones ----------
    st.markdown("### Tus cupones")
    if u.get("coupons"):
        for c in u["coupons"]:
            st.write(f"- `{c['code']}` (origen: {c['source']})")
    else:
        st.caption("Sin cupones todavía.")

    _save_db(db)

    if is_happy_hour():
        st.success("⏰ **Happy Hour** activo: ¡descuentos especiales en tienda por 1 hora!")

    # ---- Retos diarios ----
    st.markdown("### Retos diarios")
  # ---- Pasos ----
steps = st.number_input("Pasos de hoy", min_value=0, value=0, step=500, key="daily_steps_input")
if st.button("Confirmar 7.000 pasos", key="btn_steps_confirm"):
    ok, msg = log_steps(u, db, int(steps))
    st.success("Reto completado +30 pts") if ok else st.error(msg)

# ---- Foto gym/actividad física ----
gym_file = st.file_uploader("Foto de actividad física", type=["jpg","jpeg","png"], key="upload_gym_photo")
if st.button("Validar foto de actividad", key="btn_validate_gym"):
    d = ensure_daily(u)
    if d["gym_done"]:
        st.info("Este reto ya está completado hoy.")
    elif not gym_file:
        st.error("Sube una foto primero.")
    else:
        ok = verify_gym_photo(gym_file)
        if ok:
            d["gym_done"] = True
            add_points(u, db, 30, "Reto diario: actividad física (foto)")
            st.success("Foto válida ✔ +30 pts")
        else:
            st.error("No parece una foto válida de actividad física. Intenta otra.")

# ---- Foto comida saludable ----
food_file = st.file_uploader("Foto de comida saludable", type=["jpg","jpeg","png"], key="upload_food_photo")
if st.button("Validar comida saludable", key="btn_validate_food"):
    d = ensure_daily(u)
    if d["food_done"]:
        st.info("Este reto ya está completado hoy.")
    elif not food_file:
        st.error("Sube una foto primero.")
    else:
        ok = verify_healthy_food(food_file)
        if ok:
            d["food_done"] = True
            add_points(u, db, 30, "Reto diario: comida saludable (foto)")
            st.success("¡Se ve saludable! ✔ +30 pts")
        else:
            st.error("No parece una comida saludable (según verificación básica). Intenta otra.")

    # ---- Ruleta del bienestar ----
    st.markdown("### Ruleta del bienestar (diaria)")
    if can_spin_today(u):
        if st.button("🎡 Girar la ruleta"):
            prize, msg = spin(u, db)
            if prize:
                txt = f"Resultado: **{prize['label']}**"
                if prize["points"]>0: txt += f" → +{prize['points']} pts"
                if prize["coupon"]:   txt += f" → cupón: `{prize['coupon']}`"
                st.success(txt)
            else:
                st.error(msg or "No disponible")
    else:
        st.info("Ya giraste hoy. Vuelve mañana ✨")

    # ---- Semana Zero (demo manual) ----
    st.markdown("### Semana Zero")
    prod = st.selectbox("Registra tu compra para Semana Zero", ["Açaí Zero 120g","Açaí Zero 180g","Jugo 350 ml","Jugo 600 ml"])
    if st.button("Registrar compra"):
        code = record_purchase(u, db, prod)
        if code:
            st.success(f"¡Siguiente {prod} puede ser **GRATIS**! Cupón: `{code}`")
        else:
            st.info("Compra registrada. Si repites el producto dos veces seguidas, generamos cupón gratuito.")

    # ---- Invita a un amigo ----
    st.markdown("### Invita a un amigo")
    st.write("Comparte tu código de referido:")
    st.code(u["ref_code"], language="text")

    # ---- Tus cupones ----
    st.markdown("### Tus cupones")
    if u["coupons"]:
        for c in u["coupons"]:
            st.write(f"- `{c['code']}` (origen: {c['source']})")
    else:
        st.caption("Sin cupones todavía.")

    _save_db(db)
elif page == "Zona de canjeo":
    st.title("Zona de canjeo")
    if not current_user:
        st.warning("Inicia sesión para canjear tus puntos.")
        st.stop()

    st.subheader(f"Tu balance: {current_user['points']} pts")
    for item in REDEEM_ITEMS:
        with st.container(border=True):
            st.markdown(f"**{item['name']}** — {item['cost']} pts")
            if st.button(f"Canjear: {item['name']}", key=f"redeem-{item['name']}"):
                ok, code = redeem(current_user, db, item)
                if ok:
                    st.success(f"¡Canje hecho! Presenta el cupón `{code}` en el kiosco.")
                else:
                    st.error(code)
    _save_db(db)
elif page == "Ranking":
    st.title("Ranking Benessere")
    db = _load_db()
    top = leaderboard(db, top_n=10)
    if not top:
        st.info("Aún no hay usuarios con puntos.")
    for i, u in enumerate(top, 1):
        st.write(f"**#{i}** — {u.get('name','(sin nombre)')} — {u.get('points',0)} pts")

else:
    st.title("Más detalles")
    with st.expander("¿Qué hace diferente a Benessere?", expanded=True):
        st.write("Ingredientes reales, tiempos rápidos y diseño premium. Solo **Açaí Zero** en dos tamaños, jugos naturales, ensaladas y cereales.")
    with st.expander("¿Delivery o pickup?"):
        st.write("Pickup en kiosco y pedido por WhatsApp.")
    with st.expander("¿Personalización?"):
        st.write("Elige base, toppings y crunch a tu gusto.")

st.markdown(
    '<a style="position:fixed;right:18px;bottom:18px;background:#25D366;color:#0b1a0f;'
    'padding:10px 14px;border-radius:999px;font-weight:800;box-shadow:0 8px 20px rgba(0,0,0,.25);z-index:9999;" '
    'href="https://wa.me/59176073314?text=Hola%20Benessere,%20quiero%20hacer%20un%20pedido" target="_blank">'
    'WhatsApp</a>',
    unsafe_allow_html=True,
)

