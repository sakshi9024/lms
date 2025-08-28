import os
import pythoncom
import win32com.client
from docx2pdf import convert as docx2pdf_convert
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from PIL import Image
import pandas as pd

def convert_doc_to_pdf(input_path, output_path):
    pythoncom.CoInitialize()
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        doc = word.Documents.Open(input_path)
        doc.SaveAs(output_path, FileFormat=17)
        doc.Close()
    finally:
        word.Quit()
        pythoncom.CoUninitialize()

def convert_to_pdf(input_path, output_path):
    print("DEBUG convert:", input_path, "->", output_path)
    ext = os.path.splitext(input_path)[1].lower()

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if ext == ".pdf":
        with open(input_path, "rb") as src, open(output_path, "wb") as dst:
            dst.write(src.read())
    elif ext in [".doc", ".docx"]:
        convert_doc_to_pdf(os.path.abspath(input_path), os.path.abspath(output_path))
    elif ext == ".csv":
        df = pd.read_csv(input_path, skiprows=1)
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = [Paragraph("CSV Data", styles["Title"]), Spacer(1, 12)]
        data = [df.columns.tolist()] + df.astype(str).values.tolist()
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.grey),
            ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("BOTTOMPADDING", (0,0), (-1,0), 10),
            ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ]))
        elements.append(table)
        doc.build(elements)
    elif ext in [".jpg", ".jpeg", ".png"]:
        image = Image.open(input_path).convert("RGB")
        image.save(output_path, "PDF")
    else:
        raise ValueError(f"Unsupported format: {ext}")


# using LibreOffice


# import subprocess
# import os
# from PIL import Image


# def convert_to_pdf(input_file, output_dir):
#     """
#     Convert DOC, DOCX, CSV → PDF using LibreOffice.
#     Returns output file path.
#     """
#     try:
#         subprocess.run(
#             [
#                 "soffice",
#                 "--headless",
#                 "--convert-to", "pdf",
#                 "--outdir", output_dir,
#                 input_file
#             ],
#             check=True,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE
#         )
#         filename = os.path.splitext(os.path.basename(input_file))[0] + ".pdf"
#         return os.path.join(output_dir, filename)
#     except subprocess.CalledProcessError as e:
#         raise Exception(f"LibreOffice conversion failed: {e.stderr.decode('utf-8')}")


# def image_to_pdf(input_file, output_file):
#     """
#     Convert Image (JPG, PNG) → PDF using Pillow.
#     Returns output file path.
#     """
#     try:
#         image = Image.open(input_file)
#         if image.mode in ("RGBA", "P"):
#             image = image.convert("RGB")
#         image.save(output_file, "PDF", resolution=100.0)
#         return output_file
#     except Exception as e:
#         raise Exception(f"Image conversion failed: {str(e)}")
