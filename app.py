import streamlit as st
import sqlite3
from datetime import datetime, date

# Importação dos teus módulos auxiliares
from styles import apply_styles
from database import init_db, seed_demo_data, get_stats
from logic import gerar_escala_mensal, export_to_excel

# 1. Configuração de Página
st.set_page_config(page_title="Command Center - Operacional", layout="wide", page_icon="🛡️")
init_db()
apply_styles()

# 2. Cabeçalho Minimalista
st.markdown("<h1 style='text-align: center; color: #374151;'>SISTEMA OPERACIONAL</h1>", unsafe_allow_html=True)

# 3. Menu Superior Dropdown
menu_opcoes = [
    "🏠 Dashboard", 
    "👤 Elementos", 
    "📅 Escalas", 
    "🔄 Presenças", 
    "⚙️ Configuração"
]
escolha = st.selectbox("NAVEGAÇÃO PRINCIPAL", menu_opcoes, label_visibility="collapsed")

# 4. Contentor Principal
st.markdown('<div class="main-card">', unsafe_allow_html=True)

if escolha == "🏠 Dashboard":
    df_stats = get_stats()
    c1, c2, c3 = st.columns(3)
    c1.metric("Efetivos Registados", len(df_stats))
    c2.metric("Serviços Acumulados", df_stats['servicos'].sum())
    c3.metric("Faltas Totais", df_stats['faltas'].sum())
    st.info("Utilize o menu acima para navegar.")

elif escolha == "👤 Elementos":
    aba_lista, aba_novo = st.tabs(["📋 Lista de Efetivos", "➕ Novo Cadastro"])
    
    with aba_lista:
        st.data_editor(get_stats(), use_container_width=True, hide_index=True)
        
    with aba_novo:
        with st.form("form_novo_elemento", clear_on_submit=True):
            col1, col2 = st.columns(2)
            nome = col1.text_input("Nome Profissional")
            num = col2.text_input("Número Interno")
            
            col3, col4, col5 = st.columns(3)
            posto = col3.selectbox("Posto", ["Est", "ESP", "B1", "B2", "B3", "SCH", "CHF", "OFB1", "OFB2", "CMD"])
            mot = col4.radio("Motorista", ["Ligeiro", "Pesado"], horizontal=True)
            curso = col5.selectbox("Curso", ["TAS", "TAT", "TS", "Sem curso"])
            
            st.markdown("---")
            st.write("📅 **Disponibilidade**")
            tipo_d = st.radio("Tipo de Disponibilidade", ["Fixo", "Pontual"], horizontal=True)
            
            detalhe_final = ""

            if tipo_d == "Fixo":
                dias = st.multiselect("Selecione os dias da semana:", 
                                     ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"])
                detalhe_final = ", ".join(dias)
            else:
                # CORREÇÃO DO CALENDÁRIO:
                # Usamos uma tupla vazia ou uma data padrão para forçar o widget
                datas_selecionadas = st.date_input(
                    "Clique nos dias do calendário (Seleção Múltipla):",
                    value=(), # Tupla vazia permite selecionar vários dias individuais
                    format="DD/MM/YYYY",
                    help="Selecione cada dia que o elemento estará disponível."
                )
                if datas_selecionadas:
                    # Converter lista de datas em string para a BD
                    detalhe_final = ", ".join([d.strftime("%Y-%m-%d") for d in datas_selecionadas])

            if st.form_submit_button("💾 GUARDAR ELEMENTO"):
                if nome and num and detalhe_final:
                    conn = sqlite3.connect('gestao_operacional.db')
                    try:
                        conn.execute("""INSERT INTO pessoal 
                                     (nome, num_interno, posto, motorista, curso, disp_tipo, disp_detalhe) 
                                     VALUES (?,?,?,?,?,?,?)""",
                                     (nome, num, posto, mot, curso, tipo_d, detalhe_final))
                        conn.commit()
                        st.success(f"Elemento {nome} guardado com sucesso!")
                    except Exception as e:
                        st.error(f"Erro: Verifique se o Nº Interno já existe. ({e})")
                    finally:
                        conn.close()
                else:
                    st.warning("Preencha todos os campos e selecione os dias no calendário.")

elif escolha == "📅 Escalas":
    st.subheader("Gerar Escala Mensal")
    c1, c2 = st.columns(2)
    mes = c1.selectbox("Mês", range(1, 13), index=datetime.now().month-1)
    ano = c2.number_input("Ano", value=2026)
    
    if st.button("🚀 GERAR ESCALA"):
        df_esc, msg = gerar_escala_mensal(mes, ano)
        if df_esc is not None:
            st.table(df_esc)
        else:
            st.error(msg)

elif escolha == "🔄 Presenças":
    st.subheader("Registo de Assiduidade")
    with st.form("registo_p"):
        d = st.date_input("Data do Serviço", value=date.today())
        ni = st.text_input("Nº Interno")
        t = st.selectbox("Tipo", ["Serviço", "Falta"])
        if st.form_submit_button("REGISTAR"):
            conn = sqlite3.connect('gestao_operacional.db')
            conn.execute("INSERT INTO presencas (data_servico, num_interno, tipo) VALUES (?,?,?)", (str(d), ni, t))
            conn.commit()
            conn.close()
            st.success("Registo efetuado.")

elif escolha == "⚙️ Configuração":
    st.subheader("Ferramentas")
    if st.button("🔄 POVOAR 60 ELEMENTOS DEMO"):
        seed_demo_data()
        st.success("Dados de teste criados!")
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
