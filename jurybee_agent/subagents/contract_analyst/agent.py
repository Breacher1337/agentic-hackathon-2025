from google.adk.agents import LlmAgent

from ..long_contract import long_contract
from ..short_contract import short_contract

import gdown, fitz, re, tempfile,os

def extract_text_from_gdrive_pdf_secure(gdrive_link: str) -> str:
    """
    Securely downloads a PDF from Google Drive, extracts all text, and returns it.
    Handles temp file permissions correctly on Windows and auto-cleans up.
    """
    # Extract the file ID from the Google Drive URL
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', gdrive_link)
    if not match:
        raise ValueError("Invalid Google Drive link format.")
    file_id = match.group(1)

    # Create a temp file path (file is not open, so gdown can write to it)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_path = temp_file.name
    temp_file.close()  # Close the file so Windows unlocks it

    try:
        # Download the PDF from Google Drive
        gdown.download(f"https://drive.google.com/uc?id={file_id}", temp_path, quiet=True)

        # Extract text using PyMuPDF
        text = ""
        with fitz.open(temp_path) as pdf:
            for page in pdf:
                text += page.get_text()

        return text

    finally:
        # Always delete the temp file afterward
        if os.path.exists(temp_path):
            os.remove(temp_path)


contract_analyst = LlmAgent(
    name='contract_analyst',
    model='gemini-2.0-flash',
    description="An agent that analyzes contracts by extracting text from PDFs.",
    instruction="""
        You are an expert contract analyst. Your primary function is to use the `extract_text_from_gdrive_pdf_secure` function to extract text from a PDF stored on Google Drive.


        ### PDF Contract Analysis Workflow

        
        **Upon Receiving the GDRIVE LINK:**
        1. **Use the `extract_text_from_gdrive_pdf_secure` function to extract text from the GDRIVE PDF**
            *this tool will securely download the PDF, extract all text, and return it as a string**

        2.  **Judge Contract Length and Route to `short_contract`:**
            * If text extraction was successful, determine the character length of the `extracted_text`.
            * **Regardless of length (since `long_contract` is not ready), you MUST route to the `short_contract` subagent.**
            * Pass the entire `extracted_text` and the original `user_query` to the `short_contract` subagent for analysis.
            * **Important:** If the text is actually long (>= 5000 chars), include a note in your final response to the user stating that it was processed using the short contract logic due to system limitations.

        3.  **Present Findings:**
            * Present the findings from the `short_contract` sub-agent in a clear, concise, and well-structured format. Your presentation should incorporate insights relevant to the `user_query` and include:
                * A summary of the key terms and purpose of the contract.
                * Identification of critical clauses such as: Parties involved, Term/Duration, Payment terms, Termination conditions, Confidentiality, Dispute resolution, Limitation of liability, Governing Law.
                * Highlighting of potential risks or important points related to the `user_query` or generally apparent.
                * A high-level summary of the contract's implications.

        4.  **Formatting:**
            * Use bullet points or numbered lists for summaries and key clauses to ensure readability.
    """,
    sub_agents=[short_contract, long_contract], # Keep both listed, but follow routing logic
    tools=[extract_text_from_gdrive_pdf_secure]
)