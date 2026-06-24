"""
Mappings Package - Insurance type column mappings.
Mirrors backend configs/mappings/ structure exactly.

Registry pattern for dynamic mapping lookup.
"""
from configs.mappings.base_mapping import BaseInsuranceMapping
from configs.mappings.travel_mapping import TravelMapping
from configs.mappings.vehicle_mapping import VehicleMapping
from configs.mappings.moto_mapping import MotoMapping
from configs.mappings.medical_social_mapping import MedicalSocialMapping
from configs.mappings.health_mapping import HealthMapping


# Registry of all available mappings (matches backend MAPPING_REGISTRY)
MAPPING_REGISTRY = {
    'TRAVEL': TravelMapping,
    'VEHICLE': VehicleMapping,
    'MOTO': MotoMapping,
    'MEDICAL_SOCIAL': MedicalSocialMapping,
    'HEALTH': HealthMapping,
}


def get_mapping(insurance_type: str) -> BaseInsuranceMapping:
    """
    Get mapping instance for insurance type.

    Args:
        insurance_type: Insurance type identifier

    Returns:
        Mapping instance

    Raises:
        ValueError: If insurance type is not supported
    """
    mapping_class = MAPPING_REGISTRY.get(insurance_type)
    if not mapping_class:
        raise ValueError(f"Unsupported insurance type: {insurance_type}")
    return mapping_class()


def get_supported_types() -> list:
    """Get list of supported insurance types."""
    return list(MAPPING_REGISTRY.keys())


__all__ = [
    'BaseInsuranceMapping',
    'TravelMapping', 'VehicleMapping', 'MotoMapping',
    'MedicalSocialMapping', 'HealthMapping',
    'MAPPING_REGISTRY', 'get_mapping', 'get_supported_types',
]
