"""
Streamlit UI — Simple file upload and extraction preview.
Run: streamlit run ui/app.py
"""
import streamlit as st
import requests
import json
from PIL import Image
import io

API_BASE = "http://localhost:8000/api/v1/documents"

st.set_page_config(
    page_title="DocExtract Platform",
    page_icon="📄",
    layout="wide",
)

st.title("📄 Intelligent Document Extraction Platform")
st.caption("Upload a document image → get structured data instantly using OCR + LLM")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    doc_type = st.selectbox(
        "Document Type",
        options=["aadhaar", "driving_licence", "passport", "invoice"],
        format_func=lambda x: x.replace("_", " ").title(),
    )

    FIELD_OPTIONS = {
        "aadhaar": ["name", "dob", "gender", "aadhaar_number", "address", "pincode"],
        "driving_licence": ["name", "dob", "licence_number", "issue_date", "expiry_date", "address", "vehicle_classes"],
        "passport": ["surname", "given_names", "nationality", "dob", "sex", "passport_number", "issue_date", "expiry_date"],
        "invoice": ["invoice_number", "invoice_date", "seller_name", "buyer_name", "items", "total_amount"],
    }

    selected_fields = st.multiselect(
        "Output Fields (leave empty = all fields)",
        options=FIELD_OPTIONS.get(doc_type, []),
    )

# ── Main area ─────────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📤 Upload Document")
    uploaded_file = st.file_uploader(
        "Drag & drop your document",
        type=["jpg", "jpeg", "png"],
        help="Supported: JPG, PNG",
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption=uploaded_file.name, use_column_width=True)

    if st.button("🚀 Extract Now", type="primary", disabled=not uploaded_file):
        with st.spinner("Running OCR + LLM extraction..."):
            uploaded_file.seek(0)
            files = {"file": (uploaded_file.name, uploaded_file.read(), uploaded_file.type)}
            data = {"document_type": doc_type}
            if selected_fields:
                data["output_fields"] = ",".join(selected_fields)

            try:
                response = requests.post(API_BASE + "/extract", files=files, data=data, timeout=120)
                if response.status_code == 201:
                    result = response.json()
                    st.session_state["last_result"] = result
                    st.success("✅ Extraction successful!")
                else:
                    st.error(f"❌ API Error {response.status_code}: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Make sure the FastAPI server is running on port 8000.")

with col2:
    st.subheader("📋 Extraction Result")
    if "last_result" in st.session_state:
        result = st.session_state["last_result"]
        st.markdown(f"**Document ID:** `{result['id']}`")
        st.markdown(f"**Status:** `{result['status']}`")
        st.markdown(f"**Type:** `{result['document_type']}`")

        if result.get("extracted_fields"):
            st.markdown("### 🗂️ Extracted Fields")
            fields = result["extracted_fields"]
            for key, value in fields.items():
                if isinstance(value, list):
                    st.markdown(f"**{key.replace('_', ' ').title()}:**")
                    for item in value:
                        st.markdown(f"  - {item}")
                else:
                    st.markdown(f"**{key.replace('_', ' ').title()}:** `{value}`")

            st.markdown("### 📦 Raw JSON")
            st.json(fields)
        elif result.get("error_message"):
            st.error(f"Extraction failed: {result['error_message']}")
    else:
        st.info("Upload a document and click **Extract Now** to see results here.")

# ── History ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🕓 Extraction History")
if st.button("🔄 Refresh History"):
    try:
        resp = requests.get(API_BASE + "/", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            st.markdown(f"**Total documents processed:** {data['total']}")
            for item in data["items"]:
                status_icon = "✅" if item["status"] == "success" else ("❌" if item["status"] == "failed" else "⏳")
                with st.expander(f"{status_icon} [{item['document_type']}] {item['filename']} (ID: {item['id']})"):
                    st.json(item.get("extracted_fields") or {"error": item.get("error_message")})
    except requests.exceptions.ConnectionError:
        st.warning("API not reachable.")
