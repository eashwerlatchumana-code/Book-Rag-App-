from openai import OpenAI
from dotenv import load_dotenv
import os 
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#Storing all responses in this dictionary 
all_response = {}
# response = client.chat.completions.create(
#     model="gpt-4o",
#     messages= [{"role": "system", "content": "You are a helpful assistant."},
#     {"role": "user", "content": "What is Python?"},{"role": "assistant", "content": f"python is a versatile language"} ]
# )

# print(response.choices[0].message.content)
history = []
msg = []
def histroylabel(num, userques, llmresponse):
    rstr = f"{num} You:{userques}"
    return rstr
def session_approach(qnum,userquestion): 
    msgdict = {}
    msgdict["role"] = "user"
    msgdict["content"] = f"{userquestion}"
    msg.append(msgdict)
    response = client.chat.completions.create(model="gpt-4o",messages=msg)
    llmresponse = (response.choices[0].message.content)
    msgdict["role"] = "assistant"
    msgdict["content"] = llmresponse
    msg.append(msgdict)
    history.append(histroylabel(qnum, userquestion, llmresponse))
    return llmresponse
currentques =0
chat = ''
while chat != "end":
    print("\n")
    chat = input("Hey there input your question, if you want to see history, type: 'h', To End the chat, type : 'end'\nEnter your question:")
    print("---------------------------------------------------------------------------------------------------")
    currentques+=1
    if chat =='h':
         
        print("History:\n")
        for i in history: 
            print(i)
    else: 
        print("---------------------------------------------------------------------------------------------------")
        llmresp = session_approach(currentques,f"{chat}")
        print("\n")
        print(f"User: {chat}")
        print(f"Response: {llmresp}")

    

