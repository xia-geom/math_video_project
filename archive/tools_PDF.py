from pypdf import PdfReader, PdfWriter

# Files
input_pdf = "F-1021_02-2022_dynamique.pdf"
output_pdf = "F1021_MAT0339_Xia_Xiao.pdf"

# Mapping your Plan de cours data
data = {
    "Cours code": "MAT0339",
    "Groupe": "040",
    "Trimestre": "Hiver 2026",
    "Titre du cours": "Mathématiques générales",
    "Département ou faculté": "Département de mathématiques",
    "NOMBRE": "1\n1\n-",
    "FORME ET OBJET DE LÉVALUATION": "Examen intra (mi-session)\nExamen final\nPrésence aux cours",
    "ÉCHÉANCE": "18 février\n29 avril\nTout le trimestre",
    "PONDÉRATION": "47,5 % *\n47,5 % *\n5 %",
    "AUTRES DISPOSITIONS À INCLURE À L'ENTENTE": (
        "FORMULE DE CALCUL DE LA NOTE FINALE :\n"
        "Note = 5% (Présence) + 47,5% (Final) + 47,5% * max(Intra, Final).\n\n"
        "* Note : Si le résultat de l'examen final est supérieur à l'intra, "
        "la pondération de l'intra est transférée au final (le final vaut alors 95%)."
    ),
    "aaaa/mm/dd": "2026/01/14",
    "Professeur-e ou chargé-e de cours": "Xia Xiao",
}

def generate_uqam_form():
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    # 1. Copy the page
    page = reader.pages[0]
    writer.add_page(page)

    # 2. IMPORTANT: Copy the AcroForm structural metadata from reader to writer
    # This resolves the "No /AcroForm dictionary" error
    if reader.trailer.get("/Root", {}).get("/AcroForm"):
        writer._root_object.update({
            "/AcroForm": reader.trailer["/Root"]["/AcroForm"]
        })

    # 3. Fill the fields
    writer.update_page_form_field_values(writer.pages[0], data)

    with open(output_pdf, "wb") as output_stream:
        writer.write(output_stream)
    
    print(f"File '{output_pdf}' generated successfully.")

if __name__ == "__main__":
    generate_uqam_form()