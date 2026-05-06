import streamlit as st
from datetime import datetime, date
import sqlite3

# Importações dos módulos auxiliares
from styles import apply_styles
from database import init_db, seed_demo_data, get_stats
from logic import gerar_escala_mensal, export_to_excel, import_from_excel

# Configuração Inicial
st.set_page_config(page_title="Gestão Operacional", layout="wide", page_icon="🛡️")
init_db()
apply_styles()

# Título Principal
st.markdown("<h1 style='text-align: center;'>SISTEMA DE GESTÃO OPERACIONAL</h1>", unsafe_allow_html=True)

# Menu Dropdown Estilo Minimalista
menu_opcoes = [
    "🏠 Dashboard", 
    "👤 Gestão de Elementos", 
    "📅 Gerador de Escalas", 
    "🔄 Presenças e Trocas", 
    "📥 Importar/Exportar Dados",
    "⚙️ Configurações"
]
escolha = st.selectbox("NAVEGAÇÃO", menu_opcoes, label_visibility="collapsed")

st.markdown('<div class="main-card">', unsafe_allow_html=True)

# --- NAVEGAÇÃO ---

if escolha == "🏠 Dashboard":
    st.subheader("Painel de Controlo")
    df_stats = get_stats()
    c1, c2, c3 = st.columns(3)
    c1.metric("Efetivos Registados", len(df_stats))
    c2.metric("Total Serviços (Acumulado)", df_stats['servicos'].sum())
    c3.metric("Faltas Totais", df_stats['faltas'].sum())
    st.info("Utilize o menu acima para gerir os elementos ou gerar a escala do mês.")

elif escolha == "👤 Gestão de Elementos":
    st.subheader("Base de Dados de Pessoal")
    aba1, aba2 = st.tabs(["📋 Lista de Efetivos", "➕ Registar Novo"])
    
    with aba1:
        df_p = get_stats()
        st.data_editor(df_p, use_container_width=True, hide_index=True)
        
    with aba2:
        with st.form("novo_e"):
            col1, col2 = st.columns(2)
            nome = col1.text_input("Nome")
            num = col2.text_input("Nº Interno")
            p = st.selectbox("Posto", ["Est", "ESP", "B1", "B2", "B3", "SCH", "CHF", "OFB1", "OFB2"])
            m = st.radio("Motorista", ["Ligeiro", "Pesado"], horizontal=True)
            c = st.selectbox("Curso", ["TAS", "TAT", "TS", "Sem curso"])
            d_tipo = st.radio("Disponibilidade", ["Fixo", "Pontual"], horizontal=True)
            d_det = st.text_input("Detalhe (Dias da semana ou datas YYYY-MM-DD)")
            
            if st.form_submit_button("GUARDAR ELEMENTO"):
                conn = sqlite3.connect('gestao_operacional.db')
                conn.execute("INSERT INTO pessoal (nome, num_interno, posto, motorista, curso, disp_tipo, disp_detalhe) VALUES (?,?,?,?,?,?,?)",
                             (nome, num, p, m, c, d_tipo, d_det))
                conn.commit()
                conn.close()
                st.success("Elemento registado com sucesso!")

elif escolha == "📅 Gerador de Escalas":
    st.subheader("Gerar Escala Mensal (22:00 - 07:00)")
    c_m, c_a = st.columns(2)
    mes = c_m.selectbox("Mês", range(1, 13), index=datetime.now().month - 1)
    ano = c_a.number_input("Ano", value=2026)
    
    if st.button("🚀 EXECUTAR ALGORITMO"):
        df_esc, msg = gerar_escala_mensal(mes, ano)
        if df_esc is not None:
            st.success("Escala gerada com sucesso!")
            st.table(df_esc) # st.table expande as células para mostrar os dados detalhados
            csv = df_esc.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Baixar Escala (CSV)", csv, f"escala_{mes}_{ano}.csv")
        else:
            st.error(msg)

elif escolha == "🔄 Presenças e Trocas":
    st.subheader("Registo de Execução de Serviço")
    with st.form("presenca"):
        c1, c2, c3 = st.columns(3)
        d_serv = c1.date_input("Data do Serviço")
        ni = c2.text_input("Nº Interno do Operacional")
        t_reg = c3.selectbox("Tipo", ["Serviço", "Falta"])
        if st.form_submit_button("REGISTAR"):
            conn = sqlite3.connect('gestao_operacional.db')
            conn.execute("INSERT INTO presencas (data_servico, num_interno, tipo) VALUES (?,?,?)",
                         (str(d_serv), ni, t_reg))
            conn.commit()
            conn.close()
            st.success(f"Registo de {t_reg} efetuado.")

elif escolha == "📥 Importar/Exportar Dados":
    st.subheader("Movimentação de Ficheiros")
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("### Exportação")
        if st.button("Gerar Excel de Estatísticas"):
            ex_data = export_to_excel()
            st.download_button("💾 Baixar Estatísticas", ex_data, "estatisticas.xlsx")
            
    with col_b:
        st.write("### Importação")
        up = st.file_uploader("Carregar Excel de Elementos", type=["xlsx"])
        if up and st.button("Processar Importação"):
            s, m = import_from_excel(up)
            if s: st.success(m)
            else: st.error(m)

elif escolha == "⚙️ Configurações":
    st.subheader("Ferramentas de Sistema")
    if st.button("🔄 GERAR 60 ELEMENTOS DEMO"):
        seed_demo_data()
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
