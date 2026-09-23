# Certificate PDF - ReportLab/fpdf, fallback txt
import os
def make_certificate_pdf(name, event_title, token):
    base = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "qr")
    os.makedirs(base, exist_ok=True)
    path = os.path.join(base, f"cert_{token}.pdf")
    try:
        from fpdf import FPDF
        pdf = FPDF(orientation="L")
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 28)
        pdf.cell(0, 20, "Certificate of Participation", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 16)
        pdf.cell(0, 12, f"Proudly presented to {name}", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 12, f"for attending {event_title}", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 10, f"ID: {token} | College Events 2026", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.output(path)
    except Exception as ex:
        with open(path, "w") as f:
            f.write(f"Certificate: {name} attended {event_title} ({token}) err:{ex}")
    return path

def make_certificate(name, event_title):
    return make_certificate_pdf(name, event_title, "demo")
