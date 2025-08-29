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

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
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