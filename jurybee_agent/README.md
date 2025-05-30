# JuryBee Legal Multi-agent tool

This repository is for GENAI Hackaton and it is a legal multi-agent tool for JuryBee. The tool is designed to analyze contacts and provide low-level legal advice to users.

## Getting Started

### Setup Environment

You only need to create one virtual environment for all examples in this course. Follow these steps to set it up:

```bash
# Create virtual environment in the root directory
python -m venv .venv

# Activate (each new terminal)
# macOS/Linux:
source .venv/bin/activate
# Windows CMD:
.venv\Scripts\activate.bat
# Windows PowerShell:
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

Once set up, this single environment will work for all examples in the repository.

### Setting Up API Keys

1. Create an account in Google Cloud https://cloud.google.com/?hl=en
2. Create a new project
3. Go to https://aistudio.google.com/apikey
4. Create an API key
5. Assign key to the project
6. Connect to a billing account
7. Navigate to the jurybee_agent folder
8. Rename `.env.example` to `.env`
9. Open the `.env` file and replace the placeholder with your API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

### Setting Up for RAG

1. Rename `.env.example` to `.env`
2. Open the `.env` file and replace the placeholder with your googlecloud information
3. run the prepare_corpus_data.py script to prepare the corpus data

## Official Documentation

For more detailed information, check out the official ADK documentation:

- https://google.github.io/adk-docs/get-started/quickstart
- [Vertex AI RAG Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-overview)
- [Google Agent Development Kit (ADK) Documentation](https://github.com/google/agents-framework)
- [Google Cloud Authentication Guide](https://cloud.google.com/docs/authentication)
