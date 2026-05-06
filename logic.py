import pandas as pd
import sqlite3
import calendar
import random
import io
from datetime import date

def gerar_escala_mensal(mes, ano):
    conn = sqlite3.connect('gestao_operacional.db')
    df = pd.read_sql_query("SELECT * FROM pessoal", conn)
    conn.close()

    if len(df) < 6:
        return None, "Erro: Necessários pelo menos 6 elementos."

    num_dias = calendar.monthrange(ano, mes)[1]
    chefes_lista = ["SCH", "CHF", "OFB2", "OFB1", "OFB Princ", "OFB Sup", "ADJ CMD", "2 CMD", "CMD"]
    dias_semana_pt = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    
    escala_dados = []

    for dia in range(1, num_dias + 1):
        data_atual = date(ano, mes, dia)
        dia_nome = dias_semana_pt[data_atual.weekday()]
        
        disponiveis = []
        for _, p in df.iterrows():
            if p['disp_tipo'] == "Fixo" and dia_nome in str(p['disp_detalhe']):
                disponiveis.append(p.to_dict())
            elif p['disp_tipo'] == "Pontual" and str(data_atual) in str(p['disp_detalhe']):
                disponiveis.append(p.to_dict())

        random.shuffle(disponiveis)
        equipa = []

        # Requisitos: Chefe, Pesado, TAS
        c = next((p for p in disponiveis if p['posto'] in chefes_lista), None)
        if c: equipa.append(c)
        
        m = next((p for p in disponiveis if p['motorista'] == "Pesado" and p not in equipa), None)
        if m: equipa.append(m)
        
        t = next((p for p in disponiveis if p['curso'] == "TAS" and p not in equipa), None)
        if t: equipa.append(t)

        for p in disponiveis:
            if p not in equipa and len(equipa) < 6:
                equipa.append(p)

        # Formatação Célula: Nome, ID, Mot, Curso
        celulas = []
        for e in equipa:
            celulas.append(f"**{e['nome']}**\nID: {e['num_interno']}\n{e['motorista']}\n{e['curso']}")
        
        while len(celulas) < 6: celulas.append("⚠️\nFALTA\nPESSOAL")
        escala_dados.append([f"{dia:02d}/{mes:02d}"] + celulas)

    return pd.DataFrame(escala_dados, columns=["Dia", "Chefe", "Pesado", "TAS", "E4", "E5", "E6"]), "OK"

def export_to_excel():
    from database import get_stats
    df = get_stats()
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()
