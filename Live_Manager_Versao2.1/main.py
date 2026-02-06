from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import os
import csv
import io
import re

# --- Configuração Inicial ---
DB_NAME = "lives.db"
app = FastAPI()

# Criar pastas 'static' e 'templates' caso não existam
if not os.path.exists("static"):
    os.makedirs("static")
if not os.path.exists("templates"):
    os.makedirs("templates")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- Banco de Dados ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    # Tabela Twitch (ATUALIZADA: visualizacoes agora é REAL para aceitar decimais)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS twitch (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_transmissao TEXT,
            horas_transmitidas TEXT,
            visualizacoes REAL,
            seguidores_novos INTEGER,
            subscribers_novos INTEGER,
            conteudo TEXT,
            valor_usd REAL,
            donates_brl REAL,
            minutos_assistidos INTEGER,
            espectadores_unicos INTEGER
        )
    """)
    # Tabela YouTube
    cur.execute("""
        CREATE TABLE IF NOT EXISTS youtube (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            data TEXT,
            horario TEXT,
            visualizacoes INTEGER,
            media_visualizacoes TEXT,
            picos_simultaneos TEXT,
            likes TEXT
        )
    """)
    # Tabela Kick
    cur.execute("""
        CREATE TABLE IF NOT EXISTS kick (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_transmissao TEXT,
            horas_transmitidas TEXT,
            inscricoes_novas INTEGER,
            seguidores_novos INTEGER,
            conteudo TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- Rotas de Páginas (HTML) ---
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/cadastro/twitch", response_class=HTMLResponse)
async def form_cadastro_twitch(request: Request):
    return templates.TemplateResponse("cadastro_twitch.html", {"request": request})

@app.get("/cadastro/youtube", response_class=HTMLResponse)
async def form_cadastro_youtube(request: Request):
    return templates.TemplateResponse("cadastro_youtube.html", {"request": request})

@app.get("/cadastro/kick", response_class=HTMLResponse)
async def form_cadastro_kick(request: Request):
    return templates.TemplateResponse("cadastro_kick.html", {"request": request})

# --- Função Auxiliar de Limpeza de Moeda e Números Decimais ---
def limpar_moeda(valor_str):
    if not valor_str:
        return 0.0
    # 1. Substitui vírgula por ponto
    valor = valor_str.replace(',', '.')
    # 2. Remove tudo que NÃO for dígito ou ponto (remove letras R, U, S, $, espaços, etc)
    valor = re.sub(r'[^\d.]', '', valor)
    try:
        return float(valor)
    except ValueError:
        return 0.0

# --- Rotas de Ações (Formulários) ---
@app.post("/cadastro/twitch")
async def salvar_twitch(request: Request):
    try:
        form = await request.form()
        data_transmissao = form.get('data_transmissao', '')
        horas_transmitidas = form.get('horas_transmitidas', '')
        
        # ATUALIZADO: Agora usamos float e tratamos a vírgula
        # A função limpar_moeda serve bem aqui pois ela troca , por . e remove lixo se houver
        visualizacoes = limpar_moeda(form.get('visualizacoes', '0'))
        
        seguidores_novos = int(form.get('seguidores_novos') or 0)
        subscribers_novos = int(form.get('subscribers_novos') or 0)
        conteudo = form.get('conteudo', '')
        
        # Sanitizar os campos de moeda
        valor_usd = limpar_moeda(form.get('valor_usd', '0'))
        donates_brl = limpar_moeda(form.get('donates_brl', '0'))
        
        minutos_assistidos = int(form.get('minutos_assistidos') or 0)
        espectadores_unicos = int(form.get('espectadores_unicos') or 0)

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO twitch (data_transmissao, horas_transmitidas, visualizacoes, seguidores_novos, subscribers_novos, conteudo, valor_usd, donates_brl, minutos_assistidos, espectadores_unicos) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (data_transmissao, horas_transmitidas, visualizacoes, seguidores_novos, subscribers_novos, conteudo, valor_usd, donates_brl, minutos_assistidos, espectadores_unicos)
        )
        conn.commit()
        conn.close()
    except sqlite3.OperationalError as e:
        print(f"ERRO DE BANCO DE DADOS: {e}")
        raise HTTPException(status_code=500, detail=f"Erro de Banco de Dados: {e}. Provavelmente o arquivo 'lives.db' está desatualizado.")
    except (ValueError, TypeError) as e:
        print(f"ERRO DE DADOS DO FORMULÁRIO: {e}")
        raise HTTPException(status_code=400, detail=f"Erro nos dados do formulário: {e}.")
    
    return RedirectResponse("/", status_code=303)

@app.post("/cadastro/youtube")
async def salvar_youtube(request: Request):
    try:
        form = await request.form()
        titulo = form.get("titulo")
        data = form.get("data")
        horario = form.get("horario")
        visualizacoes = int(form.get("Visualizacoes") or 0)
        media = form.get("Media", "")
        picos = form.get("picos", "")
        likes = form.get("likes", "")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO youtube (titulo, data, horario, visualizacoes, media_visualizacoes, picos_simultaneos, likes) VALUES (?, ?, ?, ?, ?, ?, ?)", 
            (titulo, data, horario, visualizacoes, media, picos, likes)
        )
        conn.commit()
        conn.close()
    except sqlite3.OperationalError as e:
        print(f"ERRO DE BANCO DE DADOS: {e}")
        raise HTTPException(status_code=500, detail=f"Erro de Banco de Dados: {e}.")
    except (ValueError, TypeError) as e:
        print(f"ERRO DE DADOS DO FORMULÁRIO: {e}")
        raise HTTPException(status_code=400, detail=f"Erro nos dados do formulário: {e}.")

    return RedirectResponse("/", status_code=303)

@app.post("/cadastro/kick")
async def salvar_kick(request: Request):
    try:
        form = await request.form()
        data_transmissao = form.get('data_transmissao', '')
        horas_transmitidas = form.get('horario', '') 
        inscricoes_novas = int(form.get('inscricoes_novas') or 0)
        seguidores_novos = int(form.get('seguidores_novos') or 0)
        conteudo = form.get('conteudo', '')
        
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO kick (data_transmissao, horas_transmitidas, inscricoes_novas, seguidores_novos, conteudo) VALUES (?, ?, ?, ?, ?)",
            (data_transmissao, horas_transmitidas, inscricoes_novas, seguidores_novos, conteudo)
        )
        conn.commit()
        conn.close()
    except sqlite3.OperationalError as e:
        print(f"ERRO DE BANCO DE DADOS: {e}")
        raise HTTPException(status_code=500, detail=f"Erro de Banco de Dados: {e}.")
    except (ValueError, TypeError) as e:
        print(f"ERRO DE DADOS DO FORMULÁRIO: {e}")
        raise HTTPException(status_code=400, detail=f"Erro nos dados do formulário: {e}.")

    return RedirectResponse("/", status_code=303)

# --- Rotas de Exportação ---
@app.get("/export/twitch/csv")
async def export_twitch_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM twitch")
    rows = cursor.fetchall()
    if rows:
        headers = rows[0].keys()
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)
    else:
        cursor.execute("PRAGMA table_info(twitch)")
        headers = [info[1] for info in cursor.fetchall()]
        writer.writerow(headers)
    conn.close()
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=dados_twitch.csv"})

@app.get("/export/youtube/csv")
async def export_youtube_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM youtube")
    rows = cursor.fetchall()
    if rows:
        headers = rows[0].keys()
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)
    else:
        cursor.execute("PRAGMA table_info(youtube)")
        headers = [info[1] for info in cursor.fetchall()]
        writer.writerow(headers)
    conn.close()
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=dados_youtube.csv"})

@app.get("/export/kick/csv")
async def export_kick_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM kick")
    rows = cursor.fetchall()
    if rows:
        headers = rows[0].keys()
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)
    else:
        cursor.execute("PRAGMA table_info(kick)")
        headers = [info[1] for info in cursor.fetchall()]
        writer.writerow(headers)
    conn.close()
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=dados_kick.csv"})