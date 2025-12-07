from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.memory import ConversationBufferWindowMemory
from .agents.accident_data_collector_agent import AccidentDataCollectorAgent

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
        session_id = request.session.session_key or self.MVP_SESSION_ID


        agent = AccidentDataCollectorAgent()

        try:
            response = agent.collect_data(user_input, session_id=session_id)
            collected_data = agent.get_collected_data(session_id=session_id)
            return Response({
                "response": response, 
                "session_id": session_id,
                "collected_data": collected_data.model_dump()})
        except Exception as e:
            print(f"Error during agent execution: {e}")
            return Response({"error": "Internal server error"}, status=500)