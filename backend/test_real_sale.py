
from app.agents.property_extractor import extract_property_data
from app.services.ocr_service import extract_text_with_ocr

pages = extract_text_with_ocr("sale_deedsamp.pdf")

page_texts = []

for page in pages:
    page_texts.append(
        "--- Page " + str(page["page_number"]) + " ---\n"
        + page["text"]
    )

text = "\n".join(page_texts)

result = extract_property_data(
    text,
    "Property Sale Agreement"
)

print("\nDOCUMENT TYPE:")
print(result["document_type"])

print("\nFIELDS FOUND:")
print(result["extraction_summary"]["fields_found"])

print("\nEXTRACTED FIELDS:")

for field, details in result["extracted_fields"].items():
    if details["status"] == "FOUND":
        print(field, ":", details["value"])
