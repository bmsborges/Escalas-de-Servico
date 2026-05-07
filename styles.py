import streamlit as st

def apply_styles():
    st.markdown("""
        <style>
        @import url('https://fonts.cdnfonts.com/css/aptos');
        
        html, body, [class*="css"] {
            font-family: 'Aptos', sans-serif !important;
            background-color: #F3F4F6;
            color: #1F2937;
        }

        /* Layout Centrado (Estilo App) */
        .block-container {
            max-width: 850px !important;
            padding-top: 2rem !important;
        }

        /* Cartões Premium */
        .main-card {
            background-color: #FFFFFF;
            padding: 24px;
            border-radius: 28px; /* Cantos arredondados estilo iOS/Android moderno */
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }

        /* Botões Estilo App */
        .stButton>button {
            border-radius: 18px !important;
            height: 30px !important;
            font-weight: 600 !important;
            background-color: #1F2937 !important;
            transition: all 0.3s ease;
        }
        
        /* Dropdown e Inputs Arredondados */
        div[data-baseweb="select"], input {
            border-radius: 14px !important;
        }

        /* Escala (Tabela) */
        .stTable td {
            white-space: pre-wrap !important;
            font-size: 0.85rem !important;
            vertical-align: top !important;
        }
        </style>
    """, unsafe_allow_html=True)
