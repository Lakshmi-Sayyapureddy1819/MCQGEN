import os
import json
import traceback
import pandas as pd
import streamlit as st
from io import StringIO, BytesIO
from fpdf import FPDF
from dotenv import load_dotenv
from mcqgenerator.gemini_generator import generate_mcq_with_gemini
from mcqgenerator.utils import read_file, get_table_data

# --- Load environment variables ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Define the expected response format for Gemini ---
RESPONSE_JSON = """
{
  "1": {
    "mcq": "Sample question?",
    "options": {
      "a": "Option A",
      "b": "Option B",
      "c": "Option C",
      "d": "Option D"
    },
    "correct": "a"
  }
}
"""

# --- Custom CSS for advanced UI ---
st.markdown("""
    <style>
    body {
        background-color: #e0e7ef;
    }
    .stApp {
        background-image: linear-gradient(rgba(240,244,250,0.85), rgba(240,244,250,0.85)), 
            url('https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1500&q=80');
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    .main > div {
        background: rgba(255,255,255,0.82);
        border-radius: 18px;
        padding: 2.5rem;
        margin-top: 2rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.18);
        backdrop-filter: blur(7px);
        -webkit-backdrop-filter: blur(7px);
        border: 1px solid rgba(255,255,255,0.18);
    }
    .sidebar .sidebar-content {
        background: rgba(255,255,255,0.7);
    }
    .stButton>button {
        color: white;
        background: linear-gradient(90deg, #3b82f6 0%, #06b6d4 100%);
        border: none;
        border-radius: 8px;
        padding: 0.5em 1.5em;
        font-size: 1.1em;
        font-weight: 600;
        margin: 0.5em 0;
        transition: background 0.3s;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #06b6d4 0%, #3b82f6 100%);
    }
    </style>
""", unsafe_allow_html=True)

# --- Title with emoji and LangChain "logo" ---
st.markdown("""
    <h1 style='text-align: center; font-size: 2.8rem;'>
        🐦⛓️ <span style="color:#3b82f6;">MCQ Creator</span> with Gemini & LangChain
    </h1>
    <div style='text-align: center; font-size: 1.2rem; color: #444; margin-bottom: 1.5rem;'>
        Generate Multiple Choice Questions from your PDF or TXT files using <b>Google Gemini</b>.
    </div>
""", unsafe_allow_html=True)

# --- Sidebar for Inputs ---
with st.sidebar:
    st.header("Upload & Settings")
    uploaded_file = st.file_uploader("Upload a PDF or TXT file")
    mcq_count = st.number_input("Number of MCQs", min_value=3, max_value=50, value=5)
    subject = st.text_input("Subject", max_chars=20)
    tone = st.text_input("Complexity Level", max_chars=20, placeholder="Simple")
    button = st.button("Create MCQs")

generated_df = None

if button and uploaded_file and mcq_count and subject and tone:
    with st.spinner("Generating MCQs using Gemini..."):
        try:
            text = read_file(uploaded_file)
            quiz = generate_mcq_with_gemini(
                text=text,
                number=mcq_count,
                subject=subject,
                tone=tone,
                response_format=RESPONSE_JSON,
                gemini_api_key=GEMINI_API_KEY
            )
            if isinstance(quiz, str):
                st.write("Gemini raw output:", quiz)
                if quiz.strip() == "":
                    st.error("Gemini API returned an empty response.")
                    st.stop()
                try:
                    quiz = json.loads(quiz)
                except Exception as e:
                    st.error("Gemini API did not return valid JSON.")
                    st.write(quiz)
                    st.stop()
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            st.error("An error occurred while generating MCQs")
        else:
            st.write("Parsed quiz object:", quiz)
            table_data = get_table_data(quiz)
            if table_data:
                df = pd.DataFrame(table_data)
                df.index += 1
                st.success("MCQs generated successfully!")
                generated_df = df
            else:
                st.warning("No MCQs found in the response.")

# --- Tabs for Output and Downloads ---
if generated_df is not None:
    tab1, tab2 = st.tabs(["📋 MCQ Table", "📥 Download"])
    with tab1:
        st.markdown("### Your MCQs")
        st.dataframe(generated_df, use_container_width=True)
    with tab2:
        st.markdown("### Download Your MCQs")
        # CSV
        csv_buffer = StringIO()
        generated_df.to_csv(csv_buffer, index=False)
        st.download_button("Download as CSV", csv_buffer.getvalue(), file_name="quiz.csv", mime="text/csv")

        # Excel
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            generated_df.to_excel(writer, index=False, sheet_name='MCQs')
        st.download_button("Download as Excel", data=excel_buffer.getvalue(), file_name="quiz.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for idx, row in generated_df.iterrows():
            pdf.multi_cell(0, 10, f"Q{idx}. {row['MCQ']}")
            pdf.multi_cell(0, 10, f"Options: {row['Choices']}")
            pdf.multi_cell(0, 10, f"Answer: {row['Correct']}")
            pdf.ln()
        pdf_bytes = pdf.output(dest='S').encode('latin1')
        pdf_buffer = BytesIO(pdf_bytes)
        st.download_button("Download as PDF", data=pdf_buffer, file_name="quiz.pdf", mime="application/pdf")

# --- Footer ---
st.markdown(
    "<hr style='margin-top:2em;margin-bottom:1em;'>"
    "<div style='text-align:center;color:#888;font-size:1em;'>"
    "Made with 🐦⛓️ Gemini & LangChain | <a href='https://github.com/langchain-ai/langchain' target='_blank'>LangChain</a>"
    "</div>",
    unsafe_allow_html=True
)