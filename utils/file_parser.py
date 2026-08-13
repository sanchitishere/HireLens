try:
    from pypdf import PdfReader
    import docx
except ImportError:
    pass

def extract_text_from_file(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        try:
            reader = PdfReader(uploaded_file)
            text = "".join(page.extract_text() for page in reader.pages if page.extract_text())
            return text[:4000]
        except Exception:
            return ""
    elif uploaded_file.name.endswith(".docx"):
        try:
            doc = docx.Document(uploaded_file)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text[:4000]
        except Exception:
            return ""
    return ""
