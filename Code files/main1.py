import openai 
import langchain
import pinecone 
from langchain.document_loaders import PyPDFDirectoryLoader 
from langchain_text_splitters import RecursiveCharacterTextSplitter
