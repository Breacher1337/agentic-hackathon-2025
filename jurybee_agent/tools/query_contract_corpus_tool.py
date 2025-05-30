"""
Tool for querying a specific Vertex AI RAG corpus using a pre-defined corpus resource name from environment.
"""

import logging
import os
from typing import List, Dict, Optional

# Assuming ToolContext is available from google.adk.tools.tool_context
from google.adk.tools.tool_context import ToolContext
from vertexai import rag

# It's good practice to explicitly load dotenv if your script relies on it.
# Although google.adk often handles this, for a standalone tool file, it's safer.
from dotenv import load_dotenv
load_dotenv()

# Import configurations
# Ensure that PROJECT_ID, LOCATION, DEFAULT_TOP_K, and DEFAULT_DISTANCE_THRESHOLD
# are defined in your config.py or as environment variables.
# We'll also directly load RAG_CORPUS from env.
from ..config import (
    PROJECT_ID, # Will be loaded from .env via dotenv in config.py
    LOCATION,   # Will be loaded from .env via dotenv in config.py
    DEFAULT_TOP_K,
    DEFAULT_DISTANCE_THRESHOLD,
)

# Load the RAG_CORPUS resource name directly from environment variables
RAG_CORPUS_RESOURCE_NAME = os.environ.get("RAG_CORPUS")

# Initialize Vertex AI globally if not already initialized
import vertexai
try:
    
    vertexai.init(project=PROJECT_ID, location=LOCATION)
except Exception as e:
    logging.error(f"Failed to initialize Vertex AI: {e}. "
                  "Please ensure GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION "
                  "are correctly set in your .env or environment variables.")
    # In a production environment, you might want a more robust error handling strategy here,
    # potentially raising the exception to prevent the application from starting without proper config.

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def query_contract_corpus_tool(
    query_text: str,
    tool_context: ToolContext, # Required by ADK tool signature
    contract_type: Optional[str] = None, # Kept as per your prompt's tool usage example
) -> dict:
    """
    Queries the pre-configured Vertex AI RAG corpus (resource name loaded from RAG_CORPUS environment variable)
    to find similar clauses or related legal commentary.

    This function is designed to be registered as a tool with your LlmAgent.

    Args:
        query_text (str): The text query to search for in the corpus (e.g., a contract clause).
        tool_context (ToolContext): The tool context provided by the ADK agent.
                                     While not directly used in this simplified RAG query logic,
                                     it adheres to the ADK tool signature.
        contract_type (str, optional): An optional parameter for the type of contract (e.g., "NDA", "Service Agreement").
                                       Note: Vertex AI RAG `rag.Filter` currently does not directly support
                                       arbitrary metadata filtering (like `contract_type`). If this filtering
                                       is crucial, consider separate corpora or post-retrieval filtering
                                       based on content. This parameter is kept to align with your prompt's example.

    Returns:
        dict: The query results and status, including 'status', 'message', 'query',
              'corpus_resource_name', 'results' (list of dicts), and 'results_count'.
    """
    if not RAG_CORPUS_RESOURCE_NAME:
        error_msg = "RAG_CORPUS environment variable is not set. Cannot query corpus."
        logging.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "query": query_text,
            "corpus_resource_name": None,
            "results": [],
            "results_count": 0,
        }

    if not query_text:
        logging.warning("Query text is empty. No search performed.")
        return {
            "status": "warning",
            "message": "Query text is empty. No search performed.",
            "query": query_text,
            "corpus_resource_name": RAG_CORPUS_RESOURCE_NAME,
            "results": [],
            "results_count": 0,
        }

    if not RAG_CORPUS_RESOURCE_NAME.startswith("projects/"):
        logging.error(f"Invalid RAG_CORPUS_RESOURCE_NAME loaded from environment: '{RAG_CORPUS_RESOURCE_NAME}'. "
                      "It must be a full resource name like 'projects/PROJECT_ID/locations/LOCATION/ragCorpora/CORPUS_ID'.")
        return {
            "status": "error",
            "message": f"Invalid corpus resource name loaded: '{RAG_CORPUS_RESOURCE_NAME}'. Please check your .env file.",
            "query": query_text,
            "corpus_resource_name": RAG_CORPUS_RESOURCE_NAME,
            "results": [],
            "results_count": 0,
        }

    try:
        # Configure retrieval parameters
        rag_retrieval_config = rag.RagRetrievalConfig(
            top_k=DEFAULT_TOP_K,
            filter=rag.Filter(vector_distance_threshold=DEFAULT_DISTANCE_THRESHOLD),
        )

        logging.info(f"Performing retrieval query on corpus '{RAG_CORPUS_RESOURCE_NAME}' for query: '{query_text[:50]}...'")
        response = rag.retrieval_query(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=RAG_CORPUS_RESOURCE_NAME,
                )
            ],
            text=query_text,
            rag_retrieval_config=rag_retrieval_config,
        )

        # Process the response into a more usable format
        results = []
        if hasattr(response, "contexts") and response.contexts:
            for ctx_group in response.contexts.contexts:
                result = {
                    "source_uri": (
                        ctx_group.source_uri if hasattr(ctx_group, "source_uri") else ""
                    ),
                    "source_name": (
                        ctx_group.source_display_name
                        if hasattr(ctx_group, "source_display_name")
                        else "Unknown Source"
                    ),
                    "text": ctx_group.text if hasattr(ctx_group, "text") else "",
                    "score": ctx_group.score if hasattr(ctx_group, "score") else 0.0,
                }
                results.append(result)

        # If no results found after processing
        if not results:
            logging.info(f"No relevant results found in corpus '{RAG_CORPUS_RESOURCE_NAME}' for query: '{query_text}'")
            return {
                "status": "warning",
                "message": f"No relevant results found in corpus '{RAG_CORPUS_RESOURCE_NAME}' for query: '{query_text}'",
                "query": query_text,
                "corpus_resource_name": RAG_CORPUS_RESOURCE_NAME,
                "results": [],
                "results_count": 0,
            }

        logging.info(f"Successfully retrieved {len(results)} results from corpus '{RAG_CORPUS_RESOURCE_NAME}'.")
        return {
            "status": "success",
            "message": f"Successfully queried corpus '{RAG_CORPUS_RESOURCE_NAME}'",
            "query": query_text,
            "corpus_resource_name": RAG_CORPUS_RESOURCE_NAME,
            "results": results,
            "results_count": len(results),
        }

    except Exception as e:
        error_msg = f"Error querying corpus '{RAG_CORPUS_RESOURCE_NAME}' with query '{query_text}': {str(e)}"
        logging.error(error_msg, exc_info=True) # Log full traceback for debugging
        return {
            "status": "error",
            "message": error_msg,
            "query": query_text,
            "corpus_resource_name": RAG_CORPUS_RESOURCE_NAME,
            "results": [],
            "results_count": 0,
        }