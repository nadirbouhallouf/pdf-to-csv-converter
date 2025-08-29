import re
import pandas as pd
import pdfplumber
import pypdf
from typing import List, Dict, Optional
from datetime import datetime

class BnpParserImproved:
    def __init__(self, pdf_path: str):
        """
        Initialisation du parser BNP Paribas amélioré
        
        :param pdf_path: Chemin du fichier PDF à parser
        """
        self.pdf_path = pdf_path
        
    def extract_transactions(self) -> List[Dict]:
        """Extrait les transactions depuis le PDF bancaire BNP Paribas"""
        return self._extract_from_pdf(self.pdf_path)
    
    def _extract_from_pdf(self, pdf_path: str) -> List[Dict]:
        """Extrait le texte du PDF et parse les transactions"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
            return self._extract_from_text(full_text)
        except Exception as e:
            print(f"Erreur pdfplumber: {e}, tentative avec pypdf...")
            try:
                with open(pdf_path, 'rb') as f:
                    pdf = pypdf.PdfReader(f)
                    full_text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
                return self._extract_from_text(full_text)
            except Exception as e2:
                print(f"Erreur lors du traitement du PDF: {e2}")
                return []

    def _extract_from_text(self, text: str) -> List[Dict]:
        """Parse les transactions depuis le texte extrait"""
        print("=== DÉBUT DU PARSING ===")
        transactions = []
        lines = text.split('\n')
        
        # Debug: afficher les premières lignes
        print("=== PREMIÈRES LIGNES ===")
        for i, line in enumerate(lines[:30]):
            if line.strip():
                print(f"{i:2d}: {line}")
        
        # Sections à traiter
        sections_config = {
            "VIREMENTS RECUS": {"type": "credit", "keywords": ["VIR SEPA RECU"]},
            "AUTRES OPERATIONS CREDIT": {"type": "credit", "keywords": ["REMBOURST"]},
            "PAIEMENTS PAR CARTES": {"type": "debit", "keywords": ["DU "]},
            "VIREMENTS EMIS": {"type": "debit", "keywords": ["VIREMENT SEPA EMIS"]},
            "PRELEVEMENTS, AMORTISSEMENTS DE PRETS": {"type": "debit", "keywords": ["PRLV SEPA"]},
            "AUTRES OPERATIONS DEBIT": {"type": "debit", "keywords": ["COMMISSIONS"]}
        }
        
        for section_name, config in sections_config.items():
            print(f"\n=== TRAITEMENT SECTION: {section_name} ===")
            section_transactions = self._parse_section_improved(lines, section_name, config)
            print(f"Trouvé {len(section_transactions)} transactions")
            transactions.extend(section_transactions)
            
            # Debug: afficher les premières transactions trouvées
            for i, trans in enumerate(section_transactions[:3]):
                print(f"  {i+1}. {trans['DATE']} | {trans['LIBELLE'][:50]} | D:{trans.get('DEBIT')} C:{trans.get('CREDIT')}")
        
        print(f"\n=== TOTAL: {len(transactions)} transactions extraites ===")
        return self._validate_transactions(transactions)
    
    def _parse_section_improved(self, lines: List[str], section_name: str, config: Dict) -> List[Dict]:
        """Parse une section avec une approche améliorée"""
        transactions = []
        
        # Trouver le début de la section
        start_index = -1
        for i, line in enumerate(lines):
            if section_name in line:
                start_index = i + 1
                print(f"Section '{section_name}' trouvée ligne {i}")
                break
        
        if start_index == -1:
            print(f"Section '{section_name}' non trouvée")
            return transactions
        
        # Trouver la fin de la section
        end_index = len(lines)
        for i in range(start_index, len(lines)):
            line = lines[i].strip()
            if "Sous total..." in line or self._is_new_section(line):
                end_index = i
                print(f"Fin de section à la ligne {i}: '{line[:50]}'")
                break
        
        # Parser les lignes de la section
        i = start_index
        while i < end_index:
            line = lines[i].strip()
            
            if not line or self._is_skip_line(line):
                i += 1
                continue
            
            print(f"  Analyse ligne {i}: {line}")
            
            # Essayer de parser la transaction
            transaction = self._parse_transaction_line(line, lines, i, end_index, config)
            
            if transaction:
                transaction['SECTION'] = section_name
                transactions.append(transaction)
                i = transaction.get('_next_line', i + 1)
                print(f"    ✓ Transaction trouvée: {transaction['LIBELLE'][:40]}")
            else:
                i += 1
                print(f"    ✗ Ligne ignorée")
        
        return transactions
    
    def _parse_transaction_line(self, line: str, lines: List[str], line_index: int, end_index: int, config: Dict) -> Optional[Dict]:
        """Parse une ligne de transaction avec plusieurs patterns"""
        
        # Pattern principal: DATE DESCRIPTION DATE MONTANT
        patterns = [
            # Pattern standard BNP
            r'^(\d{2}\.\d{2}\.\d{2})\s+(.+?)\s+(\d{2}\.\d{2}\.\d{2})\s+(\d{1,3}(?:\s\d{3})*,\d{2})$',
            # Pattern sans date de valeur
            r'^(\d{2}\.\d{2}\.\d{2})\s+(.+?)\s+(\d{1,3}(?:\s\d{3})*,\d{2})$',
            # Pattern plus flexible
            r'^(\d{2}\.\d{2}\.\d{2})\s+(.+)'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                groups = match.groups()
                
                if len(groups) == 4:  # Date, description, date_valeur, montant
                    date_comptable, description, date_valeur, montant = groups
                elif len(groups) == 3:
                    if re.match(r'^\d{1,3}(?:\s\d{3})*,\d{2}$', groups[2]):  # Le 3ème groupe est un montant
                        date_comptable, description, montant = groups
                        date_valeur = date_comptable
                    else:  # Le 3ème groupe est une date
                        date_comptable, description, date_valeur = groups
                        # Chercher le montant sur la ligne suivante ou dans la même ligne
                        montant = self._find_amount_in_context(lines, line_index, end_index)
                        if not montant:
                            continue
                else:  # Ligne incomplète, chercher le montant ailleurs
                    date_comptable = groups[0]
                    description = groups[1]
                    date_valeur = date_comptable
                    montant = self._find_amount_in_context(lines, line_index, end_index)
                    if not montant:
                        continue
                
                # Collecter les lignes de description supplémentaires
                full_description = description.strip()
                next_line_idx = line_index + 1
                
                while next_line_idx < end_index and next_line_idx < len(lines):
                    next_line = lines[next_line_idx].strip()
                    if (not next_line or 
                        re.match(r'^\d{2}\.\d{2}\.\d{2}', next_line) or
                        "Sous total..." in next_line or
                        self._is_skip_line(next_line) or
                        re.match(r'^\d{1,3}(?:\s\d{3})*,\d{2}$', next_line)):
                        break
                    
                    full_description += " " + next_line
                    next_line_idx += 1
                
                # Créer la transaction
                is_credit = (config["type"] == "credit")
                
                return {
                    'DATE': self._convert_date_format(date_comptable),
                    'DATE_VALEUR': self._convert_date_format(date_valeur),
                    'LIBELLE': full_description,
                    'DEBIT': None if is_credit else self._clean_amount(montant),
                    'CREDIT': self._clean_amount(montant) if is_credit else None,
                    '_next_line': next_line_idx
                }
        
        return None
    
    def _find_amount_in_context(self, lines: List[str], start_idx: int, end_idx: int) -> Optional[str]:
        """Cherche un montant dans les lignes suivantes"""
        for i in range(start_idx, min(start_idx + 3, end_idx, len(lines))):
            line = lines[i].strip()
            # Chercher un montant dans la ligne
            amount_match = re.search(r'\b(\d{1,3}(?:\s\d{3})*,\d{2})\b', line)
            if amount_match:
                return amount_match.group(1)
        return None
    
    def _is_new_section(self, line: str) -> bool:
        """Vérifie si une ligne marque le début d'une nouvelle section"""
        section_keywords = [
            "VIREMENTS RECUS", "AUTRES OPERATIONS CREDIT", "PAIEMENTS PAR CARTES",
            "VIREMENTS EMIS", "PRELEVEMENTS, AMORTISSEMENTS DE PRETS", 
            "AUTRES OPERATIONS DEBIT", "TOTAL DES OPERATIONS"
        ]
        return any(keyword in line for keyword in section_keywords)
    
    def _is_skip_line(self, line: str) -> bool:
        """Détermine si une ligne doit être ignorée"""
        skip_patterns = [
            r"^- CARTE N°",
            r"^Page \d+",
            r"^BNP PARIBAS SA",
            r"^3478",
            r"^P\.",
            r"^\d{12}$",
            r"^SORPSITSPREPFC",
            "RELEVE DE VOTRE COMPTE",
            "Raison sociale",
            "RIB :",
            "IBAN :",
            "BIC :",
            "Les sommes déposées",
            "www.garantiedesdepots.fr",
            "Relevé N°",
            "PERIODE DU",
            "Solde au",
            "Votre chargé d'Affaires",
            "DATE COMPTABLE",
            "NATURE DES OPERATIONS",
            "DATE DE VALEUR",
            "DEBIT CREDIT"
        ]
        
        return any(re.match(pattern, line) or pattern in line for pattern in skip_patterns)
    
    def _convert_date_format(self, date_str: str) -> str:
        """Convertit le format de date BNP (dd.mm.yy) vers dd/mm/yyyy"""
        if not date_str:
            return date_str
            
        try:
            parts = date_str.split('.')
            if len(parts) == 3:
                day, month, year = parts
                if len(year) == 2:
                    year = '20' + year if int(year) <= 50 else '19' + year
                return f"{day}/{month}/{year}"
        except:
            pass
            
        return date_str
    
    def _clean_amount(self, amount: Optional[str]) -> Optional[str]:
        """Nettoie un montant en format BNP (avec espaces et virgules)"""
        if not amount:
            return None
        # Format BNP: "1 234,56" -> "1234.56"
        cleaned = amount.replace(' ', '').replace(',', '.')
        return cleaned
    
    def _validate_transactions(self, transactions: List[Dict]) -> List[Dict]:
        """Valide et complète les transactions"""
        validated_transactions = []
        
        for transaction in transactions:
            validated_transaction = {
                'DATE': transaction.get('DATE', ''),
                'DATE_VALEUR': transaction.get('DATE_VALEUR', ''),
                'LIBELLE': transaction.get('LIBELLE', ''),
                'DEBIT': transaction.get('DEBIT'),
                'CREDIT': transaction.get('CREDIT'),
                'SECTION': transaction.get('SECTION', 'UNKNOWN')
            }
            # Supprimer les clés techniques
            validated_transaction = {k: v for k, v in validated_transaction.items() if not k.startswith('_')}
            validated_transactions.append(validated_transaction)
        
        return validated_transactions

def save_to_csv_improved(transactions: List[Dict], output_path: str = 'transactions_bnp_improved.csv'):
    """Sauvegarde améliorée des transactions en CSV"""
    if not transactions:
        print("❌ Aucune transaction à exporter")
        return

    try:
        df = pd.DataFrame(transactions)
        
        print(f"📊 DataFrame créé avec {len(df)} lignes et colonnes: {list(df.columns)}")
        
        # Conversion des dates
        for col in ['DATE', 'DATE_VALEUR']:
            if col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col], format='%d/%m/%Y', errors='coerce')
                except Exception as e:
                    print(f"⚠️ Erreur conversion date {col}: {e}")
        
        # Conversion des montants
        for col in ['DEBIT', 'CREDIT']:
            if col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except Exception as e:
                    print(f"⚠️ Erreur conversion montant {col}: {e}")
        
        # Tri par date
        if 'DATE' in df.columns:
            df = df.sort_values('DATE', na_position='last')
        
        # Sauvegarde
        df.to_csv(output_path, index=False, sep=';', encoding='utf-8')
        print(f"✅ Transactions exportées dans {output_path}")
        
        # Statistiques
        print(f"\n=== STATISTIQUES ===")
        print(f"Nombre total de transactions: {len(df)}")
        
        if 'SECTION' in df.columns:
            print("\nRépartition par section:")
            section_counts = df['SECTION'].value_counts()
            for section, count in section_counts.items():
                print(f"  {section}: {count}")
        
        # Calculs financiers
        total_debit = df['DEBIT'].sum() if 'DEBIT' in df.columns else 0
        total_credit = df['CREDIT'].sum() if 'CREDIT' in df.columns else 0
        
        if not pd.isna(total_debit) and not pd.isna(total_credit):
            print(f"\n💰 Total débits: {total_debit:.2f} EUR")
            print(f"💳 Total crédits: {total_credit:.2f} EUR")
            print(f"📈 Solde net: {total_credit - total_debit:.2f} EUR")
        
        # Aperçu des données
        print(f"\n=== APERÇU DES TRANSACTIONS ===")
        print(df.head(10).to_string(index=False))
        
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        
        # Sauvegarde de secours
        try:
            backup_path = output_path.replace('.csv', '_backup.txt')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write("=== TRANSACTIONS BNP PARIBAS (BACKUP) ===\n\n")
                for i, trans in enumerate(transactions):
                    f.write(f"Transaction {i+1}:\n")
                    for key, value in trans.items():
                        f.write(f"  {key}: {value}\n")
                    f.write("\n")
            print(f"💾 Sauvegarde de secours créée: {backup_path}")
        except Exception as backup_error:
            print(f"❌ Impossible de créer une sauvegarde: {backup_error}")

def test_parser():
    """Fonction de test du parser"""
    pdf_path = "RLV_CHQ_300040089500010220854_20230202.pdf"
    
    print("=== TEST DU PARSER BNP AMÉLIORÉ ===")
    parser = BnpParserImproved(pdf_path)
    transactions = parser.extract_transactions()
    
    if transactions:
        print(f"\n✅ Parsing réussi! {len(transactions)} transactions trouvées")
        save_to_csv_improved(transactions)
    else:
        print("\n❌ Aucune transaction extraite")
    
    return transactions

# Exemple d'utilisation
if __name__ == "__main__":
    test_parser()