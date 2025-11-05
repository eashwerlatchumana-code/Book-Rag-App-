from app.services.pinecone_service import PineconeService
from app.database.chats_repo import chatsRepo
from app.database.messages_repo import MessagesRepo
from app.services.openai_service import OpenAIResponse

class ChatService:
    def __init__(self, user_id: str, question: str, retrieve_history : bool):
        self.user_id = user_id
        pinecone_service = PineconeService()
        self.vectorstore = pinecone_service.get_vectorstore(f"user_{user_id}")
        self.question = question
        self.chats_repo = chatsRepo()
        self.messages_repo = MessagesRepo()
        self.openai_service = OpenAIResponse()

    def new_chat(self, question, vectorstore):
        # Call the OpenAI new_chat method to get AI response
        result = self.openai_service.new_chat(question=question, pinconevectorstore=vectorstore)

        if result is not None:
            chat_id = self.initialize_chat_id(airesponse=result)

            # If chat was created successfully, add the message
            if chat_id:
                self.messages_repo.add_message(
                    chat_id=chat_id,
                    role="user",
                    content=question
                )
                self.messages_repo.add_message(
                    chat_id=chat_id,
                    role="assistant",
                    content=result
                )

                # Get all messages for this chat_id and update the chat
                messages = self.messages_repo.get_messages_by_chat_id(chat_id=chat_id)
                if messages:
                    for message in messages:
                        message_id = message.get('message_id')
                        if message_id:
                            self.chats_repo.update_chat(chat_id=chat_id, message_id=message_id)

                print("chat saved!")
                return result
            else:
                print("chat-id couldn't be created as of now, sorry!")
                return "end"
        else:
            print("sorry techinical difficulty, ai function is not responding")
            return "end"
    def initialize_chat_id(self, airesponse):
        title = airesponse[:30]
        response = self.chats_repo.create_chat(
            user_id=self.user_id,
            title=title
        )

        # Get the chat_id from the created chat
        if response:
            chat_data = self.chats_repo.get_chat_by_id(title=title)
            if chat_data:
                return chat_data.get('chat_id')

        print("Had difficulty creating the chat")
        return None

    def continuing_chat(self, chat_id, question):
        """
        Continue an existing chat conversation.

        Parameters:
        -----------
        chat_id : str
            The chat_id to continue
        question : str
            The user's question to continue the conversation

        Returns:
        --------
        str : Result from AI or status message
        """
        # Get chat by chat_id
        chat_data = self.chats_repo.get_chat_by_id(chat_id=chat_id)

        # Verify the user_id matches
        if chat_data and chat_data.get('user_id') == self.user_id:
            # Call continue_chat from openai_service
            result = self.openai_service.continue_chat(
                chat_id=chat_id,
                question=question,
                pinconevectorstore=self.vectorstore
            )

            if result:
                # Add user message
                self.messages_repo.add_message(
                    chat_id=chat_id,
                    role="user",
                    content=question
                )
                # Add assistant response
                self.messages_repo.add_message(
                    chat_id=chat_id,
                    role="assistant",
                    content=result
                )

                # Get all messages for this chat_id and update the chat
                messages = self.messages_repo.get_messages_by_chat_id(chat_id=chat_id)
                if messages:
                    for message in messages:
                        message_id = message.get('message_id')
                        if message_id:
                            self.chats_repo.update_chat(chat_id=chat_id, message_id=message_id)

               
                return result
            else:
                print("Sorry, technical difficulty - AI function is not responding")
                return "end"
        else:
            print("Sorry this chat_id doesn't belong to you, there must be technical difficulty")
            return "end" 
    