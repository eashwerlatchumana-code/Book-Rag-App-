import openai 
import langchain
import pinecone 
from langchain.document_loaders import PyPDFDirectoryLoader 
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone 
from langchain.llms import OpenAI 
import os 

#Reading PDF file or document 
def read_doc(directory): 
    file_loader = PyPDFDirectoryLoader(directory) #This function is used via directory (file location)
    documents  = file_loader.load() #Defining the loaded document 
    return documents 

doc = read_doc("Code files")
print(doc)