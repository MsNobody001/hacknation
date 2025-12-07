from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.memory import ConversationBufferWindowMemory
from .agents.accident_data_collector_agent import  AccidentDataCollectorAgent
import os
import redis
import json

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
    REDIS_HISTORY_KEY = f"chat_history:{MVP_SESSION_ID}"
    REDIS_DATA_KEY = f"collected_data:{MVP_SESSION_ID}"

    def post(self, request):
        user_input = request.data.get("input", "")
        redis_url = os.environ.get("AZURE_REDIS_URI") or os.environ.get("REDIS_URL") or ""
        if not redis_url:
            host = os.environ.get("REDIS_HOST")
            port = os.environ.get("REDIS_PORT")
            db = os.environ.get("REDIS_DB", "0")
            password = os.environ.get("REDIS_KEY")
            if host and port:
                scheme = "rediss" if port == "6380" or os.environ.get("REDIS_SSL", "1") == "1" else "redis"
                auth = f":{password}@" if password else ""
                redis_url = f"{scheme}://{auth}{host}:{port}/{db}"

        print(f"Connecting to Redis at {redis_url}")
        try:
            self.redis = redis.Redis.from_url(redis_url, decode_responses=True) if redis_url else None
            if self.redis:
                self.redis.ping()
                print("Connected to Redis successfully")
        except Exception as e:
            print(f"Error connecting to Redis: {e}")
            self.redis = None

        chat_history = []
        try:
            if self.redis:
                raw_history = self.redis.get(self.REDIS_HISTORY_KEY)
                if raw_history:
                    chat_history = json.loads(raw_history)
                raw_data = self.redis.get(self.REDIS_DATA_KEY)
                if raw_data:
                    collected_data_dict = json.loads(raw_data)
        except Exception as e:
            print(f"Error reading chat history from Redis: {e}")
            chat_history = []

        agent = AccidentDataCollectorAgent()

        try:
            response = agent.collect_data(user_input, chat_history)
        except TypeError:
            response = agent.collect_data(user_input)
        except Exception as e:
            print(f"Error during agent execution: {e}")
            return Response({"error": "Internal server error"}, status=500)

        try:
            resp_text = response if isinstance(response, str) else json.dumps(response, ensure_ascii=False)
            chat_history.append({"role": "user", "content": user_input})
            chat_history.append({"role": "assistant", "content": resp_text})

            MAX_ENTRIES = 100
            if len(chat_history) > MAX_ENTRIES:
                chat_history = chat_history[-MAX_ENTRIES:]

            if self.redis:
                self.redis.set(self.REDIS_HISTORY_KEY, json.dumps(chat_history, ensure_ascii=False))
                self.redis.set(self.REDIS_DATA_KEY, json.dumps(agent.get_collected_data().__dict__, ensure_ascii=False))
        except Exception as e:
            print(f"Error saving chat history to Redis: {e}")

        return Response({
            "response": response, 
            "session_id": self.MVP_SESSION_ID,
            "collected_data": agent.get_collected_data().__dict__})


class AccidentStatementCollectorView(APIView):
    MVP_SESSION_ID = "mvp_single_user_session"
    def post(self, request):
        from .agents.accident_statement_collector_agent import AccidentStatementCollectorAgent
        user_input = request.data.get("input", "")
        session_id = request.session.session_key or self.MVP_SESSION_ID

        agent = AccidentStatementCollectorAgent()

        try:
            response = agent.collect_data(user_input, chat_history=[])
            collected_data = agent.get_collected_data()
            return Response({
                "response": response, 
                "session_id": session_id,
                "collected_data": collected_data.model_dump()})
        except Exception as e:
            print(f"Error during agent execution: {e}")
            return Response({"error": "Internal server error"}, status=500)


class AccidentReportCollectorView(APIView):
    MVP_SESSION_ID = "mvp_single_user_session"
    def post(self, request):
        from .agents.accident_report_collector_agent import AccidentReportCollectorAgent
        user_input = request.data.get("input", "")
        session_id = request.session.session_key or self.MVP_SESSION_ID

        agent = AccidentReportCollectorAgent()

        try:
            response = agent.collect_data(user_input, chat_history=[])
            collected_data = agent.get_collected_data()
            return Response({
                "response": response, 
                "session_id": session_id,
                "collected_data": collected_data.model_dump()})
        except Exception as e:
            print(f"Error during agent execution: {e}")
            return Response({"error": "Internal server error"}, status=500)