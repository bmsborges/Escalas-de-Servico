import pandas as pd
import sqlite3
import io
import calendar
import random
from datetime import date

def gerar_escala_mensal(mes, ano):
    """Gera a escala mensal com 6 elementos e formatação detalhada por célula."""
    conn = sqlite3.connect('gestao_operacional.db')
    df = pd.read_sql_query("SELECT * FROM pessoal", conn)
    conn.close()

    if len(df) < 6:
        return None, "Erro: Necessitas de pelo menos 6 elementos na base de dados."

    num_dias = calendar.monthrange(ano, mes)[1]
    # Lista de postos que podem ser chefes de equipa
    chefes_lista = ["SCH", "CHF", "OFB2", "OFB1", "OFB Princ", "OFB Sup", "ADJ CMD", "2 CMD", "CMD"]
    dias_semana_pt = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    
    escala_final = []

    for dia in range(1, num_dias + 1):
        data_atual = date(ano, mes, dia)
        dia_semana_nome = dias_semana_pt[data_atual.weekday()]
        
        # 1. Filtrar disponíveis (Fixo ou Pontual)
        disponiveis = []
        for _, p in df.iterrows():
            if p['disp_tipo'] == "Fixo":
                if dia_semana_nome in str(p['disp_detalhe']):
                    disponiveis.append(p.to_dict())
            elif p['disp_tipo'] == "Pontual":
                if str(data_atual) in str(p['disp_detalhe']):
                    disponiveis.append(p.to_dict())

        random.shuffle(disponiveis)
        equipa = []

        # 2. Seleção por Requisitos
        # A. Chefe
        chefe = next((p for p in disponiveis if p['posto'] in chefes_lista), None)
        if chefe: equipa.append(chefe)
        
        # B. Motorista Pesados
        pesado = next((p for p in disponiveis if p['motorista'] == "Pesado" and p not in equipa), None)
        if pesado: equipa.append(pesado)
        
        # C. TAS
        tas = next((p for p in disponiveis if p['curso'] == "TAS" and p not in equipa), None)
        if tas: equipa.append(tas)

        # D. Restantes (até 6)
        for p in disponiveis:
            if p not in equipa and len(equipa) < 6:
                equipa.append(p)

        # 3. Formatação Detalhada da Célula (Nome, ID, Motorista, Curso)
        celulas_formatadas = []
        for e in equipa:
            info = (
                f"**{e['nome']}**\n"
                f"ID: {e['num_interno']}\n"
                f"Mot: {e['motorista']}\n"
                f"Curso: {e['curso']}"
            )
            celulas_formatadas.append(info)

        while len(celulas_formatadas) < 6:
            celulas_formatadas.append("⚠️\n**FALTA PESSOAL**\n---\n---")
        
        escala_final.append([f"{dia:02d}/{mes:02d}"] + celulas_formatadas)

    colunas = ["Dia", "Chefe de Equipa", "Mot. Pesado", "TAS", "Elemento 4", "Elemento 5", "Elemento 6"]
    return pd.DataFrame(escala_final, columns=colunas), "Sucesso"

def export_to_excel():
    """Exporta as estatísticas de serviços e faltas para Excel."""
    from database import get_stats
    df = get_stats()
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Estatísticas')
    return output.getvalue()

def import_from_excel(uploaded_file):
    """Importa elementos de um ficheiro Excel para a base de dados."""
    try:
        df = pd.read_excel(uploaded_file)
        conn = sqlite3.connect('gestao_operacional.db')
        df.to_sql('pessoal', conn, if_exists='append', index=False)
        conn.close()
        return True, f"Sucesso: {len(df)} elementos importados."
    except Exception as e:
        return False, f"Erro na importação: {e}"
