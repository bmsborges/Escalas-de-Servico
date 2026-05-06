import streamlit as st
from datetime import datetime
import sqlite3

# Importação dos módulos locais
from styles import apply_styles
from database import init_db, seed_demo_data, get_stats
from logic import gerar_escala_mensal, export_to_excel, import_from_excel

# 1. Configuração Inicial
st.set_page_config(
    page_title="Command Center - Gestão de Escalas",
    layout="wide",
    page_icon="🛡️"
)

# 2. Inicializar Base de Dados e Estilos
init_db()
apply_styles()

# 3. Cabeçalho Minimalista
st.markdown("<h1 style='text-align: center; color: #1F2937;'>SISTEMA OPERACIONAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #6B7280; font-size: 0.9rem;'>TURNO NOTURNO: 22:00 — 07:00</p>", unsafe_allow_html=True)

# 4. Menu Superior Estilo Dropdown
# Criamos uma lista limpa para o utilizador escolher a secção
opcoes_menu = [
    "🏠 Início (Dashboard)",
    "👤 Elementos: Novo / Editar",
    "🗓️ Escalas: Gerar / Consultar",
    "🔄 Registo de Presenças & Trocas",
    "📥 Arquivo & Importação / Exportação",
    "⚙️ Configurações do Sistema"
]

selected_page = st.selectbox("NAVEGAÇÃO", opcoes_menu, label_visibility="collapsed")

# Espaçamento para o conteúdo
st.markdown('<div class="main-card">', unsafe_allow_html=True)

# --- LÓGICA DE NAVEGAÇÃO ---

# A. HOME / DASHBOARD
if "Início" in selected_page:
    st.subheader("Painel de Controlo")
    df_stats = get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Efetivos", len(df_stats))
    with col2:
        st.metric("Serviços (Mês)", df_stats['servicos'].sum())
    with col3:
        st.metric("Faltas Registadas", df_stats['faltas'].sum())
    with col4:
        taxa = 100 - (df_stats['faltas'].sum() / max(1, df_stats['servicos'].sum()) * 100)
        st.metric("Assiduidade", f"{min(100, taxa):.1f}%")
    
    st.divider()
    st.markdown("### 💡 Instruções")
    st.info("Para começar, verifique se tem elementos registados. Utilize o menu superior para gerar escalas mensais ou registar trocas de serviço.")

# B. ELEMENTOS: NOVO / EDITAR
elif "Elementos" in selected_page:
    st.subheader("Gestão de Efetivos")
    
    aba_lista, aba_novo = st.tabs(["📋 Lista e Edição", "➕ Novo Cadastro"])
    
    with aba_lista:
        df_pessoal = get_stats() # Traz também as estatísticas
        st.write("Edite os dados diretamente na tabela abaixo:")
        # O data_editor permite editar nomes, postos, etc. diretamente
        st.data_editor(df_pessoal, use_container_width=True, hide_index=True)
        
    with aba_novo:
        with st.form("novo_elemento"):
            c1, c2 = st.columns(2)
            nome = c1.text_input("Nome Completo")
            num = c2.text_input("Nº Interno")
            
            c3, c4, c5 = st.columns(3)
            posto = c3.selectbox("Posto", ["Est", "ESP", "B1", "B2", "B3", "SCH", "CHF", "OFB1", "OFB2", "CMD"])
            mot = c4.radio("Tipo Motorista", ["Pesado", "Ligeiro"])
            curso = c5.selectbox("Curso", ["TAS", "TAT", "TS", "Sem curso"])
            
            tipo_disp = st.radio("Disponibilidade", ["Fixo", "Pontual"], horizontal=True)
            detalhe = st.text_input("Detalhe (Ex: Segunda, Terça ou data YYYY-MM-DD)")
            
            if st.form_submit_button("GUARDAR REGISTO"):
                if nome and num:
                    conn = sqlite3.connect('gestao_operacional.db')
                    try:
                        conn.execute("INSERT INTO pessoal (nome, num_interno, posto, motorista, curso, disp_tipo, disp_detalhe) VALUES (?,?,?,?,?,?,?)",
