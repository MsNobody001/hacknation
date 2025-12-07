import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from .accident_models import AccidentInfo
import redis
import json
from pathlib import Path
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()


PROMPT_FILE_PATH = Path(__file__).parent / "prompts" / "collect_accident_data.txt"

class AccidentDataCollectorAgent:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
            openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
            temperature=0,
        )
        self._current_session_id = None
        
        redis_url = os.environ.get("AZURE_REDIS_URI") or os.environ.get("REDIS_URL") or ""
        if not redis_url:
            host = os.environ.get("REDIS_HOST")
            port = os.environ.get("REDIS_PORT")
            db = os.environ.get("REDIS_DB", "0")
            password = os.environ.get("REDIS_KEY")  # Azure Redis typically uses password/key
            if host and port:
                scheme = "rediss" if port == "6380" or os.environ.get("REDIS_SSL", "1") == "1" else "redis"
                auth = f":{password}@" if password else ""
                redis_url = f"{scheme}://{auth}{host}:{port}/{db}"

        print(f"Connecting to Redis at {redis_url}")
        try:
            self.redis = redis.Redis.from_url(redis_url, decode_responses=True)
            self.redis.ping()
            print("Connected to Redis successfully")
        except Exception as e:
            print(f"Error connecting to Redis: {e}")
            self.redis = None

        self.tools = self._create_tools()

        with open(PROMPT_FILE_PATH, "r", encoding="utf-8") as file:
            prompt_template = file.read()
        
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    prompt_template
                ),
                ("placeholder", "{chat_history}"),
                ("user", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)

    def _create_tools(self):
        @tool
        def save_accident_info(
            accident_date: str = None,
            accident_time: str = None,
            location: str = None,
            work_start_time: str = None,
            work_end_time: str = None,
            injury_type: str = None,
            circumstances: str = None,
            cause: str = None,
            place_description: str = None,
            medical_help: str = None,
            investigation: str = None,
            machines_involved: bool = None,
            machine_condition: str = None,
            proper_use: str = None,
            machine_description: str = None,
            machine_certification: str = None,
            machine_registry: str = None,
            witnesses: str = None
        ):
            """
            Zapisz informacje o wypadku podane przez użytkownika.
            Wywołaj tę funkcję gdy użytkownik poda jakiekolwiek dane o wypadku.
            Możesz wypełnić jedno lub więcej pól jednocześnie.
            
            Args:
                accident_date: Data wypadku
                accident_time: Godzina wypadku  
                location: Miejsce gdzie się wydarzył
                work_start_time: Planowana godzina rozpoczęcia pracy
                work_end_time: Planowana godzina zakończenia pracy
                injury_type: Rodzaj doznanych obrażeń
                circumstances: Ogólne okoliczności wypadku
                cause: Przyczyna wypadku
                place_description: Szczegółowy opis miejsca wypadku
                medical_help: Czy udzielono pomocy medycznej, nazwa placówki
                investigation: Czy prowadzono postępowanie, organ
                machines_involved: Czy były maszyny
                machine_condition: Czy maszyna była sprawna
                proper_use: Czy używano zgodnie z instrukcją
                machine_description: Opis maszyny/urządzenia
                machine_certification: Czy posiada atest/deklarację zgodności
                machine_registry: Czy wpisana do ewidencji środków trwałych
                witnesses: Dane świadków (imię, nazwisko, adres)
                activity_before_accident: Co robił bezpośrednio przed wypadkiem
                event_sequence: Szczegółowa sekwencja zdarzeń krok po kroku
                direct_cause: Bezpośrednia przyczyna urazu
                indirect_causes: Czynniki które przyczyniły się do wypadku
            """
            print(f'Saving accident info: {locals()}')

            collected_data = self.load_memory(self._current_session_id)
            if accident_date is not None:
                collected_data.accident_date = accident_date
            if accident_time is not None:
                collected_data.accident_time = accident_time
            if location is not None:
                collected_data.location = location
            if work_start_time is not None:
                collected_data.work_start_time = work_start_time
            if work_end_time is not None:
                collected_data.work_end_time = work_end_time
            if injury_type is not None:
                collected_data.injury_type = injury_type
            if circumstances is not None:
                collected_data.circumstances = circumstances
            if cause is not None:
                collected_data.cause = cause
            if place_description is not None:
                collected_data.place_description = place_description
            if medical_help is not None:
                collected_data.medical_help = medical_help
            if investigation is not None:
                collected_data.investigation = investigation
            if machines_involved is not None:
                collected_data.machines_involved = machines_involved
            if machine_condition is not None:
                collected_data.machine_condition = machine_condition
            if proper_use is not None:
                collected_data.proper_use = proper_use
            if machine_description is not None:
                collected_data.machine_description = machine_description
            if machine_certification is not None:
                collected_data.machine_certification = machine_certification
            if machine_registry is not None:
                collected_data.machine_registry = machine_registry
            if witnesses is not None:
                collected_data.witnesses = witnesses

            self.save_memory(self._current_session_id, collected_data)
            return "Data saved successfully"
        
        @tool  
        def analyze_accident_causes(
            activity_before_accident: str,
            event_sequence: str,
            direct_cause: str,
            indirect_causes: str = None
        ):
            """
            Przeprowadź szczegółową analizę przyczyn wypadku (drzewo przyczyn).
            Wywołaj tę funkcję TYLKO gdy masz już podstawowe informacje o wypadku.
            
            Args:
                activity_before_accident: Co poszkodowany robił bezpośrednio przed wypadkiem
                event_sequence: Szczegółowa sekwencja zdarzeń krok po kroku (1. 2. 3...)
                direct_cause: Bezpośrednia przyczyna urazu (co fizycznie spowodowało obrażenie)
                indirect_causes: Czynniki które przyczyniły się do wypadku (warunki, okoliczności)
            """
            print(f'Analyzing accident causes: {locals()}')

            collected_data = self.load_memory(self._current_session_id)

            collected_data.activity_before_accident = activity_before_accident
            collected_data.event_sequence = event_sequence
            collected_data.direct_cause = direct_cause
            if indirect_causes:
                collected_data.indirect_causes = indirect_causes

            self.save_memory(self._current_session_id, collected_data)
            return "Cause analysis saved successfully"
        return [save_accident_info, analyze_accident_causes]

    def _load_chat_history(self, session_id):
        """Load chat history from Redis"""
        if self.redis is None or not session_id:
            return []
        
        try:
            history_json = self.redis.get(f"chat_history:{session_id}")
            if history_json:
                history_data = json.loads(history_json)
                messages = []
                for msg in history_data:
                    if msg["type"] == "human":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["type"] == "ai":
                        messages.append(AIMessage(content=msg["content"]))
                print(f"[REDIS] Loaded {len(messages)} chat messages")
                return messages
        except Exception as e:
            print(f"[REDIS] Error loading chat history: {e}")
        
        return []

    def _save_chat_history(self, session_id, chat_history, expire_seconds=3600):
        """Save chat history to Redis"""
        if self.redis is None or not session_id:
            return
        
        try:
            history_data = []
            for msg in chat_history:
                if isinstance(msg, HumanMessage):
                    history_data.append({"type": "human", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    history_data.append({"type": "ai", "content": msg.content})
            
            history_json = json.dumps(history_data)
            self.redis.setex(f"chat_history:{session_id}", expire_seconds, history_json)
            print(f"[REDIS] Saved {len(history_data)} chat messages")
        except Exception as e:
            print(f"[REDIS] Error saving chat history: {e}")

    def load_memory(self, session_id):
        """Load accident data from Redis for the given session ID"""
        if self.redis is None or not session_id:
            print(f"[REDIS] Cannot load - Redis not available or no session_id")
            return AccidentInfo()
        
        try:
            data_json = self.redis.get(f"accident_data_memory:{session_id}")
            if data_json:
                print(f"[REDIS] Loaded data for session: {session_id}")
                return AccidentInfo.parse_raw(data_json)
            else:
                print(f"[REDIS] No existing data for session: {session_id}, returning empty")
                return AccidentInfo()
        except Exception as e:
            print(f"[REDIS] Error loading memory: {e}")
            return AccidentInfo()
        
    def save_memory(self, session_id, collected_data, expire_seconds=3600):
        """Save conversation memory to Redis for the given session ID"""
        print(f"[DEBUG] save_memory called")
        print(f"[DEBUG] session_id: {session_id}")
        print(f"[DEBUG] collected_data type: {type(collected_data)}")
        print(f"[DEBUG] collected_data: {collected_data}")
        
        if self.redis is None or not session_id:
            print(f"[REDIS] Cannot save - Redis not available or no session_id")
            return
        
        try:
            # Tu może być problem - sprawdźmy co to jest collected_data
            print(f"[DEBUG] About to call collected_data.json()")
            data_json = collected_data.json()
            print(f"[DEBUG] Successfully converted to JSON")
            
            self.redis.setex(f"accident_data_memory:{session_id}", expire_seconds, data_json)
            print(f"[REDIS] Saved data for session: {session_id}")
        except Exception as e:
            print(f"[ERROR] Error saving memory to Redis: {e}")
            import traceback
            traceback.print_exc()

    def collect_data(self, user_input, chat_history=None, session_id = "default"):
        """Collect accident data through a conversation"""
        self._current_session_id = session_id
        
        print(f"\n{'='*60}")
        print(f"[SESSION] Processing input for session: {session_id}")
        print(f"[INPUT] User: {user_input}")
        
        if chat_history is None:
            chat_history = self._load_chat_history(session_id)

        try:
            result = self.agent_executor.invoke({
                "input": user_input,
                "chat_history": chat_history
            })

            chat_history.append(HumanMessage(content=user_input))
            chat_history.append(AIMessage(content=result["output"]))
            
            self._save_chat_history(session_id, chat_history[-20:])
            
            print(f"[OUTPUT] {result['output']}")
            print(f"{'='*60}\n")
            
            return result["output"]
            
        except Exception as e:
            print(f"[ERROR] Exception during agent execution: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def get_collected_data(self, session_id="default"):
        """Returns collected accident data for specific session"""
        return self.load_memory(session_id)


if __name__ == "__main__":
    agent = AccidentDataCollectorAgent()
    response = agent.collect_data("Miałam wypadek")
    print(response)
    