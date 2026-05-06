import sqlite3
import random
from datetime import datetime, timedelta

def init_db():
    conn = sqlite3.connect('gestao_operacional.db')
    c = conn.cursor()
    # Tabela de Elementos
    c.execute('''CREATE TABLE IF NOT EXISTS pessoal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT, 
                    num_interno TEXT UNIQUE, 
                    posto TEXT, 
                    motorista TEXT, 
                    curso TEXT, 
                    disp_tipo TEXT, 
                    disp_detalhe TEXT)''')
    
    # Tabela de Controlo de Presenças
    c.execute('''CREATE TABLE IF NOT EXISTS presencas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_servico TEXT, 
                    num_interno TEXT,
                    tipo TEXT)''')
    conn.commit()
    conn.close()

def seed_demo_data():
    """Gera 60 elementos com lógica aleatória mas equilibrada para escalas."""
    init_db()
    
    nomes_base = ["João", "Maria", "António", "José", "Francisco", "Manuel", "Rui", "Pedro", "Paulo", "Miguel", 
                  "Ricardo", "Nuno", "André", "Luís", "Carlos", "Tiago", "Diogo", "Marco", "Bruno", "Hugo"]
    apelidos = ["Silva", "Santos", "Ferreira", "Pereira", "Oliveira", "Costa", "Rodrigues", "Martins", "Jesus", "Sousa"]
    
    # Listas conforme os teus requisitos
    postos = ["Est", "ESP", "B3", "B2", "B1", "SCH", "CHF", "OFB2", "OFB1", "OFB Princ", "OFB Sup", "ADJ CMD", "2 CMD", "CMD"]
    cursos_lista = ["TAS", "TAT", "TS", "Sem curso"]
    dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    
    conn = sqlite3.connect('gestao_operacional.db')
    c = conn.cursor()

    # Limpar dados existentes para evitar duplicados no ID interno
    c.execute("DELETE FROM pessoal")

    for i in range(1, 61):
        nome_completo = f"{random.choice(nomes_base)} {random.choice(apelidos)} {random.choice(apelidos)}"
        num_interno = str(1000 + i) # Números de 1001 a 1060
        
        # --- LÓGICA DE DISTRIBUIÇÃO OPERACIONAL ---
        # Garantir cerca de 20% de chefias (SCH para cima)
        if i <= 12:
            posto = random.choice(["SCH", "CHF", "OFB1", "OFB2"])
        else:
            posto = random.choice(["Est", "ESP", "B3", "B2", "B1"])

        # Garantir 40% de motoristas de pesados
        motorista = "Pesado" if random.random() < 0.4 else "Ligeiro"
        
        # Garantir 50% de elementos com curso TAS
        curso = "TAS" if random.random() < 0.5 else random.choice(["TAT", "TS", "Sem curso"])

        # --- LÓGICA DE DISPONIBILIDADE ---
        tipo_disp = random.choice(["Fixo", "Pontual"])
        
        if tipo_disp == "Fixo":
            # Escolhe entre 2 a 4 dias fixos por semana
            dias_selecionados = random.sample(dias_semana, random.randint(2, 4))
            detalhe = ", ".join(dias_selecionados)
        else:
            # Gera 5 datas aleatórias para o mês de Junho de 2026
            datas_aleatorias = []
            for _ in range(5):
                dia = random.randint(1, 30)
                datas_aleatorias.append(f"2026-06-{dia:02d}")
            detalhe = ", ".join(sorted(list(set(datas_aleatorias))))

        c.execute('''INSERT INTO pessoal (nome, num_interno, posto, motorista, curso, disp_tipo, disp_detalhe) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                  (nome_completo, num_interno, posto, motorista, curso, tipo_disp, detalhe))

    conn.commit()
    conn.close()

def get_stats():
    """Retorna o DataFrame com as estatísticas de pessoal."""
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
