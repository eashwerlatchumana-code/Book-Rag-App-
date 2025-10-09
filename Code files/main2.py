#Importing required libraries 
import langchain
import pinecone 
import openai
import os 
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_openai import OpenAI
from langchain_pinecone import PineconeVectorStore 
from pinecone import Pinecone


#Reading a file 

def read_doc(directory):
    file_loader = PyPDFDirectoryLoader(directory)
    document = file_loader.load()
    return document

doc = read_doc("Code files")