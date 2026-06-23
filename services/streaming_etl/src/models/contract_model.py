"""
Contract data model.
Mirrors backend models/contract_model.py exactly.
Supports both fixed and dynamic fields from Excel data.
"""
from typing import Optional, Dict, Any
from datetime import datetime


class ContractRecord:
    """Contract record model - supports both fixed and dynamic fields."""

    def __init__(self, data: Dict[str, Any]):
        """
        Initialize contract record from dictionary.

        Args:
            data: Dictionary containing contract data
        """
        # Store ALL original data for validation and flexible access
        self._raw_data = data.copy()

        # Core required fields (4 business keys)
        self.contract_id: Optional[str] = data.get("contractId")
        self.name: Optional[str] = data.get("name") or data.get("peopleName")
        self.major_name: Optional[str] = data.get("majorName")
        self.company_provider_name: Optional[str] = data.get("companyProviderName")

        # Additional fields
        self.people_name: Optional[str] = data.get("peopleName")
        self.id_card: Optional[str] = data.get("idCard")
        self.gender: Optional[str] = data.get("gender")
        self.address: Optional[str] = data.get("address")
        self.dob: Optional[str] = data.get("dob")
        self.start_insurance: Optional[str] = data.get("startInsurance")
        self.end_insurance: Optional[str] = data.get("endInsurance")
        self.beneficiary: Optional[str] = data.get("beneficiary")
        self.package_name: Optional[str] = data.get("packageName")
        self.total_fee: Optional[float] = data.get("totalFee")
        self.note: Optional[str] = data.get("note")

        # Vehicle specific fields
        self.license_plate: Optional[str] = data.get("licensePlate")
        self.chassis_number: Optional[str] = data.get("chassisNumber")
        self.engine_number: Optional[str] = data.get("engineNumber")
        self.vehicle_type: Optional[str] = data.get("vehicleType")

        # Travel specific fields
        self.start_date_journey: Optional[str] = data.get("startDateJourney")
        self.end_date_journey: Optional[str] = data.get("endDateJourney")
        self.fee_insurance: Optional[float] = data.get("feeInsurance")
        self.program_name: Optional[str] = data.get("programName")
        self.sale_id: Optional[str] = data.get("saleId")
        self.channel_id: Optional[str] = data.get("channelId")

        # Metadata
        self.insurance_type: Optional[str] = data.get("insuranceType")
        self.created_at: Optional[datetime] = data.get("createdAt")
        self.updated_at: Optional[datetime] = data.get("updatedAt")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary for database insertion.
        Returns ALL data including dynamic fields from Excel.
        """
        result = self._raw_data.copy()

        # Ensure core fields are updated
        result.update({
            "contractId": self.contract_id,
            "name": self.name,
            "majorName": self.major_name,
            "companyProviderName": self.company_provider_name,
            "peopleName": self.people_name,
            "idCard": self.id_card,
            "gender": self.gender,
            "address": self.address,
            "dob": self.dob,
            "startInsurance": self.start_insurance,
            "endInsurance": self.end_insurance,
            "beneficiary": self.beneficiary,
            "packageName": self.package_name,
            "totalFee": self.total_fee,
            "note": self.note,
            "licensePlate": self.license_plate,
            "chassisNumber": self.chassis_number,
            "engineNumber": self.engine_number,
            "vehicleType": self.vehicle_type,
            "insuranceType": self.insurance_type,
            "startDateJourney": self.start_date_journey,
            "endDateJourney": self.end_date_journey,
            "feeInsurance": self.fee_insurance,
            "programName": self.program_name,
            "saleId": self.sale_id,
            "channelId": self.channel_id,
        })

        return result

    def get_business_keys(self) -> Dict[str, Any]:
        """Get business key fields for duplicate checking."""
        return {
            "contractId": self.contract_id,
            "name": self.name,
            "majorName": self.major_name,
            "companyProviderName": self.company_provider_name,
        }

    def validate(self) -> tuple:
        """
        Validate required fields.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.contract_id:
            return False, "contractId is required"
        if not self.name:
            return False, "name or peopleName is required"
        if not self.major_name:
            return False, "majorName is required"
        if not self.company_provider_name:
            return False, "companyProviderName is required"

        return True, None

    def __repr__(self):
        return f"ContractRecord(contractId={self.contract_id}, name={self.name})"
