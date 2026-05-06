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
                                     (nome, num, posto, mot, curso, tipo_disp, detalhe))
                        conn.commit()
                        st.success(f"{nome} adicionado com sucesso!")
                    except:
                        st.error("Erro: Número interno já existe.")
                    finally:
                        conn.close()
                else:
                    st.warning("Preencha o Nome e o Número Interno.")

# C. ESCALAS: GERAR / CONSULTAR
elif "Escalas" in selected_page:
    st.subheader("Planeamento de Turnos")
    
    c_m, c_a = st.columns(2)
    mes_alvo = c_m.selectbox("Mês", range(1, 13), index=datetime.now().month - 1)
    ano_alvo = c_a.number_input("Ano", value=2026)
    
if st.button("🚀 EXECUTAR ALGORITMO"):
        from logic import gerar_escala_mensal
        
        with st.spinner("A processar requisitos..."):
            df_gerado, msg = gerar_escala_mensal(mes_alvo, ano_alvo)
            
            if df_gerado is not None:
                st.success("Escala Gerada!")
                # Usar st.table para garantir que as 4 linhas por célula aparecem
                st.table(df_gerado) 
                
                # O download em CSV continuará a funcionar com todos os dados na mesma célula
                csv = df_gerado.to_csv(index=False).encode('utf-8')
                st.download_button("Baixar Escala", csv, "escala_detalhada.csv")

# D. REGISTO DE PRESENÇAS & TROCAS
elif "Presenças" in selected_page:
    st.subheader("🔄 Controlo de Execução de Serviço")
    st.write("Registe quem efetuou o serviço ou reporte faltas para as estatísticas.")
    
    with st.form("registo_efetivo"):
        col_d, col_n, col_t = st.columns(3)
        data_s = col_d.date_input("Data do Serviço")
        num_i = col_n.text_input("Nº Interno do Operacional")
        tipo_s = col_t.selectbox("Tipo", ["Serviço", "Falta"])
        
        if st.form_submit_button("REGISTAR NA BASE DE DADOS"):
            if num_i:
                conn = sqlite3.connect('gestao_operacional.db')
                conn.execute("INSERT INTO presencas (data_servico, num_interno, tipo) VALUES (?,?,?)",
                             (str(data_s), num_i, tipo_s))
                conn.commit()
                conn.close()
                st.success(f"Registo de {tipo_s} efetuado para o operacional {num_i}.")
            else:
                st.error("Insira o Número Interno.")

# E. ARQUIVO & IMPORTAÇÃO / EXPORTAÇÃO
elif "Arquivo" in selected_page:
    st.subheader("📥 Gestão de Ficheiros")
    
    col_exp, col_imp = st.columns(2)
    
    with col_exp:
        st.write("### Exportar Dados")
        st.write("Gere um ficheiro Excel com todos os elementos e contagem de serviços/faltas.")
        excel_bin = export_to_excel()
        st.download_button("💾 Baixar Estatísticas (Excel)", excel_bin, "estatisticas_pessoal.xlsx")
        
    with col_imp:
        st.write("### Importar Dados")
        st.write("Carregue o ficheiro template preenchido.")
        f_upload = st.file_uploader("Escolher Excel (.xlsx)", type=["xlsx"])
        if f_upload and st.button("CONFIRMAR IMPORTAÇÃO"):
            sucesso, msg_imp = import_from_excel(f_upload)
            if sucesso: st.success(msg_imp)
            else: st.error(msg_imp)

# F. CONFIGURAÇÕES
elif "Configurações" in selected_page:
    st.subheader("Definições Técnicas")
    st.write("Utilize estas ferramentas apenas para manutenção ou testes.")
    
    if st.button("🔄 GERAR 60 ELEMENTOS DEMO"):
        seed_demo_data()
        st.success("Base de dados povoada com 60 elementos de teste!")
        st.rerun()
    
    if st.button("⚠️ LIMPAR TODA A BASE DE DADOS", type="secondary"):
        conn = sqlite3.connect('gestao_operacional.db')
        conn.execute("DELETE FROM pessoal")
        conn.execute("DELETE FROM presencas")
        conn.commit()
        conn.close()
        st.warning("Todos os dados foram apagados.")
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #9CA3AF; margin-top: 30px; font-size: 0.8rem;'>Sistema de Gestão Operacional 2026</div>", unsafe_allow_html=True)
