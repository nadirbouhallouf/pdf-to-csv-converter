import pytesseract
from pdf2image import convert_from_path
import tempfile
import os
import cv2
import numpy as np

def extract_text_from_scanned_pdf(pdf_path, lang='fra'):
    """Extrait le texte d'un PDF scanné en utilisant OCR"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Conversion PDF en images
        images = convert_from_path(pdf_path, output_folder=temp_dir)
        
        full_text = ""
        
        for i, image in enumerate(images):
            # Prétraitement de l'image pour améliorer l'OCR
            img = preprocess_image(image)
            
            # Extraction du texte avec Tesseract
            text = pytesseract.image_to_string(img, lang=lang)
            full_text += f"\n--- Page {i+1} ---\n{text}\n"
            
    return full_text

def preprocess_image(image):
    """Améliore la qualité de l'image pour l'OCR"""
    # Conversion en numpy array
    img = np.array(image)
    
    # Conversion en niveaux de gris
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Seuillage adaptatif
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    
    return thresh
