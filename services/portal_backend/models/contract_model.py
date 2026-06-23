"""
Contract data model
"""
from typing import Optional, Dict, Any
from datetime import datetime


class ContractRecord:
    """Contract record model - supports both fixed and dynamic fields"""
    
    def __init__(self, data: Dict[str, Any]):
        """
        Initialize contract record from dictionary
        
        Args:
            data: Dictionary containing contract data
        """
        # Store ALL original data for validation and flexible access
        self._raw_data = data.copy()
        
        # Core required fields (4 business keys)
        self.contract_id: Optional[str] = data.get("contractId")
        self.payer_name: Optional[str] = data.get("payerName")
        self.major_name: Optional[str] = data.get("majorName")
        self.company_provider_name: Optional[str] = data.get("companyProviderName")
        
        # Legacy field (kept for backward compat, not used in business key)
        self.name: Optional[str] = data.get("name")
        
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
        Convert model to dictionary for database insertion
        Returns ALL data including dynamic fields from Excel
        """
        # Start with raw data to preserve all fields
        # (including fields written by post_process, e.g. mirrored peopleName)
        result = self._raw_data.copy()
        
        # Always override with authoritative instance vars for business key fields
        result.update({
            "contractId": self.contract_id,
            "payerName": self.payer_name,
            "majorName": self.major_name,
            "companyProviderName": self.company_provider_name,
            "insuranceType": self.insurance_type,
        })
        
        # For optional fields, only override if instance var is not None.
        # This preserves changes made to _raw_data in post_process
        # (e.g. peopleName mirrored from payerName stays intact).
        optional_updates = {
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
            "startDateJourney": self.start_date_journey,
            "endDateJourney": self.end_date_journey,
            "feeInsurance": self.fee_insurance,
            "programName": self.program_name,
            "saleId": self.sale_id,
            "channelId": self.channel_id,
        }
        result.update({k: v for k, v in optional_updates.items() if v is not None})
        
        return result

    @staticmethod
    def _normalize_date_key(value: Any) -> Optional[str]:
        """Normalize date/datetime value to YYYY-MM-DD for duplicate keys."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        text = str(value).strip()
        if not text:
            return None

        # Handle common datetime string formats, keep date-only for key matching.
        if " " in text:
            text = text.split(" ")[0]
        if "T" in text:
            text = text.split("T")[0]

        try:
            return datetime.fromisoformat(text).strftime("%Y-%m-%d")
        except ValueError:
            return text
    
    def get_normalized_start_date(self) -> str:
        """Get normalized start date from any available field for 7-key deduplication.
        Priority order: journey > contractObject > contract > insurance (matches repository logic)
        """
        val = (
            self.start_date_journey or 
            self._raw_data.get("contractObjectStartDate") or 
            self._raw_data.get("contractStartDate") or 
            self.start_insurance or 
            ""
        )
        return self._normalize_date_key(val)

    def get_normalized_end_date(self) -> str:
        """Get normalized end date from any available field for 7-key deduplication.
        Priority order: journey > contractObject > contract > insurance (matches repository logic)
        """
        val = (
            self.end_date_journey or 
            self._raw_data.get("contractObjectEndDate") or 
            self._raw_data.get("contractEndDate") or 
            self.end_insurance or 
            ""
        )
        return self._normalize_date_key(val)

    def get_normalized_fee_insurance(self) -> str:
        """Normalize feeInsurance for 7-key deduplication - matches repository normalization."""
        # First try instance var (set during __init__), then raw_data (set during post_process)
        val = self.fee_insurance if self.fee_insurance is not None else self._raw_data.get("feeInsurance")
        if val is None or val == "":
            return None  # Return None instead of empty string to match repository behavior
        try:
            if isinstance(val, (int, float)):
                num = float(val)
            else:
                text = str(val).strip()
                if not text:
                    return None
                text = text.replace('.', '').replace(',', '.')
                num = float(text)
            # Format with 6 decimal places, then strip trailing zeros
            result = f"{num:.6f}".rstrip('0').rstrip('.')
            return result if result else None
        except (ValueError, TypeError):
            return None

    def get_business_keys(self) -> Dict[str, Any]:
        """Get business key fields for duplicate checking (7 keys)."""
        return {
            "contractId": self.contract_id,
            "peopleName": self.people_name,
            "majorName": self.major_name,
            "companyProviderName": self.company_provider_name,
            "startDate": self.get_normalized_start_date(),
            "endDate": self.get_normalized_end_date(),
            "feeInsurance": self.get_normalized_fee_insurance()
        }
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate required fields
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.contract_id:
            return False, "contractId is required"
        if not self.people_name:
            return False, "peopleName is required"
        if not self.major_name:
            return False, "majorName is required"
        if not self.company_provider_name:
            return False, "companyProviderName is required"
        
        return True, None
    
    def __repr__(self):
        return f"ContractRecord(contractId={self.contract_id}, peopleName={self.people_name})"
