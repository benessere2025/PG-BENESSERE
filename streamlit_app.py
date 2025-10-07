
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

st.markdown("""
<style>
:root{
  --bg:#0f0718; --brand:#2E0647; --accent:#7C4DFF; --text:#ECE8F7; --muted:#B7A8D9;
}
.main { background: var(--bg); color: var(--text); }
h1,h2,h3,h4 { color: var(--text); }
.block-container { padding-top: 1rem; }
.btn a { text-decoration:none; background: var(--accent); color:#0c0613; 
  padding:.6rem 1rem; border-radius:12px; font-weight:800; }
.card{background:#1b0f2b; border:1px solid #2a1b40; border-radius:16px; padding:1rem; margin:.4rem 0;}
.price{background:rgba(124,77,255,.15); padding:.2rem .6rem; border-radius:999px;}
hr{border: none; border-top: 1px solid #2a1b40;}
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

st.sidebar.image(_find_image("logo.jpg"), width=140), width=140)
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
        st.markdown('<div class="btn"><a href="?Repertorio">Ver repertorio</a></div>', unsafe_allow_html=True)
    with col2:
        _safe_image("bowl2.jpg", use_column_width=True)
    st.markdown("### Destacados")
    cols = st.columns(4)
    sample = []
    for cat in MENU.values():
        sample += cat[:2]
    for i, it in enumerate(sample[:4]):
        with cols[i]:
            st.markdown(f'<div class="card"><h4>{it["name"]}</h4><p>{it["desc"]}</p>'
                        f'<span class="price">Bs {it["price"]:.2f}</span></div>', unsafe_allow_html=True)
    _safe_image("kiosk.jpg", width=360); _safe_image("bowl.jpg", width=360)

elif page == "Repertorio":
    st.title("Repertorio")
    for cat, items in MENU.items():
        st.subheader(cat.capitalize())
        cols = st.columns(3)
        for i, it in enumerate(items):
            with cols[i % 3]:
                st.markdown(f'<div class="card"><h4>{it["name"]}</h4><p>{it["desc"]}</p>'
                            f'<span class="price">Bs {it["price"]:.2f}</span></div>', unsafe_allow_html=True)

elif page == "Nosotros":
    st.title("Nosotros")
    st.write("""
**Benessere** es una cadena de snacks saludables en campus universitarios. Estamos en la
*Universidad Privada del Valle* y venimos a servirte de la mejor manera: rápido, fresco y con
una estética que te inspira a cuidarte.

Nuestro repertorio se centra en bowls de **Açaí Zero** en dos tamaños (120g y 180g),
ensaladas completas, cereales y jugos 100% naturales. Ingredientes reales, porciones honestas y precios justos.
    """)
    _safe_image("juices.jpg", width=420); _safe_image("bowl2.jpg", width=420)

elif page == "Ubicación":
    st.title("Ubicación")
    st.write("Benessere — Campus **Universidad Privada del Valle**.")
    html(
        """
        <iframe
          src="https://www.google.com/maps?q=Universidad%20Privada%20del%20Valle&output=embed"
          width="100%" height="380" style="border:0;border-radius:16px;"
          allowfullscreen="" loading="lazy"></iframe>
        """, height=400
    )
    st.markdown(
        '<div class="btn"><a target="_blank" href="https://www.google.com/maps/search/?api=1&query=Universidad%20Privada%20del%20Valle">Abrir en Google Maps</a></div>',
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
