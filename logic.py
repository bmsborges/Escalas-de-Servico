import pandas as pd
import sqlite3
import io

def export_to_excel():
    from database import get_stats
    df = get_stats()
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Estatisticas')
    return output.getvalue()

def import_from_excel(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file)
        conn = sqlite3.connect('gestao_operacional.db')
        # Mapeia colunas e insere
        df.to_sql('pessoal', conn, if_exists='append', index=False)
        conn.close()
        return True, f"Importados {len(df)} elementos."
    except Exception as e:
        return False, str(e)
