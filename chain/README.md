# Chain Implementation for Compliance Chatbot

This folder contains the core implementation of the chains used in the OCBC Compliance Chatbot. These chains are responsible for handling query routing, chains development, and integrating with large language models (LLMs) for answering complex compliance-related questions.

## Files Overview

### `rag_chain.py`
This file defines various functions and classes that:
- **Create Sequential Chains (Fast-Retrieval Method)** <br>To answer the question from OJK first, if not answered, then it will go to BI, and lastly it will go to SIKEPO.
  ![image](https://github.com/user-attachments/assets/6e36d76f-1f79-4488-834a-09af6465028d)

- **Create Combined Chains (Default for Best Result)** <br>To retrieve and generate answers in parallel from each source (OJK, BI, Sikepo) and generate a unified response.
  ![image](https://github.com/user-attachments/assets/35701f98-af8e-4485-8fb9-51d68576eff6)

- **Create Combined Context Chains (Fast-Retrieval Method)** <br>To merge multiple contexts from all retrievers (OJK, BI, Sikepo) and generate a unified response.
  ![image](https://github.com/user-attachments/assets/bbc7676c-9f3c-421f-bc42-c1e7fdbf797e)

- **Chat History Management:** <br>Allows for the integration of chat history, enabling context-aware responses across conversations.

### `chain_routing.py`
This file provides the routing logic for determining the best data source for answering a user's query:
- **Question Routing:** Determines which module (Regulation Detail, Regulation Track Record) is best suited to answer the query.
- **Answer Routing:** Checks if the generated answer is adequate or needs to be routed to another chain for a more accurate response. USed for Sequential Chains.

## Dependencies
The implementation heavily relies on:
- **Langchain Core Runnables:** For creating and executing different chain configurations.
- **Pydantic:** For structured data validation within the routing logic.
- **PromptTemplate:** For templating the prompts used in the LLM-based modules.

## How to Use
1. **Import the Required Modules:** The chains are designed to be modular. Import the functions and classes needed for your specific use case.
2. **Create a Chain:** Use the provided functions to create a custom chain depending on the compliance question you need to answer.
3. **Invoke the Chain:** Pass in the user's query along with any necessary configuration (e.g., LLM model, retrievers) to get a response.
