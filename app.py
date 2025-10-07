
from flask import Flask, render_template, jsonify
import json, os

app = Flask(__name__)

def load_menu():
    path = os.path.join(app.root_path, "data", "menu.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

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
    return render_template("nosotros.html")

@app.route("/api/menu")
def menu_api():
    return jsonify(load_menu())

if __name__ == "__main__":
    app.run(debug=True)
