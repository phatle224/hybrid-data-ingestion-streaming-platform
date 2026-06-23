"""
Excel service with Factory Pattern.
Mirrors backend services/excel_service.py.
Manages insurance type detection and processor instantiation.
"""
import os
import logging
from typing import Optional, Tuple, List, Dict, Any
from models.contract_model import ContractRecord
from processors.base_processor import IInsuranceProcessor
from processors import PROCESSOR_REGISTRY
from configs.mappings import MAPPING_REGISTRY

logger = logging.getLogger(__name__)


class ProcessorFactory:
    """
    Factory class to create appropriate processor based on insurance type.

    Design Pattern: Factory Pattern
    - Encapsulates object creation logic
    - Allows easy extension for new insurance types
    """

    _processors = PROCESSOR_REGISTRY
    _mappings = MAPPING_REGISTRY

    @classmethod
    def register_processor(cls, insurance_type: str, processor_class: type):
        """Register a new processor type."""
        cls._processors[insurance_type] = processor_class

    @classmethod
    def register_mapping(cls, insurance_type: str, mapping_class: type):
        """Register a new mapping type."""
        cls._mappings[insurance_type] = mapping_class

    @classmethod
    def create_processor(cls, insurance_type: str) -> IInsuranceProcessor:
        """
        Create processor instance for given insurance type.

        Raises:
            ValueError: If insurance type is not supported
        """
        processor_class = cls._processors.get(insurance_type)
        if not processor_class:
            raise ValueError(f"Unsupported insurance type: {insurance_type}")
        return processor_class()

    @classmethod
    def get_supported_types(cls) -> List[str]:
        """Get list of supported insurance types."""
        return list(cls._processors.keys())


class ExcelService:
    """
    Excel service using factory pattern.
    Provides high-level interface for Excel processing.
    """

    def __init__(self):
        self.factory = ProcessorFactory()

    def detect_insurance_type(self, filename: str) -> str:
        """
        Detect insurance type from filename.

        Args:
            filename: Name of the Excel file

        Returns:
            Insurance type string (TRAVEL, VEHICLE, etc.)

        Raises:
            ValueError: If insurance type cannot be detected
        """
        filename_upper = filename.upper()

        for insurance_type, mapping_class in ProcessorFactory._mappings.items():
            keywords = mapping_class.get_file_keywords()
            for keyword in keywords:
                if keyword.upper() in filename_upper:
                    return insurance_type

        raise ValueError(f"Cannot detect insurance type from filename: {filename}")

    def process_excel_file(
        self,
        file_path: str,
        insurance_type: Optional[str] = None,
    ) -> Tuple[List[ContractRecord], List[Dict[str, Any]]]:
        """
        Process Excel file with appropriate processor.

        Args:
            file_path: Path to Excel file
            insurance_type: Optional insurance type (auto-detect if not provided)

        Returns:
            Tuple of (valid_records, detailed_errors)
        """
        # Auto-detect if not provided
        if not insurance_type:
            filename = os.path.basename(file_path)
            insurance_type = self.detect_insurance_type(filename)

        logger.info("Processing %s as %s", file_path, insurance_type)

        # Get appropriate processor
        processor = self.factory.create_processor(insurance_type)

        # Process file using Template Method
        valid_records, errors = processor.process_file(file_path)

        logger.info(
            "[%s] Processed: %d valid, %d errors",
            insurance_type, len(valid_records), len(errors)
        )

        return valid_records, errors

    def get_supported_insurance_types(self) -> List[str]:
        """Get list of supported insurance types."""
        return self.factory.get_supported_types()

    def get_processor(self, insurance_type: str) -> IInsuranceProcessor:
        """Get processor instance for specific insurance type."""
        return self.factory.create_processor(insurance_type)
