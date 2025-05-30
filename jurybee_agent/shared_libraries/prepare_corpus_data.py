from google.auth import default
import vertexai
from vertexai.preview import rag
import os
from dotenv import load_dotenv, set_key
import json 
import tempfile

from ..config import (
    DEFAULT_EMBEDDING_MODEL
)

load_dotenv()


PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
if not PROJECT_ID:
    raise ValueError(
        "GOOGLE_CLOUD_PROJECT environment variable not set. Please set it in your .env file."
    )
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
if not LOCATION:
    raise ValueError(
        "GOOGLE_CLOUD_LOCATION environment variable not set. Please set it in your .env file."
    )

CORPUS_DISPLAY_NAME = "CUADv1_corpus" 
CORPUS_DESCRIPTION = "Corpus containing data from the CUADv1 dataset"
CUAD_JSON_FILENAME = "CUAD_v1.json" 
ENV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env")) 

def initialize_vertex_ai():
    credentials, _ = default()
    vertexai.init(
        project=PROJECT_ID, location=LOCATION, credentials=credentials
    )

def create_or_get_corpus():
    """Creates a new corpus or retrieves an existing one."""
    embedding_model_config = rag.EmbeddingModelConfig(
        publisher_model=DEFAULT_EMBEDDING_MODEL
    )
    existing_corpora = rag.list_corpora()
    corpus = None
    for existing_corpus in existing_corpora:
        if existing_corpus.display_name == CORPUS_DISPLAY_NAME:
            corpus = existing_corpus
            print(f"Found existing corpus with display name '{CORPUS_DISPLAY_NAME}'")
            break
    if corpus is None:
        corpus = rag.create_corpus(
            display_name=CORPUS_DISPLAY_NAME,
            description=CORPUS_DESCRIPTION,
            embedding_model_config=embedding_model_config,
        )
        print(f"Created new corpus with display name '{CORPUS_DISPLAY_NAME}'")
    return corpus

def load_cuad_json_data(json_path):
    """Loads and extracts context text from CUADv1 JSON."""
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"CUAD JSON file not found at: {json_path}")

    print(f"Loading data from {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    extracted_contexts = []
    
    for article in data['data']:
        for paragraph in article['paragraphs']:
            context = paragraph['context']
            extracted_contexts.append(context)
    print(f"Extracted {len(extracted_contexts)} contexts from the JSON.")
    return extracted_contexts

def upload_text_to_corpus(corpus_name, text_content, display_name, description):
    """Uploads text content to the specified corpus by creating a temp file."""
    print(f"Uploading '{display_name}' to corpus...")
    
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8', suffix='.txt') as temp_file:
        temp_file.write(text_content)
        temp_file_path = temp_file.name

    try:
        rag_file = rag.upload_file(
            corpus_name=corpus_name,
            path=temp_file_path,
            display_name=display_name,
            description=description,
        )
        print(f"Successfully uploaded '{display_name}' to corpus: {rag_file.name}")
        return rag_file
    except Exception as e:
        print(f"Error uploading file '{display_name}': {e}")
        return None
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


def update_env_file(corpus_name, env_file_path):
    """Updates the .env file with the corpus name."""
    try:
        set_key(env_file_path, "RAG_CORPUS", corpus_name)
        print(f"Updated RAG_CORPUS in {env_file_path} to {corpus_name}")
    except Exception as e:
        print(f"Error updating .env file: {e}")

def list_corpus_files(corpus_name):
    """Lists files in the specified corpus."""
    files = list(rag.list_files(corpus_name=corpus_name))
    print(f"Total files in corpus: {len(files)}")
    for file in files:
        print(f"File: {file.display_name} - {file.name}")


def main():
    initialize_vertex_ai()
    corpus = create_or_get_corpus()

    update_env_file(corpus.name, ENV_FILE_PATH)

    cuad_json_path = os.path.join(os.path.dirname(__file__), CUAD_JSON_FILENAME)

    cuad_contexts = load_cuad_json_data(cuad_json_path)

    for i, context in enumerate(cuad_contexts):
        display_name = f"CUAD_Context_{i+1}"
        description = f"Context from CUADv1.json, paragraph {i+1}"
        upload_text_to_corpus(
            corpus_name=corpus.name,
            text_content=context,
            display_name=display_name,
            description=description
        )   
    list_corpus_files(corpus_name=corpus.name)

if __name__ == "__main__":
    main()