import re
import pandas as pd
import pdfplumber
import pypdf
from typing import List, Dict, Optional

class CicParser:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        
    def extract_transactions(self) -> List[Dict]:
        """Extrait les transactions depuis le PDF bancaire"""
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

    def _detect_bank_format(self, text: str) -> str:
        """Détecte le format de la banque"""
        if "CREDIT MUTUEL" in text.upper() or "CCM" in text:
            return "CREDIT_MUTUEL"
        elif "CIC" in text.upper():
            return "CIC"
        else:
            return "UNKNOWN"

    def _extract_from_text(self, text: str) -> List[Dict]:
        """Parse les transactions selon le format détecté"""
        bank_format = self._detect_bank_format(text)
        
        if bank_format == "CREDIT_MUTUEL":
            return self._parse_credit_mutuel(text)
        elif bank_format == "CIC":
            return self._parse_cic(text)
        else:
            print("Format de banque non reconnu, tentative avec le parser générique...")
            return self._parse_generic(text)

    def _parse_credit_mutuel(self, text: str) -> List[Dict]:
        """Parse spécifique pour Crédit Mutuel"""
        transactions = []
        lines = text.split('\n')
        
        # Recherche de la section des transactions
        start_index = 0
        for i, line in enumerate(lines):
            if "Date Date valeur Opération Débit EUROS Crédit EUROS" in line:
                start_index = i + 1
                break
        
        # Pattern pour les transactions Crédit Mutuel
        # Format: Date Date_valeur Description Montant_débit Montant_crédit
        trans_pattern = re.compile(
            r'^(\d{2}/\d{2}/\d{4})\s+'  # Date opération
            r'(\d{2}/\d{2}/\d{4})\s+'   # Date valeur
            r'(.+?)(?:\s+'              # Description (non-greedy)
            r'(\d{1,3}(?:\.\d{3})*,\d{2}))?$'  # Montant (optionnel)
        )
        
        i = start_index
        while i < len(lines):
            line = lines[i].strip()
            
            # Ignorer les lignes non pertinentes
            if (not line or 
                "Page" in line or
                "Sous réserve" in line or
                "Total des mouvements" in line or
                "SOLDE CREDITEUR" in line or
                "<<Suite au verso>>" in line or
                "Information sur la protection" in line or
                "Date Date valeur" in line):
                i += 1
                continue
            
            match = trans_pattern.match(line)
            if match:
                date_op, date_val, description, montant = match.groups()
                
                # Nettoyage de la description
                description = description.strip()
                
                # Gestion des descriptions multilignes
                j = i + 1
                while j < len(lines) and j < i + 5:  # Limite à 5 lignes suivantes
                    next_line = lines[j].strip()
                    
                    # Arrêter si nouvelle transaction ou ligne de contrôle
                    if (trans_pattern.match(next_line) or
                        not next_line or
                        any(keyword in next_line for keyword in [
                            "Page", "Sous réserve", "Total des mouvements",
                            "SOLDE CREDITEUR", "<<Suite", "Date Date valeur"
                        ])):
                        break
                    
                    # Vérifier si c'est un montant isolé (crédit)
                    montant_match = re.match(r'^(\d{1,3}(?:\.\d{3})*,\d{2})$', next_line)
                    if montant_match and not montant:
                        montant = montant_match.group(1)
                        j += 1
                        break
                    
                    # Sinon, ajouter à la description si pertinent
                    if (len(next_line) > 2 and 
                        not re.match(r'^\d+$', next_line) and  # Pas juste des chiffres
                        len(description) < 150):  # Limite de longueur
                        description += " " + next_line
                    
                    j += 1
                
                # Déterminer si c'est un débit ou crédit
                debit = None
                credit = None
                
                if montant:
                    # Logique pour déterminer débit/crédit basée sur le type d'opération
                    description_upper = description.upper()
                    
                    # Opérations typiquement créditrices
                    if any(keyword in description_upper for keyword in [
                        'REMCB', 'REM CHQ', 'VRST', 'VIR INST'
                    ]):
                        credit = montant
                    # Opérations typiquement débitrices
                    elif any(keyword in description_upper for keyword in [
                        'PAIEMENT CB', 'PAIEMENT PSC', 'CHEQUE', 'PRLV SEPA',
                        'COMCB', 'FACT'
                    ]):
                        debit = montant
                    else:
                        # Par défaut, considérer comme débit
                        debit = montant
                
                # Nettoyage final de la description
                description = re.sub(r'\s+', ' ', description.strip())
                description = re.sub(r'ICS\s*:\s*\S+\s*RUM\s*:\s*\S+', '', description)
                description = description.strip()
                
                transactions.append({
                    'DATE': date_op,
                    'DATE_VALEUR': date_val,
                    'LIBELLE': description,
                    'DEBIT': self._clean_amount(debit),
                    'CREDIT': self._clean_amount(credit)
                })
                
                i = j
            else:
                i += 1
        
        return transactions

    def _parse_cic(self, text: str) -> List[Dict]:
        """Parse spécifique pour CIC (code original adapté)"""
        transactions = []
        lines = text.split('\n')
        
        # Pattern pour les lignes de transaction CIC
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
                
                # Gestion des descriptions multilignes
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    
                    if (trans_pattern.match(next_line) or 
                        re.match(r'^\d{1,3}(?:\.\d{3})*,\d{2}$', next_line)):
                        break
                        
                    if (next_line and len(description) < 200):
                        clean_line = ' '.join(next_line.split())
                        if clean_line.strip():
                            description += " " + clean_line.strip()
                    j += 1
                
                # Vérifier crédit isolé
                for k in range(j, min(j+3, len(lines))):
                    next_line = lines[k].strip()
                    credit_match = re.match(r'^(\d{1,3}(?:\.\d{3})*,\d{2})$', next_line)
                    if credit_match:
                        credit = credit_match.group()
                        j = k + 1
                        break
                
                transactions.append({
                    'DATE': date_op,
                    'DATE_VALEUR': date_val,
                    'LIBELLE': re.sub(r'\s+', ' ', description).strip(),
                    'DEBIT': self._clean_amount(debit),
                    'CREDIT': self._clean_amount(credit)
                })
                
                i = j
            else:
                i += 1
                
        return transactions

    def _parse_generic(self, text: str) -> List[Dict]:
        """Parser générique pour formats non reconnus"""
        # Implémentation basique pour autres formats
        return []

    def _clean_amount(self, amount: Optional[str]) -> Optional[str]:
        """Nettoie un montant (suppression points + conversion virgule)"""
        if not amount:
            return None
        return amount.replace('.', '').replace(',', '.')

def save_to_csv(transactions: List[Dict], output_path: str = 'transactions_bancaires.csv'):
    """Sauvegarde les transactions en CSV"""
    if not transactions:
        print("Aucune transaction à exporter")
        return
    
    df = pd.DataFrame(transactions)
    
    # Conversion des types
    try:
        df['DATE'] = pd.to_datetime(df['DATE'], format='%d/%m/%Y')
        df['DATE_VALEUR'] = pd.to_datetime(df['DATE_VALEUR'], format='%d/%m/%Y')
    except:
        print("Erreur lors de la conversion des dates")
    
    for col in ['DEBIT', 'CREDIT']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Tri par date
    df = df.sort_values('DATE')
    
    df.to_csv(output_path, index=False, sep=';', encoding='utf-8')
    print(f"Transactions exportées dans {output_path}")
    print(f"Nombre de transactions: {len(transactions)}")
    
    # Statistiques
    total_debit = df['DEBIT'].sum()
    total_credit = df['CREDIT'].sum()
    print(f"Total débits: {total_debit:.2f} EUR")
    print(f"Total crédits: {total_credit:.2f} EUR")
    print(f"Solde: {total_credit - total_debit:.2f} EUR")

def analyze_transactions(transactions: List[Dict]):
    """Analyse les transactions extraites"""
    if not transactions:
        print("Aucune transaction à analyser")
        return
    
    print(f"\n=== ANALYSE DES TRANSACTIONS ===")
    print(f"Nombre total: {len(transactions)}")
    
    # Compter les transactions avec/sans montants
    with_debit = sum(1 for t in transactions if t.get('DEBIT'))
    with_credit = sum(1 for t in transactions if t.get('CREDIT'))
    
    print(f"Avec débit: {with_debit}")
    print(f"Avec crédit: {with_credit}")
    
    # Échantillon des premières transactions
    print(f"\n=== ÉCHANTILLON ===")
    for i, trans in enumerate(transactions[:5]):
        print(f"{i+1}. {trans['DATE']} - {trans['LIBELLE'][:50]}...")
        print(f"   Débit: {trans.get('DEBIT', 'N/A')} | Crédit: {trans.get('CREDIT', 'N/A')}")

# Exemple d'utilisation
if __name__ == "__main__":
    # Utilisation du parser amélioré
    parser = CicParser("DVI-Extrait_de_comptes_-_Compte_02167_000216877_02_C_C_Eurocompte.pdf")
    transactions = parser.extract_transactions()
    
    # Analyse des résultats
    analyze_transactions(transactions)
    
    # Sauvegarde
    if transactions:
        save_to_csv(transactions, 'transactions_credit_mutuel.csv')
