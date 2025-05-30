## for long contracts 
    # 1. The long_analyst_agent takes the user's long document text.
    # 2. Chunking: The agent breaks the long document text into smaller, manageable chunks in your application's code (e.g., using LangChain's text splitters or a custom function). These are just strings in memory.
    # 3. Querying CUADv1_corpus: For each chunk (or selected important chunks) from the user's document:
    # 4. This chunk is used as the input text to rag.retrieval_tool(...) that targets your existing CUADv1_corpus.
    # 5. The tool embeds this input chunk and searches CUADv1_corpus for similar paragraphs from CUAD.
    # 6. The LLM gets: [User's document chunk] + [Retrieved CUAD paragraphs].
from google.adk.agents import LlmAgent

long_contract = LlmAgent(
    name="long_contract",
    model='gemini-2.0-flash',
    description="not finsihed yet",
    instruction="""
        If you were called just tell return that this is not finished yet
    """,
)