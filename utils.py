import os
import re
import pandas as pd
import joblib
import pythoncom
import win32com.client

from docx import Document
from pypdf import PdfReader


# Load trained model
model = joblib.load("artifacts/resume_classifier.pkl")


# DOCX extraction
def extract_docx(file_path):

    document = Document(file_path)

    text = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text.append(paragraph.text)

    for table in document.tables:
        for row in table.rows:

            row_text = []

            for cell in row.cells:
                if cell.text.strip():
                    row_text.append(cell.text.strip())

            if row_text:
                text.append(" ".join(row_text))

    return "\n".join(text)


# PDF extraction
def extract_pdf(file_path):

    reader = PdfReader(file_path)

    text = []

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text.append(page_text)

    return "\n".join(text)


# DOC extraction
def extract_doc(file_path):

    pythoncom.CoInitialize()

    word = None
    doc = None

    try:

        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False

        doc = word.Documents.Open(os.path.abspath(file_path))

        resume_text = doc.Content.Text

        return resume_text

    finally:

        if doc is not None:
            doc.Close(False)

        if word is not None:
            word.Quit()

        pythoncom.CoUninitialize()


# General resume extraction dispatcher
def extract_resume_text(file_path):

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".docx":

        resume_text = extract_docx(file_path)

    elif extension == ".pdf":

        resume_text = extract_pdf(file_path)

    elif extension == ".doc":

        resume_text = extract_doc(file_path)

    else:

        raise ValueError("Unsupported file format")

    if not resume_text.strip():

        raise ValueError("No text extracted from resume")

    return resume_text


# Text cleaning
def clean_resume(text):

    text = text.lower()

    text = re.sub(r'[^a-z\s]', ' ', text)

    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# Resume classification
def classify_resume(file_path):

    resume_text = extract_resume_text(file_path)

    cleaned_resume = clean_resume(resume_text)

    predicted_role = model.predict([cleaned_resume])[0]

    probabilities = model.predict_proba([cleaned_resume])[0]

    result = pd.DataFrame({
        "Job Role": model.classes_,
        "Probability": probabilities
    })

    result = result.sort_values(
        by="Probability",
        ascending=False
    ).reset_index(drop=True)

    return resume_text, predicted_role, result