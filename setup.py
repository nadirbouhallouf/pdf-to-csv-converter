from setuptools import setup, find_packages

setup(
    name="pdf_to_csv",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'pdfplumber',
        'pandas',
        'streamlit',
        'python-dateutil'
    ],
    python_requires='>=3.8',
)
