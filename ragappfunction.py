import openai
import langchain
import os 
from dotenv import load_dotenv
# For document loading
from langchain_community.document_loaders import PyPDFLoader

# For text splitting
from langchain.text_splitter import RecursiveCharacterTextSplitter

# For vector store
from langchain_pinecone import PineconeVectorStore

# For LLM and chain
from langchain_openai import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
load_dotenv()
def read_doc(directory):
    file_loader = PyPDFLoader(directory)
    document = file_loader.load()
    return document

def chunks(docs, chuck_size = 400, chunck_overlap = 50):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = chuck_size, chunk_overlap = chunck_overlap)
    splited_doc = text_splitter.split_documents(docs)
    return splited_doc

def vectorstore( embedings, indexname, pineconeapikey,doc=None):
    vectorstore = PineconeVectorStore( embedding=embedings, 
                                                 index_name = indexname, pinecone_api_key = pineconeapikey)
    if doc == None: 
        pass
    else: 
        vectorstore.add_documents(doc)
    return vectorstore
def retrive_query(vectorstore, query, k=2):
    matching_results = vectorstore.similarity_search(query, k=k)
    return matching_results


llm = ChatOpenAI(model="gpt-4o", temperature=0.5, api_key="Insert your OpenAi ApiKey")
chain = load_qa_chain(llm,chain_type="stuff" )

def retrive_ans(query):
    docsearch = retrive_query(query) #This is the document that is going to fetched from the vector data base 
    response = chain.invoke({'input_documents' : docsearch, 'question':query})
    return response
                                            