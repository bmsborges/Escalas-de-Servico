import streamlit as st
import pandas as pd
import sqlite3
import calendar
from datetime import datetime
import random

# --- CONFIGURAÇÃO DA BASE DE DADOS ---
def init_db():
    conn = sqlite3.connect('escala_servico.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pessoal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT,
                    num_interno TEXT,
                    posto TEXT,
                    motorista TEXT,
                    curso TEXT,
                    disp_tipo TEXT,
                    disp_detalhe TEXT)''')
    conn.commit()
    conn.close()

def save_to_db(nome, num, posto, motorista, curso, disp_tipo, disp_detalhe):
    conn = sqlite3.connect('escala_servico.db')
    c = conn.cursor()
    c.execute("INSERT INTO pessoal (nome, num_interno, posto, motorista, curso, disp_tipo, disp_detalhe) VALUES (?,?,?,?,?,?,?)",
              (nome, num, posto, motorista, curso, disp_tipo, disp_detalhe))
    conn.commit()
    conn.close()

def get_all_pessoal():
    conn = sqlite3.connect('escala_servico.db')
    df = pd.read_sql_query("SELECT * FROM pessoal", conn)
    conn.close()
    return df

# --- LÓGICA DE ESCALA ---
def gerar_escala_mensal(df, ano, mes):
    dias_no_mes = calendar.monthrange(ano, mes)[1]
    escala = []

    # Lista de postos que podem ser Chefe de Equipa
    chefes_possiveis = ['SCH', 'CHF', 'OFB2', 'OFB1', 'OFB Princ', 'OFB Sup', 'ADJ CMD', '2 CMD', 'CMD']

    for dia in range(1, dias_no_mes + 1):
        data = datetime(ano, mes, dia)
        # Filtro básico de disponibilidade (simplificado para o exemplo)
        disponiveis = df.to_dict('records')
        random.shuffle(disponiveis)
        
        equipa_dia = []
        
        # 1. Tenta garantir 1 Chefe
        chefe = next((p for p in disponiveis if p['posto'] in chefes_possiveis), None)
        if chefe: equipa_dia.append(chefe)
        
        # 2. Tenta garantir 1 Motorista Pesado (que não seja o chefe já escolhido)
        pesado = next((p for p in disponiveis if p['motorista'] == 'Pesado' and p not in equipa_dia), None)
        if pesado: equipa_dia.append(pesado)
        
        # 3. Tenta garantir 1 TAS
        tas = next((p for p in disponiveis if p['curso'] == 'TAS' and p not in equipa_dia), None)
        if tas: equipa_dia.append(tas)
        
        # 4. Preenche o resto até 6 elementos
        for p in disponiveis:
            if p not in equipa_dia and len(equipa_dia) < 6:
                equipa_dia.append(p)
        
        nomes_equipa = [p['nome'] for p in equipa_dia]
        # Preencher com "VAGO" se não houver pessoal suficiente
        while len(nomes_equipa) < 6:
            nomes_equipa.append("FALTA PESSOAL")
            
        escala.append([dia] + nomes_equipa)

    return pd.DataFrame(escala, columns=['Dia', 'Chefe', 'Moti. Pesado', 'TAS', 'Elem 4', 'Elem 5', 'Elem 6'])

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Gestão de Escalas 22-07", layout="wide")
init_db()

st.title("🌙 Gestor de Turnos Noturnos (22:00 - 07:00)")

menu = ["Gerir Pessoal", "Gerar Escala Mensal"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Gerir Pessoal":
    st.header("👤 Cadastro de Elementos")
    
    with st.expander("Adicionar Novo Elemento"):
        with st.form("form_pessoal"):
            col1, col2, col3 = st.columns(3)
            nome = col1.text_input("Nome Completo")
            num = col2.text_input("Nº Interno")
            posto = col3.selectbox("Posto", ["Est", "ESP", "B3", "B2", "B1", "SCH", "CHF", "OFB2", "OFB1", "OFB Princ", "OFB Sup", "ADJ CMD", "2 CMD", "CMD"])
            
            col4, col5 = st.columns(2)
            mot = col4.radio("Tipo Motorista", ["Pesado", "Ligeiro"])
            curso = col5.selectbox("Curso", ["TAS", "TAT", "TS", "Sem curso"])
            
            tipo_disp = st.selectbox("Tipo Disponibilidade", ["Fixo", "Pontual"])
            detalhe_disp = st.text_input("Detalhe (Ex: Seg,Ter ou datas 2026-05-10)")
            
            if st.form_submit_button("Guardar na Base de Dados"):
                save_to_db(nome, num, posto, mot, curso, tipo_disp, detalhe_disp)
                st.success(f"Elemento {nome} guardado com sucesso!")

    st.divider()
    st.subheader("Lista de Pessoal")
    df_lista = get_all_pessoal()
    st.dataframe(df_lista, use_container_width=True)
    
    if st.button("Limpar Base de Dados (CUIDADO)"):
        conn = sqlite3.connect('escala_servico.db')
        conn.execute("DELETE FROM pessoal")
        conn.commit()
        conn.close()
        st.rerun()

elif choice == "Gerar Escala Mensal":
    st.header("📅 Gerador de Escala")
    df_pessoal = get_all_pessoal()
    
    if df_pessoal.empty:
        st.warning("A base de dados está vazia. Adicione elementos primeiro.")
    else:
        col_m, col_a = st.columns(2)
        mes_escolhido = col_m.selectbox("Mês", range(1, 13), index=datetime.now().month - 1)
        ano_escolhido = col_a.number_input("Ano", value=2026)
        
        if st.button("Gerar Escala de 30 Dias"):
            df_escala = gerar_escala_mensal(df_pessoal, ano_escolhido, mes_escolhido)
            st.table(df_escala)
            
            # Exportar
            csv = df_escala.to_csv(index=False).encode('utf-8')
            st.download_button("Descarregar Escala (CSV)", csv, "escala_noite.csv", "text/csv")
