"""
Processors Package - Insurance type processors
"""
from services.processors.base_processor import IInsuranceProcessor
from services.processors.travel_processor import TravelProcessor
from services.processors.vehicle_processor import VehicleProcessor
from services.processors.moto_processor import MotoProcessor
from services.processors.medical_social_processor import MedicalSocialProcessor
from services.processors.health_processor import HealthProcessor
from services.processors.hazard_processor import HazardProcessor


# Registry of all available processors
PROCESSOR_REGISTRY = {
    'TRAVEL': TravelProcessor,
    'VEHICLE': VehicleProcessor,
    'MOTO': MotoProcessor,
    'MEDICAL_SOCIAL': MedicalSocialProcessor,
    'HEALTH': HealthProcessor,
    'HAZARD': HazardProcessor,
}


def get_processor(insurance_type: str) -> IInsuranceProcessor:
    """
    Get processor instance for insurance type
    
    Args:
        insurance_type: Insurance type identifier
        
    Returns:
        Processor instance
        
    Raises:
        ValueError: If insurance type is not supported
    """
    processor_class = PROCESSOR_REGISTRY.get(insurance_type)
    if not processor_class:
        raise ValueError(f"Unsupported insurance type: {insurance_type}")
    return processor_class()


def get_supported_types() -> list:
    """Get list of supported insurance types"""
    return list(PROCESSOR_REGISTRY.keys())


__all__ = [
    'IInsuranceProcessor',
    'TravelProcessor',
    'VehicleProcessor',
    'MotoProcessor',
    'MedicalSocialProcessor',
    'HealthProcessor',
    'HazardProcessor',
    'PROCESSOR_REGISTRY',
    'get_processor',
    'get_supported_types',
]
