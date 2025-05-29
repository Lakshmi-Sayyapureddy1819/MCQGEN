import json
from PyPDF2 import PdfReader

def read_file(uploaded_file):
    if uploaded_file.name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8")
    elif uploaded_file.name.endswith(".pdf"):
        pdf = PdfReader(uploaded_file)
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
        return text
    else:
        return ""

def get_table_data(response_text_or_json):
    try:
        if isinstance(response_text_or_json, str):
            response_json = json.loads(response_text_or_json)
        else:
            response_json = response_text_or_json

        table = []
        for item in response_json.get("questions", []):
            question = item.get("question", "")
            options = item.get("options", [])
            answer = item.get("answer", "")

            option_str = ", ".join([f"{chr(65 + i)}. {opt}" for i, opt in enumerate(options)])
            table.append({
                "MCQ": question,
                "Choices": option_str,
                "Correct": answer
            })
        return table
    except Exception as e:
        print("Parsing error:", e)
        return None