from pydantic import BaseModel, Field
from typing import Optional


class AccidentInfo(BaseModel):
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
        missing = []
        if not self.accident_date:
            missing.append("data wypadku")
        if not self.accident_time:
            missing.append("godzina wypadku")
        if not self.location:
            missing.append("miejsce wypadku")
        if not self.work_start_time:
            missing.append("planowana godzina rozpoczęcia pracy")
        if not self.work_end_time:
            missing.append("planowana godzina zakończenia pracy")
        if not self.injury_type:
            missing.append("rodzaj urazu")
        if not self.circumstances:
            missing.append("okoliczności wypadku")
        if not self.cause:
            missing.append("przyczyna wypadku")
        if not self.place_description:
            missing.append("opis miejsca wypadku")
        if not self.witnesses:
            missing.append("dane świadków wypadku")
        if not self.activity_before_accident:
            missing.append("czynności wykonywane bezpośrednio przed wypadkiem")
        if not self.event_sequence:
            missing.append("szczegółowa sekwencja zdarzeń krok po kroku")
        if not self.direct_cause:
            missing.append("bezpośrednia przyczyna urazu")
        if not self.indirect_causes:
            missing.append("czynniki które przyczyniły się do wypadku")
        return missing
    
    def is_complete(self) -> bool:
        """Check if all required fields are filled"""
        return len(self.get_missing_required_fields()) == 0
