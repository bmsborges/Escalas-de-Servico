import streamlit as st
import pandas as pd
import sqlite3
import calendar
import random
from datetime import datetime, date

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão Operacional", layout="wide", page_icon="🔘")

# --- ESTILO CSS (GILL SANS & TONS DE CINZA) ---
st.markdown("""
    <style>
    /* Importação de Fonte e Estilo Global */
    @import url('https://fonts.cdnfonts.com/css/gill-sans-mt');
    
    html, body, [class*="css"] {
        font-family: 'Gill Sans MT', 'Gill Sans', sans-serif !important;
        background-color: #F9FAFB;
        color: #374151;
    }

    /* Menu Superior Minimalista */
    .stButton > button {
        border: none;
        background-color: transparent;
        color: #6B7280;
        font-weight: 400;
        border-bottom: 2px solid transparent;
        border-radius: 0px;
        transition: 0.3s;
    }
    .stButton > button:hover {
        color: #111827;
        border-bottom: 2px solid #9CA3AF;
    }
    
    /* Input Fields e Tabelas */
    .stTextInput, .stSelectbox, .stDateInput {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB !important;
    }
    
    /* Remover Sidebar padrão */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Estilo de Cartões Cinza */
    .gray-card {
        background-color: #F3F4F6;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE BASE DE DADOS ---
def init_db():
    conn = sqlite3.connect('operacional.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pessoal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT, num_interno TEXT, posto TEXT, 
                    motorista TEXT, curso TEXT, 
                    disp_tipo TEXT, disp_detalhe TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS arquivo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mes_ano TEXT, dados_csv TEXT, data_geracao TEXT)''')
    conn.commit()
    conn.close()

def seed_60_elementos():
    primeiros = ["João", "Maria", "Rui", "Ana", "Carlos", "Luís", "Nuno", "André"]
    apelidos = ["Silva", "Santos", "Costa", "Pereira", "Martins", "Oliveira"]
    postos = ["Est", "ESP", "B3", "B2", "B1", "SCH", "CHF", "OFB2", "OFB1"]
    
    conn = sqlite3.connect('operacional.db')
    for i in range(60):
        nome = f"{random.choice(primeiros)} {random.choice(apelidos)}"
        num = str(3000 + i)
        pst = random.choice(postos)
        mot = "Pesado" if random.random() < 0.4 else "Ligeiro"
        crs = "TAS" if random.random() < 0.5 else "TAT"
        conn.execute("INSERT INTO pessoal (nome, num_interno, posto, motorista, curso, disp_tipo, disp_detalhe) VALUES (?,?,?,?,?,?,?)",
                     (nome, num, pst, mot, crs, "Fixo", "Segunda, Quarta, Sexta"))
    conn.commit()
    conn.close()

# --- LÓGICA DE NAVEGAÇÃO ---
if 'menu' not in st.session_state:
    st.session_state.menu = 'Home'
if 'submenu' not in st.session_state:
    st.session_state.submenu = None

# --- CABEÇALHO / MENU SUPERIOR ---
init_db()
st.title("SISTEMA OPERACIONAL")

# Linha do Menu Principal
col1, col2, col3, col4, col5 = st.columns(5)
if col1.button("ELEMENTOS"): st.session_state.menu = 'Elementos'
if col2.button("ESCALAS"): st.session_state.menu = 'Escalas'
if col3.button("ARQUIVO"): st.session_state.menu = 'Arquivo'
if col4.button("CONFIGURAÇÃO"): st.session_state.menu = 'Configuração'
if col5.button("HOME"): st.session_state.menu = 'Home'

st.markdown("---")

# --- CONTEÚDO ---

# MENU: ELEMENTOS
if st.session_state.menu == 'Elementos':
    sub1, sub2, _ = st.columns([1,1,4])
    if sub1.button("NOVO"): st.session_state.submenu = 'Novo'
    if sub2.button("EDITAR"): st.session_state.submenu = 'Editar'
    
    if st.session_state.submenu == 'Novo':
        with st.container():
            st.subheader("Registo de Elemento")
            with st.form("add"):
                c1, c2, c3 = st.columns(3)
                n = c1.text_input("Nome")
                num = c2.text_input("Nº Interno")
                p = c3.selectbox("Posto", ["Est", "ESP", "B3", "B2", "B1", "SCH", "CHF"])
                sub_btn = st.form_submit_button("GUARDAR")
                if sub_btn: st.success("Elemento adicionado.")
                
    elif st.session_state.submenu == 'Editar':
        conn = sqlite3.connect('operacional.db')
        df = pd.read_sql_query("SELECT * FROM pessoal", conn)
        st.data_editor(df, use_container_width=True)

# MENU: ESCALAS
elif st.session_state.menu == 'Escalas':
    sub1, sub2, _ = st.columns([1,1,4])
    if sub1.button("GERAR"): st.session_state.submenu = 'Gerar'
    if sub2.button("CONSULTAR"): st.session_state.submenu = 'Consultar'
    
    if st.session_state.submenu == 'Gerar':
        st.subheader("Parâmetros de Geração")
        mes = st.selectbox("Mês", range(1,13), index=4)
        if st.button("EXECUTAR ALGORITMO"):
            st.info("A processar escala para 22:00 - 07:00...")
            # Lógica de escala aqui...

# MENU: CONFIGURAÇÃO
elif st.session_state.menu == 'Configuração':
    tab1, tab2, tab3 = st.tabs(["Campos", "Equipas", "Gráfico"])
    
    with tab1:
        st.write("Gestão de Postos e Cursos.")
        if st.button("Povoar com 60 Elementos (Demo)"):
            seed_60_elementos()
            st.success("Dados gerados.")
            
    with tab2:
        st.write("Configuração de Mínimos Operacionais.")
        st.number_input("Mínimo TAS", value=1)
        st.number_input("Mínimo Pesados", value=1)

    with tab3:
        st.write("Definições de UI.")
        st.color_picker("Cor Principal", "#6B7280")

# HOME / DASHBOARD
else:
    st.markdown("""
        <div class="gray-card">
            <h3>Bem-vindo ao Command Center</h3>
            <p>Selecione uma opção no menu superior para começar.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Métricas Minimalistas
    m1, m2, m3 = st.columns(3)
    m1.metric("Efetivo Total", "60", "Prontos")
    m2.metric("Turno Hoje", "6", "Elementos")
    m3.metric("Viaturas", "2", "Ativas")
