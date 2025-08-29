import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from pdf_to_csv.bank_parsers import get_parser
import os
from pdf_to_csv.utils.date_utils import parse_date
from pdf_to_csv.utils.ocr_utils import extract_text_from_scanned_pdf

st.set_page_config(page_title="PDF Bancaire vers CSV", layout="wide")

def main():
    st.title("Convertisseur de relevés bancaires PDF vers CSV")
    
    # Upload du fichier
    uploaded_file = st.file_uploader("Télécharger un relevé bancaire PDF", type="pdf")
    
    if uploaded_file:
        # Sauvegarde temporaire du fichier
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        try:
            # Détection du type de banque et extraction des données
            with st.spinner("Extraction de transactions en cours..."):
                parser = get_parser("temp.pdf")
            
            with st.status("Analyse des transactions...", expanded=False) as status:
                transactions = parser.extract_transactions()
                status.update(label="Analyse terminée", state="complete")
            
            # Conversion en DataFrame
            with st.spinner("Création du DataFrame..."):
                df = pd.DataFrame(transactions)
                
                # S'assurer que les colonnes DEBIT et CREDIT existent
                if 'DEBIT' not in df.columns:
                    df['DEBIT'] = None
                if 'CREDIT' not in df.columns:
                    df['CREDIT'] = None
            
            # Création colonne montant unifiée avec gestion d'erreur
            try:
                credit_values = pd.to_numeric(df['CREDIT'], errors='coerce').fillna(0)
                debit_values = pd.to_numeric(df['DEBIT'], errors='coerce').fillna(0)
                df['montant'] = credit_values - debit_values
            except Exception as e:
                st.error(f"Erreur lors du calcul du montant: {e}")
                df['montant'] = 0
            
            # Options de formatage
            st.sidebar.header("Options CSV")
            decimal_sep = st.sidebar.selectbox("Séparateur décimal", [",", "."])
            delimiter = st.sidebar.selectbox("Séparateur de champ", [";", ","])
            
            # Affichage des données
            st.subheader("Aperçu des données")
            st.dataframe(df)
            
            # Statistiques
            st.subheader("Statistiques")
            col1, col2, col3 = st.columns(3)
            col1.metric("Nombre de transactions", len(df))
            
            # Calcul des totaux avec gestion d'erreur
            try:
                total_debit = pd.to_numeric(df['DEBIT'], errors='coerce').sum()
                total_credit = pd.to_numeric(df['CREDIT'], errors='coerce').sum()
                col2.metric("Total Débit", f"{total_debit:.2f} €")
                col3.metric("Total Crédit", f"{total_credit:.2f} €")
            except Exception as e:
                col2.metric("Total Débit", "Erreur")
                col3.metric("Total Crédit", "Erreur")
            
            # Conversion en CSV
            with st.status("Génération du fichier CSV...", expanded=False) as status:
                csv = df.to_csv(sep=delimiter, decimal=decimal_sep, index=False)
                status.update(label="CSV prêt à être téléchargé", state="complete")
            
            # Bouton de téléchargement
            st.download_button(
                label="Télécharger en CSV",
                data=csv,
                file_name="releve_bancaire.csv",
                mime="text/csv"
            )
            
        except Exception as e:
            st.error(f"Erreur lors du traitement du PDF: {str(e)}")
        finally:
            # Nettoyage du fichier temporaire
            if os.path.exists("temp.pdf"):
                os.remove("temp.pdf")

if __name__ == "__main__":
    main()
