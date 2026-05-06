import sqlite3
import pandas as pd
import random
from datetime import datetime

def init_db():
    conn = sqlite3.connect('gestao_operacional.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pessoal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT, num_interno TEXT UNIQUE, posto TEXT, 
                    motorista TEXT, curso TEXT, 
                    disp_tipo TEXT, disp_detalhe TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS presencas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_servico TEXT, num_interno TEXT,
                    tipo TEXT)''') # Tipo: 'Serviço' ou 'Falta'
    conn.commit()
    conn.close()

def seed_demo_data():
    init_db()
    nomes = ["António", "Maria", "José", "Carlos", "Rui", "Ana", "Paulo", "Luís"]
    apelidos = ["Silva", "Santos", "Costa", "Oliveira", "Pereira", "Martins"]
    postos = ["B1", "B2", "SCH", "CHF"]
    
    conn = sqlite3.connect('gestao_operacional.db')
    for i in range(60):
        n = f"{random.choice(nomes)} {random.choice(apelidos)} {i}"
        ni = str(4000 + i)
        conn.execute("INSERT OR IGNORE INTO pessoal VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)",
                     (n, ni, random.choice(postos), "Pesado", "TAS", "Fixo", "Segunda"))
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect('gestao_operacional.db')
    # Join entre pessoal e contagem de presenças/faltas
    query = """
    SELECT p.num_interno, p.nome, p.posto,
    (SELECT COUNT(*) FROM presencas WHERE num_interno = p.num_interno AND tipo = 'Serviço') as servicos,
    (SELECT COUNT(*) FROM presencas WHERE num_interno = p.num_interno AND tipo = 'Falta') as faltas
    FROM pessoal p
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
