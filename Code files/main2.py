
# Importing required libraries 
import langchain
import pinecone 
import openai
import os 
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_openai import OpenAI
from langchain_pinecone.vectorstores import Pinecone, PineconeVectorStore
from pinecone import Pinecone
from dotenv import load_dotenv
from langchain.chains.question_answering import load_qa_chain
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
print(type(changed_doc))
#embedding technique of OPEN AI 
try:
    embeddings=OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
except Exception as E: 
    print(f"{E}, issue with finding llm api")
vectors =embeddings.embed_query("TEST")
print(len(vectors))

#Vecter Serch DB in pincone 
vectorstore = PineconeVectorStore.from_documents(documents=changed_doc, embedding=embeddings, 
                                                 index_name = "langchain", pinecone_api_key = os.getenv("PINECONE_API_KEY")
                                                 )

#cosine similarity, retrive results from vector db 

def retrive_query(query, k=2):
    matching_results = vectorstore.similarity_search(query, k=k)
    return matching_results

#Using Load_qa_chain
#Defining the llm i am going to use 
llm = OpenAI(model="gpt-4o", temperature=0.5)
chain = load_qa_chain()