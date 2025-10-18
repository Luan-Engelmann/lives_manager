from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import os
import csv
import io

# ============================================================
# Configuração Inicial
# ============================================================

DB_NAME = "lives.db"
app = FastAPI()

# Garante que pastas necessárias existam
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ============================================================
# Banco de Dados
# ============================================================

def init_db():
    """Cria as tabelas no banco de dados, se ainda não existirem."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS twitch (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_transmissao TEXT,
            horas_transmitidas TEXT,
            visualizacoes INTEGER,
            seguidores_novos INTEGER,
            subscribers_novos INTEGER,
            conteudo TEXT,
            valor_usd TEXT,
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


def sanitize_currency(value: str, symbol: str) -> float:
    """Remove símbolo e converte string de moeda para float."""
    if not value:
        return 0.0
    cleaned = value.replace(symbol, "").replace(",", ".").strip()
    return float(cleaned or 0.0)


# Inicializa banco ao iniciar o app
init_db()


# ============================================================
# Rotas de Páginas (HTML)
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/cadastro/twitch", response_class=HTMLResponse)
async def form_twitch(request: Request):
    return templates.TemplateResponse("cadastro_twitch.html", {"request": request})


@app.get("/cadastro/youtube", response_class=HTMLResponse)
async def form_youtube(request: Request):
    return templates.TemplateResponse("cadastro_youtube.html", {"request": request})


@app.get("/cadastro/kick", response_class=HTMLResponse)
async def form_kick(request: Request):
    return templates.TemplateResponse("cadastro_kick.html", {"request": request})


# ============================================================
# Rotas de Ações (Formulários)
# ============================================================

@app.post("/cadastro/twitch")
async def salvar_twitch(request: Request):
    try:
        form = await request.form()

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO twitch (
                data_transmissao, horas_transmitidas, visualizacoes,
                seguidores_novos, subscribers_novos, conteudo,
                valor_usd, donates_brl, minutos_assistidos, espectadores_unicos
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            form.get('data_transmissao', ''),
            form.get('horas_transmitidas', ''),
            int(form.get('visualizacoes') or 0),
            int(form.get('seguidores_novos') or 0),
            int(form.get('subscribers_novos') or 0),
            form.get('conteudo', ''),
            sanitize_currency(form.get('valor_usd', ''), 'US$'),
            sanitize_currency(form.get('donates_brl', ''), 'R$'),
            int(form.get('minutos_assistidos') or 0),
            int(form.get('espectadores_unicos') or 0)
        ))

        conn.commit()
        conn.close()
        return RedirectResponse("/", status_code=303)

    except sqlite3.OperationalError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro de Banco de Dados: {e}. Apague o arquivo 'lives.db' e reinicie a aplicação."
        )
    except (ValueError, TypeError) as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro nos dados do formulário: {e}. Verifique se os campos numéricos estão corretos."
        )


@app.post("/cadastro/youtube")
async def salvar_youtube(request: Request):
    try:
        form = await request.form()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO youtube (titulo, data, horario)
            VALUES (?, ?, ?)
        """, (form.get("titulo"), form.get("data"), form.get("horario")))

        conn.commit()
        conn.close()
        return RedirectResponse("/", status_code=303)

    except sqlite3.OperationalError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro de Banco de Dados: {e}. Apague o arquivo 'lives.db' e reinicie a aplicação."
        )


@app.post("/cadastro/kick")
async def salvar_kick(request: Request):
    try:
        form = await request.form()
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO kick (
                data_transmissao, horas_transmitidas,
                inscricoes_novas, seguidores_novos, conteudo
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            form.get('data_transmissao', ''),
            form.get('horas_transmitidas', ''),
            int(form.get('inscricoes_novas') or 0),
            int(form.get('seguidores_novos') or 0),
            form.get('conteudo', '')
        ))

        conn.commit()
        conn.close()
        return RedirectResponse("/", status_code=303)

    except sqlite3.OperationalError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro de Banco de Dados: {e}. Apague o arquivo 'lives.db' e reinicie a aplicação."
        )
    except (ValueError, TypeError) as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro nos dados do formulário: {e}. Verifique se os campos numéricos estão corretos."
        )


# ============================================================
# Rotas de Exportação CSV
# ============================================================

def export_table_to_csv(table_name: str, filename: str):
    """Função genérica para exportar qualquer tabela em CSV."""
    output = io.StringIO()
    writer = csv.writer(output)

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    if rows:
        writer.writerow(rows[0].keys())
        writer.writerows(rows)
    else:
        cursor.execute(f"PRAGMA table_info({table_name})")
        writer.writerow([info[1] for info in cursor.fetchall()])

    conn.close()
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.get("/export/twitch/csv")
async def export_twitch_csv():
    return export_table_to_csv("twitch", "dados_twitch.csv")


@app.get("/export/youtube/csv")
async def export_youtube_csv():
    return export_table_to_csv("youtube", "dados_youtube.csv")


@app.get("/export/kick/csv")
async def export_kick_csv():
    return export_table_to_csv("kick", "dados_kick.csv")
