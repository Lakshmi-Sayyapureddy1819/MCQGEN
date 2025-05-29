import google.generativeai as genai # type: ignore

def generate_mcq_with_gemini(text, number, subject, tone, response_format, gemini_api_key):
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('models/gemini-1.5-pro-latest')

    prompt = f"""
    Generate {number} MCQs on the subject '{subject}' with a '{tone}' tone.
    Format the output as JSON like this:
    {response_format}

    TEXT:
    {text}
    """

    response = model.generate_content(prompt)
    return response.text if hasattr(response, "text") else response