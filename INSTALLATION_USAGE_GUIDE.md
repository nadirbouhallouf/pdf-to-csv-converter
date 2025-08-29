# Guide d'Installation et d'Utilisation - Convertisseur PDF Bancaire vers CSV

## 📋 Vue d'ensemble

Cette application est un convertisseur intelligent de relevés bancaires PDF vers des fichiers CSV structurés. Elle supporte plusieurs banques françaises et peut traiter à la fois les PDF textuels et les PDF scannés via OCR.

### 🏦 Banques supportées
- **BNP Paribas** - Parser optimisé avec détection de sections
- **Société Générale** - Support complet des relevés classiques
- **CIC** - Banque CIC et Crédit Industriel et Commercial
- **Crédit Mutuel** - Relevés Crédit Mutuel
- **LCL** - Crédit Lyonnais et LCL

### ✨ Fonctionnalités principales
- **Interface web intuitive** avec Streamlit
- **Support OCR** pour PDF scannés
- **Détection automatique** du type de banque
- **Options de formatage CSV** personnalisables
- **Aperçu des données** avant export
- **Statistiques** des transactions

## 🚀 Installation

### Prérequis système
- **Python 3.8 ou supérieur**
- **Système d'exploitation** : Windows, macOS ou Linux
- **Connexion internet** pour l'installation des dépendances

### Étape 1 : Installation de Python
Si Python n'est pas installé :
- **Windows** : Télécharger depuis [python.org](https://www.python.org/downloads/)
- **macOS** : `brew install python3` (via Homebrew)
- **Linux** : `sudo apt install python3 python3-pip`

### Étape 2 : Installation de Tesseract OCR (requis pour les PDF scannés)

#### Windows
1. Télécharger Tesseract depuis : https://github.com/UB-Mannheim/tesseract/wiki
2. Exécuter l'installateur et suivre les instructions
3. Ajouter Tesseract au PATH système si nécessaire

#### macOS
```bash
brew install tesseract
```

#### Linux
```bash
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
```

### Étape 3 : Cloner le projet
```bash
git clone [URL_DU_REPO]
cd PDF_CSV_ACCOUNT_STATEMENT
```

### Étape 4 : Installation des dépendances Python

#### Option A : Installation standard
```bash
cd pdf_to_csv
pip install -r requirements.txt
```

#### Option B : Installation via setup.py
```bash
pip install -e .
```

#### Option C : Installation dans un environnement virtuel (recommandé)
```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

## 📦 Dépendances principales

| Package | Version | Description |
|---------|---------|-------------|
| streamlit | 1.32.0 | Interface web |
| pdfplumber | 0.10.3 | Extraction de texte PDF |
| pandas | 2.1.0 | Manipulation de données |
| pypdf | 3.17.4 | Alternative pour PDF |
| pytesseract | 0.3.10 | OCR pour PDF scannés |
| pdf2image | 1.16.3 | Conversion PDF en images |
| python-dateutil | 2.8.2 | Parsing de dates |
| dateparser | 1.1.8 | Parsing de dates intelligent |
| openpyxl | 3.1.2 | Support Excel |

## 🎯 Utilisation

### Méthode 1 : Interface Web (Recommandée)

1. **Lancer l'application** :
```bash
cd pdf_to_csv
streamlit run main.py
```

2. **Accéder à l'interface** :
   - L'application s'ouvre automatiquement dans votre navigateur
   - URL par défaut : `http://localhost:8501`

3. **Utiliser l'application** :
   - Cliquer sur "Browse files" ou glisser-déposer un PDF
   - Attendre l'analyse automatique
   - Vérifier l'aperçu des données
   - Configurer les options CSV si nécessaire
   - Télécharger le fichier CSV

### Méthode