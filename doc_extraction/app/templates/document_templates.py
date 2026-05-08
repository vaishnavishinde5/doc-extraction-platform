"""
Template-based extraction: each document type defines its expected fields
and a prompt hint for the LLM.
"""
from typing import Dict, List
from dataclasses import dataclass, field


@dataclass
class DocumentTemplate:
    doc_type: str
    fields: List[str]                # all extractable fields
    llm_prompt_hint: str             # tells LLM what to look for


TEMPLATES: Dict[str, DocumentTemplate] = {
    "aadhaar": DocumentTemplate(
        doc_type="aadhaar",
        fields=["name", "dob", "gender", "aadhaar_number", "address", "pincode"],
        llm_prompt_hint=(
            "This is an Aadhaar Card. Extract: name, date of birth, gender, "
            "12-digit Aadhaar number, full address, and pincode."
        ),
    ),
    "driving_licence": DocumentTemplate(
        doc_type="driving_licence",
        fields=["name", "dob", "licence_number", "issue_date", "expiry_date",
                "address", "vehicle_classes"],
        llm_prompt_hint=(
            "This is an Indian Driving Licence. Extract: name, date of birth, "
            "licence number, issue date, expiry date, address, and vehicle classes authorized."
        ),
    ),
    "passport": DocumentTemplate(
        doc_type="passport",
        fields=["surname", "given_names", "nationality", "dob", "sex",
                "passport_number", "issue_date", "expiry_date", "place_of_birth",
                "place_of_issue", "mrz_line1", "mrz_line2"],
        llm_prompt_hint=(
            "This is a Passport. Extract: surname, given names, nationality, "
            "date of birth, sex, passport number, issue date, expiry date, "
            "place of birth, place of issue, and both MRZ lines."
        ),
    ),
    "invoice": DocumentTemplate(
        doc_type="invoice",
        fields=["invoice_number", "invoice_date", "seller_name", "seller_address",
                "buyer_name", "buyer_address", "items", "subtotal",
                "tax", "total_amount", "payment_terms"],
        llm_prompt_hint=(
            "This is an Invoice. Extract: invoice number, invoice date, "
            "seller name & address, buyer name & address, line items with quantities "
            "and prices, subtotal, tax amount, total amount, and payment terms."
        ),
    ),
}


def get_template(doc_type: str) -> DocumentTemplate:
    template = TEMPLATES.get(doc_type.lower())
    if not template:
        raise ValueError(f"No template found for document type: {doc_type}")
    return template
