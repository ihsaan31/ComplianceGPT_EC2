from langchain.chains.query_constructor.base import AttributeInfo
from langchain.chains.query_constructor.base import (
    StructuredQueryOutputParser,
    get_query_constructor_prompt,
)
from langchain_core.language_models.base import BaseLanguageModel
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_core.vectorstores import VectorStore

from retriever.self_query import self_query

# Define metadata field information
metadata_field_info = [
    AttributeInfo(
        name="title",
        description="The title of the document of regulation",
        type="string",
    ),
    AttributeInfo(
        name="sector",
        description="""The sector of the regulation""",
        type="string",
    ),
    AttributeInfo(
        name="subsector",
        description="The subsector of the regulation",
        type="string",
    ),
    AttributeInfo(
        name="regulation_type",
        description="""The type of the regulation""",
        type="string",
    ),
    AttributeInfo(
        name="regulation_number",
        description="The number of the regulation",
        type="string",
    ),
    AttributeInfo(
        name="effective_date",
        description="The effective date of the regulation",
        type="date",
    ),
]

# Define document content description
document_content_description = "The content of the document"


# Create query constructor
def self_query_ojk(llm_model: BaseLanguageModel, vector_store: VectorStore, search_type: str = "similarity") -> SelfQueryRetriever:
    return self_query(llm_model, vector_store, document_content_description, metadata_field_info, search_type=search_type)
