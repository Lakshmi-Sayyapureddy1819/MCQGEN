import google.generativeai as genai # type: ignore
import re
import json
from io import BytesIO
from fpdf import FPDF

def generate_mcq_with_gemini(text, number, subject, tone, response_format, gemini_api_key):
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('models/gemini-1.5-pro-latest')

    prompt = f"""
    Generate {number} MCQs on the subject '{subject}' with a '{tone}' tone.
    Return ONLY valid JSON in this format, no explanation, no markdown:

    {{
      "1": {{
        "mcq": "Sample question?",
        "options": {{
          "a": "Option A",
          "b": "Option B",
          "c": "Option C",
          "d": "Option D"
        }},
        "correct": "a"
      }}
    }}

    TEXT:
    {text}
    """

    response = model.generate_content(prompt)
    quiz = response.text if hasattr(response, "text") else response

    if isinstance(quiz, str):
        print("Gemini raw output:", quiz)
        if quiz.strip() == "":
            print("Gemini API returned an empty response.")
            return None
        # Try to extract JSON object from the response
        match = re.search(r"\{[\s\S]*\}", quiz)
        if match:
            quiz_json_str = match.group(0)
            try:
                quiz = json.loads(quiz_json_str)
            except Exception as e:
                print("Gemini API did not return valid JSON (even after extraction).")
                print(quiz_json_str)
                return None
        else:
            print("Could not find JSON object in Gemini response.")
            print(quiz)
            return None

    return quiz

def download_quiz_as_pdf(quiz):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", size=12)

    for index, question in enumerate(quiz.get("questions", []), start=1):
        pdf.multi_cell(0, 10, f"Q{index}: {question.get('question', '')}")
        for option in question.get("options", []):
            pdf.multi_cell(0, 10, f"- {option}")
        pdf.ln()

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_buffer = BytesIO(pdf_bytes)
    return pdf_buffer.getvalue()