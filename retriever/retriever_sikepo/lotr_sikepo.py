# ISI RETRIEVER DARI SIKEPO KETENTUAN TERKAIT, OUTPUT HARUS SATU RETRIEVER SAJA
from langchain_cohere import CohereRerank
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers import (
    ContextualCompressionRetriever,
    MergerRetriever,
)
from langchain_core.runnables import RunnableLambda
from langchain_community.document_transformers import (
    EmbeddingsRedundantFilter, EmbeddingsClusteringFilter, LongContextReorder
)
# from langchain.retrievers.document_compressors.flashrank_rerank import FlashrankRerank
# from langchain_community.document_compressors.rankllm_rerank import RankLLMRerank
from langchain.retrievers.document_compressors.base import DocumentCompressorPipeline
from langchain_core.vectorstores import VectorStore
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.embeddings import Embeddings
from langchain_community.document_transformers.embeddings_redundant_filter import _DocumentWithState
from langchain_core.runnables import RunnableLambda
from constant.prefilter import FILTER_SIKEPO as filter_dict
from retriever.retriever_sikepo.self_query_sikepo import self_query_retriever_sikepo

def to_documents(context: list[_DocumentWithState]):
    context_unique = [i.to_document() for i in context]
    return context_unique

def lotr_sikepo(vector_store: VectorStore, llm_model: BaseLanguageModel, embed_model: Embeddings, config: dict = {}, top_k: int = 8, with_self_query: bool = True):
    retriever_mmr = vector_store.as_retriever(search_type="mmr", search_kwargs={'k': top_k, 'lambda_mult': 0.85, 'fetch_k': 40, 'filter':filter_dict})
    retriever_similarity = vector_store.as_retriever(search_type="similarity", search_kwargs={'k': top_k, 'filter': filter_dict})
    self_query_retriever = self_query_retriever_sikepo(
        llm_model=llm_model, vector_store=vector_store, top_k=top_k, filter=filter_dict)

    lotr = retriever_mmr
    # merge retrievers
    if with_self_query:
        lotr = MergerRetriever(retrievers=[self_query_retriever, retriever_mmr])


    # remove redundant documents
    filter = EmbeddingsRedundantFilter(embeddings=embed_model)
    reordering = LongContextReorder()
    pipeline = DocumentCompressorPipeline(transformers=[filter])
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=pipeline, base_retriever=lotr
    )

    chain = compression_retriever | RunnableLambda(to_documents)

    # rerank with Cohere
    # compressor = CohereRerank(
    #     cohere_api_key=config['cohere_api_key'], top_n=top_n, model="rerank-multilingual-v3.0")
    # compressor = FlashrankRerank(top_n=top_n)
    # compressor = RankLLMRerank(top_n=top_n, model="gpt", gpt_model="gpt-3.5-turbo")
    
    # retriever = ContextualCompressionRetriever(
    #     base_compressor=compressor, base_retriever=compression_retriever
    # )

    return chain
