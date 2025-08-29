# 🏦 PDF to CSV Bank Statement Converter

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/built%20with-Streamlit-FF4B4B.svg)](https://streamlit.io/)



Convertissez vos relevés bancaires PDF en fichiers CSV structurés avec une interface web intuitive.

## ✨ Fonctionnalités

- **🎯 Multi-banques** : Support de BNP Paribas, Société Générale, CIC, Crédit Mutuel, LCL
- **📄 PDF textuels & scannés** : Traitement avec OCR pour les documents scannés
- **🎨 Interface web** : Application Streamlit facile à utiliser
- **⚙️ Personnalisable** : Options de formatage CSV flexibles
- **📊 Statistiques** : Aperçu des données et analyses
- **🔍 Détection automatique** : Reconnaissance intelligente du type de banque

## 🚀 Installation rapide

### Via Docker (Recommandé)
```bash
docker-compose up
# Accéder à http://localhost:8501
```

### Via Python
```bash
# Cloner le dépôt
git clone https://github.com/nadirbouhallouf/pdf-to-csv-converter.git
cd pdf-to-csv-converter

# Installer les dépendances
pip install -r pdf_to_csv/requirements.txt

# Lancer l'application
cd pdf_to_csv && streamlit run main.py
```

## 📋 Prérequis

- Python 3.8+
- Tesseract OCR (pour les PDF scannés)

### Installation de Tesseract
- **Windows** : [Télécharger ici](https://github.com/UB-Mannheim/tesseract/wiki)
- **macOS** : `brew install tesseract`
- **Linux** : `sudo apt install tesseract-ocr`

## 🎯 Utilisation

1. **Lancer l'application** : `streamlit run pdf_to_csv/main.py`
2. **Uploader un PDF** : Glisser-déposer ou sélectionner un fichier
3. **Vérifier** : Consulter l'aperçu des données extraites
4. **Télécharger** : Récupérer le fichier CSV formaté

## 🏗️ Architecture

```
pdf_to_csv/
├── main.py                 # Application Streamlit principale
├── bank_parsers/          # Parsers spécifiques par banque
│   ├── bnp.py            # Parser BNP Paribas
│   ├── societe_generale.py  # Parser Société Générale
│   ├── cic.py            # Parser CIC
│   ├── credit_mutuel.py  # Parser Crédit Mutuel
│   └── lcl.py            # Parser LCL
├── utils/                 # Utilitaires
│   ├── ocr_utils.py      # OCR et prétraitement
│   └── date_utils.py     # Parsing de dates
└── requirements.txt      # Dépendances Python
```

## 🛠️ Développement

### Installation pour le développement
```bash
git clone https://github.com/nadirbouhallouf/pdf-to-csv-converter.git
cd pdf-to-csv-converter
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r pdf_to_csv/requirements.txt
pip install pytest flake8
```

### Tests
```bash
pytest tests/
```

### Linting
```bash
flake8 pdf_to_csv/
```

## 🤝 Contribution

Les contributions sont les bienvenues !

1. Fork le projet
2. Créez votre branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📄 Documentation

- [Guide d'installation détaillé](INSTALLATION_USAGE_GUIDE.md)
- [Guide de déploiement](DEPLOYMENT_CHECKLIST.md)
