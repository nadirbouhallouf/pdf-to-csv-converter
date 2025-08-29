FROM python:3.9-slim

# Installer Tesseract OCR et autres dépendances système
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-fra \
    libtesseract-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY pdf_to_csv/requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY pdf_to_csv/ ./pdf_to_csv/

# Exposer le port Streamlit
EXPOSE 8501

# Commande pour lancer l'application
CMD ["streamlit", "run", "pdf_to_csv/main.py", "--server.port=8501", "--server.address=0.0.0.0"]