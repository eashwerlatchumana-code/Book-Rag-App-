
#Importing required libraries 

import langchain
import pinecone 
import openai
import os 
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_openai import OpenAI
from langchain_pinecone import PineconeVectorStore 
from pinecone import Pinecone
from dotenv import load_dotenv
load_dotenv()

#Reading a file 

def read_doc(directory):
    file_loader = PyPDFDirectoryLoader(directory)
    document = file_loader.load()
    return document

doc = read_doc("Code files")
(type(doc)) # This is a list type 
#breaking into chunks 

def chunks(docs, chuck_size = 400, chunck_overlap = 50):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = chuck_size, chunk_overlap = chunck_overlap)
    splited_doc = text_splitter.split_documents(docs)
    return splited_doc

changed_doc = chunks(docs = doc) #This is chunked document 

#embedding technique of OPEN AI 
try:
    embeddings=OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
    print(embeddings)
except Exception as E: 
    print(f"{E}, issue with finding llm api")
