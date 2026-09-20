import os
from typing import TypedDict, List
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END

load_dotenv()

class RAGState(TypedDict):
    question: str
    chat_history: List[BaseMessage]
    context: List[Document]
    answer: str

CHROMA_PATH = "vectorstore_fiqa"

def get_rag_graph():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",
        temperature=0.2,
        api_key=os.getenv("GROQ_API_KEY")
    )

    def retrieve(state: RAGState):
        return {"context": retriever.invoke(state["question"])}

    def generate(state: RAGState):
        context_text = "\n\n---\n\n".join([doc.page_content for doc in state["context"]])
        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "Você é um assistente financeiro especialista baseado na base FiQA.\n"
                "Responda à dúvida estritamente com base nos trechos abaixo.\n"
                "Se não souber ou a resposta não estiver no contexto, afirme claramente.\n\n"
                "Contexto recuperado:\n{context}"
            )),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])
        chain = prompt | llm
        response = chain.invoke({
            "context": context_text,
            "chat_history": state["chat_history"],
            "question": state["question"]
        })
        return {"answer": response.content}

    workflow = StateGraph(RAGState)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("generate", generate)
    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()

rag_app = get_rag_graph()