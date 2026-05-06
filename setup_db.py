import sqlite3
import random

def setup_completo():
    # 1. Cria/Liga ao ficheiro da base de dados
    conn = sqlite3.connect('gestao_operacional.db')
    c = conn.cursor()

    # 2. Criação das Tabelas
    print("A configurar tabelas...")
    c.execute('''CREATE TABLE IF NOT EXISTS pessoal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT, 
                    num_interno TEXT UNIQUE, 
                    posto TEXT, 
                    motorista TEXT, 
                    curso TEXT, 
                    disp_tipo TEXT, 
                    disp_detalhe TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS presencas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_servico TEXT, 
                    num_interno TEXT,
                    tipo TEXT)''') # 'Serviço' ou 'Falta'

    # 3. Geração dos 60 Elementos Demo
    print("A gerar 60 elementos...")
    
    nomes_base = ["João", "Ricardo", "Miguel", "Nuno", "André", "Luís", "Carlos", "António", "Pedro", "José"]
    apelidos = ["Silva", "Santos", "Ferreira", "Pereira", "Oliveira", "Costa", "Rodrigues", "Martins", "Sousa"]
    postos = ["Est", "ESP", "B3", "B2", "B1", "SCH", "CHF", "OFB2", "OFB1"]
    cursos = ["TAS", "TAT", "TS", "Sem curso"]
    dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

    elementos = []
    for i in range(60):
        nome = f"{random.choice(nomes_base)} {random.choice(apelidos)} {i+1}"
        num_int = str(1000 + i)
        posto = random.choice(postos)
        
        # Lógica para garantir especialidades
        motorista = "Pesado" if random.random() < 0.4 else "Ligeiro"
        curso = "TAS" if random.random() < 0.5 else random.choice(cursos)
        
        # Disponibilidade aleatória
        tipo_disp = random.choice(["Fixo", "Pontual"])
        if tipo_disp == "Fixo":
            detalhe = ", ".join(random.sample(dias, 2)) # 2 dias fixos por semana
        else:
            detalhe = f"2026-05-{random.randint(10, 28)}" # Data pontual em Maio

        elementos.append((nome, num_int, posto, motorista, curso, tipo_disp, detalhe))

    # 4. Inserir na Base de Dados
    c.executemany('''INSERT OR IGNORE INTO pessoal 
                     (nome, num_interno, posto, motorista, curso, disp_tipo, disp_detalhe) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)''', elementos)

    conn.commit()
    conn.close()
    print("Sucesso! O ficheiro 'gestao_operacional.db' foi criado com 60 elementos.")

if __name__ == "__main__":
    setup_completo()
