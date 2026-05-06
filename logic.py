import pandas as pd
import sqlite3
import io
import calendar
import random
from datetime import date

def gerar_escala_mensal(mes, ano):
    conn = sqlite3.connect('gestao_operacional.db')
    df = pd.read_sql_query("SELECT * FROM pessoal", conn)
    conn.close()

    if len(df) < 6:
        return None, "Erro: Necessitas de pelo menos 6 elementos na base de dados."

    num_dias = calendar.monthrange(ano, mes)[1]
    chefes_lista = ["SCH", "CHF", "OFB2", "OFB1", "OFB Princ", "OFB Sup", "ADJ CMD", "2 CMD", "CMD"]
    dias_semana_pt = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    
    escala_final = []

    for dia in range(1, num_dias + 1):
        data_atual = date(ano, mes, dia)
        dia_semana_nome = dias_semana_pt[data_atual.weekday()]
        
        # 1. Filtrar quem está disponível hoje
        disponiveis = []
        for _, p in df.iterrows():
            if p['disp_tipo'] == "Fixo":
                if dia_semana_nome in p['disp_detalhe']:
                    disponiveis.append(p.to_dict())
            elif p['disp_tipo'] == "Pontual":
                if str(data_atual) in p['disp_detalhe']:
                    disponiveis.append(p.to_dict())

        random.shuffle(disponiveis) # Para rotatividade justa
        equipa = []

        # 2. Tentar preencher requisitos mínimos
        # Chefe
        chefe = next((p for p in disponiveis if p['posto'] in chefes_lista), None)
        if chefe: equipa.append(chefe)
        
        # Motorista Pesados
        pesado = next((p for p in disponiveis if p['motorista'] == "Pesado" and p not in equipa), None)
        if pesado: equipa.append(pesado)
        
        # TAS
        tas = next((p for p in disponiveis if p['curso'] == "TAS" and p not in equipa), None)
        if tas: equipa.append(tas)

        # 3. Completar até 6 elementos
        for p in disponiveis:
            if p not in equipa and len(equipa) < 6:
                equipa.append(p)

        # Formatar nomes para a tabela
        nomes = [e['nome'] for e in equipa]
        while len(nomes) < 6: nomes.append("⚠️ FALTA PESSOAL")
        
        escala_final.append([f"{dia:02d}/{mes:02d}", nomes[0], nomes[1], nomes[2], nomes[3], nomes[4], nomes[5]])

    colunas = ["Dia", "Chefe", "Pesado", "TAS", "Elem 4", "Elem 5", "Elem 6"]
    return pd.DataFrame(escala_final, columns=colunas), "Sucesso"

# Manter as outras funções (export_to_excel, etc) abaixo...
