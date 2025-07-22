
from fpdf import FPDF
import tempfile

def gerar_pdf_resumo(df):
    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 14)
            self.cell(0, 10, "Relatório VigiSolo", ln=True, align="C")

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", "", 12)

    total = len(df)
    locais = df['Localidade'].nunique()
    municipios = df['Município'].nunique()

    pdf.multi_cell(0, 10, f"Total de registros: {total}")
    pdf.multi_cell(0, 10, f"Número de localidades: {locais}")
    pdf.multi_cell(0, 10, f"Número de municípios: {municipios}")

    # Salvar PDF temporariamente
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp.name)
    return tmp.name
