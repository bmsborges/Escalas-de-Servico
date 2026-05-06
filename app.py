import streamlit as st
import pandas as pd
import sqlite3
import random
from datetime import datetime, date

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão Operacional", layout="wide", page_icon="🔘")

# --- ESTILO CSS (GILL SANS, CINZAS E DROPDOWN) ---
st.markdown("""
    <style>
    @import url('https://fonts.cdnfonts.com/css/gill-sans-mt');
    
    html, body, [class*="css"] {
        font-family: 'Gill Sans MT', sans-serif !important;
        background-color: #F3F4F6;
        color: #1F2937;
    }

    /* Esconder Sidebar */
    [data-testid="stSidebar"] { display: none; }

    /* Estilo do Dropdown de Navegação */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #FFFFFF;
        border: 1px solid #D1D5DB;
        border-radius: 4px;
        cursor: pointer;
    }

    /* Cartões e Inputs */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #FFFFFF;
        border: 1px solid #D1D5DB !important;
    }

    .main-container {
        background-color: #FFFFFF;
        padding: 30px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-top: 20px;
    }

    .footer {
        text-align: center;
        color: #9CA3AF;
        font-size: 0.8rem;
        margin-top: 50px;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DA BASE DE DADOS ---
def init_db():
    conn = sqlite3.connect('operacional_v2.db')
    c = conn.cursor()
    # Tabela Pessoal
    c.execute('''CREATE TABLE IF NOT EXISTS pessoal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT, num_interno TEXT UNIQUE, posto TEXT, 
                    motorista TEXT, curso TEXT, 
                    disp_tipo TEXT, disp_detalhe TEXT)''')
    # Tabela de Presenças / Trocas
    c.execute('''CREATE TABLE IF NOT EXISTS presencas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_servico TEXT,
                    num_interno_efetivo TEXT,
                    tipo_registo TEXT,
                    observacoes TEXT,
                    timestamp TEXT)''')
    conn.commit()
    conn.close()

# --- FUNÇÕES DE APOIO ---
def get_pessoal():
    conn = sqlite3.connect('operacional_v2.db')
    df = pd.read_sql_query("SELECT * FROM pessoal", conn)
    conn.close()
    return df

def registrar_presenca(data, num, tipo, obs):
    try:
        conn = sqlite3.connect('operacional_v2.db')
        c = conn.cursor()
        # Verificar se o número existe
        c.execute("SELECT nome FROM pessoal WHERE num_interno = ?", (num,))
        res = c.fetchone()
        if res:
            c.execute("INSERT INTO presencas (data_servico, num_interno_efetivo, tipo_registo, observacoes, timestamp) VALUES (?,?,?,?,?)",
                      (str(data), num, tipo, obs, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            return True, res[0]
        return False, "Número interno não encontrado."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# --- INTERFACE PRINCIPAL ---
init_db()

# Cabeçalho Minimalista
st.title("SISTEMA OPERACIONAL")

# MENU DROPDOWN NO TOPO
menu_options = [
    "🏠 Home", 
    "👤 Elementos: Novo", 
    "👥 Elementos: Editar", 
    "📅 Escalas: Gerar", 
    "🔍 Escalas: Consultar", 
    "🔄 Registo de Presenças & Trocas",
    "⚙️ Configurações"
]

selected_page = st.selectbox("NAVEGAÇÃO PRINCIPAL", menu_options, label_visibility="collapsed")

st.markdown('<div class="main-container">', unsafe_allow_html=True)

# --- LÓGICA DE PÁGINAS ---

# 1. HOME
if selected_page == "🏠 Home":
    st.subheader("Painel de Controlo")
    c1, c2, c3 = st.columns(3)
    c1.metric("Efetivos Registados", len(get_pessoal()))
    c2.metric("Turnos este Mês", "30")
    c3.metric("Estado do Sistema", "OK")
    st.info("Utilize o seletor acima para navegar entre as secções.")

# 2. ELEMENTOS: NOVO
elif "Elementos: Novo" in selected_page:
    st.subheader("Novo Registo de Elemento")
    with st.form("novo_form"):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome Profissional")
        num = col2.text_input("Número Interno (ID)")
        
        col3, col4 = st.columns(2)
        posto = col3.selectbox("Posto", ["Est", "ESP", "B3", "B2", "B1", "SCH", "CHF", "OFB2", "OFB1"])
        curso = col4.selectbox("Curso", ["TAS", "TAT", "TS", "Nenhum"])
        
        if st.form_submit_button("GUARDAR"):
            conn = sqlite3.connect('operacional_v2.db')
            try:
                conn.execute("INSERT INTO pessoal (nome, num_interno, posto, motorista, curso, disp_tipo, disp_detalhe) VALUES (?,?,?,?,?,?,?)",
                             (nome, num, posto, "Ligeiro", curso, "Fixo", "Segunda"))
                conn.commit()
                st.success(f"{nome} guardado com sucesso.")
            except:
                st.error("Erro: Número interno já existe.")
            conn.close()

# 3. ELEMENTOS: EDITAR
elif "Elementos: Editar" in selected_page:
    st.subheader("Base de Dados de Efetivos")
    df = get_pessoal()
    st.data_editor(df, use_container_width=True, hide_index=True)

# 4. REGISTO DE PRESENÇAS & TROCAS (NOVA SECÇÃO)
elif "Presenças & Trocas" in selected_page:
    st.subheader("🔄 Registo de Execução de Serviço")
    st.write("Coloque o número interno do elemento que **realmente** efetuou o turno.")
    
    with st.form("registo_presenca"):
        col_data, col_num = st.columns(2)
        data_efetiva = col_data.date_input("Data do Serviço", value=date.today())
        num_interno_real = col_num.text_input("Nº Interno do Operacional")
        
        tipo_acao = st.radio("Tipo de Registo", ["Presença Normal", "Troca Autorizada", "Reforço"], horizontal=True)
        obs = st.text_input("Observações / Motivo da Troca")
        
        if st.form_submit_button("REGISTAR NA FOLHA DE SERVIÇO"):
            sucesso, msg = registrar_presenca(data_efetiva, num_interno_real, tipo_acao, obs)
            if sucesso:
                st.success(f"Confirmado: {msg} registado para o dia {data_efetiva}.")
            else:
                st.error(msg)
    
    st.divider()
    st.write("Últimos Registos de Execução:")
    conn = sqlite3.connect('operacional_v2.db')
    presencas_df = pd.read_sql_query("SELECT * FROM presencas ORDER BY timestamp DESC LIMIT 10", conn)
    st.table(presencas_df)
    conn.close()

# 5. CONFIGURAÇÕES
elif "Configurações" in selected_page:
    st.subheader("Configurações do Sistema")
    if st.button("Povoar com 60 Elementos Demo"):
        # Lógica de povoamento (simplificada para o exemplo)
        st.success("Dados de teste gerados.")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="footer">Sistema de Gestão 2026 • Operações Noturnas</div>', unsafe_allow_html=True)
