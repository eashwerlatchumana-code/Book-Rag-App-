import ragappfunction 
from langchain_openai import OpenAIEmbeddings
import os 
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from pinecone import Pinecone
load_dotenv()
document = ragappfunction.read_doc("Insert the file here (Located in your directory)") #load my document 
  
chunkeddoc = ragappfunction.chunks(docs = document) #create it into chunks 

try:
    embeddings=OpenAIEmbeddings(api_key="Insert you OpenAI API Key Here")#getting openai llm 
    pineconeapi = "Insert you Pinecone API Key Here" #getting pineconeapi 
except Exception: 
    print("This embeddings has an error")

#creating the vectorstore 
pc = Pinecone(api_key = pineconeapi)
indexname = "Insert the name of your Pinecone Index"
index = pc.Index(indexname)
vectorstore = ragappfunction.vectorstore(embedings=embeddings,indexname=indexname, pineconeapikey=pineconeapi)

#LLM
try:
    llm = ChatOpenAI(model="gpt-4o", temperature=0.5, api_key="INsert openai Api Key ")
    chain = load_qa_chain(llm,chain_type="stuff" )
except Exception as e: 
    print("This llm has an error")

def retrive_ans(query_ans):
    docsearch = ragappfunction.retrive_query(vectorstore=vectorstore,query=query_ans) #This is the document that is going to fetched from the vector data base 
    response = chain.invoke({'input_documents' : docsearch, 'question':query_ans})
    return response
question = input("Enter the question you have regarding the shortstory:")
answer = retrive_ans(question)

print(f"\n{answer['output_text']}")
