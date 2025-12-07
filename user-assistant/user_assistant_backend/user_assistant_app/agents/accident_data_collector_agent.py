import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from .accident_models import AccidentInfo
from pathlib import Path


load_dotenv()

BASE_DIR = Path(__file__).resolve()
PROMPT_FILE_PATH = BASE_DIR.parent / "prompts" / "collect_accident_data.txt"
class AccidentDataCollectorAgent:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
            openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        )

        self.collected_data = AccidentInfo()
        
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

            if accident_date is not None:
                self.collected_data.accident_date = accident_date
            if accident_time is not None:
                self.collected_data.accident_time = accident_time
            if location is not None:
                self.collected_data.location = location
            if work_start_time is not None:
                self.collected_data.work_start_time = work_start_time
            if work_end_time is not None:
                self.collected_data.work_end_time = work_end_time
            if injury_type is not None:
                self.collected_data.injury_type = injury_type
            if circumstances is not None:
                self.collected_data.circumstances = circumstances
            if cause is not None:
                self.collected_data.cause = cause
            if place_description is not None:
                self.collected_data.place_description = place_description
            if medical_help is not None:
                self.collected_data.medical_help = medical_help
            if investigation is not None:
                self.collected_data.investigation = investigation
            if machines_involved is not None:
                self.collected_data.machines_involved = machines_involved
            if machine_condition is not None:
                self.collected_data.machine_condition = machine_condition
            if proper_use is not None:
                self.collected_data.proper_use = proper_use
            if machine_description is not None:
                self.collected_data.machine_description = machine_description
            if machine_certification is not None:
                self.collected_data.machine_certification = machine_certification
            if machine_registry is not None:
                self.collected_data.machine_registry = machine_registry
            if witnesses is not None:
                self.collected_data.witnesses = witnesses

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
            self.collected_data.activity_before_accident = activity_before_accident
            self.collected_data.event_sequence = event_sequence
            self.collected_data.direct_cause = direct_cause
            if indirect_causes:
                self.collected_data.indirect_causes = indirect_causes
            return "Cause analysis saved successfully"


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
        
        self.agent = create_tool_calling_agent(self.llm, [save_accident_info, analyze_accident_causes], self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=[save_accident_info, analyze_accident_causes], verbose=True)

    def collect_data(self, user_input, chat_history=None):
        """Collect accident data through a conversation"""
        if chat_history is None:
            chat_history = []
            
        result = self.agent_executor.invoke({
            "input": user_input,
            "chat_history": chat_history
        })
        return result["output"]
    
    def get_collected_data(self):
        """Returns collected accident data"""
        return self.collected_data


if __name__ == "__main__":
    agent = AccidentDataCollectorAgent()
    response = agent.collect_data("Miałam wypadek")
    print(response)
    