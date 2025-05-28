import google.generativeai as genai
import os

def generate_mcq_with_gemini(text, prompt, number=5, subject=None, tone=None, response_format=None):
    model = genai.GenerativeModel("gemini-pro")
    
    # Compose the full prompt, including subject, tone, and response_format if provided
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