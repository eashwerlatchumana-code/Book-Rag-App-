import os
from openai import OpenAI
from dotenv import load_dotenv
from app.services import ragappfunction
from app.database.chats_repo import chatsRepo

load_dotenv()

class OpenAIResponse:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant. Answer questions based only on the provided context. If the answer is not in the context, say so.; If the User asks another topic or question, then don't worry about the context"
            }
        ]
        self.chats_repo = chatsRepo()

    def new_chat(self, question=None, pinconevectorstore=None):
        def retrive_ans(messages, query_ans, pinconevectorstore):
            docsearch = ragappfunction.retrive_query(vectorstore=pinconevectorstore, query=query_ans)
            # Debug: Print number of documents retrieved
            if docsearch:
                print(f"[DEBUG] Retrieved {len(docsearch)} document(s) from vectorstore")
            else:
                print("[DEBUG] No documents retrieved from vectorstore")
            messages.append({"role": "user", "content": f"Context::\n{docsearch}\n\nQuestion: {query_ans}"})
            return messages

        def answer(messages):
            response = self.client.chat.completions.create(
                model="gpt-4o",
                temperature=0.5,
                messages=messages)
            return response.choices[0].message.content

        try:
            messages = retrive_ans(self.messages, question, pinconevectorstore)
            result = answer(messages)
            return result
        except Exception as e:
            # If vectorstore query fails, proceed without context
            print(f"\n[WARNING] Could not retrieve context from vectorstore: {str(e)}")
            print("[INFO] Proceeding without book context - AI will use general knowledge only")
            docsearch = None
            self.messages.append({"role": "user", "content": f"Context::\n{docsearch}\n\nQuestion: {question}"})
            result = answer(self.messages)
            return result

    def continue_chat(self, chat_id=None, question=None, pinconevectorstore=None):
        def retrive_ans(messages, query_ans, pinconevectorstore):
            docsearch = ragappfunction.retrive_query(vectorstore=pinconevectorstore, query=query_ans)
            # Debug: Print number of documents retrieved
            if docsearch:
                print(f"[DEBUG] Retrieved {len(docsearch)} document(s) from vectorstore")
            else:
                print("[DEBUG] No documents retrieved from vectorstore")
            messages.append({"role": "user", "content": f"Context::\n{docsearch}\n\nQuestion: {query_ans}"})
            return messages

        def answer(messages):
            response = self.client.chat.completions.create(
                model="gpt-4o",
                temperature=0.5,
                messages=messages)
            return response.choices[0].message.content

        chat_data = self.chats_repo.get_chat_by_id(chat_id=chat_id)
        messages_data = chat_data['messages']

        for key, value in messages_data.items():
            self.messages.append(value)

        try:
            messages = retrive_ans(messages=self.messages, query_ans=question, pinconevectorstore=pinconevectorstore)
            result = answer(messages)
            return result
        except Exception as e:
            # If vectorstore query fails, proceed without context
            print(f"\n[WARNING] Could not retrieve context from vectorstore: {str(e)}")
            print("[INFO] Proceeding without book context - AI will use general knowledge only")
            docsearch = None
            self.messages.append({"role": "user", "content": f"Context::\n{docsearch}\n\nQuestion: {question}"})
            result = answer(self.messages)
            return result
