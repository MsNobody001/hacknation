# from langchain.agents import create_agent
# import threading

# _agent_lock = threading.Lock()
# _cached_agents = {}

# def get_agent(name, recreate=False):
#     if recreate:
#         with _agent_lock:
#             _cached_agents.pop(name, None)

#     if name not in _cached_agents:
#         with _agent_lock:
#             if name not in _cached_agents:
#                 _cached_agents[name] = create_agent(name)

#     return _cached_agents[name]
    

# def get_sequential_events_agent(recreate=False):
#     return get_agent("sequential_events", recreate=recreate)

import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
import threading

load_dotenv()

class AccidentDataCollectorAgent:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                llm = AzureChatOpenAI(
                    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
                    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
                    temperature=0,
                )
                
                prompt = ChatPromptTemplate.from_messages(
                    [
                        (
                            "system",
                            "Jesteś asystentem ZUS zbierającym informacje o wypadku przy pracy. "
                            "Prowadź rozmowę z użytkownikiem, aby uzyskać wszystkie niezbędne informacje: "
                            "1) Nagłość zdarzenia, 2) Przyczynę zewnętrzną, 3) Skutek w postaci urazu, "
                            "4) Związek z pracą (czy podczas wykonywania czynności zawodowych). "
                            "Zadawaj pytania jedno po drugim, aby zebrać kompletne dane."
                        ),
                        ("placeholder", "{chat_history}"),
                        ("user", "{input}"),
                        ("placeholder", "{agent_scratchpad}"),
                    ]
                )
                
                agent = create_tool_calling_agent(llm, [], prompt)

                cls._instance = object.__new__(cls)
                cls._instance._runnable_agent = agent
                cls._instance.llm = llm
            return cls._instance
        
    def __init__(self):
        pass

    def collect_data(self, user_input, memory):
        """Collect accident data through a conversation"""
        agent_executor = AgentExecutor.from_agent_and_tools(
            self._runnable_agent,
            [],
            memory=memory,
            verbose=True,
            handle_parsing_errors=True,
        )
        result = agent_executor.invoke({
            "input": user_input,
        })
        return result["output"]


if __name__ == "__main__":
    # 1. Pobieranie instancji Singletona
    agent_singleton = AccidentDataCollectorAgent.get_instance()
    
    # 2. Tworzenie pamięci dla pierwszej sesji (User A)
    user_a_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    print("--- Sesja A (Rozmowa 1) ---")
    response_1 = agent_singleton.collect_data("Wczoraj, gdy przenosiłem ciężkie pudło, nagle poczułem ostry ból w plecach.", user_a_memory)
    print(response_1)
    
    print("\n--- Sesja A (Rozmowa 2) ---")
    response_2 = agent_singleton.collect_data("Tak, byłem w trakcie wykonywania obowiązków służbowych.", user_a_memory)
    print(response_2)
    
    # 3. Sprawdzenie, czy instancja jest ta sama
    agent_singleton_2 = AccidentDataCollectorAgent.get_instance()
    print(f"\nCzy instancje są identyczne? {agent_singleton is agent_singleton_2}")