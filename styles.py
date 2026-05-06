import streamlit as st

def apply_styles():
    st.markdown("""
        <style>
        @import url('https://fonts.cdnfonts.com/css/gill-sans-mt');
        
        html, body, [class*="css"] {
            font-family: 'Gill Sans MT', sans-serif !important;
            background-color: #F8F9FA;
            color: #333333;
        }

        /* Menu Dropdown */
        .stSelectbox div[data-baseweb="select"] {
            border: 1px solid #D1D5DB;
            border-radius: 4px;
        }

        /* Content Container */
        .block-container {
            padding-top: 2rem;
            max-width: 1100px;
        }

        .main-card {
            background-color: #FFFFFF;
            padding: 25px;
            border-radius: 10px;
            border: 1px solid #E5E7EB;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        
        .stButton>button {
            border-radius: 4px;
            background-color: #4B5563;
            color: white;
            border: none;
        }
        </style>
    """, unsafe_allow_html=True)
