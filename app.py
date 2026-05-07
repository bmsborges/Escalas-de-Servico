import streamlit as st
from datetime import datetime, date
import sqlite3
from styles import apply_styles
from database import init_db, seed_demo_data, get_stats
from logic import gerar_escala_mensal

st.set_page_config(page_title="GestOP", layout="wide")
init_db()
apply_styles()

# Topo Estilo App
st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>🛡️ Comando</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #6B7280;'>Gestão Operacional de Escalas</p>", unsafe_allow_html=True)

menu = st.selectbox("MENU", ["🏠 Dashboard", "👤 Elementos", "📅 Escalas", "⚙️ Configuração"], label_visibility="collapsed")

st.markdown('<div class="main-card">', unsafe_allow_html=True)

if menu == "🏠 Dashboard":
    df = get_stats()
    c1, c2, c3 = st.columns(3)
    c1.metric("Efetivos", len(df))
    c2.metric("Serviços", df['servicos'].sum())
    c3.metric("Faltas", df['faltas'].sum())

elif menu == "👤 Elementos":
    aba1, aba2 = st.tabs(["📋 Lista de Efetivos", "➕ Novo Registo"])
    with aba1:
        st.data_editor(get_stats(), use_container_width=True, hide_index=True)
    with aba2:
        with st.form("novo_elem", clear_on_submit=True):
            n = st.text_input("Nome Profissional")
            ni = st.text_input("Nº Interno")
            col_a, col_b = st.columns(2)
            pst = col_a.selectbox("Posto", ["B1", "B2", "SCH", "CHF"])
            crs = col_b.selectbox("Curso", ["TAS", "TAT", "Sem curso"])
            mot = st.radio("Motorista", ["Ligeiro", "Pesado"], horizontal=True)
            
            st.markdown("---")
            tipo_d = st.radio("Disponibilidade", ["Fixo", "Pontual"], horizontal=True)
            detalhe_final = ""

            if tipo_d == "Fixo":
                d_fixos = st.multiselect("Dias da Semana", ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"])
                detalhe_final = ", ".join(d_fixos)
            else:
                if st.button("📅 Selecionar Datas Específicas"):
                   st.session_state.mostrar_calendario = True
                if st.session_state.get('mostrar_calendario', False):
        # A tupla vazia () em 'value' permite selecionar múltiplos dias avulsos
                datas_selecionadas = st.date_input(
                "Selecione os dias no calendário:",
                value=(), 
                format="DD/MM/YYYY",
                help="Clique em cada dia que deseja adicionar. Clique novamente para remover."
                )

            if datas_selecionadas:
                # Exibição visual das datas selecionadas para o utilizador
                st.write(f"**Datas selecionadas:** {len(datas_selecionadas)}")
                
                # Conversão para o formato de texto YYYY-MM-DD esperado pela base de dados
                detalhe_final = ", ".join([d.strftime("%Y-%m-%d") for d in datas_selecionadas])
    
                if st.form_submit_button("💾 GUARDAR ELEMENTO"):
                    if n and ni and detalhe_final:
                        conn = sqlite3.connect('gestao_operacional.db')
                        conn.execute("INSERT INTO pessoal (nome, num_interno, posto, motorista, curso, disp_tipo, disp_detalhe) VALUES (?,?,?,?,?,?,?)",
                                     (n, ni, pst, mot, crs, tipo_d, detalhe_final))
                        conn.commit()
                        conn.close()
                        st.success("Operacional registado!")
                        st.session_state.calendario_aberto = False

elif menu == "📅 Escalas":
    c1, c2 = st.columns(2)
    m = c1.selectbox("Mês", range(1, 13), index=datetime.now().month-1)
    a = c2.number_input("Ano", value=2026)
    if st.button("🚀 GERAR ESCALA MENSAL"):
        df_esc, msg = gerar_escala_mensal(m, a)
        if df_esc is not None:
            st.table(df_esc) # Expande células para mostrar detalhe completo[cite: 1]

elif menu == "⚙️ Configuração":
    if st.button("🔄 GERAR 60 ELEMENTOS DEMO"):
        seed_demo_data()
        st.success("Dados carregados!")
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
