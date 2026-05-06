import streamlit as st
import pandas as pd
import sqlite3
import calendar
import random
from datetime import datetime, date

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão de Escalas 22-07", layout="wide", page_icon="🛡️")

# --- CONSTANTES E REGRAS ---
POSTOS = ["Est", "ESP", "B3", "B2", "B1", "SCH", "CHF", "OFB2", "OFB1", "OFB Princ", "OFB Sup", "ADJ CMD", "2 CMD", "CMD"]
CHEFES_LISTA = ["SCH", "CHF", "OFB2", "OFB1", "OFB Princ", "OFB Sup", "ADJ CMD", "2 CMD", "CMD"]
CURSOS = ["TAS", "TAT", "TS", "Sem curso"]
DIAS_SEMANA = {"Segunda": 0, "Terça": 1, "Quarta": 2, "Quinta": 3, "Sexta": 4, "Sábado": 5, "Domingo": 6}

# --- BASE DE DADOS ---
def init_db():
    conn = sqlite3.connect('gestao_escalas.db')
    c = conn.cursor()
    # Tabela de Elementos
    c.execute('''CREATE TABLE IF NOT EXISTS pessoal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT, num_interno TEXT, posto TEXT, 
                    motorista TEXT, curso TEXT, 
                    disp_tipo TEXT, disp_detalhe TEXT)''')
    # Tabela de Arquivo de Escalas
    c.execute('''CREATE TABLE IF NOT EXISTS arquivo_escalas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mes_ano TEXT, dados_csv TEXT, data_geracao TEXT)''')
    conn.commit()
    conn.close()

# --- FUNÇÕES DE LÓGICA ---
def get_pessoal():
    conn = sqlite3.connect('gestao_escalas.db')
    df = pd.read_sql_query("SELECT * FROM pessoal", conn)
    conn.close()
    return df

def gerar_escala_logica(df, mes, ano):
    num_dias = calendar.monthrange(ano, mes)[1]
    escala_mensal = []
    
    for dia in range(1, num_dias + 1):
        data_atual = date(ano, mes, dia)
        dia_semana_num = data_atual.weekday()
        
        # Filtrar disponíveis para o dia
        disponiveis = []
        for _, p in df.iterrows():
            is_disp = False
            if p['disp_tipo'] == "Fixo":
                dias_escolhidos = p['disp_detalhe'].split(", ")
                if any(DIAS_SEMANA[d] == dia_semana_num for d in dias_escolhidos):
                    is_disp = True
            elif p['disp_tipo'] == "Pontual":
                if str(data_atual) in p['disp_detalhe']:
                    is_disp = True
            
            if is_disp:
                disponiveis.append(p.to_dict())
        
        random.shuffle(disponiveis)
        equipa = []
        
        # 1. Chefe de Equipa
        chefe = next((p for p in disponiveis if p['posto'] in CHEFES_LISTA), None)
        if chefe: equipa.append(chefe)
        
        # 2. Motorista Pesado
        pesado = next((p for p in disponiveis if p['motorista'] == "Pesado" and p not in equipa), None)
        if pesado: equipa.append(pesado)
        
        # 3. TAS
        tas = next((p for p in disponiveis if p['curso'] == "TAS" and p not in equipa), None)
        if tas: equipa.append(tas)
        
        # 4. Restantes elementos até completar 6
        for p in disponiveis:
            if p not in equipa and len(equipa) < 6:
                equipa.append(p)
        
        # Formatação da linha
        nomes_equipa = [e['nome'] for e in equipa]
        while len(nomes_equipa) < 6: nomes_equipa.append("⚠️ VAGO")
        
        escala_mensal.append([f"{dia}/{mes}/{ano}"] + nomes_equipa)
    
    return pd.DataFrame(escala_mensal, columns=["Data", "Chefe", "Mot. Pesado", "TAS", "Elem 4", "Elem 5", "Elem 6"])

# --- INTERFACE (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    [data-testid="stSidebar"] { background-color: #111827; }
    .stButton>button { border-radius: 5px; height: 3em; background-color: #2563eb; color: white; border: none; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; border: 1px solid #e5e7eb; }
    </style>
    """, unsafe_allow_html=True)

# --- MENU LATERAL ---
init_db()
with st.sidebar:
    st.title("🛡️ Operacional")
    st.markdown("---")
    
    # Estrutura solicitada
    st.subheader("👤 Elementos")
    menu_elementos = st.radio("Ação:", ["Novo", "Editar"], label_visibility="collapsed")
    
    st.subheader("📅 Escalas")
    menu_escalas = st.radio("Ação:", ["Gerar", "Consultar"], label_visibility="collapsed")
    
    st.subheader("📁 Histórico")
    menu_arquivo = st.checkbox("Ver Arquivo")
    
    st.subheader("⚙️ Configuração")
    menu_config = st.selectbox("Opção:", ["Campos Elementos", "Constituição das Equipas", "Aspecto Gráfico"])

# --- LÓGICA DE PÁGINAS ---

# 1. ELEMENTOS: NOVO
if not menu_arquivo and menu_elementos == "Novo" and not "Gerar" in menu_escalas:
    st.title("➕ Novo Elemento")
    with st.form("form_novo"):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome Completo")
        num = col2.text_input("Número Interno")
        
        col3, col4, col5 = st.columns(3)
        posto = col3.selectbox("Posto", POSTOS)
        mot = col4.radio("Motorista", ["Pesado", "Ligeiro"])
        curso = col5.selectbox("Curso", CURSOS)
        
        st.markdown("---")
        st.write("📅 **Disponibilidade**")
        tipo_disp = st.radio("Tipo", ["Fixo", "Pontual"], horizontal=True)
        
        if tipo_disp == "Fixo":
            detalhe = st.multiselect("Dias da Semana:", list(DIAS_SEMANA.keys()))
            detalhe_str = ", ".join(detalhe)
        else:
            detalhe_str = st.text_area("Datas (Formato: YYYY-MM-DD, separadas por vírgula)")
            
        if st.form_submit_button("Guardar Elemento"):
            conn = sqlite3.connect('gestao_escalas.db')
            conn.execute("INSERT INTO pessoal (nome, num_interno, posto, motorista, curso, disp_tipo, disp_detalhe) VALUES (?,?,?,?,?,?,?)",
                         (nome, num, posto, mot, curso, tipo_disp, detalhe_str))
            conn.commit()
            conn.close()
            st.success("Elemento registado!")

# 2. ELEMENTOS: EDITAR
elif not menu_arquivo and menu_elementos == "Editar":
    st.title("📝 Editar Efetivos")
    df = get_pessoal()
    st.data_editor(df, use_container_width=True, num_rows="dynamic")
    st.info("Pode editar diretamente na tabela acima.")
