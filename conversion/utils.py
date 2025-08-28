import os
import mimetypes
from docx2pdf import convert as docx2pdf_convert
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from PIL import Image
import pandas as pd





def convert_to_pdf(input_path, output_path):
    ext = os.path.splitext(input_path)[1].lower()

    if ext == ".pdf":
        # Already a PDF, just copy
        with open(input_path, "rb") as src, open(output_path, "wb") as dst:
            dst.write(src.read())

    elif ext == ".docx":
        # Convert Word .docx → PDF (Windows/Mac only)
        docx2pdf_convert(input_path, output_path)

    elif ext == ".doc":
        # docx2pdf does NOT support .doc (older Word)
        raise ValueError("The .doc format is not supported. Please convert it to .docx first.")

    elif ext == ".csv":
        # Convert CSV → PDF using pandas + reportlab
        try:
            df = pd.read_csv(input_path, skiprows=1)  # Skip comment line
        except Exception as e:
            raise ValueError(f"Error reading CSV: {e}")

        # Create PDF
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        elements.append(Paragraph("CSV Data", styles["Title"]))
        elements.append(Spacer(1, 12))

        data = [df.columns.tolist()] + df.values.tolist()

        # Convert all values to strings to avoid issues
        data = [[str(cell) for cell in row] for row in data]

        # Create the table
        table = Table(data, repeatRows=1)

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ]))

        elements.append(table)
        doc.build(elements)

    elif ext in [".jpg", ".jpeg", ".png"]:
        # Convert Image → PDF using Pillow
        image = Image.open(input_path)
        image = image.convert("RGB")  # Ensure it's in RGB
        image.save(output_path, "PDF")

    else:
        raise ValueError(f"Unsupported file format: {ext}")

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
