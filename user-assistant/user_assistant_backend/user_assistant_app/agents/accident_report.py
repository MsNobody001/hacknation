from pydantic import BaseModel, Field
from typing import Optional


class AccidentReport(BaseModel):
    """Structured data model for collecting accident information"""
    
    # PRIORITY 1 - REQUIRED FIELDS
    accident_date: Optional[str] = None
    accident_time: Optional[str] = None
    location: Optional[str] = None
    
    work_start_time: Optional[str] = None
    work_end_time: Optional[str] = None
    
    injury_type: Optional[str] = None
    
    circumstances: Optional[str] = None
    cause: Optional[str] = None
    place_description: Optional[str] = None
    
    # PRIORITY 2 - ADDITIONAL
    medical_help: Optional[str] = None
    investigation: Optional[str] = None
    
    # MACHINES AND EQUIPMENT
    machines_involved: Optional[bool] = None
    machine_condition: Optional[str] = None
    proper_use: Optional[str] = None
    machine_description: Optional[str] = None
    machine_certification: Optional[str] = None
    machine_registry: Optional[str] = None
    
    # WITNESSES
    witnesses: Optional[str] = None

    # EVENT SEQUENCE AND CAUSES
    activity_before_accident: Optional[str] = None
    event_sequence: Optional[str] = None
    direct_cause: Optional[str] = None 
    indirect_causes: Optional[str] = None 
    
    def get_missing_required_fields(self):
        """Returns a list of missing required fields"""
        required_fields = {
            'accident_date': 'data wypadku',
            'accident_time': 'godzina wypadku',
            'location': 'miejsce wypadku',
            'work_start_time': 'planowana godzina rozpoczęcia pracy',
            'work_end_time': 'planowana godzina zakończenia pracy',
            'injury_type': 'rodzaj urazu',
            'circumstances': 'okoliczności wypadku',
            'cause': 'przyczyna wypadku',
            'place_description': 'opis miejsca wypadku',
            'witnesses': 'dane świadków wypadku',
            'activity_before_accident': 'czynności wykonywane bezpośrednio przed wypadkiem',
            'event_sequence': 'szczegółowa sekwencja zdarzeń krok po kroku',
            'direct_cause': 'bezpośrednia przyczyna urazu',
            'indirect_causes': 'czynniki które przyczyniły się do wypadku',
        }
        
        return [label for field, label in required_fields.items() if not getattr(self, field)]
    
    def is_complete(self) -> bool:
        """Check if all required fields are filled"""
        return len(self.get_missing_required_fields()) == 0
