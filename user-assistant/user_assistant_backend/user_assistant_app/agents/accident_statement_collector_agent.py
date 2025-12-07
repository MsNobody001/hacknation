import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from .base_data_collector_agent import BaseDataCollectorAgent
from .accident_statement import AccidentStatement


load_dotenv()

PROMPT_FILE_PATH = os.path.join(os.path.dirname(__file__), "prompts/collect_accident_statement_data.txt")

class AccidentStatementCollectorAgent(BaseDataCollectorAgent):
    """Agent for collecting accident statement data"""
    
    def __init__(self):
        super().__init__(
            prompt_file_path=PROMPT_FILE_PATH,
            data_model_class=AccidentStatement
        )
    
    def _create_tools(self):
        """Create tools specific for accident statement collection"""
        
        @tool
        def save_statement_info(
            accident_date: str = None,
            accident_time: str = None,
            location: str = None,
            work_start_time: str = None,
            work_end_time: str = None,
            activity_before_accident: str = None,
            circumstances: str = None,
            cause: str = None,
            place_description: str = None,
            machines_involved: bool = None,
            machine_name_type: str = None,
            machine_production_date: str = None,
            machine_condition: str = None,
            proper_use: str = None,
            machine_description: str = None,
            safety_equipment_used: bool = None,
            safety_equipment_types: str = None,
            safety_equipment_condition: str = None,
            bhp_compliance: bool = None,
            professional_preparation: bool = None,
            bhp_training: bool = None,
            risk_assessment: bool = None,
            risk_mitigation: str = None,
            safety_measures: bool = None,
            work_solo_or_team: str = None,
            sobriety_state: bool = None,
            sobriety_tested: bool = None,
            sobriety_tested_by: str = None,
            investigation_authorities: bool = None,
            authority_name: str = None,
            authority_address: str = None,
            authority_case_number: str = None,
            authority_case_status: str = None,
            first_aid_provided: bool = None,
            first_aid_date: str = None,
            medical_facility: str = None,
            hospitalization_period: str = None,
            hospitalization_place: str = None,
            diagnosed_injury: str = None,
            work_incapacity_period: str = None,
            sick_leave_on_accident_day: bool = None,
            witnesses: str = None,
            event_sequence: str = None
        ):
            """
            Zapisz informacje z wyjaśnień poszkodowanego podane przez użytkownika.
            Wywołaj tę funkcję gdy użytkownik poda jakiekolwiek dane.
            Możesz wypełnić jedno lub więcej pól jednocześnie.
            
            Args:
                accident_date: Data wypadku
                accident_time: Godzina wypadku  
                location: Miejsce gdzie się wydarzył wypadek
                work_start_time: Planowana godzina rozpoczęcia pracy
                work_end_time: Planowana godzina zakończenia pracy
                activity_before_accident: Jaki rodzaj czynności wykonywał poszkodowany do momentu wypadku
                circumstances: Szczegółowy opis okoliczności w jakich doszło do wypadku
                cause: Jakie były przyczyny wypadku
                place_description: Szczegółowy opis miejsca, w którym wydarzył się wypadek
                machines_involved: Czy były używane maszyny lub narzędzia
                machine_name_type: Nazwa, typ urządzenia
                machine_production_date: Data produkcji urządzenia
                machine_condition: Czy urządzenie było sprawne
                proper_use: Czy używano zgodnie z zasadami producenta
                machine_description: W jaki dokładnie sposób używano maszyny/narzędzia
                safety_equipment_used: Czy stosowano zabezpieczenia/środki ochrony osobistej
                safety_equipment_types: Jakie środki ochrony (buty, kask, odzież, rękawice)
                safety_equipment_condition: Czy stosowane środki były właściwe i sprawne
                bhp_compliance: Czy przestrzegano zasad BHP w trakcie pracy
                professional_preparation: Czy poszkodowany posiada przygotowanie do wykonywania zadań
                bhp_training: Czy poszkodowany odbył szkolenia z BHP dla pracodawców
                risk_assessment: Czy posiada opracowaną ocenę ryzyka zawodowego
                risk_mitigation: Jakie środki stosuje w celu zmniejszenia ryzyka
                safety_measures: Czy stosowano podczas pracy asekurację
                work_solo_or_team: Czy pracę można było wykonywać samodzielnie czy wymagała co najmniej dwóch osób
                sobriety_state: Czy w chwili wypadku był w stanie nietrzeźwości lub pod wpływem środków
                sobriety_tested: Czy był badany stan trzeźwości w dniu wypadku
                sobriety_tested_by: Przez kogo był badany stan trzeźwości (np. policja)
                investigation_authorities: Czy były podjęte czynności wyjaśniające przez organy kontroli (policja, inspekcja pracy, dozór techniczny, inspekcja sanitarna, straż pożarna)
                authority_name: Nazwa organu prowadzącego postępowanie
                authority_address: Adres organu
                authority_case_number: Numer sprawy/decyzji
                authority_case_status: Status sprawy (zakończona/w trakcie/umorzona)
                first_aid_provided: Czy udzielono pierwszej pomocy
                first_aid_date: W którym dniu udzielono pomocy
                medical_facility: Nazwa placówki ochrony zdrowia
                hospitalization_period: Okres hospitalizacji
                hospitalization_place: Miejsce hospitalizacji
                diagnosed_injury: Uraz rozpoznany na podstawie dokumentacji lekarskiej
                work_incapacity_period: Okres niezdolności do świadczenia pracy
                sick_leave_on_accident_day: Czy w dniu wypadku przebywał na zwolnieniu lekarskim
                witnesses: Dane świadków (imię, nazwisko, adres z kodem pocztowym i krajem)
                event_sequence: Szczegółowa sekwencja zdarzeń (co robił przed, co się stało, kolejne etapy)
            """
            self.collected_data.accident_date = accident_date
            self.collected_data.accident_time = accident_time
            self.collected_data.location = location
            self.collected_data.work_start_time = work_start_time
            self.collected_data.work_end_time = work_end_time
            self.collected_data.activity_before_accident = activity_before_accident
            self.collected_data.circumstances = circumstances
            self.collected_data.cause = cause
            self.collected_data.place_description = place_description
            self.collected_data.machines_involved = machines_involved
            self.collected_data.machine_name_type = machine_name_type
            self.collected_data.machine_production_date = machine_production_date
            self.collected_data.machine_condition = machine_condition
            self.collected_data.proper_use = proper_use
            self.collected_data.machine_description = machine_description
            self.collected_data.safety_equipment_used = safety_equipment_used
            self.collected_data.safety_equipment_types = safety_equipment_types
            self.collected_data.safety_equipment_condition = safety_equipment_condition
            self.collected_data.bhp_compliance = bhp_compliance
            self.collected_data.professional_preparation = professional_preparation
            self.collected_data.bhp_training = bhp_training
            self.collected_data.risk_assessment = risk_assessment
            self.collected_data.risk_mitigation = risk_mitigation
            self.collected_data.safety_measures = safety_measures
            self.collected_data.work_solo_or_team = work_solo_or_team
            self.collected_data.sobriety_state = sobriety_state
            self.collected_data.sobriety_tested = sobriety_tested
            self.collected_data.sobriety_tested_by = sobriety_tested_by
            self.collected_data.investigation_authorities = investigation_authorities
            self.collected_data.authority_name = authority_name
            self.collected_data.authority_address = authority_address
            self.collected_data.authority_case_number = authority_case_number
            self.collected_data.authority_case_status = authority_case_status
            self.collected_data.first_aid_provided = first_aid_provided
            self.collected_data.first_aid_date = first_aid_date
            self.collected_data.medical_facility = medical_facility
            self.collected_data.hospitalization_period = hospitalization_period
            self.collected_data.hospitalization_place = hospitalization_place
            self.collected_data.diagnosed_injury = diagnosed_injury
            self.collected_data.work_incapacity_period = work_incapacity_period
            self.collected_data.sick_leave_on_accident_day = sick_leave_on_accident_day
            self.collected_data.witnesses = witnesses
            self.collected_data.event_sequence = event_sequence
            return "Data saved successfully"
        
        return [save_statement_info]


if __name__ == "__main__":
    agent = AccidentStatementCollectorAgent()
    response = agent.collect_data("Miałam wypadek")
    print(response)
