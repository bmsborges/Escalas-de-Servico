import pandas as pd
import sqlite3
import calendar
import random
from datetime import date

def gerar_escala_mensal(mes, ano):
    conn = sqlite3.connect('gestao_operacional.db')
    df = pd.read_sql_query("SELECT * FROM pessoal", conn)
    conn.close()

    num_dias = calendar.monthrange(ano, mes)[1]
    chefes = ["SCH", "CHF", "OFB1", "OFB2", "CMD"]
    escala_dados = []

    for dia in range(1, num_dias + 1):
        data_atual = date(ano, mes, dia)
        dia_nome = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"][data_atual.weekday()]
        
        disponiveis = []
        for _, p in df.iterrows():
            if p['disp_tipo'] == "Fixo" and dia_nome in str(p['disp_detalhe']):
                disponiveis.append(p.to_dict())
            elif p['disp_tipo'] == "Pontual" and str(data_atual) in str(p['disp_detalhe']):
                disponiveis.append(p.to_dict())

        random.shuffle(disponiveis)
        equipa = []
        
        # Seleção lógica: Chefe, Motorista Pesado, TAS
        c = next((p for p in disponiveis if p['posto'] in chefes), None)
        if c: equipa.append(c)
        m = next((p for p in disponiveis if p['motorista'] == "Pesado" and p not in equipa), None)
        if m: equipa.append(m)
        t = next((p for p in disponiveis if p['curso'] == "TAS" and p not in equipa), None)
        if t: equipa.append(t)

        for p in disponiveis:
            if p not in equipa and len(equipa) < 6: equipa.append(p)

        # Formatação das células
        celulas = [f"**{e['nome']}**\nID: {e['num_interno']}\n{e['motorista']}\n{e['curso']}" for e in equipa]
        while len(celulas) < 6: celulas.append("⚠️\nFALTA\nPESSOAL")
        escala_dados.append([f"{dia:02d}/{mes:02d}"] + celulas)

    return pd.DataFrame(escala_dados, columns=["Dia", "Chefe", "Pesado", "TAS", "E4", "E5", "E6"]), "OK"
