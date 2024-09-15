import streamlit as st
import requests
import pandas as pd
import io
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Streamlit app configuration
st.set_page_config(page_title="Company Comparative Analysis", layout="wide")

# Custom CSS for enhanced styling
st.markdown("""
<style>
    .reportview-container {
        background: #f7f8fa;
    }
    .main {
        background: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    h1, h2, h3 {
        color: #0073e6;
        font-family: 'Arial', sans-serif;
    }
    .stButton>button {
        background-color: #0073e6;
        color: white;
        border-radius: 5px;
        font-weight: bold;
        padding: 0.5rem 1.5rem;
    }
    .stButton>button:hover {
        background-color: #005bb5;
    }
    .st-expander {
        border-radius: 5px;
        border: 1px solid #d1d9e6;
        margin-bottom: 10px;
    }
    .st-expander > div > div {
        background-color: #f1f3f5;
    }
</style>
""", unsafe_allow_html=True)

# App title
st.title("Company Comparative Analysis")

# File upload
uploaded_files = st.file_uploader("Upload exactly 4 PDF files", type="pdf", accept_multiple_files=True)

# API endpoint
API_ENDPOINT = "http://localhost:8000/analyze-companies/"

def parse_markdown_table(markdown_content):
    lines = markdown_content.strip().split('\n')
    headers = [header.strip() for header in lines[0].split('|')[1:-1]]
    data = []
    for line in lines[2:]:  # Skip the separator line
        if line.startswith('|'):
            row = [cell.strip() for cell in line.split('|')[1:-1]]
            if len(row) == len(headers):  # Ensure row matches headers
                data.append(row)
    return pd.DataFrame(data, columns=headers)

def create_excel_report(result):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book

        # Add a title format
        title_format = workbook.add_format({'bold': True, 'font_size': 14})
        header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#D9D9D9', 'border': 1})

        # Individual company analyses
        for company_name, analysis in result["individual_analyses"].items():
            df = parse_markdown_table(analysis)
            sheet_name = company_name[:31]  # Excel sheet names are limited to 31 characters
            df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=1, header=False)
            worksheet = writer.sheets[sheet_name]
            
            worksheet.write(0, 0, f"{company_name} Analysis", title_format)
            
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(1, col_num, value, header_format)
            
            for i, col in enumerate(df.columns):
                column_len = max(df[col].astype(str).map(len).max(), len(col))
                worksheet.set_column(i, i, column_len + 2)

        # Comparative analysis
        comp_df = parse_markdown_table(result["comparative_analysis"])
        
        if not comp_df.empty:
            comp_df.to_excel(writer, sheet_name='Company Comparison', index=False, startrow=1, header=False)
            comp_worksheet = writer.sheets['Company Comparison']
            
            comp_worksheet.write(0, 0, "Comparative Analysis", title_format)
            
            for col_num, value in enumerate(comp_df.columns.values):
                comp_worksheet.write(1, col_num, value, header_format)
            
            for i, col in enumerate(comp_df.columns):
                column_len = max(comp_df[col].astype(str).map(len).max(), len(col))
                comp_worksheet.set_column(i, i, column_len + 2)
        else:
            logger.warning("Comparative analysis table is empty")

    output.seek(0)
    return output

if uploaded_files and len(uploaded_files) == 4:
    files = [("files", (file.name, file.getvalue(), "application/pdf")) for file in uploaded_files]
    
    if st.button("Analyze Companies"):
        try:
            with st.spinner("Analyzing... This may take a few minutes."):
                response = requests.post(API_ENDPOINT, files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    logger.info("Analysis completed successfully")
                    
                    st.success("Analysis completed successfully!")
                    
                    st.header("Individual Company Analyses")
                    for company_name, analysis in result["individual_analyses"].items():
                        with st.expander(f"{company_name} Analysis"):
                            st.markdown(analysis)
                    
                    st.header("Comparative Analysis")
                    st.markdown(result["comparative_analysis"])
                    
                    excel_report = create_excel_report(result)
                    st.download_button(
                        label="Download Excel Report",
                        data=excel_report,
                        file_name="company_analysis_report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    logger.error(f"API Error: {response.status_code} - {response.text}")
                    st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            logger.exception(f"An error occurred: {str(e)}")
            st.error(f"An error occurred: {str(e)}")

elif uploaded_files:
    st.warning("Please upload exactly 4 PDF files.")
else:
    st.info("Please upload the PDF files to begin.")

# Instructions
st.markdown("---")
st.subheader("How to use this tool:")
st.write("""
1. Upload exactly 4 PDF files containing company information.
2. Click 'Analyze Companies' to start the analysis process.
3. View the individual and comparative analyses.
4. Download the Excel report for a detailed view.
""")

# Footer with company branding
st.markdown("---")
st.markdown("Powered by AI - Developed by YourCompany", unsafe_allow_html=True)