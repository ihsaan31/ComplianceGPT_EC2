import nest_asyncio
import warnings
from fastapi import FastAPI, HTTPException, Depends, Request, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from utils.config import get_config
from utils.models import ModelName, LLMModelName, EmbeddingModelName, get_model, get_azure_openai_llm

from database.vector_store.vector_store import ElasticIndexManager
from database.vector_store.neo4j_graph_store import Neo4jGraphStore

from retriever.retriever_ojk.retriever_ojk import get_retriever_ojk
from retriever.retriever_bi.retriever_bi import get_retriever_bi
from retriever.retriever_sikepo.lotr_sikepo import lotr_sikepo
from database.chat_store import ElasticChatStore

from chain.rag_chain import create_combined_answer_chain, create_chain_with_chat_history, print_answer_stream, create_combined_context_chain
from chain.chain_sikepo.graph_cypher_sikepo_chain import graph_rag_chain

import logging
import urllib.parse as urlparse


# Apply nest_asyncio and filter warnings
nest_asyncio.apply()
warnings.filterwarnings("ignore")

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========== CONFIG ===========
security = HTTPBearer()
config = get_config()

# =========== MODEL INITIALIZATION ===========
llm_model, embed_model = get_model(model_name=ModelName.AZURE_OPENAI, config=config,
                                   llm_model_name=LLMModelName.GPT_AZURE, embedding_model_name=EmbeddingModelName.EMBEDDING_3_SMALL)
best_llm = get_azure_openai_llm(
    **config['config_azure_emb'], llm_model_name=LLMModelName.GPT_4O)
# efficient_llm = get_azure_openai_llm(**config['config_azure_emb'], llm_model_name=LLMModelName.GPT_35_TURBO)
efficient_llm, _ = get_model(model_name=ModelName.OPENAI, config=config,
                             llm_model_name=LLMModelName.GPT_4O_MINI, embedding_model_name=EmbeddingModelName.EMBEDDING_3_SMALL)
llm_model = efficient_llm
best_llm = efficient_llm

top_k_quality = 15
top_k_speed = 8

# =========== DATABASE INITIALIZATION ===========
index_ojk = ElasticIndexManager(
    index_name='ojk', embed_model=embed_model, config=config)
index_bi = ElasticIndexManager(
    index_name='bi-new', embed_model=embed_model, config=config)
index_sikepo_ket = ElasticIndexManager(
    index_name='sikepo-ketentuan-terkait', embed_model=embed_model, config=config)
index_sikepo_rek = ElasticIndexManager(
    index_name='sikepo-rekam-jejak', embed_model=embed_model, config=config)

vector_store_ojk = index_ojk.load_vector_index()
vector_store_bi = index_bi.load_vector_index()
vector_store_ket = index_sikepo_ket.load_vector_index()
vector_store_rek = index_sikepo_rek.load_vector_index()

neo4j_sikepo = Neo4jGraphStore(config=config)
graph = neo4j_sikepo.get_graph()

chat_store = ElasticChatStore(k=4, config=config)

# =========== RETRIEVER INITIALIZATION ===========
retriever_ojk_quality = get_retriever_ojk(vector_store=vector_store_ojk, top_k=top_k_quality,
                                          llm_model=efficient_llm, embed_model=embed_model, config=config)
retriever_bi_quality = get_retriever_bi(vector_store=vector_store_bi, top_k=top_k_quality,
                                        llm_model=efficient_llm, embed_model=embed_model, config=config)
retriever_sikepo_ket_quality = lotr_sikepo(vector_store=vector_store_ket, top_k=top_k_quality,
                                           llm_model=efficient_llm, embed_model=embed_model, config=config)
retriever_sikepo_rek_quality = lotr_sikepo(vector_store=vector_store_rek, top_k=top_k_quality,
                                           llm_model=efficient_llm, embed_model=embed_model, config=config)

retreiver_ojk_speed = get_retriever_ojk(vector_store=vector_store_ojk, top_k=top_k_speed,
                                        llm_model=efficient_llm, embed_model=embed_model, config=config)
retriever_bi_speed = get_retriever_bi(vector_store=vector_store_bi, top_k=top_k_speed,
                                      llm_model=efficient_llm, embed_model=embed_model, config=config)
retriever_sikepo_ket_speed = lotr_sikepo(vector_store=vector_store_ket, top_k=top_k_speed,
                                         llm_model=efficient_llm, embed_model=embed_model, config=config)
retriever_sikepo_rek_speed = lotr_sikepo(vector_store=vector_store_rek, top_k=top_k_speed,
                                         llm_model=efficient_llm, embed_model=embed_model, config=config)

# =========== CHAIN INITIALIZATION ===========
graph_chain = graph_rag_chain(best_llm, llm_model, graph=graph)

chain_quality = create_combined_answer_chain(
    llm_model=llm_model,
    graph_chain=graph_chain,
    retriever_ojk=retriever_ojk_quality,
    retriever_bi=retriever_bi_quality,
    retriever_sikepo_ketentuan=retriever_sikepo_ket_quality,
    retriever_sikepo_rekam=retriever_sikepo_rek_quality,
    best_llm=best_llm,
    efficient_llm=efficient_llm
)

chain_speed = create_combined_answer_chain(
    llm_model=llm_model,
    graph_chain=graph_chain,
    retriever_ojk=retreiver_ojk_speed,
    retriever_bi=retriever_bi_speed,
    retriever_sikepo_ketentuan=retriever_sikepo_ket_speed,
    retriever_sikepo_rekam=retriever_sikepo_rek_speed,
    best_llm=best_llm,
    efficient_llm=efficient_llm
)

# =========== CHAIN HISTORY INITIALIZATION ===========
chain_history_quality = create_chain_with_chat_history(
    final_chain=chain_quality,
    chat_store=chat_store,
)

chain_history_speed = create_chain_with_chat_history(
    final_chain=chain_speed,
    chat_store=chat_store,
)


# =========== FASTAPI APP ===========
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler


@app.middleware("http")
async def custom_exception_handler(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Unhandled error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"message": "An internal error occurred",
                     "details": str(e)},
        )


# =========== INTERFACE ===========
class ChatRequest(BaseModel):
    user_input: str


class ChatResponse(BaseModel):
    user_message: str
    ai_response: str


class ModelRequest(BaseModel):
    model: str


# =========== API ENDPOINTS ===========
@app.get("/api/chat/{model_type}")
async def chat_endpoint(model_type: str, message: str, conv_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    conv_id = urlparse.unquote(conv_id)
    user_id = credentials.credentials
    user_id = urlparse.unquote(user_id)
    try:
        if model_type == "quality":
            response = StreamingResponse(print_answer_stream(
                message, chain=chain_history_quality, user_id=user_id, conversation_id=conv_id), media_type="text/event-stream")
            return response
        elif model_type == "speed":
            response = StreamingResponse(print_answer_stream(
                message, chain=chain_history_speed, user_id=user_id, conversation_id=conv_id), media_type="text/event-stream")
            return response
        else:
            raise HTTPException(status_code=400, detail="Invalid model type")
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An error occurred during chat processing", "details": str(e)},
        )


@app.get("/api/fetch_conversations/")
async def fetch_conv(credentials: HTTPAuthorizationCredentials = Depends(security)):
    user_id = credentials.credentials
    user_id = urlparse.unquote(user_id)
    try:
        session_ids_with_title = chat_store.get_conversation_ids_by_user_id(
            user_id)
        return JSONResponse(
            status_code=200,
            content=session_ids_with_title
        )
    except Exception as e:
        logger.error(f"Error fetching conversations: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An error occurred while fetching conversations", "details": str(e)},
        )


@app.get("/api/fetch_messages/{conversation_id}")
async def fetch_message(conversation_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    # decode conversation_id
    conversation_id = urlparse.unquote(conversation_id)
    user_id = credentials.credentials
    user_id = urlparse.unquote(user_id)
    try:
        messages = chat_store.get_conversation(
            user_id=user_id, conversation_id=conversation_id)
        if not messages:
            return JSONResponse(
                status_code=404,
                content={"message": "Conversation not found"}
            )
        return JSONResponse(
            status_code=200,
            content=messages
        )
    except Exception as e:
        logger.error(f"Error fetching messages: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An error occurred while fetching messages", "details": str(e)},
        )


@app.put("/api/rename_conversation/{conversation_id}")
async def rename_conversation(
    conversation_id: str,
    new_title: str = Query(..., description="New title for the conversation"),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # decode conversation_id
    conversation_id = urlparse.unquote(conversation_id)
    user_id = credentials.credentials
    user_id = urlparse.unquote(user_id)
    try:
        success = chat_store.rename_title(user_id, conversation_id, new_title)
        if success:
            return JSONResponse(status_code=200, content={"message": "Conversation renamed successfully"})
        else:
            raise HTTPException(
                status_code=404, detail="Conversation not found")
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f"Error renaming conversation: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An error occurred while renaming the conversation", "details": str(e)},
        )


@app.put("/api/rename_conversation/{conversation_id}")
async def rename_conversation(
    conversation_id: str,
    new_title: str = Query(..., description="New title for the conversation"),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # decode conversation_id
    conversation_id = urlparse.unquote(conversation_id)
    user_id = credentials.credentials
    user_id = urlparse.unquote(user_id)
    try:
        success = chat_store.rename_title(user_id, conversation_id, new_title)
        if success:
            return JSONResponse(status_code=200, content={"message": "Conversation renamed successfully"})
        else:
            raise HTTPException(
                status_code=404, detail="Conversation not found")
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f"Error renaming conversation: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An error occurred while renaming the conversation", "details": str(e)},
        )


@app.delete("/api/delete_conversation/{conversation_id}")
async def delete_conversation(conversation_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    # decode conversation_id
    conversation_id = urlparse.unquote(conversation_id)
    user_id = credentials.credentials
    user_id = urlparse.unquote(user_id)
    try:
        success = chat_store.clear_session_history(user_id, conversation_id)
        if success:
            return JSONResponse(status_code=200, content={"message": "Conversation deleted successfully"})
        else:
            raise HTTPException(
                status_code=404, detail="Conversation not found")
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An error occurred while deleting the conversation", "details": str(e)},
        )


@app.delete("/api/delete_all_conversations/")
async def delete_all_user_chats(credentials: HTTPAuthorizationCredentials = Depends(security)):
    user_id = credentials.credentials
    user_id = urlparse.unquote(user_id)
    try:
        success = chat_store.clear_conversation_by_userid(user_id)
        if success:
            return JSONResponse(status_code=200, content={"message": "All conversations deleted successfully"})
        else:
            raise HTTPException(
                status_code=404, detail="No conversations found for the user")
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f"Error deleting all conversations: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "message": "An error occurred while deleting all conversations", "details": str(e)},
        )

# =========== MAIN ===========
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9898)
