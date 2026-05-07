import sqlite3
import pandas as pd
import random

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
                    data_servico TEXT, num_interno TEXT, tipo TEXT)''')
    conn.commit()
    conn.close()

def get_stats():
    init_db()
    conn = sqlite3.connect('gestao_operacional.db')
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
    conn = sqlite3.connect('gestao_operacional.db')
    c = conn.cursor()
    c.execute("DELETE FROM pessoal")
    postos = ["Est", "B1", "B2", "SCH", "CHF"]
    for i in range(1, 61):
        c.execute("INSERT INTO pessoal (nome, num_interno, posto, motorista, curso, disp_tipo, disp_detalhe) VALUES (?,?,?,?,?,?,?)",
                  (f"Operacional {i}", str(3000+i), random.choice(postos), "Pesado" if i%3==0 else "Ligeiro", "TAS" if i%2==0 else "Sem curso", "Fixo", "Segunda, Quinta"))
    conn.commit()
    conn.close()
