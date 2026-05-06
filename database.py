import sqlite3
import pandas as pd
import random

DB_NAME = 'gestao_operacional.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pessoal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT, num_interno TEXT UNIQUE, posto TEXT, 
                    motorista TEXT, curso TEXT, 
                    disp_tipo TEXT, disp_detalhe TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS presencas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_servico TEXT, num_interno TEXT, tipo TEXT)''')
    conn.commit()
    conn.close()

def get_stats():
    init_db()
    conn = sqlite3.connect(DB_NAME)
    query = """
    SELECT p.num_interno, p.nome, p.posto, p.motorista, p.curso, p.disp_tipo, p.disp_detalhe,
    (SELECT COUNT(*) FROM presencas WHERE num_interno = p.num_interno AND tipo = 'Serviço') as servicos,
    (SELECT COUNT(*) FROM presencas WHERE num_interno = p.num_interno AND tipo = 'Falta') as faltas
    FROM pessoal p
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def seed_demo_data():
    init_db()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM pessoal")
    c.execute("DELETE FROM presencas")
    
    postos = ["Est", "ESP", "B1", "B2", "B3", "SCH", "CHF", "OFB1"]
    nomes = ["João", "Maria", "António", "José", "Carlos", "Rui", "Ana", "Luís", "Nuno", "André"]
    apelidos = ["Silva", "Santos", "Costa", "Oliveira", "Pereira"]

    for i in range(1, 61):
        n = f"{random.choice(nomes)} {random.choice(apelidos)} {i}"
        ni = str(2000 + i)
        pst = random.choice(postos)
        mot = "Pesado" if random.random() < 0.4 else "Ligeiro"
        crs = "TAS" if random.random() < 0.5 else "Sem curso"
        
        c.execute("INSERT INTO pessoal (nome, num_interno, posto, motorista, curso, disp_tipo, disp_detalhe) VALUES (?,?,?,?,?,?,?)",
                  (n, ni, pst, mot, crs, "Fixo", "Segunda, Quarta, Sexta"))
    conn.commit()
    conn.close()
