import streamlit as st
from datetime import datetime, date
import sqlite3
from styles import apply_styles
from database import init_db, seed_demo_data, get_stats
from logic import gerar_escala_mensal

# Inicialização
st.set_page_config(page_title="Ops Manager", layout="centered") # Centrado para look mobile
init_db()
apply_styles()

# Área de Perfil/Topo (Simulando App Taxi)
st.markdown("""
    <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;'>
        <div>
            <p style='margin:0; color: #6B7280; font-size: 0.9rem;'>Bom dia,</p>
            <h2 style='margin:0; font-weight: 800;'>Comando Operacional</h2>
        </div>
        <div style='width: 45px; height: 45px; background: #1F2937; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white;'>
            CO
        </div>
    </div>
""", unsafe_allow_html=True)

# Navegação Centralizada (Dropdown Minimalista)
opcoes = ["🏠 Início", "👤 Gestão de Efetivos", "📅 Gerar Escala", "🔄 Trocas & Faltas", "⚙️ Configurações"]
menu = st.selectbox("Escolha o módulo", opcoes, label_visibility="collapsed")

# --- CONTEÚDO DENTRO DE CARDS ---

if "Início" in menu:
    df = get_stats()
    st.markdown(f"""
        <div class='main-card'>
            <p style='color: #6B7280; margin-bottom: 5px;'>Efetivos Ativos</p>
            <h1 style='margin:0;'>{len(df)} <span style='font-size: 1rem; color: #10B981;'>● Online</span></h1>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='main-card' style='text-align: center;'><h4>Turnos</h4><h2>124</h2></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='main-card' style='text-align: center;'><h4>Faltas</h4><h2 style='color: #EF4444;'>2</h2></div>", unsafe_allow_html=True)

elif "Efetivos" in menu:
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.subheader("Registo de Pessoal")
    # Baseado na estrutura do template
    aba1, aba2 = st.tabs(["Lista", "Novo"])
    
    with aba1:
        st.data_editor(get_stats(), use_container_width=True, hide_index=True)
    
    with aba2:
        with st.form("novo_app", clear_on_submit=True):
            nome = st.text_input("Nome Profissional")
            ni = st.text_input("Número Interno")
            p = st.selectbox("Posto", ["B1", "SCH", "CHF", "CMD"])
            
            tipo_d = st.radio("Disponibilidade", ["Fixo", "Pontual"], horizontal=True)
            if tipo_d == "Pontual":
                datas = st.date_input("Escolha os dias", value=(), format="DD/MM/YYYY")
                detalhe = ", ".join([d.strftime("%Y-%m-%d") for d in datas])
            else:
                dias = st.multiselect("Selecione os dias da semana:", 
                                     ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"])
                detalhe_final = ", ".join(dias)

            if st.form_submit_button("REGISTAR ELEMENTO"):
                st.success("Guardado!")
    st.markdown("</div>", unsafe_allow_html=True)

elif "Gerar Escala" in menu:
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.subheader("Planear Próximo Mês")
    m = st.selectbox("Mês", range(1, 13), index=datetime.now().month-1)
    a = st.number_input("Ano", value=2026)
    
    if st.button("🚀 GERAR ESCALA AGORA"):
        df_esc, msg = gerar_escala_mensal(m, a)
        if df_esc is not None:
            st.table(df_esc)
        else:
            st.error(msg)
    st.markdown("</div>", unsafe_allow_html=True)

elif "Configurações" in menu:
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.write("Ações de Administrador")
    if st.button("🔄 REPOR DADOS DEMO (60 ELEM)"):
        seed_demo_data()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #9CA3AF; font-size: 0.8rem;'>Ops Manager v3.0 • 2026</p>", unsafe_allow_html=True)
