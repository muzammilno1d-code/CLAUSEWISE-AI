
from app.agents.property_extractor import extract_property_data
from app.services.ocr_service import extract_text_with_ocr

# Extract pages from the actual PDF
pages = extract_text_with_ocr("encum_samp.pdf")

# Combine page text while preserving page numbers
page_texts = []

for page in pages:
    page_texts.append(
        "--- Page " + str(page["page_number"]) + " ---\n"
        + page["text"]
    )

text = "\n".join(page_texts)

# Extract property information
result = extract_property_data(
    text,
    "Encumbrance Certificate Application / Copy"
)

print("\nSEARCH PERIOD:")
print(result["extracted_fields"]["search_period"])

print("\nFIELDS FOUND:")
print(result["extraction_summary"]["fields_found"])

print("\nALL EXTRACTED FIELDS:")

for field, details in result["extracted_fields"].items():
    if details["status"] == "FOUND":
        print(field, ":", details["value"])
