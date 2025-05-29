import os
import google.generativeai as genai # type: ignore

def generate_mcq_with_gemini(
    text,
    number=5,
    subject=None,
    tone=None,
    response_format=None,
    gemini_api_key=None
):
    """
    Generate MCQs using Google Gemini API.

    Args:
        text (str): Source text for MCQ generation.
        number (int): Number of MCQs to generate.
        subject (str, optional): Subject for MCQs.
        tone (str, optional): Tone for MCQs.
        response_format (str, optional): Extra format instructions.
        gemini_api_key (str, optional): API key (overrides env).

    Returns:
        str: Gemini model response (JSON string).
    """
    # Prefer explicit key, fallback to env
    api_key = gemini_api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("No Gemini API key provided or found in environment.")
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    full_prompt = f"""
    Generate {number} multiple choice questions (MCQs) from the following text.
    Subject: {subject if subject else 'N/A'}
    Tone: {tone if tone else 'N/A'}
    Format your response as JSON with keys 'mcq', 'options', and 'correct'.
    {f"Response format: {response_format}" if response_format else ""}
    
    Text:
    {text}
    """
    response = model.generate_content(full_prompt)
    return response.text