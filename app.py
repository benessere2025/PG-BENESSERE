from flask import Flask, render_template, jsonify
import json, os
from functools import lru_cache

app = Flask(__name__)

# -------- Helpers --------
DATA_PATH = os.path.join(app.root_path, "data", "menu.json")

@lru_cache(maxsize=1)
def _load_menu_raw() -> dict:
    """Lee el JSON del menú de forma robusta."""
    if not os.path.exists(DATA_PATH):
        # Fallback mínimo si el archivo no existe
        return {
            "bowls": [
                {"name": "Açaí Zero 180g", "desc": "Açaí sin azúcar + toppings. Tamaño M.", "price": 30, "img": "acai_180.jpg"},
                {"name": "Açaí Zero 120g", "desc": "Açaí sin azúcar + toppings. Tamaño S.", "price": 25, "img": "acai_120.jpg"},
            ],
            "cereales": [
                {"name": "Granola Casera", "desc": "Avena, frutos secos, miel", "price": 18, "img": "granola.jpg"},
                {"name": "Overnight Oats", "desc": "Avena, chía, yogur", "price": 20, "img": "oats.jpg"},
            ],
            "bebidas": [
                {"name": "Jugo Natural 350 ml", "desc": "Fruta 100% | vaso S", "price": 7, "img": "jugo_350.jpg"},
                {"name": "Jugo Natural 600 ml", "desc": "Fruta 100% | vaso M", "price": 9, "img": "jugo_600.jpg"},
            ],
        }
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            # normaliza tipos/llaves esperadas
            for cat in data.values():
                for it in cat:
                    it["name"] = str(it.get("name", "")).strip()
                    it["desc"] = str(it.get("desc", "")).strip()
                    it["price"] = float(it.get("price", 0))
                    it["img"] = str(it.get("img", "")).strip()
            return data
    except Exception:
        # Si el JSON está malformado, no rompemos la web
        return _load_menu_raw.cache_clear() or _load_menu_raw()

def load_menu() -> dict:
    return _load_menu_raw()

# Filtro Jinja para precios
@app.template_filter("price")
def price_fmt(value):
    try:
        return f"Bs {float(value):.2f}"
    except Exception:
        return "Bs 0.00"

# Contexto global útil (WhatsApp, horario, etc.)
@app.context_processor
def inject_globals():
    return {
        "WA_NUMBER": "59176073314",
        "SCHEDULE": "9:00 – 21:00",
        "BRAND": "Benessere",
    }

# -------- Rutas --------
@app.route("/")
def index():
    items = load_menu()
    return render_template("index.html", menu=items)

@app.route("/menu")
def menu():
    return render_template("menu.html", menu=load_menu())

@app.route("/marca")
def brand():
    return render_template("brand.html")

@app.route("/ubicacion")
def location():
    return render_template("location.html")

@app.route("/detalles")
def details():
    return render_template("details.html")

@app.route("/nosotros")
def about():
    # Puedes mostrar el equipo en esta misma plantilla.
    # Asegúrate de que 'nosotros.html' lo renderice (ver instrucción debajo).
    team = [
        {"name": "Andrea", "role": "Atención & Operaciones", "img": "team_1.jpg"},
        {"name": "Carlos", "role": "Bar & Preparación", "img": "team_2.jpg"},
        {"name": "Gustavo", "role": "Gestión & Marca", "img": "team_3.jpg"},
    ]
    return render_template("nosotros.html", team=team)

@app.route("/api/menu")
def menu_api():
    return jsonify(load_menu())

if __name__ == "__main__":
    app.run(debug=True)
