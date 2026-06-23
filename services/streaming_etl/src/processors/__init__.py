"""
Processors Package - Insurance type processors.
Mirrors backend services/processors/__init__.py exactly.

Registry pattern for dynamic processor lookup.
"""
from processors.base_processor import IInsuranceProcessor
from processors.travel_processor import TravelProcessor
from processors.vehicle_processor import VehicleProcessor
from processors.moto_processor import MotoProcessor
from processors.medical_social_processor import MedicalSocialProcessor
from processors.health_processor import HealthProcessor
from processors.hazard_processor import HazardProcessor


# Registry of all available processors (matches backend PROCESSOR_REGISTRY)
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
    Get processor instance for insurance type.

    Raises:
        ValueError: If insurance type is not supported
    """
    processor_class = PROCESSOR_REGISTRY.get(insurance_type)
    if not processor_class:
        raise ValueError(f"Unsupported insurance type: {insurance_type}")
    return processor_class()


def get_supported_types() -> list:
    """Get list of supported insurance types."""
    return list(PROCESSOR_REGISTRY.keys())


__all__ = [
    'IInsuranceProcessor',
    'TravelProcessor', 'VehicleProcessor', 'MotoProcessor',
    'MedicalSocialProcessor', 'HealthProcessor', 'HazardProcessor',
    'PROCESSOR_REGISTRY', 'get_processor', 'get_supported_types',
]
