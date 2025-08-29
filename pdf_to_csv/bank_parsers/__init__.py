import pdfplumber
from pdf_to_csv.utils.ocr_utils import extract_text_from_scanned_pdf
from .societe_generale import SocieteGeneraleParser
from .cic import CicParser
from .credit_mutuel import CreditMutuelParser
from .lcl import LclParser
from .bnp import BnpParserImproved as BnpParser

def get_parser(pdf_path):
    """Détecte le type de relevé et retourne le parser approprié"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            first_page = pdf.pages[0]
            text = first_page.extract_text() or ""
            
            # Détection Société Générale
            if "SOCIETE GENERALE" in text or "Société Générale" in text:
                return SocieteGeneraleParser(pdf_path)
            
            # Détection CIC
            if "CIC" in text or "Banque CIC" in text:
                return CicParser(pdf_path)
            
            # Détection Crédit Mutuel
            if "CREDIT MUTUEL" in text or "Crédit Mutuel" in text:
                return CreditMutuelParser(pdf_path)
            
            # Détection LCL
            if "CREDIT LYONNAIS" in text or "Crédit Lyonnais" in text or "LCL" in text:
                return LclParser(pdf_path)
            
            # Détection BNP Paribas
            if "BNP PARIBAS" in text:
                return BnpParser(pdf_path)
                
            raise ValueError("Format de relevé non supporté")
            
    except Exception as e:
        # Handle scanned PDFs
        text = extract_text_from_scanned_pdf(pdf_path)
        if "SOCIETE GENERALE" in text or "Société Générale" in text:
            return SocieteGeneraleParser(pdf_path)
        elif "CIC" in text or "Banque CIC" in text:
            return CicParser(pdf_path)
        elif "CREDIT MUTUEL" in text or "Crédit Mutuel" in text:
            return CreditMutuelParser(pdf_path)
        elif "CREDIT LYONNAIS" in text or "Crédit Lyonnais" in text or "LCL" in text:
            return LclParser(pdf_path)
        elif "BNP PARIBAS" in text:
            return BnpParser(pdf_path)
            
        raise ValueError("Format de relevé non reconnu après OCR")
