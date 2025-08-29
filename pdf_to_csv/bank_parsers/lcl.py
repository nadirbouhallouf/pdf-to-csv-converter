import re
import pdfplumber
import pypdf
from typing import List, Dict

class LclParser:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        
    def extract_transactions(self) -> List[Dict]:
        """Extrait les transactions depuis le PDF LCL"""
        return self._extract_from_pdf(self.pdf_path)
    
    def _extract_from_pdf(self, pdf_path: str) -> List[Dict]:
        """Extrait le texte du PDF et parse les transactions"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = "\n".join(page.extract_text() for page in pdf.pages)
            return self._extract_from_text(full_text)
        except Exception as e:
            print(f"Erreur pdfplumber: {e}, tentative avec pypdf...")
            try:
                with open(pdf_path, 'rb') as f:
                    pdf = pypdf.PdfReader(f)
                    full_text = "\n".join(page.extract_text() for page in pdf.pages)
                return self._extract_from_text(full_text)
            except Exception as e2:
                print(f"Erreur pypdf: {e2}")
                return []

    def _extract_from_text(self, text: str) -> List[Dict]:
        """Parse les transactions depuis le texte brut"""
        transactions = []
        lines = text.split('\n')
        
        # Pattern pour les lignes de transaction LCL
        # Format: Date Libellé Date_valeur Montant
        trans_pattern = re.compile(
            r'^(\d{2}\.\d{2})\s+'       # Date opération (07.07)
            r'(.+?)\s+'                   # Libellé
            r'(\d{2}\.\d{2}\.\d{2})\s+'  # Date valeur (07.07.25)
            r'([\d\s]+,\d{2})\s*'        # Montant
            r'(\.)?$'                     # Point final pour crédit
        )
        
        # Pattern pour détecter les sections à ignorer
        ignore_pattern = re.compile(r'^(Page \d|LIBELLE:|REF\.|ID\.|MANDAT:)')
        
        in_transactions_section = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Détecter le début de la section des transactions
            if "ECRITURES DE LA PERIODE" in line:
                in_transactions_section = True
                continue
                
            if not in_transactions_section:
                continue
                
            # Ignorer les lignes de référence/mandat
            if ignore_pattern.match(line):
                continue
                
            match = trans_pattern.match(line)
            
            if match:
                date_op, description, date_val, amount, is_credit = match.groups()
                
                # Nettoyer le libellé
                description = ' '.join(description.split())
                
                # Nettoyer le montant
                amount_clean = amount.replace(' ', '').replace(',', '.')
                
                transactions.append({
                    'DATE': date_op,
                    'DATE_VALEUR': date_val,
                    'LIBELLE': description,
                    'DEBIT': None if is_credit else amount_clean,
                    'CREDIT': amount_clean if is_credit else None
                })
                
        return transactions

def save_to_csv(transactions: List[Dict], output_path: str = 'transactions_lcl.csv'):
    """Sauvegarde les transactions en CSV"""
    if not transactions:
        print("Aucune transaction à exporter")
        return
    
    import pandas as pd
    df = pd.DataFrame(transactions)
    
    # Conversion des types
    df['DATE'] = pd.to_datetime(df['DATE'], format='%d.%m')
    df['DATE_VALEUR'] = pd.to_datetime(df['DATE_VALEUR'], format='%d.%m.%y')
    for col in ['DEBIT', 'CREDIT']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df.to_csv(output_path, index=False, sep=';', encoding='utf-8')
    print(f"Transactions exportées dans {output_path}")

# Exemple d'utilisation
if __name__ == "__main__":
    parser = LclParser("releve_lcl.pdf")
    transactions = parser.extract_transactions()
    save_to_csv(transactions)
