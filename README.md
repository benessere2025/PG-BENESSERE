
# Benessere — Web & App

Repo: **PG-Benessere** — by `Benessere2025`

## Estructura
- `app.py` — App Flask (local/Render)
- `streamlit_app.py` — App Streamlit (Streamlit Cloud)
- `data/menu.json` — Menú editable
- `static/` — CSS/JS/Images
- `templates/` — HTML Jinja2
- `requirements.txt` — Dependencias (para ambos)
- `Procfile` — Deploy Flask en Render

## Correr localmente (Flask)
```bash
pip install -r requirements.txt
python app.py
# http://127.0.0.1:5000
```

## Correr localmente (Streamlit)
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Subir a GitHub (primera vez)
```bash
git init
git add .
git commit -m "Benessere initial commit"
git branch -M main
git remote add origin https://github.com/Benessere2025/PG-Benessere.git
git push -u origin main
```

## Desplegar en Streamlit Cloud
1. Ve a https://share.streamlit.io/ (o https://streamlit.io/cloud) e inicia sesión con GitHub.
2. New app → Repo: `Benessere2025/PG-Benessere`, Branch: `main`, File: `streamlit_app.py`.
3. Deploy. (La app leerá `data/menu.json` e imágenes de `static/`).

## Desplegar Flask en Render (opcional)
1. https://render.com → New → Web Service → Conecta `Benessere2025/PG-Benessere`.
2. Runtime: Python 3.11, Build Command: `pip install -r requirements.txt`
3. Start Command: `gunicorn app:app`
4. Deploy.
