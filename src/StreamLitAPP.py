import os
import sys
import json
import traceback
import pandas as pd
import streamlit as st
from io import StringIO, BytesIO
from fpdf import FPDF
from dotenv import load_dotenv
from mcqgenerator.gemini_generator import generate_mcq_with_gemini

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from mcqgenerator.utils import read_file, get_table_data

load_dotenv()
with open('response.json', 'r') as file:
    RESPONSE_JSON = json.load(file)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="MCQ Creator with Gemini", layout="centered")
st.title("MCQ Creator Application with Gemini API")

with st.form("user_inputs"):
    uploaded_file = st.file_uploader("Upload a PDF or TXT file")
    mcq_count = st.number_input("Number of MCQs", min_value=3, max_value=50)
    subject = st.text_input("Insert Subject", max_chars=20)
    tone = st.text_input("Complexity level of Questions", max_chars=20, placeholder="Simple")
    button = st.form_submit_button("Create MCQs")

    if button and uploaded_file is not None and mcq_count and subject and tone:
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
                    st.write("Gemini raw output:", quiz)  # Debug output
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
                table_data = get_table_data(quiz)
                if table_data:
                    df = pd.DataFrame(table_data)
                    df.index += 1
                    st.dataframe(df)

                    csv_buffer = StringIO()
                    df.to_csv(csv_buffer, index=False)
                    st.download_button("Download as CSV", csv_buffer.getvalue(), file_name="quiz.csv", mime="text/csv")

                    excel_buffer = BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False, sheet_name='MCQs')
                    st.download_button("Download as Excel", data=excel_buffer.getvalue(), file_name="quiz.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    for idx, row in df.iterrows():
                        pdf.multi_cell(0, 10, f"Q{idx}. {row['MCQ']}")
                        pdf.multi_cell(0, 10, f"Options: {row['Choices']}")
                        pdf.multi_cell(0, 10, f"Answer: {row['Correct']}")
                        pdf.ln()

                    pdf_buffer = BytesIO()
                    pdf.output(pdf_buffer)
                    st.download_button("Download as PDF", data=pdf_buffer.getvalue(), file_name="quiz.pdf", mime="application/pdf")
                else:
                    st.error("Failed to parse quiz data into table format.")