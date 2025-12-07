from pydantic import BaseModel, Field
from typing import Optional


class AccidentStatement(BaseModel):
    """Structured data model for collecting injured person's statement (wyjaśnienia poszkodowanego)"""
    
    # BASIC EVENT DATA
    accident_date: Optional[str] = None
    accident_time: Optional[str] = None
    location: Optional[str] = None
    
    # WORK TIME
    work_start_time: Optional[str] = None
    work_end_time: Optional[str] = None
    
    # ACTIVITY BEFORE ACCIDENT
    activity_before_accident: Optional[str] = None
    
    # CIRCUMSTANCES AND CAUSES
    circumstances: Optional[str] = None
    cause: Optional[str] = None
    place_description: Optional[str] = None
    
    # MACHINES AND EQUIPMENT
    machines_involved: Optional[bool] = None
    machine_name_type: Optional[str] = None
    machine_production_date: Optional[str] = None
    machine_condition: Optional[str] = None
    proper_use: Optional[str] = None
    machine_description: Optional[str] = None
    
    # SAFETY EQUIPMENT
    safety_equipment_used: Optional[bool] = None
    safety_equipment_types: Optional[str] = None
    safety_equipment_condition: Optional[str] = None
    
    # BHP AND TRAINING
    bhp_compliance: Optional[bool] = None
    professional_preparation: Optional[bool] = None
    bhp_training: Optional[bool] = None
    risk_assessment: Optional[bool] = None
    risk_mitigation: Optional[str] = None
    
    # WORK SAFETY PROCEDURES
    safety_measures: Optional[bool] = None
    work_solo_or_team: Optional[str] = None
    
    # SOBRIETY
    sobriety_state: Optional[bool] = None
    sobriety_tested: Optional[bool] = None
    sobriety_tested_by: Optional[str] = None
    
    # INVESTIGATION BY AUTHORITIES
    investigation_authorities: Optional[bool] = None
    authority_name: Optional[str] = None
    authority_address: Optional[str] = None
    authority_case_number: Optional[str] = None
    authority_case_status: Optional[str] = None
    
    # MEDICAL HELP AND HOSPITALIZATION
    first_aid_provided: Optional[bool] = None
    first_aid_date: Optional[str] = None
    medical_facility: Optional[str] = None
    hospitalization_period: Optional[str] = None
    hospitalization_place: Optional[str] = None
    diagnosed_injury: Optional[str] = None
    work_incapacity_period: Optional[str] = None
    
    # SICK LEAVE
    sick_leave_on_accident_day: Optional[bool] = None
    
    # WITNESSES
    witnesses: Optional[str] = None
    
    # EVENT SEQUENCE
    event_sequence: Optional[str] = None
    
    def get_missing_required_fields(self):
        """Returns a list of missing required fields"""
        # Fields with string values (check with 'not')
        string_fields = {
            'accident_date': 'data wypadku',
            'accident_time': 'godzina wypadku',
            'location': 'miejsce wypadku',
            'work_start_time': 'planowana godzina rozpoczęcia pracy',
            'work_end_time': 'planowana godzina zakończenia pracy',
            'activity_before_accident': 'rodzaj czynności wykonywanych do momentu wypadku',
            'circumstances': 'szczegółowy opis okoliczności wypadku',
            'cause': 'przyczyny wypadku',
            'place_description': 'szczegółowy opis miejsca wypadku',
            'work_solo_or_team': 'czy praca jednoosobowa czy wieloosobowa',
            'medical_facility': 'nazwa placówki ochrony zdrowia',
            'diagnosed_injury': 'rozpoznany uraz',
            'work_incapacity_period': 'okres niezdolności do pracy',
            'event_sequence': 'szczegółowa sekwencja zdarzeń',
        }
        
        # Fields with boolean values (check with 'is None')
        boolean_fields = {
            'machines_involved': 'czy były używane maszyny lub narzędzia',
            'safety_equipment_used': 'czy stosowano środki ochrony osobistej',
            'bhp_compliance': 'czy przestrzegano zasad BHP',
            'professional_preparation': 'czy posiada przygotowanie zawodowe',
            'bhp_training': 'czy odbył szkolenia z BHP',
            'risk_assessment': 'czy posiada opracowaną ocenę ryzyka',
            'safety_measures': 'czy stosowano asekurację',
            'sobriety_state': 'czy był w stanie trzeźwości',
            'sobriety_tested': 'czy był badany stan trzeźwości',
            'investigation_authorities': 'czy były podjęte czynności przez organy kontroli',
            'first_aid_provided': 'czy udzielono pierwszej pomocy',
            'sick_leave_on_accident_day': 'czy przebywał na zwolnieniu w dniu wypadku',
        }
        
        missing = []
        missing.extend([label for field, label in string_fields.items() if not getattr(self, field)])
        missing.extend([label for field, label in boolean_fields.items() if getattr(self, field) is None])
        
        return missing
    
    def is_complete(self) -> bool:
        """Check if all required fields are filled"""
        return len(self.get_missing_required_fields()) == 0
