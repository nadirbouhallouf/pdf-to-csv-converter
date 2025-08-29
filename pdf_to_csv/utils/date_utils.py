import dateparser
from datetime import datetime

def parse_date(date_str):
    """Convertit une chaîne de date en objet datetime"""
    # Gestion des dates au format JJ/MM (on suppose l'année courante)
    if len(date_str.split('/')) == 2:
        date_str = f"{date_str}/{datetime.now().year}"
    
    # Utilisation de dateparser pour gérer différents formats
    date = dateparser.parse(date_str, languages=['fr'], date_formats=['%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y'])
    if not date:
        raise ValueError(f"Format de date non reconnu: {date_str}")
    
    return date

def format_date(date, format='%d/%m/%Y'):
    """Formate une date selon le format spécifié"""
    return date.strftime(format)
