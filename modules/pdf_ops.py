"""Módulo de operações com PDF para o PyRPA."""

import io

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False


class PDFOperations:

    def extract_text(self, pdf_file) -> dict:
        if not HAS_PYPDF2:
            return {"status": "Erro", "message": "Instale: pip install PyPDF2"}
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            text_parts = []
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"--- Página {i+1} ---\n{page_text}")
            return {"status": "Sucesso", "data": "\n\n".join(text_parts)}
        except Exception as e:
            return {"status": "Erro", "message": str(e)}

    def merge_pdfs(self, pdf_files: list) -> dict:
        if not HAS_PYPDF2:
            return {"status": "Erro", "message": "Instale: pip install PyPDF2"}
        try:
            merger = PyPDF2.PdfMerger()
            for f in pdf_files:
                merger.append(f)
            output = io.BytesIO()
            merger.write(output)
            merger.close()
            output.seek(0)
            return {"status": "Sucesso", "data": output.getvalue()}
        except Exception as e:
            return {"status": "Erro", "message": str(e)}

    def get_info(self, pdf_file) -> dict:
        if not HAS_PYPDF2:
            return {"status": "Erro", "message": "Instale: pip install PyPDF2"}
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            meta = reader.metadata
            info = {
                "páginas": len(reader.pages),
                "título": str(meta.title) if meta and meta.title else "N/A",
                "autor": str(meta.author) if meta and meta.author else "N/A",
                "criador": str(meta.creator) if meta and meta.creator else "N/A",
                "criptografado": reader.is_encrypted,
            }
            return {"status": "Sucesso", "data": info}
        except Exception as e:
            return {"status": "Erro", "message": str(e)}

    def generate_script(self, action: str) -> str:
        scripts = {
            "Extrair texto": '''"""Extrair texto de PDF — gerado pelo PyRPA."""
import PyPDF2

def extrair_texto(caminho: str) -> str:
    with open(caminho, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        texto = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                texto.append(t)
    return "\\n".join(texto)

if __name__ == "__main__":
    print(extrair_texto("documento.pdf"))
''',
            "Mesclar": '''"""Mesclar múltiplos PDFs — gerado pelo PyRPA."""
import PyPDF2
import glob

def mesclar_pdfs(padrao: str, saida: str = "merged.pdf"):
    merger = PyPDF2.PdfMerger()
    for pdf in sorted(glob.glob(padrao)):
        print(f"Adicionando: {pdf}")
        merger.append(pdf)
    merger.write(saida)
    merger.close()
    print(f"Mesclado em: {saida}")

if __name__ == "__main__":
    mesclar_pdfs("*.pdf", "resultado.pdf")
''',
            "Dividir": '''"""Dividir PDF em páginas individuais — gerado pelo PyRPA."""
import PyPDF2

def dividir_pdf(caminho: str, pasta_saida: str = "paginas"):
    import os; os.makedirs(pasta_saida, exist_ok=True)
    with open(caminho, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for i, page in enumerate(reader.pages, 1):
            writer = PyPDF2.PdfWriter()
            writer.add_page(page)
            out = os.path.join(pasta_saida, f"pagina_{i:03d}.pdf")
            with open(out, "wb") as out_f:
                writer.write(out_f)
            print(f"Página {i} salva em {out}")

if __name__ == "__main__":
    dividir_pdf("documento.pdf")
''',
            "Converter para imagem": '''"""Converter PDF para imagens — gerado pelo PyRPA.
Dependência: pip install pdf2image
No Linux: sudo apt install poppler-utils
No Windows: instalar poppler e adicionar ao PATH
"""
from pdf2image import convert_from_path

def pdf_para_imagens(caminho: str, dpi: int = 200, pasta: str = "imagens"):
    import os; os.makedirs(pasta, exist_ok=True)
    imagens = convert_from_path(caminho, dpi=dpi)
    for i, img in enumerate(imagens, 1):
        out = os.path.join(pasta, f"pagina_{i:03d}.png")
        img.save(out, "PNG")
        print(f"Salvo: {out}")

if __name__ == "__main__":
    pdf_para_imagens("documento.pdf")
''',
            "OCR": '''"""OCR em PDF escaneado — gerado pelo PyRPA.
Dependências: pip install pytesseract pdf2image Pillow
Sistema: sudo apt install tesseract-ocr poppler-utils
"""
import pytesseract
from pdf2image import convert_from_path

def ocr_pdf(caminho: str, idioma: str = "por") -> str:
    imagens = convert_from_path(caminho, dpi=300)
    texto_completo = []
    for i, img in enumerate(imagens, 1):
        texto = pytesseract.image_to_string(img, lang=idioma)
        texto_completo.append(f"--- Página {i} ---\\n{texto}")
        print(f"Página {i} processada")
    return "\\n\\n".join(texto_completo)

if __name__ == "__main__":
    resultado = ocr_pdf("documento_escaneado.pdf")
    with open("texto_ocr.txt", "w", encoding="utf-8") as f:
        f.write(resultado)
    print("OCR concluído!")
''',
        }
        return scripts.get(action, "# Ação não reconhecida")
