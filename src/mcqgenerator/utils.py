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

def get_table_data(quiz):
    table = []
    for qid, entry in quiz.items():
        mcq = entry.get("mcq", "")
        options = " | ".join([f"{k}: {v}" for k, v in entry.get("options", {}).items()])
        correct = entry.get("correct", "")
        table.append({"MCQ": mcq, "Choices": options, "Correct": correct})
    return table

# Example usage with the suggested code change
quiz_data = {
    "1": {
        "mcq": "What is ...?",
        "options": {"a": "...", "b": "...", "c": "...", "d": "..."},
        "correct": "a"
    }
}

table_data = get_table_data(quiz_data)
print(table_data)