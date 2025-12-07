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

MVP_SESSION_ID = "mvp_single_user_session"

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
            r = redis.Redis.from_url(redis_url, decode_responses=True) if redis_url else None
            if redis:
                r.ping()
                print("Connected to Redis successfully")
        except Exception as e:
            print(f"Error connecting to Redis: {e}")
            r = None

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
    REDIS_HISTORY_KEY = f"accident_chat_history:"
    REDIS_DATA_KEY = f"accident_collected_data:"

    def post(self, request):
        user_input = request.data.get("input", "")
        session_id = request.data.get("session_id") or MVP_SESSION_ID

        chat_history = get_redis_history(self.REDIS_HISTORY_KEY + session_id)

        agent = AccidentDataCollectorAgent()

        try:
            response = agent.collect_data(user_input, chat_history)
        except TypeError:
            response = agent.collect_data(user_input)
        except Exception as e:
            print(f"Error during agent execution: {e}")
            return Response({"error": "Internal server error"}, status=500)
        
        resp_text = response if isinstance(response, str) else json.dumps(response, ensure_ascii=False)
        set_redis_history(self.REDIS_HISTORY_KEY+session_id, user_input, resp_text, chat_history)
        set_redis_data(self.REDIS_DATA_KEY+session_id, agent.get_collected_data())

        return Response({
            "response": response, 
            "session_id": session_id,
            "collected_data": agent.get_collected_data().__dict__})


class AccidentStatementCollectorView(APIView):
    REDIS_HISTORY_KEY = f"statement_chat_history:"
    REDIS_DATA_KEY = f"statement_collected_data:"
    def post(self, request):
        from .agents.accident_statement_collector_agent import AccidentStatementCollectorAgent
        user_input = request.data.get("input", "")
        session_id = request.data.get("session_id") or MVP_SESSION_ID

        chat_history = get_redis_history(self.REDIS_HISTORY_KEY + session_id)
        collected_data_dict = get_redis_data(self.REDIS_DATA_KEY + session_id)

        agent = AccidentStatementCollectorAgent()

        if collected_data_dict:
            agent.load_collected_data(collected_data_dict)
        try:
            response = agent.collect_data(user_input, chat_history)
            collected_data = agent.get_collected_data()

        except Exception as e:
            print(f"Error during agent execution: {e}")
            return Response({"error": "Internal server error"}, status=500)
        resp_text = response if isinstance(response, str) else json.dumps(response, ensure_ascii=False)
        set_redis_history(self.REDIS_HISTORY_KEY+session_id, user_input, resp_text, chat_history)
        set_redis_data(self.REDIS_DATA_KEY+session_id, collected_data)
        return Response({
            "response": response, 
            "session_id": session_id,
            "collected_data": collected_data.model_dump()})

class AccidentReportCollectorView(APIView):
    REDIS_HISTORY_KEY = f"report_chat_history:"
    REDIS_DATA_KEY = f"report_collected_data:"

    def post(self, request):
        from .agents.accident_report_collector_agent import AccidentReportCollectorAgent
        user_input = request.data.get("input", "")
        session_id = request.data.get("session_id") or MVP_SESSION_ID

        chat_history = get_redis_history(self.REDIS_HISTORY_KEY + session_id)
        collected_data_dict = get_redis_data(self.REDIS_DATA_KEY + session_id)

        agent = AccidentReportCollectorAgent()

        if collected_data_dict:
            agent.load_collected_data(collected_data_dict)

        try:
            response = agent.collect_data(user_input, chat_history)
            collected_data = agent.get_collected_data()

        except Exception as e:
            print(f"Error during agent execution: {e}")
            return Response({"error": "Internal server error"}, status=500)
        
        resp_text = response if isinstance(response, str) else json.dumps(response, ensure_ascii=False)
        set_redis_history(self.REDIS_HISTORY_KEY+session_id, user_input, resp_text, chat_history)
        set_redis_data(self.REDIS_DATA_KEY+session_id, collected_data)
        return Response({
            "response": response, 
            "session_id": session_id,
            "collected_data": collected_data.model_dump()})


def get_redis_history(history_key):
    chat_history = []
    try:
        if r:
            raw_history = r.get(history_key)
            if raw_history:
                chat_history = json.loads(raw_history)
    except Exception as e:
        print(f"Error reading chat history from Redis: {e}")
        chat_history = []
    return chat_history

def set_redis_history(history_key, user_input, agent_response, chat_history):
    try:
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": agent_response})

        MAX_ENTRIES = 100
        if len(chat_history) > MAX_ENTRIES:
            chat_history = chat_history[-MAX_ENTRIES:]

        if r:
            r.set(history_key, json.dumps(chat_history, ensure_ascii=False))
    except Exception as e:
        print(f"Error saving chat history to Redis: {e}")

def set_redis_data(data_key, collected_data):
    try:
        if r:
            r.set(data_key, json.dumps(collected_data.__dict__, ensure_ascii=False))
    except Exception as e:
        print(f"Error saving collected data to Redis: {e}")

def get_redis_data(data_key):
    collected_data = None
    try:
        if r:
            raw_data = r.get(data_key)
            if raw_data:
                collected_data_dict = json.loads(raw_data)
                collected_data = collected_data_dict
    except Exception as e:
        print(f"Error reading collected data from Redis: {e}")
    return collected_data