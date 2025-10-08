import json
import streamlit as st
from pathlib import Path
from streamlit.components.v1 import html

ROOT = Path(__file__).parent
IMG = ROOT / "static" / "images"
MENU_PATH = ROOT / "data" / "menu.json"

import sys

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
    # Fallback default menu if file not found
    return {
        "bowls":[
            {"name":"Açaí Zero 180g", "desc":"Açaí sin azúcar + toppings. Tamaño M.", "price":30},
            {"name":"Açaí Zero 120g", "desc":"Açaí sin azúcar + toppings. Tamaño S.", "price":25},
        ],
        "bebidas":[
            {"name":"Jugo Natural 350 ml","desc":"Fruta 100% | vaso S","price":7},
            {"name":"Jugo Natural 600 ml","desc":"Fruta 100% | vaso M","price":9},
        ]
    }

st.set_page_config(page_title="Benessere", page_icon=str(IMG/"logo.jpg"), layout="wide")

# 🔧 CORREGIDO: un solo st.markdown con el CSS (el duplicado causaba el error)
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#0f0718; --card:#1b0f2b; --border:#2a1b40; --text:#ECE8F7; --muted:#B7A8D9; --accent:#7C4DFF;
}
html, body, .main { background: var(--bg); color: var(--text); font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto; }
.block-container { max-width: 1200px; padding-top: 0.8rem; }
h1,h2,h3,h4 { color: var(--text); letter-spacing: .2px; }
p { color: var(--muted); }

/* Cards */
.card{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 14px;
  margin: .6rem 0;
  box-shadow: 0 6px 18px rgba(0,0,0,.18);
  transition: transform .12s ease, box-shadow .12s ease, border-color .12s ease;
}
.card:hover{ transform: translateY(-2px); box-shadow: 0 10px 22px rgba(0,0,0,.26); border-color:#3a2b57; }
.price{ background:rgba(124,77,255,.18); padding:.25rem .7rem; border-radius:999px; font-weight:600; }

/* Imagen de producto consistente */
.product-img img{ border-radius: 12px; width: 120px; height: 120px; object-fit: cover; border:1px solid var(--border); }

/* Avatar equipo */
.team-card img{ border-radius: 18px; width: 100%; height: 220px; object-fit: cover; border:1px solid var(--border); }

/* Limpieza UI Streamlit */
#MainMenu, header, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def _find_image(filename: str):
    candidates = [
        IMG / filename,
        Path.cwd() / "static" / "images" / filename,
        ROOT / "static" / "images" / filename,
        Path(filename)
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

MENU = load_menu()

st.sidebar.image(_find_image("logo.jpg"), width=140)
page = st.sidebar.radio("Navegación", ["Inicio", "Repertorio", "Nosotros", "Ubicación", "Más detalles"])
st.sidebar.markdown(
    '<div class="btn"><a target="_blank" href="https://wa.me/59176073314?text=Hola,%20quiero%20pedir%20un%20Açaí%20Zero%20180g%20y%20un%20Açaí%20Zero%20120g.">Pedir por WhatsApp</a></div>',
    unsafe_allow_html=True
)
st.sidebar.write("Horario: **9:00 – 21:00**")

if page == "Inicio":
    col1, col2 = st.columns([1.2,1])
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
                unsafe_allow_html=True
            )
    _safe_image("kiosk.jpg", width=360); _safe_image("bowl.jpg", width=360)

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
        {"name": "Nicolas D", "role": "CMO", "img": "team_5.jpg"}
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

    # Foto del campus
    _safe_image("univalle_sc.jpg", use_container_width=True)

    # Mapa centrado en Univalle Santa Cruz de la Sierra
    html(
        """
        <iframe
          src="https://www.google.com/maps?q=Universidad%20Privada%20del%20Valle%20Santa%20Cruz%20de%20la%20Sierra&output=embed"
          width="100%" height="380" style="border:0;border-radius:16px;"
          allowfullscreen="" loading="lazy"></iframe>
        """,
        height=400
    )

    st.markdown(
        '<div class="btn"><a target="_blank" href="https://www.google.com/maps/search/?api=1&query=Universidad%20Privada%20del%20Valle%20Santa%20Cruz%20de%20la%20Sierra">Abrir en Google Maps</a></div>',
        unsafe_allow_html=True
    )
    st.write("Horario: **9:00 – 21:00**")

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
    'WhatsApp</a>', unsafe_allow_html=True
)

