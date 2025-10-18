from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import os

app = FastAPI()

# Criar pasta static caso não exista
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Criação do banco de dados e tabelas
def init_db():
    conn = sqlite3.connect("lives.db")
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS twitch (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_transmissao TEXT,
        horas_transmitidas TEXT,
        visualizacoes INTEGER,
        seguidores_novos INTEGER,
        subscribers_novos INTEGER,
        conteudo TEXT,
        valor_usd REAL,
        donates_brl REAL,
        minutos_assistidos INTEGER,
        espectadores_unicos INTEGER
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS youtube (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            data TEXT,
            horario TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/cadastro/twitch", response_class=HTMLResponse)
async def cadastro_twitch(request: Request):
    return templates.TemplateResponse("cadastro_twitch.html", {"request": request})

# Cadastro Twitch
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/cadastro/twitch", response_class=HTMLResponse)
async def cadastro_twitch(request: Request):
    return templates.TemplateResponse("cadastro_twitch.html", {"request": request})

@app.post("/cadastro/twitch")
async def salvar_twitch(request: Request):
    form = await request.form()
    # Pegar valores do form e converter
    data_transmissao = form.get('data_transmissao', '')
    horas_transmitidas = form.get('horas_transmitidas', '')
    visualizacoes = int(form.get('visualizacoes', 0) or 0)
    seguidores_novos = int(form.get('seguidores_novos', 0) or 0)
    subscribers_novos = int(form.get('subscribers_novos', 0) or 0)
    conteudo = form.get('conteudo', '')
    valor_usd = float(form.get('valor_usd', 0) or 0)
    donates_brl = float(form.get('donates_brl', 0) or 0)
    minutos_assistidos = int(form.get('minutos_assistidos', 0) or 0)
    espectadores_unicos = int(form.get('espectadores_unicos', 0) or 0)

    conn = sqlite3.connect("lives.db")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO twitch_lives (data_transmissao, horas_transmitidas, visualizacoes, seguidores_novos, subscribers_novos, conteudo, valor_usd, donates_brl, minutos_assistidos, espectadores_unicos) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (data_transmissao, horas_transmitidas, visualizacoes, seguidores_novos, subscribers_novos, conteudo, valor_usd, donates_brl, minutos_assistidos, espectadores_unicos)
    )
    conn.commit()
    conn.close()
    return RedirectResponse("/", status_code=303)

# Cadastro YouTube
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/cadastro/youtube", response_class=HTMLResponse)
async def cadastro_youtube(request: Request):
    return templates.TemplateResponse("cadastro_youtube.html", {"request": request})

@app.post("/cadastro/youtube")
async def cadastro_youtube(request: Request):
    form = await request.form()
    titulo = form.get("titulo")
    data = form.get("data")
    horario = form.get("horario")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO youtube (titulo, data, horario) VALUES (?, ?, ?)", (titulo, data, horario))
    conn.commit()
    conn.close()

    return RedirectResponse("/", status_code=303)

# Exportar registros Twitch
@app.get("/export/twitch")
def export_twitch():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM twitch")
    registros = cursor.fetchall()
    conn.close()
    return {"twitch": registros}

# Exportar registros YouTube
@app.get("/export/youtube")
def export_youtube():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM youtube")
    registros = cursor.fetchall()
    conn.close()
    return {"youtube": registros}
