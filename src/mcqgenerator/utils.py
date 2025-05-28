import os
import PyPDF2
import json
import traceback
from PyPDF2 import PdfReader
from io import BytesIO

def read_file(file):
    if file.name.endswith(".pdf"):
        try:
            pdf_reader = PdfReader(BytesIO(file.read()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise Exception("Error reading the PDF file: " + str(e))
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    else:
        raise Exception("Unsupported file format. Only PDF and TXT files are supported.")


def get_table_data(quiz):
    try:
        # If `quiz` is a JSON string, parse it
        if isinstance(quiz, str):
            quiz = json.loads(quiz)

        quiz_table_data = []
        for item in quiz:
            question = item.get("question", "N/A")
            options = item.get("options", [])
            answer = item.get("answer", "N/A")

            options_str = " | ".join(
                [f"{chr(65 + idx)}: {opt}" for idx, opt in enumerate(options)]
            )

            quiz_table_data.append({
                "MCQ": question,
                "Choices": options_str,
                "Correct": answer
            })

        return quiz_table_data
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return False
