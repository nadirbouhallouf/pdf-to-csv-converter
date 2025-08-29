import re
import pandas as pd
import pdfplumber
import pypdf
from typing import List, Dict

class SocieteGeneraleParser:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        
    def extract_transactions(self) -> List[Dict]:
        """Extrait les transactions depuis le PDF Société Générale"""
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
        
        # Pattern pour les lignes de transaction Société Générale
        trans_pattern = re.compile(
            r'^(\d{2}/\d{2}/\d{4})\s+'  # Date opération
            r'(\d{2}/\d{2}/\d{4})\s+'   # Date valeur
            r'(.+?)\s+'                  # Libellé
            r'(\d{1,3}(?:\.\d{3})*,\d{2})?\s*'  # Débit (optionnel)
            r'(\d{1,3}(?:\.\d{3})*,\d{2})?$'   # Crédit (optionnel)
        )
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            match = trans_pattern.match(line)
            
            if match:
                date_op, date_val, description, debit, credit = match.groups()
                
                # Gestion des descriptions multilignes complètes
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    
                    # Arrêter si nouvelle transaction ou montant isolé
                    if (trans_pattern.match(next_line) or 
                        re.match(r'^\d{1,3}(?:\.\d{3})*,\d{2}$', next_line)):
                        break
                        
                    # Ignorer les lignes non pertinentes
                    if (next_line and 
                        not any(x in next_line for x in [
                            'Date', 'Valeur', 'Nature', 'Débit', 'Crédit',
                            'RELEVÉ DE COMPTE', 'COMPTE D\'ENTREPRISE',
                            'Page \\d', 'envoi n°', 
                            'VOS CONTACTS', 'Votre Banque à Distance',
                            'TOTAUX DES MOUVEMENTS', 'NOUVEAU SOLDE',
                            '*Opération exonérée', 'PROGRAMME DE FIDÉLITÉ',
                            'Rappel des seuils', 'suite>>'
                        ]) and
                        len(description) < 200):  # Limite de longueur
                        
                        # Nettoyage des espaces et éléments parasites
                        clean_line = ' '.join(next_line.split())
                        clean_line = re.sub(r'\*+$', '', clean_line)  # Supprime les astérisques
                        clean_line = re.sub(r'^\d+\s+', '', clean_line)  # Supprime numéros de ligne
                        if clean_line.strip():
                            description += " " + clean_line.strip()
                            
                    # Arrêter si saut de page
                    elif 'Page' in next_line:
                        break
                    j += 1
                
                # Vérifier les 3 lignes suivantes pour crédit isolé
                for k in range(j, min(j+3, len(lines))):
                    next_line = lines[k].strip()
                    credit_match = re.match(r'^(\d{1,3}(?:\.\d{3})*,\d{2})$', next_line)
                    if credit_match and not any(x in next_line.lower() for x in ['débit', 'date', 'valeur']):
                        credit = credit_match.group()
                        j = k + 1
                        break
                else:
                    credit = None
                
                # Nettoyage final
                description = re.sub(r'\s+', ' ', description).strip()
                
                # Conversion des montants
                clean_amount = lambda x: x.replace('.', '').replace(',', '.') if x else None
                
                transactions.append({
                    'DATE': date_op,
                    'DATE_VALEUR': date_val,
                    'LIBELLE': description,
                    'DEBIT': clean_amount(debit),
                    'CREDIT': clean_amount(credit)
                })
                
                i = j  # Avancer à la ligne suivante
            else:
                i += 1
                
        return transactions

def save_to_csv(transactions: List[Dict], output_path: str = 'transactions_sg.csv'):
    """Sauvegarde les transactions en CSV"""
    if not transactions:
        print("Aucune transaction à exporter")
        return
    
    df = pd.DataFrame(transactions)
    
    # Conversion des types
    df['DATE'] = pd.to_datetime(df['DATE'], format='%d/%m/%Y')
    df['DATE_VALEUR'] = pd.to_datetime(df['DATE_VALEUR'], format='%d/%m/%Y')
    for col in ['DEBIT', 'CREDIT']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df.to_csv(output_path, index=False, sep=';', encoding='utf-8')
    print(f"Transactions exportées dans {output_path}")

# Exemple d'utilisation
if __name__ == "__main__":
    parser = SocieteGeneraleParser("releve_sg.pdf")
    transactions = parser.extract_transactions()
    save_to_csv(transactions)
