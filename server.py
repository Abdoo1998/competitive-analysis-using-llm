from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import List
import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import  ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

#load openai api key from .env file
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

llm=ChatOpenAI(model="gpt-4-turbo",temperature=0,api_key=OPENAI_API_KEY)
def process_pdf(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
    return texts

def analyze_company(company_name: str, company_data: str) -> str:
    prompt = PromptTemplate(
        input_variables=["company_name", "company_data"],
        template="""
Analyze the following data for {company_name}. Provide a concise summary covering:
1. Financial Performance
2. Market Position
3. Operational Efficiency
4. Innovation and R&D
5. Key Strengths and Weaknesses

Data:
{company_data}

Provide a brief analysis in the following markdown table format:

| Category | Analysis |
| --- | --- |
| Financial Performance | (analysis here) |
| Market Position | (analysis here) |
| Operational Efficiency | (analysis here) |
| Innovation and R&D | (analysis here) |
| Key Strengths | (analysis here) |
| Key Weaknesses | (analysis here) |

Ensure that the table is properly formatted with the | character at the start and end of each row, and that the separator row (| --- | --- |) is included.

Analysis:
"""
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run(company_name=company_name, company_data=company_data[:100000])  # Limit input to 100k characters

def compare_companies(company_analyses: dict) -> str:
    prompt = PromptTemplate(
        input_variables=["analyses"],
        template="""
Compare the following companies based on their individual analyses:

{analyses}

Provide a comprehensive comparative analysis in the following markdown table format:

| Category | Company A  | Company B | Company C | Company D |
| Financial Performance | (analysis) | (analysis) | (analysis) | (analysis) |
| Market Position | (analysis) | (analysis) | (analysis) | (analysis) |
| Operational Efficiency | (analysis) | (analysis) | (analysis) | (analysis) |
| Innovation and R&D | (analysis) | (analysis) | (analysis) | (analysis) |
| Key Strengths | (analysis) | (analysis) | (analysis) | (analysis) |
| Key Weaknesses | (analysis) | (analysis) | (analysis) | (analysis) |
Ensure that the table is properly formatted with the | character at the start and end of each row, and that the separator row (| --- | --- | --- | --- | --- |) is included.

Then, provide strategic recommendations for (Company A) in a separate markdown table:

| Recommendation | Description |
| Recommendation 1 | (description) |
| Recommendation 2 | (description) |
| Recommendation 3 | (description) |

Again, ensure that this table is properly formatted with the | character at the start and end of each row, and that the separator row (| --- | --- |) is included.

Comparative Analysis:
"""
    )
    analyses_text = "\n\n".join([f"{name}:\n{analysis}" for name, analysis in company_analyses.items()])
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run(analyses=analyses_text)

@app.post("/analyze-companies/")
async def analyze_companies(
    files: List[UploadFile] = File(...)
):
    if len(files) != 4:
        raise HTTPException(status_code=400, detail="Exactly 4 PDF files are required")

    company_data = {}
    company_names = ["Company A ", "Company B", "Company C", "Company D"]

    # Process PDF files
    for file, company_name in zip(files, company_names):
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail=f"File {file.filename} must be a PDF")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        texts = process_pdf(temp_file_path)
        company_data[company_name] = "\n".join([doc.page_content for doc in texts])

        os.unlink(temp_file_path)

    try:
        logger.debug("Analyzing individual companies...")
        company_analyses = {}
        for company_name, data in company_data.items():
            company_analyses[company_name] = analyze_company(company_name, data)
        
        logger.debug("Performing comparative analysis...")
        comparative_analysis = compare_companies(company_analyses)

        return {
            "message": "Analysis completed successfully",
            "individual_analyses": company_analyses,
            "comparative_analysis": comparative_analysis
        }
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during analysis: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)