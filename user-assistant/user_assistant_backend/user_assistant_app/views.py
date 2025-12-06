from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.memory import ConversationBufferWindowMemory
from .agents import  AccidentDataCollectorAgent

class SampleView(APIView):
    def get(self, request):
        return Response({"message": "OK"})
    
class SequentialEventsAgentView(APIView):

    def post(self, request):
        user_input = request.data.get("input", "")
        agent = AccidentDataCollectorAgent()
        response = agent.collect_data(user_input)
        print(response)
        
        return Response({"result": response})

class AccidentDataCollectorView(APIView):
    MVP_SESSION_ID = "mvp_single_user_session"
    def post(self, request):
        user_input = request.data.get("input", "")
        print(settings.AZURE_REDIS_URI)
        print(settings.AZURE_REDIS_HOST)
        try:
            chat_history = RedisChatMessageHistory(
                session_id=self.MVP_SESSION_ID,
                url=settings.AZURE_REDIS_URI,
                key_prefix="zus_mvp_history:",
            )
            
            memory = ConversationBufferWindowMemory(
                memory_key="chat_history",
                chat_memory=chat_history,
                return_messages=True,
                k=10
            )
        except Exception as e:
            print(f"FATAL ERROR: Błąd połączenia z Redisem lub inicjalizacji pamięci! {e}")
            raise
        except Exception as e:
            print(f"Error initializing RedisChatMessageHistory: {e}")
            memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, k=10)

        agent = AccidentDataCollectorAgent.get_instance()
        
        try:
            response = agent.collect_data(user_input, memory)
            return Response({
                "response": response, 
                "session_id": self.MVP_SESSION_ID})
        except Exception as e:
            print(f"Error during agent execution: {e}")
            return Response({"error": "Internal server error"}, status=500)