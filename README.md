<p align="center">
    <h1 align="center">
      <span style="color: white; font-weight: bold;">OCBC Compliance GPT</span>
    </h1>
</p>
<p align="center">
  <!-- Typing SVG by DenverCoder1 - https://github.com/DenverCoder1/readme-typing-svg -->
<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.herokuapp.com?font=Fira+Sans&pause=1000&color=ED1C24&center=true&vCenter=true&width=435&lines=CRAYON+2024+Internship;OCBC+Indonesia;Abraham+Megantoro;Ahmad+Rizki;Arkan+Alexei;Bryan+Delton;Ihsan+Fathiya" alt="Typing SVG" /></a>
</p>

## **Author**


<p align="center"> 
<table>
    <tr>
        <td colspan=4 align="center">CRAYON 2024 Intern @ OCBC Indonesia</td>
    </tr>
    <tr>
        <td>No.</td>
        <td>Name</td>
        <td>University</td>
        <td>Email</td>
    </tr>
    <tr>
        <td>1.</td>
        <td>Abraham Megantoro</td>
        <td>Bandung Institute of Technology</td>
        <td><a href="mailto:abrahams.ocbc@gmail.com">abrahams.ocbc@gmail.com</a></td>
    </tr>
    <tr>
        <td>2.</td>
        <td>Ahmad Rizki</td>
        <td>Bandung Institute of Technology</td>
        <td><a href="mailto:ahmadr.ocbc@gmail.com">ahmadr.ocbc@gmail.com</a></td>
    </tr>
    <tr>
        <td>3.</td>
        <td>Arkan Alexei</td>
        <td>University of Indonesia</td>
        <td><a href="mailto:arkan.ocbc@gmail.com">arkan.ocbc@gmail.com</a></td>
    </tr>
    <tr>
        <td>4.</td>
        <td>Bryan Delton T S</td>
        <td>Chinese University of Hong Kong, Shenzhen</td>
        <td><a href="mailto:bryandelton.ocbc@gmail.com">bryandelton.ocbc@gmail.com</a></td>
    </tr>
    <tr>
        <td>5.</td>
        <td>Ihsan Fathya</td>
        <td>Gunadarma University</td>
        <td><a href="mailto:ihsan.ihsan@ocbc.id">ihsan.ihsan@ocbc.id</a></td>
    </tr>
</table>
</p>

<br>

## **Folder Structure**

Here's an overview of the main folders and files in this repository:

```plaintext
├── chain/                    
│   ├── chain_bi/             
│   ├── chain_ojk/           
│   ├── chain_sikepo/         
│   ├── chain_routing.py     
│   └── rag_chain.py        
├── constant/                
│   ├── bi/
│   ├── evaluation/
│   ├── ojk/
│   ├── sikepo/
│   └── prompt.py
├── database/                
│   ├── store_logs/
│   ├── vector_store/
│   └── chat_store.py
├── retriever/               
│   ├── retriever_bi/
│   ├── retriever_ojk/
│   ├── retriever_sikepo/
│   └── self_query.py
├── scraping/                
├── utils/
├── evaluation.ipynb
├── main.py
└── main_storing_ojk.ipynb
```

<br>

### **Key Folders and Files**

- **chain/**: Contains the logic and routing for different processing chains, including BI, OJK, and SIKEPO. Click [here](https://github.com/taytb/chatbot-be/blob/main/chain/README.md) for the details.
  - `chain_routing.py`: Manages routing between different chains.
  - `rag_chain.py`: Handles Retrieval-Augmented Generation (RAG) for chaining.

- **constant/**: Stores constant files (prompt) and configurations for BI, OJK, SIKEPO, and evaluation results.

- **database/**: Manages data storage, including logs, chat history, and vector database.
  - **vector_store/**: Contains files related to vector and graph storage.
  - **store_logs/**: Contains files related to logs when storing vector databases.
  - `chat_store.py`: Handle the abstraction for chat message history
    
- **retriever/**: Scripts for data retrieval from the vector database specific to BI, OJK, and SIKEPO.

- **scraping/**: Includes scripts for web scraping and data extraction.

- **utils/**: Utility scripts for tasks like document extraction and configuration management.

- ``evaluation.ipynb``: Notebooks related to the evaluation process.

- ``main.py``: The primary script for running the project.


<br>

## **Installation**

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/taytb/chatbot-be.git
   ```

2. **Install Dependencies**  
   Ensure you're using Python 3.9.19, then install the required packages:  
   ```bash
   pip install -r requirements.txt
   ```
<br>

## **Usage**

1. **Start the API** <br>
   Launch the API with the following command:
   
   ```bash
   uvicorn main:app --reload
   ```

<br>

