import openai
import langchain
import os 
from dotenv import load_dotenv
# For document loading
from langchain_community.document_loaders import PyPDFLoader

# For text splitting
from langchain_text_splitters import RecursiveCharacterTextSplitter

# For vector store
from langchain_pinecone import PineconeVectorStore

# For LLM and chain
from langchain_openai import ChatOpenAI
load_dotenv()
def read_doc(directory):
    file_loader = PyPDFLoader(directory)
    document = file_loader.load()
    return document

def chunks(docs, chunk_size = 400, chunk_overlap = 50):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = chunk_size, chunk_overlap = chunk_overlap)
    splited_doc = text_splitter.split_documents(docs)
    return splited_doc

def vectorstore(embeddings, indexname, pineconeapikey, doc=None, namespace: str = ""):
    vectorstore = PineconeVectorStore(embedding=embeddings,
                                                 index_name = indexname, pinecone_api_key = pineconeapikey, namespace=namespace)
    if doc == None: 
        pass
    else: 
        vectorstore.add_documents(doc)
    return vectorstore
def retrive_query(vectorstore, query, k=2):
    matching_results = vectorstore.similarity_search(query, k=k)
    return matching_results


                                            