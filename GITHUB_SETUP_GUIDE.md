# Guide de Préparation pour GitHub

## 🚀 Préparation du dépôt GitHub

### 1. Créer les fichiers nécessaires

#### .gitignore
Créez un fichier `.gitignore` avec le contenu suivant :

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Environnements virtuels
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Fichiers temporaires
*.tmp
*.temp
temp.pdf
*.log

# Données sensibles
*.pdf
!examples/*.pdf
.env
.env.local

# Streamlit
.streamlit/
```

#### LICENSE
Créez un fichier `LICENSE` avec la licence MIT :

```
MIT License

Copyright (c) 2024 PDF to CSV Converter

Par les présentes, l’autorisation est concédée, à titre gratuit, à toute personne obtenant une copie du présent logiciel et des fichiers de documentation associés (ci-après le « Logiciel »), de traiter le Logiciel sans restriction, y compris, sans que cette énumération soit limitative, les droits d’utiliser, de copier, de modifier, de fusionner, de publier, de distribuer, de sous-licencier et/ou de vendre des copies du Logiciel, ainsi que d’autoriser les personnes auxquelles le Logiciel est fourni à le faire, sous réserve des conditions suivantes :

L’avis de droit d’auteur ci-dessus et le présent avis d’autorisation devront être inclus dans toutes copies ou parties substantielles du Logiciel.

LE LOGICIEL EST FOURNI « EN L’ÉTAT », SANS GARANTIE D’AUCUNE SORTE, EXPRESSE OU IMPLICITE, Y COMPRIS, MAIS SANS S’Y LIMITER, LES GARANTIES RELATIVES À LA QUALITÉ MARCHANDE, À L’ADÉQUATION À UN USAGE PARTICULIER ET À L’ABSENCE DE CONTREFAÇON. EN AUCUN CAS LES AUTEURS OU LES TITULAIRES DES DROITS D’AUTEUR NE POURRONT ÊTRE TENUS RESPONSABLES DE TOUTE RÉCLAMATION, DOMMAGE OU AUTRE RESPONSABILITÉ, QU’IL S’AGISSE D’UNE ACTION CONTRACTUELLE, DÉLICTUELLE OU AUTRE, RÉSULTANT DU LOGICIEL OU DE L’UTILISATION OU D’AUTRES RELATIONS AVEC LE LOGICIEL.
```

### 2. Structure du dépôt GitHub

```
pdf-to-csv-converter/
├── .github/
│   └── workflows/
│       └── python-app.yml
├── pdf_to_csv/
│   ├── bank_parsers/
│   ├── utils/
│   ├── main.py
│   ├── requirements.txt
│   └── README.md
├── examples/
│   └── sample_pdfs/
├── tests/
├── .gitignore
├── LICENSE
├── README.md
├── INSTALLATION_USAGE_GUIDE.md
└── setup.py
```

### 3. GitHub Actions Workflow

Créez `.github/workflows/python-app.yml` :

```yaml
name: Python application

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.9
      uses: actions/setup-python@v3
      with:
        python-version: 3.9
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r pdf_to_csv/requirements.txt
        pip install pytest
        
    - name: Lint with flake8
      run: |
        pip install flake8
        flake8 pdf_to_csv --count --select=E9,F63,F7,F82 --show-source --statistics
        
    - name: Test with pytest
      run: |
        pytest tests/ -v
```

### 4. README.md amélioré pour GitHub

```markdown
# 🏦 PDF to CSV Bank Statement Converter

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/built%20with-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Convertissez vos relevés bancaires PDF en fichiers CSV structurés avec une interface web intuitive.

## ✨ Fonctionnalités

- **🎯 Multi-banques** : Support de BNP Paribas, Société Générale, CIC